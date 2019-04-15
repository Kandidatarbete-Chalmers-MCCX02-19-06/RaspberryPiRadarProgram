// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#ifndef ACC_SERVICE_POWER_BINS_H_
#define ACC_SERVICE_POWER_BINS_H_

#include <stdint.h>

#include "acc_service.h"
#include "acc_sweep_configuration.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @defgroup Power Power Bins Service
 * @ingroup Services
 *
 * @brief Power Bins service API description
 *
 * @{
 */


/**
 * @brief Metadata for the power bins service
 */
typedef struct
{
	float        free_space_absolute_offset;
	float        actual_start_m;
	float        actual_length_m;
	uint16_t     actual_bin_count;
} acc_service_power_bins_metadata_t;


/**
 * @brief Metadata for each result provided by the power bins service
 */
typedef struct
{
	bool     sensor_communication_error;
	uint32_t sequence_number;
} acc_service_power_bins_result_info_t;


/**
 * @brief Definition of a power bins callback function
 */
typedef void (acc_power_bins_callback_t)(const acc_service_handle_t service_handle, const float *power_bins_data, const acc_service_power_bins_result_info_t *result_info, void *user_reference);


/**
 * @brief Create a configuration for a power bins service
 *
 * @return Service configuration, NULL if creation was not possible
 */
extern acc_service_configuration_t acc_service_power_bins_configuration_create(void);


/**
 * @brief Destroy a power bins configuration
 *
 * Destroy a power bins configuration that is no longer needed, may be done even if a
 * service has been created with the specific configuration and has not yet been destroyed.
 * The service configuration reference is set to NULL after destruction.
 *
 * @param[in] service_configuration The configuration to destroy, set to NULL
 */
extern void acc_service_power_bins_configuration_destroy(acc_service_configuration_t *service_configuration);


/**
 * @brief Get the requested bin count
 *
 * @param[in] service_configuration The service configuration to get the requested bin count from
 * @return Requested bin count
 */
extern uint16_t acc_service_power_bins_requested_bin_count_get(acc_service_configuration_t service_configuration);


/**
 * @brief Set the requested bin count
 *
 * @param[in] service_configuration The service configuration to set the requested bin count in
 * @param[in] requested_bin_count The requested bin count
 */
extern void acc_service_power_bins_requested_bin_count_set(acc_service_configuration_t service_configuration, uint16_t requested_bin_count);


/**
 * @brief Set a callback to receive power bins results
 *
 * If a callback is used, power bins results are indicated by calling the function that is set.
 * Within the callback it is only allowed to copy the data to a application memory to allow the best
 * possible service execution. Setting the callback as NULL disables callback operation.
 *
 * @param[in] service_configuration The configuration to set a callback for
 * @param[in] power_bins_callback The callback function to set
 * @param[in] user_reference A user chosen reference that will be provided when calling the callback
 */
extern void acc_service_power_bins_power_bins_callback_set(acc_service_configuration_t service_configuration, acc_power_bins_callback_t *power_bins_callback, void *user_reference);


/**
 * @brief Get service metadata
 *
 * May only be called after a service has been created.
 *
 * @param[in] handle The service handle for the service to get metadata for
 * @param[out] metadata Metadata results are provided in this parameter
 */
extern void acc_service_power_bins_get_metadata(acc_service_handle_t handle, acc_service_power_bins_metadata_t *metadata);


/**
 * @brief Retrieve the next result from the service
 *
 * May only be called after a service has been activated to retrieve the next result, blocks
 * the application until a result is ready.
 * It is not possible to use this blocking call and callbacks simultaneously.
 *
 * @param[in] handle The service handle for the service to get the next result for
 * @param[out] power_bins_data Power bins result
 * @param[in] power_bins_data_length The length of the buffer provided for the result
 * @param[in] result_info IQ result info
 * @return Service status
 */
extern acc_service_status_t acc_service_power_bins_get_next(acc_service_handle_t handle, float *power_bins_data, uint16_t power_bins_data_length, acc_service_power_bins_result_info_t *result_info);


/**
 * @brief Execute service one time
 *
 * Activates service, produces one result and then deactivates the service. Blocks the
 * application until a service result has been produced. Will not work if service is
 * already active.
 *
 * @param[in] handle The service handle for the service to execute
 * @param[out] power_bins_data Power bins result
 * @param[in] power_bins_data_length The length of the buffer provided for the result
 * @param[in] result_info IQ result info
 * @return Service status
 */
extern acc_service_status_t acc_service_power_bins_execute_once(acc_service_handle_t handle, float *power_bins_data, uint16_t power_bins_data_length, acc_service_power_bins_result_info_t *result_info);


/**
 * @}
 */

#ifdef __cplusplus
}
#endif

#endif
