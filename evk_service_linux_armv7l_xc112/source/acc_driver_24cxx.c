// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_driver_24cxx.h"

#include "acc_device.h"
#include "acc_device_i2c.h"
#include "acc_device_memory.h"
#include "acc_device_os.h"
#include "acc_log.h"
#include "acc_types.h"


#define MODULE "driver_24cxx" /**< module name */
#define M24128_PAGE_SIZE 64
#define MIN(a, b) ((a) < (b)) ? (a) : (b)


typedef struct
{
	acc_device_handle_t i2c_device_handle;
	uint8_t             i2c_device_id;
	size_t              memory_size;
} driver_context_t;


static driver_context_t driver_context;


/**
 * @brief Return the size of the EEPROM memory
 *
 * @param[out] memory_size Return memory size in bytes
 * @return Status
 */
static acc_status_t acc_driver_24cxx_get_size(size_t *memory_size)
{
	*memory_size = driver_context.memory_size;

	return ACC_STATUS_SUCCESS;
}


/**
 * @brief Read a memory block
 *
 * @param[in] address Start address for read
 * @param[out] buffer Buffer to write to
 * @param[in] size Number of bytes to read and store into buffer
 * @return Status
 */
static acc_status_t acc_driver_24cxx_read(uint32_t address, void *buffer, size_t size)
{
	if (!acc_device_i2c_read_from_address_16(driver_context.i2c_device_handle, driver_context.i2c_device_id, address, buffer, size))
	{
		return ACC_STATUS_FAILURE;
	}

	return ACC_STATUS_SUCCESS;
}


/**
 * @brief Write a memory block
 *
 * @param[in] address Start address for write
 * @param[in] buffer Buffer to write
 * @param[in] size Number of bytes to write to memory
 * @return Status
 */
static acc_status_t acc_driver_24cxx_write(uint32_t address, const void *buffer, size_t size)
{
	bool success = true;
	const uint8_t *data = buffer;
	while (size > 0)
	{
		size_t chunk_size = MIN(size, M24128_PAGE_SIZE - (address % M24128_PAGE_SIZE));

		if (!acc_device_i2c_write_to_address_16(driver_context.i2c_device_handle,
		                                        driver_context.i2c_device_id,
		                                        address, data, chunk_size))
		{
			ACC_LOG_ERROR("Failed to write to memory.");
			success = false;
			break;
		}

		uint8_t dummy;

		/* According to datasheet, page 30: https://www.st.com/resource/en/datasheet/m24128-df.pdf
		 * max write delay is 5ms (tw), we could also poll, but currently there is a poll timeout in
		 * the driver of 100ms which will give a slower result.
		 */
		acc_os_sleep_us(5000);

		if (!acc_device_i2c_read_from_address_16(driver_context.i2c_device_handle,
		                                         driver_context.i2c_device_id,
		                                         address, &dummy, 1))
		{
			ACC_LOG_ERROR("Write action did not complete in time.");
			success = false;
			break;
		}
		size -= chunk_size;
		address += chunk_size;
		data += chunk_size;
	}
	return success ? ACC_STATUS_SUCCESS : ACC_STATUS_FAILURE;
}


void acc_driver_24cxx_register(acc_device_handle_t i2c_device_handle, uint8_t i2c_device_id, size_t memory_size)
{
	driver_context.i2c_device_handle = i2c_device_handle;
	driver_context.i2c_device_id     = i2c_device_id;
	driver_context.memory_size       = memory_size;

	acc_device_memory_get_size_func = acc_driver_24cxx_get_size;
	acc_device_memory_read_func     = acc_driver_24cxx_read;
	acc_device_memory_write_func    = acc_driver_24cxx_write;
}
