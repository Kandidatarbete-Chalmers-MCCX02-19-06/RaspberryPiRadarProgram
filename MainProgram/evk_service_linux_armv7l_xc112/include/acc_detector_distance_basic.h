// Copyright (c) Acconeer AB, 2018
// All rights reserved

#ifndef ACC_DETECTOR_DISTANCE_BASIC_H_
#define ACC_DETECTOR_DISTANCE_BASIC_H_

#include "acc_definitions.h"
#include "acc_service.h"
#include "acc_service_envelope.h"
#include "acc_sweep_configuration.h"

/**
 * @defgroup Distance_Basic Distance Basic Detector
 * @ingroup Detectors
 *
 * @brief Distance basic detector API description
 *
 * @{
 */


/**
 * @brief Detector handle to be used when getting results after creation
 */
typedef struct acc_detector_distance_basic_handle acc_detector_distance_basic_handle_t;


/**
 * @brief Struct for a reflection
 */
typedef struct
{
	float    distance;
	uint16_t amplitude;
} acc_detector_distance_basic_reflection_t;


/**
 * @brief Create a distance basic detector
 *
 * @param[in] sensor The sensor where the detector will get its result from
 * @param[in] range_start The start range in meters where the detector will look for reflections
 * @param[in] range_length The range window length where the detector will look for reflections
 * @return Detector handle, NULL if creation failed
 */
extern acc_detector_distance_basic_handle_t *acc_detector_distance_basic_create(acc_sensor_id_t sensor, float range_start, float range_length);


/**
 * @brief Destroy a distance basic detector
 *
 * The distance basic detector handle reference is set to NULL after destruction.
 * If NULL is sent in, nothing happens.
 *
 * @param[in] handle The detector handle to destroy, will be set to NULL
 */
extern void acc_detector_distance_basic_destroy(acc_detector_distance_basic_handle_t **handle);


/**
 * @brief Get a reflection from the distance basic detector
 *
 * May only be called after the detector has been created, blocks the application until a result is ready.
 *
 * @param[in] handle The detector handle to get the next result for
 * @return The resulting reflection, if the reflection is 0, somehing went wrong or no reflection was detected
 */
extern acc_detector_distance_basic_reflection_t acc_detector_distance_basic_get_reflection(acc_detector_distance_basic_handle_t *handle);


/**
 * @}
 */

#endif
