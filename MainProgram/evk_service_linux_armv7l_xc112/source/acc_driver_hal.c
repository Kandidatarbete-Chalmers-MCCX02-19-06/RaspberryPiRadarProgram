// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#include <stdbool.h>
#include <stdint.h>

#include "acc_driver_hal.h"

#include "acc_board.h"
#include "acc_definitions.h"
#include "acc_device_spi.h"
#include "acc_driver_os.h"
#include "acc_log.h"
#include "acc_types.h"


#define MODULE "driver_hal"

//-----------------------------
// Private declarations
//-----------------------------

static acc_integration_register_isr_status_t sensor_register_isr(acc_hal_sensor_isr_t isr);

//-----------------------------
// Public definitions
//-----------------------------

bool acc_driver_hal_init(void)
{
	if (!acc_board_init())
	{
		return false;
	}

	if (!acc_board_gpio_init())
	{
		return false;
	}

	return true;
}


acc_hal_t acc_driver_hal_get_implementation(void)
{
	acc_hal_t hal;

	hal.properties.sensor_count = acc_board_get_sensor_count();
	hal.properties.max_spi_transfer_size = acc_device_spi_get_max_transfer_size();

	hal.sensor_device.power_on = acc_board_start_sensor;
	hal.sensor_device.power_off = acc_board_stop_sensor;
	hal.sensor_device.is_interrupt_connected = acc_board_is_sensor_interrupt_connected;
	hal.sensor_device.is_interrupt_active = acc_board_is_sensor_interrupt_active;
	hal.sensor_device.register_isr = sensor_register_isr;
	hal.sensor_device.transfer = acc_board_sensor_transfer;
	hal.sensor_device.get_reference_frequency = acc_board_get_ref_freq;

	hal.os.sleep_us = acc_device_os_sleep_us_func;
	hal.os.mem_alloc = acc_device_os_mem_alloc_func;
	hal.os.mem_free = acc_device_os_mem_free_func;
	hal.os.get_thread_id = acc_device_os_get_thread_id_func;
	hal.os.gettime = acc_device_os_get_time_func;
	hal.os.mutex_create = acc_device_os_mutex_create_func;
	hal.os.mutex_destroy = acc_device_os_mutex_destroy_func;
	hal.os.mutex_lock = acc_device_os_mutex_lock_func;
	hal.os.mutex_unlock = acc_device_os_mutex_unlock_func;
	hal.os.thread_create = acc_device_os_thread_create_func;
	hal.os.thread_exit = acc_device_os_thread_exit_func;
	hal.os.thread_cleanup = acc_device_os_thread_cleanup_func;
	hal.os.semaphore_create = acc_device_os_semaphore_create_func;
	hal.os.semaphore_destroy = acc_device_os_semaphore_destroy_func;
	hal.os.semaphore_wait = acc_device_os_semaphore_wait_func;
	hal.os.semaphore_signal = acc_device_os_semaphore_signal_func;
	hal.os.semaphore_signal_from_interrupt = acc_device_os_semaphore_signal_from_interrupt_func;


	return hal;
}


//-----------------------------
// Private definitions
//-----------------------------

acc_integration_register_isr_status_t sensor_register_isr(acc_hal_sensor_isr_t isr)
{
	acc_status_t status = acc_board_register_isr(isr);

	if (status == ACC_STATUS_SUCCESS)
	{
		return ACC_INTEGRATION_REGISTER_ISR_STATUS_OK;
	}
	else if (status == ACC_STATUS_UNSUPPORTED)
	{
		return ACC_INTEGRATION_REGISTER_ISR_STATUS_UNSUPPORTED;
	}
	else
	{
		return ACC_INTEGRATION_REGISTER_ISR_STATUS_FAILURE;
	}
}
