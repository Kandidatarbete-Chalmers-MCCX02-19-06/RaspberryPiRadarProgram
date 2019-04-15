// Copyright (c) Acconeer AB, 2018
// All rights reserved

#include <stdbool.h>
#include <stdint.h>

#include "acc_detector_distance_basic.h"

#include "acc_definitions.h"
#include "acc_device_os.h"
#include "acc_log.h"
#include "acc_service.h"
#include "acc_service_envelope.h"
#include "acc_sweep_configuration.h"


#define MODULE	"detector_distance_basic"

#define MAGIC_NUMBER                        (0xACC0D157)
#define INDEX_TO_DISTANCE_CONVERSION(X,K,M) ((K) * (X) + (M))



typedef struct acc_detector_distance_basic_handle
{
	uint32_t             magic_number;
	acc_service_handle_t envelope_handle;
	uint16_t             *envelope_data;
	uint16_t             envelope_data_length;
	float                absolute_offset;
	float                distance_offset;
	float                distance_slope;
} acc_detector_distance_basic_handle_internal_t;


static bool handle_valid(acc_detector_distance_basic_handle_t *detector_handle);
static uint16_t get_reflection_index(uint16_t *data, uint16_t data_length);


//-----------------------------
// Public definitions
//-----------------------------
acc_detector_distance_basic_handle_t *acc_detector_distance_basic_create(acc_sensor_id_t sensor, float range_start, float range_length)
{
	acc_service_configuration_t envelope_configuration = acc_service_envelope_configuration_create();

	if (envelope_configuration == NULL)
	{
		ACC_LOG_ERROR("Distance basic detector not possible to allocate");
		return NULL;
	}

	acc_service_envelope_profile_set(envelope_configuration, ACC_SERVICE_ENVELOPE_PROFILE_MAXIMIZE_SNR);

	acc_sweep_configuration_t sweep_configuration = acc_service_get_sweep_configuration(envelope_configuration);

	acc_sweep_configuration_repetition_mode_max_frequency_set(sweep_configuration);
	acc_sweep_configuration_requested_range_set(sweep_configuration, range_start, range_length);
	acc_sweep_configuration_sensor_set(sweep_configuration, sensor);

	acc_detector_distance_basic_handle_internal_t *detector_handle = acc_os_mem_alloc(sizeof(*detector_handle));

	if (detector_handle != NULL)
	{
		detector_handle->magic_number = MAGIC_NUMBER;
		detector_handle->envelope_handle = acc_service_create(envelope_configuration);

		if (detector_handle->envelope_handle != NULL)
		{
			acc_service_envelope_metadata_t envelope_metadata;
			acc_service_envelope_get_metadata(detector_handle->envelope_handle, &envelope_metadata);

			detector_handle->absolute_offset = envelope_metadata.free_space_absolute_offset;
			detector_handle->envelope_data_length = envelope_metadata.data_length;
			detector_handle->envelope_data = acc_os_mem_alloc(sizeof(*detector_handle->envelope_data) * detector_handle->envelope_data_length);
			detector_handle->distance_offset = envelope_metadata.actual_start_m;
			detector_handle->distance_slope = envelope_metadata.actual_length_m / (float)(envelope_metadata.data_length - 1);

			if (detector_handle->envelope_data != NULL)
			{
				acc_service_activate(detector_handle->envelope_handle);
			}
			else
			{
				acc_service_destroy(&detector_handle->envelope_handle);
				acc_os_mem_free(detector_handle);
				detector_handle = NULL;
				ACC_LOG_ERROR("Distance basic detector not possible to allocate");
			}
		}
		else
		{
			acc_os_mem_free(detector_handle);
			detector_handle = NULL;
			ACC_LOG_ERROR("Distance basic detector not possible to create");
		}
	}
	else
	{
		detector_handle = NULL;
		ACC_LOG_ERROR("Distance basic detector not possible to allocate");
	}

	acc_service_envelope_configuration_destroy(&envelope_configuration);

	return (acc_detector_distance_basic_handle_t*)detector_handle;
}


void acc_detector_distance_basic_destroy(acc_detector_distance_basic_handle_t **handle)
{
	if (handle != NULL)
	{
		if (handle_valid(*handle))
		{
			acc_service_deactivate((*handle)->envelope_handle);
			acc_os_mem_free((*handle)->envelope_data);
			acc_service_destroy(&(*handle)->envelope_handle);
			acc_os_mem_free(*handle);
			*handle = NULL;
		}
	}
}


acc_detector_distance_basic_reflection_t acc_detector_distance_basic_get_reflection(acc_detector_distance_basic_handle_t *handle)
{
	acc_detector_distance_basic_reflection_t reflection;
	reflection.distance = 0.0;
	reflection.amplitude = 0.0;

	if (handle_valid(handle))
	{
		uint16_t *envelope_data = handle->envelope_data;
		uint16_t envelope_data_length = handle->envelope_data_length;

		acc_service_envelope_result_info_t result_info;
		acc_service_envelope_get_next(handle->envelope_handle, envelope_data, envelope_data_length, &result_info);

		uint16_t reflection_index = get_reflection_index(envelope_data, envelope_data_length);

		reflection.amplitude = envelope_data[reflection_index];
		reflection.distance = INDEX_TO_DISTANCE_CONVERSION(reflection_index, handle->distance_slope, handle->distance_offset);
	}

	return reflection;
}


//-----------------------------
// Private definitions
//-----------------------------
bool handle_valid(acc_detector_distance_basic_handle_t *detector_handle)
{
	bool valid = true;

	if ((detector_handle == NULL) || (detector_handle->magic_number != MAGIC_NUMBER))
	{
		ACC_LOG_ERROR("Invalid detector motion handle");
		valid = false;
	}

	return valid;
}


uint16_t get_reflection_index(uint16_t *data, uint16_t data_length)
{
	uint16_t reflection_amplitude = 0;
	uint16_t reflection_index = 0;
	for (uint16_t i = 0; i < data_length; i++)
	{
		if (data[i] > reflection_amplitude)
		{
			reflection_amplitude = data[i];
			reflection_index = i;
		}
	}

	return reflection_index;
}
