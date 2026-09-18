# -*- coding: utf-8 -*-
"""PHASE 4 deliverable: A | B | C review sheet."""
import cv2, numpy as np
import render_2d as R, geometry_master as G

A  = cv2.imread('out/A_source_plan.png')
B  = cv2.imread('out/B_vector_trace_OPEN.png')
C  = cv2.imread('out/C_overlay_OPEN.png')
h,w = A.shape[:2]
sc  = 1000.0/h
def rs(im): return cv2.resize(im,(int(w*sc),1000),interpolation=cv2.INTER_AREA)
A,B,C = rs(A),rs(B),rs(C)
pw = A.shape[1]
HDR, LEG = 54, 250
sheet = np.full((1000+HDR, pw*3+LEG+40, 3), 255, np.uint8)
for i,(im,t) in enumerate(((A,'A  SOURCE PLAN  (PHASE 2: no correction applied)'),
                           (B,'B  VECTOR 2D TRACE  (storage wall = OPEN / PARKED)'),
                           (C,'C  OVERLAY  A + B'))):
    x=i*(pw+10)
    sheet[HDR:HDR+1000, x:x+pw]=im
    cv2.putText(sheet,t,(x+4,34),cv2.FONT_HERSHEY_SIMPLEX,0.52,(0,0,0),1,cv2.LINE_AA)
    cv2.rectangle(sheet,(x,HDR),(x+pw-1,HDR+999),(180,180,180),1)
lx=3*(pw+10)+6
items=[('OUTER_WALLS / envelope',R.COL['outer']),('COLUMNS (C_NE, C_SE)',R.COL['column']),
       ('PS (pipe shaft)',R.COL['ps']),('INNER_WALLS',R.COL['inner']),
       ('STORAGE_WALL rail + pocket',R.COL['storage']),('STORAGE_WALL panels (parked)',R.COL['park']),
       ('Casework / fixtures',R.COL['case']),('DOORS (hinge, leaf, swing)',R.COL['door']),
       ('WINDOW (balcony sash)',R.COL['win']),('BALCONY + railing',R.COL['bal'])]
cv2.putText(sheet,'LEGEND',(lx,34),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,0),1,cv2.LINE_AA)
y=HDR+26
for t,c in items:
    cv2.rectangle(sheet,(lx,y-11),(lx+26,y+3),c,-1)
    cv2.putText(sheet,t,(lx+34,y),cv2.FONT_HERSHEY_SIMPLEX,0.43,(40,40,40),1,cv2.LINE_AA)
    y+=30
y+=16
for t in ['MASTER COORDINATES', 'origin = NW corner of the', 'building outline (exterior faces)',
          'X right / Y down,  unit = source px', 'NO mm conversion (per instruction)','',
          'OVERLAY RESIDUAL', '73 traced elements', 'mean-of-means 0.54 px', 'worst p95   3.0 px',
          '(excluding 3 curved symbols', ' recorded as bounding boxes)','',
          'BALCONY', 'both side partitions parallel', 'west 19.43 deg / east 19.60 deg', 
          'from vertical -> PARALLELOGRAM', 'residual sd 0.31 px']:
    cv2.putText(sheet,t,(lx,y),cv2.FONT_HERSHEY_SIMPLEX,0.42,(40,40,40),1,cv2.LINE_AA); y+=23
cv2.imwrite('out/PHASE4_2D_GEOMETRY_REVIEW.png',sheet)
print('sheet', sheet.shape)
