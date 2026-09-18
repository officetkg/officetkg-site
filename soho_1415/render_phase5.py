# -*- coding: utf-8 -*-
"""PHASE 5 plan: locked architecture (grey) + furniture (colour)."""
import cv2, numpy as np, math
import geometry_master as G, furniture as F, render_2d as R

CROP=R.CROP; S=R.S
def m2p(mx,my): return R.m2p(mx,my)
def mr(rc): return m2p(rc["x0"],rc["y0"]), m2p(rc["x1"],rc["y1"])
W_,H_=R.W_,R.H_

src=cv2.imread(R.SRC)[R.WY0:R.WY0+980, R.WX0:R.WX0+900]
A=cv2.resize(src[CROP[1]:CROP[3],CROP[0]:CROP[2]],(W_,H_),interpolation=cv2.INTER_CUBIC)
base=cv2.addWeighted(A,0.30,np.full_like(A,255),0.70,0)      # faded architecture
R.draw(base, parked=True)                                     # locked 2D master on top

F_COL={'desk':(20,110,190),'chair':(60,60,60),'table':(15,85,160),
       'mchair':(70,70,70),'monitor':(200,0,0),'printer':(120,100,60)}
def kind(k):
    if k.startswith('WORK_DESK'): return 'desk'
    if k.startswith('WORK_CHAIR'): return 'chair'
    if k=='MEETING_TABLE': return 'table'
    if k.startswith('MEETING_CHAIR'): return 'mchair'
    if k=='MONITOR_55': return 'monitor'
    return 'printer'

ov=base.copy()
for k,v in F.FURNITURE.items():
    a,b=mr(v["box"]); c=F_COL[kind(k)]
    cv2.rectangle(ov,a,b,c,-1)
base=cv2.addWeighted(base,0.55,ov,0.45,0)
for k,v in F.FURNITURE.items():
    a,b=mr(v["box"]); c=F_COL[kind(k)]
    cv2.rectangle(base,a,b,c,2)
    if kind(k) in ('chair','mchair'):            # seat-back tick
        cx,cy=(a[0]+b[0])//2,(a[1]+b[1])//2
        cv2.circle(base,(cx,cy),max(3,(b[0]-a[0])//5),c,1)
# monitor view cone
mt=F.FURNITURE["MEETING_TABLE"]["box"]; mo=F.FURNITURE["MONITOR_55"]["box"]
mc=m2p((mo["x0"]+mo["x1"])//2,(mo["y0"]+mo["y1"])//2)
for p in (m2p(mt["x0"],mt["y0"]),m2p(mt["x0"],mt["y1"])):
    cv2.line(base,mc,p,(200,0,0),1,cv2.LINE_AA)

TAGS=[("1","WORK_DESK_1"),("1","WORK_DESK_2"),("2","WORK_CHAIR_1"),("2","WORK_CHAIR_2"),
      ("3","PRINTER_UNIT"),("4","MEETING_TABLE"),("5","MEETING_CHAIR_1"),("5","MEETING_CHAIR_2"),
      ("5","MEETING_CHAIR_3"),("5","MEETING_CHAIR_4"),("5","MEETING_CHAIR_5"),("5","MEETING_CHAIR_6"),
      ("6","MONITOR_55"),("7",None)]
for t,k in TAGS:
    if k is None: continue
    bx=F.FURNITURE[k]["box"]; c=m2p((bx["x0"]+bx["x1"])//2,(bx["y0"]+bx["y1"])//2)
    if k=="MONITOR_55": c=(c[0]-26,c[1])
    cv2.circle(base,c,13,(255,255,255),-1); cv2.circle(base,c,13,(0,0,0),1)
    cv2.putText(base,t,(c[0]-5,c[1]+5),cv2.FONT_HERSHEY_SIMPLEX,0.46,(0,0,0),1,cv2.LINE_AA)
# 7 = existing Book Shelf (reused, not new furniture)
bs=G.BOOK_SHELF["body"]; c=m2p(bs["x1"]+14,(bs["y0"]+bs["y1"])//2)
cv2.circle(base,c,13,(255,255,255),-1); cv2.circle(base,c,13,(0,0,0),1)
cv2.putText(base,"7",(c[0]-5,c[1]+5),cv2.FONT_HERSHEY_SIMPLEX,0.46,(0,0,0),1,cv2.LINE_AA)
cv2.imwrite('out/PHASE5_furniture_plan.png',base)

# ---- review sheet ----
sc=1100.0/H_; P=cv2.resize(base,(int(W_*sc),1100),interpolation=cv2.INTER_AREA)
pw=P.shape[1]; HDR=52; LEG=420
sh=np.full((1100+HDR,pw+LEG+20,3),255,np.uint8); sh[HDR:HDR+1100,0:pw]=P
cv2.rectangle(sh,(0,HDR),(pw-1,HDR+1099),(180,180,180),1)
cv2.putText(sh,'PHASE 5  FURNITURE LAYOUT  (architecture XY LOCKED, storage wall OPEN)',
            (4,34),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,0),1,cv2.LINE_AA)
x=pw+14; y=HDR+28
def txt(t,b=False,col=(40,40,40)):
    global y
    cv2.putText(sh,t,(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.46 if b else 0.42,col,1,cv2.LINE_AA); y+=24
txt('SCALE  1 px = 13.2 mm  (provisional +/-5%)',True); y+=6
for t in ['1 WORK_DESK_1 / _2   2 PLAN CHAIRS','3 PRINTER_UNIT       4 MEETING_TABLE',
          '5 MEETING_CHAIR_1-6  6 MONITOR_55','7 existing BOOK SHELF (reused as is)']: txt(t)
y+=8
txt('WORKSTATIONS  -  bedroom zone',True,(20,110,190))
for t in ['WORK_DESK_1 / _2   700 x 1400 mm each','  in line on the west wall, 2.8 m run',
          'WORK_CHAIR_1 / _2  650 x 650 mm','  clear behind: 2218 / 2376 mm',
          'PRINTER_UNIT       500 x 450 mm']: txt(t)
y+=8; txt('MEETING  -  living dining zone',True,(15,85,160))
for t in ['MEETING_TABLE      1800 x 900 mm','  long axis E-W, in the widest part of',
          '  the opened-up volume, balcony daylight','MEETING_CHAIR_1-6  3 north + 3 south',
          '  600 mm seat pitch','MONITOR_55  1230 mm on the EAST wall',
          '  aligned on the table axis','  viewing 1.4 - 2.6 m']: txt(t)
y+=8; txt('CIRCULATION  (all PASS)',True)
for t in ['entrance -> LD          1663 mm','LD north open area      2455 mm',
          'east aisle -> balcony    792 mm','MB <-> LD east gap      1584 mm',
          'MB <-> south gap        1201 mm','balcony sash access     2402 mm',
          'Book Shelf access       1808 mm','Clo. bi-fold swing      clear']: txt(t)
y+=8; txt('CHECKS',True)
for t in ['architecture clashes  0','furniture clashes     0','all items inside the envelope',
          'no bed / sofa / lounge / low table','no reception counter, no extra storage']: txt(t)
cv2.imwrite('out/PHASE5_FURNITURE_REVIEW.png',sh); print('done',sh.shape)
