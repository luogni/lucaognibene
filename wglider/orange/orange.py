import socket
import serial
import sys
import datetime
import time

try:
    MODE = sys.argv[1]
except:
    MODE = "test-battery"


def open_serial():
    for i in range(0, 10):
        d = "/dev/ttyUSB%d" % i
        try:
            ser = serial.Serial(d, 57600)
            print "Using", d
            print ser.read()
            ser.write('8 b')
            time.sleep(1)
            return ser
        except:
            continue
    return None


def send(m0, m1, r, sl=0, repeat=1):
    # rr = repeat
    # while rr > 0:
    #     ser.write('67,77,%d,%d,%d,20 s' % (int(m0), int(m1), int(r)))
    #     if sl > 0:
    #         time.sleep(sl)
    #     rr -= 1
    pass

ser = open_serial()

if MODE == "test-321321":
    # send(255, 255, 0, 1, 10)
    pass
else:
    for line in ser:
        spl = line.split(' ')
        if (spl[0] == "OK")and(int(spl[1]) == 21)and(int(spl[2]) == ord('Y')):
            level = int(spl[4]) * 256 + int(spl[3])
            with open("battery.log", "a") as f:
                print datetime.datetime.now(), level
                f.write(str(datetime.datetime.now()) + " " + str(level) + "\n")

