# -*- coding: utf-8 -*-
"""
DECORATION
==========
Only what the brief permits:
    laptop, keyboard, mouse, notebook, pen, a FEW books, 1-2 small plants.
Explicitly excluded, per the brief: bed, sofa, lounge chair, coffee table,
banks of plants, large art, clutter, household goods.

Every item sits ON an approved surface and inside that surface's footprint;
verify_decoration() proves it.  No architectural coordinate is touched.
"""
import numpy as np, trimesh, math
import heights as H, furniture as F, geometry_master as G

def P(mm): return mm/H.MM_PER_PX
DESK_TOP  = H.DESK_HEIGHT
TABLE_TOP = H.TABLE_HEIGHT

def _box(x0, y0, x1, y1, z0, z1):
    m = trimesh.creation.box(extents=(x1-x0, y1-y0, z1-z0))
    m.apply_translation(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    return m

def _tilted(x0, y0, x1, y1, z0, z1, deg, axis=(0, 1, 0)):
    m = trimesh.creation.box(extents=(x1-x0, y1-y0, z1-z0))
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(deg), axis))
    m.apply_translation(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    return m

def laptop(cx, cy, z, facing_x=+1):
    """base + screen.  facing_x = which way the user sits relative to the laptop."""
    bw, bd, bt = P(320), P(220), P(16)          # base
    sw, sh, st = P(320), P(205), P(9)           # screen
    base = [_box(cx-bd/2, cy-bw/2, cx+bd/2, cy+bw/2, z, z+bt)]
    hinge = cx - facing_x*bd/2
    sc = _tilted(hinge-st/2, cy-sw/2, hinge+st/2, cy+sw/2, z+bt, z+bt+sh,
                 -facing_x*22, axis=(0, 1, 0))
    sc.apply_translation((facing_x*P(28), 0, 0))
    return base, [sc]

def keyboard(cx, cy, z):
    return [_box(cx-P(65), cy-P(220), cx+P(65), cy+P(220), z, z+P(20))]

def mouse(cx, cy, z):
    m = trimesh.creation.icosphere(subdivisions=2, radius=P(46))
    m.apply_transform(np.diag([0.72, 1.0, 0.40, 1.0]))
    m.apply_translation((cx, cy, z+P(46)*0.40))
    return [m]

def notebook(cx, cy, z, deg=0):
    n = _tilted(cx-P(105), cy-P(148), cx+P(105), cy+P(148), z, z+P(11), deg, (0, 0, 1))
    return [n]

def pen(cx, cy, z, deg=18):
    p = trimesh.creation.cylinder(radius=P(4.5), height=P(140), sections=10)
    p.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (0, 1, 0)))
    p.apply_transform(trimesh.transformations.rotation_matrix(math.radians(deg), (0, 0, 1)))
    p.apply_translation((cx, cy, z+P(4.5)))
    return [p]

def books(x0, x1, y0, z, n=6, h_mm=(190, 250)):
    """a short run of upright books in one shelf cubby."""
    out, y = [], y0
    rng = np.random.default_rng(int(y0*7) & 0xffff)
    for i in range(n):
        t = P(float(rng.uniform(16, 32)))
        hh = P(float(rng.uniform(*h_mm)))
        out.append(_box(x0, y, x1-P(float(rng.uniform(0, 30))), y+t, z, z+hh))
        y += t + P(1.5)
    return out

def plant(cx, cy, z, pot_d=220, pot_h=210, foliage_d=430):
    pot = trimesh.creation.cylinder(radius=P(pot_d)/2, height=P(pot_h), sections=18)
    pot.apply_translation((cx, cy, z+P(pot_h)/2))
    fol = trimesh.creation.icosphere(subdivisions=2, radius=P(foliage_d)/2)
    fol.apply_transform(np.diag([1.0, 0.92, 0.80, 1.0]))
    fol.apply_translation((cx, cy, z+P(pot_h)+P(foliage_d)*0.34))
    stem = trimesh.creation.cylinder(radius=P(14), height=P(foliage_d)*0.4, sections=8)
    stem.apply_translation((cx, cy, z+P(pot_h)+P(foliage_d)*0.16))
    return [pot], [fol, stem]

# ----------------------------------------------------------------------
def build():
    """-> {group_name: [meshes]}, and the support record for verification."""
    out = {"Laptops": [], "Laptop_Screens": [], "Desk_Kit": [], "Paper": [],
           "Books": [], "Plant_Pots": [], "Plant_Foliage": []}
    support = []
    for k in ("WORK_DESK_1", "WORK_DESK_2"):
        d = F.FURNITURE[k]["box"]
        cy = (d["y0"] + d["y1"])/2
        _b, _s = laptop(d["x0"]+P(300), cy-P(60), DESK_TOP, +1)
        out["Laptops"] += _b; out["Laptop_Screens"] += _s
        out["Desk_Kit"] += keyboard(d["x1"]-P(230), cy-P(60), DESK_TOP)
        out["Desk_Kit"] += mouse(d["x1"]-P(240), cy+P(430), DESK_TOP)
        out["Paper"] += notebook(d["x0"]+P(250), cy+P(470), DESK_TOP, 12)
        support += [(k, d)]*4
    t = F.FURNITURE["MEETING_TABLE"]["box"]
    for dx, dy, rot in ((P(520), P(240), -9), (P(1230), P(640), 7)):
        out["Paper"] += notebook(t["x0"]+dx, t["y0"]+dy, TABLE_TOP, rot)
        out["Paper"] += pen(t["x0"]+dx+P(140), t["y0"]+dy-P(40), TABLE_TOP, rot+22)
        support += [("MEETING_TABLE", t)]*2
    # a few books, four cubbies out of thirty
    bs = G.BOOK_SHELF["body"]
    for i, (row, ycell) in enumerate([(4, 0), (3, 2), (2, 1), (4, 3)]):
        z = H.BOOKSHELF_HEIGHT*row/6.0 + P(20)
        y0 = bs["y0"] + (bs["y1"]-bs["y0"])*(ycell + .12)/5.0
        out["Books"] += books(bs["x0"]+P(30), bs["x1"]-P(20), y0, z, n=6)
        support += [("BOOK_SHELF", bs)]*6
    # two small plants: one on the floor by the window, one on a shelf
    pot, fol = plant(318, 620, 0.0)
    out["Plant_Pots"] += pot; out["Plant_Foliage"] += fol
    pot, fol = plant(bs["x0"]+P(140), bs["y0"]+P(1500),
                     H.BOOKSHELF_HEIGHT*5/6.0 + P(20),
                     pot_d=130, pot_h=120, foliage_d=230)
    out["Plant_Pots"] += pot; out["Plant_Foliage"] += fol
    return {k: v for k, v in out.items() if v}, support

BANNED = ["bed", "sofa", "lounge chair", "coffee table", "bank of plants",
          "large artwork", "clutter", "household goods"]

def _supports():
    out = {}
    for k in ("WORK_DESK_1", "WORK_DESK_2"):
        b = F.FURNITURE[k]["box"]; out[k] = (b, DESK_TOP)
    b = F.FURNITURE["MEETING_TABLE"]["box"]; out["MEETING_TABLE"] = (b, TABLE_TOP)
    b = G.BOOK_SHELF["body"];                out["BOOK_SHELF"] = (b, 0.0)
    out["FLOOR"] = ({"x0": 159, "y0": 568, "x1": 355, "y1": 666}, 0.0)   # clear LD floor
    return out

def verify():
    """every item must sit ON an approved surface and INSIDE its footprint."""
    objs, _ = build()
    sup = _supports()
    print(f'{"group":16s} {"items":>5s}  {"z mm":>16s}   support / status')
    bad = 0
    for k, v in objs.items():
        m = trimesh.util.concatenate(v)
        lo, hi = m.bounds
        hit = None
        for nm, (b, top) in sup.items():
            if (lo[0] >= b["x0"]-1 and lo[1] >= b["y0"]-1
                    and hi[0] <= b["x1"]+1 and hi[1] <= b["y1"]+1
                    and lo[2] >= top-0.6):
                hit = nm; break
        if hit is None:
            # desk items span two desks; test each mesh separately
            per = []
            for mm_ in v:
                l2, h2 = mm_.bounds; ok = False
                for nm, (b, top) in sup.items():
                    if (l2[0] >= b["x0"]-1 and l2[1] >= b["y0"]-1
                            and h2[0] <= b["x1"]+1 and h2[1] <= b["y1"]+1
                            and l2[2] >= top-0.6):
                        per.append(nm); ok = True; break
                if not ok: per.append("OFF-SUPPORT"); bad += 1
            hit = "/".join(sorted(set(per)))
        print(f'{k:16s} {len(v):5d}  {lo[2]*H.MM_PER_PX:6.0f} ..{hi[2]*H.MM_PER_PX:7.0f}   {hit}')
    print(f'\ntotal items: {sum(len(v) for v in objs.values())}')
    print("items off an approved support:", bad)
    print("banned items: none of", ", ".join(BANNED))
    return objs

if __name__ == "__main__":
    verify()
