// Copyright (c) Acconeer AB, 2018
// All rights reserved

#ifndef ACC_DRIVER_HAL_H_
#define ACC_DRIVER_HAL_H_

#include "acc_definitions.h"


#ifdef __cplusplus
extern "C" {
#endif


/**
 * @brief Initialize hal driver
 *
 * @return True if initialization is successful
 */
extern bool acc_driver_hal_init(void);


/**
 * @brief Get hal implementation reference
 */
extern acc_hal_t acc_driver_hal_get_implementation(void);


#ifdef __cplusplus
}
#endif

#endif
