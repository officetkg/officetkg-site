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
def _clip_near(tri_cam, near, attr=None):
    """カメラ空間三角形を近接面 cz >= near でクリップ。頂点属性も一緒に補間する."""
    n_in = int((tri_cam[:, 2] >= near).sum())
    if n_in == 3:
        return [(tri_cam, attr)]
    if n_in == 0:
        return []
    poly, pat = [], []
    for i in range(3):
        a, b = tri_cam[i], tri_cam[(i + 1) % 3]
        ain, bin_ = a[2] >= near, b[2] >= near
        if ain:
            poly.append(a)
            if attr is not None:
                pat.append(attr[i])
        if ain != bin_:
            t = (near - a[2]) / (b[2] - a[2])
            poly.append(a + t * (b - a))
            if attr is not None:
                pat.append(attr[i] + t * (attr[(i + 1) % 3] - attr[i]))
    if len(poly) < 3:
        return []
    poly = np.asarray(poly)
    pat = np.asarray(pat) if attr is not None else None
    return [(np.stack([poly[0], poly[i], poly[i + 1]]),
             None if pat is None else np.stack([pat[0], pat[i], pat[i + 1]]))
            for i in range(1, len(poly) - 1)]


def render_perspective(tris, face_rgb, face_alpha, eye, target, focal_mm=30.0,
                       width=1800, height=1200, up_world=(0.0, 0.0, 1.0),
                       sensor_mm=36.0, near=40.0,
                       key=(0.15, -0.95, 0.28), ambient=0.46, prelit=False,
                       vertex_rgb=None,
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
    if prelit:
        shade = np.ones(len(tris), np.float32)     # 照度は light_faces で計算済み
    else:
        sky = 0.14 * (n[:, 2] * 0.5 + 0.5)         # 半球天空光
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
        vc = None if vertex_rgb is None else vertex_rgb[t].astype(np.float32)
        for c, va in _clip_near(cam[t], near, vc):
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
            if va is None:
                col = face_rgb[t].astype(np.float32) * shade[t]
            else:
                zc = np.maximum(z, 1e-9)
                col = ((w0[..., None] * va[0] * w[0] + w1[..., None] * va[1] * w[1]
                        + w2[..., None] * va[2] * w[2]) / zc[..., None])
                col = col[hit]
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


# =====================================================================
#  照明 (工程 "光")
#  ジオメトリは変更しない。面を細分してから照度を計算するだけ。
# =====================================================================
def tessellate(tris, rgb, alpha, max_edge=260.0, max_faces=1200000):
    """長辺が max_edge を超える三角形を再帰分割する (形状は不変)."""
    T, C, A = [tris], [rgb], [alpha]
    for _ in range(12):
        t = np.concatenate(T); c = np.concatenate(C); a = np.concatenate(A)
        e = np.stack([np.linalg.norm(t[:, 1] - t[:, 0], axis=1),
                      np.linalg.norm(t[:, 2] - t[:, 1], axis=1),
                      np.linalg.norm(t[:, 0] - t[:, 2], axis=1)], 1)
        big = e.max(1) > max_edge
        if not big.any() or len(t) * 4 > max_faces:
            return t, c, a
        keep = ~big
        b = t[big]
        m01 = (b[:, 0] + b[:, 1]) / 2
        m12 = (b[:, 1] + b[:, 2]) / 2
        m20 = (b[:, 2] + b[:, 0]) / 2
        sub = np.concatenate([
            np.stack([b[:, 0], m01, m20], 1), np.stack([m01, b[:, 1], m12], 1),
            np.stack([m20, m12, b[:, 2]], 1), np.stack([m01, m12, m20], 1)])
        T = [t[keep], sub]
        C = [c[keep], np.tile(c[big], (4, 1))]
        A = [a[keep], np.tile(a[big], 4)]
    return np.concatenate(T), np.concatenate(C), np.concatenate(A)


def light_faces(tris, base_rgb, portal, downlights,
                sky=(0.36, 0.375, 0.41), ground=(0.42, 0.405, 0.375),
                exterior_y=190.0, sun=(0.10, -0.62, 0.78),
                sun_color=(1.18, 1.15, 1.10), sky_out=(0.82, 0.87, 0.98),
                exposure=1.0):
    """面ごとの照度を計算して着色済み RGB を返す (影計算なし)。

    portal      : dict(center, normal, size, color, intensity)  掃き出し窓
    downlights  : list of dict(pos, color, intensity)           ダウンライト
    """
    c = tris.mean(axis=1)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = n / ln

    # 半球環境光
    up = n[:, 2:3] * 0.5 + 0.5
    L = np.asarray(sky, float) * up + np.asarray(ground, float) * (1 - up)

    # 窓 (面光源近似) : 室内の主光源
    pc = np.asarray(portal["center"], float)
    d = pc - c
    r = np.linalg.norm(d, axis=1, keepdims=True)
    r = np.maximum(r, 300.0)
    wdir = d / r
    facing = np.maximum((n * wdir).sum(1, keepdims=True), 0.0)
    # 窓法線と視線方向の一致度 (窓の裏側は寄与しない)
    pn = np.asarray(portal["normal"], float)
    front = np.maximum(-(wdir * pn).sum(1, keepdims=True), 0.0)
    ff = portal["size"] / (portal["size"] + np.pi * r ** 2 / 1.0e6)
    L = L + np.asarray(portal["color"], float) * portal["intensity"] * facing * front * ff

    # 屋外面 (バルコニー側) は昼光を直接受ける
    out_m = (c[:, 1] < exterior_y)[:, None]
    sv = np.asarray(sun, float)
    sv = sv / np.linalg.norm(sv)
    L = L + out_m * (np.asarray(sky_out, float) * (n[:, 2:3] * 0.5 + 0.5)
                     + np.asarray(sun_color, float)
                     * np.maximum((n * sv).sum(1, keepdims=True), 0.0))

    # ダウンライト (下向き配光)
    for dl in downlights:
        p = np.asarray(dl["pos"], float)
        d = p - c
        r = np.linalg.norm(d, axis=1, keepdims=True)
        r = np.maximum(r, 700.0)
        u = d / r
        cosf = np.maximum((n * u).sum(1, keepdims=True), 0.0)      # 面の向き
        # u は面->光源。光源->面 は -u なので、下向き配光との一致度は u_z。
        spot = np.maximum(u[:, 2:3], 0.0) ** 1.6                   # 下向き配光
        att = 1.0 / (1.0 + (r / 1300.0) ** 2)
        L = L + np.asarray(dl["color"], float) * dl["intensity"] * cosf * spot * att

    L = L * exposure
    out = base_rgb.astype(np.float32) * L                 # 拡散反射
    out = 255.0 * (1.0 - np.exp(-out / 255.0 * 1.15))     # トーンマップ
    return np.clip(out, 0, 255).astype(np.uint8)


def light_vertices(tris, base_rgb, portal, downlights, **kw):
    """頂点位置ごとに照度を計算する (面法線・グーロー補間用). -> (N,3,3)"""
    out = np.empty((len(tris), 3, 3), np.float32)
    for v in range(3):
        out[:, v] = _light_at(tris, tris[:, v], base_rgb, portal, downlights, **kw)
    return out


def _light_at(tris, pts, base_rgb, portal, downlights,
              sky=(0.36, 0.375, 0.41), ground=(0.42, 0.405, 0.375),
              exterior_y=190.0, sun=(0.10, -0.62, 0.78),
              sun_color=(1.18, 1.15, 1.10), sky_out=(0.82, 0.87, 0.98),
              exposure=1.0):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = n / ln
    c = pts
    up = n[:, 2:3] * 0.5 + 0.5
    L = np.asarray(sky, float) * up + np.asarray(ground, float) * (1 - up)

    pc = np.asarray(portal["center"], float)
    d = pc - c
    r = np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 700.0)
    wdir = d / r
    facing = np.maximum((n * wdir).sum(1, keepdims=True), 0.0)
    pn = np.asarray(portal["normal"], float)
    front = np.maximum(-(wdir * pn).sum(1, keepdims=True), 0.0)
    ff = portal["size"] / (portal["size"] + np.pi * r ** 2 / 1.0e6)
    L = L + np.asarray(portal["color"], float) * portal["intensity"] * facing * front * ff

    out_m = (c[:, 1] < exterior_y)[:, None]
    sv = np.asarray(sun, float)
    sv = sv / np.linalg.norm(sv)
    L = L + out_m * (np.asarray(sky_out, float) * (n[:, 2:3] * 0.5 + 0.5)
                     + np.asarray(sun_color, float)
                     * np.maximum((n * sv).sum(1, keepdims=True), 0.0))

    for dl in downlights:
        p = np.asarray(dl["pos"], float)
        d = p - c
        r = np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 700.0)
        u = d / r
        cosf = np.maximum((n * u).sum(1, keepdims=True), 0.0)
        spot = np.maximum(u[:, 2:3], 0.0) ** 1.6
        att = 1.0 / (1.0 + (r / 1300.0) ** 2)
        L = L + np.asarray(dl["color"], float) * dl["intensity"] * cosf * spot * att

    o = base_rgb.astype(np.float32) * (L * exposure)
    o = 255.0 * (1.0 - np.exp(-o / 255.0 * 1.15))
    return np.clip(o, 0, 255)
