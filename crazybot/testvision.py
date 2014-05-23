import cv2
import numpy as np
import glob
import sys


def do_color(im):
    im2 = cv2.blur(im, (3, 3))
    hsv = cv2.cvtColor(im2, cv2.COLOR_BGR2HSV)
    #mask = cv2.inRange(hsv, np.array([60,40,40], dtype=np.uint8), np.array([75,255,255], dtype=np.uint8))
    #mask1 = cv2.inRange(hsv, np.array([0,135,135], dtype=np.uint8), np.array([15,255,255], dtype=np.uint8))
    #mask2 = cv2.inRange(hsv, np.array([159,135,135], dtype=np.uint8), np.array([179,255,255], dtype=np.uint8))
    mask1 = cv2.inRange(hsv, np.array([0,40,40], dtype=np.uint8), np.array([15,255,255], dtype=np.uint8))
    mask2 = cv2.inRange(hsv, np.array([159,40,40], dtype=np.uint8), np.array([179,255,255], dtype=np.uint8))
    mask = mask1 | mask2
    return mask

files = glob.glob(sys.argv[1])

if len(files) == 1:
    im = cv2.imread(files[0])
    cv2.imshow("orig", im)
    mask = do_color(im)
    cv2.imshow("mask", mask)
    k = cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    for f in files:
        im = cv2.imread(f)
        mask = do_color(im)
        cv2.imwrite(f + "-mask.jpeg", mask)
        
