# -*- coding: utf-8 -*-
"""
Deterministic orthographic software renderer (numpy z-buffer).

画像生成 AI は一切使用しない。実ジオメトリの三角形のみをラスタライズする。
"""
import numpy as np


def _basis(eye_dir, up=(0.0, 0.0, 1.0)):
    e = np.asarray(eye_dir, float)
    e = e / np.linalg.norm(e)
    up = np.asarray(up, float)
    if abs(np.dot(e, up)) > 0.999:
        up = np.array([0.0, 1.0, 0.0])
    r = np.cross(up, e)
    r /= np.linalg.norm(r)
    u = np.cross(e, r)
    return np.stack([r, u, e])          # rows: right / up / towards-camera


def render(tris, face_rgb, face_obj, eye_dir, width=1800, height=1400,
           up=(0, 0, 1), margin=0.04, light=(0.45, -0.55, 0.70),
           bg=(252, 252, 250), ambient=0.42, outline=True,
           px_per_mm=None, center=None, up_hint=(0, 0, 1)):
    """tris: (N,3,3) world mm.  face_rgb: (N,3) uint8.  face_obj: (N,) int."""
    R = _basis(eye_dir, up_hint)
    V = tris.reshape(-1, 3) @ R.T
    V = V.reshape(-1, 3, 3)

    xs, ys = V[..., 0], V[..., 1]
    if center is None:
        cx = 0.5 * (xs.min() + xs.max())
        cy = 0.5 * (ys.min() + ys.max())
    else:
        c = np.asarray(center, float) @ R.T
        cx, cy = c[0], c[1]
    if px_per_mm is None:
        sx = width * (1 - 2 * margin) / max(xs.max() - xs.min(), 1e-6)
        sy = height * (1 - 2 * margin) / max(ys.max() - ys.min(), 1e-6)
        px_per_mm = min(sx, sy)

    px = (V[..., 0] - cx) * px_per_mm + width * 0.5
    py = height * 0.5 - (V[..., 1] - cy) * px_per_mm
    pz = V[..., 2]

    # flat shading from world-space normals
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = n / ln
    L = np.asarray(light, float)
    L = L / np.linalg.norm(L)
    lam = np.abs(n @ L)
    shade = np.clip(ambient + (1.0 - ambient) * lam, 0.0, 1.0)

    img = np.zeros((height, width, 3), np.float32)
    img[:] = np.asarray(bg, np.float32)
    zbuf = np.full((height, width), -np.inf, np.float32)
    idbuf = np.full((height, width), -1, np.int32)

    order = np.argsort(-pz.min(axis=1))          # far -> near helps cache only
    for t in order:
        x0, x1 = px[t], py[t]
        minx = int(np.floor(x0.min()))
        maxx = int(np.ceil(x0.max()))
        miny = int(np.floor(x1.min()))
        maxy = int(np.ceil(x1.max()))
        if maxx < 0 or minx >= width or maxy < 0 or miny >= height:
            continue
        minx = max(minx, 0); maxx = min(maxx, width - 1)
        miny = max(miny, 0); maxy = min(maxy, height - 1)
        if maxx < minx or maxy < miny:
            continue
        ax, ay = x0[0], x1[0]
        bx, by = x0[1], x1[1]
        cxx, cyy = x0[2], x1[2]
        den = (by - cyy) * (ax - cxx) + (cxx - bx) * (ay - cyy)
        if abs(den) < 1e-9:
            continue
        gy, gx = np.mgrid[miny:maxy + 1, minx:maxx + 1]
        gx = gx + 0.5
        gy = gy + 0.5
        w0 = ((by - cyy) * (gx - cxx) + (cxx - bx) * (gy - cyy)) / den
        w1 = ((cyy - ay) * (gx - cxx) + (ax - cxx) * (gy - cyy)) / den
        w2 = 1.0 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * pz[t, 0] + w1 * pz[t, 1] + w2 * pz[t, 2]
        sl = (slice(miny, maxy + 1), slice(minx, maxx + 1))
        better = m & (z > zbuf[sl])
        if not better.any():
            continue
        col = face_rgb[t].astype(np.float32) * shade[t]
        zb = zbuf[sl]; zb[better] = z[better]; zbuf[sl] = zb
        ib = idbuf[sl]; ib[better] = face_obj[t]; idbuf[sl] = ib
        tile = img[sl]; tile[better] = col; img[sl] = tile

    if outline:
        e = np.zeros((height, width), bool)
        e[:, 1:] |= idbuf[:, 1:] != idbuf[:, :-1]
        e[1:, :] |= idbuf[1:, :] != idbuf[:-1, :]
        d = np.zeros((height, width), bool)
        zf = np.where(np.isfinite(zbuf), zbuf, 0)
        d[:, 1:] |= np.abs(zf[:, 1:] - zf[:, :-1]) > 60
        d[1:, :] |= np.abs(zf[1:, :] - zf[:-1, :]) > 60
        e |= d & (idbuf >= 0)
        img[e] = img[e] * 0.25 + np.array([25, 25, 30], np.float32) * 0.75

    return np.clip(img, 0, 255).astype(np.uint8), px_per_mm
