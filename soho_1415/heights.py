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

PROVISIONAL = {                            # mm  -- all unverified
    "WALL_HEIGHT":              2450,      # slab-to-slab clear, assumed
    "DOOR_HEIGHT":              2000,
    "ENTRANCE_DOOR_HEIGHT":     2000,
    "WINDOW_HEAD":              2000,      # balcony sash head
    "WINDOW_SILL":                 0,      # full-height (hakidashi) sash
    "DESK_HEIGHT":               720,
    "DESK_TOP_THICKNESS":         25,
    "WORK_CHAIR_SEAT":           450,
    "WORK_CHAIR_BACK_TOP":      1050,
    "TABLE_HEIGHT":              720,
    "TABLE_TOP_THICKNESS":        30,
    "MEETING_CHAIR_SEAT":        440,
    "MEETING_CHAIR_BACK_TOP":    830,
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
globals().update({k: P(v) for k, v in PROVISIONAL.items()})   # px versions

if __name__ == "__main__":
    print(f"scale 1 px = {MM_PER_PX} mm     ALL VALUES PROVISIONAL\n")
    for k, v in PROVISIONAL.items():
        print(f"  {k:26s} {v:6d} mm = {P(v):8.2f} px")
