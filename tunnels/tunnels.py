#!/usr/bin/python

import sys
import os

try:
    ip = sys.argv[1]
except:
    ip = "62.94.168.69"

cmd = "ssh -g "

f = open ('tunnels.txt', 'r')
for l in f:
    cmd += "-L " + l.strip() + " "

f.close()

cmd += "root@%s" % (ip)

os.system(cmd)
