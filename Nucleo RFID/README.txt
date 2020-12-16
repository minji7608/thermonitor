This folder contains: 
	test-nfc5/
	test-nfc5.bin

The test-nfc5.bin file can be dragged directly to the Nucleo board to flash it with working code. 
The test-nfc5 folder contains all the necessary library files and code that generated the test-nfc5.bin file. Everything was compiled and ran using STMCubeIDE. 

The microcontroller unit used is the STM32 Nucleo L476RG board, and an expansion board X-NUCLEO-NFC05 is used to poll for and RFID to be tapped. 

UART is used for serial communication debugging with a baud rate of 115200. 

I2C is used, where the Nucleo board is a slave device and is able to transmit to a master device. The slave address of the Nucleo board is set as 0x41. 


Useful Links: 
https://my.st.com/content/my_st_com/en/products/evaluation-tools/product-evaluation-tools/mcu-mpu-eval-tools/stm32-mcu-mpu-eval-tools/stm32-nucleo-boards/nucleo-l476rg.html

https://www.st.com/content/st_com/en/products/ecosystems/stm32-open-development-environment/stm32-nucleo-expansion-boards/stm32-ode-connect-hw/x-nucleo-nfc05a1.html#documentation 

https://os.mbed.com/platforms/ST-Nucleo-L476RG/