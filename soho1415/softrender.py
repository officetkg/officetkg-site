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


# =====================================================================
#  透視投影 (室内パース用)
#  同一ジオメトリをカメラだけ変えて通常レンダリングする。画像生成ではない。
# =====================================================================
def _clip_near(tri_cam, near):
    """カメラ空間三角形を近接面 cz >= near でクリップし三角形群を返す."""
    inside = [v for v in range(3) if tri_cam[v, 2] >= near]
    if len(inside) == 3:
        return [tri_cam]
    if not inside:
        return []
    poly = []
    for i in range(3):
        a = tri_cam[i]
        b = tri_cam[(i + 1) % 3]
        ain = a[2] >= near
        bin_ = b[2] >= near
        if ain:
            poly.append(a)
        if ain != bin_:
            t = (near - a[2]) / (b[2] - a[2])
            poly.append(a + t * (b - a))
    if len(poly) < 3:
        return []
    poly = np.asarray(poly)
    return [np.stack([poly[0], poly[i], poly[i + 1]]) for i in range(1, len(poly) - 1)]


def render_perspective(tris, face_rgb, face_alpha, eye, target, focal_mm=30.0,
                       width=1800, height=1200, up_world=(0.0, 0.0, 1.0),
                       sensor_mm=36.0, near=40.0,
                       key=(0.15, -0.95, 0.28), ambient=0.46,
                       bg_top=(206, 222, 238), bg_bot=(238, 240, 240)):
    """フルサイズ換算 focal_mm の透視投影でラスタライズする."""
    eye = np.asarray(eye, float)
    fwd = np.asarray(target, float) - eye
    fwd /= np.linalg.norm(fwd)
    up_w = np.asarray(up_world, float)
    right = np.cross(fwd, up_w)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    R = np.stack([right, up, fwd])                    # 行: 右 / 上 / 前

    cam = (tris.reshape(-1, 3) - eye) @ R.T
    cam = cam.reshape(-1, 3, 3)
    scale = (width / 2.0) / np.tan(np.arctan(sensor_mm / 2.0 / focal_mm))

    # 面法線と陰影 (ワールド空間)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = n / ln
    k = np.asarray(key, float)
    k = k / np.linalg.norm(k)
    sky = 0.14 * (n[:, 2] * 0.5 + 0.5)          # 半球天空光
    shade = np.clip(ambient + 0.38 * np.abs(n @ k) + sky, 0, 1)

    img = np.zeros((height, width, 3), np.float32)
    g = np.linspace(0, 1, height)[:, None]
    img[:] = (np.asarray(bg_top, np.float32) * (1 - g)
              + np.asarray(bg_bot, np.float32) * g)[:, None, :]
    zbuf = np.full((height, width), -np.inf, np.float32)

    order = np.argsort(-cam[:, :, 2].min(axis=1))     # 遠 -> 近
    opaque = [t for t in order if face_alpha[t] >= 0.999]
    glass = [t for t in order if face_alpha[t] < 0.999]

    def raster(t, blend):
        for c in _clip_near(cam[t], near):
            sx = width * 0.5 + c[:, 0] * scale / c[:, 2]
            sy = height * 0.5 - c[:, 1] * scale / c[:, 2]
            w = 1.0 / c[:, 2]
            minx = max(int(np.floor(sx.min())), 0)
            maxx = min(int(np.ceil(sx.max())), width - 1)
            miny = max(int(np.floor(sy.min())), 0)
            maxy = min(int(np.ceil(sy.max())), height - 1)
            if maxx < minx or maxy < miny:
                continue
            den = ((sy[1] - sy[2]) * (sx[0] - sx[2])
                   + (sx[2] - sx[1]) * (sy[0] - sy[2]))
            if abs(den) < 1e-9:
                continue
            gy, gx = np.mgrid[miny:maxy + 1, minx:maxx + 1]
            gx = gx + 0.5
            gy = gy + 0.5
            w0 = ((sy[1] - sy[2]) * (gx - sx[2]) + (sx[2] - sx[1]) * (gy - sy[2])) / den
            w1 = ((sy[2] - sy[0]) * (gx - sx[2]) + (sx[0] - sx[2]) * (gy - sy[2])) / den
            w2 = 1.0 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            z = w0 * w[0] + w1 * w[1] + w2 * w[2]
            sl = (slice(miny, maxy + 1), slice(minx, maxx + 1))
            hit = m & (z > zbuf[sl])
            if not hit.any():
                continue
            col = face_rgb[t].astype(np.float32) * shade[t]
            tile = img[sl]
            if blend:
                a = face_alpha[t]
                tile[hit] = tile[hit] * (1 - a) + col * a
            else:
                tile[hit] = col
                zb = zbuf[sl]
                zb[hit] = z[hit]
                zbuf[sl] = zb
            img[sl] = tile

    for t in opaque:
        raster(t, False)
    for t in glass:
        raster(t, True)
    return np.clip(img, 0, 255).astype(np.uint8)
