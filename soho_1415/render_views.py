# -*- coding: utf-8 -*-
"""PHASE 8/10 driver: render every camera from the approved scene."""
import cv2, numpy as np, time, sys
import render_persp as RP, shading as S, cameras as CAM, materials as M

GLASS = ("Window_Glass", "Balcony_Glass")
NON_GLASS = tuple(k for k in M.PALETTE if k not in GLASS)

def one(key, W=1600, Hh=1067, palette=None, tag=""):
    c = CAM.CAMERAS[key]
    pal = palette if palette is not None else M.PALETTE
    kw = dict(focal_mm=c["focal"], W=W, Hh=Hh, shift=c["shift"],
              level=c["level"], palette=pal, z_cut=c.get("z_cut"))
    gs = RP.render(c["eye"], c["target"], skip=GLASS, **kw)
    gg = RP.render(c["eye"], c["target"], skip=NON_GLASS, **kw)
    img = np.ascontiguousarray(S.compose(gs, gg, exposure=c.get('exposure', 0.80)))
    cap = (f'{c["name"]}    {c["focal"]}mm eq.    eye {round(c["eye"][2]*13.2)}mm'
           f'    {"verticals parallel" if c["level"] else "aerial view, verticals converge"}')
    cv2.rectangle(img, (0, Hh-34), (W, Hh), (252, 251, 249), -1)
    cv2.putText(img, cap, (18, Hh-12), cv2.FONT_HERSHEY_SIMPLEX, .46, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.imwrite(f'out/CAM_{key}{tag}.png', img)
    return img

if __name__ == "__main__":
    clay = "--clay" in sys.argv
    W, Hh = (1500, 1000) if "--small" in sys.argv else (1920, 1280)
    for k in "ABCDE":
        t = time.time()
        one(k, W, Hh, M.CLAY if clay else None, "_clay" if clay else "")
        print(f'CAM_{k} rendered  {time.time()-t:.1f}s')
