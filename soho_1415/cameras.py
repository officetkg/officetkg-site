# -*- coding: utf-8 -*-
"""
PHASE 8  --  CAMERAS

The scene is the approved PHASE 6 model, unchanged.  Only the camera moves.

Rules held:
  eye height        1500-1600 mm          (1550 mm for A-D)
  lens              28-35 mm equivalent   (full-frame 36x24)
  vertical lines    exactly vertical - the camera axis is forced horizontal and
                    framing is set with a LENS SHIFT, never by tilting
  banned            fisheye, ultra-wide, 16 mm, any barrel/room-stretching
"""
from heights import MM_PER_PX as MM

def P(mm): return mm / MM
EYE_Z = P(1550)

CAMERAS = {
 "A": dict(name="CAMERA A  balcony side -> entrance",
           eye=(312, 646, EYE_Z), target=(245, 255, EYE_Z),
           focal=32, shift=-0.070, level=True,
           note="stands at the BALCONY END OF THE ROOM, in the west aisle just "
                "inside the sash, and looks SOUTH past the meeting table to the "
                "entrance wall.  It used to stand out on the balcony at y=716, "
                "which put the closed sash between the lens and everything in "
                "the frame: the glass pass then laid a bright 17 % veil over "
                "100 % of the image and washed the entrance end out.  Glass now "
                "covers 0 % of this frame."),
 "B": dict(name="CAMERA B  entrance side -> balcony",
           eye=(296, 272, EYE_Z), target=(238, 672, EYE_Z),
           focal=32, shift=-0.085, level=True,
           note="just inside the living-dining door, looks NORTH to the window"),
 "C": dict(name="CAMERA C  meeting table -> workstations",
           eye=(300, 635, EYE_Z), target=(60, 400, EYE_Z),
           focal=28, shift=-0.075, level=True,
           note="stands behind the north row of meeting chairs and looks "
                "diagonally across to the workstations.  It used to stand at "
                "(322, 545) on the monitor wall, which is now under the table: "
                "with the E-CAD butted flush to that wall there is no floor "
                "there to stand on."),
 "D": dict(name="CAMERA D  workstations -> meeting area",
           eye=(133, 320, EYE_Z), target=(250, 560, EYE_Z),
           focal=28, shift=-0.075, level=True,
           note="behind the desks, looks through the open storage wall"),
 "E": dict(name="CAMERA E  oblique aerial, whole unit",
           eye=(640, 1180, P(9500)), target=(185, 455, P(900)),
           focal=35, shift=0.0, level=False, z_cut=P(1700),
           note="the one view that must tilt: a bird's eye cannot keep verticals "
                "parallel. Walls cut at 1700 mm."),
}

def check():
    """PHASE 8 self-check against the written rules."""
    import numpy as np, math
    import build_3d as B, trimesh
    # per PART, not per group: a group bounding box spans the whole floor plate
    solids = []
    for k, ms in B.OBJECTS.items():
        if k in ("Floor_Slab", "Balcony_Floor", "Windows", "Window_Glass",
                 "Balcony_Glass", "Storage_Wall_Rail", "Balcony_Partitions"): continue
        for m in ms: solids.append((k, m.bounds))
    rows = []
    for k, c in CAMERAS.items():
        e, t = np.array(c["eye"], float), np.array(c["target"], float)
        h_mm = e[2]*MM
        f = c["focal"]
        d = t - e
        pitch = math.degrees(math.atan2(d[2], math.hypot(d[0], d[1])))
        inside = None
        for nm, b in solids:
            if (b[0][0]-2 <= e[0] <= b[1][0]+2 and b[0][1]-2 <= e[1] <= b[1][1]+2
                    and b[0][2]-2 <= e[2] <= b[1][2]+2):
                inside = nm; break
        hfov = 2*math.degrees(math.atan(18.0/f))
        rows.append((k, h_mm, f, hfov, pitch, c["level"], inside))
    print(f'{"cam":4s} {"eye h mm":>9s} {"focal":>6s} {"h.FOV":>7s} {"axis pitch":>11s} '
          f'{"verticals":>10s}  eye inside a solid?')
    ok = True
    for k, h, f, hf, p, lvl, ins in rows:
        vert = "parallel" if lvl else "converge"
        flag = ""
        if k != "E":
            if not (1500 <= h <= 1600): flag += " HEIGHT!"; ok = False
            if not lvl: flag += " TILTED!"; ok = False
        if not (28 <= f <= 35): flag += " LENS!"; ok = False
        if ins: flag += f" IN {ins}!"; ok = False
        print(f'{k:4s} {h:9.0f} {f:6.0f} {hf:6.1f}d {p:10.1f}d {vert:>10s}  '
              f'{ins or "no"}{flag}')
    print("\nRESULT:", "PASS - every camera obeys the PHASE 8 rules" if ok else "FAIL")
    return ok

if __name__ == "__main__":
    check()
