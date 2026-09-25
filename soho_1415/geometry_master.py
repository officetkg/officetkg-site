# -*- coding: utf-8 -*-
"""
OIMACHI TRACKS RESIDENCE (SOHO floor) 1415  --  2D GEOMETRY MASTER
==================================================================
PHASE 3 output.  Pure pixel-coordinate model traced from the original
real-estate floor plan.  NO mm conversion (see PHASE 2/3 decision).

SOURCE RASTER
  file   : 51014ede-image.png   (2436 x 1125, sha256 96f78452d532adee...)
  status : PHASE 2 = NO geometric correction applied.
           Measured line angles in the plan panel are exactly 0.00 deg /
           90.00 deg, i.e. the sheet is a digital PDF render, not a photo
           of paper.  before-image == after-image, bit identical.

COORDINATE SYSTEM  ("MASTER px")
  work  = source_pixel - (240, 120)          # analysis window
  MX    = work_x - 403                       # 403 = west exterior wall, OUTER face
  MY    = work_y - 150                       # 150 = north exterior wall, OUTER face
  origin: top-left corner of the building outline on the sheet (exterior faces)
  X     : right on the sheet
  Y     : down on the sheet

  !! ORIENTATION -- corrected after the compass rose was re-read !!
  The compass "N" sits at the LOWER tip of the needle, so NORTH POINTS DOWN
  THE PAGE (see orientation.py for the pixel evidence).  Therefore:
      MASTER +Y (plan down)  = NORTH   <- the balcony side
      MASTER -Y (plan up)    = SOUTH   <- the entrance / common corridor
      MASTER +X (plan right) = WEST    <- kitchen, 55 inch monitor
      MASTER -X (plan left)  = EAST    <- Book Shelf, work desks
  Every identifier below ("north", "W_shower_east_thick", "run_EAST", ...) is a
  PLAN-RELATIVE name fixed at PHASE 3 and kept so the approved model is not
  churned.  Read them as sheet directions, never as compass directions, and
  take compass directions from orientation.py only.
  unit  : 1 px of the source raster.  NOT converted to mm.

Everything below is in MASTER px.
"""

OX, OY = 403, 150          # work-coord position of the master origin
SRC_WINDOW = (240, 120)    # source -> work offset


def M(wx, wy):
    """work coords -> master coords"""
    return (wx - OX, wy - OY)


def rect(wx0, wy0, wx1, wy1):
    return {"x0": wx0 - OX, "y0": wy0 - OY, "x1": wx1 - OX, "y1": wy1 - OY}


# ----------------------------------------------------------------------
# 1. OUTER_WALLS  --  building envelope, exterior / interior faces
# ----------------------------------------------------------------------
OUTER_WALLS = {
    # outer boundary of the slab/envelope, EXCLUDING the two protruding columns
    "envelope_outline": [          # closed polyline, master px
        M(403, 150), M(726, 150),  # north face, up to the NE column
        M(726, 193),               # NE column notch (column itself is separate)
        M(768, 193),               # east face begins
        M(768, 773),               # east face ends at the SE column
        M(728, 773), M(728, 822),  # SE column notch
        M(403, 822),               # south face
        M(403, 150),
    ],
    "north": {                     # y 150 outer .. inner face varies
        "outer_y": M(0, 150)[1],
        "segments": [
            {"x0": M(413, 0)[0], "x1": M(440, 0)[0], "inner_y": M(0, 156)[1]},
            {"x0": M(440, 0)[0], "x1": M(561, 0)[0], "inner_y": M(0, 153)[1],
             "note": "PS access panel leaf sits in the wall here"},
            {"x0": M(561, 0)[0], "x1": M(590, 0)[0], "inner_y": M(0, 156)[1]},
            {"x0": M(587, 0)[0], "x1": M(634, 0)[0], "inner_y": M(0, 158)[1]},
            {"x0": M(707, 0)[0], "x1": M(726, 0)[0], "inner_y": M(0, 174)[1]},
        ],
        "opening_entrance_door": {"x0": M(637, 0)[0], "x1": M(704, 0)[0]},
    },
    "west": {                      # x 403 outer, intermediate layer line at 412/413
        "outer_x": M(403, 0)[0],
        "layer_line_x": M(412, 0)[0],
        "segments": [
            {"y0": M(0, 230)[1], "y1": M(0, 345)[1], "inner_x": M(416, 0)[0]},
            {"y0": M(0, 345)[1], "y1": M(0, 822)[1], "inner_x": M(418, 0)[0]},
        ],
    },
    "east": {                      # x 768 outer
        "outer_x": M(768, 0)[0],
        "segments": [
            {"y0": M(0, 193)[1], "y1": M(0, 405)[1], "inner_x": M(753, 0)[0]},
            {"y0": M(0, 405)[1], "y1": M(0, 773)[1], "inner_x": M(758, 0)[0]},
        ],
    },
    "south": {                     # y 822 outer
        "outer_y": M(0, 822)[1],
        "layer_line_y": M(0, 815)[1],
        "solid_segment": rect(403, 789, 538, 822),   # thick solid band, west part
        "sash_segment": {"x0": M(534, 0)[0], "x1": M(721, 0)[0]},
    },
}

# ----------------------------------------------------------------------
# 2. COLUMNS  --  grey squares straddling the envelope
# ----------------------------------------------------------------------
COLUMNS = {
    "C_NE": rect(726, 118, 800, 193),
    "C_SE": rect(728, 773, 797, 849),
}

# ----------------------------------------------------------------------
# 3. PS  (pipe shaft, opened from the common corridor - outside the dwelling)
# ----------------------------------------------------------------------
PS = {
    "interior": rect(413, 156, 587, 217),
    "wall_north": rect(413, 150, 598, 156),
    "wall_east": rect(587, 156, 598, 228),
    "wall_south": rect(403, 217, 598, 228),
    "access_panel_north": {"x0": M(440, 0)[0], "x1": M(561, 0)[0],
                           "y": M(0, 153)[1], "note": "leaf line in the north wall"},
}

# ----------------------------------------------------------------------
# 4. INNER_WALLS  --  grey filled partitions
# ----------------------------------------------------------------------
INNER_WALLS = {
    "W_entrance_south":   rect(630, 227, 721, 230),   # entrance hall / kitchen line
    "W_powder_kitchen":   rect(627, 174, 632, 394),   # vertical, powder+toilet vs kitchen
    "W_powder_north":     rect(413, 217, 627, 230),   # = PS south wall, continues east
    "W_powder_south":     rect(484, 337, 627, 342),   # powder room south wall
    "W_shower_east_thin": rect(476, 227, 479, 283),   # jamb of the shower door only
    "W_shower_east_thick":rect(476, 283, 484, 322),   # shower booth east wall
    "W_shower_north":     rect(418, 230, 476, 233),
    "W_shower_south":     rect(418, 318, 476, 322),
    "W_band_shower_clo":  rect(413, 320, 488, 342),   # solid band between shower and Clo.
    "W_closet_side":      rect(509, 342, 512, 387),   # sliver between CLO_2 and toilet
    "W_toilet_west":      rect(511, 342, 517, 408),
    "W_toilet_south":     rect(512, 403, 632, 408),
    "W_hall_south":       rect(632, 402, 758, 407),   # kitchen / LD line (holds LD door)
    "W_pocket_stub":      rect(555, 406, 572, 430),   # stub carrying the partition pocket
    # --- PHASE 5 addendum: two column returns that were present on the sheet but
    #     not yet carried in the PHASE 4 model.  They ADD faces, they do not move
    #     any approved coordinate.  Flagged to the client for acknowledgement.
    # plan-bottom-right column casing: full depth for 8 px, then a 8 px fin
    "W_SEcol_return_head": rect(720, 764, 758, 772),
    "W_SEcol_return_fin":  rect(720, 772, 728, 822),
    "W_NEcol_return":      rect(721, 174, 726, 194),  # plan-top-right column casing
    "W_niche_head":        rect(721, 194, 753, 198),  # wall over the unlabelled niche
}

# ----------------------------------------------------------------------
# 5. STORAGE WALL  (movable partition)  --  MB / LD boundary, L-shaped
#    Drawn CLOSED on the original sheet.  Design state = PARKED / OPEN.
# ----------------------------------------------------------------------
STORAGE_WALL = {
    "run_EAST": {           # east side of Master Bedroom, runs north-south
        "axis": "vertical",
        "pocket": rect(556, 430, 568, 485),        # fixed 戸袋 - panels park here
        "panel_count": 3,
        "panels_closed": [                          # as printed on the sheet
            rect(563, 485, 567, 538),               # panel 3 (outer track)
            rect(559, 534, 563, 589),               # panel 2
            rect(556, 584, 559, 639),               # panel 1 (inner track)
        ],
        "panels_parked": [                          # design state: stacked in pocket
            rect(563, 430, 567, 485),
            rect(559, 430, 563, 485),
            rect(556, 430, 559, 485),
        ],
        "clear_opening_when_open": {"x": M(562, 0)[0],
                                    "y0": M(0, 485)[1], "y1": M(0, 639)[1]},
        "rail_line": {"x": M(562, 0)[0], "y0": M(0, 430)[1], "y1": M(0, 639)[1]},
        "joint_ticks_y": [M(0, 536)[1], M(0, 586)[1]],
    },
    "run_SOUTH": {          # south side of Master Bedroom, runs east-west
        "axis": "horizontal",
        "pocket": rect(419, 640, 466, 652),
        "panel_count": 2,
        "panels_closed": [
            rect(466, 643, 510, 648),               # panel A
            rect(510, 639, 557, 643),               # panel B
        ],
        "panels_parked": [
            rect(419, 640, 466, 644),
            rect(419, 646, 466, 650),
        ],
        "clear_opening_when_open": {"y": M(0, 645)[1],
                                    "x0": M(466, 0)[0], "x1": M(557, 0)[0]},
        "rail_line": {"y": M(0, 645)[1], "x0": M(419, 0)[0], "x1": M(557, 0)[0]},
        "joint_ticks_x": [M(510, 0)[0]],
    },
    "corner": rect(553, 632, 568, 652),
    "state": "OPEN / PARKED  (panels stored, opening permanently clear)",
}

# ----------------------------------------------------------------------
# 6. FIXTURES  /  CASEWORK
# ----------------------------------------------------------------------
SC          = rect(603, 176, 629, 228)      # shoe closet, bi-fold doors facing east
SHOWER      = rect(418, 233, 476, 318)      # shower booth (inside faces)
WD          = rect(487, 280, 538, 337)      # washer/dryer space (dashed on sheet)
VANITY      = rect(540, 293, 625, 337)
VANITY_BOWL = rect(563, 300, 603, 327)
CLOSETS     = {"CLO_1": rect(420, 342, 449, 387),
               "CLO_2": rect(450, 342, 509, 387)}
TOILET      = {"room": rect(517, 342, 627, 403),
               "bowl_shape": "oval / U-shaped pan, tank to the WEST",
               "bowl": rect(537, 355, 572, 388),      # bounding box of the oval
               "tank": rect(518, 357, 536, 388),
               "upper_cabinet_dashed": rect(517, 342, 538, 405),
               "hand_basin_shape": "quarter-round corner basin",
               "hand_basin": rect(590, 386, 620, 403)}
KITCHEN     = {"room_ref": rect(632, 230, 753, 401),   # reference extent, not a traced line
               "counter": rect(703, 230, 753, 347),
               "hob": rect(708, 244, 745, 267),
               "sink_unit": rect(724, 288, 753, 346),
               "sink_bowl_shape": "rounded rectangle",
               "sink_bowl": rect(729, 293, 750, 330)}
REFRIGERATOR = rect(699, 350, 752, 398)     # "R", dashed
BOOK_SHELF  = {"body": rect(418, 651, 440, 790),
               "shelf_lines_y": [M(0, y)[1] for y in (680, 707, 734, 761)],
               "open_face": "east (towards Living Dining)"}
ENTRANCE_NICHE_UNIDENTIFIED = rect(721, 198, 753, 228)   # beige, unlabelled on sheet

# ----------------------------------------------------------------------
# 7. WINDOWS
# ----------------------------------------------------------------------
WINDOWS = {
    "W_BALCONY": {
        "opening": rect(534, 816, 721, 822),
        "mullion_x": M(602, 0)[0],
        "leaf_west": {"x0": M(539, 0)[0], "x1": M(602, 0)[0]},
        "leaf_east": {"x0": M(602, 0)[0], "x1": M(718, 0)[0]},
        "dotted_leaf_line": {"y": M(0, 819)[1],
                             "x0": M(601, 0)[0], "x1": M(664, 0)[0]},
        "note": "the ONLY glazed opening in the dwelling",
    },
}
MARK_TRIANGLE = {"apex": M(570, 814), "top_y": M(0, 806)[1],
                 "x0": M(563, 0)[0], "x1": M(578, 0)[0],
                 "note": "black triangle on the sash - meaning UNRESOLVED"}

# ----------------------------------------------------------------------
# 8. DOORS   (hinge point, leaf length, swing)
# ----------------------------------------------------------------------
DOORS = {
    "D_ENTRANCE": {
        "wall": "north exterior", "opening": {"x0": M(637, 0)[0], "x1": M(704, 0)[0],
                                              "y": M(0, 152)[1]},
        "hinge": M(704, 152), "leaf": 68, "type": "single hinged",
        "swing": "OUTWARD (north, into the common corridor); leaf sweeps west",
        "open_leaf_to": M(704, 84), "closed_leaf_to": M(637, 152),
    },
    "D_SHOWER": {
        "wall": "shower booth east", "opening": {"x": M(478, 0)[0],
                                                 "y0": M(0, 230)[1], "y1": M(0, 283)[1]},
        "hinge": M(478, 230), "leaf": 52, "type": "single hinged",
        "swing": "INTO the shower booth (west)",
        "open_leaf_to": M(426, 230), "closed_leaf_to": M(478, 283),
    },
    "D_POWDER": {
        "wall": "powder room east", "opening": {"x": M(629, 0)[0],
                                                "y0": M(0, 230)[1], "y1": M(0, 285)[1]},
        "hinge": M(628, 230), "leaf": 55, "type": "single hinged",
        "swing": "EAST, into the kitchen",
        "open_leaf_to": M(683, 230), "closed_leaf_to": M(628, 285),
    },
    "D_TOILET": {
        "wall": "toilet east", "opening": {"x": M(630, 0)[0],
                                           "y0": M(0, 343)[1], "y1": M(0, 392)[1]},
        "hinge": M(631, 392), "leaf": 49, "type": "single hinged",
        "swing": "EAST, into the kitchen",
        "open_leaf_to": M(680, 392), "closed_leaf_to": M(631, 343),
    },
    "D_LD": {
        "wall": "kitchen / Living Dining", "opening": {"y": M(0, 403)[1],
                                                       "x0": M(632, 0)[0], "x1": M(694, 0)[0]},
        "hinge": M(694, 403), "leaf": 62, "type": "single hinged",
        "swing": "SOUTH, into the Living Dining; leaf sweeps west",
        "open_leaf_to": M(700, 465), "closed_leaf_to": M(632, 403),
    },
    "D_SC": {
        "wall": "shoe closet east face", "opening": {"x": M(629, 0)[0],
                                                     "y0": M(0, 178)[1], "y1": M(0, 227)[1]},
        "type": "bi-fold, 2 chevrons", "swing": "EAST into the entrance hall",
    },
    "D_CLO_1": {"opening": {"y": M(0, 387)[1], "x0": M(420, 0)[0], "x1": M(449, 0)[0]},
                "type": "bi-fold (1 V)", "swing": "SOUTH into the Master Bedroom"},
    "D_CLO_2": {"opening": {"y": M(0, 387)[1], "x0": M(450, 0)[0], "x1": M(509, 0)[0]},
                "type": "bi-fold (2 V)", "swing": "SOUTH into the Master Bedroom"},
}

# ----------------------------------------------------------------------
# 9. BALCONY  --  traced verbatim.  Side partitions are PARALLEL (dx/dy = -0.36),
#    i.e. a raked parallelogram, NOT a trapezoid and NOT symmetric.
# ----------------------------------------------------------------------
BALCONY = {
    "north_edge_y": M(0, 822)[1],
    "north_edge_x": (M(403, 0)[0], M(728, 0)[0]),
    # least-squares fits over 55-57 sampled rows, residual sd 0.31-0.32 px
    "side_west": {"vertical_stub": [M(420, 822), M(420, 847)],
                  "raked": [M(419.3, 847), M(384.4, 946)],
                  "fit": "x = -0.3527*y + 718.03  (work coords)",
                  "angle_from_vertical_deg": 19.43,
                  "pivot_circle_at": M(420, 848)},
    "side_east": {"from_column_corner": M(773.9, 849),
                  "raked": [M(773.9, 849), M(739.4, 946)],
                  "fit": "x = -0.3561*y + 1076.20  (work coords)",
                  "angle_from_vertical_deg": 19.60},
    "sides_are_parallel": True,
    "shape": "PARALLELOGRAM (both side partitions raked the same way). "
             "NOT a trapezoid, NOT symmetric, NOT rectangular, NOT curved.",
    "railing": rect(368, 908, 765, 930),
    "railing_inner_lines_y": [M(0, 914)[1], M(0, 922)[1]],
    "break_symbols_end_y": M(0, 946)[1],
    "note": "railing runs past the unit on both sides; break symbols mark "
            "continuation to the neighbouring balconies.",
}

# ----------------------------------------------------------------------
# 10. ROOM POLYGONS (clear interior, for checking only)
# ----------------------------------------------------------------------
ROOMS = {
    "ENTRANCE_HALL": [M(632, 158), M(721, 158), M(721, 198), M(753, 198),
                      M(753, 230), M(632, 230)],
    "POWDER_ROOM":   [M(418, 230), M(627, 230), M(627, 337), M(484, 337),
                      M(484, 322), M(476, 322), M(476, 230)],
    "SHOWER":        [M(418, 233), M(476, 233), M(476, 318), M(418, 318)],
    "TOILET":        [M(517, 342), M(627, 342), M(627, 403), M(517, 403)],
    "KITCHEN":       [M(632, 230), M(753, 230), M(753, 401), M(632, 401)],
    "MASTER_BEDROOM":[M(418, 387), M(511, 387), M(511, 408), M(556, 408),
                      M(556, 639), M(557, 645), M(418, 645)],
    "LIVING_DINING": [M(562, 408), M(758, 408), M(758, 773), M(728, 773),
                      M(728, 816), M(418, 816), M(418, 645), M(557, 645),
                      M(562, 639)],
}

ALL = dict(OUTER_WALLS=OUTER_WALLS, COLUMNS=COLUMNS, PS=PS,
           INNER_WALLS=INNER_WALLS, STORAGE_WALL=STORAGE_WALL,
           SC=SC, SHOWER=SHOWER, WD=WD, VANITY=VANITY, VANITY_BOWL=VANITY_BOWL,
           CLOSETS=CLOSETS, TOILET=TOILET, KITCHEN=KITCHEN,
           REFRIGERATOR=REFRIGERATOR, BOOK_SHELF=BOOK_SHELF,
           ENTRANCE_NICHE_UNIDENTIFIED=ENTRANCE_NICHE_UNIDENTIFIED,
           WINDOWS=WINDOWS, MARK_TRIANGLE=MARK_TRIANGLE, DOORS=DOORS,
           BALCONY=BALCONY, ROOMS=ROOMS)

if __name__ == "__main__":
    import json
    print(json.dumps(ALL, ensure_ascii=False, indent=1))
