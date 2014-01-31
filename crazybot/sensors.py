import socket
import serial

host = ''
port = 5555
DEVICE = "/dev/ttyUSB0"
TPOWER = 60
TTURN = 40
m0 = 0
m1 = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))
try:
    ser = serial.Serial(DEVICE, 57600)
except:
    print "Can't open serial device"
    ser = None

while 1:
    message, address = s.recvfrom(8192)
    (ts, y, z, r) = [m.strip() for m in message.split(',')]
    print ts, y, z, r
    power = int(max(0, min(TPOWER - float(z), TPOWER)) * (255.0 / TPOWER))  # 0  255
    turn = max(-TTURN, min(float(y), TTURN)) / float(TTURN)  # -1  +1
    m0 = power
    m1 = power
    if turn < 0:
        m1 *= (1 + turn)
    elif turn > 0:
        m0 *= (1 - turn)
    print int(m0), int(m1), r
    if ser is not None:
        ser.write('67,77,%d,%d,%d,20 s' % (int(m0), int(m1), int(r)))
