# -*- coding: utf-8 -*-
"""
PHASE 5  --  FURNITURE LAYOUT
=============================
Architectural XY is LOCKED (2D GEOMETRY APPROVED). Nothing in
geometry_master.py is moved by this file; only furniture is added.

WORKING SCALE (provisional, derived in a separate calibration step)
-------------------------------------------------------------------
  1 px = 13.2 mm      (1 m = 75.76 px)      +/- 5 %
  no certain linear dimension exists on the sheet, so the scale is the
  convergence of 11 standard-fixture checks (median 13.25 mm/px,
  IQR 13.19-13.30) and the wall-centre area check against 40.76 m2
  (13.17-13.22 mm/px).  Used ONLY to size furniture.
  px remains the authoritative unit for all architecture.

PROGRAM
  ORIENTATION: north is plan-DOWN (see orientation.py).  The balcony faces
  NORTH; the entrance is on the SOUTH side; plan-right is WEST.

  Master Bedroom zone  -> 2 permanent workstations
  Living Dining zone   -> 6-seat meeting table + 55" monitor
  existing Book Shelf  -> reused as-is
  storage wall         -> OPEN / PARKED throughout
"""
from geometry_master import M, rect, OX, OY

MM_PER_PX = 13.2
def mm(v): return round(v * MM_PER_PX)

FURNITURE = {
    # ------------------------------------------------ Master Bedroom zone
    "WORK_DESK_1":  {"box": rect(418, 420, 471, 526), "size_mm": (700, 1400),
                     "note": "worktop against the plan-left (EAST) wall, user faces east"},
    "WORK_DESK_2":  {"box": rect(418, 530, 471, 636), "size_mm": (700, 1400),
                     "note": "in line with DESK_1, continuous 2.8 m run on the same EAST wall"},
    "WORK_CHAIR_1": {"box": rect(471, 448, 520, 497), "size_mm": (650, 650),
                     "note": "task chair"},
    "WORK_CHAIR_2": {"box": rect(471, 558, 520, 607), "size_mm": (650, 650),
                     "note": "task chair"},
    "PRINTER_UNIT": {"box": rect(517, 410, 555, 444), "size_mm": (500, 450),
                     "note": "small printer on a low unit, in the plan top-right "
                             "(SOUTH-WEST) nook of the bedroom zone, against the "
                             "storage-wall pocket stub"},

    # ------------------------------------------------ Living Dining zone
    "MEETING_TABLE":   {"box": rect(562, 650, 698, 718), "size_mm": (1800, 900),
                        "note": "long axis runs EAST-WEST; its plan-right (WEST) end "
                                "faces the monitor wall; "
                                "sits in the widest part of the opened-up volume, "
                                "straddling the south storage-wall line, in the "
                                "daylight from the balcony"},
    "MEETING_CHAIR_1": {"box": rect(562, 605, 607, 650), "size_mm": (594, 594)},
    "MEETING_CHAIR_2": {"box": rect(607, 605, 652, 650), "size_mm": (594, 594)},
    "MEETING_CHAIR_3": {"box": rect(653, 605, 698, 650), "size_mm": (594, 594)},
    "MEETING_CHAIR_4": {"box": rect(562, 718, 607, 763), "size_mm": (594, 594)},
    "MEETING_CHAIR_5": {"box": rect(607, 718, 652, 763), "size_mm": (594, 594)},
    "MEETING_CHAIR_6": {"box": rect(653, 718, 698, 763), "size_mm": (594, 594)},

    "MONITOR_55":   {"box": rect(754, 637, 758, 730), "size_mm": (1230, 55),
                     "note": "55 inch 16:9, wall mounted on the plan-right (WEST) wall, "
                             "screen centre aligned with the meeting table axis"},
}

# rows named by COMPASS direction (plan top = south, plan bottom = north)
SEAT_ROWS = {"south": ["MEETING_CHAIR_1","MEETING_CHAIR_2","MEETING_CHAIR_3"],
             "north": ["MEETING_CHAIR_4","MEETING_CHAIR_5","MEETING_CHAIR_6"]}

# ----------------------------------------------------------------------
# circulation / clearance routes that must stay open (work px)
# ----------------------------------------------------------------------
CLEARANCES = {
    "entrance (SOUTH) -> LD":          {"zone": rect(632, 408, 758, 500), "min_mm": 800},
    "LD south open area (plan top)":   {"zone": rect(562, 408, 758, 605), "min_mm": 1200},
    "west aisle, LD -> north zone":    {"zone": rect(698, 408, 758, 764), "min_mm": 750},
    "MB <-> LD, west partition gap":   {"zone": rect(556, 485, 572, 605), "min_mm": 600},
    "MB <-> north zone, north gap":    {"zone": rect(466, 636, 557, 660), "min_mm": 900},
    "work chair 1 pull-out":           {"zone": rect(471, 448, 700, 497), "min_mm": 900},
    "work chair 2 pull-out":           {"zone": rect(471, 558, 700, 605), "min_mm": 900},
    "meeting chair pull-out, south":   {"zone": rect(562, 560, 698, 605), "min_mm": 550},
    "meeting chair pull-out, north":   {"zone": rect(562, 763, 698, 816), "min_mm": 550},
    "Clo. bi-fold door swing":         {"zone": rect(420, 387, 509, 405), "min_mm": 200},
    "Book Shelf access":               {"zone": rect(440, 651, 500, 790), "min_mm": 650},
    "balcony sash access":             {"zone": rect(534, 763, 721, 816), "min_mm": 700},
    "north zone, east of meeting":     {"zone": rect(440, 652, 562, 816), "min_mm": 900},
    "kitchen / toilet / powder":       {"zone": rect(632, 230, 753, 401), "min_mm": 750},
}

if __name__ == "__main__":
    print(f"scale: 1 px = {MM_PER_PX} mm\n")
    for k, v in FURNITURE.items():
        b = v["box"]
        print(f'{k:18s} MASTER x {b["x0"]:4d}..{b["x1"]:4d}  y {b["y0"]:4d}..{b["y1"]:4d}'
              f'   = {mm(b["x1"]-b["x0"]):5d} x {mm(b["y1"]-b["y0"]):5d} mm')
