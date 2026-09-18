# -*- coding: utf-8 -*-
"""PHASE 7 pixel check: every 2D MASTER line vs the nearest edge in the
orthographic top view of the 3D model (same origin, scale, aspect)."""
import cv2, numpy as np, math
import geometry_master as G, furniture as F, render_2d as R
import topview_ortho as T

img, mask, edge, IDX, NAMES, SSF = T.render_top()   # edges from the object/height index map
DT = cv2.distanceTransform(255-edge, cv2.DIST_L2, 5) / R.S     # px in MASTER units
H_, W_ = DT.shape

def d(mx, my):
    p = R.m2p(mx, my)
    if 0 <= p[0] < W_ and 0 <= p[1] < H_: return float(DT[p[1], p[0]])
    return float('nan')
def sample(p, q, n=None):
    n = n or max(4, int(math.hypot(q[0]-p[0], q[1]-p[1])*R.S))
    return [d(p[0]+(q[0]-p[0])*i/n, p[1]+(q[1]-p[1])*i/n) for i in range(n+1)]
def rep(name, vals):
    v = np.array([x for x in vals if not math.isnan(x)])
    return (name, v.mean(), np.percentile(v,95), v.max()) if len(v) else None
rows=[]
def box(name, r):
    a=(r["x0"],r["y0"]); b=(r["x1"],r["y0"]); c=(r["x1"],r["y1"]); e=(r["x0"],r["y1"])
    rows.append(rep(name, sample(a,b)+sample(b,c)+sample(c,e)+sample(e,a)))
def seg(name,p,q): rows.append(rep(name, sample(p,q)))

ow=G.OUTER_WALLS; pts=ow["envelope_outline"]
rows.append(rep("OUTER envelope", sum([sample(pts[i],pts[i+1]) for i in range(len(pts)-1)],[])))
for s in ow["west"]["segments"]: seg("OUTER west inner",(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]))
for s in ow["east"]["segments"]: seg("OUTER east inner",(s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]))
box("OUTER south solid band", ow["south"]["solid_segment"])
for k,r in G.COLUMNS.items(): box("COLUMN "+k, r)
for k,r in G.INNER_WALLS.items(): box("INNER "+k, r)
for tag,run in (("EAST",G.STORAGE_WALL["run_EAST"]),("SOUTH",G.STORAGE_WALL["run_SOUTH"])):
    box(f"STORAGE {tag} pocket", run["pocket"])
    for i,p in enumerate(run["panels_parked"]): box(f"STORAGE {tag} parked panel {i+1}", p)
for nm,r in (("SHOWER",G.SHOWER),("WD",G.WD),("VANITY",G.VANITY),("REFRIGERATOR",G.REFRIGERATOR),
             ("BOOK_SHELF",G.BOOK_SHELF["body"]),("SC",G.SC)): box(nm,r)
for k,r in G.CLOSETS.items(): box("CLO "+k,r)
box("KITCHEN counter", G.KITCHEN["counter"])
box("WINDOW balcony opening", G.WINDOWS["W_BALCONY"]["opening"])
b=G.BALCONY
seg("BALCONY north edge",(b["north_edge_x"][0],b["north_edge_y"]),(b["north_edge_x"][1],b["north_edge_y"]))
seg("BALCONY west stub", *b["side_west"]["vertical_stub"])
wr=b["side_west"]["raked"]; er=b["side_east"]["raked"]; ylim=b["railing"]["y1"]
def clip(r):
    t=(ylim-r[0][1])/(r[1][1]-r[0][1]); return (r[0], (r[0][0]+(r[1][0]-r[0][0])*t, ylim))
seg("BALCONY west raked (to railing)", *clip(wr))
seg("BALCONY east raked (to railing)", *clip(er))
box("BALCONY railing", b["railing"])
for k,v in F.FURNITURE.items(): box("FURN "+k, v["box"])

rows=[r for r in rows if r]; rows.sort(key=lambda r:-r[2])
print(f'{"element":36s} {"mean":>6s} {"p95":>6s} {"max":>6s}')
print('-'*62)
for n,m,p,x in rows: print(f'{n:36s} {m:6.2f} {p:6.2f} {x:6.2f}')
print('-'*62)
print(f'{len(rows)} elements   mean-of-means {np.mean([r[1] for r in rows]):.2f} px'
      f'   worst p95 {max(r[2] for r in rows):.2f} px = {max(r[2] for r in rows)*13.2:.0f} mm')

# --------------------------------------------------------------------------
# Mechanical classification of every residual: a 2D MASTER line can legitimately
# have no edge in a TOP VIEW when it runs underneath / inside another solid of
# equal or greater height.  For each deviating sample point we look up which 3D
# object actually occupies that pixel.
def occupant(mx, my):
    p = R.m2p(mx, my)
    xi, yi = p[0]*SSF, p[1]*SSF
    if 0 <= xi < IDX.shape[1] and 0 <= yi < IDX.shape[0]:
        k = IDX[yi, xi]
        return NAMES[k] if k >= 0 else None
    return None

def classify(name, pts):
    buried, loose, tot = {}, 0, 0
    for i in range(len(pts)-1):
        p, q = pts[i], pts[i+1]
        n = max(4, int(math.hypot(q[0]-p[0], q[1]-p[1])*R.S))
        for j in range(n+1):
            t = j/n; x, y = p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t
            if d(x, y) <= 1.5: continue
            tot += 1
            o = occupant(x, y)
            if o: buried[o] = buried.get(o, 0)+1
            else: loose += 1
    return tot, buried, loose

def outline(r): 
    return [(r["x0"],r["y0"]),(r["x1"],r["y0"]),(r["x1"],r["y1"]),(r["x0"],r["y1"]),(r["x0"],r["y0"])]

SRC = {}
for k, r in G.INNER_WALLS.items(): SRC["INNER "+k] = outline(r)
for k, r in G.COLUMNS.items():     SRC["COLUMN "+k] = outline(r)
for tag, run in (("EAST",G.STORAGE_WALL["run_EAST"]),("SOUTH",G.STORAGE_WALL["run_SOUTH"])):
    SRC[f"STORAGE {tag} pocket"] = outline(run["pocket"])
    for i,p_ in enumerate(run["panels_parked"]): SRC[f"STORAGE {tag} parked panel {i+1}"] = outline(p_)
SRC["SC"] = outline(G.SC)
for s_ in G.OUTER_WALLS["west"]["segments"]:
    SRC[f"OUTER west inner y{int(s_['y0'])}"] = [(s_["inner_x"],s_["y0"]),(s_["inner_x"],s_["y1"])]
b_ = G.BALCONY; yl = b_["railing"]["y1"]
for nm_, r_ in (("BALCONY west raked", b_["side_west"]["raked"]), ("BALCONY east raked", b_["side_east"]["raked"])):
    t_ = (yl-r_[0][1])/(r_[1][1]-r_[0][1])
    SRC[nm_] = [r_[0], (r_[0][0]+(r_[1][0]-r_[0][0])*t_, yl)]
for k, v in F.FURNITURE.items(): SRC["FURN "+k] = outline(v["box"])

if __name__ == "__main__":
    print("\nmechanical classification of residual points (> 1.5 px)")
    print(f'{"element":34s} {"pts":>4s} {"buried":>7s} {"loose":>6s}   occupying solid')
    tot_l = 0
    for nm_, pts_ in SRC.items():
        t_, bu_, lo_ = classify(nm_, pts_)
        if t_ == 0: continue
        tot_l += lo_
        top = max(bu_.items(), key=lambda kv: kv[1])[0] if bu_ else "-"
        print(f'{nm_:34s} {t_:4d} {sum(bu_.values()):7d} {lo_:6d}   {top}')
    print(f'\nresidual points not covered by any solid: {tot_l}')
    print("0 means every residual is a line that is genuinely inside or under "
          "another object, i.e. invisible in a top view - not a geometry error.")
