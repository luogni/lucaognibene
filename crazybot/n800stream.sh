#!/bin/sh

# recv
# gst-launch-0.10 tcpclientsrc host=192.168.1.21 port=1234 ! gdpdepay ! ffdec_h263 ! videoflip method=vertical-flip ! xvimagesink sync=false

WIDTH=352
HEIGHT=288
FPS=15
PORT=1234

#while bin/true; do gst-launch-0.10 v4l2src ! video/x-raw-yuv,width=$WIDTH,height=$HEIGHT,framerate=\(fraction\)$FPS/1 ! hantro4200enc stream-type=1 profile-and-level=1007 bit-rate=515 ! video/x-h263,framerate=\(fraction\)$FPS/1 ! tcpserversink protocol=gdp port=$PORT; done
while bin/true; do gst-launch-0.10 gconfv4l2src ! video/x-raw-yuv,width=$WIDTH,height=$HEIGHT,framerate=\(fraction\)$FPS/1 ! hantro4200enc stream-type=1 profile-and-level=245 bit-rate=515 ! video/mpeg,framerate=\(fraction\)$FPS/1 ! tcpserversink protocol=gdp port=$PORT; done
