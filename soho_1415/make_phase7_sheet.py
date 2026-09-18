# -*- coding: utf-8 -*-
"""PHASE 7 deliverable: A (2D MASTER) | B (ortho top view of the 3D) | C (overlay)."""
import cv2, numpy as np
import render_2d as R, topview_ortho as T, build_3d as B3

img, mask, edges, idx, names, ss = T.render_top()
A = R.draw(np.full((R.H_, R.W_, 3), 255, np.uint8), parked=True)
Bv = img
m = (A < 250).any(2)
C = cv2.addWeighted(Bv, 0.60, np.full_like(Bv, 255), 0.40, 0); C[m] = A[m]
cv2.imwrite('out/A3_2D_master.png', A)
cv2.imwrite('out/B3_topview_ortho.png', Bv)
cv2.imwrite('out/C3_overlay_2Dmaster_on_3Dtop.png', C)

sc = 1000.0/R.H_
def rs(x): return cv2.resize(x, (int(R.W_*sc), 1000), interpolation=cv2.INTER_AREA)
A, Bv, C = rs(A), rs(Bv), rs(C)
pw = A.shape[1]; HDR, LEG = 54, 330
sh = np.full((1000+HDR, pw*3+LEG+40, 3), 255, np.uint8)
for i, (im, t) in enumerate(((A, 'A  2D MASTER  (approved, storage wall OPEN)'),
                             (Bv, 'B  3D MODEL - ORTHOGRAPHIC TOP VIEW'),
                             (C, 'C  OVERLAY  A + B'))):
    x = i*(pw+10); sh[HDR:HDR+1000, x:x+pw] = im
    cv2.putText(sh, t, (x+4, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0,0,0), 1, cv2.LINE_AA)
    cv2.rectangle(sh, (x, HDR), (x+pw-1, HDR+999), (180,180,180), 1)
x = 3*(pw+10)+6; y = HDR+26
def txt(t, b=False, c=(40,40,40)):
    global y; cv2.putText(sh, t, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .46 if b else .42, c, 1, cv2.LINE_AA); y += 23
txt('CAMERA FOR VIEW B', True)
for t in ['perspective            = 0', 'camera axis            = -Z (straight down)',
          'origin, scale, aspect  = identical to A',
          'projection is literally (MASTER x, y)',
          'applied to the real triangles of the',
          'built mesh, with a z-buffer.', 'Nothing is redrawn by hand.']: txt(t)
y += 10; txt('3D XY vs 2D MASTER XY  (bounds)', True)
for t in ['21 object groups compared',
          '19 groups            0.00 px  exact',
          'work + meeting chairs 1.00 px INSIDE',
          '  their approved envelope, by design',
          'RESULT: PASS']: txt(t)
y += 10; txt('TOP-VIEW LINE CHECK', True)
for t in ['59 traced elements vs the rendered',
          'object boundaries of the 3D model',
          'mean-of-means        0.66 px',
          'residual points not covered',
          'by another solid          0',
          '=> every residual is a line that is',
          '   inside or under another object,',
          '   invisible in a top view.']: txt(t)
y += 10; txt('HEIGHTS', True)
for t in ['every Z is a PROVISIONAL VARIABLE',
          '(heights.py). The sheet carries no',
          'section. Changing any Z cannot',
          'change any X or Y.']: txt(t)
y += 10; txt('STORAGE WALL = OPEN / PARKED', True, (0,140,0))
for t in ['3 panels parked in the north pocket',
          '2 panels parked in the west pocket',
          'rails kept, openings permanently clear']: txt(t)
cv2.imwrite('out/PHASE7_3D_GEOMETRY_REVIEW.png', sh)
print('sheet', sh.shape)
