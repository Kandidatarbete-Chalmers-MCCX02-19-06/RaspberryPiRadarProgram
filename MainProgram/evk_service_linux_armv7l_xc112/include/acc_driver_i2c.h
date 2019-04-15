// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#ifndef ACC_DRIVER_I2C_H_
#define ACC_DRIVER_I2C_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_device.h"
#include "acc_device_i2c.h"

#ifdef __cplusplus
extern "C" {
#endif


typedef acc_device_handle_t (*acc_device_i2c_create_function_t)(acc_device_i2c_configuration_t configuration);
typedef void (*acc_device_i2c_destroy_function_t)(acc_device_handle_t *handle);
typedef bool (*acc_device_i2c_write_to_address_8_function_t)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size);
typedef bool (*acc_device_i2c_write_to_address_16_function_t)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size);
typedef bool (*acc_device_i2c_read_from_address_8_function_t)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size);
typedef bool (*acc_device_i2c_read_from_address_16_function_t)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size);
typedef bool (*acc_device_i2c_read_function_t)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size);
typedef void (*acc_device_i2c_slave_access_isr_register_function_t)(acc_device_handle_t device_handle, acc_device_i2c_slave_isr_callback_t slave_access_isr);


typedef struct
{
	acc_device_i2c_create_function_t                     create;
	acc_device_i2c_destroy_function_t                    destroy;
	acc_device_i2c_write_to_address_8_function_t         write_to_address_8;
	acc_device_i2c_write_to_address_16_function_t        write_to_address_16;
	acc_device_i2c_read_from_address_8_function_t        read_from_address_8;
	acc_device_i2c_read_from_address_16_function_t       read_from_address_16;
	acc_device_i2c_slave_access_isr_register_function_t  slave_access_isr_register;
} acc_driver_i2c_t;


extern acc_device_handle_t (*acc_device_i2c_create_func)(acc_device_i2c_configuration_t configuration);
extern void (*acc_device_i2c_destroy_func)(acc_device_handle_t *handle);
extern bool (*acc_device_i2c_write_to_address_8_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, const uint8_t *buffer, size_t buffer_size);
extern bool (*acc_device_i2c_write_to_address_16_func)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, const uint8_t *buffer, size_t buffer_size);
extern bool (*acc_device_i2c_read_from_address_8_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t address, uint8_t *buffer , size_t buffer_size);
extern bool (*acc_device_i2c_read_from_address_16_func)(acc_device_handle_t device_handle, uint8_t device_id, uint16_t address, uint8_t *buffer , size_t buffer_size);
extern bool (*acc_device_i2c_read_func)(acc_device_handle_t device_handle, uint8_t device_id, uint8_t *buffer, size_t buffer_size);
extern void (*acc_device_i2c_slave_access_isr_register_func)(acc_device_handle_t device_handle, acc_device_i2c_slave_isr_callback_t *slave_access_isr);

#ifdef __cplusplus
}
#endif

#endif
