# Prevent make message "Nothing to be done for 'all'." by having a top level
# target which always does something (in this case a no-operation)
all_all : all
	@:

all :

BUILD_ALL  :=
BUILD_LIBS :=
BUILD_POST :=

CFLAGS  :=
LDFLAGS :=
LDLIBS  :=

OUT_DIR 	:= out
OUT_OBJ_DIR	:= $(OUT_DIR)/obj
OUT_LIB_DIR	:= $(OUT_DIR)/lib
VPATH		+= $(OUT_LIB_DIR)
LDFLAGS		+= -L$(OUT_LIB_DIR)

ifneq ($(V),)
SUPPRESS :=
else
SUPPRESS := @
endif

include $(wildcard rule/makefile_target_*.inc)

TARGET := $(TARGET_OS)_$(TARGET_ARCHITECTURE)

AR      := $(TOOLS_AR)
AS      := $(TOOLS_AS)
CC      := $(CCACHE) $(TOOLS_CC)
OBJDUMP := $(TOOLS_OBJDUMP)
OBJCOPY := $(TOOLS_OBJCOPY)
SIZE    := $(TOOLS_SIZE)

VPATH   += include/ lib/ source/ user_include/ user_lib/ user_source/
CFLAGS  += -Iinclude/ -Isource/ -Iuser_include/ -Iuser_source/
LDFLAGS += -Llib/ -Luser_lib/

include $(wildcard rule/makefile_define_*.inc)
include $(wildcard rule/makefile_build_*.inc)
include $(wildcard user_rule/makefile_define_*.inc)
include $(wildcard user_rule/makefile_build_*.inc)

SOURCES := $(wildcard source/*.c) $(wildcard user_source/*.c)
DEPENDS := $(addprefix out/, $(notdir $(SOURCES:.c=.d)))

-include $(DEPENDS)

all : $(BUILD_ALL) $(BUILD_LIBS) $(BUILD_POST)

$(BUILD_ALL) : | $(BUILD_LIBS)

$(BUILD_POST) : | $(BUILD_ALL)

$(OUT_OBJ_DIR)/%.o : %.c
	@echo "    Compiling $(notdir $<)"
	$(SUPPRESS)mkdir -p out
	$(SUPPRESS)mkdir -p $(OUT_OBJ_DIR)
	$(SUPPRESS)mkdir -p $(OUT_LIB_DIR)
	$(SUPPRESS)$(COMPILE.c) -o $(OUT_OBJ_DIR)/$(notdir $@) $<

.PHONY : clean
clean :
	$(SUPPRESS)rm -rf out/
	$(SUPPRESS)rm -rf utils/
