// Copyright (c) Acconeer AB, 2015-2018
// All rights reserved

#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "acc_driver_spi_linux_spidev.h"
#include "acc_device_spi.h"
#include "acc_log.h"
#include "acc_types.h"

/**
 * @brief The module name
 */
#define MODULE				"driver_spi_linux_spidev"


//SPI specific macros
#define ACC_SPI_TRANSFER_SIZE(A)	((((A)*(sizeof(spidev_transfer_t))) < (1 << _IOC_SIZEBITS)) ? \
					((A)*(sizeof(spidev_transfer_t))) : 0)

#define SPIDEV_PATH 			"/dev/spidev%u.%u"

#define SPI_BUS_MAX			2
#define SPI_BUS_DEVICE_MAX		2
#define MAX_SPI_COUNT			ACC_DEVICE_SPI_BUS_MAX


/**
 * @brief SPI transfer information
 */
typedef struct {
	uint64_t	tx;
	uint64_t	rx;
	uint32_t	length;
	uint32_t	speed;
	uint32_t	pad;
	uint16_t	delay;
	uint8_t		bits_per_word;
	uint8_t		cs_deselect;
} spidev_transfer_t;


typedef struct {
	uint_fast8_t	bus;
	uint_fast8_t	device;
	uint32_t	speed;
} acc_driver_spi_linux_spidev_handle_t;


static acc_driver_spi_linux_spidev_handle_t handles[MAX_SPI_COUNT];

static uint_fast8_t spi_count = 0;

/**
 * File descriptors for all open SPI device files
 */
static int spidev_fd[SPI_BUS_MAX][SPI_BUS_DEVICE_MAX];


/**
 * @brief Internal SPI open
 *
 * Open fd to /dev/spidevN.N.
 *
 * @param bus SPI bus
 * @param device SPI device on bus
 * @return Status
 */
static acc_status_t internal_spi_open(uint_fast8_t bus, uint_fast8_t device)
{
	uint32_t	mode = 0;
	char		spidev[sizeof(SPIDEV_PATH) + 1];

	snprintf(spidev, sizeof(spidev), SPIDEV_PATH, bus, device);

	if ((spidev_fd[bus][device] = open(spidev, O_RDWR)) < 0) {
		ACC_LOG_FATAL("Unable to open SPI (%u, %u): %s", bus, device, strerror(errno));
		return ACC_STATUS_FAILURE;
	}

	if (ioctl(spidev_fd[bus][device], _IOR('k', 1, uint8_t), &mode) < 0) {
		ACC_LOG_WARNING("Could not set SPI (read) mode %u", mode);
	}
	if (ioctl(spidev_fd[bus][device], _IOW('k', 1, uint8_t), &mode) < 0) {
		ACC_LOG_WARNING("Could not set SPI (write) mode %u", mode);
	}

	return ACC_STATUS_SUCCESS;
}


/**
 * @brief Create SPI driver and initialize the driver.
 *
 * @param[in] configuration The configuration to be used for the driver
 */
static acc_device_handle_t acc_driver_spi_linux_spidev_create(acc_device_spi_configuration_t *configuration)
{
	if (spi_count >= MAX_SPI_COUNT) {
		ACC_LOG_ERROR("Max number of spi drivers initiated");
		return NULL;
	}

	if (!configuration->master) {
		ACC_LOG_ERROR("Slave mode not supported");
		return NULL;
	}

	spidev_fd[configuration->bus][configuration->device] = -1;

	handles[spi_count].bus 		= configuration->bus;
	handles[spi_count].device	= configuration->device;
	handles[spi_count].speed	= configuration->speed;

	return (acc_device_handle_t) &handles[spi_count++];
}


/**
 * @brief Destroy SPI driver
 *
 * @param[in] handle The handle of the driver
 */
static void acc_driver_spi_linux_spidev_destroy(acc_device_handle_t *handle)
{
	*handle = NULL;
}


/**
 * @brief Return maximum allowed size of one SPI transfer
 *
 * @return Maximum allowed transfer size in bytes, or zero if unknown
 */
static size_t acc_driver_spi_linux_spidev_get_max_transfer_size(void)
{
	return 4095;
}


/**
 * @brief Data transfer (SPI)
 *
 * @param dev_handle The handle of the SPI driver
 * @param buffer The data to be transferred
 * @param buffer_size The size of the buffer in bytes
 * @return True if successful, false otherwise
 */
static bool acc_driver_spi_linux_spidev_transfer(
		acc_device_handle_t dev_handle,
		uint8_t		*buffer,
		size_t		buffer_size)
{
	acc_driver_spi_linux_spidev_handle_t *handle = dev_handle;

	if ((handle->bus >= SPI_BUS_MAX) || (handle->device >= SPI_BUS_DEVICE_MAX)) {
		return false;
	}

	if (spidev_fd[handle->bus][handle->device] < 0) {
		internal_spi_open(handle->bus, handle->device);
	}
	if (spidev_fd[handle->bus][handle->device] < 0) {
		return false;
	}

	spidev_transfer_t spi_transfer = {
		.tx		= (uintptr_t)buffer,
		.rx		= (uintptr_t)buffer,
		.length		= buffer_size,
		.speed		= handle->speed,
		.delay		= 0,
		.bits_per_word	= 8,
		.cs_deselect	= 0,
		.pad		= 0,
	};

	int ret_val = ioctl(spidev_fd[handle->bus][handle->device], _IOW('k', 0, char[ACC_SPI_TRANSFER_SIZE(1)]), &spi_transfer);
	if (ret_val < 0) {
		ACC_LOG_ERROR("SPI transfer failure: %s", strerror(errno));
		return false;
	}

	return true;
}


/**
 * @brief Return bus of the handle
 *
 * @param dev_handle SPI device handle
 * @return Number of the SPI bus
 */
static uint8_t acc_driver_spi_linux_spidev_get_bus(acc_device_handle_t dev_handle)
{
	acc_driver_spi_linux_spidev_handle_t *handle = dev_handle;

	return handle->bus;
}


/**
 * @brief Request driver to register with appropriate device(s)
 */
void acc_driver_spi_linux_spidev_register(void)
{
	acc_device_spi_create_func			= acc_driver_spi_linux_spidev_create;
	acc_device_spi_destroy_func			= acc_driver_spi_linux_spidev_destroy;
	acc_device_spi_get_max_transfer_size_func	= acc_driver_spi_linux_spidev_get_max_transfer_size;
	acc_device_spi_transfer_func			= acc_driver_spi_linux_spidev_transfer;
	acc_device_spi_get_bus_func			= acc_driver_spi_linux_spidev_get_bus;
}
