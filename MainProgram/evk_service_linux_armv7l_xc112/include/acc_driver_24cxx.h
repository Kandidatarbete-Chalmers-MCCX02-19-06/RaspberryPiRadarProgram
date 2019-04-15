// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#ifndef ACC_DRIVER_24CXX_H_
#define ACC_DRIVER_24CXX_H_

#include <stdint.h>
#include <stdlib.h>

#include "acc_device.h"

#ifdef __cplusplus
extern "C" {
#endif


/**
 * @brief Request driver to register with device(s)
 *
 * @param[in] i2c_device_handle I2C device handle
 * @param[in] i2c_device_id I2C device id of memory chip
 * @param[in] memory_size Size of memory chip in bytes
 */
extern void acc_driver_24cxx_register(acc_device_handle_t i2c_device_handle, uint8_t i2c_device_id, size_t memory_size);

#ifdef __cplusplus
}
#endif

#endif
