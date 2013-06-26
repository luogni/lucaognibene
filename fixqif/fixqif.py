import os
import sys

fname = sys.argv[1]
f = open(fname, 'r')

fo = open(fname+'-fix', 'w')
fo.write('!Account\r\n')
fo.write('Nmps\r\n')
fo.write('^\r\n')
for l in f.readlines():
    if l.startswith('T+') or l.startswith('T-'):
        l = l.replace('.', '')
        l = l.replace('T+', 'T')
    l = l.replace(',', '.')    
    fo.write(l)

f.close()
fo.close()
