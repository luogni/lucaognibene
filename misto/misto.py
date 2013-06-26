import serial
import sys
import datetime
import bitstring
import shelve
import time
import getopt

opts, args = getopt.getopt(sys.argv[1:],
                           'acs:d:l', ['add', 'clear', 'start=', 'device=', 'last'])

s = '/dev/ttyUSB0'
clear = False
start = 0
add = False
mode = 'add'
for opt, arg in opts:
    if opt in ('-c', '--clear'):
        clear = True
    elif opt in ('-s', '--start'):
        start = int(arg)
    elif opt in ('-d', '--device'):
        s = arg
    elif opt in ('-a', '--add'):
        add = True
    elif opt in ('-l', '--last'):
        mode = 'last'

print "talk to misto via", s, "clear", clear, "start", start, "add", add, "mode", mode

first = True #[RF12demo.6] B i20 g212 @ 868 MHz
REPORT_EVERY = 2
ASK_NUM = 20

def check_first_conf(ser, l):
    conf = True    
    ll = l.split(' ')
    if ll[0] != "[RF12demo.6]":
        print "Error finding correct sketch loaded", ll[0]
        sys.exit(1)
    if (ll[2] != 'i20')or(ll[3] != 'g212')or(ll[5] != '868'):
        conf = False

    if conf == False:
        print "Fixing configuration.."
        ser.writelines(['20i', '212g', '8b', '0c'])
        ser.flush()
    else:
        print "Configuration ok."

def misto_set_time():
    print "Set time"
    n = datetime.datetime.now()
    s = ",".join((str(n.year - 1900), str(n.month), str(n.day), str(n.hour), str(n.minute), str(n.second)))
    ser.write('116,' + s + ",1 s\r\n")

def misto_ask_status(ser):
    print "Ask status"
    ser.write('100,1 s\r\n')

def misto_load(ser, i, num):
    i1 = i / 256
    i2 = i % 256
    num += i
    n1 = num / 256
    n2 = num % 256
    print "Load", i, num, "[", i1, i2, n1, n2, "]"
    ser.write("108,%d,%d,%d,%d,1 s\r\n" % (i1, i2, n1, n2))

def misto_clear_mem(ser):
    print "Clear mem"
    ser.write('99,1 s\r\n')

def parse_reply(ll, fmt):
    s = ""    
    for l in ll:
        s += chr(int(l))
    b = bitstring.BitString(bytes=s)
    return b.unpack(fmt)

def misto_parse_reply(l, db):
    ll = l.split(' ')
    cmd = ll[8]
    data = ll[2:]    
    if cmd in ['2']:
        (y, mo, d, h, m, s, cmd, t1, t2, t3, lowbat) = parse_reply(data, "uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, uintle:8, intle:16, intle:16, intle:16, uint:1")
        t1 /= 10.0
        t2 /= 10.0
        t3 /= 10.0
        try:
            t = datetime.datetime(1900+y, mo, d, h, m, s)
        except:
            print "Not valid", y, mo, d, h, m, s
            return False
        print "Misto status [%s][T1 %.1fC][T2 %.1fC][T3 %.1fC][B %d]" % (str(t), t1, t2, t3, lowbat)
        if add == True:
            db['data'].append({'t': t, 't1': t1, 't2': t2, 't3': t3, 'lowbat': lowbat})
        return True
    else:
        print "Misto unknown status", ll
    return False

def misto_db_sync(db):
    if add == True:
        db.sync()

db = shelve.open('data.shelve', writeback=True)
if db.has_key ('data') == False:
    db['data'] = []

if mode == 'last':
    print db['data'][-1]
    sys.exit(0)
    
ser = serial.Serial(s, 57600, timeout=0.1)
l = ser.readline()
old = datetime.datetime.now()
while True:
    l = l.strip()
    #if l != "":
    #    print l
    if (first == True)and(l != "")and(l != "AVR ISP"):
        check_first_conf(ser, l)
        first = False
        break
    if first == True:
        l = ser.readline()
        continue

misto_set_time()
i = start
started = False
found = 0
while True:    
    if l.startswith('OK'):
        ret = misto_parse_reply(l, db)
        found += 1
        if ret == True:
            started = True
        elif started == True:
            print "No mode data"
            break
    now = datetime.datetime.now()
    d = now - old
    if d.seconds >= REPORT_EVERY:
        if (found > 0):
            #ask only if i've replied to previous command
            i += ASK_NUM
        misto_load(ser, i, ASK_NUM)
        found = 0
        old = now
    l = ser.readline()
misto_db_sync(db)
if clear == True:
    misto_clear_mem(ser)
    time.sleep(5)
ser.close()

