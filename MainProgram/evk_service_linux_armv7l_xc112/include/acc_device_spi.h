// Copyright (c) Acconeer AB, 2016-2018
// All rights reserved

#ifndef ACC_DEVICE_SPI_H_
#define ACC_DEVICE_SPI_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_device.h"

#ifdef __cplusplus
extern "C" {
#endif


#define ACC_DEVICE_SPI_BUS_MAX	2


typedef struct {
	uint8_t	bus;
	uint8_t	device;
	uint32_t	speed;
	bool		master;
	void		*configuration;
} acc_device_spi_configuration_t;


typedef enum {
	ACC_DEVICE_SPI_TRANSFER_STATUS_OK = 0,
	ACC_DEVICE_SPI_TRANSFER_STATUS_ABORTED,
} acc_device_spi_transfer_status_enum_t;
typedef uint32_t acc_device_spi_transfer_status_t;


/**
 * @brief Function that will be called when acc_device_spi_transfer_async is done
 *
 * @param handle SPI device handle
 * @param status SPI the status of the transfer
 */
typedef void (*acc_device_spi_transfer_callback_t)(acc_device_handle_t handle, acc_device_spi_transfer_status_t status);


// These functions are to be used by drivers only, do not use them directly
extern size_t			(*acc_device_spi_get_max_transfer_size_func)(void);
extern acc_device_handle_t	(*acc_device_spi_create_func)(acc_device_spi_configuration_t *configuration);
extern void			(*acc_device_spi_destroy_func)(acc_device_handle_t *handle);
extern bool		(*acc_device_spi_transfer_func)(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size);
extern bool		(*acc_device_spi_transfer_async_func)(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size, acc_device_spi_transfer_callback_t callback);
extern uint8_t			(*acc_device_spi_get_bus_func)(acc_device_handle_t);


/**
 * @brief Create SPI device handle
 *
 * @param[in] configuration Configuration for the SPI device
 * @return Status
 */
extern acc_device_handle_t acc_device_spi_create(acc_device_spi_configuration_t *configuration);


/**
 * @brief Destroy SPI device handle
 *
 * @param[in] handle The handle to be destroyed
 */
extern void acc_device_spi_destroy(acc_device_handle_t *handle);


/**
 * @brief Extract the bus number of the device
 *
 * @param handle SPI device handle
 */
extern uint_fast8_t acc_device_spi_get_bus(acc_device_handle_t handle);


/**
 * @brief Reserve SPI bus
 *
 * @param bus The SPI bus to reserve
 * @return True if successful, false otherwise
 */
extern bool acc_device_spi_lock(uint_fast8_t bus);


/**
 * @brief Release SPI bus
 *
 * @param bus The SPI bus to release
 * @return True if successful, false otherwise
 */
extern bool acc_device_spi_unlock(uint_fast8_t bus);


/**
 * @brief Return maximum allowed size of one SPI transfer
 *
 * @return Maximum allowed transfer size in bytes, or zero if unknown
 */
extern size_t acc_device_spi_get_max_transfer_size(void);


/**
 * @brief Data transfer (SPI)
 *
 * @param handle SPI device handle
 * @param buffer The data to be transferred
 * @param buffer_size The size of the buffer in bytes
 * @return Status
 */
extern bool acc_device_spi_transfer(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size);


/**
 * @brief Data transfer (SPI)
 *
 * @param handle SPI device handle
 * @param buffer The data to be transferred. The buffer must be valid until the transfer is completed.
 *               It is the callers responsibility to free the buffer once the transfer is finished
 * @param buffer_size The size of the buffer in bytes
 * @param[in] callback Callback function to be called when transfer is complete
 * @return Status
 */
extern bool acc_device_spi_transfer_async(acc_device_handle_t handle, uint8_t *buffer, size_t buffer_size, acc_device_spi_transfer_callback_t callback);

#ifdef __cplusplus
}
#endif

#endif
