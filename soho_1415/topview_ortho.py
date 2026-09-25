# -*- coding: utf-8 -*-
"""
PHASE 7  --  ORTHOGRAPHIC TOP VIEW of the 3D model.

Perspective = 0.  Camera axis = straight down (-Z).  Same origin, same scale and
same aspect ratio as the 2D MASTER, because the projection used is literally
    screen = (MASTER_x, MASTER_y)
applied to the real triangles of the built mesh, with a z-buffer.
Nothing is re-drawn by hand.
"""
import cv2, numpy as np
import build_3d as B, render_2d as R

CROP, S = R.CROP, R.S
OX, OY = R.OX, R.OY
W_, H_ = R.W_, R.H_
SS = 2                                     # supersampling for the z-buffer only

COLORS = {
 "Exterior_Walls":(40,40,40),"Interior_Walls":(105,105,105),"Columns":(160,0,200),
 "PS":(150,150,150),"Entrance":(0,120,200),"Shower":(190,190,120),"WD":(190,190,120),
 "Powder_Room_Fixtures":(190,190,120),"Toilet":(190,190,120),"Kitchen":(180,150,90),
 "Refrigerator":(180,150,90),"Closets":(0,140,190),"Book_Shelf":(0,140,190),
 "Storage_Wall_Pocket":(0,150,0),"Storage_Wall_Parked_Panels":(0,210,0),
 "Storage_Wall_Rail":(0,110,0),"Windows":(60,60,70),"Window_Glass":(210,180,120),
 "Balcony_Glass":(215,195,150),"Balcony_Partitions":(60,40,95),"Downpipe":(190,200,205),"Balcony_Floor":(255,200,150),
 "Balcony_Railing":(255,110,0),"Work_Desks":(20,110,190),"Work_Chairs":(70,70,70),
 "Printer_Unit":(120,100,60),"Meeting_Table":(15,85,160),"Meeting_Chairs":(80,80,80),
 "Monitor_55":(0,0,220),"Floor_Slab":(248,248,248),"Floor_Carpet":(242,244,246),"Floor_Tile":(238,238,236),
 "Table_Frame":(90,120,170),"Table_Wirebox":(40,40,60),
 "Work_Chair_Bases":(120,120,130),"Meeting_Chair_Bases":(120,120,130),
}

# A plan view is cut BELOW the ceiling, so the ceiling, its coffer and the
# downlights are never part of it -- leaving them in simply paints the whole
# sheet with the slab.  Decoration is a finishing layer, not geometry under
# verification, so it is left out of this view too.
SKIP_TOP = {"Ceiling_Slab", "Ceiling_Coffer", "Downlights",
            "Laptops", "Laptop_Screens", "Desk_Kit", "Paper", "Books",
            "Plant_Pots", "Plant_Foliage"}

def render_top():
    w, h = W_*SS, H_*SS
    zbuf = np.full((h, w), -1e9, np.float32)
    idx  = np.full((h, w), -1, np.int32)
    names = [n for n in B.OBJECTS.keys() if n not in SKIP_TOP]
    for oi, name in enumerate(names):
        for m in B.OBJECTS[name]:
            V, Fc = m.vertices, m.faces
            for tri in Fc:
                p = V[tri]
                z = float(p[:, 2].mean())
                pts = np.empty((3, 2), np.int32)
                pts[:, 0] = np.round((p[:, 0] + OX - CROP[0]) * S * SS)
                pts[:, 1] = np.round((p[:, 1] + OY - CROP[1]) * S * SS)
                x0, y0 = pts.min(0); x1, y1 = pts.max(0)
                if x1 < 0 or y1 < 0 or x0 >= w or y0 >= h: continue
                if (x1-x0) < 1 or (y1-y0) < 1: continue          # vertical face
                x0c, y0c = max(x0,0), max(y0,0); x1c, y1c = min(x1+1,w), min(y1+1,h)
                sub = np.zeros((y1c-y0c, x1c-x0c), np.uint8)
                cv2.fillConvexPoly(sub, pts - [x0c, y0c], 1)
                sel = (sub.astype(bool)) & (z > zbuf[y0c:y1c, x0c:x1c])
                zbuf[y0c:y1c, x0c:x1c][sel] = z
                idx [y0c:y1c, x0c:x1c][sel] = oi
    img = np.full((h, w, 3), 255, np.uint8)
    zmin, zmax = -B.H.SLAB_THICKNESS, B.H.WALL_HEIGHT
    for oi, name in enumerate(names):
        sel = idx == oi
        if not sel.any(): continue
        shade = 0.55 + 0.45 * np.clip((zbuf[sel]-zmin)/(zmax-zmin), 0, 1)
        c = np.array(COLORS.get(name, (128,128,128)), np.float32)
        img[sel] = np.clip(c[None,:] * shade[:,None] + 255*(1-shade[:,None])*0.25, 0, 255)
    # object-boundary edges, independent of colour and of equal heights
    e = np.zeros_like(idx, bool)
    e[:, :-1] |= idx[:, :-1] != idx[:, 1:]
    e[:-1, :] |= idx[:-1, :] != idx[1:, :]
    # also boundaries between separate parts of the SAME object (height steps)
    zs = (zbuf*100).astype(np.int64)
    e[:, :-1] |= zs[:, :-1] != zs[:, 1:]
    e[:-1, :] |= zs[:-1, :] != zs[1:, :]
    e8 = cv2.dilate(e.astype(np.uint8)*255, np.ones((SS, SS), np.uint8))
    edges = cv2.resize(e8, (W_, H_), interpolation=cv2.INTER_NEAREST)
    img = cv2.resize(img, (W_, H_), interpolation=cv2.INTER_AREA)
    mask = cv2.resize((idx >= 0).astype(np.uint8)*255, (W_, H_), interpolation=cv2.INTER_AREA)
    return img, mask, edges, idx, names, SS

if __name__ == "__main__":
    img, mask, edges, _i, _n, _s = render_top()
    cv2.imwrite("out/B3_topview_ortho.png", img)
    print("ortho top view rendered", img.shape)
