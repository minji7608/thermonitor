import time
import smbus2
import json
import pydarknet
from pydarknet import Detector, Image
import cv2
import threading
from smbus2 import SMBus
import board
import digitalio
import random
from mttkinter import *
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = 'HostName=Thermonitor2020.azure-devices.net;DeviceId=jetson-nano-moonji;SharedAccessKey=LoJEq95prhB8PrmZILDDeLqOlALehMaZHgqsgYjPvMI='

MSG_TXT = '{{"temperature": {temperature},"rfid": {rfid}}}'

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

#globals
lock = threading.Lock()

ready = False
current_rfid = "" 
prev_rfid = ""
curr_temp = -1

rled = digitalio.DigitalInOut(board.D17)
gled = digitalio.DigitalInOut(board.D18)
rled.direction = digitalio.Direction.OUTPUT
gled.direction = digitalio.Direction.OUTPUT



def start_RFID():
    global current_rfid
    global prev_rfid
    bus=SMBus(0)
    time.sleep(1)
    ok = True
    id = ""
    while True:
        
        try:
            gled.value=False
            print("reading...")
            start=time.time()
            b=bus.read_byte(0x41)
            
            id+=chr(b)
            print("read", chr(b))
            if(len(id)) % 2 == 1:
                gled.value = True
            else:
                gled.value = False



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

        except Exception as e:
            print(e)
            end = time.time()
            #print(end-start)
            if(end-start > 2):
                print("resetting prev_rfid")
                lock.acquire()
                prev_rfid=""
                current_rfid =""
                lock.release()
            ok = False
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
    temp = (val * 0.02) - 273.15 + 2

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
    display_width=800,
    display_height=590,
    framerate=5,
    flip_method=6,
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
        
def drawbox(x,y,w,h, frame, color, thickness):
    tl = (int(x-w/2), int(y-h/2))
    tr = (int(x+w/2), int(y-h/2))
    bl = (int(x-w/2), int(y+h/2))
    br = (int(x+w/2), int(y+h/2))

    tl1 = (int(tl[0]+w/4), tl[1])
    tl2 = (tl[0], int(tl[1]+h/4))
                
    tr1 = (int(tr[0]-w/4), tr[1])
    tr2 = (tr[0], int(tr[1]+h/4))
                
    bl1 = (int(bl[0]+w/4), bl[1])
    bl2 = (bl[0], int(bl[1]-h/4))

    br1 = (int(br[0]-w/4), br[1])
    br2 = (br[0], int(br[1]-h/4))

    cv2.line(frame, tl, tl1, color, thickness)
    cv2.line(frame, tl, tl2, color, thickness)
               
    cv2.line(frame, tr, tr1, color, thickness)
    cv2.line(frame, tr, tr2, color, thickness)


    cv2.line(frame, bl, bl1, color, thickness)
    cv2.line(frame, bl, bl2, color, thickness)

    cv2.line(frame, br, br1, color, thickness)
    cv2.line(frame, br, br2, color, thickness)


   
def facedetect():
    global current_rfid
    global prev_rfid
    global curr_temp
    global ready
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
            areas = []
            for cat, score, bounds in results:
                x, y, w, h = bounds
                area = int(w) * int(h)
                areas.append(area)


            maskon = False
            cv2.ellipse(frame, (400,250), (120,180), 0, 0, 360, (169,169,169), 1)
            for cat, score, bounds in results:

                x, y, w, h = bounds
                area = int(w) * int(h)

                if str(cat.decode("utf-8")) == "Mask On":
                    color = (0,255,0)
                elif str(cat.decode("utf-8"))=="Face Forward":
                    color = (255, 255, 0)
                else:
                    color = (0, 0, 255)

                if area == max(areas):
                    if(str(cat.decode("utf-8")) == "Mask On"):
                        maskon = True
                    thickness = 5
                    drawbox(x,y,w,h, frame, color, thickness)
                    cv2.putText(frame, str(cat.decode("utf-8")),
                    (int(x)-50, int(y)-160), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, color, 2)
                     #cv2.putText(frame, str(round(temperature,2))+"C", (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                else:
                    thickness = 1
               
               
                #cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color, thickness)
                #cv2.putText(frame, str(cat.decode("utf-8")), (int(x)-50, int(y)-160), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                #cv2.putText(frame, str(round(temperature,2))+"C", (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                lock.acquire()
                #print("THIS IS CURR RFID", current_rfid)
                #print("THIS IS PREV_RFID", prev_rfid) 
                if maskon == True and current_rfid != "" and current_rfid != prev_rfid and int(round(temperature,2)) > 32:
                    counter = 0
                    while counter < 50:
                        if int(round(temperature,2)) < 32:
                            break
                        if current_temp == -1:
                            current_temp = temperature
                        else:
                            current_temp = (current_temp + temperature)/2
                        counter+=1
                    
                    msg_json = {
                            "rfid" : str(current_rfid),
                            "temperature" : str(round(current_temp,2))
                    }

                    msg_txt_formatted = json.dumps(msg_json)
                     
                    message = Message(msg_txt_formatted)
                    print("Sending message: {}".format(message))
                    client.send_message(message)
                    print("Message successfully sent")

                    prev_rfid = current_rfid
                    current_rfid = ""
                    curr_temp = current_temp
                    ready=True
                    print("this is avg of ur current temp and rfid", current_rfid, round(current_temp,2))
                lock.release()
               

            cv2.namedWindow('preview', cv2.WINDOW_NORMAL)
            #cv2.setWindowProperty('preview', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            cv2.resizeWindow("preview", 800, 590)
            cv2.moveWindow("preview", 0, 0)
            cv2.imshow("preview", frame)
            #cv2.namedWindow('preview', cv2.WND_PROP_FULLSCREEN)

            #cv2.setWindowProperty('preview', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
    cap.release()


def displaytemp():
    #global current_rfid
    #global curr_temp
    my_window = mtTkinter.Tk()
    ws = my_window.winfo_screenwidth()
    hs = my_window.winfo_screenheight()
    tkheight = 100
    my_window.attributes('-type', 'dock')
    my_window.geometry('%dx%d+%d+%d' % (ws, tkheight, 0, (hs-tkheight)))
    sleep = False

    T = mtTkinter.Label(my_window, text="PLEASE TAP YOUR ID", bg="#808080", fg="white", font="none 24", height = 50, width = 50, anchor = mtTkinter.CENTER)
    T.pack()  
 
    def redraw():
        global ready
        nonlocal sleep
        global curr_temp
        global current_rfid
        nonlocal T 
        if sleep:
            time.sleep(5)
            sleep = False
        lock.acquire()
       
        if ready:
            print("DRAWING CURR TEMP:", curr_temp)
            if curr_temp > 38:
                T.config(text="FAIL "+str(round(curr_temp,2))+"C", bg="#b53737", fg="white")

            elif curr_temp > 32 and curr_temp <= 38:
                T.config(text="PASS  "+str(round(curr_temp,2))+"C", bg="#06a94d", fg="white")
            else:
                T.config(text="INVALID", bg="#ffff00", fg="white")

            sleep = True
            ready = False
        elif current_rfid:
            T.config(text="RFID SCANNED\n Please hold still. Taking temperature...", font = "none 18",  bg="#333333", fg="white")
            
        else:
            T.config(text="PLEASE TAP YOUR ID", bg="#808080", font="none 24", height = 50, width = 50)
        lock.release()
        my_window.after(100, redraw)
    redraw()
    my_window.mainloop()



t=threading.Thread(target=start_RFID)
t2 = threading.Thread(target=facedetect)
t.start()
t2.start()
displaytemp()

