import serial
import sys
import datetime
import shelve
import os

try:
    s = sys.argv[1]
except:
    s = '/dev/ttyUSB0'

print "talk to scope via", s

try:
    os.unlink('data.shelve')
except:
    pass
db = shelve.open('data.shelve', writeback=False)
ser = serial.Serial(s, 115200, timeout=1)
old = datetime.datetime.now()
start = datetime.datetime.now()
c = []
count = 0
while True:
    l = ser.read(1)    
    if len (l) == 0:
        continue
    count += 1
    now = datetime.datetime.now()
    c.append(ord(l))
    d = now - old
    ds = now - start
    if d.seconds >= 1:
        print count
        old = now
        count = 0
    if ds.seconds >= 7:
        break
db['data'] = c
db.close()
ser.close()
