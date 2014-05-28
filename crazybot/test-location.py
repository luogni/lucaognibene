import cv2
import sys
import numpy as np
import time


GW = 12
GH = 12
SIZE = 15
MAXSPEED = 20


def display_grid(grid, out):
    it = np.nditer(grid, flags=['multi_index'])
    mm = np.amax(grid)
    while not it.finished:
        if it[0] > 0:
            cl = (it[0] * 255) / mm
            cv2.circle(out, (it.multi_index[0] * GW + GW / 2,
                             it.multi_index[1] * GH + GH / 2),
                       4, (cl, cl, cl), -1)
        it.iternext()


def addgrid(grid, bx, by, prob=1, size=10, num=10, weight=1):
    d = np.random.multivariate_normal([bx, by], [[size, 0], [0, size]], int(num))
    for p in d:
        try:
            gx = int(p[0]) / GW
            gy = int(p[1]) / GH
            grid[gx][gy] += prob * weight
        except:
            pass


def getcontours(mask):
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # FIXME: pr should not be linked to max area but area similar to cbo expected size (maybe last size)
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
    ret = []
    for c in contours:
        M = cv2.moments(c)
        if M['m00'] == 0:
            continue
        area = cv2.contourArea(c)
        bx, by = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
        ret.append({'bx': bx, 'by': by, 'biggest': area == max_area, 'area': area, 'maxarea': max_area})
    return ret


def getbestpos2(mask, lx, ly, lt):
    ret = getcontours(mask)
    try:
        (bx, by) = [(r['bx'], r['by']) for r in ret if r['biggest']][0]
    except:
        return (lx, ly, time.time())
    n = int(time.time() * 1000)
    # if lx is not None:
    #     speed = np.linalg.norm(np.array([lx, ly]) - np.array([bx, by])) / (n - lt)
    #     print (lx, ly), (bx, by), speed
    return (bx, by, n)
    

def analyze(out, mask, color, grid=None, weight=1):
    ret = getcontours(mask)
    for r in ret:
        if (out is not None)and(r['biggest']):
            cv2.circle(out, (r['bx'], r['by']), 5, color, -1)
        pr = r['area'] / r['maxarea']
        if grid is not None:
            addgrid(grid, r['bx'], r['by'], prob=1, size=SIZE, num=100 * pr, weight=weight)


def getbestpos(grid):
    m = grid.argmax()
    m = np.unravel_index(m, grid.shape)
    lx = m[0] * GW + GW / 2
    ly = m[1] * GH + GH / 2
    return (lx, ly)


cap = cv2.VideoCapture(sys.argv[1])
fgbg = cv2.BackgroundSubtractorMOG()

f = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
avg1 = np.float32(f)
avg2 = np.float32(f)

cv2.namedWindow('prob')
cv2.namedWindow('mask-motion-2')
cv2.namedWindow('mask-color')
cv2.namedWindow('orig')
cv2.namedWindow('mask-position')
cv2.namedWindow('frame')
cv2.moveWindow('mask-color', 100, 100)
cv2.moveWindow('mask-motion-2', 500, 100)
cv2.moveWindow('mask-position', 900, 100)
cv2.moveWindow('orig', 100, 450)
cv2.moveWindow('prob', 500, 450)
cv2.moveWindow('frame', 900, 450)

lx = ly = lt = None
pause = 0

while(1):
    if not pause:
        ret, frame = cap.read()
        orig = frame.copy()
        frame = cv2.blur(frame, (3, 3))
        # fgmask = fgbg.apply(frame)

        # ngw = frame.shape[0] / GW
        # ngh = frame.shape[1] / GH
        # grid = np.zeros([ngw, ngh])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 40, 40], dtype=np.uint8), np.array([15, 255, 255], dtype=np.uint8))
        mask2 = cv2.inRange(hsv, np.array([159, 40, 40], dtype=np.uint8), np.array([179, 255, 255], dtype=np.uint8))
        mask = mask1 | mask2

        cv2.accumulateWeighted(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), avg1, 0.2)
        # cv2.accumulateWeighted(frame, avg2, 0.01)

        res1 = cv2.convertScaleAbs(avg1)
        # res2 = cv2.convertScaleAbs(avg2)
        d = cv2.absdiff(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), res1)
        mask2 = cv2.threshold(d, 20, 255, cv2.THRESH_BINARY)[1]
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        
        mask3 = np.zeros([frame.shape[0], frame.shape[1]], np.uint8)
        if lx is not None:
            cv2.circle(mask3, (lx, ly), (SIZE * 2) / 2, (255, 255, 255), -1)
        else:
            mask3.fill(255)

        masktotal = (mask | mask2) & mask3
        (lx, ly, lt) = getbestpos2(masktotal, lx, ly, lt)
        if lx is not None:
            cv2.circle(frame, (lx, ly), 5, (0, 0, 255), 2)

        # analyze(None, mask, (0, 0, 255), grid, 0.5)
        # display_grid(grid, mask)
        # analyze(None, mask2, (255, 0, 0), grid, 0.1)
        # display_grid(grid, mask2)
        # if lx is not None:
        #     addgrid(grid, lx, ly, prob=1, size=SIZE * 3, num=300, weight=0.4)

        # (lx, ly) = getbestpos(grid)
        # cv2.circle(orig, (lx, ly), 5, (0, 0, 255), -1)
        # display_grid(grid, frame)

        cv2.imshow('mask-position', mask3)
        cv2.imshow('mask-motion-2', mask2)
        cv2.imshow('mask-color', mask)
        cv2.imshow('orig', orig)
        cv2.imshow('prob', masktotal)
        cv2.imshow('frame', frame)
    k = cv2.waitKey(10) & 0xff
    if k == 27:
        break
    elif k == 112:  # p
        pause = 1 - pause
    elif k != 255:
        print k

cap.release()
cv2.destroyAllWindows()
                            
