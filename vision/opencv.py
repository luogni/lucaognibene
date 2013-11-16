import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import cv2
import numpy as np

# python opencv.py "filesrc location=/home/luogni/Scaricati/1.avi ! decodebin ! videoscale ! video/x-raw-yuv,width=320,height=240 ! ffmpegcolorspace ! video/x-raw-rgb ! opencv ! ffmpegcolorspace ! xvimagesink"

class OpenCV(gst.Element):
    __gstdetails__ = ('AyOpenCV', 'Transform',
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

        self.face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')

        self.fgbg = cv2.BackgroundSubtractorMOG()

    def face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        print faces
        # for (x,y,w,h) in faces:
        #     cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        #     roi_gray = gray[y:y+h, x:x+w]
        #     roi_color = img[y:y+h, x:x+w]
        #     eyes = eye_cascade.detectMultiScale(roi_gray)
        #     for (ex,ey,ew,eh) in eyes:
        #         cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        return img

    def bkg(self, img):
        fgmask = self.fgbg.apply(img)
        return cv2.cvtColor(fgmask, cv2.COLOR_GRAY2RGB)

    def chainfunc(self, pad, buffer):
        c = buffer.get_caps()
        w = c[0]['width']
        h = c[0]['height']
        img = np.frombuffer(buffer.data, dtype=np.uint8)
        img = img.reshape((w, h, 3))
        #img = self.face(img)
        img = self.bkg(img)
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
        
