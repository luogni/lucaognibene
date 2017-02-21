# import numpy as np
import cv2
import sys

cap = cv2.VideoCapture(sys.argv[1])

fgbg = cv2.BackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()
    if not frame:
        break
    print type(frame), frame.shape
    fgmask = fgbg.apply(frame)
    cv2.imshow('frame', fgmask)
    contours, _ = cv2.findContours(fgmask, cv2.RETR_LIST,
                                   cv2.CHAIN_APPROX_SIMPLE)
    print contours
    for c in contours:
        rect = cv2.boundingRect(c)
        if rect[2] < 5 or rect[3] < 5:
            continue
        print cv2.contourArea(c)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
