from smbus2 import SMBus
import time
bus = SMBus(0)
time.sleep(1)

while True:
    counter = 0
    id = ""
    ok = True
    while len(id) < 8:
    #while True:
        try:
            start = time.time()
            print("reading...")
            b = bus.read_byte(0x41)
            end = time.time()
            print(end-start)
            print("read", chr(b))
            if end-start > 1:
                print("set ok to true")
                ok = True
            if ok:
                id += chr(b)
            
        except Exception as e:
            print(e)
            ok = False
            id=""
            continue
    
    #print("resetting counter")
    print("RFID Scanned: ", id)


"""
while True:
    try:
        b = bus.read_byte(0x41)
        print(chr(b))
    except Exception as e:
        print(e)
        continue

bus.close()
"""

ok = True;
id = ""
count = 0;
while True:
    try:    
        if (ok):
            b = bus.read_byte(0x41)
            id += chr(b)
            
            print("reading, ok = T, " + chr(b))

            if (len(id) == 8):
                print(id)
        else:
            b = bus.read_byte(0x41)
            id += chr(b)
            
            print("reading, ok = F, " + chr(b))

            if (count == 8):
                id = chr(b) + id
                ok = True
                print(id)
                id = ""
    except Exception as e:
        print("exception")
        ok = False;
        id = "";
        print(e)

bus.close()
