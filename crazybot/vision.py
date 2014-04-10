import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import cv2
import numpy as np

# python vision.py "filesrc location=/home/luogni/Scaricati/1.avi ! decodebin ! videoscale ! video/x-raw-yuv,width=320,height=240 ! ffmpegcolorspace ! video/x-raw-rgb ! opencv ! ffmpegcolorspace ! xvimagesink"

class OpenCV(gst.Element):
    __gstdetails__ = ('CrazyOpenCV', 'Transform',
                      'OpenCV chain element', 'Luca Ognibene')

    _sinkpadtemplate = gst.PadTemplate("sink",
                                       gst.PAD_SINK,
                                       gst.PAD_ALWAYS,
                                       gst.caps_new_any())
    _srcpadtemplate = gst.PadTemplate("src",
                                      gst.PAD_SRC,
                                      gst.PAD_ALWAYS,
                                      gst.caps_new_any())

    def __init__(self):
        gst.Element.__init__(self)

        self.sinkpad = gst.Pad(self._sinkpadtemplate, "sink")
        self.sinkpad.set_chain_function(self.chainfunc)
        self.add_pad(self.sinkpad)

        self.srcpad = gst.Pad(self._srcpadtemplate, "src")
        self.add_pad(self.srcpad)
        self.refframe_stream = False
        self.refframe_vision = False
        self.poly = np.array([[[280, 280], [380, 300], [380, 470], [100, 470]]])

        self.targetx = 0
        self.targety = 0
        self.tx = 0
        self.ty = 0
        self.tspeed = 50
        self.lasttimestamp = 0

    def test_move_bot(self, ts):
        if (self.lasttimestamp == 0):
            self.lasttimestamp = ts
            return
        dts = float(ts - self.lasttimestamp) / gst.SECOND
        self.lasttimestamp = ts
        mx = my = int(dts * self.tspeed)
        if self.targetx < self.tx:
            mx *= -1
        if self.targety < self.ty:
            my *= -1
        self.tx += mx
        self.ty += my

    def next_target(self):
        self.passgrid[self.tx / self.gw][self.ty / self.gh] += 1
        m = self.passgrid.argmin()
        m = np.unravel_index(m, self.passgrid.shape)
        self.targetx = m[0] * self.gw + self.gw/2
        self.targety = m[1] * self.gh + self.gh/2
        print m[0], m[1], self.targetx

    def find_bot(self, frame):
        frame2 = cv2.blur(frame,(3,3))
        hsv = cv2.cvtColor(frame2, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, np.array([60,40,40], dtype=np.uint8), np.array([75,255,255], dtype=np.uint8))
        # find contours in the threshold image
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # finding contour with maximum area and store it as best_cnt
        max_area = 0
        best_cnt = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                best_cnt = cnt
        if self.refframe_vision is False:
            self.dorefframe_vision(frame)
            self.refframe_vision = True
        if best_cnt is not None:
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            #cv2.circle(frame, (cx,cy), 5, 255, -1)
            #print self.distance[cx][cy]
        cv2.circle(frame, (self.tx, self.ty), 2, (255, 0, 0), -1)
        cv2.circle(frame, (self.targetx, self.targety), 2, (0, 255, 0), -1)
        cv2.polylines(frame, self.poly, True, [0, 255, 0])
        return frame

    def dorefframe_stream(self, buffer):
        c = buffer.get_caps()
        self.w = c[0]['width']
        self.h = c[0]['height']

    def dorefframe_vision(self, frame):
        self.gw = 20
        self.gh = 20
        self.ngw = self.w / self.gw
        self.ngh = self.h / self.gh
        self.distance = np.empty([self.w, self.h])
        self.distgrid = np.zeros([self.ngw, self.ngh])
        self.passgrid = np.zeros([self.ngw, self.ngh])
        for x in range(0, self.w):
            for y in range(0, self.h):
                gx = x / self.gw
                gy = y / self.gh
                dist = cv2.pointPolygonTest(self.poly, (x, y), True)
                self.distance[x][y] = dist
                if dist > 0:
                    self.distgrid[gx][gy] += dist
                else:
                    self.distgrid[gx][gy] = -1  # grid with border or outside
                    self.passgrid[gx][gy] = np.inf
                #cv2.line(frame, (x, y), (x, y), c)
        
    def chainfunc(self, pad, buffer):
        if self.refframe_stream is False:
            self.dorefframe_stream(buffer)
            self.refframe_stream = True
        self.test_move_bot(buffer.timestamp)
        img = np.frombuffer(buffer.data, dtype=np.uint8)
        img = img.reshape((self.h, self.w, 3))
        img = self.find_bot(img)
        self.next_target()
        b2 = gst.Buffer(img.tostring())
        b2.set_caps(buffer.get_caps())
        b2.timestamp = buffer.timestamp
        return self.srcpad.push(b2)

gobject.type_register(OpenCV)
gst.element_register(OpenCV, "opencv", gst.RANK_MARGINAL)


if __name__ == '__main__':
    import sys
    print "Use --gst-debug=python:3 to see output from this example"
    #bin = gst.parse_launch("videotestsrc ! video/x-raw-rgb,width=320,height=240,framerate=5/1 ! opencv ! ffmpegcolorspace ! xvimagesink")
    bin = gst.parse_launch(sys.argv[1])

    def bus_event(bus, message):
        # print message.type
        t = message.type
        if t == gst.MESSAGE_EOS:
            mainloop.quit()
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            mainloop.quit()
        elif t == gst.MESSAGE_TAG:
            tl = message.parse_tag()
            #for k in tl.keys():
            #    print(k, tl[k])
        return True
        
    bin.get_bus().add_watch(bus_event)        
    bin.set_state(gst.STATE_PLAYING)        
    mainloop = gobject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass
    bin.set_state(gst.STATE_NULL)
        
