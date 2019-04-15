// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#ifndef ACC_SERVICE_IQ_H_
#define ACC_SERVICE_IQ_H_

#include <complex.h>
#include <stdint.h>

#include "acc_service.h"
#include "acc_sweep_configuration.h"

/**
 * @defgroup IQ IQ Service
 * @ingroup Services
 *
 * @brief IQ Service API description
 *
 * @{
 */


/**
 * @brief Metadata for the iq service
 */
typedef struct
{
	float        free_space_absolute_offset;
	float        actual_start_m;
	float        actual_length_m;
	uint16_t     data_length;
} acc_service_iq_metadata_t;


/**
 * @brief Metadata for each result provided by the iq service
 */
typedef struct
{
	bool     sensor_communication_error;
	uint32_t sequence_number;
} acc_service_iq_result_info_t;


/**
 * @brief Definition of an iq callback function providing iq data as float (complex)
 */
typedef void (acc_iq_float_callback_t)(const acc_service_handle_t service_handle, const float complex *iq_data, const acc_service_iq_result_info_t *result_info, void *user_reference);


/**
 * @brief Create a configuration for an iq service
 *
 * @return Service configuration, NULL if creation was not possible
 */
extern acc_service_configuration_t acc_service_iq_configuration_create(void);


/**
 * @brief Destroy an iq configuration
 *
 * Destroy an iq configuration that is no longer needed, may be done even if a
 * service has been created with the specific configuration and has not yet been destroyed.
 * The service configuration reference is set to NULL after destruction.
 *
 * @param[in] service_configuration The configuration to destroy, set to NULL
 */
extern void acc_service_iq_configuration_destroy(acc_service_configuration_t *service_configuration);


/**
 * @brief Get running average factor
 *
 * The running average factor is the factor of which the most recent sweep is weighed against previous sweeps.
 * Valid range is between 0.0 and 1.0 where 0.0 means that no history is weighed in, i.e filtering is effectively disabled.
 * A factor of 1.0 means that the most recent sweep has no effect on the result,
 * which will result in that the first sweep is forever received as the result.
 *
 * @param[in] service_configuration The configuration to set the running average factor for
 * @return Running average factor
 */
extern float acc_service_iq_running_average_factor_get(acc_service_configuration_t service_configuration);


/**
 * @brief Set running average factor
 *
 * The running average factor is the factor of which the most recent sweep is weighed against previous sweeps.
 * Valid range is between 0.0 and 1.0 where 0.0 means that no history is weighed in, i.e filtering is effectively disabled.
 * A factor of 1.0 means that the most recent sweep has no effect on the result,
 * which will result in that the first sweep is forever received as the result.
 *
 * @param[in] service_configuration The configuration to set the running average factor for
 * @param[in] factor The running average factor to set
 */
extern void acc_service_iq_running_average_factor_set(acc_service_configuration_t service_configuration, float factor);


/**
 * @brief Set a callback to receive iq results in iq float format
 *
 * If a callback is used, iq results are indicated by calling the function that is set.
 * Within the callback it is only allowed to copy the data to a application memory to allow the best
 * possible service execution. Setting the callback to NULL sets the service in blocking mode and results
 * have to be retrieved through calling the acc_service_iq_get_next function.
 *
 * @param[in] service_configuration The configuration to set a callback for
 * @param[in] callback The callback function to set
 * @param[in] user_reference A client chosen reference that will be provided when calling the callback
 */
extern void acc_service_iq_iq_float_callback_set(acc_service_configuration_t service_configuration, acc_iq_float_callback_t *callback, void *user_reference);


/**
 * @brief Get service metadata
 *
 * May only be called after a service has been created.
 *
 * @param[in] handle The service handle for the service to get metadata for
 * @param[out] metadata Metadata results are provided in this parameter
 */
extern void acc_service_iq_get_metadata(acc_service_handle_t handle, acc_service_iq_metadata_t *metadata);


/**
 * @brief Retrieve the next result from the service
 *
 * May only be called after a service has been activated to retrieve the next result, blocks
 * the application until a result is ready.
 * It is not possible to use this blocking call and callbacks simultaneously.
 *
 * @param[in] handle The service handle for the service to get the next result for
 * @param[out] iq_data IQ data result
 * @param[in] iq_data_length The length of the buffer provided for the result
 * @param[in] result_info IQ result info
 * @return Service status
 */
extern acc_service_status_t acc_service_iq_get_next(acc_service_handle_t handle, float complex *iq_data, uint16_t iq_data_length, acc_service_iq_result_info_t *result_info);


/**
 * @brief Execute service one time
 *
 * Activates service, produces one result and then deactivates the service. Blocks the
 * application until a service result has been produced. Will not work if service is
 * already active.
 *
 * @param[in] handle The service handle for the service to execute
 * @param[out] iq_data IQ data result
 * @param[in] iq_data_length The length of the buffer provided for the result
 * @param[in] result_info IQ result info
 * @return Service status
 */
extern acc_service_status_t acc_service_iq_execute_once(acc_service_handle_t handle, float complex *iq_data, uint16_t iq_data_length, acc_service_iq_result_info_t *result_info);


/**
 * @}
 */

#endif
