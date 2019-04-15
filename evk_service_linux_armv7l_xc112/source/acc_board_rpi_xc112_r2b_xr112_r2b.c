// Copyright (c) Acconeer AB, 2018-2019
// All rights reserved

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "acc_board.h"
#include "acc_definitions.h"
#include "acc_device.h"
#include "acc_device_gpio.h"
#include "acc_device_i2c.h"
#include "acc_device_os.h"
#include "acc_device_spi.h"
#include "acc_log.h"

#if defined(TARGET_OS_android)
#include "acc_driver_gpio_android.h"
#include "acc_driver_os_android.h"
#include "acc_driver_spi_android.h"
#elif defined(TARGET_OS_linux)
#include "acc_device_memory.h"
#include "acc_driver_24cxx.h"
#include "acc_driver_gpio_linux_sysfs.h"
#include "acc_driver_i2c_linux.h"
#include "acc_driver_os_linux.h"
#include "acc_driver_spi_linux_spidev.h"
#else
#error "Target operating system is not supported"
#endif

/**
 * @brief The module name
 */
#define MODULE "board_rpi_xc112_r2b"

#define I2C_24CXX_DEVICE_ID   0x50
#define I2C_24CXX_MEMORY_SIZE 0x4000
#define BOARD_DATA_LENGTH     51

#define PIN_HIGH (1)
#define PIN_LOW  (0)

#define SENSOR_COUNT (4) /**< @brief The number of sensors available on the board */

#define PIN_PMU_EN (17) /**< @brief PMU_EN BCM:17 J5:11 */

#define PIN_SS_N            (8)  /**< @brief SPI SSn BCM:8 J5:24 */
#define PIN_SPI_ENABLE_S1_N (18) /**< @brief SPI S1 enable BCM:18 J5:12 */
#define PIN_SPI_ENABLE_S2_N (27) /**< @brief SPI S2 enable BCM:27 J5:13 */
#define PIN_SPI_ENABLE_S3_N (22) /**< @brief SPI S3 enable BCM:22 J5:15 */
#define PIN_SPI_ENABLE_S4_N (7)  /**< @brief SPI S4 enable BCM:7 J5:26 */

#define PIN_ENABLE_N      (6)  /**< @brief Gpio Enable BCM:4 J5:31 */
#define PIN_ENABLE_S1_3V3 (23) /**< @brief Gpio Enable S1 BCM:23 J5:16 */
#define PIN_ENABLE_S2_3V3 (5)  /**< @brief Gpio Enable S2 BCM:5 J5:29 */
#define PIN_ENABLE_S3_3V3 (12) /**< @brief Gpio Enable S3 BCM:12 J5:32 */
#define PIN_ENABLE_S4_3V3 (26) /**< @brief Gpio Enable S4 BCM:26 J5:37 */

#define PIN_SENSOR_INTERRUPT_S1_3V3 (20) /**< @brief Gpio Interrupt S1 BCM:20 J5:38, connect to sensor 1 GPIO 5 */
#define PIN_SENSOR_INTERRUPT_S2_3V3 (21) /**< @brief Gpio Interrupt S2 BCM:21 J5:40, connect to sensor 2 GPIO 5 */
#define PIN_SENSOR_INTERRUPT_S3_3V3 (24) /**< @brief Gpio Interrupt S3 BCM:24 J5:18, connect to sensor 3 GPIO 5 */
#define PIN_SENSOR_INTERRUPT_S4_3V3 (25) /**< @brief Gpio Interrupt S4 BCM:25 J5:22, connect to sensor 4 GPIO 5 */

#define ACC_BOARD_REF_FREQ  (24000000) /**< @brief The reference frequency assumes 26 MHz on reference board */
#define ACC_BOARD_SPI_SPEED (15000000) /**< @brief The SPI speed of this board */
#define ACC_BOARD_BUS       (0)        /**< @brief The SPI bus of this board */
#define ACC_BOARD_CS        (0)        /**< @brief The SPI device of the board */

/**
 * @brief Number of GPIO pins
 */
#define GPIO_PIN_COUNT 28

/**
 * @brief Sensor states
 */
typedef enum
{
	SENSOR_DISABLED,
	SENSOR_ENABLED,
	SENSOR_ENABLED_AND_SELECTED
} acc_board_sensor_state_t;

typedef struct
{
	acc_board_sensor_state_t state;
	const uint8_t            enable_pin;
	const uint8_t            interrupt_pin;
	const uint8_t            slave_select_pin;
} acc_sensor_pins_t;

static acc_sensor_pins_t sensor_pins[SENSOR_COUNT] = {
	{.state            = SENSOR_DISABLED,
	 .enable_pin       = PIN_ENABLE_S1_3V3,
	 .interrupt_pin    = PIN_SENSOR_INTERRUPT_S1_3V3,
	 .slave_select_pin = PIN_SPI_ENABLE_S1_N},
	{.state            = SENSOR_DISABLED,
	 .enable_pin       = PIN_ENABLE_S2_3V3,
	 .interrupt_pin    = PIN_SENSOR_INTERRUPT_S2_3V3,
	 .slave_select_pin = PIN_SPI_ENABLE_S2_N},
	{.state            = SENSOR_DISABLED,
	 .enable_pin       = PIN_ENABLE_S3_3V3,
	 .interrupt_pin    = PIN_SENSOR_INTERRUPT_S3_3V3,
	 .slave_select_pin = PIN_SPI_ENABLE_S3_N},
	{.state            = SENSOR_DISABLED,
	 .enable_pin       = PIN_ENABLE_S4_3V3,
	 .interrupt_pin    = PIN_SENSOR_INTERRUPT_S4_3V3,
	 .slave_select_pin = PIN_SPI_ENABLE_S4_N}
};

static acc_board_isr_t     master_isr;
static acc_device_handle_t spi_handle;
static gpio_t              gpios[GPIO_PIN_COUNT];


static void isr_sensor1(void)
{
	if (master_isr)
	{
		master_isr(1);
	}
}


static void isr_sensor2(void)
{
	if (master_isr)
	{
		master_isr(2);
	}
}


static void isr_sensor3(void)
{
	if (master_isr)
	{
		master_isr(3);
	}
}


static void isr_sensor4(void)
{
	if (master_isr)
	{
		master_isr(4);
	}
}


/**
 * @brief Handle to the i2c device for EEPROM
 */
#if defined(TARGET_OS_linux)
static acc_device_handle_t device_handle_i2c_1;

#endif

/**
 * @brief Private function to check if there is at least one active sensor
 *
 * @return True if there is at least one active sensor, false otherwise
 */
static bool any_sensor_active();


bool acc_board_gpio_init(void)
{
	static bool           init_done  = false;

	if (init_done)
	{
		return true;
	}

	acc_os_init();

	/*
	   NOTE:
	        Observe that initial pull state of PIN_ENABLE_N, PIN_ENABLE_S2_3V3,
	        PIN_SS_N, PIN_SPI_ENABLE_S4_N, PIN_I2C_SCL_1 and PIN_I2C_SDA_1 pins are HIGH
	        The rest of the pins are LOW
	 */
	if (
		!acc_device_gpio_set_initial_pull(PIN_SENSOR_INTERRUPT_S1_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SENSOR_INTERRUPT_S2_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SENSOR_INTERRUPT_S3_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SENSOR_INTERRUPT_S4_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_ENABLE_N, PIN_HIGH) ||
		!acc_device_gpio_set_initial_pull(PIN_ENABLE_S1_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_ENABLE_S2_3V3, PIN_HIGH) ||
		!acc_device_gpio_set_initial_pull(PIN_ENABLE_S3_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_ENABLE_S4_3V3, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SS_N, PIN_HIGH) ||
		!acc_device_gpio_set_initial_pull(PIN_SPI_ENABLE_S1_N, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SPI_ENABLE_S2_N, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SPI_ENABLE_S3_N, PIN_LOW) ||
		!acc_device_gpio_set_initial_pull(PIN_SPI_ENABLE_S4_N, PIN_HIGH) ||
		!acc_device_gpio_set_initial_pull(PIN_PMU_EN, PIN_LOW))
	{
		ACC_LOG_WARNING("%s: failed to set initial pull", __func__);
	}

	/*
	   NOTE:
	        PIN_ENABLE_N is active low and controls the /OE (output enable, active low) of the level shifter).
	        The PIN_ENABLE_N is inited two times, first we set it high to disable the chip
	        until ENABLE_S1-4 are inited.
	        The second time the PIN_ENABLE_N is set low in order for the chip to become enabled.
	 */
	if (
		!acc_device_gpio_write(PIN_PMU_EN, PIN_LOW) ||
		!acc_device_gpio_write(PIN_ENABLE_N, PIN_HIGH) ||
		!acc_device_gpio_write(PIN_SS_N, PIN_HIGH) ||
		!acc_device_gpio_input(PIN_SENSOR_INTERRUPT_S1_3V3) ||
		!acc_device_gpio_input(PIN_SENSOR_INTERRUPT_S2_3V3) ||
		!acc_device_gpio_input(PIN_SENSOR_INTERRUPT_S3_3V3) ||
		!acc_device_gpio_input(PIN_SENSOR_INTERRUPT_S4_3V3) ||
		!acc_device_gpio_write(PIN_ENABLE_S1_3V3, PIN_LOW) ||
		!acc_device_gpio_write(PIN_ENABLE_S2_3V3, PIN_LOW) ||
		!acc_device_gpio_write(PIN_ENABLE_S3_3V3, PIN_LOW) ||
		!acc_device_gpio_write(PIN_ENABLE_S4_3V3, PIN_LOW) ||
		!acc_device_gpio_write(PIN_SPI_ENABLE_S1_N, PIN_HIGH) ||
		!acc_device_gpio_write(PIN_SPI_ENABLE_S2_N, PIN_HIGH) ||
		!acc_device_gpio_write(PIN_SPI_ENABLE_S3_N, PIN_HIGH) ||
		!acc_device_gpio_write(PIN_SPI_ENABLE_S4_N, PIN_HIGH))
	{
		return false;
	}

	init_done = true;

	return true;
}


bool acc_board_init(void)
{
	static bool           init_done  = false;

	if (init_done)
	{
		return true;
	}

#if defined(TARGET_OS_android)
	acc_driver_os_android_register();
#elif defined(TARGET_OS_linux)
	acc_driver_os_linux_register();
#endif

	acc_os_init();

#if defined(TARGET_OS_android)
	acc_driver_gpio_android_register(GPIO_PIN_COUNT, gpios);
	acc_driver_spi_android_register();
	// NOTE: The i2c driver for Android is not yet implemented
#elif defined(TARGET_OS_linux)
	acc_driver_gpio_linux_sysfs_register(GPIO_PIN_COUNT, gpios);
	acc_driver_spi_linux_spidev_register();
	// EEPROM connected via i2c
	acc_driver_i2c_linux_register();
#endif

	acc_device_gpio_init();

	acc_device_spi_configuration_t configuration;

	configuration.bus           = ACC_BOARD_BUS;
	configuration.configuration = NULL;
	configuration.device        = ACC_BOARD_CS;
	configuration.master        = true;
	configuration.speed         = ACC_BOARD_SPI_SPEED;

	spi_handle = acc_device_spi_create(&configuration);

#if defined(TARGET_OS_linux)

	acc_device_i2c_configuration_t i2c_1_configuration;

	i2c_1_configuration.bus                   = 1;
	i2c_1_configuration.master                = true;
	i2c_1_configuration.mode.master.frequency = 400000;
	device_handle_i2c_1                       = acc_device_i2c_create(i2c_1_configuration);

	if (device_handle_i2c_1 != NULL)
	{
		acc_driver_24cxx_register(device_handle_i2c_1, I2C_24CXX_DEVICE_ID, I2C_24CXX_MEMORY_SIZE);

		acc_device_memory_init();

		char buffer[BOARD_DATA_LENGTH];

		if (acc_device_memory_read(0, buffer, BOARD_DATA_LENGTH) == ACC_STATUS_SUCCESS)
		{
			buffer[BOARD_DATA_LENGTH - 1] = 0;
			ACC_LOG_INFO("Board data from EEPROM: %s", buffer);
		}
		else
		{
			ACC_LOG_ERROR("Board data could not be read");
		}
	}
	else
	{
		ACC_LOG_ERROR("Could not create i2c_device");
	}

#endif

	init_done = true;

	return true;
}


static bool any_sensor_active()
{
	for (uint_fast8_t i = 0; i < SENSOR_COUNT; i++)
	{
		if (sensor_pins[i].state != SENSOR_DISABLED)
		{
			return true;
		}
	}

	return false;
}


void acc_board_start_sensor(acc_sensor_id_t sensor)
{
	acc_sensor_pins_t *p_sensor = &sensor_pins[sensor - 1];

	if (p_sensor->state != SENSOR_DISABLED)
	{
		ACC_LOG_ERROR("Sensor %" PRIsensor " already enabled.", sensor);
		return;
	}

	if (!any_sensor_active())
	{
		// No active sensors yet, set pmu high to start the board

		if (!acc_device_gpio_write(PIN_PMU_EN, PIN_HIGH))
		{
			ACC_LOG_ERROR("Couldn't enable pmu for sensor %" PRIsensor, sensor);
			return;
		}

		// Wait for the board to power up
		acc_os_sleep_us(5000);

		if (!acc_device_gpio_write(PIN_ENABLE_N, PIN_LOW))
		{
			ACC_LOG_ERROR("Couldn't set enable to low for sensor %" PRIsensor, sensor);
			return;
		}

		acc_os_sleep_us(5000);
	}

	if (!acc_device_gpio_write(p_sensor->enable_pin, PIN_HIGH))
	{
		ACC_LOG_ERROR("Unable to activate ENABLE on sensor %" PRIsensor, sensor);
		return;
	}

	acc_os_sleep_us(5000);

	p_sensor->state = SENSOR_ENABLED;
}


void acc_board_stop_sensor(acc_sensor_id_t sensor)
{
	acc_sensor_pins_t *p_sensor = &sensor_pins[sensor - 1];

	if (p_sensor->state != SENSOR_DISABLED)
	{
		// "unselect" spi slave select
		if (p_sensor->state == SENSOR_ENABLED_AND_SELECTED)
		{
			if (!acc_device_gpio_write(p_sensor->slave_select_pin, PIN_HIGH))
			{
				ACC_LOG_ERROR("Failed to deselect sensor %" PRIsensor, sensor);
				return;
			}
		}

		// Disable sensor
		if (!acc_device_gpio_write(p_sensor->enable_pin, PIN_LOW))
		{
			// Set the state to enabled since it is not selected and failed to disable
			p_sensor->state = SENSOR_ENABLED;
			ACC_LOG_ERROR("Unable to deactivate ENABLE on sensor %" PRIsensor, sensor);
			return;
		}

		p_sensor->state = SENSOR_DISABLED;
	}
	else
	{
		ACC_LOG_ERROR("Sensor %" PRIsensor " already inactive", sensor);
	}

	if (!any_sensor_active())
	{
		// No active sensors, shut down the board to save power
		acc_device_gpio_write(PIN_ENABLE_N, PIN_HIGH);
		acc_device_gpio_write(PIN_PMU_EN, PIN_LOW);
	}
}


bool acc_board_chip_select(acc_sensor_t sensor, uint_fast8_t cs_assert)
{
	acc_sensor_pins_t *p_sensor = &sensor_pins[sensor - 1];

	if (cs_assert)
	{
		if (p_sensor->state == SENSOR_ENABLED)
		{
			// Since only one sensor can be active, loop through all the other sensors and deselect the active one
			for (uint_fast8_t i = 0; i < SENSOR_COUNT; i++)
			{
				if ((i != (sensor - 1)) && (sensor_pins[i].state == SENSOR_ENABLED_AND_SELECTED))
				{
					if (!acc_device_gpio_write(sensor_pins[i].slave_select_pin, PIN_HIGH))
					{
						ACC_LOG_ERROR("Failed to deselect sensor %" PRIsensor "", sensor);
						return false;
					}

					sensor_pins[i].state = SENSOR_ENABLED;
				}
			}

			// Select the sensor
			if (!acc_device_gpio_write(p_sensor->slave_select_pin, PIN_LOW))
			{
				ACC_LOG_ERROR("Failed to select sensor %" PRIsensor "", sensor);
				return false;
			}

			p_sensor->state = SENSOR_ENABLED_AND_SELECTED;

			return true;
		}
		else if (p_sensor->state == SENSOR_DISABLED)
		{
			ACC_LOG_ERROR("Failed to select sensor %" PRIsensor ", it is disabled", sensor);

			return ACC_STATUS_FAILURE;
		}
		else if (p_sensor->state == SENSOR_ENABLED_AND_SELECTED)
		{
			ACC_LOG_DEBUG("Sensor %" PRIsensor " already selected", sensor);

			return ACC_STATUS_SUCCESS;
		}
		else
		{
			ACC_LOG_ERROR("Unknown state when selecting sensor %" PRIsensor, sensor);

			return ACC_STATUS_FAILURE;
		}
	}
	else
	{
		if (p_sensor->state == SENSOR_ENABLED_AND_SELECTED)
		{
			if (!acc_device_gpio_write(p_sensor->slave_select_pin, PIN_HIGH))
			{
				ACC_LOG_ERROR("Failed to deselect sensor %" PRIsensor "", sensor);
				return ACC_STATUS_FAILURE;
			}

			p_sensor->state = SENSOR_ENABLED;
		}
	}

	return ACC_STATUS_SUCCESS;
}


uint32_t acc_board_get_sensor_count(void)
{
	return SENSOR_COUNT;
}


acc_status_t acc_board_register_isr(acc_board_isr_t isr)
{
	if (isr != NULL)
	{
		if (
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S1_3V3, ACC_DEVICE_GPIO_EDGE_RISING, &isr_sensor1) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S2_3V3, ACC_DEVICE_GPIO_EDGE_RISING, &isr_sensor2) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S3_3V3, ACC_DEVICE_GPIO_EDGE_RISING, &isr_sensor3) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S4_3V3, ACC_DEVICE_GPIO_EDGE_RISING, &isr_sensor4))
		{
			return ACC_STATUS_FAILURE;
		}
	}
	else
	{
		if (
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S1_3V3, ACC_DEVICE_GPIO_EDGE_NONE, NULL) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S2_3V3, ACC_DEVICE_GPIO_EDGE_NONE, NULL) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S3_3V3, ACC_DEVICE_GPIO_EDGE_NONE, NULL) ||
			!acc_device_gpio_register_isr(PIN_SENSOR_INTERRUPT_S4_3V3, ACC_DEVICE_GPIO_EDGE_NONE, NULL))
		{
			return ACC_STATUS_FAILURE;
		}
	}

	master_isr = isr;

	return ACC_STATUS_SUCCESS;
}


bool acc_board_is_sensor_interrupt_connected(acc_sensor_id_t sensor)
{
	ACC_UNUSED(sensor);

	return true;
}


bool acc_board_is_sensor_interrupt_active(acc_sensor_id_t sensor)
{
	uint_fast8_t value;

	if (!acc_device_gpio_read(sensor_pins[sensor - 1].interrupt_pin, &value))
	{
		ACC_LOG_ERROR("Could not obtain GPIO interrupt value for sensor %" PRIsensor "", sensor);
		return false;
	}

	return value != 0;
}


float acc_board_get_ref_freq(void)
{
	return ACC_BOARD_REF_FREQ;
}


bool acc_board_set_ref_freq(float ref_freq)
{
	ACC_UNUSED(ref_freq);

	return false;
}


void acc_board_sensor_transfer(acc_sensor_t sensor_id, uint8_t *buffer, size_t buffer_length)
{
	uint_fast8_t bus = acc_device_spi_get_bus(spi_handle);

	acc_device_spi_lock(bus);

	if (!acc_board_chip_select(sensor_id, 1))
	{
		ACC_LOG_ERROR("%s failed", __func__);
		acc_device_spi_unlock(bus);
		return;
	}

	if (!acc_device_spi_transfer(spi_handle, buffer, buffer_length))
	{
		acc_device_spi_unlock(bus);
		return;
	}

	acc_board_chip_select(sensor_id, 0);

	acc_device_spi_unlock(bus);
	}
