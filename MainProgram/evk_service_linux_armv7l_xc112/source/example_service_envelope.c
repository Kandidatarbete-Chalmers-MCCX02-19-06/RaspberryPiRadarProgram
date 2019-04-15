// Copyright (c) Acconeer AB, 2015-2019
// All rights reserved

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "acc_device_os.h"
#include "acc_rss.h"
#include "acc_service.h"
#include "acc_service_envelope.h"
#include "acc_sweep_configuration.h"

#include "acc_version.h"


/**
 * @brief Example that shows how to use the envelope service
 *
 * This is an example on how the envelope service can be used.
 * The example executes as follows:
 *   - Activate Radar System Services (RSS)
 *   - Create an envelope service configuration (with blocking mode as default)
 *   - Create an envelope service using the previously created configuration
 *   - Activate the envelope service
 *   - Get the result and print it 5 times, where the last result is intentionally late
 *   - Deactivate and destroy the envelope service
 *   - Reconfigure the envelope service configuration with callback mode
 *   - Create and activate envelope service
 *   - Get the result and print it 2 times
 *   - Deactivate and destroy the envelope service
 *   - Destroy the envelope service configuration
 *   - Deactivate Radar System Services
 */


typedef struct
{
	uint16_t                   data_length;
	uint_fast8_t               sweep_count;
} envelope_callback_user_data_t;

static acc_service_status_t execute_envelope_with_blocking_calls(acc_service_configuration_t envelope_configuration);
static acc_service_status_t execute_envelope_with_callback(acc_service_configuration_t envelope_configuration);
static void envelope_callback(const acc_service_handle_t service_handle, const uint16_t *envelope_data, const acc_service_envelope_result_info_t *result_info, void *user_reference);
static void reconfigure_sweeps(acc_service_configuration_t envelope_configuration);
static bool any_sweeps_left(const envelope_callback_user_data_t *callback_user_data);


static acc_os_mutex_t callback_data_lock;


int main(void)
{
	printf("Acconeer software version %s\n", ACC_VERSION);
	printf("Acconeer RSS version %s\n", acc_rss_version());

	if (!acc_rss_activate()) {
		return EXIT_FAILURE;
	}

	acc_service_configuration_t envelope_configuration = acc_service_envelope_configuration_create();

	if (envelope_configuration == NULL) {
		printf("acc_service_envelope_configuration_create() failed\n");
		return EXIT_FAILURE;
	}

	acc_service_status_t service_status;

	service_status = execute_envelope_with_blocking_calls(envelope_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_envelope_with_blocking_calls() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		acc_service_envelope_configuration_destroy(&envelope_configuration);
		return EXIT_FAILURE;
	}

	reconfigure_sweeps(envelope_configuration);

	service_status = execute_envelope_with_callback(envelope_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_envelope_with_callback() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		acc_service_envelope_configuration_destroy(&envelope_configuration);
		acc_rss_deactivate();
		return EXIT_FAILURE;
	}

	acc_service_envelope_configuration_destroy(&envelope_configuration);

	acc_rss_deactivate();

	return EXIT_SUCCESS;
}


acc_service_status_t execute_envelope_with_blocking_calls(acc_service_configuration_t envelope_configuration)
{
	acc_service_handle_t handle = acc_service_create(envelope_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_envelope_metadata_t envelope_metadata;
	acc_service_envelope_get_metadata(handle, &envelope_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(envelope_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(envelope_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(envelope_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((envelope_metadata.actual_start_m + envelope_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Data length: %u\n", (unsigned int)(envelope_metadata.data_length));

	uint16_t envelope_data[envelope_metadata.data_length];

	acc_service_envelope_result_info_t result_info;
	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		uint_fast8_t sweep_count = 5;

		while (sweep_count > 0) {
			service_status = acc_service_envelope_get_next(handle, envelope_data, envelope_metadata.data_length, &result_info);

			if (service_status == ACC_SERVICE_STATUS_OK) {
				printf("Envelope result_info.sequence_number: %u\n", (unsigned int)result_info.sequence_number);
				printf("Envelope data:\n");
				for (uint_fast16_t index = 0; index < envelope_metadata.data_length; index++) {
					if (index && !(index % 8)) {
						printf("\n");
					}
					printf("%6u", (unsigned int)(envelope_data[index] + 0.5));
				}
				printf("\n");
			}
			else {
				printf("Envelope data not properly retrieved\n");
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


acc_service_status_t execute_envelope_with_callback(acc_service_configuration_t envelope_configuration)
{
	envelope_callback_user_data_t callback_user_data;

	acc_service_envelope_envelope_callback_set(envelope_configuration, &envelope_callback, &callback_user_data);

	callback_data_lock = acc_os_mutex_create();
	if (callback_data_lock == NULL) {
		printf("Failed to create mutex.\n");
		return EXIT_FAILURE;
	}

	acc_service_handle_t handle = acc_service_create(envelope_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_envelope_metadata_t envelope_metadata;
	acc_service_envelope_get_metadata(handle, &envelope_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(envelope_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(envelope_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(envelope_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((envelope_metadata.actual_start_m + envelope_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Data length: %u\n", (unsigned int)(envelope_metadata.data_length));

	// Configure callback user data
	callback_user_data.sweep_count = 2;
	callback_user_data.data_length = envelope_metadata.data_length;

	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		while (any_sweeps_left(&callback_user_data)) {
			acc_os_sleep_us(200);
		}

		service_status = acc_service_deactivate(handle);
	}
	else {
		printf("acc_service_activate() %u => %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
	}

	acc_service_destroy(&handle);

	acc_os_mutex_destroy(callback_data_lock);

	return service_status;
}


void envelope_callback(const acc_service_handle_t service_handle, const uint16_t *envelope_data, const acc_service_envelope_result_info_t *result_info, void *user_reference)
{
	ACC_UNUSED(service_handle);

	if (result_info->sensor_communication_error)
	{
		// Handle error, for example restart service
	}

	envelope_callback_user_data_t *callback_user_data = user_reference;

	acc_os_mutex_lock(callback_data_lock);

	if (callback_user_data->sweep_count > 0) {
		printf("Envelope callback result_info->sequence_number: %u\n", (unsigned int)result_info->sequence_number);
		printf("Envelope callback data:\n");
		for (uint_fast16_t index = 0; index < callback_user_data->data_length; index++) {
			if (index && !(index % 8)) {
				printf("\n");
			}
			printf("%6u", (unsigned int)(envelope_data[index]));
		}
		printf("\n");

		callback_user_data->sweep_count--;
	}

	acc_os_mutex_unlock(callback_data_lock);
}


static bool any_sweeps_left(const envelope_callback_user_data_t *callback_user_data)
{
	acc_os_mutex_lock(callback_data_lock);
	bool sweeps_left = callback_user_data->sweep_count > 0;
	acc_os_mutex_unlock(callback_data_lock);

	return sweeps_left;
}


void reconfigure_sweeps(acc_service_configuration_t envelope_configuration)
{
	acc_sweep_configuration_t sweep_configuration = acc_service_get_sweep_configuration(envelope_configuration);

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
