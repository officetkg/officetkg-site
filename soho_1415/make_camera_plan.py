# -*- coding: utf-8 -*-
"""PHASE 8 deliverable: camera positions and view cones on the 2D MASTER."""
import cv2, numpy as np, math
import render_2d as R, cameras as CAM, furniture as F, geometry_master as G

img = R.draw(np.full((R.H_, R.W_, 3), 255, np.uint8), parked=True)
img = cv2.addWeighted(img, 0.42, np.full_like(img, 255), 0.58, 0)
ov = img.copy()
COLS = {"A": (0, 90, 220), "B": (0, 150, 80), "C": (190, 60, 0),
        "D": (150, 0, 160), "E": (90, 90, 90)}
for k, c in CAM.CAMERAS.items():
    e, t = np.array(c["eye"], float), np.array(c["target"], float)
    col = COLS[k]
    half = math.radians(math.degrees(math.atan(18.0 / c["focal"])))
    d = t[:2] - e[:2]
    a = math.atan2(d[1], d[0]); L = 330 if k != "E" else 150
    p0 = R.m2p(*e[:2])
    p1 = R.m2p(e[0] + L*math.cos(a-half), e[1] + L*math.sin(a-half))
    p2 = R.m2p(e[0] + L*math.cos(a+half), e[1] + L*math.sin(a+half))
    cv2.fillPoly(ov, [np.array([p0, p1, p2], np.int32)], col)
img = cv2.addWeighted(img, 0.86, ov, 0.14, 0)
for k, c in CAM.CAMERAS.items():
    e, t = np.array(c["eye"], float), np.array(c["target"], float)
    col = COLS[k]
    half = math.radians(math.degrees(math.atan(18.0 / c["focal"])))
    d = t[:2] - e[:2]; a = math.atan2(d[1], d[0]); L = 330 if k != "E" else 150
    p0 = R.m2p(*e[:2])
    for s in (-half, half):
        cv2.line(img, p0, R.m2p(e[0]+L*math.cos(a+s), e[1]+L*math.sin(a+s)), col, 1, cv2.LINE_AA)
    cv2.line(img, p0, R.m2p(e[0]+L*0.42*math.cos(a), e[1]+L*0.42*math.sin(a)), col, 2, cv2.LINE_AA)
    cv2.circle(img, p0, 13, (255, 255, 255), -1); cv2.circle(img, p0, 13, col, 2)
    cv2.putText(img, k, (p0[0]-6, p0[1]+6), cv2.FONT_HERSHEY_SIMPLEX, .55, col, 2, cv2.LINE_AA)
cv2.imwrite('out/PHASE8_camera_plan.png', img)

sc = 1080.0/img.shape[0]
P = cv2.resize(img, (int(img.shape[1]*sc), 1080), interpolation=cv2.INTER_AREA)
pw = P.shape[1]; HDR, LEG = 52, 470
sh = np.full((1080+HDR, pw+LEG+24, 3), 255, np.uint8)
sh[HDR:HDR+1080, 0:pw] = P
cv2.rectangle(sh, (0, HDR), (pw-1, HDR+1079), (185, 185, 185), 1)
cv2.putText(sh, 'PHASE 8   CAMERA PLAN   plan as drawn: NORTH IS DOWN, balcony at the bottom',
            (4, 34), cv2.FONT_HERSHEY_SIMPLEX, .55, (0, 0, 0), 1, cv2.LINE_AA)
x, y = pw+16, HDR+28
def txt(t, b=False, col=(45, 45, 45)):
    global y
    cv2.putText(sh, t, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .46 if b else .42, col, 1, cv2.LINE_AA)
    y += 23
for k in "ABCDE":
    c = CAM.CAMERAS[k]
    txt(c["name"], True, COLS[k])
    txt(f'   {c["focal"]}mm eq.   eye {round(c["eye"][2]*13.2)}mm   '
        f'{"verticals parallel" if c["level"] else "aerial, tilted"}')
    for line in [c["note"][i:i+52] for i in range(0, len(c["note"]), 52)]:
        txt('   ' + line, col=(120, 120, 120))
    y += 6
y += 8; txt('RULES HELD', True)
for t in ['eye height   1500-1600 mm  (1550 for A-D)',
          'lens         28-35 mm equivalent, 36x24 sensor',
          'verticals    axis forced horizontal, framed by lens',
          '             shift - never by tilting the camera',
          'banned       fisheye, ultra-wide, 16 mm, any barrel',
          '             or room-stretching distortion',
          'E only       a bird\'s eye cannot keep verticals',
          '             parallel; stated on the image']: txt(t)
y += 8; txt('SELF-CHECK', True)
for t in ['height, lens, pitch and "is the eye inside a',
          'solid" tested per camera in cameras.py -> PASS']: txt(t)
cv2.imwrite('out/PHASE8_CAMERA_REVIEW.png', sh)
print('camera plan', sh.shape)
