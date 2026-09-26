# -*- coding: utf-8 -*-
"""
PHASE 9  --  LIGHTING

The balcony faces NORTH, so no direct sun ever reaches the living zone.  The
model is therefore: one large, even north window as the key, a cool sky term
from above, a warm bounce off the timber floor, and the existing ceiling
downlights as a weak fill.  No invented sun, no HDR grading, no film look.

Glass is rendered as glass: the scene is rasterised without the panes so you
see through to the balustrade and the sky, then the panes are composited back
at low opacity for the sheen.
"""
import numpy as np, cv2
import lighting as LT
from heights import WALL_HEIGHT as _WH

WINDOW_N  = 666.0                       # MASTER y of the sash plane (north is +y)
SKY_COOL  = np.array([0.97, 0.99, 1.05])
WIN_TINT  = np.array([1.00, 1.00, 1.01])
BOUNCE    = np.array([1.06, 1.01, 0.94])
LAMP_TINT = np.array([1.06, 1.00, 0.92])
SKY_BG    = np.array([0.93, 0.945, 0.96])

# ----------------------------------------------------------------------
# AMBIENT OCCLUSION
# ----------------------------------------------------------------------
# Calibrated against the listing photos, not chosen by eye.  Two ratios are
# measured off the reference photo of the Living Dining and reproduced here:
#     internal wall/ceiling corner  /  flat wall face      = 0.935
#     Book Shelf cubby shadow       /  shelf board face    = 0.679
# Raw geometric occlusion cannot give those numbers: a 90 degree corner between
# two white surfaces hides half the hemisphere, yet the photo shows it only
# 6.5 % darker, because the light comes straight back off the facing white
# wall.  ao_apply() is that first-order interreflection correction -- a bright
# surface keeps nearly all of its ambient in a corner, a darker recess loses
# more.  Without it every internal corner and every shelf cubby renders as a
# black line, which is exactly what the photos do NOT show.
AO_RADIUS_MM   = 340.0     # world radius the occlusion test looks over
AO_SCREEN_PX   = (7, 15, 29)   # screen radii sampled, so near and far both work
AO_FLOOR       = 0.30      # raw occlusion never closes completely
INTERREFLECT   = 0.96      # how much of the lost ambient a bright surface wins back
INTERREFLECT_G = 1.0       # exponent on albedo: >1 widens the gap between a white
                           # wall, which barely darkens, and a deeper recess

def ssao(pos, nrm, obj, radius_mm=None, samples=10, strength=1.0):
    """Raw geometric openness in 0..1 (1 = fully open).

    The world distance window is set in millimetres and is independent of the
    screen radius sampled, so the term means the same thing near and far.
    """
    h, w = obj.shape
    valid = obj >= 0
    R = (AO_RADIUS_MM if radius_mm is None else radius_mm)/13.2   # mm -> MASTER px
    occ = np.zeros((h, w), np.float32); cnt = 0
    rng = np.random.default_rng(7)
    for ring in AO_SCREEN_PX:
        for k in range(samples):
            a = 2*np.pi*k/samples + rng.uniform(0, .4)
            dx, dy = int(round(ring*np.cos(a))), int(round(ring*np.sin(a)))
            if dx == 0 and dy == 0: continue
            sp = np.roll(np.roll(pos, dy, 0), dx, 1)
            sv = np.roll(np.roll(valid, dy, 0), dx, 1)
            d = sp - pos
            dist = np.linalg.norm(d, axis=2) + 1e-6
            cosang = (d*nrm).sum(2)/dist
            occ += np.where(sv & (dist < R) & (cosang > 0.20),
                            np.clip(cosang, 0, 1), 0)
            cnt += 1
    ao = np.clip(1.0 - strength*np.clip(occ/max(cnt, 1), 0, 1)*1.70, AO_FLOOR, 1.0)
    return np.where(valid, cv2.GaussianBlur(ao, (0, 0), 3.0), 1.0)

def _luma(alb):
    return alb[..., 0]*0.2126 + alb[..., 1]*0.7152 + alb[..., 2]*0.0722

def ao_apply(ao, alb, interreflect=None):
    """Interreflection-corrected occlusion, to be multiplied into the AMBIENT
    terms only -- never into the window term, which the shadow map already
    handles."""
    if interreflect is None: interreflect = INTERREFLECT   # read at call time
    k = np.clip(1.0 - interreflect*_luma(alb)**INTERREFLECT_G, 0.0, 1.0)
    return np.clip(1.0 - k*(1.0 - ao), 0.0, 1.0)

_R0 = LT.P(1600)                       # downlight falloff reference
def downlights(pos, n):
    """The building's own recessed downlights, as read from the photos.
    Secondary to daylight - the brief keeps natural light primary."""
    tot = np.zeros(pos.shape[:2], np.float32)
    for lx, ly, kind in LT.luminaires():
        lz = _WH - LT.COFFER_DROP if kind == "living" else _WH
        lp = np.array([-lx, ly, lz], np.float32)        # MASTER -> ENU
        v = lp[None, None, :] - pos
        d = np.linalg.norm(v, axis=2) + 1e-6
        l = v/d[..., None]
        ndl = np.clip((n*l).sum(2), 0, 1)
        cone = np.clip((l[..., 2] - LT.DL_CONE)/(1.0 - LT.DL_CONE), 0, 1)**1.4
        tot += ndl*cone/(1.0 + (d/_R0)**2)
    return tot*LT.DL_LUMENS*0.42

def _linear(g, ao_strength=1.0):
    """Linear-light RGB for one G-buffer, plus the hit mask."""
    alb, nrm, pos, obj = g["albedo"], g["normal"], g["pos"], g["obj"]
    hit = obj >= 0
    n = nrm.copy()
    to_eye = g["eye"][None, None, :] - pos
    to_eye /= np.maximum(np.linalg.norm(to_eye, axis=2, keepdims=True), 1e-6)
    n[(n*to_eye).sum(2) < 0] *= -1.0
    up = n[..., 2]

    L = np.array([0.0, 1.0, 0.16]); L /= np.linalg.norm(L)
    ndl = np.clip((n*L).sum(2)*0.62 + 0.38, 0, 1)**1.5
    dist_n = np.clip(WINDOW_N - pos[..., 1], 0, None)
    fall = 1.0/(1.0 + (dist_n/270.0)**1.6)
    win = ndl*(0.34 + 0.66*fall)*1.30

    sky    = np.clip(0.5 + 0.5*up, 0, 1)*0.28
    bounce = np.clip(-up, 0, 1)*0.20 + np.clip(1.0-np.abs(up), 0, 1)*0.12
    amb    = 0.24
    lamps  = downlights(pos, n) + 0.02

    a2 = ao_apply(ssao(pos, n, obj, strength=ao_strength), alb)[..., None]
    col = alb*(win[..., None]*WIN_TINT
               + sky[..., None]*SKY_COOL*a2
               + bounce[..., None]*BOUNCE*a2
               + lamps[..., None]*LAMP_TINT*a2
               + amb*a2)
    names = g.get("names") or []
    if "Downlights" in names:
        m = obj == names.index("Downlights")
        col[m] = np.array([1.35, 1.30, 1.18], np.float32)      # lit aperture
    return col, hit

# Same soft knee as photoreal._tone: the base curve reaches 1.0 at a linear
# luma of exactly 1.0 and was then clipped, so the plain shaded views blew out
# in the same places the photoreal ones did.  Below the knee nothing changes.
TONE_KNEE = 0.75

def _tone(lin):
    x = np.clip(lin, 0, None)
    y = x/(x + 0.90)*1.90
    k = TONE_KNEE
    y = np.where(y <= k, y, k + (1.0-k)*(1.0 - np.exp(-(y-k)/(1.0-k))))
    return np.clip(y, 0, 1)**(1/1.06)

def compose(g_scene, g_glass=None, glass_opacity=0.16, exposure=1.0):
    """scene without glass, then the panes blended back at low opacity."""
    lin, hit = _linear(g_scene)
    lin *= exposure
    img = np.where(hit[..., None], _tone(lin), SKY_BG)
    if g_glass is not None:
        gl_lin, gl_hit = _linear(g_glass, ao_strength=0.25)
        gl = _tone(gl_lin*exposure*1.15)
        m = (gl_hit[..., None]).astype(np.float32)*glass_opacity
        img = img*(1 - m) + gl*m
    return (np.clip(img, 0, 1)*255).astype(np.uint8)[..., ::-1]     # RGB -> BGR

def shade(g, exposure=1.0, ao_strength=1.0):
    lin, hit = _linear(g, ao_strength)
    img = np.where(hit[..., None], _tone(lin*exposure), SKY_BG)
    return (np.clip(img, 0, 1)*255).astype(np.uint8)[..., ::-1]
