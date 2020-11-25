import time
import smbus2

i2c_ch = 1

# TMP102 address on the I2C bus
i2c_address = 0x5a

# Register addresses
reg_temp = 0x07
reg_config = 0x25

# Calculate the 2's complement of a number
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# Read temperature registers and calculate Celsius
def read_temp():

    # Read temperature registers
    val = bus.read_word_data(i2c_address, reg_temp)
    temp = (val * 0.02) - 273.15

    return temp

# Initialize I2C (SMBus)
bus = smbus2.SMBus(i2c_ch)

# Read the CONFIG register (2 bytes)
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("Old CONFIG:", val)

# Set to 4 Hz sampling (CR1, CR0 = 0b10)
val[1] = val[1] & 0b00111111
val[1] = val[1] | (0b10 << 6)

# Write 4 Hz sampling back to CONFIG
bus.write_i2c_block_data(i2c_address, reg_config, val)

# Read CONFIG to verify that we changed it
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("New CONFIG:", val)

# Print out temperature every second
while True:
    temperature = read_temp()
    print(round(temperature, 2), "C")
    time.sleep(0.5)
