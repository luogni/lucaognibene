import socket


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


UDP_IP = "192.168.1.255"
UDP_PORT = 5555

getch = _GetchUnix()


def send_data(o1, o2, r):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto("cr,%d,%d,%d" % (o2, o1, r), (UDP_IP, UDP_PORT))


c = ''
o1 = 60
o2 = 0
r = 0
while c != 'q':
    c = getch()
    if c == 'i':
        o1 -= 1
    elif c == 'k':
        o1 += 1
    elif c == 'j':
        o2 += 1
    elif c == 'l':
        o2 -= 1
    print o1, o2
    send_data(o1, o2, 0)

