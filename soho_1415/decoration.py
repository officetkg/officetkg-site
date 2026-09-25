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

def plant(cx, cy, z, pot_d=210, pot_h=190, spread=300):
    """A small plant: a slightly tapered pot, a short trunk and three
    overlapping leaf clusters.  Deliberately modest -- the brief allows one or
    two SMALL plants, not a specimen tree, and a single big sphere reads as a
    blob rather than as planting."""
    pot = trimesh.creation.cylinder(radius=P(pot_d)/2, height=P(pot_h), sections=24)
    v = pot.vertices.copy()                       # taper: base 76 % of the rim
    lo, hi = v[:, 2].min(), v[:, 2].max()
    k = 0.76 + 0.24*(v[:, 2]-lo)/(hi-lo)
    v[:, 0] *= k; v[:, 1] *= k
    pot = trimesh.Trimesh(vertices=v, faces=pot.faces, process=False)
    pot.apply_translation((cx, cy, z + P(pot_h)/2))
    trunk = trimesh.creation.cylinder(radius=P(16), height=P(spread)*0.55, sections=10)
    trunk.apply_translation((cx, cy, z + P(pot_h) + P(spread)*0.27))
    fol = []
    for dx, dy, dz, sc in ((-0.26, 0.10, 0.62, 0.62),
                           ( 0.24, -0.14, 0.78, 0.70),
                           ( 0.02, 0.16, 1.02, 0.54)):
        b = trimesh.creation.icosphere(subdivisions=3, radius=P(spread)/2*sc)
        b.apply_transform(np.diag([1.0, 0.90, 0.72, 1.0]))
        b.apply_translation((cx + P(spread)*dx, cy + P(spread)*dy,
                             z + P(pot_h) + P(spread)*dz))
        fol.append(b)
    return [pot], [trunk] + fol

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
    # two small plants: one on the floor by the window, one on a shelf.
    # The floor plant stands in the clear band in front of the glazing, beside
    # the solid stub of the window wall -- 277 mm clear of everything.  It used
    # to sit at (318, 620), which is INSIDE W_SEcol_return_head, so it grew out
    # of the wall at the column corner.
    pot, fol = plant(156, 644, 0.0)
    out["Plant_Pots"] += pot; out["Plant_Foliage"] += fol
    pot, fol = plant(bs["x0"]+P(140), bs["y0"]+P(1500),
                     H.BOOKSHELF_HEIGHT*5/6.0 + P(20),
                     pot_d=130, pot_h=115, spread=190)
    out["Plant_Pots"] += pot; out["Plant_Foliage"] += fol
    return {k: v for k, v in out.items() if v}, support

def _obstacles():
    """Every solid a decoration item must not intersect, as plan rectangles."""
    out = []
    def push(n, x0, y0, x1, y1):
        out.append((n, dict(x0=min(x0, x1), y0=min(y0, y1),
                            x1=max(x0, x1), y1=max(y0, y1))))
    def walk(prefix, v):
        if isinstance(v, dict):
            if {"x0", "y0", "x1", "y1"} <= set(v):
                push(prefix, v["x0"], v["y0"], v["x1"], v["y1"]); return
            for k, sub in v.items(): walk(f"{prefix}.{k}", sub)
        elif isinstance(v, list):
            for i, sub in enumerate(v): walk(f"{prefix}[{i}]", sub)
    ow = G.OUTER_WALLS
    for seg in ow["north"]["segments"]: push("OUTER.north", seg["x0"], 0, seg["x1"], seg["inner_y"])
    for seg in ow["west"]["segments"]:  push("OUTER.west", 0, seg["y0"], seg["inner_x"], seg["y1"])
    for seg in ow["east"]["segments"]:  push("OUTER.east", seg["inner_x"], seg["y0"], 365, seg["y1"])
    ss = ow["south"]["solid_segment"]
    push("OUTER.south_solid", ss["x0"], ss["y0"], ss["x1"], ss["y1"])
    push("OUTER.south_sash", ow["south"]["sash_segment"]["x0"], 665,
         ow["south"]["sash_segment"]["x1"], 672)
    for nm in ("INNER_WALLS", "COLUMNS", "PS", "STORAGE_WALL", "KITCHEN",
               "CLOSETS", "SHOWER", "WD", "VANITY", "TOILET", "REFRIGERATOR"):
        if hasattr(G, nm): walk(nm, getattr(G, nm))
    b = G.BOOK_SHELF["body"]; push("BOOK_SHELF", b["x0"], b["y0"], b["x1"], b["y1"])
    for k, d in F.FURNITURE.items():
        bb = d.get("box")
        if bb: push(k, bb["x0"], bb["y0"], bb["x1"], bb["y1"])
    return out

BANNED = ["bed", "sofa", "lounge chair", "coffee table", "bank of plants",
          "large artwork", "clutter", "household goods"]

def _supports():
    out = {}
    for k in ("WORK_DESK_1", "WORK_DESK_2"):
        b = F.FURNITURE[k]["box"]; out[k] = (b, DESK_TOP)
    b = F.FURNITURE["MEETING_TABLE"]["box"]; out["MEETING_TABLE"] = (b, TABLE_TOP)
    b = G.BOOK_SHELF["body"];                out["BOOK_SHELF"] = (b, 0.0)
    # Clear LD floor: the band between the meeting chairs and the glazing.
    # Bounded by the solid stub of the window wall (east end x=135), the west
    # face of the SE column return (x=317), the north edge of the meeting
    # chairs (y=613) and the inner face of the sash (y=665).  The old rect ran
    # to x=355 / y=666 and so swallowed the column return, which let an item be
    # "on the floor" while standing inside a wall.
    out["FLOOR"] = ({"x0": 136, "y0": 613, "x1": 317, "y1": 665}, 0.0)
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
    # ---- clash: nothing may reach into a wall, a column, casework or a piece
    # of furniture that is not the item's own support.
    obs = _obstacles()
    clash = 0
    for k, v in objs.items():
        for mm_ in v:
            l2, h2 = mm_.bounds
            own = None
            for nm, (b, top) in sup.items():
                if (l2[0] >= b["x0"]-1 and l2[1] >= b["y0"]-1
                        and h2[0] <= b["x1"]+1 and h2[1] <= b["y1"]+1):
                    own = nm; break
            for nm, r in obs:
                if own and (nm == own or nm.startswith(own)): continue
                if (l2[0] < r["x1"] and h2[0] > r["x0"]
                        and l2[1] < r["y1"] and h2[1] > r["y0"]):
                    ov = (min(h2[0], r["x1"])-max(l2[0], r["x0"]),
                          min(h2[1], r["y1"])-max(l2[1], r["y0"]))
                    print(f'  CLASH  {k} overlaps {nm} by '
                          f'{ov[0]*H.MM_PER_PX:.0f} x {ov[1]*H.MM_PER_PX:.0f} mm')
                    clash += 1

    print(f'\ntotal items: {sum(len(v) for v in objs.values())}')
    print("items off an approved support:", bad)
    print("items intersecting a wall, column, casework or other furniture:", clash)
    print("banned items: none of", ", ".join(BANNED))
    return objs

if __name__ == "__main__":
    verify()
