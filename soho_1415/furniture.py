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

SPECIFIED PRODUCTS (client's choice, published maker dimensions)
  MEETING_TABLE   NISHIKI E-CAD-2190KW   2100 x 900 x H720
                  angular top, walnut, polished 4-leg frame, wiring box
  WORK_CHAIR_1/2  Herman Miller Aeron, size B      658 W x 598 D x 1090 H
  MEETING_CHAIR_1..6
                  Herman Miller Setu, 5-star base  658 W x 658 D x  965 H
  existing Book Shelf  -> reused as-is
  storage wall         -> OPEN / PARKED throughout
"""
from geometry_master import M, rect, OX, OY

MM_PER_PX = 13.2
def mm(v): return round(v * MM_PER_PX)

FURNITURE = {
    # ------------------------------------------------ Master Bedroom zone
    "WORK_DESK_1":  {"box": rect(418, 408, 471, 514), "size_mm": (700, 1400),
                     "note": "worktop against the plan-left (EAST) wall, user faces east"},
    "WORK_DESK_2":  {"box": rect(418, 517, 471, 623), "size_mm": (700, 1400),
                     "note": "in line with DESK_1, continuous 2.8 m run on the same "
                             "EAST wall.  The pair moved 170 mm plan-up when the "
                             "meeting table grew to 2100: that keeps the Aeron at "
                             "DESK_2 clear in Y of the Setu at the table's EAST end, "
                             "so the 900 mm pull-out behind it survives."},
    "WORK_CHAIR_1": {"box": rect(471, 446, 516, 496), "size_mm": (594, 660),
                     "product": "Herman Miller Aeron, size B",
                     "product_mm": (658, 598, 1090),
                     "note": "depth 598 runs EAST-WEST (the user faces east), "
                             "width 658 runs NORTH-SOUTH; centred on DESK_1"},
    "WORK_CHAIR_2": {"box": rect(471, 545, 516, 595), "size_mm": (594, 660),
                     "product": "Herman Miller Aeron, size B",
                     "product_mm": (658, 598, 1090),
                     "note": "as CHAIR_1, centred on DESK_2"},
    "PRINTER_UNIT": {"box": rect(517, 410, 555, 444), "size_mm": (500, 450),
                     "note": "small printer on a low unit, in the plan top-right "
                             "(SOUTH-WEST) nook of the bedroom zone, against the "
                             "storage-wall pocket stub"},

    # ------------------------------------------------ Living Dining zone
    "MEETING_TABLE":   {"box": rect(599, 645, 758, 713), "size_mm": (2100, 900),
                        "product": "NISHIKI E-CAD-2190KW",
                        "product_mm": (2100, 900, 720),
                        "note": "long axis runs EAST-WEST, FLUSH AGAINST THE MONITOR "
                                "WALL: its WEST end sits on the inner face at x=355, "
                                "directly under the 55 inch screen.  The screen's "
                                "bottom edge is at 904 mm and the table top at 720 mm, "
                                "so 184 mm of wall shows between them and the screen "
                                "is never fouled.  The LD bay is 2587 mm between the "
                                "partition line and that wall and the table is 2100 mm, "
                                "so the 488 mm that is left now sits at the EAST end "
                                "instead of as a 792 mm aisle at the west."},
    "MEETING_CHAIR_1": {"box": rect(599, 595, 649, 645), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},
    "MEETING_CHAIR_2": {"box": rect(652, 595, 702, 645), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},
    "MEETING_CHAIR_3": {"box": rect(704, 595, 754, 645), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},
    "MEETING_CHAIR_4": {"box": rect(599, 713, 649, 763), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},
    "MEETING_CHAIR_5": {"box": rect(652, 713, 702, 763), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},
    "MEETING_CHAIR_6": {"box": rect(704, 713, 754, 763), "size_mm": (660, 660),
                        "product": "Herman Miller Setu, 5-star base"},

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
    "LD south open area (plan top)":   {"zone": rect(562, 408, 758, 595), "min_mm": 1200},
    # The west aisle no longer exists: the table is flush against that wall.
    # What is left is the 488 mm gap at the EAST end of the table, and the
    # indirect route through the two permanently open storage-wall openings.
    "east of meeting table -> north": {"zone": rect(562, 595, 599, 763), "min_mm": 450},
    "MB <-> LD, west partition gap":   {"zone": rect(556, 485, 572, 605), "min_mm": 600},
    "MB <-> north zone, north gap":    {"zone": rect(466, 636, 557, 660), "min_mm": 900},
    "work chair 1 pull-out":           {"zone": rect(471, 446, 700, 496), "min_mm": 900},
    "work chair 2 pull-out":           {"zone": rect(471, 545, 700, 595), "min_mm": 900},
    "meeting chair pull-out, south":   {"zone": rect(599, 545, 754, 595), "min_mm": 550},
    "meeting chair pull-out, north":   {"zone": rect(599, 763, 754, 816), "min_mm": 550},
    "Clo. bi-fold door swing":         {"zone": rect(420, 387, 509, 405), "min_mm": 200},
    "Book Shelf access":               {"zone": rect(440, 651, 500, 790), "min_mm": 650},
    "balcony sash access":             {"zone": rect(534, 763, 721, 816), "min_mm": 700},
    "north zone, east of meeting":     {"zone": rect(440, 652, 599, 816), "min_mm": 900},
    "kitchen / toilet / powder":       {"zone": rect(632, 230, 753, 401), "min_mm": 750},
}

if __name__ == "__main__":
    print(f"scale: 1 px = {MM_PER_PX} mm\n")
    for k, v in FURNITURE.items():
        b = v["box"]
        print(f'{k:18s} MASTER x {b["x0"]:4d}..{b["x1"]:4d}  y {b["y0"]:4d}..{b["y1"]:4d}'
              f'   = {mm(b["x1"]-b["x0"]):5d} x {mm(b["y1"]-b["y0"]):5d} mm'
              f'   {v.get("product","")}')
