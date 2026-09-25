# -*- coding: utf-8 -*-
"""
PHASE 6  --  Z VARIABLES
========================
NOTHING in this file is measured from the plan.  The original sheet carries no
section, no ceiling height and no window head height, so every value here is a
PROVISIONAL VARIABLE, declared in mm and converted to MASTER px with the
provisional 13.2 mm/px working scale.

XY accuracy has priority over height: changing any value below must never
change an X or Y coordinate.
"""
MM_PER_PX = 13.2
def P(mm): return mm / MM_PER_PX          # mm -> MASTER px

# ----------------------------------------------------------------------
# SPECIFIED -- published manufacturer dimensions for the three products the
# client named.  These are NOT provisional in the way the rest of this file
# is: they come from the makers' own specifications, not from reading the
# plan.  They still cannot move an X or a Y of the architecture.
#   meeting table  NISHIKI E-CAD-2190KW   2100 x 900 x 720
#   work chairs    Herman Miller Aeron, size B
#   meeting chairs Herman Miller Setu, 5-star base, armless
# Seat heights are gas-lift adjustable; the value used is a SET POSITION
# inside the published range, noted per key.
# ----------------------------------------------------------------------
SPECIFIED = {                              # mm
    "TABLE_HEIGHT":              720,      # E-CAD-2190KW overall height
    "TABLE_TOP_THICKNESS":        30,      # melamine top, ABS edge
    "TABLE_LEG_W":                60,      # steel pipe 60 x 30, polished
    "TABLE_LEG_D":                30,
    "TABLE_WIRE_BOX_W":          400,      # flip-up wiring box lid -- size assumed
    "TABLE_WIRE_BOX_D":          160,
    "TABLE_WIRE_TRAY_DROP":      110,      # cable tray under the top -- assumed

    "WORK_CHAIR_SEAT":           450,      # Aeron B: adjustable 406-521, set 450
    "WORK_CHAIR_BACK_TOP":      1090,      # Aeron B overall height
    "WORK_CHAIR_ARM_TOP":        680,      # arm pad, set position
    "WORK_CHAIR_BASE_DIA":       658,      # 5-star base, = overall width
    "WORK_CHAIR_CASTOR_DIA":      50,

    "MEETING_CHAIR_SEAT":        460,      # Setu: adjustable 399-551, set 460
    "MEETING_CHAIR_BACK_TOP":    965,      # Setu overall height (950-980 range)
    "MEETING_CHAIR_BASE_DIA":    658,      # 5-star base, = overall width
    "MEETING_CHAIR_CASTOR_DIA":   50,
    "MEETING_CHAIR_SHELL_T":      26,      # one-piece kinematic spine, thin
}

PROVISIONAL = {                            # mm  -- all unverified
    "WALL_HEIGHT":              2450,      # slab-to-slab clear, assumed
    "DOOR_HEIGHT":              2000,
    "ENTRANCE_DOOR_HEIGHT":     2000,
    "WINDOW_HEAD":              2000,      # balcony sash head
    "WINDOW_SILL":                 0,      # full-height (hakidashi) sash
    "DESK_HEIGHT":               720,
    "DESK_TOP_THICKNESS":         25,
    "BOOKSHELF_HEIGHT":         2400,      # photos show it floor-to-ceiling - see README
    "KITCHEN_COUNTER_HEIGHT":    850,
    "KITCHEN_UPPER_BOTTOM":     1500,
    "KITCHEN_UPPER_TOP":        2100,
    "VANITY_HEIGHT":             800,
    "TOILET_PAN_HEIGHT":         400,
    "TOILET_TANK_HEIGHT":        750,
    "HAND_BASIN_HEIGHT":         800,
    "SHOWER_ENCLOSURE_HEIGHT":  2000,
    "WD_HEIGHT":                1000,
    "REFRIGERATOR_HEIGHT":      1800,
    "CLOSET_HEIGHT":            2300,
    "SC_HEIGHT":                2300,
    "PARTITION_PANEL_HEIGHT":   2200,      # movable panels and their pocket
    "PARTITION_RAIL_DROP":        60,      # head track depth below ceiling
    "PRINTER_UNIT_HEIGHT":       700,
    "MONITOR_CENTRE_Z":         1250,
    "MONITOR_SCREEN_W":         1230,      # 55 inch 16:9
    "MONITOR_SCREEN_H":          692,
    "MONITOR_DEPTH":              55,
    "BALCONY_SLAB_DROP":         150,      # balcony FL below interior FL
    "BALCONY_RAILING_HEIGHT":   1200,      # top of the capping, from balcony FL
    "BALCONY_RAILING_BASE":      100,      # upstand / base channel
    "BALCONY_RAILING_GLASS_TOP":1130,      # glass stops under the capping
    "BALCONY_RAILING_CAP":        70,      # flat capping depth
    "BALCONY_POST_PITCH":       1300,      # posts along the run
    "BALCONY_PARTITION_HEIGHT": 2350,      # hedate-ita, floor to soffit in the photos
    "BALCONY_SOFFIT":           2400,
    "DOWNPIPE_DIA":              100,
    "WINDOW_FRAME":               70,      # sash frame member
    "GLASS_THICKNESS":            16,
    "PS_HEIGHT":                2450,
    "COLUMN_HEIGHT":            2450,
    "SLAB_THICKNESS":            200,
}
ALL = {**SPECIFIED, **PROVISIONAL}
globals().update({k: P(v) for k, v in ALL.items()})      # px versions

if __name__ == "__main__":
    print(f"scale 1 px = {MM_PER_PX} mm\n")
    print("SPECIFIED (manufacturer dimensions)")
    for k, v in SPECIFIED.items():
        print(f"  {k:28s} {v:6d} mm = {P(v):8.2f} px")
    print("\nPROVISIONAL (nothing below is measured)")
    for k, v in PROVISIONAL.items():
        print(f"  {k:28s} {v:6d} mm = {P(v):8.2f} px")
