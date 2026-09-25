# -*- coding: utf-8 -*-
"""PHASE 7 numeric validation: 3D object XY bounds vs the approved 2D MASTER."""
import numpy as np, trimesh
import geometry_master as G, furniture as F, build_3d as B

def bnds(name):
    m = trimesh.util.concatenate(B.OBJECTS[name])
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
 "Work_Desks": union([F.FURNITURE["WORK_DESK_1"]["box"], F.FURNITURE["WORK_DESK_2"]["box"]]),
 "Work_Chairs": union([F.FURNITURE["WORK_CHAIR_1"]["box"], F.FURNITURE["WORK_CHAIR_2"]["box"]]),
 "Printer_Unit": rb(F.FURNITURE["PRINTER_UNIT"]["box"]),
 "Meeting_Table": rb(F.FURNITURE["MEETING_TABLE"]["box"]),
 "Meeting_Chairs": union([F.FURNITURE[f"MEETING_CHAIR_{i}"]["box"] for i in range(1,7)]),
 "Monitor_55": rb(F.FURNITURE["MONITOR_55"]["box"]),
 "Interior_Walls": union(list(G.INNER_WALLS.values())),
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
print('-'*78)
print(f'objects compared: {len(EXPECT)}   worst XY deviation: {worst:.2f} px = {worst*13.2:.1f} mm')
print('RESULT:', 'PASS  (3D XY == 2D MASTER XY)' if not bad else f'FAIL {bad}')
