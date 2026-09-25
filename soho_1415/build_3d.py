# -*- coding: utf-8 -*-
"""
PHASE 6  --  3D GEOMETRY
========================
Built ONLY from the approved 2D MASTER (geometry_master.py) and the approved
furniture layout (furniture.py).  Every X and Y is read from those files; this
module adds Z and nothing else.  No image was consulted while writing it.

Units: MASTER px in X, Y and Z.  Z comes from heights.py (all provisional).
Right-handed: X east, Y south, Z up.  Interior floor level Z = 0.
"""
import numpy as np, trimesh, json
from shapely.geometry import Polygon
import geometry_master as G, furniture as F, heights as H

OBJECTS = {}                      # name -> list of trimesh meshes

def _box(x0, y0, x1, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    if x1-x0 <= 0 or y1-y0 <= 0 or z1-z0 <= 0: return None
    m = trimesh.creation.box(extents=(x1-x0, y1-y0, z1-z0))
    m.apply_translation(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    return m

def add(group, *meshes):
    OBJECTS.setdefault(group, [])
    for m in meshes:
        if m is not None: OBJECTS[group].append(m)

def R(r, z0, z1):                                   # master rect dict -> box
    return _box(r["x0"], r["y0"], r["x1"], r["y1"], z0, z1)

def wall(r, z0, z1, axis=None, openings=()):
    """Wall from a master rect with openings along `axis` ('x' or 'y').
    openings = list of (a0, a1, head_z) in master coords."""
    if not openings: return [R(r, z0, z1)]
    out, pos = [], (r["x0"] if axis == "x" else r["y0"])
    end = r["x1"] if axis == "x" else r["y1"]
    for a0, a1, head in sorted(openings):
        if a0 > pos:
            out.append(_box(pos, r["y0"], a0, r["y1"], z0, z1) if axis == "x"
                       else _box(r["x0"], pos, r["x1"], a0, z0, z1))
        out.append(_box(a0, r["y0"], a1, r["y1"], head, z1) if axis == "x"
                   else _box(r["x0"], a0, r["x1"], a1, head, z1))
        pos = a1
    if pos < end:
        out.append(_box(pos, r["y0"], end, r["y1"], z0, z1) if axis == "x"
                   else _box(r["x0"], pos, r["x1"], end, z0, z1))
    return out

M   = G.M
WH  = H.WALL_HEIGHT
DH  = H.DOOR_HEIGHT

# ======================================================================
# 1. EXTERIOR WALLS
# ======================================================================
ow = G.OUTER_WALLS
# -- west (three thickness segments straight out of the master)
for s in ow["west"]["segments"]:
    add("Exterior_Walls", _box(ow["west"]["outer_x"], s["y0"], s["inner_x"], s["y1"], 0, WH))
add("Exterior_Walls", _box(ow["west"]["outer_x"], M(0,150)[1], M(418,0)[0], M(0,230)[1], 0, WH))
# -- east
for s in ow["east"]["segments"]:
    add("Exterior_Walls", _box(s["inner_x"], s["y0"], ow["east"]["outer_x"], s["y1"], 0, WH))
# -- north, segment by segment, entrance door left open
add("Exterior_Walls",
    _box(M(403,0)[0], 0, M(590,0)[0], M(0,156)[1], 0, WH),
    _box(M(587,0)[0], 0, M(637,0)[0], M(0,158)[1], 0, WH),
    _box(M(704,0)[0], 0, M(726,0)[0], M(0,174)[1], 0, WH),
    _box(M(637,0)[0], 0, M(704,0)[0], M(0,158)[1],          # head over entrance door
         H.ENTRANCE_DOOR_HEIGHT, WH))
# -- south: solid band, sash head, east pier
add("Exterior_Walls",
    R(ow["south"]["solid_segment"], 0, WH),
    _box(M(534,0)[0], M(0,816)[1], M(721,0)[0], M(0,822)[1], H.WINDOW_HEAD, WH),
    _box(M(721,0)[0], M(0,816)[1], M(728,0)[0], M(0,822)[1], 0, WH))

# ======================================================================
# 2. INTERIOR WALLS  (door openings split out of the runs)
# ======================================================================
IW = dict(G.INNER_WALLS)
add("Interior_Walls", *wall(IW.pop("W_powder_kitchen"), 0, WH, "y",
        [(M(0,230)[1], M(0,285)[1], DH),        # powder room door
         (M(0,343)[1], M(0,392)[1], DH)]))      # toilet door
add("Interior_Walls", *wall(IW.pop("W_hall_south"), 0, WH, "x",
        [(M(632,0)[0], M(694,0)[0], DH)]))      # living dining door
IW.pop("W_shower_east_thin")                    # that piece IS the shower door
for k, r in IW.items():
    add("Interior_Walls", R(r, 0, WH))

# ======================================================================
# 3. COLUMNS
# ======================================================================
for k, r in G.COLUMNS.items():
    add("Columns", R(r, 0, H.COLUMN_HEIGHT))

# ======================================================================
# 4. PS
# ======================================================================
for k, r in G.PS.items():
    if isinstance(r, dict) and "y0" in r and k != "interior":
        add("PS", R(r, 0, H.PS_HEIGHT))

# ======================================================================
# 5. ENTRANCE  (door leaf, closed position - the 2D swing arc is annotation)
# ======================================================================
d = G.DOORS["D_ENTRANCE"]
add("Entrance", _box(d["opening"]["x0"], M(0,150)[1], d["opening"]["x1"], M(0,155)[1],
                     0, H.ENTRANCE_DOOR_HEIGHT))
add("Entrance", R(G.SC, 0, H.SC_HEIGHT))

# ======================================================================
# 6-13. FIXTURES
# ======================================================================
add("Shower", R(G.SHOWER, 0, 2/H.MM_PER_PX))                       # tray
add("Shower", _box(G.SHOWER["x1"], G.SHOWER["y0"], G.SHOWER["x1"]+3,
                   G.SHOWER["y1"], 0, H.SHOWER_ENCLOSURE_HEIGHT))  # glazed screen + door,
# plane taken straight from INNER_WALLS["W_shower_east_thin"] in the 2D master
add("WD", R(G.WD, 0, H.WD_HEIGHT))
add("Powder_Room_Fixtures", R(G.VANITY, 0, H.VANITY_HEIGHT))
add("Powder_Room_Fixtures", R(G.VANITY_BOWL, H.VANITY_HEIGHT-4, H.VANITY_HEIGHT))
add("Toilet", R(G.TOILET["bowl"], 0, H.TOILET_PAN_HEIGHT),
              R(G.TOILET["tank"], 0, H.TOILET_TANK_HEIGHT),
              R(G.TOILET["hand_basin"], 0, H.HAND_BASIN_HEIGHT))
add("Kitchen", R(G.KITCHEN["counter"], 0, H.KITCHEN_COUNTER_HEIGHT),
               R(G.KITCHEN["hob"], H.KITCHEN_COUNTER_HEIGHT,
                 H.KITCHEN_COUNTER_HEIGHT + 2/H.MM_PER_PX),
               R(G.KITCHEN["sink_bowl"], H.KITCHEN_COUNTER_HEIGHT-12,
                 H.KITCHEN_COUNTER_HEIGHT))
add("Refrigerator", R(G.REFRIGERATOR, 0, H.REFRIGERATOR_HEIGHT))
for k, r in G.CLOSETS.items():
    add("Closets", R(r, 0, H.CLOSET_HEIGHT))
bs = G.BOOK_SHELF["body"]
add("Book_Shelf", R(bs, 0, H.BOOKSHELF_HEIGHT))
for y in G.BOOK_SHELF["shelf_lines_y"]:
    add("Book_Shelf", _box(bs["x0"], y-0.5, bs["x1"], y+0.5, 0, H.BOOKSHELF_HEIGHT))

# ======================================================================
# 14-15. STORAGE WALL  --  OPEN / PARKED
# ======================================================================
for tag, run in (("EAST", G.STORAGE_WALL["run_EAST"]),
                 ("SOUTH", G.STORAGE_WALL["run_SOUTH"])):
    pk = run["pocket"]                       # open-mouthed casing, not a solid block
    t = 1.5
    if run["axis"] == "vertical":            # mouth faces south
        add("Storage_Wall_Pocket",
            _box(pk["x0"], pk["y0"], pk["x0"]+t, pk["y1"], 0, H.PARTITION_PANEL_HEIGHT),
            _box(pk["x1"]-t, pk["y0"], pk["x1"], pk["y1"], 0, H.PARTITION_PANEL_HEIGHT),
            _box(pk["x0"], pk["y0"], pk["x1"], pk["y0"]+t, 0, H.PARTITION_PANEL_HEIGHT))
    else:                                    # mouth faces east
        add("Storage_Wall_Pocket",
            _box(pk["x0"], pk["y0"], pk["x1"], pk["y0"]+t, 0, H.PARTITION_PANEL_HEIGHT),
            _box(pk["x0"], pk["y1"]-t, pk["x1"], pk["y1"], 0, H.PARTITION_PANEL_HEIGHT),
            _box(pk["x0"], pk["y0"], pk["x0"]+t, pk["y1"], 0, H.PARTITION_PANEL_HEIGHT))
    for p in run["panels_parked"]:
        add("Storage_Wall_Parked_Panels", R(p, 0, H.PARTITION_PANEL_HEIGHT))
    rl = run["rail_line"]
    if run["axis"] == "vertical":
        add("Storage_Wall_Rail", _box(run["pocket"]["x0"], rl["y0"], run["pocket"]["x1"],
                                      rl["y1"], WH-H.PARTITION_RAIL_DROP, WH))
    else:
        add("Storage_Wall_Rail", _box(rl["x0"], run["pocket"]["y0"], rl["x1"],
                                      run["pocket"]["y1"], WH-H.PARTITION_RAIL_DROP, WH))

# ======================================================================
# 16. WINDOWS  --  2 leaves, unequal, wide leaf WEST / narrow leaf EAST,
#     head below the ceiling.  All confirmed against the listing photos;
#     XY unchanged, taken from WINDOWS["W_BALCONY"].
# ======================================================================
wb = G.WINDOWS["W_BALCONY"]["opening"]
FR  = H.WINDOW_FRAME
yc  = (wb["y0"] + wb["y1"]) / 2
gt  = H.GLASS_THICKNESS / 2
add("Windows",                                            # outer frame
    _box(wb["x0"], wb["y0"], wb["x1"], wb["y1"], H.WINDOW_HEAD - FR, H.WINDOW_HEAD),
    _box(wb["x0"], wb["y0"], wb["x1"], wb["y1"], 0, FR * 0.4),
    _box(wb["x0"], wb["y0"], wb["x0"] + FR, wb["y1"], 0, H.WINDOW_HEAD),
    _box(wb["x1"] - FR, wb["y0"], wb["x1"], wb["y1"], 0, H.WINDOW_HEAD))
add("Windows",                                            # meeting stile
    _box(M(600,0)[0], wb["y0"], M(604,0)[0], wb["y1"], 0, H.WINDOW_HEAD))
add("Window_Glass",                                       # narrow leaf, EAST
    _box(M(539,0)[0] + FR, yc - gt, M(600,0)[0], yc + gt, FR * 0.4, H.WINDOW_HEAD - FR))
add("Window_Glass",                                       # wide leaf, WEST
    _box(M(604,0)[0], yc - gt, M(718,0)[0] - FR, yc + gt, FR * 0.4, H.WINDOW_HEAD - FR))

# ======================================================================
# 17-18. BALCONY
# ======================================================================
B = G.BALCONY
bz0, bz1 = -H.BALCONY_SLAB_DROP, 0
col = G.COLUMNS["C_SE"]
w_top, e_top = B["side_west"]["raked"][0], B["side_east"]["raked"][0]
def rake(p0, p1, y):
    t = (y - p0[1]) / (p1[1] - p0[1]); return p0[0] + (p1[0]-p0[0]) * t
y_rail = B["railing"]["y1"]   # slab runs out to the railing outer face
poly = [(B["side_west"]["vertical_stub"][0][0], B["north_edge_y"]),
        (col["x0"], B["north_edge_y"]), (col["x0"], col["y1"]),
        (e_top[0], col["y1"]),
        (rake(e_top, B["side_east"]["raked"][1], y_rail), y_rail),
        (rake(w_top, B["side_west"]["raked"][1], y_rail), y_rail),
        (w_top[0], w_top[1])]
bal = trimesh.creation.extrude_polygon(Polygon(poly), height=bz1-bz0)
bal.apply_translation((0, 0, bz0))
add("Balcony_Floor", bal)

# --- balustrade: clear glass, dark capping, dark posts (per the photos) ---
rail = B["railing"]; rz = bz0
ry0, ry1 = rail["y0"], rail["y1"]
rmid = (ry0 + ry1) / 2
add("Balcony_Railing",                                     # base channel, full footprint
    _box(rail["x0"], ry0, rail["x1"], ry1, rz, rz + H.BALCONY_RAILING_BASE))
add("Balcony_Railing",                                     # flat capping
    _box(rail["x0"], ry0 + 1, rail["x1"], ry1 - 1,
         rz + H.BALCONY_RAILING_HEIGHT - H.BALCONY_RAILING_CAP,
         rz + H.BALCONY_RAILING_HEIGHT))
_pitch = H.BALCONY_POST_PITCH
_x = rail["x0"]
while _x < rail["x1"]:                                     # posts
    add("Balcony_Railing", _box(_x, rmid - 3, min(_x + 5, rail["x1"]), rmid + 3,
                                rz, rz + H.BALCONY_RAILING_HEIGHT))
    _x += _pitch
add("Balcony_Glass",                                       # clear infill
    _box(rail["x0"], rmid - H.GLASS_THICKNESS/2, rail["x1"], rmid + H.GLASS_THICKNESS/2,
         rz + H.BALCONY_RAILING_BASE, rz + H.BALCONY_RAILING_GLASS_TOP))

# --- hedate-ita: the maroon escape partitions on the two raked side lines ---
def _slab(p, q, t, z0, z1):
    """thin panel of thickness t along the segment p->q (master XY)."""
    import math
    dx, dy = q[0]-p[0], q[1]-p[1]
    L = math.hypot(dx, dy)
    m = trimesh.creation.box(extents=(L, t, z1-z0))
    m.apply_transform(trimesh.transformations.rotation_matrix(math.atan2(dy, dx), (0,0,1)))
    m.apply_translation(((p[0]+q[0])/2, (p[1]+q[1])/2, (z0+z1)/2))
    return m
PT = 2.5                                                   # ~33 mm panel
pz1 = bz0 + H.BALCONY_PARTITION_HEIGHT
ws = B["side_west"]
add("Balcony_Partitions", _slab(ws["vertical_stub"][0], ws["vertical_stub"][1], PT, bz0, pz1))
_wr = ws["raked"]
_we = (rake(_wr[0], _wr[1], ry1), ry1)
add("Balcony_Partitions", _slab(_wr[0], _we, PT, bz0, pz1))
_er = B["side_east"]["raked"]
_ee = (rake(_er[0], _er[1], ry1), ry1)
add("Balcony_Partitions", _slab(_er[0], _ee, PT, bz0, pz1))

# --- rainwater downpipe: the small circle at the west bend, identified in BAL_3 ---
_pc = ws["pivot_circle_at"]; _pr = H.DOWNPIPE_DIA / 2
_dp = trimesh.creation.cylinder(radius=_pr, height=H.BALCONY_SOFFIT, sections=16)
_dp.apply_translation((_pc[0], _pc[1], bz0 + H.BALCONY_SOFFIT/2))
add("Downpipe", _dp)

# ======================================================================
# 19-23. FURNITURE  (XY straight from the approved layout)
# ======================================================================
def f(k): return F.FURNITURE[k]["box"]
for k in ("WORK_DESK_1", "WORK_DESK_2"):
    add("Work_Desks", R(f(k), H.DESK_HEIGHT - H.DESK_TOP_THICKNESS, H.DESK_HEIGHT))
    r = f(k)                                             # two end gables
    for x in (r["x0"], r["x1"]-2):
        add("Work_Desks", _box(x, r["y0"]+1, x+2, r["y1"]-1, 0, H.DESK_HEIGHT-H.DESK_TOP_THICKNESS))
for k in ("WORK_CHAIR_1", "WORK_CHAIR_2"):
    r = f(k)
    add("Work_Chairs", _box(r["x0"]+1, r["y0"]+1, r["x1"]-1, r["y1"]-1,
                            H.WORK_CHAIR_SEAT-3, H.WORK_CHAIR_SEAT))
    add("Work_Chairs", _box(r["x1"]-4, r["y0"]+1, r["x1"]-1, r["y1"]-1,
                            H.WORK_CHAIR_SEAT, H.WORK_CHAIR_BACK_TOP))
    add("Work_Chairs", _box((r["x0"]+r["x1"])/2-2, (r["y0"]+r["y1"])/2-2,
                            (r["x0"]+r["x1"])/2+2, (r["y0"]+r["y1"])/2+2, 0, H.WORK_CHAIR_SEAT-3))
add("Printer_Unit", R(f("PRINTER_UNIT"), 0, H.PRINTER_UNIT_HEIGHT))
mt = f("MEETING_TABLE")
add("Meeting_Table", R(mt, H.TABLE_HEIGHT-H.TABLE_TOP_THICKNESS, H.TABLE_HEIGHT))
for cx in (mt["x0"]+3, mt["x1"]-6):
    for cy in (mt["y0"]+3, mt["y1"]-6):
        add("Meeting_Table", _box(cx, cy, cx+3, cy+3, 0, H.TABLE_HEIGHT-H.TABLE_TOP_THICKNESS))
for i in range(1, 7):
    r = f(f"MEETING_CHAIR_{i}")
    north = i <= 3
    add("Meeting_Chairs", _box(r["x0"]+1, r["y0"]+1, r["x1"]-1, r["y1"]-1,
                               H.MEETING_CHAIR_SEAT-3, H.MEETING_CHAIR_SEAT))
    by0, by1 = (r["y0"]+1, r["y0"]+4) if north else (r["y1"]-4, r["y1"]-1)
    add("Meeting_Chairs", _box(r["x0"]+1, by0, r["x1"]-1, by1,
                               H.MEETING_CHAIR_SEAT, H.MEETING_CHAIR_BACK_TOP))
    add("Meeting_Chairs", _box((r["x0"]+r["x1"])/2-2, (r["y0"]+r["y1"])/2-2,
                               (r["x0"]+r["x1"])/2+2, (r["y0"]+r["y1"])/2+2,
                               0, H.MEETING_CHAIR_SEAT-3))
mo = f("MONITOR_55")
add("Monitor_55", _box(mo["x0"], mo["y0"], mo["x1"], mo["y1"],
                       H.MONITOR_CENTRE_Z - H.MONITOR_SCREEN_H/2,
                       H.MONITOR_CENTRE_Z + H.MONITOR_SCREEN_H/2))

# ======================================================================
# floor slab (interior), for the renders only
# ======================================================================
add("Floor_Slab", _box(M(403,0)[0], M(0,150)[1], M(768,0)[0], M(0,822)[1],
                       -H.SLAB_THICKNESS, 0))

if __name__ == "__main__":
    scene = trimesh.Scene()
    rows = []
    for name, meshes in OBJECTS.items():
        m = trimesh.util.concatenate(meshes)
        m.metadata["name"] = name
        scene.add_geometry(m, node_name=name, geom_name=name)
        rows.append((name, len(meshes), len(m.faces),
                     *np.round(m.bounds.reshape(-1), 1)))
    print(f'{"object":28s} {"parts":>5s} {"tris":>6s}   bounds  x0 y0 z0  x1 y1 z1  (MASTER px)')
    for r in rows:
        print(f'{r[0]:28s} {r[1]:5d} {r[2]:6d}   '
              f'{r[3]:7.1f} {r[4]:7.1f} {r[5]:6.1f}  {r[6]:7.1f} {r[7]:7.1f} {r[8]:6.1f}')
    scene.export("out/model_3d.glb")
    print(f'\n{len(rows)} objects exported -> out/model_3d.glb')
