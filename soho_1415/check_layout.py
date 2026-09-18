# -*- coding: utf-8 -*-
"""PHASE 5 validation: furniture vs architecture, furniture vs furniture, circulation."""
import numpy as np, itertools
import geometry_master as G, furniture as F

OX,OY=G.OX,G.OY
def w(r): return (r["x0"]+OX, r["y0"]+OY, r["x1"]+OX, r["y1"]+OY)   # master -> work
def ov(a,b):
    x=min(a[2],b[2])-max(a[0],b[0]); y=min(a[3],b[3])-max(a[1],b[1])
    return (x,y) if x>0 and y>0 else None

# --- architectural solids furniture must not enter -------------------------
SOLID={}
for k,v in G.INNER_WALLS.items(): SOLID["wall:"+k]=w(v)
for k,v in G.COLUMNS.items():     SOLID["column:"+k]=w(v)
for k,v in G.PS.items():
    if isinstance(v,dict) and "y0" in v: SOLID["PS:"+k]=w(v)
SOLID["outer:south_band"]=w(G.OUTER_WALLS["south"]["solid_segment"])
for nm,v in (("SC",G.SC),("SHOWER",G.SHOWER),("WD",G.WD),("VANITY",G.VANITY),
             ("REFRIGERATOR",G.REFRIGERATOR),("BOOK_SHELF",G.BOOK_SHELF["body"]),
             ("ENTRANCE_NICHE",G.ENTRANCE_NICHE_UNIDENTIFIED)): SOLID[nm]=w(v)
for k,v in G.CLOSETS.items(): SOLID["CLO:"+k]=w(v)
for k,v in G.TOILET.items():
    if isinstance(v,dict) and "y0" in v: SOLID["TOILET:"+k]=w(v)
for k,v in G.KITCHEN.items():
    if isinstance(v,dict) and "y0" in v and k!="room_ref": SOLID["KITCHEN:"+k]=w(v)
for tag,run in (("EAST",G.STORAGE_WALL["run_EAST"]),("SOUTH",G.STORAGE_WALL["run_SOUTH"])):
    SOLID[f"STORAGE:{tag}.pocket"]=w(run["pocket"])          # pocket box is physical
# exterior wall inner faces -> inside-of-dwelling box
INSIDE=(418,408,758,816)   # combined MB+LD volume (work px), south limit = sash line

FUR={k:w(v["box"]) for k,v in F.FURNITURE.items()}
MM=F.MM_PER_PX
bad=0
print("=== 1. furniture vs architecture ===")
for fk,fb in FUR.items():
    for sk,sb in SOLID.items():
        o=ov(fb,sb)
        if o:
            print(f"  CLASH  {fk} x {sk}   overlap {o[0]}x{o[1]} px = {o[0]*MM:.0f}x{o[1]*MM:.0f} mm"); bad+=1
print("  none" if bad==0 else "")
print("=== 2. furniture vs furniture ===")
b2=0
for (ak,ab),(bk,bb) in itertools.combinations(FUR.items(),2):
    o=ov(ab,bb)
    if o:
        touching = o[0]<=1 or o[1]<=1
        if not touching:
            print(f"  CLASH  {ak} x {bk}  overlap {o[0]}x{o[1]} px"); b2+=1
print("  none" if b2==0 else "")
print("=== 3. inside the dwelling ===")
b3=0
for fk,fb in FUR.items():
    if not (fb[0]>=INSIDE[0]-1 and fb[1]>=INSIDE[1]-1 and fb[2]<=INSIDE[2]+1 and fb[3]<=INSIDE[3]+1):
        print(f"  OUTSIDE  {fk} {fb}"); b3+=1
print("  all inside" if b3==0 else "")
print("=== 4. circulation widths (narrowest free dimension of each route) ===")
for nm,c in F.CLEARANCES.items():
    z=w(c["zone"]); x0,y0,x1,y1=z
    occ=np.zeros((y1-y0, x1-x0),bool)
    for fk,fb in FUR.items():
        o=ov(z,fb)
        if o:
            occ[max(fb[1],y0)-y0:min(fb[3],y1)-y0, max(fb[0],x0)-x0:min(fb[2],x1)-x0]=True
    for sk,sb in SOLID.items():
        o=ov(z,sb)
        if o:
            occ[max(sb[1],y0)-y0:min(sb[3],y1)-y0, max(sb[0],x0)-x0:min(sb[2],x1)-x0]=True
    free_rows=(~occ).all(1).sum(); free_cols=(~occ).all(0).sum()
    freest=max(free_rows,free_cols)*MM
    ok = "OK " if freest>=c["min_mm"] else "!! "
    print(f"  {ok}{nm:34s} clear {freest:6.0f} mm   (need {c['min_mm']} mm)")
print(f"\nRESULT: {'PASS' if bad==0 and b2==0 and b3==0 else 'FAIL'}  "
      f"(architecture clashes {bad}, furniture clashes {b2}, outside {b3})")
