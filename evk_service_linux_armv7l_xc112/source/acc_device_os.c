// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#include "acc_device_os.h"

#include <stdbool.h>
#include <stdio.h>

static acc_os_mutex_t os_mutex;
static bool init_done;

void                   (*acc_device_os_init_func)(void);
void                   (*acc_device_os_stack_setup_func)(size_t stack_size);
size_t                 (*acc_device_os_stack_get_usage_func)(size_t stack_size);
void                   (*acc_device_os_sleep_us_func)(uint32_t time_usec);
void*                  (*acc_device_os_mem_alloc_func)(size_t);
void                   (*acc_device_os_mem_free_func)(void *);
acc_os_thread_id_t     (*acc_device_os_get_thread_id_func)(void);
void                   (*acc_device_os_get_time_func)(uint32_t *time_usec);
acc_os_mutex_t         (*acc_device_os_mutex_create_func)(void);
void                   (*acc_device_os_mutex_lock_func)(acc_os_mutex_t mutex);
void                   (*acc_device_os_mutex_unlock_func)(acc_os_mutex_t mutex);
void                   (*acc_device_os_mutex_destroy_func)(acc_os_mutex_t mutex);
acc_os_thread_handle_t (*acc_device_os_thread_create_func)(void (*func)(void *param), void *param, const char *name);
void                   (*acc_device_os_thread_exit_func)(void);
bool                   (*acc_device_os_thread_cleanup_func)(acc_os_thread_handle_t handle);
acc_os_semaphore_t     (*acc_device_os_semaphore_create_func)(void);
bool                   (*acc_device_os_semaphore_wait_func)(acc_os_semaphore_t sem, uint16_t timeout_ms);
void                   (*acc_device_os_semaphore_signal_func)(acc_os_semaphore_t sem);
void                   (*acc_device_os_semaphore_signal_from_interrupt_func)(acc_os_semaphore_t sem);
void                   (*acc_device_os_semaphore_destroy_func)(acc_os_semaphore_t sem);

static bool heap_debug = false;


void acc_os_init(void)
{
	if (init_done) {
		return;
	}

	os_mutex = acc_os_mutex_create();

	if (acc_device_os_init_func != NULL) {
		acc_device_os_init_func();
	}

	init_done = true;

	if (heap_debug) {
		acc_os_debug_init(acc_device_os_mem_alloc_func, acc_device_os_mem_free_func);
	}

}


void acc_os_stack_setup(size_t stack_size)
{
	if (init_done && acc_device_os_stack_setup_func != NULL) {
		acc_device_os_stack_setup_func(stack_size);
	}
}


size_t acc_os_stack_get_usage(size_t stack_size)
{
	size_t result = 0;

	if (init_done && acc_device_os_stack_get_usage_func != NULL) {
		result = acc_device_os_stack_get_usage_func(stack_size);
	}

	return result;
}


void acc_os_sleep_us(uint32_t time_usec)
{
	if (init_done && acc_device_os_sleep_us_func != NULL) {
		acc_device_os_sleep_us_func(time_usec);
	}
}


void *acc_os_mem_alloc_debug(size_t size, const char *file, uint16_t line)
{
	void *result = NULL;

	if (init_done && acc_device_os_mem_alloc_func != NULL) {
		result = acc_device_os_mem_alloc_func(size);

		if (heap_debug) {
			acc_os_debug_track_allocation(result, size, file, line);
		}
	}

	return result;
}


void *acc_os_mem_calloc_debug(size_t num, size_t size, const char *file, uint16_t line)
{
	if (num == 0) {
		return NULL;
	}

	size_t total_size = num * size;
	void *mem = acc_os_mem_alloc_debug(total_size, file, line);

	if (mem == NULL) {
		return NULL;
	}

	memset(mem, 0, total_size);

	return mem;
}


void acc_os_mem_free(void *ptr)
{
	if (init_done && acc_device_os_mem_free_func != NULL) {
		if (heap_debug) {
			acc_os_debug_untrack_allocation(ptr);
		}
		acc_device_os_mem_free_func(ptr);
	}
}


acc_os_thread_id_t acc_os_get_thread_id(void)
{
	acc_os_thread_id_t result = {0};

	if (init_done && acc_device_os_get_thread_id_func != NULL) {
		result = acc_device_os_get_thread_id_func();
	}

	return result;
}


void acc_os_get_time(uint32_t *time_usec)
{
	if (init_done && acc_device_os_get_time_func != NULL) {
		acc_device_os_get_time_func(time_usec);
	}
}


acc_os_mutex_t acc_os_mutex_create(void)
{
	acc_os_mutex_t result = NULL;

	if (init_done && acc_device_os_mutex_create_func != NULL) {
		result = acc_device_os_mutex_create_func();
	}

	return result;
}


void acc_os_mutex_lock(acc_os_mutex_t mutex)
{
	if (init_done && acc_device_os_mutex_lock_func != NULL) {
		acc_device_os_mutex_lock_func(mutex);
	}
}


void acc_os_mutex_unlock(acc_os_mutex_t mutex)
{
	if (init_done && acc_device_os_mutex_unlock_func != NULL) {
		acc_device_os_mutex_unlock_func(mutex);
	}
}


void acc_os_mutex_destroy(acc_os_mutex_t mutex)
{
	if (init_done && acc_device_os_mutex_destroy_func != NULL) {
		acc_device_os_mutex_destroy_func(mutex);
	}
}


acc_os_thread_handle_t acc_os_thread_create(void (*func)(void *param), void *param, const char *name)
{
	acc_os_thread_handle_t result = NULL;

	if (init_done && acc_device_os_thread_create_func != NULL) {
		result = acc_device_os_thread_create_func(func, param, name);
	}
	return result;
}


void acc_os_thread_exit(void)
{
	if (init_done && acc_device_os_thread_exit_func != NULL) {
		acc_device_os_thread_exit_func();
	}
}


void acc_os_thread_cleanup(acc_os_thread_handle_t handle)
{
	if (init_done && acc_device_os_thread_cleanup_func != NULL) {
		acc_device_os_thread_cleanup_func(handle);
	}
}


acc_os_semaphore_t acc_os_semaphore_create()
{
	acc_os_semaphore_t result = NULL;

	if (init_done && acc_device_os_semaphore_create_func != NULL) {
		result = acc_device_os_semaphore_create_func();
	}

	return result;
}


bool acc_os_semaphore_wait(acc_os_semaphore_t sem, uint16_t timeout_ms)
{
	bool result = false;

	if (init_done && acc_device_os_semaphore_wait_func != NULL) {
		result = acc_device_os_semaphore_wait_func(sem, timeout_ms);
	}

	return result;

}


void acc_os_semaphore_signal(acc_os_semaphore_t sem)
{
	if (init_done && acc_device_os_semaphore_signal_func != NULL) {
		acc_device_os_semaphore_signal_func(sem);
	}
}


void acc_os_semaphore_signal_from_interrupt(acc_os_semaphore_t sem)
{
	if (init_done && acc_device_os_semaphore_signal_from_interrupt_func != NULL) {
		acc_device_os_semaphore_signal_from_interrupt_func(sem);
	}
}


void acc_os_semaphore_destroy(acc_os_semaphore_t sem)
{
	if (init_done && acc_device_os_semaphore_destroy_func != NULL) {
		acc_device_os_semaphore_destroy_func(sem);
	}
}


uint16_t acc_os_ntohs(uint16_t value)
{
	uint8_t *char_value = (uint8_t *)&value;

	return ((uint32_t) char_value[0] << 8) |
	        (uint32_t) char_value[1];
}


uint16_t acc_os_htons(uint16_t value)
{
	uint16_t result = 0;
	uint8_t *char_value = (uint8_t *)&result;

	char_value[0] = (uint8_t)((value >> 8) & 0xff);
	char_value[1] = (uint8_t)(value & 0xff);
	return result;
}


uint32_t acc_os_ntohl(uint32_t value)
{
	uint8_t *char_value = (uint8_t *)&value;

	return ((uint32_t) char_value[0] << 24) |
	        ((uint32_t) char_value[1] << 16) |
	        ((uint32_t) char_value[2] << 8) |
	        (uint32_t) char_value[3];
}


uint32_t acc_os_htonl(uint32_t value)
{
	uint32_t result = 0;
	uint8_t *char_value = (unsigned char *)&result;

	char_value[0] = (uint8_t)((value >> 24) & 0xff);
	char_value[1] = (uint8_t)((value >> 16) & 0xff);
	char_value[2] = (uint8_t)((value >> 8) & 0xff);
	char_value[3] = (uint8_t)(value & 0xff);
	return result;
}


bool acc_os_multithread_support(void)
{
	bool result = false;

	// We assume that we are multithreaded if the client has implemented thread_create
	if (init_done && acc_device_os_thread_create_func != NULL) {
		result = true;
	}

	return result;
}
