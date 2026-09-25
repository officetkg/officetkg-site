# -*- coding: utf-8 -*-
"""
GEOGRAPHIC ORIENTATION OF THE MASTER FRAME
==========================================
Established from the compass rose printed on the original sheet, at
source-image pixels x 1119..1168, y 978..1054.

Evidence, measured not assumed:
  * the needle is a plain line through the rose, 1-3 px wide at BOTH ends.
    Neither end carries an arrow head, so the letter is the only cue.
  * upper tip   (1139.5, 978)   - nothing printed above it (scanned y 900..977,
                                  threshold 215, zero ink)
  * lower tip   (1148.0, 1041)
  * an italic serif "N", ink at x 1144..1156, y 1043..1054, sits directly under
    the LOWER tip, touching it.

    => the "N" labels the lower end.  NORTH POINTS DOWN THE PAGE.

  * needle vector, upper tip -> lower tip = (+8.5, +63) px
    => north is 7.7 deg off plan-down, rotated towards plan-right.

Consequences for the MASTER frame (X = plan-right, Y = plan-down, Z = up):
"""
import numpy as np

NEEDLE_TOP    = (1139.5, 978.0)      # source-image px
NEEDLE_BOTTOM = (1148.0, 1041.0)
LABEL_N_AT    = "lower tip"

_v = np.array(NEEDLE_BOTTOM) - np.array(NEEDLE_TOP)
NORTH_IN_PLAN = tuple(np.round(_v/np.linalg.norm(_v), 4))       # (+0.134, +0.991)
NORTH_OFF_PLAN_DOWN_DEG = round(float(np.degrees(np.arctan2(_v[0], _v[1]))), 1)

# Axis mapping.  The small 7.7 deg skew is carried as a note only; all geometry
# stays on the orthogonal MASTER axes, exactly as approved.
UP    = (0, 0, +1)
NORTH = (0, +1, 0)      # MASTER +Y = plan down  = the balcony side
SOUTH = (0, -1, 0)      # MASTER -Y = plan up    = the entrance / corridor side
EAST  = (-1, 0, 0)      # MASTER -X = plan LEFT  = Book Shelf / work desks side
WEST  = (+1, 0, 0)      # MASTER +X = plan RIGHT = kitchen / monitor side

FACING = {
    "balcony":            "NORTH",
    "entrance / corridor":"SOUTH",
    "Book Shelf wall, work desks": "EAST wall (plan left)",
    "kitchen wall, 55 inch monitor": "WEST wall (plan right)",
}

def to_enu(P):
    """MASTER px (x right, y down, z up) -> right-handed ENU px (east, north, up)."""
    P = np.asarray(P, float)
    return np.stack([-P[..., 0], P[..., 1], P[..., 2]], -1)

def camera_basis(bearing_deg, elevation_deg):
    """Right-handed camera basis in ENU.
    bearing = compass bearing of the CAMERA from the building (0 = due north).
    Returns (screen_right, screen_up, toward_eye)."""
    b, e = np.radians(bearing_deg), np.radians(elevation_deg)
    zc = np.array([np.cos(e)*np.sin(b), np.cos(e)*np.cos(b), np.sin(e)])   # target -> eye
    up = np.array([0.0, 0.0, 1.0])
    if elevation_deg > 85:                       # looking (almost) straight down
        up = np.array([-np.sin(b), -np.cos(b), 0.0])   # screen up = away from the camera
    xc = np.cross(up, zc); xc /= np.linalg.norm(xc)
    yc = np.cross(zc, xc)
    return xc, yc, zc

if __name__ == "__main__":
    print(__doc__)
    print(f"  north in plan coords : {NORTH_IN_PLAN}  ({NORTH_OFF_PLAN_DOWN_DEG} deg off plan-down)")
    for k, v in FACING.items(): print(f"  {k:32s} -> {v}")
    print("\n  sanity checks on camera_basis (screen right / screen up):")
    for b, e, note in [(180, 89.5, "TOP, north up"), (0, 30, "camera due NORTH"),
                       (90, 30, "camera due EAST"), (180, 30, "camera due SOUTH")]:
        r, u, _ = camera_basis(b, e)
        nm = lambda v: ("E" if v[0] > .7 else "W" if v[0] < -.7 else
                        "N" if v[1] > .7 else "S" if v[1] < -.7 else
                        "U" if v[2] > .7 else "D" if v[2] < -.7 else "?")
        print(f"    bearing {b:3d} el {e:4.1f}  right={nm(r)}  up={nm(u)}   ({note})")
