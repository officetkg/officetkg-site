# -*- coding: utf-8 -*-
"""
PHASE 9  --  ARCHITECTURAL LIGHTING

SOURCE AND STATUS
-----------------
The marketing sheet carries NO reflected ceiling plan.  Everything in this file
is read from the listing photos alone, so it is PROVISIONAL and deliberately
kept out of geometry_master.py: the approved architectural XY is untouched.

What the photos show (LD_1, LD_3, BAL_3, KIT, PWD, WC):
  * a coffered ceiling: a raised centre panel with a DROPPED PERIMETER BAND
    running round the living zone
  * small recessed downlights set in that dropped band, placed in PAIRS
  * more downlights in the kitchen and the inner hall
  * no pendants, no cove uplighting, no decorative fittings
  * a recessed air-conditioning unit near the window head

The brief: "base it on the building's own lighting in the photos, daylight led,
no unnatural added lighting".  Nothing here is invented beyond the pitch at
which the pairs repeat, which the photos cannot resolve exactly.
"""
from heights import MM_PER_PX as MM
def P(mm): return mm / MM

COFFER_DROP   = P(120)      # perimeter band below the main ceiling
COFFER_BAND   = P(450)      # band width
DL_DIA        = P(100)      # downlight aperture
DL_PAIR_GAP   = P(180)      # centres within a pair
DL_PITCH      = P(1750)     # pair to pair along a band
DL_LUMENS     = 1.18        # relative; daylight stays the primary source
DL_CONE       = 0.62        # cos of the half angle of the beam

# living zone ceiling extent (interior faces, MASTER px)
ZONE = dict(x0=15, x1=355, y0=252, y1=666)

def band_centreline():
    h = COFFER_BAND/2
    return dict(west=ZONE["x1"]-h, east=ZONE["x0"]+h,
                north=ZONE["y1"]-h, south=ZONE["y0"]+h)

def pairs_along(a0, a1, pitch=None):
    """centres of each PAIR along a run, kept clear of the corners."""
    pitch = pitch or DL_PITCH
    span = a1 - a0
    n = max(1, int(round(span/pitch)))
    step = span/n
    return [a0 + step*(i + .5) for i in range(n)]

def luminaires():
    """[(x, y, z_of_aperture, kind)] in MASTER px, aperture facing down."""
    c = band_centreline()
    out = []
    g = DL_PAIR_GAP/2
    for y in pairs_along(ZONE["y0"]+COFFER_BAND, ZONE["y1"]-COFFER_BAND):
        for x in (c["east"], c["west"]):
            out += [(x, y-g, "living"), (x, y+g, "living")]
    for x in pairs_along(ZONE["x0"]+COFFER_BAND*1.6, ZONE["x1"]-COFFER_BAND*1.6):
        for y in (c["south"], c["north"]):
            out += [(x-g, y, "living"), (x+g, y, "living")]
    # kitchen and inner hall, from the KIT / HALL / WC photos
    for p in [(330, 110), (330, 148), (300, 196), (268, 196),
              (300,  60), (268,  60), (150, 120), (120, 120),
              (95, 215), (60, 215)]:
        out.append((p[0], p[1], "service"))
    return out

def summary():
    L = luminaires()
    print(f"coffer: band {COFFER_BAND*MM:.0f} mm wide, dropped {COFFER_DROP*MM:.0f} mm")
    print(f"downlights: {len(L)} total "
          f"({sum(1 for l in L if l[2]=='living')} living zone, "
          f"{sum(1 for l in L if l[2]=='service')} kitchen / hall)")
    print(f"aperture {DL_DIA*MM:.0f} mm, pair gap {DL_PAIR_GAP*MM:.0f} mm, "
          f"pair pitch {DL_PITCH*MM:.0f} mm")
    print("STATUS: photo-derived, PROVISIONAL - the sheet has no reflected ceiling plan")

if __name__ == "__main__":
    summary()
