# -*- coding: utf-8 -*-
"""PHASE 10 deliverables: photoreal contact sheet + a decoration before/after.

Reads only the rendered PNGs; it never touches geometry.
out/_predeco/PR_*.png are the same five cameras rendered before decoration.py
was hooked into build_3d.py, so the pair differs by decoration alone.
"""
import cv2, numpy as np, os

KEYS = "ABCDE"
CAP = {'A': 'CAMERA A   balcony end -> entrance',
       'B': 'CAMERA B   entrance -> balcony',
       'C': 'CAMERA C   meeting table -> workstations',
       'D': 'CAMERA D   workstations -> meeting area',
       'E': 'CAMERA E   aerial, whole tenancy'}

def load(p, w):
    im = cv2.imread(p)
    h = int(round(im.shape[0]*w/im.shape[1]))
    return cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)

def label(sh, t, x, y, s=.50, c=(50, 50, 50), th=1):
    cv2.putText(sh, t, (x, y), cv2.FONT_HERSHEY_SIMPLEX, s, c, th, cv2.LINE_AA)

# ---------------------------------------------------------------- contact sheet
W, G, HDR = 900, 16, 84
ims = [load(f'out/PR_{k}.png', W) for k in KEYS]
h = ims[0].shape[0]
rows = [(0, 1, 2), (3, 4)]
H = HDR + len(rows)*(h + 30 + G)
sheet = np.full((H, 3*W + 4*G, 3), 250, np.uint8)
label(sheet, 'OIMACHI TRACKS RESIDENCE 1415  /  SOHO OFFICE  -  PHASE 10 PHOTOREAL',
      G, 36, .62, (25, 25, 25))
label(sheet, 'geometry unchanged from the approved 2D MASTER  ·  finishes and lighting read from the listing photos  ·  E-CAD-2190KW walnut table, Aeron x2, Setu x6',
      G, 62, .44, (110, 110, 110))
y = HDR
for r in rows:
    for j, i in enumerate(r):
        x = G + j*(W + G)
        sheet[y:y+h, x:x+W] = ims[i]
        cv2.rectangle(sheet, (x, y), (x+W-1, y+h-1), (205, 205, 205), 1)
        label(sheet, CAP[KEYS[i]], x+2, y+h+20, .46)
    y += h + 30 + G
cv2.imwrite('out/PHOTOREAL_CONTACT_SHEET.png', sheet)
print('out/PHOTOREAL_CONTACT_SHEET.png', sheet.shape)

# ------------------------------------------------------------- before / after
def before_after(src, out_path, title, subtitle):
    pair = [k for k in KEYS if os.path.exists(f'{src}/PR_{k}.png')]
    if not pair:
        print('skipped', out_path); return
    W2, HDR2 = 820, 84
    bef = [load(f'{src}/PR_{k}.png', W2) for k in pair]
    aft = [load(f'out/PR_{k}.png', W2) for k in pair]
    h2 = bef[0].shape[0]
    ba = np.full((HDR2 + len(pair)*(h2 + 26 + G), 2*W2 + 3*G, 3), 250, np.uint8)
    label(ba, title, G, 36, .62, (25, 25, 25))
    label(ba, subtitle, G, 62, .44, (110, 110, 110))
    y = HDR2
    for i, k in enumerate(pair):
        for j, (im, t) in enumerate(((bef[i], f'BEFORE  {CAP[k]}'),
                                     (aft[i], f'AFTER   {CAP[k]}'))):
            x = G + j*(W2 + G)
            ba[y:y+h2, x:x+W2] = im
            cv2.rectangle(ba, (x, y), (x+W2-1, y+h2-1), (205, 205, 205), 1)
            label(ba, t, x+2, y+h2+18, .44, (50, 50, 50) if j else (140, 140, 140))
        y += h2 + 26 + G
    cv2.imwrite(out_path, ba)
    print(out_path, ba.shape)

before_after('out/_preproducts', 'out/PHOTOREAL_BEFORE_AFTER_products.png',
             'SPECIFIED PRODUCTS  -  BEFORE / AFTER',
             'E-CAD-2190KW walnut table (1800 -> 2100), Aeron x2, Setu x6; '
             'architecture untouched, all circulation still PASS')
before_after('out/_preexpo', 'out/PHOTOREAL_BEFORE_AFTER.png',
             'HIGHLIGHT / EXPOSURE FIX  -  BEFORE / AFTER',
             'camera A no longer shoots through the closed sash, the window light falls off '
             'with distance, the tone curve has a shoulder, and the shadow penumbra is sized '
             'by the blocker gap')
before_after('out/_prefloor', 'out/PHOTOREAL_BEFORE_AFTER_floor.png',
             'FLOOR FINISH  -  BEFORE / AFTER',
             'the photos show TWO finishes: light oak plank in the Master Bedroom, hall and '
             'kitchen, and a neutral carpet in the Living Dining')
before_after('out/_preao', 'out/PHOTOREAL_BEFORE_AFTER_shading.png',
             'SHADING FIX  -  BEFORE / AFTER',
             'ambient occlusion applied once with an interreflection correction, and the '
             'partition head track recoloured from matte black to the light head the photos show')
before_after('out/_predeco', 'out/PHOTOREAL_BEFORE_AFTER_decoration.png',
             'DECORATION  -  BEFORE / AFTER',
             '48 items, every one on an approved support '
             '(the AFTER column also carries the specified products)')
