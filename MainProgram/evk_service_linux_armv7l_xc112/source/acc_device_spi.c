// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "acc_device.h"
#include "acc_device_os.h"
#include "acc_device_spi.h"
#include "acc_log.h"

/**
 * @brief The module name
 */
#define MODULE		"device_spi"


size_t			(*acc_device_spi_get_max_transfer_size_func)(void);
acc_device_handle_t	(*acc_device_spi_create_func)(acc_device_spi_configuration_t *configuration);
void			(*acc_device_spi_destroy_func)(acc_device_handle_t *handle);
bool		(*acc_device_spi_transfer_func)(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size);
bool		(*acc_device_spi_transfer_async_func)(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size, acc_device_spi_transfer_callback_t callback);
uint8_t			(*acc_device_spi_get_bus_func)(acc_device_handle_t);


/**
 * @brief Mutex to protect SPI transfers
 */
static acc_os_mutex_t spi_mutex[ACC_DEVICE_SPI_BUS_MAX] = {NULL};


acc_device_handle_t acc_device_spi_create(acc_device_spi_configuration_t *configuration)
{
	if (acc_device_spi_create_func != NULL) {
		if (spi_mutex[0] == NULL) {
			for (uint_fast8_t index = 0; index < ACC_DEVICE_SPI_BUS_MAX; index++)
			{
				spi_mutex[index] = acc_os_mutex_create();
			}
		}

		return (acc_device_spi_create_func(configuration));
	}

	return NULL;
}


void acc_device_spi_destroy(acc_device_handle_t *handle)
{
	if (acc_device_spi_destroy_func != NULL) {
		acc_device_spi_destroy_func(handle);
	}
}


uint_fast8_t acc_device_spi_get_bus(acc_device_handle_t handle)
{
	if (acc_device_spi_get_bus_func != NULL) {
		return acc_device_spi_get_bus_func(handle);
	}

	ACC_LOG_WARNING("Default SPI bus returned");

	return 0;
}


bool acc_device_spi_lock(uint_fast8_t bus)
{
	if (bus >= ACC_DEVICE_SPI_BUS_MAX) {
		return false;
	}

	acc_os_mutex_lock(spi_mutex[bus]);

	return true;
}


bool acc_device_spi_unlock(uint_fast8_t bus)
{
	if (bus >= ACC_DEVICE_SPI_BUS_MAX) {
		return false;
	}

	acc_os_mutex_unlock(spi_mutex[bus]);

	return true;
}


size_t acc_device_spi_get_max_transfer_size(void)
{
	if (acc_device_spi_get_max_transfer_size_func) {
		return acc_device_spi_get_max_transfer_size_func();
	}

	return 0;
}


bool acc_device_spi_transfer(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size)
{
	bool status = false;
	if (acc_device_spi_transfer_func != NULL) {
		status = acc_device_spi_transfer_func(handle, buffer, buffer_size);
	}

	if (!status) {
		ACC_LOG_ERROR("%s failed", __func__);
	}

	return status;
}


bool acc_device_spi_transfer_async(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size, acc_device_spi_transfer_callback_t callback)
{
	bool status = false;
	if (acc_device_spi_transfer_async_func != NULL) {
		status = acc_device_spi_transfer_async_func(handle, buffer, buffer_size, callback);
	}

	if (!status) {
		ACC_LOG_ERROR("%s failed", __func__);
	}

	return status;
}
