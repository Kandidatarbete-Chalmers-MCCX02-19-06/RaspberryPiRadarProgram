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
#include "acc_service_power_bins.h"
#include "acc_sweep_configuration.h"

#include "acc_version.h"


/**
 * @brief Example that shows how to use the Power Bins service
 *
 * This is an example on how the Power Bins service can be used.
 * The example executes as follows:
 *   - Activate Radar System Services (RSS)
 *   - Create a Power Bins service configuration (with blocking mode as default)
 *   - Create a Power Bins service using the previously created configuration
 *   - Activate the Power Bins service
 *   - Get the result and print it 5 times, where the last result is intentionally late
 *   - Deactivate and destroy the Power Bins service
 *   - Reconfigure the Power Bins service configuration with callback mode
 *   - Create and activate Power Bins service
 *   - Get the result and print it 2 times
 *   - Deactivate and destroy the Power Bins service
 *   - Destroy the Power Bins service configuration
 *   - Deactivate Radar System Services
 */


static acc_service_status_t execute_power_bins_with_blocking_calls(acc_service_configuration_t power_bins_configuration);
static acc_service_status_t execute_power_bins_with_callback(acc_service_configuration_t power_bins_configuration);
static void power_bins_callback(const acc_service_handle_t service_handle, const float *power_bins_data, const acc_service_power_bins_result_info_t *result_info, void *user_reference);
static void reconfigure_sweeps(acc_service_configuration_t envelope_configuration);


typedef struct
{
	uint16_t                   bin_count;
	uint_fast8_t               sweep_count;
} power_bins_callback_user_data_t;


int main(int argc, char *argv[])
{
	ACC_UNUSED(argc);
	ACC_UNUSED(argv);

	printf("Acconeer software version %s\n", ACC_VERSION);
	printf("Acconeer RSS version %s\n", acc_rss_version());

	if (!acc_rss_activate()) {
		return EXIT_FAILURE;
	}

	acc_service_configuration_t power_bins_configuration = acc_service_power_bins_configuration_create();

	if (power_bins_configuration == NULL) {
		printf("acc_service_power_bins_configuration_create() failed\n");
		return EXIT_FAILURE;
	}

	acc_service_status_t service_status;

	service_status = execute_power_bins_with_blocking_calls(power_bins_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_power_bins_with_blocking_calls() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		acc_service_power_bins_configuration_destroy(&power_bins_configuration);
		return EXIT_FAILURE;
	}

	reconfigure_sweeps(power_bins_configuration);

	service_status = execute_power_bins_with_callback(power_bins_configuration);

	if (service_status != ACC_SERVICE_STATUS_OK) {
		printf("execute_power_bins_with_callback() => (%u) %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
		acc_service_power_bins_configuration_destroy(&power_bins_configuration);
		return EXIT_FAILURE;
	}

	acc_service_power_bins_configuration_destroy(&power_bins_configuration);

	acc_rss_deactivate();

	return EXIT_SUCCESS;
}


acc_service_status_t execute_power_bins_with_blocking_calls(acc_service_configuration_t power_bins_configuration)
{
	acc_service_handle_t handle = acc_service_create(power_bins_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_power_bins_metadata_t power_bins_metadata;
	acc_service_power_bins_get_metadata(handle, &power_bins_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(power_bins_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(power_bins_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(power_bins_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((power_bins_metadata.actual_start_m + power_bins_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Bin count: %u\n", (unsigned int)(power_bins_metadata.actual_bin_count));

	float power_bins_data[power_bins_metadata.actual_bin_count];

	acc_service_power_bins_result_info_t result_info;
	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		uint_fast8_t sweep_count = 5;

		while (sweep_count > 0) {
			service_status = acc_service_power_bins_get_next(handle, power_bins_data, power_bins_metadata.actual_bin_count, &result_info);

			if (service_status == ACC_SERVICE_STATUS_OK) {
				printf("Power_bins result_info.sequence_number: %u\n", (unsigned int)result_info.sequence_number);
				printf("Power_bins data:\n");
				for (uint_fast16_t index = 0; index < power_bins_metadata.actual_bin_count; index++) {
					printf("%u\t%u", (unsigned int)index, (unsigned int)(power_bins_data[index] + 0.5));
				}
				printf("\n");
			}
			else {
				printf("Power_bins data not properly retrieved\n");
			}

			sweep_count--;
		}

		service_status = acc_service_deactivate(handle);
	}
	else {
		printf("acc_service_activate() %u => %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
	}

	acc_service_destroy(&handle);

	return service_status;
}


acc_service_status_t execute_power_bins_with_callback(acc_service_configuration_t power_bins_configuration)
{
	power_bins_callback_user_data_t callback_user_data;

	acc_service_power_bins_requested_bin_count_set(power_bins_configuration, 8);
	acc_service_power_bins_power_bins_callback_set(power_bins_configuration, &power_bins_callback, &callback_user_data);

	acc_service_handle_t handle = acc_service_create(power_bins_configuration);

	if (handle == NULL) {
		printf("acc_service_create failed\n");
		return ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED;
	}

	acc_service_power_bins_metadata_t power_bins_metadata;
	acc_service_power_bins_get_metadata(handle, &power_bins_metadata);

	printf("Free space absolute offset: %u mm\n", (unsigned int)(power_bins_metadata.free_space_absolute_offset * 1000.0 + 0.5));
	printf("Actual start: %u mm\n", (unsigned int)(power_bins_metadata.actual_start_m * 1000.0 + 0.5));
	printf("Actual length: %u mm\n", (unsigned int)(power_bins_metadata.actual_length_m * 1000.0 + 0.5));
	printf("Actual end: %u mm\n", (unsigned int)((power_bins_metadata.actual_start_m + power_bins_metadata.actual_length_m) * 1000.0 + 0.5));
	printf("Bin count: %u\n", (unsigned int)(power_bins_metadata.actual_bin_count));

	// Configure callback user data
	callback_user_data.sweep_count = 5;
	callback_user_data.bin_count = power_bins_metadata.actual_bin_count;

	acc_service_status_t service_status = acc_service_activate(handle);

	if (service_status == ACC_SERVICE_STATUS_OK) {
		while (callback_user_data.sweep_count > 0) {
			acc_os_sleep_us(200);
		}

		service_status = acc_service_deactivate(handle);
	}
	else {
		printf("acc_service_activate() %u => %s\n", (unsigned int)service_status, acc_service_status_name_get(service_status));
	}

	if (handle != NULL) {
		acc_service_destroy(&handle);
	}

	return service_status;
}


void power_bins_callback(const acc_service_handle_t service_handle, const float *power_bins_data, const acc_service_power_bins_result_info_t *result_info, void *user_reference)
{
	ACC_UNUSED(service_handle);

	if (result_info->sensor_communication_error)
	{
		// Handle error, for example restart service
	}

	power_bins_callback_user_data_t *callback_user_data = user_reference;

	if (callback_user_data->sweep_count > 0) {
		printf("Power_bins callback result_info->sequence_number: %u\n", (unsigned int)result_info->sequence_number);
		printf("Power_bins callback data:\n");
		for (uint_fast16_t index = 0; index < callback_user_data->bin_count; index++) {
			printf("%u\t%u", (unsigned int)index, (unsigned int)(power_bins_data[index] + 0.5));
		}
		printf("\n");

		callback_user_data->sweep_count--;
	}
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
