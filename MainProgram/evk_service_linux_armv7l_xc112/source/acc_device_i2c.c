// Copyright (c) Acconeer AB, 2016-2019
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "acc_device.h"
#include "acc_device_i2c.h"

/**
 * @brief The module name
 */
#define MODULE "device_i2c"


acc_device_handle_t (*acc_device_i2c_create_func)(acc_device_i2c_configuration_t configuration);
void (*acc_device_i2c_destroy_func)(acc_device_handle_t *handle);
bool (*acc_device_i2c_write_to_address_8_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size);
bool (*acc_device_i2c_write_to_address_16_func)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size);
bool (*acc_device_i2c_read_from_address_8_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size);
bool (*acc_device_i2c_read_from_address_16_func)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size);
bool (*acc_device_i2c_read_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size);
void (*acc_device_i2c_slave_access_isr_register_func)(acc_device_handle_t device_handle, acc_device_i2c_slave_isr_callback_t *slave_access_isr);


acc_device_handle_t acc_device_i2c_create(acc_device_i2c_configuration_t configuration)
{
	if (acc_device_i2c_create_func != NULL)
	{
		return (acc_device_i2c_create_func(configuration));
	}

	return NULL;
}


void acc_device_i2c_destroy(acc_device_handle_t *handle)
{
	if (acc_device_i2c_destroy_func != NULL)
	{
		acc_device_i2c_destroy_func(handle);
	}
}


bool acc_device_i2c_write_to_address_8(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size)
{
	if (acc_device_i2c_write_to_address_8_func != NULL)
	{
		return acc_device_i2c_write_to_address_8_func(device_handle, device_id, address, buffer, buffer_size);
	}

	return false;
}


bool acc_device_i2c_write_to_address_16(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size)
{
	if (acc_device_i2c_write_to_address_16_func != NULL)
	{
		return acc_device_i2c_write_to_address_16_func(device_handle, device_id, address, buffer, buffer_size);
	}

	return false;
}


bool acc_device_i2c_read_from_address_8(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size)
{
	if (acc_device_i2c_read_from_address_8_func != NULL)
	{
		return acc_device_i2c_read_from_address_8_func(device_handle, device_id, address, buffer, buffer_size);
	}

	return false;
}


bool acc_device_i2c_read_from_address_16(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size)
{
	if (acc_device_i2c_read_from_address_16_func != NULL)
	{
		return acc_device_i2c_read_from_address_16_func(device_handle, device_id, address, buffer, buffer_size);
	}

	return false;
}


bool acc_device_i2c_read(acc_device_handle_t device_handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size)
{
	if (acc_device_i2c_read_func != NULL)
	{
		return acc_device_i2c_read_func(device_handle, device_id, buffer, buffer_size);
	}

	return false;
}


void acc_device_i2c_slave_access_isr_register(acc_device_handle_t device_handle, acc_device_i2c_slave_isr_callback_t *slave_access_isr)
{
	if (acc_device_i2c_slave_access_isr_register_func != NULL)
	{
		acc_device_i2c_slave_access_isr_register_func(device_handle, slave_access_isr);
	}
}
