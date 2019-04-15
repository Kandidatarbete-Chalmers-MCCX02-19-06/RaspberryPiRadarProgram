// Copyright (c) Acconeer AB, 2017-2018
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "acc_device_memory.h"

#include "acc_device_os.h"
#include "acc_log.h"
#include "acc_types.h"


#define MODULE "device_memory"	/**< Module name */

acc_status_t (*acc_device_memory_init_func)(void);
acc_status_t (*acc_device_memory_get_size_func)(size_t *memory_size);
acc_status_t (*acc_device_memory_read_func)(uint32_t address, void *buffer, size_t size);
acc_status_t (*acc_device_memory_write_func)(uint32_t address, const void *buffer, size_t size);

static acc_os_mutex_t	memory_mutex = NULL;	/**< Mutex to protect memory transfers */
static bool		init_done = false;	/**< Flag to indicate if device has been initialized */
static size_t		memory_size;		/**< Size of the currently registered memory in bytes, or 0 if unknown */


acc_status_t acc_device_memory_init(void)
{
	acc_status_t		status;
	static acc_os_mutex_t	init_mutex = NULL;

	if (init_done) {
		return ACC_STATUS_SUCCESS;
	}

	acc_os_init();
	init_mutex = acc_os_mutex_create();
	memory_mutex = acc_os_mutex_create();

	acc_os_mutex_lock(init_mutex);
	if (init_done) {
		acc_os_mutex_unlock(init_mutex);
		return ACC_STATUS_SUCCESS;
	}

	if (acc_device_memory_init_func != NULL) {
		status = acc_device_memory_init_func();
		if (status != ACC_STATUS_SUCCESS) {
			acc_os_mutex_unlock(init_mutex);
			return status;
		}
	}

	init_done = true;
	status = acc_device_memory_get_size(&memory_size);
	if (status != ACC_STATUS_SUCCESS) {
		memory_size = 0;
	}

	acc_os_mutex_unlock(init_mutex);

	return ACC_STATUS_SUCCESS;
}


acc_status_t acc_device_memory_get_size(size_t *memory_size)
{
	if (!init_done) {
		return ACC_STATUS_FAILURE;
	}

	if (memory_size == NULL) {
		return ACC_STATUS_BAD_PARAM;
	}

	if (acc_device_memory_get_size_func == NULL) {
		return ACC_STATUS_UNSUPPORTED;
	}

	return acc_device_memory_get_size_func(memory_size);
}


acc_status_t acc_device_memory_read(uint32_t address, void *buffer, size_t size)
{
	acc_status_t status;

	if (!init_done) {
		return ACC_STATUS_FAILURE;
	}

	if (size == 0) {
		return ACC_STATUS_BAD_PARAM;
	}

	if ((memory_size != 0) && (address + size > memory_size)) {
		return ACC_STATUS_BAD_PARAM;
	}

	acc_os_mutex_lock(memory_mutex);

	if (acc_device_memory_read_func != NULL) {
		status = acc_device_memory_read_func(address, buffer, size);
	}
	else {
		status = ACC_STATUS_UNSUPPORTED;
	}

	acc_os_mutex_unlock(memory_mutex);

	return status;
}


acc_status_t acc_device_memory_write(uint32_t address, const void *buffer, size_t size)
{
	acc_status_t status;

	if (!init_done) {
		return ACC_STATUS_FAILURE;
	}

	if (size == 0) {
		return ACC_STATUS_BAD_PARAM;
	}

	if ((memory_size != 0) && (address + size > memory_size)) {
		return ACC_STATUS_BAD_PARAM;
	}

	acc_os_mutex_lock(memory_mutex);

	if (acc_device_memory_write_func != NULL) {
		status = acc_device_memory_write_func(address, buffer, size);
	}
	else {
		status = ACC_STATUS_UNSUPPORTED;
	}

	acc_os_mutex_unlock(memory_mutex);

	return status;
}
