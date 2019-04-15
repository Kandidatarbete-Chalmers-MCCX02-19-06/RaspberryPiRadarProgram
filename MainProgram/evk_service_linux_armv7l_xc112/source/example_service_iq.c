// Copyright (c) Acconeer AB, 2019
// All rights reserved

#include <complex.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "acc_device_os.h"
#include "acc_log.h"
#include "acc_rss.h"
#include "acc_service.h"
#include "acc_service_iq.h"
#include "acc_sweep_configuration.h"

#include "acc_version.h"


/**
 * @brief Example that shows how to use the IQ service
 *
 * This is an example on how the IQ service can be used.
 * The example executes as follows:
 *   - Activate Radar System Services (RSS)
 *   - Create an IQ service configuration (with blocking mode as default)
 *   - Create an IQ service using the previously created configuration
 *   - Activate the IQ service
 *   - Get the result and print it 5 times, where the last result is intentionally late
 *   - Deactivate and destroy the IQ service
 *   - Reconfigure the IQ service configuration with callback mode
 *   - Create and activate IQ service
 *   - Get the result and print it 2 times
 *   - Deactivate and destroy the IQ service
 *   - Destroy the IQ service configuration
 *   - Deactivate Radar System Services
 */


static acc_service_status_t execute_iq_with_blocking_calls(acc_service_configuration_t iq_configuration);
static acc_service_status_t execute_iq_with_callback(acc_service_configuration_t iq_configuration);
static void iq_callback(const acc_service_handle_t service_handle, const float complex *iq_data, const acc_service_iq_result_info_t *result_info, void *user_reference);
static void reconfigure_sweeps(acc_service_configuration_t iq_configuration);

typedef struct
{
	uint16_t                   data_length;
	uint_fast8_t               sweep_count;
} iq_callback_user_data_t;


int main(void)
{
	printf("Acconeer software version %s\n", ACC_VERSION);
	printf("Acconeer RSS version %s\n", acc_rss_version());

	if (!acc_rss_activate()) {
		return EXIT_FAILURE;
	}

	acc_service_configuration_t iq_configuration = acc_service_iq_configuration_create();

	if (iq_configuration == NULL) {
		printf("acc_service_iq_configuration_create() failed\n");
		return EXIT_FAILURE;
	}

	acc_service_status_t service_status;

	service_status = execute_iq_with_blocking_calls(iq_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_iq_with_blocking_calls() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		return EXIT_FAILURE;
	}

	reconfigure_sweeps(iq_configuration);

	service_status = execute_iq_with_callback(iq_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_iq_with_callback() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		return EXIT_FAILURE;
	}

	acc_service_iq_configuration_destroy(&iq_configuration);

	acc_rss_deactivate();

	return EXIT_SUCCESS;
}


acc_service_status_t execute_iq_with_blocking_calls(acc_service_configuration_t iq_configuration)
{
	acc_service_handle_t handle = acc_service_create(iq_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_iq_metadata_t iq_metadata;
	acc_service_iq_get_metadata(handle, &iq_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(iq_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(iq_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(iq_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((iq_metadata.actual_start_m + iq_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Data length: %u\n", (unsigned int)(iq_metadata.data_length));

	float complex iq_data[iq_metadata.data_length];
	acc_service_iq_result_info_t result_info;

	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		uint_fast8_t sweep_count = 5;

		while (sweep_count > 0) {
			service_status = acc_service_iq_get_next(handle, iq_data, iq_metadata.data_length, &result_info);

			if (service_status == ACC_SERVICE_STATUS_OK) {
				printf("IQ result_info->sequence_number: %u\n", (unsigned int)result_info.sequence_number);
				printf("IQ data in polar coordinates (r, phi):\n");
				for (uint_fast16_t index = 0; index < iq_metadata.data_length; index++) {
					if (index && !(index % 8)) {
						printf("\n");
					}
					printf("(%"PRIfloat", %"PRIfloat")\t", ACC_LOG_FLOAT_TO_INTEGER(cabsf(iq_data[index])), ACC_LOG_FLOAT_TO_INTEGER(cargf(iq_data[index])));
				}
				printf("\n");
			}
			else {
				printf("IQ data not properly retrieved\n");
			}

			sweep_count--;

			// Show what happens if application is late
			if (sweep_count == 1) {
				acc_os_sleep_us(200000);
			}
		}

		service_status = acc_service_deactivate(handle);
	}
	else {
		printf("acc_service_activate() %u => %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
	}

	acc_service_destroy(&handle);

	return service_status;
}


acc_service_status_t execute_iq_with_callback(acc_service_configuration_t iq_configuration)
{
	iq_callback_user_data_t iq_callback_user_data;

	acc_service_iq_iq_float_callback_set(iq_configuration, &iq_callback, &iq_callback_user_data);

	acc_service_handle_t handle = acc_service_create(iq_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_iq_metadata_t iq_metadata;
	acc_service_iq_get_metadata(handle, &iq_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(iq_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(iq_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(iq_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((iq_metadata.actual_start_m + iq_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Data length: %u\n", (unsigned int)(iq_metadata.data_length));

	// Configure callback user data
	iq_callback_user_data.sweep_count = 2;
	iq_callback_user_data.data_length = iq_metadata.data_length;

	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		while (iq_callback_user_data.sweep_count > 0) {
			acc_os_sleep_us(200);
		}

		service_status = acc_service_deactivate(handle);
	}
	else {
		printf("acc_service_activate() %u => %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
	}

	acc_service_destroy(&handle);

	return service_status;
}


void iq_callback(const acc_service_handle_t service_handle, const float complex *iq_data, const acc_service_iq_result_info_t *result_info, void *user_reference)
{
	ACC_UNUSED(service_handle);

	if (result_info->sensor_communication_error)
	{
		// Handle error, for example restart service
	}

	iq_callback_user_data_t *iq_callback_user_data = user_reference;

	if (iq_callback_user_data->sweep_count > 0) {
		printf("IQ callback result_info->sequence_number: %u\n", (unsigned int)result_info->sequence_number);
		printf("IQ callback data in cartesian coordinates (a, b):\n");
		for (uint_fast16_t index = 0; index < iq_callback_user_data->data_length; index++) {
			if (index && !(index % 8)) {
				printf("\n");
			}
			printf("(%"PRIfloat", %"PRIfloat")\t", ACC_LOG_FLOAT_TO_INTEGER(crealf(iq_data[index])), ACC_LOG_FLOAT_TO_INTEGER(cimagf(iq_data[index])));
		}
		printf("\n");

		iq_callback_user_data->sweep_count--;
	}
}


void reconfigure_sweeps(acc_service_configuration_t iq_configuration)
{
	acc_sweep_configuration_t sweep_configuration = acc_service_get_sweep_configuration(iq_configuration);

	if (sweep_configuration == NULL) {
		printf("Sweep configuration not available\n");
	}
	else {
		float start_m = 0.4;
		float length_m = 0.5;
		float sweep_frequency_hz = 100;

		acc_sweep_configuration_requested_start_set(sweep_configuration, start_m);
		acc_sweep_configuration_requested_length_set(sweep_configuration, length_m);

		acc_sweep_configuration_repetition_mode_streaming_set(sweep_configuration, sweep_frequency_hz);
	}
}
