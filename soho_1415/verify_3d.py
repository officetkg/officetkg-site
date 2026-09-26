# -*- coding: utf-8 -*-
"""PHASE 7 numeric validation: 3D object XY bounds vs the approved 2D MASTER."""
import numpy as np, trimesh
import geometry_master as G, furniture as F, build_3d as B

def bnds(name):
    """Bounds of one group, or of the union of several."""
    names = (name,) if isinstance(name, str) else name
    m = trimesh.util.concatenate([x for n in names for x in B.OBJECTS[n]])
    b = m.bounds
    return (b[0][0], b[0][1], b[1][0], b[1][1])

def rb(r): return (r["x0"], r["y0"], r["x1"], r["y1"])
def union(rs):
    a = np.array([rb(r) for r in rs], float)
    return (a[:,0].min(), a[:,1].min(), a[:,2].max(), a[:,3].max())

ow = G.OUTER_WALLS
EXPECT = {
 "Exterior_Walls": (ow["west"]["outer_x"], 0, ow["east"]["outer_x"], ow["south"]["outer_y"]),
 "Columns": union(list(G.COLUMNS.values())),
 "PS": union([v for k,v in G.PS.items() if isinstance(v,dict) and "y0" in v and k!="interior"]),
 "Closets": union(list(G.CLOSETS.values())),
 "Book_Shelf": rb(G.BOOK_SHELF["body"]),
 # tray (G.SHOWER) + glazed screen: screen X plane taken from the 2D door-leaf
 # element W_shower_east_thin, screen Y span = the booth's own depth.
 "Shower": (G.SHOWER["x0"], G.SHOWER["y0"],
            G.INNER_WALLS["W_shower_east_thin"]["x1"], G.SHOWER["y1"]),
 "WD": rb(G.WD),
 "Powder_Room_Fixtures": rb(G.VANITY),
 "Toilet": union([G.TOILET["bowl"],G.TOILET["tank"],G.TOILET["hand_basin"]]),
 "Kitchen": rb(G.KITCHEN["counter"]),
 "Refrigerator": rb(G.REFRIGERATOR),
 "Storage_Wall_Pocket": union([G.STORAGE_WALL["run_EAST"]["pocket"],
                               G.STORAGE_WALL["run_SOUTH"]["pocket"]]),
 "Storage_Wall_Parked_Panels": union(G.STORAGE_WALL["run_EAST"]["panels_parked"]
                                     + G.STORAGE_WALL["run_SOUTH"]["panels_parked"]),
 "Balcony_Railing": rb(G.BALCONY["railing"]),
 "Windows":         rb(G.WINDOWS["W_BALCONY"]["opening"]),
 "Work_Desks": union([F.FURNITURE["WORK_DESK_1"]["box"], F.FURNITURE["WORK_DESK_2"]["box"]]),

 "Printer_Unit": rb(F.FURNITURE["PRINTER_UNIT"]["box"]),
 "Meeting_Table": rb(F.FURNITURE["MEETING_TABLE"]["box"]),

 "Monitor_55": rb(F.FURNITURE["MONITOR_55"]["box"]),
 "Interior_Walls": union(list(G.INNER_WALLS.values())),
}
# components that legitimately sit INSIDE a master rect rather than filling it:
# a pane of glass is thinner than the band it is drawn as.
CONTAINED = {
 "Balcony_Glass": (rb(G.BALCONY["railing"]), "x"),          # x must match, y inside
 "Window_Glass":  (rb(G.WINDOWS["W_BALCONY"]["opening"]), None),
 # A 5-star chair base is a circle, so neither chair fills the rectangular
 # envelope it is planned with; the Aeron reaches its published 658 mm width
 # at the arm pads and sits inside its 598 mm depth.
 ("Work_Chairs", "Work_Chair_Bases"):
     (union([F.FURNITURE["WORK_CHAIR_1"]["box"], F.FURNITURE["WORK_CHAIR_2"]["box"]]), None),
 ("Meeting_Chairs", "Meeting_Chair_Bases"):
     (union([F.FURNITURE[f"MEETING_CHAIR_{i}"]["box"] for i in range(1,7)]), None),
 # the polished frame and the wiring box of the E-CAD sit under / inside the top
 "Table_Frame":   (rb(F.FURNITURE["MEETING_TABLE"]["box"]), None),
 "Table_Wirebox": (rb(F.FURNITURE["MEETING_TABLE"]["box"]), None),
 # the LD carpet is a finish laid inside the Living Dining room polygon
 "Floor_Carpet": ((min(p[0] for p in G.ROOMS["LIVING_DINING"]),
                   min(p[1] for p in G.ROOMS["LIVING_DINING"]),
                   max(p[0] for p in G.ROOMS["LIVING_DINING"]),
                   max(p[1] for p in G.ROOMS["LIVING_DINING"])), None),
 # the hall / wet-area tile is a finish inside the building outline
 "Floor_Tile": ((ow["west"]["outer_x"], 0, ow["east"]["outer_x"], ow["south"]["outer_y"]), None),
 "Book_Shelf_Back": (rb(G.BOOK_SHELF["body"]), None),
}
print(f'{"3D object":30s} {"dx0":>6s} {"dy0":>6s} {"dx1":>6s} {"dy1":>6s}   max|d| px / mm')
print('-'*78)
worst=0; bad=[]
for name, exp in EXPECT.items():
    got = bnds(name)
    d = [g-e for g,e in zip(got, exp)]
    mx = max(abs(v) for v in d); worst=max(worst,mx)
    flag = '' if mx <= 1.01 else '   <== CHECK'
    if mx > 1.01: bad.append(name)
    print(f'{name:30s} {d[0]:6.1f} {d[1]:6.1f} {d[2]:6.1f} {d[3]:6.1f}   {mx:5.2f} / {mx*13.2:5.1f}{flag}')
TOL = 1.01                      # px; one pixel = 13.2 mm at the working scale
for name,(exp,exact_axis) in CONTAINED.items():
    label = name if isinstance(name, str) else " + ".join(name)
    got = bnds(name)
    out = max(exp[0]-got[0], exp[1]-got[1], got[2]-exp[2], got[3]-exp[3], 0.0)
    inside = out <= TOL
    worst = max(worst, out)
    ex = True
    if exact_axis == "x": ex = abs(got[0]-exp[0]) <= .01 and abs(got[2]-exp[2]) <= .01
    ok = inside and ex
    if not ok: bad.append(label)
    note = "inside master rect" if inside else "OUTSIDE master rect"
    print(f'{label:44s} {note:>21s}'
          f'{"  + x exact" if exact_axis=="x" and ex else ""}'
          f'{"" if out <= .01 else f"   overshoot {out:.2f} px = {out*13.2:.0f} mm"}')
print('-'*78)
print(f'objects compared: {len(EXPECT)} exact + {len(CONTAINED)} contained'
      f'   worst XY deviation: {worst:.2f} px = {worst*13.2:.1f} mm')
print('RESULT:', 'PASS  (3D XY == 2D MASTER XY)' if not bad else f'FAIL {bad}')
