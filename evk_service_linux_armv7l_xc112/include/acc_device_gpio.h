// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#ifndef ACC_DEVICE_GPIO_H_
#define ACC_DEVICE_GPIO_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_types.h"

#ifdef __cplusplus
extern "C" {
#endif


typedef void (*acc_device_gpio_isr_t)(void);

typedef enum
{
	ACC_DEVICE_GPIO_EDGE_NONE,
	ACC_DEVICE_GPIO_EDGE_FALLING,
	ACC_DEVICE_GPIO_EDGE_RISING,
	ACC_DEVICE_GPIO_EDGE_BOTH
} acc_gpio_edge_t;


// These functions are to be used by drivers only, do not use them directly
extern bool (*acc_device_gpio_init_func)(void);
extern bool (*acc_device_gpio_set_initial_pull_func)(uint_fast8_t pin, uint_fast8_t level);
extern bool (*acc_device_gpio_input_func)(uint_fast8_t pin);
extern bool (*acc_device_gpio_read_func)(uint_fast8_t pin, uint_fast8_t *level);
extern bool (*acc_device_gpio_write_func)(uint_fast8_t pin, uint_fast8_t level);
extern bool (*acc_device_gpio_register_isr_func)(uint_fast8_t pin, acc_gpio_edge_t edge, acc_device_gpio_isr_t isr);
extern bool (*acc_device_gpio_suspend_func)(void);
extern bool (*acc_device_gpio_resume_func)(void);


/**
 * @brief Initialize GPIO device
 *
 * @return Status
 */
extern bool acc_device_gpio_init(void);


/**
 * @brief Inform the driver of the pull up/down level for a GPIO pin after reset
 *
 * This does not change the pull level, but only informs the driver what pull level
 * the pin is configured to have.
 *
 * The GPIO pin numbering is decided by the GPIO driver.
 *
 * @param pin Pin number
 * @param level The pull level 0 or 1
 * @return Status
 */
extern bool acc_device_gpio_set_initial_pull(uint_fast8_t pin, uint_fast8_t level);


/**
 * @brief Set GPIO to input
 *
 * This function sets the direction of a GPIO to input.
 * The GPIO pin numbering is decided by the GPIO driver
 *
 * @param pin Pin to be set to input
 * @return Status
 */
extern bool acc_device_gpio_input(uint_fast8_t pin);


/**
 * @brief Read from GPIO
 *
 * The GPIO pin numbering is decided by the GPIO driver
 *
 * @param pin Pin to be read
 * @param level The pin level is returned here
 * @return Status
 */
extern bool acc_device_gpio_read(uint_fast8_t pin, uint_fast8_t *level);


/**
 * @brief Set GPIO output level
 *
 * This function sets a GPIO to output and the level to low or high.
 * The GPIO pin numbering is decided by the GPIO driver
 *
 * @param pin Pin to be written
 * @param level 0 to 1 to set pin low or high
 * @return Status
 */
extern bool acc_device_gpio_write(uint_fast8_t pin, uint_fast8_t level);


/**
 * @brief Register an interrupt service routine for a GPIO pin
 *
 * Registers an interrupt service routine which will be called when the specified edge is detected on the selected GPIO pin.
 * If true is returned the interrupt service routine will immediately be triggered if the specified edge is detected.
 * If a new interrupt service routine is registered it will replace the old one.
 *
 * The interrupt service routine can be unregistered by register NULL.
 * Unregister an already unregistered interrupt service routine has no effect.
 *
 * @param pin GPIO pin the interrupt service routine will be attached to.
 * @param edge The edge that will trigger the interrupt service routine. Can be set to "falling", "rising" or both.
 * @param isr The function to be called when the specified edge is detected.
 * @return true if the interrupt service routine was registered, false if the specified pin does not
 *      support interrupts or if the registration failed.
 */
extern bool acc_device_gpio_register_isr(uint_fast8_t pin, acc_gpio_edge_t edge, acc_device_gpio_isr_t isr);


/**
 * @brief Suspend the GPIO device
 *
 * @return true if successful
 */
extern bool acc_device_gpio_suspend(void);


/**
 * @brief Resume the GPIO device
 *
 * @return true if successful
 */
extern bool acc_device_gpio_resume(void);


#ifdef __cplusplus
}
#endif

#endif
