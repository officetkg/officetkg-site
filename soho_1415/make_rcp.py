# -*- coding: utf-8 -*-
"""PHASE 9 deliverable: reflected ceiling plan - coffer + downlights, photo-derived."""
import cv2, numpy as np
import render_2d as R, lighting as LT

img = R.draw(np.full((R.H_, R.W_, 3), 255, np.uint8), parked=True)
img = cv2.addWeighted(img, 0.38, np.full_like(img, 255), 0.62, 0)
Z, bw = LT.ZONE, LT.COFFER_BAND
ov = img.copy()
cv2.rectangle(ov, R.m2p(Z["x0"], Z["y0"]), R.m2p(Z["x1"], Z["y1"]), (150, 205, 235), -1)
cv2.rectangle(ov, R.m2p(Z["x0"]+bw, Z["y0"]+bw), R.m2p(Z["x1"]-bw, Z["y1"]-bw),
              (255, 255, 255), -1)
img = cv2.addWeighted(img, 0.72, ov, 0.28, 0)
cv2.rectangle(img, R.m2p(Z["x0"], Z["y0"]), R.m2p(Z["x1"], Z["y1"]), (150, 120, 40), 2)
cv2.rectangle(img, R.m2p(Z["x0"]+bw, Z["y0"]+bw), R.m2p(Z["x1"]-bw, Z["y1"]-bw),
              (150, 120, 40), 1)
for lx, ly, kind in LT.luminaires():
    p = R.m2p(lx, ly); col = (30, 110, 200) if kind == "living" else (120, 120, 120)
    cv2.circle(img, p, 7, (255, 255, 255), -1)
    cv2.circle(img, p, 7, col, 2)
    cv2.line(img, (p[0]-3, p[1]), (p[0]+3, p[1]), col, 1)
cv2.imwrite('out/PHASE9_reflected_ceiling_plan.png', img)

sc = 1080.0/img.shape[0]
P = cv2.resize(img, (int(img.shape[1]*sc), 1080), interpolation=cv2.INTER_AREA)
pw = P.shape[1]; HDR, LEG = 52, 470
sh = np.full((1080+HDR, pw+LEG+24, 3), 255, np.uint8); sh[HDR:HDR+1080, 0:pw] = P
cv2.rectangle(sh, (0, HDR), (pw-1, HDR+1079), (185, 185, 185), 1)
cv2.putText(sh, 'PHASE 9   REFLECTED CEILING PLAN   photo-derived, PROVISIONAL',
            (4, 34), cv2.FONT_HERSHEY_SIMPLEX, .55, (0, 0, 0), 1, cv2.LINE_AA)
x, y = pw+16, HDR+28
def txt(t, b=False, c=(45, 45, 45)):
    global y; cv2.putText(sh, t, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .46 if b else .42, c, 1, cv2.LINE_AA); y += 23
L = LT.luminaires()
txt('WHAT THE PHOTOS SHOW', True)
for t in ['coffered ceiling: raised centre panel with a',
          'DROPPED PERIMETER BAND round the living zone',
          'small recessed downlights set in that band,',
          'placed in PAIRS',
          'more downlights in kitchen and inner hall',
          'no pendants, no cove uplighting, no',
          'decorative fittings',
          'a recessed air-con unit near the window head']: txt(t)
y += 8; txt('AS MODELLED', True)
for t in [f'band      {LT.COFFER_BAND*13.2:.0f} mm wide, dropped {LT.COFFER_DROP*13.2:.0f} mm',
          f'aperture  {LT.DL_DIA*13.2:.0f} mm',
          f'pair gap  {LT.DL_PAIR_GAP*13.2:.0f} mm',
          f'pair pitch {LT.DL_PITCH*13.2:.0f} mm',
          f'count     {len(L)}  ({sum(1 for l in L if l[2]=="living")} living, '
          f'{sum(1 for l in L if l[2]=="service")} service)']: txt(t)
y += 8; txt('STATUS', True, (170, 70, 0))
for t in ['The sheet has NO reflected ceiling plan, so',
          'every position here comes from the photos.',
          'It is PROVISIONAL and lives in lighting.py,',
          'deliberately outside geometry_master.py.',
          'The approved architectural XY is untouched.']: txt(t, c=(170, 70, 0))
y += 8; txt('DAYLIGHT STAYS PRIMARY', True)
for t in ['balcony faces NORTH - no direct sun, ever.',
          'The downlights are a secondary layer; the',
          'north window carries the rooms.']: txt(t)
cv2.imwrite('out/PHASE9_LIGHTING_REVIEW.png', sh); print('rcp', sh.shape)
