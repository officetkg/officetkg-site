# -*- coding: utf-8 -*-
"""
PHASE 8/9/10  --  PERSPECTIVE RENDERER

Renders the SAME scene built in build_3d.py.  Nothing is generated, nothing is
re-modelled; only the camera moves.  Two-point perspective: the camera axis is
forced horizontal and the framing is set with a LENS SHIFT, so vertical lines
stay exactly vertical.  No fisheye, no ultra-wide, no barrel distortion.
"""
import numpy as np, cv2, math
import build_3d as B, heights as H, orientation as O, render_axo as A

SENSOR_W, SENSOR_H = 36.0, 24.0          # full frame, for the "mm equivalent"

def basis_from(eye, target, level=True):
    """Right-handed camera basis in ENU.  level=True forces a horizontal axis."""
    e, t = np.asarray(eye, float), np.asarray(target, float)
    d = t - e
    if level: d = np.array([d[0], d[1], 0.0])
    zc = -d / np.linalg.norm(d)                      # points from target to eye
    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(zc, up)) > .999: up = np.array([0.0, 1.0, 0.0])
    xc = np.cross(up, zc); xc /= np.linalg.norm(xc)
    yc = np.cross(zc, xc)
    return xc, yc, zc

def render(eye_master, target_master, focal_mm=32.0, W=1600, Hh=1067,
           shift=0.0, z_cut=None, skip=(), level=True, palette=None,
           mirror_y=False):
    """eye/target in MASTER px.  shift = lens rise (+) / fall (-), in image heights."""
    eye = O.to_enu(np.asarray(eye_master, float))
    tgt = O.to_enu(np.asarray(target_master, float))
    xc, yc, zc = basis_from(eye, tgt, level)
    R = np.stack([xc, yc, zc])                        # world -> camera rows

    T, C, OID, NRM = A.collect(z_cut, skip, palette)
    T = O.to_enu(T); N = O.to_enu(NRM)
    N = N / np.maximum(np.linalg.norm(N, axis=1), 1e-9)[:, None]

    V = (T - eye) @ R.T                               # camera space, -Z forward
    fpx = (W / 2.0) / math.tan(math.atan(SENSOR_W / (2.0 * focal_mm)))
    sh  = shift * Hh
    NEAR = 0.05

    alb = np.zeros((Hh, W, 3), np.float32)
    nrm = np.zeros((Hh, W, 3), np.float32)
    pos = np.zeros((Hh, W, 3), np.float32)
    obj = np.full((Hh, W), -1, np.int32)
    zb  = np.full((Hh, W), np.inf, np.float32)

    def clip_near(p):
        """Sutherland-Hodgman against z = -NEAR; returns a polygon."""
        out = []
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            ain, bin_ = a[2] <= -NEAR, b[2] <= -NEAR
            if ain: out.append(a)
            if ain != bin_:
                t = (-NEAR - a[2]) / (b[2] - a[2])
                out.append(a + (b - a) * t)
        return out

    my = -1.0 if mirror_y else 1.0
    def project(p):
        d = -p[:, 2]
        return np.stack([W/2 + fpx*(p[:, 0]/d),
                         Hh/2 - my*fpx*(p[:, 1]/d) + sh], -1), d

    for i in range(len(V)):
        poly = V[i]
        if (poly[:, 2] > -NEAR).any():
            poly = np.array(clip_near(list(poly)))
            if len(poly) < 3: continue
        tris = [(poly[0], poly[k], poly[k + 1]) for k in range(1, len(poly) - 1)]
        for tri in tris:
            P = np.array(tri)
            S, D = project(P)
            a0, b0 = int(np.floor(S[:, 0].min())), int(np.floor(S[:, 1].min()))
            a1, b1 = int(np.ceil(S[:, 0].max())) + 1, int(np.ceil(S[:, 1].max())) + 1
            a0, b0 = max(a0, 0), max(b0, 0); a1, b1 = min(a1, W), min(b1, Hh)
            if a1 <= a0 or b1 <= b0: continue
            if (a1 - a0) * (b1 - b0) > W * Hh * 1.4: continue
            gx, gy = np.meshgrid(np.arange(a0, a1) + .5, np.arange(b0, b1) + .5)
            x1, y1c = S[0]; x2, y2c = S[1]; x3, y3c = S[2]
            den = (y2c - y3c) * (x1 - x3) + (x3 - x2) * (y1c - y3c)
            if abs(den) < 1e-9: continue
            l1 = ((y2c - y3c) * (gx - x3) + (x3 - x2) * (gy - y3c)) / den
            l2 = ((y3c - y1c) * (gx - x3) + (x1 - x3) * (gy - y3c)) / den
            l3 = 1.0 - l1 - l2
            m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not m.any(): continue
            iw = l1 / D[0] + l2 / D[1] + l3 / D[2]          # perspective correct
            with np.errstate(divide='ignore', invalid='ignore'):
                z = 1.0 / iw
            sub = zb[b0:b1, a0:a1]
            sel = m & (z > 0) & (z < sub)
            if not sel.any(): continue
            sub[sel] = z[sel]
            obj[b0:b1, a0:a1][sel] = OID[i]
            alb[b0:b1, a0:a1][sel] = C[i] / 255.0
            nrm[b0:b1, a0:a1][sel] = N[i]
            w = np.stack([l1 / D[0], l2 / D[1], l3 / D[2]], -1) * z[..., None]
            wp = (w[..., None] * P[None, None, :, :]).sum(2)      # camera space
            world = wp @ R + eye
            pos[b0:b1, a0:a1][sel] = world[sel]
    return dict(albedo=alb, normal=nrm, pos=pos, obj=obj, depth=zb,
                eye=eye, basis=(xc, yc, zc), size=(W, Hh),
                names=list(B.OBJECTS.keys()))
