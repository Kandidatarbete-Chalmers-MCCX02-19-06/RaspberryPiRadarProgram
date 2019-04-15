// Copyright (c) Acconeer AB, 2018
// All rights reserved

#ifndef ACC_SERVICE_H_
#define ACC_SERVICE_H_

#include <stdint.h>

#include "acc_sweep_configuration.h"

/**
 * @defgroup Services Services
 *
 * @brief Radar services provided by Acconeer
 *
 * @defgroup Generic Generic Service API
 * @ingroup Services
 *
 * @brief Generic service API description
 *
 * @{
 */


/**
 * @brief Return status for service methods
 */
typedef enum
{
	ACC_SERVICE_STATUS_OK,
	ACC_SERVICE_STATUS_FAILURE_UNSPECIFIED
} acc_service_status_enum_t;
typedef uint32_t acc_service_status_t;


/**
 * @brief Generic service configuration container
 */
struct acc_service_configuration;
typedef struct acc_service_configuration *acc_service_configuration_t;


/**
 * @brief Generic service handle
 */
struct acc_service_handle;
typedef struct acc_service_handle *acc_service_handle_t;


/**
 * @brief Return a string with a service status name
 *
 * @param[in] status The service status to get the name for
 * @return Status string
 */
extern char *acc_service_status_name_get(acc_service_status_t status);


/**
 * @brief Create a service with the provided configuration
 *
 * Only one service may exist for a specific sensor at any given time and
 * invalid configurations will not allow for service creation.
 *
 * @param[in] configuration The service configuration to create a service with
 * @return Service handle, NULL if service was not possible to create
 */
extern acc_service_handle_t acc_service_create(acc_service_configuration_t configuration);


/**
 * @brief Activate the service associated with the provided handle
 *
 * @param[in] service_handle The service handle for the service to activate
 * @return Service status
 */
extern acc_service_status_t acc_service_activate(acc_service_handle_t service_handle);


/**
 * @brief Deactivate the service associated with the provided handle
 *
 * @param[in] service_handle The service handle for the service to deactivate
 * @return Service status
 */
extern acc_service_status_t acc_service_deactivate(acc_service_handle_t service_handle);


/**
 * @brief Destroy a service identified with the provided service handle
 *
 * Destroy the context of a service allowing another service to be created using the
 * same resources. The service handle reference is set to NULL after destruction.
 *
 * @param[in] service_handle A reference to the service handle to destroy
 */
extern void acc_service_destroy(acc_service_handle_t *service_handle);


/**
 * @brief Retrieve a sweep configuration from a service configuration
 *
 * @param[in] service_configuration The service configuration to get a sweep configuration from
 * @return Sweep configuration, NULL if the service configuration does not contain a sweep configuration
 */
extern acc_sweep_configuration_t acc_service_get_sweep_configuration(acc_service_configuration_t service_configuration);


/**
 * @brief Check if the status of a service is active or not
 *
 * @param[in] service_handle The service handle for the service to check the status for
 * @return True if the service is active, false otherwise
 */
extern bool acc_service_is_service_active(acc_service_handle_t service_handle);


/**
 * @}
 */

#endif
