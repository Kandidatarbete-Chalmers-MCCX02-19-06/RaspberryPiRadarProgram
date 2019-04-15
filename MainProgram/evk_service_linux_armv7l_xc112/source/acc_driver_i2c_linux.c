// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "acc_driver_i2c_linux.h"

#include "acc_device_i2c.h"
#include "acc_device_os.h"
#include "acc_driver_i2c.h"
#include "acc_log.h"
#include "acc_types.h"


/**
 * @brief The module name
 */
#define MODULE    "driver_i2c_linux"


/**
 * @brief The path to the I2C device file to the Kernel
 */
#define I2C_PATH  "/dev/i2c-1"


/**
 * @brief File descriptor of I2C device file to Kernel
 */
static int i2c_fd = -1;


//-----------------------------
// Private declarations
//-----------------------------

/**
 * @brief Create an I2C device
 *
 * @param[in] configuration The I2C configuration to create a device for
 * @return Handle if creation is successful, NULL otherwise
 */
static acc_device_handle_t create_device(acc_device_i2c_configuration_t configuration);


/**
 * @brief Destroy an I2C device
 */
static void destroy_device(acc_device_handle_t *handle);


/**
 * @brief I2C write
 *
 * Write to specific device ID at specific 8-bit address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to write to
 * @param[in] address The 8-bit address to write to
 * @param[in] buffer The data to be written
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool write_to_address_8(acc_device_handle_t handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C write
 *
 * Write to specific device ID at specific 16-bit address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to write to
 * @param[in] address The 16-bit address to write to
 * @param[in] buffer The data to be written
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool write_to_address_16(acc_device_handle_t handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C write
 *
 * Write to specific device ID at specific address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to write to
 * @param[in] address The address to write to
 * @param[in] address_size Number of bytes of address data
 * @param[in] buffer The data to be written
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool write_to_address(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint_fast8_t address_size, const uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C read from specified 8-bit address
 *
 * Read from specific device ID from specific 8-bit address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to read from
 * @param[in] address The 8-bit address to start reading from
 * @param[out] buffer The result of the read is stored here
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool read_from_address_8(acc_device_handle_t handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size);


/**
 * @brief I2C read from specified 16-bit address
 *
 * Read from specific device ID from specific 16-bit address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to read from
 * @param[in] address The 16-bit address to start reading from
 * @param[out] buffer The result of the read is stored here
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool read_from_address_16(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size);


/**
 * @brief I2C read from specified address
 *
 * Read from specific device ID from specific address.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to read from
 * @param[in] address The address to start reading from
 * @param[in] address_size Number of bytes of address data
 * @param[out] buffer The result of the read is stored here
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool read_from_address(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint_fast8_t address_size, uint8_t *buffer , size_t buffer_size);


/**
 * @brief I2C read from last read/written address
 *
 * Read from specific device ID at last read/written address. Depending on device, the address might have
 * been automatically incremented since last read/write.
 * Transfer including START and STOP.
 *
 * @param[in] handle The handle to the device
 * @param[in] device_id The ID of the device to read from
 * @param[out] buffer The result of the read is stored here
 * @param[in] buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
static bool read_from_last_address(acc_device_handle_t handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size);


/**
 * @brief Generic I2C read
 *
 * Does a read() on a file descriptor until success or timeout. Assumes that a device ID and optionally an address have already been set.
 *
 * @param file_descriptor The file descriptor to use when reading
 * @param buffer The result of the read is stored here
 * @param buffer_size The size of the buffer
 * @return True if the read was successful
 */
static bool generic_read(int file_descriptor, uint8_t *buffer, size_t buffer_size);


/**
 * @brief Generic I2C write
 *
 * Does a write() on a file descriptor until success or timeout. Assumes that a device ID and optionally an address have already been set.
 *
 * @param file_descriptor The file descriptor to use when reading
 * @param buffer The data to be written
 * @param buffer_size The size of the buffer
 * @return True if the write was successful
 */
static bool generic_write(int file_descriptor, uint8_t *buffer, size_t buffer_size);


//-----------------------------
// Public definitions
//-----------------------------

void acc_driver_i2c_linux_register(void)
{
	acc_device_i2c_create_func                = create_device;
	acc_device_i2c_destroy_func               = destroy_device;
	acc_device_i2c_write_to_address_8_func    = write_to_address_8;
	acc_device_i2c_write_to_address_16_func   = write_to_address_16;
	acc_device_i2c_read_from_address_8_func   = read_from_address_8;
	acc_device_i2c_read_from_address_16_func  = read_from_address_16;
	acc_device_i2c_read_func                  = read_from_last_address;
}


//-----------------------------
// Private definitions
//-----------------------------

acc_device_handle_t create_device(acc_device_i2c_configuration_t configuration)
{
	(void)configuration;

	if ((i2c_fd = open(I2C_PATH, O_RDWR)) < 0)
	{
		ACC_LOG_FATAL("Unable to open i2c connection: %s", strerror(errno));
		return NULL;
	}

	return (acc_device_handle_t)&i2c_fd;
}


void destroy_device(acc_device_handle_t *handle)
{
	if ((handle != NULL) && (*handle != NULL))
	{
		if (*handle == &i2c_fd)
		{
			close(i2c_fd);
		}

		*handle = NULL;
	}
}


bool write_to_address_8(acc_device_handle_t handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size)
{
	return write_to_address(handle, device_id, address, 1, buffer, buffer_size);
}


bool write_to_address_16(acc_device_handle_t handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size)
{
	return write_to_address(handle, device_id, address, 2, buffer, buffer_size);
}


bool write_to_address(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint_fast8_t address_size, const uint8_t *buffer, size_t buffer_size)
{
	int *file_descriptor_reference = handle;
	int file_descriptor = *file_descriptor_reference;

	size_t write_data_size = address_size + buffer_size;
	uint8_t write_data[write_data_size];

	if (address_size == 1)
	{
		write_data[0] = address;
	}
	else if (address_size == 2)
	{
		write_data[0] = (address >> 8) & 0xff;
		write_data[1] = address & 0xff;
	}

	memcpy(&write_data[address_size], buffer, buffer_size);

	if (ioctl(file_descriptor, 0x0703, device_id) < 0)
	{
		ACC_LOG_ERROR("Could not set i2c slave device ID %u", device_id);
		return false;
	}

	return generic_write(file_descriptor, write_data, write_data_size);
}


bool read_from_address_8(acc_device_handle_t handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size)
{
	return read_from_address(handle, device_id, address, 1, buffer, buffer_size);
}


bool read_from_address_16(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size)
{
	return read_from_address(handle, device_id, address, 2, buffer, buffer_size);
}


bool read_from_address(acc_device_handle_t handle, uint8_t device_id, uint16_t address, uint_fast8_t address_size, uint8_t *buffer , size_t buffer_size)
{
	int *file_descriptor_reference = handle;
	int file_descriptor = *file_descriptor_reference;

	uint8_t write_data[address_size];

	if (address_size == 1)
	{
		write_data[0] = address;
	}
	else if (address_size == 2)
	{
		write_data[0] = (address >> 8) & 0xff;
		write_data[1] = address & 0xff;
	}

	if (ioctl(file_descriptor, 0x0703, device_id) < 0)
	{
		ACC_LOG_ERROR("Could not set i2c slave device ID %" PRIu8, device_id);
		return false;
	}

	if (!generic_write(file_descriptor, write_data, address_size))
	{
		return false;
	}

	return generic_read(file_descriptor, buffer, buffer_size);
}


bool read_from_last_address(acc_device_handle_t handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size)
{
	int *file_descriptor_reference = handle;
	int file_descriptor = *file_descriptor_reference;

	if (ioctl(file_descriptor, 0x0703, device_id) < 0)
	{
		ACC_LOG_ERROR("Could not set i2c device ID %u: (%u) %s", device_id, errno, strerror(errno));
		return false;
	}

	return generic_read(file_descriptor, buffer, buffer_size);
}


bool generic_read(int file_descriptor, uint8_t *buffer, size_t buffer_size)
{
	ssize_t bytes_read;
	uint_fast8_t retry = 200;

	do
	{
		bytes_read = read(file_descriptor, buffer, buffer_size);
		acc_os_sleep_us(5);
	} while (bytes_read < 0 && retry--);

	if (bytes_read < 0)
	{
		ACC_LOG_ERROR("Could not read from i2c device: (%d) %s", errno, strerror(errno));
		return false;
	}

	if ((size_t)bytes_read != buffer_size)
	{
		ACC_LOG_ERROR("Number of bytes read was %lu, but should be %lu", (unsigned long)bytes_read, (unsigned long)buffer_size);
		return false;
	}

	return true;
}


bool generic_write(int file_descriptor, uint8_t *buffer, size_t buffer_size)
{
	ssize_t bytes_written;
	uint_fast8_t retry = 200;

	do
	{
		bytes_written = write(file_descriptor, buffer, buffer_size);
		acc_os_sleep_us(5);
	} while (bytes_written < 0 && retry--);

	if (bytes_written < 0)
	{
		ACC_LOG_ERROR("Could not write to i2c device: (%d) %s", errno, strerror(errno));
		return false;
	}

	if ((size_t)bytes_written != buffer_size)
	{
		ACC_LOG_ERROR("Number of bytes written was %lu, but should be %lu", (unsigned long)bytes_written, (unsigned long)buffer_size);
		return false;
	}

	return true;
}
