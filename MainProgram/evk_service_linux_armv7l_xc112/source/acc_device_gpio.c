// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "acc_device_gpio.h"
#include "acc_device_os.h"
#include "acc_log.h"
#include "acc_types.h"

/**
 * @brief The module name
 */
#define MODULE "device_gpio"

bool (*acc_device_gpio_init_func)(void);
bool (*acc_device_gpio_set_initial_pull_func)(uint_fast8_t pin, uint_fast8_t level);
bool (*acc_device_gpio_input_func)(uint_fast8_t pin);
bool (*acc_device_gpio_read_func)(uint_fast8_t pin, uint_fast8_t *level);
bool (*acc_device_gpio_write_func)(uint_fast8_t pin, uint_fast8_t level);
bool (*acc_device_gpio_register_isr_func)(uint_fast8_t pin, acc_gpio_edge_t edge, acc_device_gpio_isr_t isr);
bool (*acc_device_gpio_suspend_func)(void);
bool (*acc_device_gpio_resume_func)(void);


bool acc_device_gpio_init(void)
{
	bool                  status;

	if (acc_device_gpio_init_func)
	{
		status = acc_device_gpio_init_func();
	}
	else
	{
		ACC_LOG_ERROR("init: no driver registered");
		status = false;
	}

	if (!status)
	{
		ACC_LOG_ERROR("%s failed", __func__);
	}

	return status;
}


bool acc_device_gpio_set_initial_pull(uint_fast8_t pin, uint_fast8_t level)
{
	if (acc_device_gpio_set_initial_pull_func)
	{
		return acc_device_gpio_set_initial_pull_func(pin, level);
	}

	return true;
}


bool acc_device_gpio_input(uint_fast8_t pin)
{
	if (acc_device_gpio_input_func)
	{
		return acc_device_gpio_input_func(pin);
	}

	return true;
}


bool acc_device_gpio_read(uint_fast8_t pin, uint_fast8_t *level)
{
	if (acc_device_gpio_read_func)
	{
		return acc_device_gpio_read_func(pin, level);
	}

	return true;
}


bool acc_device_gpio_write(uint_fast8_t pin, uint_fast8_t level)
{
	if (acc_device_gpio_write_func)
	{
		return acc_device_gpio_write_func(pin, level);
	}

	return true;
}


bool acc_device_gpio_register_isr(uint_fast8_t pin, acc_gpio_edge_t edge, acc_device_gpio_isr_t isr)
{
	if (acc_device_gpio_register_isr_func != NULL)
	{
		return acc_device_gpio_register_isr_func(pin, edge, isr);
	}

	return true;
}


bool acc_device_gpio_suspend(void)
{
	if (acc_device_gpio_suspend_func != NULL)
	{
		return acc_device_gpio_suspend_func();
	}

	return true;
}


bool acc_device_gpio_resume(void)
{
	if (acc_device_gpio_resume_func != NULL)
	{
		return acc_device_gpio_resume_func();
	}

	return true;
}
