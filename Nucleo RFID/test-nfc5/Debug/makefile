################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include Middlewares/ST/rfal/Src/subdir.mk
-include Middlewares/ST/ndef/doc/examples/subdir.mk
-include Middlewares/ST/ndef/Src/poller/subdir.mk
-include Middlewares/ST/ndef/Src/message/subdir.mk
-include Drivers/STM32L4xx_HAL_Driver/Src/Legacy/subdir.mk
-include Drivers/STM32L4xx_HAL_Driver/Src/subdir.mk
-include Drivers/BSP/STM32L4xx_Nucleo/subdir.mk
-include Drivers/BSP/NFC05A1/subdir.mk
-include Drivers/BSP/Components/ST25R3911/subdir.mk
-include Core/Startup/subdir.mk
-include Core/Src/subdir.mk
-include Core/Inc/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
EXECUTABLES += \
test-nfc5.elf \

SIZE_OUTPUT += \
default.size.stdout \

OBJDUMP_LIST += \
test-nfc5.list \

OBJCOPY_BIN += \
test-nfc5.bin \


# All Target
all: test-nfc5.elf secondary-outputs

# Tool invocations
test-nfc5.elf: $(OBJS) $(USER_OBJS) C:\Users\Charles\STM32CubeIDE\workspace_1.4.0\test-nfc5\STM32L476RGTX_FLASH.ld
	arm-none-eabi-gcc -o "test-nfc5.elf" @"objects.list" $(USER_OBJS) $(LIBS) -mcpu=cortex-m4 -T"C:\Users\Charles\STM32CubeIDE\workspace_1.4.0\test-nfc5\STM32L476RGTX_FLASH.ld" --specs=nosys.specs -Wl,-Map="test-nfc5.map" -Wl,--gc-sections -static -L"C:\Users\Charles\STM32CubeIDE\workspace_1.4.0\test-nfc5\Middlewares\ST\ndef" -L"C:\Users\Charles\STM32CubeIDE\workspace_1.4.0\test-nfc5\Middlewares\ST\rfal" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -Wl,--start-group -lc -lm -Wl,--end-group
	@echo 'Finished building target: $@'
	@echo ' '

default.size.stdout: $(EXECUTABLES)
	arm-none-eabi-size  $(EXECUTABLES)
	@echo 'Finished building: $@'
	@echo ' '

test-nfc5.list: $(EXECUTABLES)
	arm-none-eabi-objdump -h -S $(EXECUTABLES) > "test-nfc5.list"
	@echo 'Finished building: $@'
	@echo ' '

test-nfc5.bin: $(EXECUTABLES)
	arm-none-eabi-objcopy  -O binary $(EXECUTABLES) "test-nfc5.bin"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) *
	-@echo ' '

secondary-outputs: $(SIZE_OUTPUT) $(OBJDUMP_LIST) $(OBJCOPY_BIN)

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
