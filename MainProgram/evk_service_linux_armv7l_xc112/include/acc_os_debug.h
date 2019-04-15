// Copyright (c) Acconeer AB, 2018
// All rights reserved

#ifndef ACC_OS_DEBUG_H_
#define ACC_OS_DEBUG_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
 * Initialization of the debug module
 */
extern void acc_os_debug_init(void* (*mem_alloc)(size_t), void (*mem_free)(void *));


/**
 * @brief Print heap leaks and other useful info about allocations.
 */
extern void acc_os_debug_print_leaks(void);


/**
 * @brief Keeps track of the memory pointer, which is a real allocation
 *
 * @param leak_pointer Pointer to the real allocation that is to be tracked
 * @param size Size of allocation
 * @param file The file that makes the allocation
 * @param line Line number in file where the allocation takes place
 */
extern void acc_os_debug_track_allocation(void *leak_pointer, size_t size, const char *file, uint16_t line);


/**
 * @brief The corresponding untracking function
 *
 * @param leak_pointer Pointer to the real allocation which shoudnt be tracked anymore
 */
extern void acc_os_debug_untrack_allocation(void *leak_pointer);


#endif // ACC_OS_HEAP_DEBUG

#ifdef __cplusplus
}
#endif
