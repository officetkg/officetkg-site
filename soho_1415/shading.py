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

WINDOW_N  = 666.0                       # MASTER y of the sash plane (north is +y)
SKY_COOL  = np.array([0.97, 0.99, 1.05])
WIN_TINT  = np.array([1.00, 1.00, 1.01])
BOUNCE    = np.array([1.06, 1.01, 0.94])
LAMP_TINT = np.array([1.06, 1.00, 0.92])
SKY_BG    = np.array([0.93, 0.945, 0.96])

def ssao(pos, nrm, obj, radius=24.0, samples=14, strength=1.0):
    h, w = obj.shape
    valid = obj >= 0
    occ = np.zeros((h, w), np.float32); cnt = 0
    rng = np.random.default_rng(7)
    for k in range(samples):
        a = 2*np.pi*k/samples + rng.uniform(0, .4)
        r = radius*(0.30 + 0.70*rng.random())
        dx, dy = int(round(r*np.cos(a))), int(round(r*np.sin(a)))
        if dx == 0 and dy == 0: continue
        sp = np.roll(np.roll(pos, dy, 0), dx, 1)
        sv = np.roll(np.roll(valid, dy, 0), dx, 1)
        d = sp - pos
        dist = np.linalg.norm(d, axis=2) + 1e-6
        cosang = (d*nrm).sum(2)/dist
        occ += np.where(sv & (dist < radius*1.6) & (cosang > 0.20),
                        np.clip(cosang, 0, 1), 0)
        cnt += 1
    ao = np.clip(1.0 - strength*np.clip(occ/max(cnt, 1), 0, 1)*1.70, 0.22, 1.0)
    return np.where(valid, cv2.GaussianBlur(ao, (0, 0), 3.0), 1.0)

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
    lamps  = np.clip(-up, 0, 1)*0.15 + 0.03
    amb    = 0.24

    ao = ssao(pos, n, obj, strength=ao_strength)
    a2 = ao**1.2
    col = alb*(win[..., None]*WIN_TINT
               + sky[..., None]*SKY_COOL*a2[..., None]
               + bounce[..., None]*BOUNCE*a2[..., None]
               + lamps[..., None]*LAMP_TINT*a2[..., None]
               + amb*a2[..., None])
    col *= ao[..., None]**0.50
    return col, hit

def _tone(lin):
    out = np.clip(lin, 0, None)
    out = out/(out + 0.90)*1.90                 # gentle shoulder, no HDR look
    return np.clip(out, 0, 1)**(1/1.06)

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
