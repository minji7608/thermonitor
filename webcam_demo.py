import time
import smbus2
import pydarknet
from pydarknet import Detector, Image
import cv2

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
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("New CONFIG:", val)



def gstreamer_pipeline(
    capture_width=640,
    capture_height=480,
    display_width=640,
    display_height=480,
    framerate=10,
    flip_method=2,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)

    net = Detector(bytes("mask-yolov3-tiny-prn.cfg", encoding="utf-8"), bytes("mask-yolov3-tiny-prn.weights", encoding="utf-8"), 0,
                   bytes("obj.data", encoding="utf-8"))

    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

    while True:
        r, frame = cap.read()
        if r:
            start_time = time.time()

            # Only measure the time taken by YOLO and API Call overhead

            dark_frame = Image(frame)
            results = net.detect(dark_frame)
            del dark_frame

            end_time = time.time()
            # Frames per second can be calculated as 1 frame divided by time required to process 1 frame
            fps = 1 / (end_time - start_time)
            
            print("FPS: ", fps)
            print("Elapsed Time:",end_time-start_time)
            temperature = read_temp()
            for cat, score, bounds in results:
                x, y, w, h = bounds
                if str(cat.decode("utf-8")) == "good":
                    color = (0,255,0)
                else:
                    color = (0, 0, 255)
                cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color)
                #cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                cv2.putText(frame, str(round(temperature,2))+"C", (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))

            cv2.imshow("preview", frame)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
    cap.release()
