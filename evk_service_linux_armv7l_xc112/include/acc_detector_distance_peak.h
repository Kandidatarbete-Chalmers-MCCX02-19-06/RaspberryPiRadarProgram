// Copyright (c) Acconeer AB, 2018
// All rights reserved

#ifndef ACC_DETECTOR_DISTANCE_PEAK_H_
#define ACC_DETECTOR_DISTANCE_PEAK_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_sweep_configuration.h"


/**
 * @defgroup Detectors Detectors
 *
 * @brief Detectors provided by Acconeer. Based on Acconeer services.
 *
 * @defgroup Distance_Peak Distance Peak Detector
 * @ingroup Detectors
 *
 * @brief Distance peak detector API description
 *
 * @{
 */


/**
 * @brief Distance detector error codes
 */
typedef enum
{
	ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS,
	ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE,
} acc_detector_distance_peak_status_enum_t;
typedef uint32_t acc_detector_distance_peak_status_t;

/**
 * @brief Predefined profiles allowing fast setup of a distance detector configuration
 *
 * A profile configures the RX/TX path in the sensor and sets all other configuration
 * parameters to a predefined value
 */
typedef enum
{
	ACC_DETECTOR_DISTANCE_PEAK_PROFILE_MAXIMIZE_DEPTH_RESOLUTION,
	ACC_DETECTOR_DISTANCE_PEAK_PROFILE_MAXIMIZE_SNR,
	ACC_DETECTOR_DISTANCE_PEAK_PROFILE_MAX,
	ACC_DETECTOR_DISTANCE_PEAK_PROFILE_DEFAULT = ACC_DETECTOR_DISTANCE_PEAK_PROFILE_MAXIMIZE_DEPTH_RESOLUTION
} acc_detector_distance_peak_profile_enum_t;
typedef uint32_t acc_detector_distance_peak_profile_t;

/**
 * @brief Distance detector configuration
*/
struct acc_detector_distance_peak_configuration;
typedef struct acc_detector_distance_peak_configuration *acc_detector_distance_peak_configuration_t;


/**
 * @brief Distance detector handle
 */
struct acc_detector_distance_peak_handle;
typedef struct acc_detector_distance_peak_handle *acc_detector_distance_peak_handle_t;


/**
 * @brief Reflection struct for the distance detector reflections
 */
typedef struct {
	float		distance;
	uint16_t	amplitude;
} acc_detector_distance_peak_reflection_t;

/**
 * @brief Metadata for the distance detector
 */
typedef struct
{
	float	free_space_absolute_offset;
	float	actual_start_m;
	float	actual_length_m;
} acc_detector_distance_peak_metadata_t;


/**
 * @brief Metadata for each result provided by the distance detector
 */
typedef struct
{
	uint32_t	sequence_number;
} acc_detector_distance_peak_result_info_t;


/**
 * @brief Create a configuration for a distance detector
 *
 * @return A reference to the distance detector configuration, NULL if creation was not possible
 */
extern acc_detector_distance_peak_configuration_t acc_detector_distance_peak_configuration_create(void);


/**
 * @brief Destroy a distance detector configuration
 *
 * Destroy a distance detector configuration that is no longer needed, may be done even if a
 * detector has been created with the specific configuration and has not yet been destroyed.
 * The detector configuration reference is set to NULL after destruction.
 *
 * @param[in] configuration The configuration to destroy, set to NULL
 */
extern void acc_detector_distance_peak_configuration_destroy(acc_detector_distance_peak_configuration_t *configuration);


/**
 * @brief Create a distance detector
 *
 * @param[in] configuration The distance detector configuration
 *
 * @return A reference to the distance detector handle. NULL in case of failure
 */
extern acc_detector_distance_peak_handle_t acc_detector_distance_peak_create(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Destroy a distance detector
 *
 * @param[in] handle The distance detector handle
 */
extern void acc_detector_distance_peak_destroy(acc_detector_distance_peak_handle_t *handle);


/**
 * @brief Activate a distance detector
 *
 * @param[in] handle The distance detector handle to activate
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_activate(acc_detector_distance_peak_handle_t handle);


/**
 * @brief Deactivate a distance detector
 *
 * @param[in] handle The distance detector handle
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_deactivate(acc_detector_distance_peak_handle_t handle);


/**
 * @brief Checks if the detector is activated or not
 *
 * @param[in] handle The distance detector handle to check
 * @return True if the detector is active, false otherwise
 */
extern bool acc_detector_distance_peak_is_active(acc_detector_distance_peak_handle_t handle);


/**
 * @brief Retrieve the distance detector sweep configuration
 *
 * @param[in] configuration The distance detector configuration
 *
 * @return A reference to the sweep configuration, or NULL if an error occurs
 */
extern acc_sweep_configuration_t acc_detector_distance_peak_get_sweep_configuration(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Get a profile of configuration parameters
 *
 * A profile consists of a number of settings for the sensor as well as the sweep setup to
 * allow a quick and easy setup of the distance detector.
 * Most parameters may be specifically set using their own set methods while the sensor
 * specific settings of e.g. transmitted energy and receiver gain are matched to the profile
 * used.
 *
 * @param[in] configuration The configuration to get a profile from
 * @return The current profile, ACC_DETECTOR_DISTANCE_PEAK_PROFILE_MAX if configuration is invalid
 */
extern acc_detector_distance_peak_profile_t acc_detector_distance_peak_profile_get(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Set a profile of configuration parameters
 *
 * A profile consists of a number of settings for the sensor as well as the sweep setup to
 * allow a quick and easy setup of the distance detector.
 * Most parameters may be specifically set using their own set methods while the sensor
 * specific settings of e.g. transmitted energy and receiver gain are matched to the profile
 * used.
 *
 * @param[in] configuration The configuration to set a profile for
 * @param[in] profile The profile to set
 */
extern void acc_detector_distance_peak_profile_set(acc_detector_distance_peak_configuration_t configuration,
					      acc_detector_distance_peak_profile_t profile);


/**
 * @brief Get running average factor
 *
 * The running average factor is the factor of which the most recent sweep is weighed against previous sweeps.
 * Valid range is between 0.0 and 1.0 where 0.0 means that no history is weighed in, i.e filtering is effectively disabled.
 * A factor of 1.0 means that the most recent sweep has no effect on the result,
 * which will result in that the first sweep is forever received as the result.
 * The filtering is coherent and is done on complex valued IQ data before conversion to envelope data.
 *
 * @param[in] configuration The configuration to get the running average factor for
 * @return Running average factor
 */
extern float acc_detector_distance_peak_running_average_factor_get(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Set running average factor
 *
 * The running average factor is the factor of which the most recent sweep is weighed against previous sweeps.
 * Valid range is between 0.0 and 1.0 where 0.0 means that no history is weighed in, i.e filtering is effectively disabled.
 * A factor of 1.0 means that the most recent sweep has no effect on the result,
 * which will result in that the first sweep is forever received as the result.
 * The filtering is coherent and is done on complex valued IQ data before conversion to envelope data.
 *
 * @param[in] configuration The configuration to set the running average factor for
 * @param[in] factor The running average factor to set
 */
extern void acc_detector_distance_peak_running_average_factor_set(acc_detector_distance_peak_configuration_t configuration, float factor);


/**
 * @brief Retrieve the next result from the distance detector
 *
 * May only be called after the distance detector has been activated to retrieve the next result, blocks
 * the application until a result is ready.
 *
 * @param[in] handle The distance detector handle
 * @param[out] reflections Reflection results
 * @param[in,out] reflection_count The maximum number reflections as input and the actual number of reflections as output
 * @param[out] result_info Detection results metadata
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_get_next(acc_detector_distance_peak_handle_t handle,
								     acc_detector_distance_peak_reflection_t *reflections,
								     uint_fast16_t *reflection_count,
								     acc_detector_distance_peak_result_info_t *result_info);


/**
 * @brief Get the distance detector metadata
 *
 * May only be called after a distance detector has been created.
 *
 * @param[in] handle The detector handle
 * @param[out] metadata Metadata results are provided in this parameter
 */
extern void acc_detector_distance_peak_get_metadata(acc_detector_distance_peak_handle_t handle,
					       acc_detector_distance_peak_metadata_t *metadata);


/**
 * @brief Set the threshold mode to fixed
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] fix_threshold_value Threshold value
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_threshold_mode_fixed(acc_detector_distance_peak_configuration_t configuration,
										     uint16_t fix_threshold_value);

/**
 * @brief Set the threshold value to the provided one
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] threshold_context_size The size of the threshold_context_data
 * @param[in] threshold_context_data A reference to a context from a previous threshold estimation
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_threshold_mode_provided(acc_detector_distance_peak_configuration_t configuration,
											size_t threshold_context_size,
											void *threshold_context_data);


/**
 * @brief Set the threshold mode to estimation i.e. the distance detector estimates and creates threshold to be used
 *
 * @param[in] configuration The distance detector configuration previously created
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_threshold_mode_estimation(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Threshold estimation update.
 *
 * Starts or updates an already ongoing threshold estimation.
 * It is recommended to use at least 50 updates. The threshold estimation must be called before activating the detector
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] updates_count The number of updates for the threshold estimation
 * @param[in] distance_start_m The distance of the first data point[m]
 * @param[in] distance_end_m The distance of the last data point[m]
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_threshold_estimation_update(acc_detector_distance_peak_configuration_t configuration,
											uint16_t updates_count,
											float distance_start_m,
											float distance_end_m);


/**
 * @brief Set if distance detector should operate on absolute amplitude (otherwise delta amplitude compared to threshold, which is the default behaviour)
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] set_absolute True if absolute amplitude should be used instead of difference (compared to threshold), false otherwise
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_absolute_amplitude(acc_detector_distance_peak_configuration_t configuration,
										   bool set_absolute);


/**
 * @brief Threshold estimation reset.
 *
 * Resets contents of any ongoing threshold estimation.
 *
 * @param[in] configuration The distance detector configuration previously created
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_threshold_estimation_reset(acc_detector_distance_peak_configuration_t configuration);


/**
 * @brief Get the size of threshold estimation data.
 *
 * Retrieves the size of threshold estimation data to use when retrieving the data.
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[out] threshold_data_size The threshold estimation data size is stored in this parameter
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_threshold_estimation_get_size(acc_detector_distance_peak_configuration_t configuration,
											  size_t *threshold_data_size);


/**
 * @brief Get the result of a threshold estimation.
 *
 * Retrieves the result of a threshold estimation which is possible to save to a file and use when recreating the distance detector.
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] threshold_data_size The size of memory referenced by threshold_data, must be of at least the size provided in acc_detector_distance_peak_threshold_estimation_get_size
 * @param[out] threshold_data The threshold data is stored in this parameter, must be of at least the size provided in acc_detector_distance_peak_threshold_estimation_get_size
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_threshold_estimation_get_data(acc_detector_distance_peak_configuration_t configuration,
											  size_t threshold_data_size,
											  uint8_t *threshold_data);


/**
 * @brief Set sensitivity factor for false detection rate, 0.0 for lowest sensitivity and 1.0 for highest sensitivity
 *
 * This function is optional but, if used, must be called before acc_detector_distance_peak_detect().
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] sensitivity Sensitivity factor to be set
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */
extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_sensitivity(acc_detector_distance_peak_configuration_t configuration,
									    float sensitivity);

/**
 * @brief Set sort reflection by amplitude
 *
 * This function is optional but, if used, must be called before acc_detector_distance_peak_create().
 *
 * @param[in] configuration The distance detector configuration previously created
 * @param[in] sort_by_amplitude True if reflections should be sorted by amplitude, largest amplitude first
 *
 * @return ACC_DETECTOR_DISTANCE_PEAK_STATUS_SUCCESS on success otherwise ACC_DETECTOR_DISTANCE_PEAK_STATUS_FAILURE
 */

extern acc_detector_distance_peak_status_t acc_detector_distance_peak_set_sort_by_amplitude(acc_detector_distance_peak_configuration_t configuration,
									    		bool sort_by_amplitude);

/**
 * @}
 */


#endif
