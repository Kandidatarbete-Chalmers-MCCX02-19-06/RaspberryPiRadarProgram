// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#ifndef ACC_DEFINITIONS_H_
#define ACC_DEFINITIONS_H_

#include <inttypes.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>


typedef uint32_t acc_sensor_id_t;

/**
 * @brief Macro for printing sensor id
 */
#define PRIsensor_id PRIu32


/**
 * @defgroup OS OS Integration
 * @ingroup Integration
 *
 * @brief Integration OS primitives
 *
 * @{
 */

typedef uint32_t acc_os_thread_id_t;

struct acc_os_mutex;

typedef struct acc_os_mutex *acc_os_mutex_t;

struct acc_os_semaphore;

typedef struct acc_os_semaphore *acc_os_semaphore_t;

struct acc_os_thread_handle;

typedef struct acc_os_thread_handle *acc_os_thread_handle_t;


/**
 * @brief Definition of a sleep microseconds function
 *
 * Must be implemented by integration, shall sleep at least the time requested.
 */
typedef void (*acc_os_sleep_us_function_t)(uint32_t time_usec);


/**
 * @brief Definition of a memory allocation function
 *
 * Must be implemented by integration. Returning NULL is seen as failure.
 */
typedef void *(*acc_os_mem_alloc_function_t)(size_t);


/**
 * @brief Definition of a memory free function
 *
 * Must be implemented by integration.
 */
typedef void (*acc_os_mem_free_function_t)(void *);


/**
 * @brief Definition of a function to retrieve the current thread id
 *
 * Optional.
 */
typedef acc_os_thread_id_t (*acc_os_get_thread_id_function_t)(void);


/**
 * @brief Definition of a time retrival function
 *
 * Must be implemented by integration, to be replaced by a simple timestamp function.
 */
typedef void (*acc_os_get_time_function_t)(uint32_t *time_usec);


/**
 * @brief Definition of a mutex creation function
 *
 * Must be implemented when threading is enabled. Returning NULL is seen as failure.
 */
typedef acc_os_mutex_t (*acc_os_mutex_create_function_t)(void);


/**
 * @brief Definition of a mutex lock function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_mutex_lock_function_t)(acc_os_mutex_t mutex);


/**
 * @brief Definition of a mutex unlock function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_mutex_unlock_function_t)(acc_os_mutex_t mutex);


/**
 * @brief Definition of a mutex destroy function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_mutex_destroy_function_t)(acc_os_mutex_t mutex);


/**
 * @brief Definition of a thread creation function
 *
 * Must be implemented when threading is enabled.
 * If it is not implemented, no threading, mutex, or semaphore function is needed and will not be used.
 * Returning NULL is seen as failure.
 */
typedef acc_os_thread_handle_t (*acc_os_thread_create_function_t)(void (*func)(void *param), void *param, const char *name);


/**
 * @brief Definition of a thread exit function
 *
 * Optionally implemented when threading is enabled, invoked as the last function
 * before a thread exits.
 */
typedef void (*acc_os_thread_exit_function_t)(void);


/**
 * @brief Definition of a thread cleanup function
 *
 * Optionally implemented when threading is enabled, invoked as a synchronization function
 * by the thread that has created another thread.
 */
typedef void (*acc_os_thread_cleanup_function_t)(acc_os_thread_handle_t handle);


/**
 * @brief Definition of a semaphore create function
 *
 * Must be implemented when threading is enabled. Returning NULL is seen as failure.
 */
typedef acc_os_semaphore_t (*acc_os_semaphore_create_function_t)(void);


/**
 * @brief Definition of a semaphore wait function
 *
 * Must be implemented when threading is enabled.
 * Return true when the semaphore is signalled.
 * Returning false is assumed to be a timeout.
 */
typedef bool (*acc_os_semaphore_wait_function_t)(acc_os_semaphore_t sem, uint16_t timeout_ms);


/**
 * @brief Definition of a semaphore signal function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_semaphore_signal_function_t)(acc_os_semaphore_t sem);


/**
 * @brief Definition of a semaphore signal from interrupt function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_semaphore_signal_from_interrupt_function_t)(acc_os_semaphore_t sem);


/**
 * @brief Definition of a semaphore destroy function
 *
 * Must be implemented when threading is enabled.
 */
typedef void (*acc_os_semaphore_destroy_function_t)(acc_os_semaphore_t sem);


/**
 * @brief Struct that contains the implementation of os integration primitives
 *
 * RSS will operate in single threaded mode if the function pointer *thread_create* is set to NULL. All
 * other functions for thead handling and syncronization can then also be set to NULL.
 */
typedef struct
{
	acc_os_sleep_us_function_t                        sleep_us;
	acc_os_mem_alloc_function_t                       mem_alloc;
	acc_os_mem_free_function_t                        mem_free;
	acc_os_get_thread_id_function_t                   get_thread_id;
	acc_os_get_time_function_t                        gettime;
	acc_os_mutex_create_function_t                    mutex_create;
	acc_os_mutex_destroy_function_t                   mutex_destroy;
	acc_os_mutex_lock_function_t                      mutex_lock;
	acc_os_mutex_unlock_function_t                    mutex_unlock;
	acc_os_thread_create_function_t                   thread_create;
	acc_os_thread_exit_function_t                     thread_exit;
	acc_os_thread_cleanup_function_t                  thread_cleanup;
	acc_os_semaphore_create_function_t                semaphore_create;
	acc_os_semaphore_destroy_function_t               semaphore_destroy;
	acc_os_semaphore_wait_function_t                  semaphore_wait;
	acc_os_semaphore_signal_function_t                semaphore_signal;
	acc_os_semaphore_signal_from_interrupt_function_t semaphore_signal_from_interrupt;
} acc_integration_os_primitives_t;

/**
 * @}
 */

/**
 * @defgroup HAL Hardware Integration
 * @ingroup Integration
 *
 * @brief Integration of Hardware Abstraction Layer for the radar sensor
 *
 * @{
 */


/**
 * @brief Definition of a sensor power function
 */
typedef void (*acc_hal_sensor_power_function_t)(acc_sensor_id_t sensor_id);


/**
 * @brief Definition of a sensor pin function
 */
typedef bool (*acc_hal_sensor_pin_function_t)(acc_sensor_id_t sensor_id);


/**
 * @brief Definition of a hal get frequency function
 */
typedef float (*acc_hal_get_frequency_function_t)(void);


/**
 * @brief Definition of a sensor interrupt service routine (ISR)
 */
typedef void (*acc_hal_sensor_isr_t)(acc_sensor_id_t sensor_id);

typedef enum
{
	ACC_INTEGRATION_REGISTER_ISR_STATUS_OK,
	ACC_INTEGRATION_REGISTER_ISR_STATUS_UNSUPPORTED,
	ACC_INTEGRATION_REGISTER_ISR_STATUS_FAILURE
} acc_integration_register_isr_status_t;


/**
 * @brief Definition of a sensor isr register function
 */
typedef acc_integration_register_isr_status_t (*acc_hal_sensor_register_isr_function_t)(acc_hal_sensor_isr_t isr);


/**
 * @brief Definition of a sensor transfer function
 */
typedef void (*acc_hal_sensor_transfer_function_t)(acc_sensor_id_t sensor_id, uint8_t *buffer, size_t buffer_size);


/**
 * @brief This struct contains function pointers that point to
 *        functions needed for communication with the radar sensor.
 */
typedef struct
{
	acc_hal_sensor_power_function_t        power_on;
	acc_hal_sensor_power_function_t        power_off;
	acc_hal_sensor_pin_function_t          is_interrupt_connected;
	acc_hal_sensor_pin_function_t          is_interrupt_active;
	acc_hal_sensor_register_isr_function_t register_isr;
	acc_hal_sensor_transfer_function_t     transfer;
	acc_hal_get_frequency_function_t       get_reference_frequency;
} acc_integration_sensor_device_t;

/**
 * @}
 */

/**
 * @defgroup Properties Integration Properties
 * @ingroup Integration
 *
 * @brief Driver and board specific properties
 *
 * @{
 */

/**
 * @brief This struct contains information about board properties that
 *        are needed by RSS.
 */

typedef struct
{
	uint32_t sensor_count;
	size_t   max_spi_transfer_size;
} acc_integration_properties_t;

/**
 * @}
 */


/**
 * @defgroup Integration Integration
 * @brief Driver and OS Integration
 *
 * @{
 */


/**
 * @brief This struct contains the information about the sensor
 *        integration that RSS needs.
 */

typedef struct
{
	acc_integration_properties_t    properties;
	acc_integration_os_primitives_t os;
	acc_integration_sensor_device_t sensor_device;
} acc_hal_t;

/**
 * @}
 */

typedef struct
{
	uint8_t data[64];
} acc_calibration_context_t;


#endif
