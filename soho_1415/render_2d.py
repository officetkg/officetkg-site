# -*- coding: utf-8 -*-
"""PHASE 3/4 renderer: vector 2D trace (B) + overlay on the source plan (C)."""
import cv2, numpy as np, os, math
import geometry_master as G

SRC = '/root/.claude/uploads/2a8afc20-6962-5ef7-92b1-d963390abca8/51014ede-image.png'
WX0, WY0 = G.SRC_WINDOW              # source -> work
OX, OY   = G.OX, G.OY                # work   -> master
CROP = (390, 110, 815, 960)          # work-coord crop for all outputs
S = 3                                # display scale

def w2p(wx, wy):  return (int(round((wx-CROP[0])*S)), int(round((wy-CROP[1])*S)))
def m2p(mx, my):  return w2p(mx+OX, my+OY)
def mr2p(r):      return m2p(r["x0"], r["y0"]), m2p(r["x1"], r["y1"])

W_, H_ = (CROP[2]-CROP[0])*S, (CROP[3]-CROP[1])*S

COL = dict(
    outer=(0,0,220), inner=(0,120,220), column=(160,0,200), ps=(120,120,120),
    storage=(0,160,0), park=(0,200,0), case=(0,140,190), door=(200,60,0),
    win=(220,0,180), bal=(0,90,255), room=(200,200,200))

def lay(bg=None):
    return np.full((H_,W_,3),255,np.uint8) if bg is None else bg.copy()

def rct(img, r, c, t=1):
    a,b = mr2p(r); cv2.rectangle(img,a,b,c,t)

def ln(img, p, q, c, t=1):
    cv2.line(img, m2p(*p), m2p(*q), c, t, cv2.LINE_AA)

def poly(img, pts, c, t=2, closed=True):
    P=np.array([m2p(*p) for p in pts],np.int32)
    cv2.polylines(img,[P],closed,c,t,cv2.LINE_AA)

def arc(img, hinge, r, a0, a1, c, t=1):
    cx,cy = m2p(*hinge)
    cv2.ellipse(img,(cx,cy),(int(r*S),int(r*S)),0,a0,a1,c,t,cv2.LINE_AA)

def draw(img, parked=True):
    # ---- envelope ----
    poly(img, G.OUTER_WALLS["envelope_outline"], COL['outer'], 2)
    ow=G.OUTER_WALLS
    for s in ow["north"]["segments"]:
        ln(img,(s["x0"],s["inner_y"]),(s["x1"],s["inner_y"]),COL['outer'],1)
    for s in ow["west"]["segments"]:
        ln(img,(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]),COL['outer'],1)
    for s in ow["east"]["segments"]:
        ln(img,(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]),COL['outer'],1)
    rct(img, ow["south"]["solid_segment"], COL['outer'],1)
    # ---- columns ----
    for k,r in G.COLUMNS.items(): rct(img,r,COL['column'],2)
    # ---- PS ----
    for k,r in G.PS.items():
        if k.startswith(('interior','wall')): rct(img,r,COL['ps'],1)
    p=G.PS["access_panel_north"]; ln(img,(p["x0"],p["y"]),(p["x1"],p["y"]),COL['ps'],2)
    # ---- inner walls ----
    for k,r in G.INNER_WALLS.items(): rct(img,r,COL['inner'],1)
    # ---- casework / fixtures ----
    for r in (G.SC,G.SHOWER,G.WD,G.VANITY,G.VANITY_BOWL,
              G.ENTRANCE_NICHE_UNIDENTIFIED,G.REFRIGERATOR):
        rct(img,r,COL['case'],1)
    for r in G.CLOSETS.values(): rct(img,r,COL['case'],1)
    for k,r in G.TOILET.items():
        if isinstance(r,dict): rct(img,r,COL["case"],1)
    for k,r in G.KITCHEN.items():
        if isinstance(r,dict): rct(img,r,COL["case"],1)
    rct(img,G.BOOK_SHELF["body"],COL['case'],2)
    bs=G.BOOK_SHELF["body"]
    for y in G.BOOK_SHELF["shelf_lines_y"]:
        ln(img,(bs["x0"],y),(bs["x1"],y),COL['case'],1)
    # ---- storage wall ----
    for run in (G.STORAGE_WALL["run_EAST"], G.STORAGE_WALL["run_SOUTH"]):
        rct(img,run["pocket"],COL['storage'],2)
        for r in (run["panels_parked"] if parked else run["panels_closed"]):
            rct(img,r,COL['park'],-1)
        rl=run["rail_line"]
        if run["axis"]=="vertical": ln(img,(rl["x"],rl["y0"]),(rl["x"],rl["y1"]),COL['storage'],1)
        else:                       ln(img,(rl["x0"],rl["y"]),(rl["x1"],rl["y"]),COL['storage'],1)
    # ---- windows ----
    wb=G.WINDOWS["W_BALCONY"]; rct(img,wb["opening"],COL['win'],2)
    ln(img,(wb["mullion_x"],wb["opening"]["y0"]),(wb["mullion_x"],wb["opening"]["y1"]),COL['win'],2)
    # ---- doors ----
    for k,d in G.DOORS.items():
        o=d["opening"]
        if "hinge" not in d:
            if "x0" in o: ln(img,(o["x0"],o["y"]),(o["x1"],o["y"]),COL['door'],2)
            else:         ln(img,(o["x"],o["y0"]),(o["x"],o["y1"]),COL['door'],2)
            continue
        h=d["hinge"]; t=d["open_leaf_to"]; c=d["closed_leaf_to"]
        ln(img,h,t,COL['door'],2)
        ln(img,h,c,COL['door'],1)
        a0=math.degrees(math.atan2(t[1]-h[1],t[0]-h[0]))
        a1=math.degrees(math.atan2(c[1]-h[1],c[0]-h[0]))
        dlt=(a1-a0)%360
        if dlt>180: a0,dlt = a1,360-dlt
        arc(img,h,d["leaf"],a0,a0+dlt,COL['door'],1)
    # ---- balcony ----
    b=G.BALCONY
    ln(img,(b["north_edge_x"][0],b["north_edge_y"]),(b["north_edge_x"][1],b["north_edge_y"]),COL['bal'],2)
    ln(img,*b["side_west"]["vertical_stub"],c=COL['bal'],t=2) if False else \
        ln(img,b["side_west"]["vertical_stub"][0],b["side_west"]["vertical_stub"][1],COL['bal'],2)
    ln(img,b["side_west"]["raked"][0],b["side_west"]["raked"][1],COL['bal'],2)
    ln(img,b["side_east"]["raked"][0],b["side_east"]["raked"][1],COL['bal'],2)
    rct(img,b["railing"],COL['bal'],2)
    for y in b["railing_inner_lines_y"]:
        ln(img,(b["railing"]["x0"],y),(b["railing"]["x1"],y),COL['bal'],1)
    return img

if __name__ == "__main__":
    os.makedirs('out',exist_ok=True)
    src=cv2.imread(SRC)
    work=src[WY0:WY0+980, WX0:WX0+900]
    A=work[CROP[1]:CROP[3], CROP[0]:CROP[2]]
    A=cv2.resize(A,(W_,H_),interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('out/A_source_plan.png',A)
    B=draw(lay(),parked=True);              cv2.imwrite('out/B_vector_trace_OPEN.png',B)
    Bc=draw(lay(),parked=False);            cv2.imwrite('out/B_vector_trace_asdrawn.png',Bc)
    for tag,V in (('OPEN',B),('asdrawn',Bc)):
        mask=(V<250).any(2)
        C=A.copy(); C=cv2.addWeighted(C,0.55,np.full_like(C,255),0.45,0)
        C[mask]=V[mask]
        cv2.imwrite(f'out/C_overlay_{tag}.png',C)
    print('rendered', A.shape)
