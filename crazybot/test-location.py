import cv2
import sys

cap = cv2.VideoCapture(sys.argv[1])
fgbg = cv2.BackgroundSubtractorMOG()

while(1):
    ret, frame = cap.read()
    frame = cv2.blur(frame, (3, 3))
    fgmask = fgbg.apply(frame)
    
    cv2.imshow('frame', fgmask)
    cv2.imshow('frame2', frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
                            
