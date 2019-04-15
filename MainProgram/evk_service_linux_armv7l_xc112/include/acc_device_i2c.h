// Copyright (c) Acconeer AB, 2016-2019
// All rights reserved

#ifndef ACC_DEVICE_I2C_H_
#define ACC_DEVICE_I2C_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_device.h"

#ifdef __cplusplus
extern "C" {
#endif


typedef struct
{
	uint32_t frequency;
} acc_device_i2c_master_configuration_t;


typedef struct
{
	void (*on_start)(acc_device_handle_t handle);               // I2C start condition received
	void (*on_stop)(acc_device_handle_t handle);                // I2C stop condition received marking end of current transfer
	void (*on_write)(acc_device_handle_t handle, uint8_t byte); // I2C write. I.e. master writing to slave
	uint8_t (*on_read)(acc_device_handle_t handle);             // I2C read. I.e. master reading from slave
} acc_device_i2c_slave_isr_callback_t;


typedef struct
{
	uint8_t                            address;
} acc_device_i2c_slave_configuration_t;


typedef struct
{
	uint8_t bus;

	bool master;

	union
	{
		acc_device_i2c_master_configuration_t master;
		acc_device_i2c_slave_configuration_t  slave;
	} mode;
} acc_device_i2c_configuration_t;


/**
 * @brief Create an I2C device
 *
 * @param[in] configuration The I2C configuration to create a device for
 * @return Handle if creation is successful, NULL otherwise
 */
extern acc_device_handle_t acc_device_i2c_create(acc_device_i2c_configuration_t configuration);


/**
 * @brief Destroy an I2C device
 */
extern void acc_device_i2c_destroy(acc_device_handle_t *handle);


/**
 * @brief I2C write
 *
 * Write to specific device ID at specific 8-bit address.
 * Transfer including START and STOP.
 *
 * @param device_handle The handle to the device
 * @param device_id The ID of the device to write to
 * @param address The 8-bit address to write to
 * @param buffer The data to be written
 * @param buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
extern bool acc_device_i2c_write_to_address_8(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C write
 *
 * Write to specific device ID at specific 16-bit address.
 * Transfer including START and STOP.
 *
 * @param device_handle The handle to the device
 * @param device_id The ID of the device to write to
 * @param address The 16-bit address to write to
 * @param buffer The data to be written
 * @param buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
extern bool acc_device_i2c_write_to_address_16(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C read from specified 8-bit address
 *
 * Read from specific device ID from specific address.
 * Transfer including START and STOP.
 *
 * @param device_handle The handle to the device
 * @param device_id The ID of the device to read from
 * @param address The 8-bit address to start reading from
 * @param buffer The result of the read is stored here
 * @param buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
extern bool acc_device_i2c_read_from_address_8(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C read from specified 16-bit address
 *
 * Read from specific device ID from specific address.
 * Transfer including START and STOP.
 *
 * @param device_handle The handle to the device
 * @param device_id The ID of the device to read from
 * @param address The 16-bit address to start reading from
 * @param buffer The result of the read is stored here
 * @param buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
extern bool acc_device_i2c_read_from_address_16(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, uint8_t *buffer, size_t buffer_size);


/**
 * @brief I2C read from last read/written address
 *
 * Read from specific device ID at last read/written address. Depending on device, the address might have
 * been automatically incremented since last read/write.
 * Transfer including START and STOP.
 *
 * @param device_handle The handle to the device
 * @param device_id The ID of the device to read from
 * @param buffer The result of the read is stored here
 * @param buffer_size The size of the buffer
 * @return True if transfer is successful, false otherwise
 */
extern bool acc_device_i2c_read(acc_device_handle_t device_handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size);


/**
 * @brief Register an interrupt service routine for slave mode access
 *
 * @param device_handle The handle to the device
 * @param slave_access_isr The struct containing the i2c interrupt routines
 */
extern void acc_device_i2c_slave_access_isr_register(acc_device_handle_t device_handle, acc_device_i2c_slave_isr_callback_t *slave_access_isr);


#ifdef __cplusplus
}
#endif

#endif
