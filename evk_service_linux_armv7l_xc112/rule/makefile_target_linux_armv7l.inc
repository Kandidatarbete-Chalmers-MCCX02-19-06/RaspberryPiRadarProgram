TOOLS_PREFIX := arm-linux-gnueabihf-
TOOLS_AR         := $(TOOLS_PREFIX)ar
TOOLS_AS         := $(TOOLS_PREFIX)as
TOOLS_CC         := $(TOOLS_PREFIX)gcc
TOOLS_OBJDUMP    := $(TOOLS_PREFIX)objdump
TOOLS_OBJCOPY    := $(TOOLS_PREFIX)objcopy
TOOLS_SIZE       := $(TOOLS_PREFIX)size

CFLAGS  += -std=c99 -pedantic -Wall -Werror -Wextra -MMD -MP -O3 -g -fPIC -fno-var-tracking-assignments \
	   -DTARGET_OS_linux -DTARGET_ARCH_armv7l \
	   -pthread

# Override optimization level
ifneq ($(ACC_CFG_OPTIM_LEVEL),)
CFLAGS  += $(ACC_CFG_OPTIM_LEVEL)
endif

LDFLAGS += -pthread
LDLIBS  += -ldl -lm -lrt

# Wrappers that enable cross-compiling on Ubuntu 18 and latest versions of Debian.
LDFLAGS += -Wl,--wrap=expf
LDFLAGS += -Wl,--wrap=logf
LDFLAGS += -Wl,--wrap=powf

# Uncomment to build for gprof profiling
#CFLAGS  += -pg
#LDFLAGS += -pg

TARGET_OS           := linux
TARGET_ARCHITECTURE := armv7l
