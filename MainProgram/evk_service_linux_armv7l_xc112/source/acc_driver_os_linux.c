// Copyright (c) Acconeer AB, 2016-2019
// All rights reserved

// needed for nanosleep
// needed for sigaction
// needed for siginfo_t
#define _POSIX_C_SOURCE 199309L

//needed for syscall
#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <pthread.h>
#include <semaphore.h>
#include <stddef.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/types.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>

#include "acc_device_os.h"
#include "acc_driver_os.h"
#include "acc_driver_os_linux.h"
#include "acc_log.h"


#define MODULE	"os"

typedef struct acc_os_mutex {
	uint_fast8_t		is_initialized;
	pthread_mutex_t		mutex;
} acc_os_mutex_s;


typedef struct acc_os_semaphore {
	uint_fast8_t	  	is_initialized;
	sem_t			handle;
} acc_os_semaphore_s;


typedef struct acc_os_thread_handle {
	pthread_t handle;
}acc_os_thread_handle_s;


/**
 * @brief Flag set if stack has been prepared for usage measurement
 */
static uint_fast8_t acc_os_stack_setup_done = 0;


/**
 * @brief General signal handler registered by os_init()
 */
static void internal_signal_handler(int signum)
{
	if (signum == SIGINT)
		exit(0);
}


/**
 * @brief Perform any os specific initialization
 */
static void acc_driver_os_init(void)
{
	static bool init_done;

	if (init_done) {
		return;
	}

	struct sigaction signal_action =
		{
		.sa_handler	= internal_signal_handler,
		.sa_flags	= 0
		};
	sigemptyset(&signal_action.sa_mask);
	if (sigaction(SIGINT, &signal_action, NULL) < 0) {
		fprintf(stderr, "Failed to setup signal handler for SIGINT, %s\n", strerror(errno));
	}

	init_done = true;
}


/**
 * @brief Prepare stack for measuring stack usage - to be called as early as possible
 *
 * @param stack_size Amount of stack in bytes that is allocated
 */
static void acc_driver_os_stack_setup(size_t stack_size)
{
	if (!stack_size)
		return;

	uint8_t stack_filler[stack_size];
	memset(stack_filler, 0x5a, sizeof(stack_filler));

	/* Prevent compiler from optimizing away stack_filler[] */
	__asm__ __volatile__("" :: "m" (stack_filler));

	acc_os_stack_setup_done = 1;
}


/**
 * @brief Measure amount of used stack in bytes
 *
 * @param stack_size Amount of stack in bytes that is allocated
 * @return Number of bytes of used stack space
 */
static size_t acc_driver_os_stack_get_usage(size_t stack_size)
{
	if (!stack_size || !acc_os_stack_setup_done)
		return 0;

	uint8_t stack_filler[stack_size];
	size_t	usage = 0;

	/* This does not give an exact figure but is useful as an indication of the used size.
	   The reason for counting backwards to allow future improvement handling any misalignment
	   garbage at the end. */
	for (size_t index = stack_size - 1; index; index--)
		if (stack_filler[index] != 0x5a)
			usage += 1;

	return usage;
}


/**
 * @brief Sleep for a specified number of microseconds
 *
 * @param time_usec Time in microseconds to sleep
 */
static void acc_driver_os_sleep_us(uint32_t time_usec)
{
	struct timespec	ts;

	if (time_usec == 0) {
		time_usec = 1;
	}

	ts.tv_sec  = time_usec / 1000000;
	ts.tv_nsec = (time_usec % 1000000) * 1000;

	nanosleep(&ts, NULL);
}


/**
 * @brief Return the unique thread ID for the current thread
 */
static acc_os_thread_id_t acc_driver_os_get_thread_id(void)
{
	return syscall(SYS_gettid);
}


/**
 * @brief Get current time and return as microseconds
 *
 * @param time_usec	Time in microseconds is returned here
 */
static void acc_driver_os_get_time(uint32_t *time_usec)
{
	struct timespec time_ts;
	int result = clock_gettime(CLOCK_MONOTONIC, &time_ts);

	if (result != 0)
	{
		ACC_LOG_ERROR("clock_gettime returned %d %d %s", result, errno, strerror(errno));
	}

	*time_usec = time_ts.tv_sec * 1000000 + time_ts.tv_nsec / 1000;
}


/**
 * @brief Create a mutex
 *
 * @return Newly initialized mutex
 */
static acc_os_mutex_t acc_driver_os_mutex_create(void)
{
	acc_os_mutex_t mutex = acc_os_mem_alloc(sizeof(*mutex));

	if (mutex != NULL) {
		pthread_mutex_init(&mutex->mutex, NULL);
		mutex->is_initialized = 1;
	}

	return mutex;
}


static void acc_driver_os_mutex_destroy(acc_os_mutex_t mutex)
{
	pthread_mutex_destroy(&mutex->mutex);
	acc_os_mem_free(mutex);
}


/**
 * @brief Mutex lock
 *
 * @param mutex Mutex to be locked
 */
static void acc_driver_os_mutex_lock(acc_os_mutex_t mutex)
{
	pthread_mutex_lock(&mutex->mutex);
}


/**
 * @brief Mutex unlock
 *
 * @param mutex Mutex to be unlocked
 */
static void acc_driver_os_mutex_unlock(acc_os_mutex_t mutex)
{
	pthread_mutex_unlock(&mutex->mutex);
}


/**
 * @brief Create new thread
 *
 * NB! If you want to run in single thread mode, make sure to NOT
 * implement this function.
 *
 * @param func	Function implementing the thread code
 * @param param	Parameter to be passed to the thread function
 * @param name	Name of the thread used for debugging
 * @return Newly created thread
 */
static acc_os_thread_handle_t acc_driver_os_thread_create(void (*func)(void *param), void *param, const char *name)
{
	int	ret;

	acc_os_thread_handle_t thread = acc_os_mem_alloc(sizeof(*thread));

	if (thread != NULL) {
		// TODO the function cast should be replaced by something safer
		ret = pthread_create(&thread->handle, NULL, (void* (*)(void*))func, param);
		if (ret != 0) {
			ACC_LOG_ERROR("%s: Error %d, %s", __func__, ret, strerror(ret));
			return thread;
		}
		if (name != NULL) {
			ret = pthread_setname_np(thread->handle, name);
			if (ret != 0) {
				ACC_LOG_ERROR("%s: Error setting thread name %d, %s", __func__, ret, strerror(ret));
			}
		}
	}

	ACC_LOG_VERBOSE("%s: created thread_handle=%lu", __func__, (unsigned long)thread->handle);
	return thread;
}


/**
 * @brief Exit current thread
 *
 * There is no return status. If the function returns, it failed.
 */
static void acc_driver_os_thread_exit(void)
{
	size_t stack_usage = acc_driver_os_stack_get_usage(0);

	if (stack_usage > 0)
	{
		ACC_LOG_INFO("Stack usage %u bytes", (unsigned int)stack_usage);
	}

	pthread_exit(NULL);
}


/**
 * @brief Cleanup after thread termination
 *
 * For operating systems that require it, perform any post-thread cleanup operation.
 *
 * @param thread Handle of thread
 */
static void acc_driver_os_thread_cleanup(acc_os_thread_handle_t thread)
{
	ACC_LOG_VERBOSE("acc_driver_os_thread_cleanup: removed thread_handle=%lu", (unsigned long)thread->handle);
	// assume thread is already terminated, or just about to terminate
	int err = pthread_join(thread->handle, NULL);

	if (err != 0) {
		ACC_LOG_ERROR("An error occurred while joining threads: %s", strerror(err));
	}
	else {
		acc_os_mem_free(thread);
	}
}


static acc_os_semaphore_t acc_driver_os_semaphore_create(void)
{
	acc_os_semaphore_t sem = NULL;

	sem = acc_os_mem_alloc(sizeof(*sem));

	if (sem != NULL) {
		if (sem_init(&sem->handle, 0, 0) == -1) {
			return NULL;
		}
		sem->is_initialized	= 1;
	}

	return sem;
}


static bool acc_driver_os_semaphore_wait(acc_os_semaphore_t sem, uint16_t timeout_ms)
{
	struct timespec ts;
	struct timeval tv;

	if (sem == NULL || sem->is_initialized != 1) {
		ACC_LOG_ERROR("Not valid semaphore");
		// Will be handled as timeout by RSS
		return false;
	}

	int result = gettimeofday(&tv, NULL);
	if (result != 0) {
		ACC_LOG_ERROR("gettimeofday returned %d %d %s", result, errno, strerror(errno));
		// Will be handled as timeout by RSS
		return false;
	}

	ts.tv_sec = tv.tv_sec;
	ts.tv_nsec = tv.tv_usec + (timeout_ms * 1000);

	while (ts.tv_nsec >= 1000000) {
		ts.tv_sec++;
		ts.tv_nsec -= 1000000;
	}
	ts.tv_nsec *= 1000;

	if (sem_timedwait(&(sem->handle), &ts) == -1) {
		if (errno == ETIMEDOUT) {
			if (timeout_ms != 0) {
				ACC_LOG_DEBUG("Semaphore timeout");
			}
			return false;
		}
		ACC_LOG_ERROR("An error has occurred: %d", errno);
		// Will be handled as timeout by RSS
		return false;
	}

	return true;
}


static void acc_driver_os_semaphore_signal(acc_os_semaphore_t sem)
{
	if (sem != NULL && sem->is_initialized) {
		sem_post(&sem->handle);
	}
}


static void acc_driver_os_semaphore_signal_from_interrupt(acc_os_semaphore_t sem)
{
	acc_os_semaphore_signal(sem);
}


static void acc_driver_os_semaphore_destroy(acc_os_semaphore_t sem)
{
	if (sem != NULL && sem->is_initialized) {
		sem_destroy(&sem->handle);

		acc_os_mem_free(sem);
	}
}

bool acc_os_driver_get_os(acc_system_os_t *os)
{
	if (os == NULL)	{
		return false;
	}

	os->sleep_us                         = acc_driver_os_sleep_us;
	os->mem_alloc                        = malloc;
	os->mem_free                         = free;
	os->get_thread_id                    = acc_driver_os_get_thread_id;
	os->gettime                          = acc_driver_os_get_time;
	os->mutex_create                     = acc_driver_os_mutex_create;
	os->mutex_destroy                    = acc_driver_os_mutex_destroy;
	os->mutex_lock                       = acc_driver_os_mutex_lock;
	os->mutex_unlock                     = acc_driver_os_mutex_unlock;
	os->thread_create                    = acc_driver_os_thread_create;
	os->thread_exit                      = acc_driver_os_thread_exit;
	os->thread_cleanup                   = acc_driver_os_thread_cleanup;
	os->semaphore_create                 = acc_driver_os_semaphore_create;
	os->semaphore_destroy                = acc_driver_os_semaphore_destroy;
	os->semaphore_wait                   = acc_driver_os_semaphore_wait;
	os->semaphore_signal                 = acc_driver_os_semaphore_signal;
	os->semaphore_signal_from_interrupt  = acc_driver_os_semaphore_signal_from_interrupt;

	return true;
}


void acc_driver_os_linux_register(void)
{
	acc_device_os_init_func					= acc_driver_os_init;
	acc_device_os_stack_setup_func				= acc_driver_os_stack_setup;
	acc_device_os_stack_get_usage_func			= acc_driver_os_stack_get_usage;
	acc_device_os_sleep_us_func				= acc_driver_os_sleep_us;
	acc_device_os_mem_alloc_func				= malloc;
	acc_device_os_mem_free_func				= free;
	acc_device_os_get_thread_id_func			= acc_driver_os_get_thread_id;
	acc_device_os_get_time_func				= acc_driver_os_get_time;
	acc_device_os_mutex_create_func				= acc_driver_os_mutex_create;
	acc_device_os_mutex_lock_func				= acc_driver_os_mutex_lock;
	acc_device_os_mutex_unlock_func				= acc_driver_os_mutex_unlock;
	acc_device_os_mutex_destroy_func			= acc_driver_os_mutex_destroy;
	acc_device_os_thread_create_func			= acc_driver_os_thread_create;
	acc_device_os_thread_exit_func				= acc_driver_os_thread_exit;
	acc_device_os_thread_cleanup_func			= acc_driver_os_thread_cleanup;
	acc_device_os_semaphore_create_func			= acc_driver_os_semaphore_create;
	acc_device_os_semaphore_wait_func			= acc_driver_os_semaphore_wait;
	acc_device_os_semaphore_signal_func			= acc_driver_os_semaphore_signal;
	acc_device_os_semaphore_signal_from_interrupt_func	= acc_driver_os_semaphore_signal_from_interrupt;
	acc_device_os_semaphore_destroy_func			= acc_driver_os_semaphore_destroy;
}
