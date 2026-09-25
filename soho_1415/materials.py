# -*- coding: utf-8 -*-
"""
PHASE 9  --  MATERIALS

Albedo only, sRGB 0-255, taken from the listing photos and from the brief.
No invented finishes, no styling beyond what the photos and the brief state.

brief: existing floor = light timber, faithful to the photos / walls = existing
white to light neutral / Book Shelf faithful to the photos / work desks natural
to medium oak / meeting table medium oak or walnut / matte black metal, sparing
/ meeting chairs black, charcoal or dark greige.
"""
PALETTE = {
 # --- shell -------------------------------------------------------------
 "Floor_Slab":                 (198, 174, 144),   # light oak, photo-matched
 "Ceiling_Slab":               (246, 245, 242),   # flat white plaster
 "Ceiling_Coffer":             (243, 242, 239),   # dropped perimeter band
 "Downlights":                 (255, 250, 238),   # warm white aperture
 "Exterior_Walls":             (238, 236, 231),   # warm white
 "Interior_Walls":             (240, 238, 233),
 "Columns":                    (236, 234, 229),
 "PS":                         (226, 224, 220),
 # --- openings ----------------------------------------------------------
 "Windows":                    ( 46,  46,  48),   # matte black aluminium sash
 "Window_Glass":               (188, 202, 208),
 "Entrance":                   (210, 188, 158),   # oak door leaf + shoe closet
 # --- wet areas and kitchen --------------------------------------------
 "Shower":                     (232, 234, 234),
 "WD":                         (228, 228, 228),
 "Powder_Room_Fixtures":       (242, 242, 240),
 "Toilet":                     (244, 244, 242),
 "Kitchen":                    (226, 222, 214),
 "Refrigerator":               (224, 224, 224),
 "Closets":                    (236, 232, 226),
 # --- joinery -----------------------------------------------------------
 "Book_Shelf":                 (214, 194, 166),   # pale oak, open grid
 "Storage_Wall_Pocket":        (234, 230, 224),
 "Storage_Wall_Parked_Panels": (205, 180, 152),   # photo: light oak sliding panel
 "Storage_Wall_Rail":          (230, 228, 223),   # photo: light head, 1.2x the
                                                  # ceiling luma -- NOT a black track
 # --- balcony -----------------------------------------------------------
 "Balcony_Floor":              (176, 176, 172),
 "Balcony_Railing":            ( 52,  52,  54),   # dark capping, posts, base
 "Balcony_Glass":              (196, 208, 206),
 "Balcony_Partitions":         (110,  50,  60),   # maroon hedate-ita
 "Downpipe":                   (222, 216, 202),
 # --- furniture ---------------------------------------------------------
 "Work_Desks":                 (196, 168, 130),   # natural oak
 "Work_Chairs":                ( 48,  48,  52),   # Aeron, graphite Pellicle
 "Work_Chair_Bases":           (176, 178, 181),   # polished aluminium
 "Printer_Unit":               (226, 226, 226),
 "Meeting_Table":              (106,  76,  56),   # E-CAD walnut top
 "Table_Frame":                (188, 190, 193),   # polished steel pipe
 "Table_Wirebox":              ( 58,  58,  60),   # wiring box lid + tray
 "Meeting_Chairs":             ( 58,  57,  60),   # Setu, graphite shell
 "Meeting_Chair_Bases":        (176, 178, 181),   # polished aluminium
 "Monitor_55":                 ( 26,  26,  28),
 # --- decoration (brief's permitted list only) ---------------------------
 "Laptops":                    (168, 170, 173),   # aluminium
 "Laptop_Screens":             ( 34,  34,  38),
 "Desk_Kit":                   (222, 221, 218),
 "Paper":                      (248, 246, 240),
 "Books":                      (176, 160, 140),   # varied by texture
 "Plant_Pots":                 (214, 208, 198),
 "Plant_Foliage":              ( 88, 106,  74),
}
CLAY = {k: (206, 203, 197) for k in PALETTE}
CLAY["Ceiling_Slab"] = (214, 212, 208)
CLAY["Ceiling_Coffer"] = (208, 206, 202)
CLAY["Downlights"] = (250, 246, 236)
for _k in ("Laptops","Laptop_Screens","Desk_Kit","Paper","Books",
           "Plant_Pots","Plant_Foliage"): CLAY[_k] = (200, 198, 194)
CLAY.update({"Window_Glass": (198, 210, 216), "Balcony_Glass": (200, 212, 210),
             "Windows": (92, 92, 94), "Balcony_Railing": (96, 96, 98),
             "Monitor_55": (70, 70, 72), "Storage_Wall_Rail": (214,212,208),
             "Storage_Wall_Parked_Panels": (150, 190, 150),
             "Storage_Wall_Pocket": (170, 200, 170)})
