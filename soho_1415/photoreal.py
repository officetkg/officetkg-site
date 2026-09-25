# -*- coding: utf-8 -*-
"""
PHOTOREAL PASS
==============
Raises the render quality without touching one coordinate of the approved
model.  Everything here is image synthesis from the SAME triangles:

  * supersampled rasterising (SSAA)
  * a real shadow map cast from the north window, so the sash frame, the
    mullion, the furniture and the balustrade actually block light
  * world-space procedural texture: oak planks and grain, plaster tooth,
    concrete on the balcony
  * planar reflection in the timber floor
  * gloss highlights, and a small bloom on the window and the downlights

No AI image generation.  No geometry is added, moved or re-derived.
"""
import numpy as np, cv2, math
import build_3d as B, heights as H, orientation as O, render_axo as A
import render_persp as RP, shading as S, materials as M, lighting as LT

# ----------------------------------------------------------------- noise
def _hash(ix, iy):
    n = (ix*374761393 + iy*668265263).astype(np.int64)
    n = (n ^ (n >> 13))*1274126177
    return ((n ^ (n >> 16)) & 0xffff).astype(np.float32)/65535.0

def vnoise(x, y):
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x-ix, y-iy
    fx = fx*fx*(3-2*fx); fy = fy*fy*(3-2*fy)
    a, b = _hash(ix, iy),   _hash(ix+1, iy)
    c, d = _hash(ix, iy+1), _hash(ix+1, iy+1)
    return (a*(1-fx)+b*fx)*(1-fy) + (c*(1-fx)+d*fx)*fy

def fbm(x, y, oct=4, lac=2.1, gain=0.5):
    s, amp, tot = 0.0, 1.0, 0.0
    for _ in range(oct):
        s = s + amp*vnoise(x, y); tot += amp
        x, y, amp = x*lac, y*lac, amp*gain
    return s/tot

# ----------------------------------------------------------------- shadow map
SM_N0   = 705.0                      # light plane, just outside the sash (MASTER y)
SM_RES  = (1500, 900)                # e, u cells
SM_E    = (-372.0, 8.0)
SM_U    = (-25.0, 215.0)
NO_CAST = ("Window_Glass", "Balcony_Glass", "Downlights")

def build_shadow_map():
    """Orthographic depth from the window plane, looking south."""
    T, C, OID, NRM = A.collect(None, NO_CAST)
    P = O.to_enu(T)
    W, Hh = SM_RES
    se = (P[..., 0]-SM_E[0])/(SM_E[1]-SM_E[0])*W
    su = (SM_U[1]-P[..., 2])/(SM_U[1]-SM_U[0])*Hh
    dep = SM_N0 - P[..., 1]
    zb = np.full((Hh, W), 1e9, np.float32)
    for i in range(len(P)):
        ax, ay, dd = se[i], su[i], dep[i]
        a0, b0 = int(np.floor(ax.min())), int(np.floor(ay.min()))
        a1, b1 = int(np.ceil(ax.max()))+1, int(np.ceil(ay.max()))+1
        a0, b0 = max(a0, 0), max(b0, 0); a1, b1 = min(a1, W), min(b1, Hh)
        if a1 <= a0 or b1 <= b0: continue
        gx, gy = np.meshgrid(np.arange(a0, a1)+.5, np.arange(b0, b1)+.5)
        x1, y1c, x2, y2c, x3, y3c = ax[0], ay[0], ax[1], ay[1], ax[2], ay[2]
        den = (y2c-y3c)*(x1-x3) + (x3-x2)*(y1c-y3c)
        if abs(den) < 1e-9: continue
        l1 = ((y2c-y3c)*(gx-x3) + (x3-x2)*(gy-y3c))/den
        l2 = ((y3c-y1c)*(gx-x3) + (x1-x3)*(gy-y3c))/den
        l3 = 1.0-l1-l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any(): continue
        z = l1*dd[0] + l2*dd[1] + l3*dd[2]
        sub = zb[b0:b1, a0:a1]
        sel = m & (z < sub)
        sub[sel] = z[sel]
    return zb

_SM = None
def window_visibility(pos, nrm, softness=7.0, bias=2.2):
    global _SM
    if _SM is None: _SM = build_shadow_map()
    W, Hh = SM_RES
    se = (pos[..., 0]-SM_E[0])/(SM_E[1]-SM_E[0])*W
    su = (SM_U[1]-pos[..., 2])/(SM_U[1]-SM_U[0])*Hh
    dep = SM_N0 - pos[..., 1]
    acc = np.zeros(pos.shape[:2], np.float32); n = 0
    for dx, dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1),
                   (-2,0),(2,0),(0,-2),(0,2)]:
        xi = np.clip((se + dx*softness).astype(np.int32), 0, W-1)
        yi = np.clip((su + dy*softness).astype(np.int32), 0, Hh-1)
        acc += (dep <= _SM[yi, xi] + bias).astype(np.float32); n += 1
    v = acc/n
    facing = np.clip(nrm[..., 1], 0, 1)*0.5 + 0.5      # back faces never lit
    return cv2.GaussianBlur(v, (0, 0), 1.6)*facing

# ----------------------------------------------------------------- texture
def texture(g):
    """albedo multiplier + a micro-normal wobble, from world position."""
    pos, obj = g["pos"], g["obj"]
    names = g["names"]
    e, n, u = pos[..., 0], pos[..., 1], pos[..., 2]
    mul = np.ones(pos.shape, np.float32)
    bump = np.zeros(pos.shape[:2], np.float32)
    idx = lambda k: names.index(k) if k in names else -999

    # --- LD carpet: a fine even speckle, no direction.  The photo measures a
    # standard deviation of only about 7/255 across the pile, so the grain is
    # deliberately much quieter than the plank floor's.
    c = obj == idx("Floor_Carpet")
    if c.any():
        sp = 0.965 + 0.070*fbm(e*9.0, n*9.0, 3)
        tuft = 0.985 + 0.030*_hash(np.floor(e/LT.P(9.0)).astype(np.int64),
                                   np.floor(n/LT.P(9.0)).astype(np.int64))
        v = sp*tuft
        mul[c] = np.stack([v, v, v*1.004], -1)[c]
        bump[c] = (fbm(e*22.0, n*22.0, 2)-0.5)[c]*0.5

    # --- hall / wet-area tile: large stone-look squares with a fine mottle
    t = obj == idx("Floor_Tile")
    if t.any():
        tp = LT.P(600.0)                                   # tile module
        jx = np.abs((e/tp) % 1.0 - 0.5)*2.0
        jy = np.abs((n/tp) % 1.0 - 0.5)*2.0
        joint = np.clip((np.maximum(jx, jy)-0.975)/0.025, 0, 1)*0.18
        mott = 0.93 + 0.14*fbm(e*2.6, n*2.6, 4)
        v = mott*(1.0-joint)
        mul[t] = np.stack([v, v*0.99, v*0.965], -1)[t]

    # --- oak floor: planks running north-south, grain along the plank -----
    f = obj == idx("Floor_Slab")
    if f.any():
        pw = LT.P(150.0)                                   # plank width
        plank = np.floor(e/pw)
        joint = np.abs((e/pw) % 1.0 - 0.5)*2.0
        tone = 0.88 + 0.24*_hash(plank.astype(np.int64), np.int64(3))
        grain = 0.94 + 0.12*fbm(e*4.0, n*0.30, 4)
        fine  = 0.97 + 0.06*np.sin(n*2.2 + _hash(plank.astype(np.int64), np.int64(9))*30)
        endj  = np.abs(((n/LT.P(1100.0)) % 1.0) - 0.5)*2.0
        seam  = np.clip((joint-0.90)/0.10, 0, 1)*0.28 + np.clip((endj-0.985)/0.015, 0, 1)*0.22
        v = tone*grain*fine*(1.0-seam)
        mul[f] = np.stack([v, v*0.995, v*0.985], -1)[f]
        bump[f] = (grain-0.94)[f]*3.0

    # --- painted plaster: very fine tooth ---------------------------------
    for k in ("Interior_Walls", "Exterior_Walls", "Ceiling_Slab", "Ceiling_Coffer",
              "Columns", "PS", "Closets", "Storage_Wall_Pocket",
              "Storage_Wall_Parked_Panels"):
        m = obj == idx(k)
        if not m.any(): continue
        t = 0.975 + 0.05*fbm(e*9.0 + n*9.0, u*9.0, 3)
        mul[m] = np.stack([t, t, t], -1)[m]
        bump[m] = (t-1.0)[m]*0.7

    # --- oak joinery: grain along the long axis ---------------------------
    for k, ax in (("Book_Shelf", "n"), ("Work_Desks", "n"),
                  ("Meeting_Table", "e"), ("Entrance", "u")):
        m = obj == idx(k)
        if not m.any(): continue
        a = {"e": e, "n": n, "u": u}[ax]
        b = n if ax == "e" else e
        t = 0.90 + 0.18*fbm(a*3.2, b*0.5, 4)
        t *= 0.97 + 0.05*np.sin(b*3.4 + fbm(a*1.1, b*1.1, 2)*7)
        mul[m] = np.stack([t, t*0.99, t*0.97], -1)[m]
        bump[m] = (t-0.99)[m]*1.6

    # --- concrete / balcony ------------------------------------------------
    for k in ("Balcony_Floor", "Balcony_Railing", "Balcony_Partitions"):
        m = obj == idx(k)
        if not m.any(): continue
        t = 0.94 + 0.12*fbm(e*6.0, n*6.0, 4)
        mul[m] = np.stack([t, t, t], -1)[m]

    # --- books: each spine its own tone ------------------------------------
    m = obj == idx("Books")
    if m.any():
        key = np.floor(n/LT.P(26.0)).astype(np.int64)
        hsh = _hash(key, np.int64(17))
        t = 0.55 + 0.75*hsh
        warm = 0.90 + 0.35*_hash(key, np.int64(23))
        mul[m] = np.stack([t*warm, t*(0.95+0.10*hsh), t*(1.05-0.18*warm)], -1)[m]

    # --- foliage: leaf break-up --------------------------------------------
    m = obj == idx("Plant_Foliage")
    if m.any():
        t = 0.72 + 0.55*fbm(e*14.0, (n+u)*14.0, 3)
        mul[m] = np.stack([t*0.95, t, t*0.85], -1)[m]

    # --- fabric on the chairs ---------------------------------------------
    for k in ("Work_Chairs", "Meeting_Chairs"):
        m = obj == idx(k)
        if not m.any(): continue
        t = 0.92 + 0.16*fbm(e*22.0, (n+u)*22.0, 3)
        mul[m] = np.stack([t, t, t], -1)[m]
    return np.clip(mul, 0, 2), bump

# ----------------------------------------------------------------- gloss
GLOSS = {"Floor_Slab": (0.055, 90.0), "Floor_Tile": (0.075, 110.0), "Meeting_Table": (0.035, 70.0),
         "Work_Desks": (0.028, 60.0), "Monitor_55": (0.10, 160.0),
         "Kitchen": (0.05, 70.0), "Toilet": (0.05, 80.0),
         "Powder_Room_Fixtures": (0.06, 90.0), "Shower": (0.07, 100.0),
         "Balcony_Glass": (0.12, 170.0), "Window_Glass": (0.12, 170.0),
         "Refrigerator": (0.04, 60.0),
         # the specified products: polished steel / aluminium, walnut, shells
         "Table_Frame": (0.22, 180.0), "Table_Wirebox": (0.06, 90.0),
         "Work_Chair_Bases": (0.20, 170.0), "Meeting_Chair_Bases": (0.20, 170.0),
         "Work_Chairs": (0.030, 55.0), "Meeting_Chairs": (0.045, 70.0)}

def specular(g, n, light_dirs):
    pos, obj, names = g["pos"], g["obj"], g["names"]
    v = g["eye"][None, None, :] - pos
    v /= np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
    spec = np.zeros(pos.shape[:2], np.float32)
    amt = np.zeros(pos.shape[:2], np.float32)
    shin = np.full(pos.shape[:2], 40.0, np.float32)
    for k, (a, sh) in GLOSS.items():
        if k not in names: continue
        m = obj == names.index(k)
        amt[m] = a; shin[m] = sh
    if not amt.any(): return spec
    for L, w in light_dirs:
        Lv = np.asarray(L, np.float32); Lv /= np.linalg.norm(Lv)
        hv = v + Lv[None, None, :]
        hv /= np.maximum(np.linalg.norm(hv, axis=2, keepdims=True), 1e-6)
        spec += w*np.clip((n*hv).sum(2), 0, 1)**shin
    return spec*amt

# ----------------------------------------------------------------- shading
WIN_L = (0.0, 1.0, 0.16)

def _normals(g):
    n = g["normal"].copy()
    v = g["eye"][None, None, :] - g["pos"]
    v /= np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
    n[(n*v).sum(2) < 0] *= -1.0
    return n

AO_STRENGTH = 0.70          # calibrated below; see the AO block in shading.py

def shade_pr(g, exposure=0.80, bump_k=0.055):
    alb, obj, pos, names = g["albedo"], g["obj"], g["pos"], g["names"]
    hit = obj >= 0
    n = _normals(g)
    tex, bump = texture(g)
    alb = np.clip(alb*tex, 0, 1)
    xc, yc, _ = g["basis"]
    gy, gx = np.gradient(bump)
    n = n + bump_k*(gx[..., None]*np.asarray(xc, np.float32)[None, None, :]
                    + gy[..., None]*np.asarray(yc, np.float32)[None, None, :])
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-6)

    up = n[..., 2]
    Lv = np.asarray(WIN_L, np.float32); Lv /= np.linalg.norm(Lv)
    ndl = np.clip((n*Lv).sum(2)*0.62 + 0.38, 0, 1)**1.5
    vis = window_visibility(pos, n)
    win = ndl*(0.22 + 0.78*vis)*1.45

    sky    = np.clip(0.5 + 0.5*up, 0, 1)*0.26
    bounce = np.clip(-up, 0, 1)*0.20 + np.clip(1.0-np.abs(up), 0, 1)*0.12
    amb    = 0.20
    lamps  = S.downlights(pos, n) + 0.02
    # AO is applied ONCE, to the ambient terms only, through the
    # interreflection correction calibrated in shading.py against the photos.
    a2     = S.ao_apply(S.ssao(pos, n, obj, strength=AO_STRENGTH), alb)[..., None]

    col = alb*(win[..., None]*S.WIN_TINT
               + sky[..., None]*S.SKY_COOL*a2
               + bounce[..., None]*S.BOUNCE*a2
               + lamps[..., None]*S.LAMP_TINT*a2
               + amb*a2)
    sp = specular(g, n, [(WIN_L, 0.85*float(np.nanmean(vis))+0.25), ((0.2, 0.3, 1.0), 0.35)])
    col += (sp*np.clip(vis*0.7+0.3, 0, 1))[..., None]*np.array([1.0, 1.0, 1.02], np.float32)
    if "Downlights" in names:
        col[obj == names.index("Downlights")] = np.array([1.5, 1.44, 1.30], np.float32)
    return col*exposure, hit

def bloom(img, thr=0.93, amt=0.11):
    b = np.clip(img-thr, 0, None)/(1-thr+1e-6)
    b = cv2.GaussianBlur(b, (0, 0), 14.0)*0.7 + cv2.GaussianBlur(b, (0, 0), 46.0)*0.5
    return np.clip(img + b*amt, 0, 1)

def _tone(lin):
    o = np.clip(lin, 0, None)
    o = o/(o+0.90)*1.90
    return np.clip(o, 0, 1)**(1/1.06)

# ----------------------------------------------------------------- driver
GLASS = ("Window_Glass", "Balcony_Glass")
NON_GLASS = tuple(k for k in M.PALETTE if k not in GLASS)

def render_pr(key, W=1920, Hh=1280, ss=2, reflect=True, tag=""):
    import cameras as CAM
    c = CAM.CAMERAS[key]
    w, h = W*ss, Hh*ss
    kw = dict(focal_mm=c["focal"], W=w, Hh=h, shift=c["shift"],
              level=c["level"], palette=M.PALETTE, z_cut=c.get("z_cut"))
    gs = RP.render(c["eye"], c["target"], skip=GLASS, **kw)
    lin, hit = shade_pr(gs, exposure=c.get("exposure", 0.80))

    # planar reflection in the timber floor
    if reflect and c["level"]:
        me = (c["eye"][0], c["eye"][1], -c["eye"][2])
        mt = (c["target"][0], c["target"][1], -c["target"][2])
        gm = RP.render(me, mt, skip=GLASS, mirror_y=True, **kw)
        rl, rh = shade_pr(gm, exposure=c.get("exposure", 0.80)*0.92)
        rl = cv2.GaussianBlur(np.where(rh[..., None], rl, 0.0), (0, 0), 3.0*ss)
        fl = (gs["obj"] == gs["names"].index("Floor_Slab"))
        v = gs["eye"][None, None, :] - gs["pos"]
        v /= np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
        fres = np.clip(1.0 - np.abs(v[..., 2]), 0, 1)**4.0        # grazing = more mirror
        wgt = np.where(fl, 0.10 + 0.34*fres, 0.0)[..., None]
        lin = lin*(1-wgt) + rl*wgt

    img = np.where(hit[..., None], _tone(lin), S.SKY_BG)

    # glass panes back at low opacity
    gg = RP.render(c["eye"], c["target"], **kw)          # full scene, so glass is occluded
    gl, _ = shade_pr(gg, exposure=c.get("exposure", 0.80)*1.1)
    gidx = [gg["names"].index(k) for k in GLASS if k in gg["names"]]
    gmask = np.isin(gg["obj"], gidx)
    m = gmask[..., None].astype(np.float32)*0.17
    img = img*(1-m) + _tone(gl)*m

    img = bloom(img)
    img = cv2.resize(img, (W, Hh), interpolation=cv2.INTER_AREA)         # SSAA down
    out = (np.clip(img, 0, 1)*255).astype(np.uint8)[..., ::-1]
    out = np.ascontiguousarray(out)
    cap = (f'{c["name"]}    {c["focal"]}mm eq.    eye {round(c["eye"][2]*13.2)}mm'
           f'    {"verticals parallel" if c["level"] else "aerial view"}')
    cv2.rectangle(out, (0, Hh-34), (W, Hh), (252, 251, 249), -1)
    cv2.putText(out, cap, (18, Hh-12), cv2.FONT_HERSHEY_SIMPLEX, .46, (95, 95, 95), 1, cv2.LINE_AA)
    cv2.imwrite(f'out/PR_{key}{tag}.png', out)
    return out

if __name__ == "__main__":
    import sys, time
    keys = sys.argv[1] if len(sys.argv) > 1 else "ABCDE"
    W, Hh, ss = (1400, 933, 2) if "--draft" in sys.argv else (1920, 1280, 2)
    for k in keys:
        t = time.time(); render_pr(k, W, Hh, ss); print(f'PR_{k}  {time.time()-t:.0f}s')
