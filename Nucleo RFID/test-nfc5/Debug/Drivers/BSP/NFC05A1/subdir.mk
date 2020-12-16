################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Drivers/BSP/NFC05A1/led.c 

OBJS += \
./Drivers/BSP/NFC05A1/led.o 

C_DEPS += \
./Drivers/BSP/NFC05A1/led.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/BSP/NFC05A1/led.o: ../Drivers/BSP/NFC05A1/led.c
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DUSE_HAL_DRIVER -DSTM32L476xx -DDEBUG -c -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Core/Inc" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/BSP/Components/ST25R3911" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/BSP/NFC05A1" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/BSP/STM32L4xx_Nucleo" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/CMSIS/Device/ST/STM32L4xx/Include" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/CMSIS/Include" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/STM32L4xx_HAL_Driver/Inc" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Drivers/STM32L4xx_HAL_Driver/Inc/Legacy" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Middlewares/ST/ndef/Inc/message" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Middlewares/ST/ndef/Inc/poller" -I"C:/Users/Charles/STM32CubeIDE/workspace_1.4.0/test-nfc5/Middlewares/ST/rfal/Inc" -I../Drivers/CMSIS/Include -I../Core/Inc -I../Drivers/CMSIS/Device/ST/STM32L4xx/Include -I../Drivers/STM32L4xx_HAL_Driver/Inc -I../Drivers/STM32L4xx_HAL_Driver/Inc/Legacy -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"Drivers/BSP/NFC05A1/led.d" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

