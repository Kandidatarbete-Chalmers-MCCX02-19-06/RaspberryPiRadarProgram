// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#ifndef ACC_RSS_H_
#define ACC_RSS_H_

#include <stdbool.h>

#include "acc_definitions.h"


/**
 * @defgroup RSS Radar System Services, RSS
 *
 * @brief Acconeer Radar System Services, RSS
 *
 * @{
 */


/**
 * @brief Activate the Acconeer Radar System Services, RSS
 *
 * The call to this function must only be made from one thread. After this, full thread safety across
 * all Acconeer services is guaranteed.
 *
 * @note Function will in future look like: acc_rss_activate(acc_hal_t *hal).
 * Activation using acc_rss_activate_with_hal is prefered until signature change is done.
 *
 * @return True if RSS is activated
 */
extern bool acc_rss_activate(void);


/**
 * @brief Activate the Acconeer Radar System Services, RSS, with HAL
 *
 * The call to this function must only be made from one thread. After this, full thread safety across
 * all Acconeer services is guaranteed.
 *
 * @return True if RSS is activated
 */
extern bool acc_rss_activate_with_hal(acc_hal_t *hal);


/**
 * @brief Deactivate the Acconeer Radar System Services, RSS
 */
extern void acc_rss_deactivate(void);


/**
 * @brief Get the Acconeer RSS version
 *
 * @return Version
 */
extern const char *acc_rss_version(void);


/**
 * @brief Get the sensor calibration context
 *
 * Must be called after RSS has been activated.
 * A calibration will be done if it hasn't been done yet for the specific sensor.
 *
 * @param[in] sensor The sensor to get the context for
 * @param[out] calibration_context Reference to struct where the context will be stored
 * @return True if successful, false otherwise
 */
extern bool acc_rss_calibration_context_get(acc_sensor_id_t sensor, acc_calibration_context_t *calibration_context);


/**
 * @brief Set a previously saved sensor calibration context
 *
 * Must be called after RSS has been activated.
 * No active service is allowed on the sensor when setting the context.
 *
 * @param[in] sensor The sensor to set the context on
 * @param[in] calibration_context The calibration context to set
 *
 * @return True if successful, false otherwise
 */
extern bool acc_rss_calibration_context_set(acc_sensor_id_t sensor, acc_calibration_context_t *calibration_context);


/**
 * @brief Reset a calibration done on the specific sensor (or remove a previously set calibration context)
 *
 * No active service is allowed on the sensor when resetting the calibration
 *
 * @param[in] sensor The sensor to reset the calibration on
 *
 * @return True if successful, false otherwise
 */
extern bool acc_rss_calibration_reset(acc_sensor_id_t sensor);


/**
 * @}
 */

#endif
