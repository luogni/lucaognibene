import socket
import serial
import sys
import time

host = ''
port = 5555
TPOWER = 60
TTURN = 40
m0 = 0
m1 = 0
lastr = 0
lasts = 0

try:
    MODE = sys.argv[1]
except:
    MODE = "proxy"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))


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
    rr = repeat
    while rr > 0:
        ser.write('67,77,%d,%d,%d,20 s' % (int(m0), int(m1), int(r)))
        if sl > 0:
            time.sleep(sl)
        rr -= 1
    
# m0 = m1 = 255
# r = 0
# ser.write('67,77,%d,%d,%d,20 s' % (int(m0), int(m1), 1 - int(r)))

ser = open_serial()

if MODE == "test-forward":
    send(255, 255, 0, 1, 10)
elif MODE == "test-forward-1":
    send(130, 130, 0, 1, 10)
elif MODE == "test-reverse-1":
    send(130, 130, 0, 1, 3)
    send(130, 130, 1, 1, 3)
elif MODE == "test-stop":
    send(0, 0, 0, 1, 10)
else:
    while 1:
        message, address = s.recvfrom(8192)
        (ts, y, z, r) = [m.strip() for m in message.split(',')]
        #print ts, y, z, r
        if (time.time() > lastr + 2)and(lastr > 0)and(MODE != 'norestart'):
            print "restart comm"
            lasts = 0
        lastr = time.time()
        if (lasts == 0):
            lasts = lastr
        if (lastr < lasts + 2):
            continue
        power = int(max(0, min(TPOWER - float(z), TPOWER)) * (255.0 / TPOWER))  # 0  255
        turn = -1 * max(-TTURN, min(float(y), TTURN)) / float(TTURN)  # -1  +1
        m0 = power
        m1 = power
        if turn < 0:
            m1 *= (1 + turn)
        elif turn > 0:
            m0 *= (1 - turn)
        print int(m0), int(m1), r
        if (ser is not None):
            # swap or not based on how i mounted them..
            lasth = time.time()
            send(m0, m1, r)
