# -*- coding: utf-8 -*-
"""PHASE 4 numeric verification: distance from every traced line to the nearest
printed ink pixel in the (uncorrected) source plan."""
import cv2, numpy as np, math
import geometry_master as G

SRC='/root/.claude/uploads/2a8afc20-6962-5ef7-92b1-d963390abca8/51014ede-image.png'
g=cv2.cvtColor(cv2.imread(SRC),cv2.COLOR_BGR2GRAY)[120:1100,240:1140]
ink=(g<175).astype(np.uint8)
# distance (in px) from any pixel to the nearest ink pixel
DT=cv2.distanceTransform(1-ink, cv2.DIST_L2, 5)
OX,OY=G.OX,G.OY
H,W=DT.shape

def d(mx,my):
    x,y=int(round(mx+OX)),int(round(my+OY))
    if 0<=x<W and 0<=y<H: return float(DT[y,x])
    return float('nan')

def sample(p,q,n=None):
    n = n or max(4,int(math.hypot(q[0]-p[0],q[1]-p[1])))
    return [d(p[0]+(q[0]-p[0])*i/n, p[1]+(q[1]-p[1])*i/n) for i in range(n+1)]

def report(name, vals):
    v=np.array([x for x in vals if not math.isnan(x)])
    if not len(v): return None
    return (name, v.mean(), np.percentile(v,95), v.max())

rows=[]
def seg(name,p,q): rows.append(report(name,sample(p,q)))
def box(name,r):
    a=(r["x0"],r["y0"]); b=(r["x1"],r["y0"]); c=(r["x1"],r["y1"]); e=(r["x0"],r["y1"])
    rows.append(report(name, sample(a,b)+sample(b,c)+sample(c,e)+sample(e,a)))

ow=G.OUTER_WALLS
pts=ow["envelope_outline"]
rows.append(report("OUTER_WALLS.envelope_outline",
    sum([sample(pts[i],pts[i+1]) for i in range(len(pts)-1)],[])))
for s in ow["north"]["segments"]: seg("OUTER.north.inner",(s["x0"],s["inner_y"]),(s["x1"],s["inner_y"]))
for s in ow["west"]["segments"]:  seg("OUTER.west.inner",(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]))
for s in ow["east"]["segments"]:  seg("OUTER.east.inner",(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]))
box("OUTER.south.solid_band", ow["south"]["solid_segment"])
for k,r in G.COLUMNS.items(): box("COLUMN."+k, r)
for k,r in G.PS.items():
    if isinstance(r,dict) and "y0" in r: box("PS."+k, r)
for k,r in G.INNER_WALLS.items(): box("INNER."+k, r)
for tag,run in (("EAST",G.STORAGE_WALL["run_EAST"]),("SOUTH",G.STORAGE_WALL["run_SOUTH"])):
    box(f"STORAGE.{tag}.pocket", run["pocket"])
    for i,r in enumerate(run["panels_closed"]): box(f"STORAGE.{tag}.panel{i+1}_closed", r)
for nm,r in (("SC",G.SC),("SHOWER",G.SHOWER),("WD",G.WD),("VANITY",G.VANITY),
             ("VANITY_BOWL",G.VANITY_BOWL),("REFRIGERATOR",G.REFRIGERATOR),
             ("ENTRANCE_NICHE",G.ENTRANCE_NICHE_UNIDENTIFIED),
             ("BOOK_SHELF",G.BOOK_SHELF["body"])): box(nm,r)
for k,r in G.CLOSETS.items(): box("CLO."+k,r)
for k,r in G.TOILET.items():
    if isinstance(r,dict) and "y0" in r: box("TOILET."+k,r)
for k,r in G.KITCHEN.items():
    if isinstance(r,dict) and "y0" in r and k!="room_ref": box("KITCHEN."+k,r)
box("WINDOW.balcony_opening", G.WINDOWS["W_BALCONY"]["opening"])
for k,dd in G.DOORS.items():
    if "hinge" in dd:
        h,t,c=dd["hinge"],dd["open_leaf_to"],dd["closed_leaf_to"]
        a0=math.atan2(t[1]-h[1],t[0]-h[0]); a1=math.atan2(c[1]-h[1],c[0]-h[0])
        dl=(a1-a0)%(2*math.pi)
        if dl>math.pi: a0,dl=a1,2*math.pi-dl
        arc=[d(h[0]+dd["leaf"]*math.cos(a0+dl*i/40), h[1]+dd["leaf"]*math.sin(a0+dl*i/40)) for i in range(41)]
        rows.append(report("DOOR."+k+".arc",arc))
        rows.append(report("DOOR."+k+".leaf",sample(h,t)))
b=G.BALCONY
seg("BALCONY.north_edge",(b["north_edge_x"][0],b["north_edge_y"]),(b["north_edge_x"][1],b["north_edge_y"]))
seg("BALCONY.side_west.stub",*b["side_west"]["vertical_stub"])
seg("BALCONY.side_west.raked",*b["side_west"]["raked"])
seg("BALCONY.side_east.raked",*b["side_east"]["raked"])
box("BALCONY.railing", b["railing"])

rows=[r for r in rows if r]
CURVED={"TOILET.bowl","TOILET.hand_basin","KITCHEN.sink_bowl","VANITY_BOWL"}
rows=[(n+"  [bbox of a curved symbol]" if n in CURVED else n,m,p,x) for n,m,p,x in rows]
rows.sort(key=lambda r:-r[2])
print(f'{"element":42s} {"mean":>6s} {"p95":>6s} {"max":>6s}')
print('-'*66)
for n,m,p,x in rows: print(f'{n:42s} {m:6.2f} {p:6.2f} {x:6.2f}')
allv=np.array([r[1] for r in rows])
print('-'*66)
print(f'elements: {len(rows)}   mean-of-means {allv.mean():.2f}px   worst p95 {max(r[2] for r in rows):.2f}px')
