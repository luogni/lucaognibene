#!/bin/sh

# recv
# gst-launch-0.10 tcpclientsrc host=192.168.1.21 port=1234 ! gdpdepay ! ffdec_h263 ! videoflip method=vertical-flip ! xvimagesink sync=false

WIDTH=352
HEIGHT=288
FPS=15
PORT=1234

gst-launch-0.10 v4l2src ! video/x-raw-yuv,width=$WIDTH,height=$HEIGHT,framerate=\(fraction\)$FPS/1 ! hantro4200enc stream-type=1 profile-and-level=1001 ! video/x-h263,framerate=\(fraction\)$FPS/1 ! tcpserversink protocol=gdp port=$PORT
