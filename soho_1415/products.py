# -*- coding: utf-8 -*-
"""
SPECIFIED PRODUCTS
==================
The three products the client named, built as real geometry rather than as the
placeholder boxes PHASE 5 used.

  MEETING TABLE   NISHIKI  E-CAD-2190KW
                  2100 W x 900 D x 720 H, angular top, walnut,
                  30 mm melamine top with ABS edge, 60 x 30 steel pipe legs,
                  polished finish, wiring box, adjusters.
  WORK CHAIRS     Herman Miller  Aeron, size B
                  658 W x 598 D x 1090 H, seat 406-521 (set 450),
                  5-star base, graphite.
  MEETING CHAIRS  Herman Miller  Setu, 5-star base, armless
                  658 W x 658 D x 950-980 H, seat 399-551 (set 460),
                  one-piece kinematic-spine shell, graphite.

RULES THIS FILE KEEPS
  * XY comes from furniture.py, which comes from the approved layout.  Nothing
    here invents a plan coordinate: every part is placed relative to the rect
    it is given, and the union of each product's parts fills that rect.
  * Published overall dimensions drive the envelope.  Anything the makers do
    not publish (the exact leg inset, the wiring-box lid size, the arc of the
    Aeron back) is an approximation and is marked as one; it never changes the
    envelope.
  * The architecture is untouched.
"""
import numpy as np, trimesh, math
import heights as H

P = H.P


# ----------------------------------------------------------------- primitives
def _box(x0, y0, x1, y1, z0, z1):
    m = trimesh.creation.box(extents=(x1-x0, y1-y0, z1-z0))
    m.apply_translation(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    return m


def _cyl(cx, cy, z0, z1, r, sections=16):
    m = trimesh.creation.cylinder(radius=r, height=z1-z0, sections=sections)
    m.apply_translation((cx, cy, (z0+z1)/2))
    return m


def _spoke(cx, cy, ang, length, w_hub, w_tip, z0, z1):
    """One arm of a star base: a flat bar tapering from the hub to the castor."""
    v = np.array([
        [0, -w_hub/2, z0], [0, w_hub/2, z0], [length, w_tip/2, z0], [length, -w_tip/2, z0],
        [0, -w_hub/2, z1], [0, w_hub/2, z1], [length, w_tip/2, z1], [length, -w_tip/2, z1]])
    f = [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
         [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
         [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]]
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    m.apply_transform(trimesh.transformations.rotation_matrix(ang, (0, 0, 1)))
    m.apply_translation((cx, cy, 0))
    return m


def star_base(cx, cy, dia, castor_dia, top_z, forward):
    """5-star base + castors + gas cylinder on a circle of the given diameter.

    A real 5-star base is a circle, not a rectangle: with one arm pointing
    straight back its footprint is 1.809 R deep by 1.902 R wide.  For a 658 mm
    base that is 595 x 626 mm, which is why both chairs sit INSIDE their
    published rectangular envelope rather than filling it.
    """
    R = dia/2
    cr = castor_dia/2
    hub_z0, hub_z1 = P(55), P(95)
    a0 = math.atan2(forward[1], forward[0]) + math.pi      # one arm to the rear
    parts = [_cyl(cx, cy, hub_z0, hub_z1, P(52), 24)]
    reach = R - cr
    for i in range(5):
        a = a0 + math.radians(i*72)
        parts.append(_spoke(cx, cy, a, reach, P(96), P(46), hub_z0, hub_z1))
        parts.append(_cyl(cx + math.cos(a)*reach, cy + math.sin(a)*reach,
                          0.0, P(52), cr, 12))
    parts.append(_cyl(cx, cy, hub_z1, top_z, P(38), 16))   # gas lift
    return parts


# --------------------------------------------------------------------- table
def meeting_table(r):
    """NISHIKI E-CAD-2190KW -> (top, frame, wiring) mesh lists.

    Published: 2100 x 900 x 720, 30 mm top, 60 x 30 polished steel pipe legs,
    wiring box, adjusters.  The leg inset from the ends, the lid size and the
    under-top cable tray are NOT published; the values below are stated
    assumptions and sit wholly inside the 2100 x 900 envelope.
    """
    TH, TT = H.TABLE_HEIGHT, H.TABLE_TOP_THICKNESS
    x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
    top = [_box(x0, y0, x1, y1, TH-TT, TH)]

    lw, ld = H.TABLE_LEG_W, H.TABLE_LEG_D           # 60 x 30 pipe
    inset_end, inset_side = P(150), P(90)           # ASSUMED
    frame = []
    xs = (x0+inset_end, x1-inset_end-lw)
    ys = (y0+inset_side, y1-inset_side-ld)
    for lx in xs:
        for ly in ys:
            frame.append(_box(lx, ly, lx+lw, ly+ld, 0, TH-TT))
        frame.append(_box(lx, ys[0], lx+lw, ys[1]+ld,                 # end frame rail
                          TH-TT-P(120), TH-TT-P(120)+P(40)))
    frame.append(_box(xs[0], (y0+y1)/2-P(20), xs[1]+lw, (y0+y1)/2+P(20),
                      TH-TT-P(90), TH-TT-P(50)))                      # centre stretcher

    cx, cy = (x0+x1)/2, (y0+y1)/2
    bw, bd = H.TABLE_WIRE_BOX_W, H.TABLE_WIRE_BOX_D
    wiring = [_box(cx-bw/2, cy-bd/2, cx+bw/2, cy+bd/2,                # flip-up lid
                   TH-P(2), TH+P(1)),
              _box(cx-bw/2-P(40), cy-P(150), cx+bw/2+P(40), cy+P(150),  # cable tray
                   TH-TT-H.TABLE_WIRE_TRAY_DROP,
                   TH-TT-H.TABLE_WIRE_TRAY_DROP+P(30))]
    return top, frame, wiring


# ---------------------------------------------------------------- task chairs
def _facing(r, face):
    """Return (centre, forward unit vector, right unit vector) for a rect."""
    cx, cy = (r["x0"]+r["x1"])/2, (r["y0"]+r["y1"])/2
    fx, fy = face
    return (cx, cy), (fx, fy), (-fy, fx)


def _centre_in(parts, r):
    """Slide an assembled chair so its XY bounding box is centred in its rect.

    A 5-star base is not symmetric front-to-back (one arm points straight back,
    two point forward at 36 degrees), so the column axis is not the centre of
    the footprint.  Centring the footprint, not the column, is what keeps the
    chair inside the published envelope it was planned with.
    """
    m = trimesh.util.concatenate(parts)
    lo, hi = m.bounds
    dx = (r["x0"]+r["x1"])/2 - (lo[0]+hi[0])/2
    dy = (r["y0"]+r["y1"])/2 - (lo[1]+hi[1])/2
    for p_ in parts:
        p_.apply_translation((dx, dy, 0.0))
    return parts


def _place(mesh_local, centre, fwd):
    """Rotate a mesh built facing +X into the given forward direction."""
    ang = math.atan2(fwd[1], fwd[0])
    mesh_local.apply_transform(trimesh.transformations.rotation_matrix(ang, (0, 0, 1)))
    mesh_local.apply_translation((centre[0], centre[1], 0))
    return mesh_local


def aeron(r, face):
    """Herman Miller Aeron, size B -> (shell, base) mesh lists.

    Built facing +X in local coordinates, then rotated.  Local +X is the
    direction the sitter looks; the back is at local -X.
    """
    (cx, cy), fwd, _ = _facing(r, face)
    dx = (r["x1"]-r["x0"])/2                      # half depth  (598/2 published)
    dy = (r["y1"]-r["y0"])/2                      # half width  (658/2 published)
    seat_z = H.WORK_CHAIR_SEAT
    top_z = H.WORK_CHAIR_BACK_TOP

    loc = []
    # seat pan: 520 wide x 470 deep, front edge forward of centre
    sw, sd = P(520)/2, P(470)
    loc.append(_box(-sd*0.46, -sw, sd*0.54, sw, seat_z-P(32), seat_z))
    loc.append(_box(-sd*0.48, -sw-P(14), sd*0.56, sw+P(14),        # frame rim
                    seat_z-P(46), seat_z-P(30)))
    # back: a curved frame leaning back, 520 -> 450 wide, top at 1090
    # the arc is an APPROXIMATION of the Aeron's curve; the envelope is exact.
    n = 9
    for i in range(n):
        t0, t1 = i/n, (i+1)/n
        z0 = seat_z + (top_z-seat_z)*t0
        z1 = seat_z + (top_z-seat_z)*t1
        lean0, lean1 = -dx*(0.52+0.48*t0), -dx*(0.52+0.48*t1)
        w0 = P(520)/2*(1.0-0.16*t0)
        w1 = P(520)/2*(1.0-0.16*t1)
        v = np.array([[lean0, -w0, z0], [lean0, w0, z0],
                      [lean0+P(42), w0, z0], [lean0+P(42), -w0, z0],
                      [lean1, -w1, z1], [lean1, w1, z1],
                      [lean1+P(42), w1, z1], [lean1+P(42), -w1, z1]])
        f = [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 4, 5], [0, 5, 1],
             [1, 5, 6], [1, 6, 2], [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]]
        loc.append(trimesh.Trimesh(vertices=v, faces=f, process=False))
    # arms
    # the arm pads are the widest part of an Aeron, so their outer faces sit on
    # the published 658 mm width exactly.
    for s in (-1, 1):
        ay = s*dy
        loc.append(_box(-dx*0.55, min(ay, ay-s*P(60)), sd*0.30, max(ay, ay-s*P(60)),
                        H.WORK_CHAIR_ARM_TOP-P(26), H.WORK_CHAIR_ARM_TOP))
        loc.append(_box(-dx*0.50, min(ay-s*P(12), ay-s*P(48)),
                        -dx*0.50+P(32), max(ay-s*P(12), ay-s*P(48)),
                        seat_z-P(30), H.WORK_CHAIR_ARM_TOP-P(26)))
    shell = [_place(m, (cx, cy), fwd) for m in loc]
    base = star_base(cx, cy, H.WORK_CHAIR_BASE_DIA, H.WORK_CHAIR_CASTOR_DIA,
                     seat_z-P(44), fwd)
    _centre_in(shell + base, r)
    return shell, base


def setu(r, face):
    """Herman Miller Setu, 5-star base, armless -> (shell, base) mesh lists.

    The seat and back are one continuous piece (the kinematic spine), so the
    shell is built as a single swept band rather than as a seat plus a back.
    """
    (cx, cy), fwd, _ = _facing(r, face)
    dx = (r["x1"]-r["x0"])/2
    dy = (r["y1"]-r["y0"])/2
    seat_z = H.MEETING_CHAIR_SEAT
    top_z = H.MEETING_CHAIR_BACK_TOP
    t = H.MEETING_CHAIR_SHELL_T

    # (along-chair position, z, half width) from the front of the seat, round
    # the bend, up the back.  An APPROXIMATION of the published silhouette.
    prof = [(dx*0.62, seat_z+P(6), P(470)/2),
            (dx*0.20, seat_z, P(490)/2),
            (-dx*0.24, seat_z, P(490)/2),
            (-dx*0.50, seat_z+P(40), P(470)/2),
            (-dx*0.62, seat_z+P(150), P(455)/2),
            (-dx*0.66, seat_z+(top_z-seat_z)*0.45, P(440)/2),
            (-dx*0.60, seat_z+(top_z-seat_z)*0.75, P(420)/2),
            (-dx*0.50, top_z, P(390)/2)]
    loc = []
    for (a0, z0, w0), (a1, z1, w1) in zip(prof, prof[1:]):
        n0 = np.array([z1-z0, 0.0]); n0 /= max(np.linalg.norm(n0), 1e-6)
        ox, oz = n0[0]*t, -n0[1]*t                    # offset to the outer face
        if abs(z1-z0) < 1e-9: ox, oz = 0.0, -t
        v = np.array([[a0, -w0, z0], [a0, w0, z0], [a1, w1, z1], [a1, -w1, z1],
                      [a0+ox, -w0, z0+oz], [a0+ox, w0, z0+oz],
                      [a1+ox, w1, z1+oz], [a1+ox, -w1, z1+oz]])
        f = [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 4, 5], [0, 5, 1],
             [1, 5, 6], [1, 6, 2], [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]]
        loc.append(trimesh.Trimesh(vertices=v, faces=f, process=False))
    shell = [_place(m, (cx, cy), fwd) for m in loc]
    base = star_base(cx, cy, H.MEETING_CHAIR_BASE_DIA, H.MEETING_CHAIR_CASTOR_DIA,
                     seat_z-P(40), fwd)
    _centre_in(shell + base, r)
    return shell, base


if __name__ == "__main__":
    import furniture as F
    for k, fn, face in (("MEETING_TABLE", None, None),
                        ("WORK_CHAIR_1", aeron, (-1, 0)),
                        ("MEETING_CHAIR_1", setu, (0, 1))):
        r = F.FURNITURE[k]["box"]
        if fn is None:
            parts = sum(meeting_table(r), [])
        else:
            a, b = fn(r, face); parts = a + b
        m = trimesh.util.concatenate(parts)
        lo, hi = m.bounds
        print(f'{k:16s} {len(parts):3d} parts   '
              f'x {lo[0]:7.2f}..{hi[0]:7.2f}  (rect {r["x0"]}..{r["x1"]})   '
              f'y {lo[1]:7.2f}..{hi[1]:7.2f}  (rect {r["y0"]}..{r["y1"]})   '
              f'H {hi[2]*H.MM_PER_PX:6.0f} mm')
