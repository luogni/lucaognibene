import socket

host = ''
port = 5555

TPOWER = 60
TTURN = 40
m0 = 0
m1 = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

while 1:
    message, address = s.recvfrom(8192)
    parse = [m.strip() for m in message.split(',')]
    ts = parse[0]
    args = parse[1:]
    for i in xrange(0, len(args), 4):
        if int(args[i]) == 81:
            (y, z) = args[i + 2:i + 4]
            power = int(max(0, min(TPOWER - float(z), TPOWER)) * (255.0 / TPOWER))  # 0  255
            turn = max(-TTURN, min(float(y), TTURN)) / float(TTURN)  # -1  +1
            m0 = power
            m1 = power
            if turn < 0:
                m1 *= (1 + turn)
            elif turn > 0:
                m0 *= (1 - turn)
            print int(m0), int(m1)
