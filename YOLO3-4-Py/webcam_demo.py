import time
import smbus2
import pydarknet
from pydarknet import Detector, Image
import cv2
import threading
from smbus2 import SMBus
import board
import digitalio
import random

from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = 'HostName=Thermonitor2020.azure-devices.net;DeviceId=jetson-nano-moonji;SharedAccessKey=LoJEq95prhB8PrmZILDDeLqOlALehMaZHgqsgYjPvMI='

MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity}}}'

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

lock = threading.Lock()

current_rfid = "" 
prev_rfid = ""
curr_temp = -1
rled = digitalio.DigitalInOut(board.D17)
gled = digitalio.DigitalInOut(board.D18)
rled.direction = digitalio.Direction.OUTPUT
gled.direction = digitalio.Direction.OUTPUT

def start_RFID():
    global current_rfid
    bus=SMBus(0)
    time.sleep(2)
    ok = True
    id = ""
    while True:
        
        #while len(id) < 16 and ok = True :
        try:
            gled.value=False
            print("reading...", ok, len(id))
            b=bus.read_byte(0x41)
            id+=chr(b)
            print("read", chr(b))
            print(id)
            if ok == False and len(id) == 15 or len(id)==16:
                rfid = id[-8:]
                id = ""
                ok = True
                lock.acquire()
                current_rfid = rfid
                lock.release()
                gled.value = True
                time.sleep(3)
                print("RFID Scanned: ", rfid, id)
            elif len(id) == 16:
                rfid = id[-8:]
                lock.acquire()
                current_rfid = rfid
                lock.release()
                id = ""
                ok = True
                gled.value=True
                time.sleep(3)
                print("RFID Scanned: ", rfid)
            #id += chr(b)

        except Exception as e:
            print(e)
            ok = False
            #id=""
            continue

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

# Write 4 Hz sampli.configure(bg='#ffff00')
bus.write_i2c_block_data(i2c_address, reg_config, val)
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("New CONFIG:", val) 



def gstreamer_pipeline(
    capture_width=820,
    capture_height=640,
    display_width=700,
    display_height=590,
    framerate=5,
    flip_method=2,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        #"nvegltransform ! nveglglessink -e"
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        #"videoscale ! "
        #"video/x-raw,width=1280,height=720 ! appsink"
        #"video/x-raw-yuv,width=(int)%d,height=(int)%
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
        )
        
    
def facedetect():
    global current_rfid
    global prev_rfid
    global curr_temp
    current_temp = -1
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)

    net = Detector(bytes("mask-yolov3-tiny-prn.cfg", encoding="utf-8"), bytes("mask-yolov3-tiny-prn.weights", encoding="utf-8"), 0,
                   bytes("obj.data", encoding="utf-8"))

    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

    client = iothub_client_init()
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
            
            #print("FPS: ", fps)
            #print("Elapsed Time:",end_time-start_time)
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
                lock.acquire()
                if current_rfid != "" and current_rfid != prev_rfid and int(round(temperature,2)) > 32:
                    counter = 0
                    while counter < 20:
                        if int(round(temperature,2)) < 32:
                            break
                        if current_temp == -1:
                            current_temp = temperature
                        else:
                            current_temp = (current_temp + temperature)/2
                        counter+=1

                    prev_rfid = current_rfid
                    current_rfid = ""
                    curr_temp = current_temp 
                    print("this is avg of ur current temp and rfid", current_rfid, round(current_temp,2))
                    msg_txt_formatted = MSG_TXT.format(humidity=100, temperature=current_temp)
                    
                    message = Message(msg_txt_formatted)
                    print("Sending message: {}".format(message))
                    client.send_message(message)
                    print("Message successfully sent")
                lock.release()

            cv2.imshow("preview", frame)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
    cap.release()
"""
def displaytemp():
    global current_rfid
    global curr_temp

    my_window = Tk()
    my_window.geometry("100x590")
    def redraw():
        lock.aquire()
        if current_rfid != "":
            if curr_temp > 38:
                my_window.configure(bg='#ff0000')
            elif curr_temp > 32 and curr_temp <= 38:
                my_window.configure(bg='#00ff00')
            else:
                my_window.configure(bg='#ffff00')
        else:
            my_window.configure(bg='#808080')
        lock.release()
        my_window.after(100, redraw)
    redraw()
    my_window.mainloop()
"""

t=threading.Thread(target=start_RFID)
t2 = threading.Thread(target=facedetect)
#t3 = threading.Thread(target=displaytemp)
t.start()
t2.start()
#t3.start()
#displaytemp()

