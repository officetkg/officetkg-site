# -*- coding: utf-8 -*-
"""
Visual inspection renderer for the PHASE 6 mesh.

ORTHOGRAPHIC projection of the real triangles of build_3d.OBJECTS, with
per-pixel depth interpolation.  No perspective, no image generation, no hand
drawing, no geometry invented.  This is a geometry-checking aid only; the
PHASE 8 cameras are a separate step.
"""
import cv2, numpy as np
import build_3d as B, heights as H, orientation as O

COL = {
 "Exterior_Walls":(236,236,238),"Interior_Walls":(226,226,230),"Columns":(206,200,212),
 "PS":(198,198,198),"Entrance":(150,175,205),"Shower":(214,224,230),"WD":(222,222,224),
 "Powder_Room_Fixtures":(234,234,236),"Toilet":(238,238,240),"Kitchen":(172,192,210),
 "Refrigerator":(212,215,218),"Closets":(162,188,210),"Book_Shelf":(132,170,202),
 "Storage_Wall_Pocket":(110,186,110),"Storage_Wall_Parked_Panels":(60,200,60),
 "Storage_Wall_Rail":(80,152,80),"Windows":(70,70,78),"Window_Glass":(226,206,170),
 "Balcony_Glass":(230,214,186),"Balcony_Partitions":(72,46,110),"Downpipe":(214,220,224),"Balcony_Floor":(196,200,204),
 "Balcony_Railing":(178,183,188),"Work_Desks":(118,162,204),"Work_Chairs":(72,72,78),
 "Printer_Unit":(158,158,163),"Meeting_Table":(106,148,194),"Meeting_Chairs":(82,82,88),
 "Monitor_55":(32,32,38),"Floor_Slab":(224,221,217),
}

def basis(bearing_deg, el_deg):
    """Right-handed camera basis in ENU. bearing = compass bearing of the CAMERA."""
    return O.camera_basis(bearing_deg, el_deg)

def collect(z_cut=None, skip=(), palette=None):
    """triangles + per-triangle colour and object id, boxes clipped at z_cut."""
    T, C, OID = [], [], []
    for oi, (name, meshes) in enumerate(B.OBJECTS.items()):
        if name in skip: continue
        src = palette if palette is not None else COL
        base = np.array(src.get(name, (150,150,150)), float)
        for m in meshes:
            if z_cut is not None:
                lo, hi = m.bounds
                if lo[2] >= z_cut: continue
                if len(m.vertices) == 8 and hi[2] > z_cut:      # axis-aligned box
                    m = __import__("trimesh").creation.box(
                            extents=(hi[0]-lo[0], hi[1]-lo[1], z_cut-lo[2]))
                    m.apply_translation(((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, (lo[2]+z_cut)/2))
            for t, n in zip(m.faces, m.face_normals):
                T.append(m.vertices[t]); C.append(base); OID.append(oi)
    return np.array(T), np.array(C), np.array(OID), \
           np.array([np.cross(p[1]-p[0], p[2]-p[0]) for p in np.array(T)])

def render(bearing=225, el=30, W=1500, Hh=1050, z_cut=None, skip=(), pad=.06,
           light=(.35,-.45,.82), outline=True):
    r, u, zc = basis(bearing, el)
    T, C, OID, NRM = collect(z_cut, skip)
    nl = np.linalg.norm(NRM, axis=1); nl[nl == 0] = 1
    N = NRM / nl[:, None]
    L = np.array(light, float); L /= np.linalg.norm(L)

    T_enu = O.to_enu(T)                      # MASTER -> right-handed east/north/up
    N = O.to_enu(N)                          # normals ride the same reflection
    N = N / np.maximum(np.linalg.norm(N, axis=1), 1e-9)[:, None]
    shade = 0.42 + 0.58 * np.clip(np.abs(N @ L), 0, 1)
    C = np.clip(np.array(C) * shade[:, None], 0, 255)
    P = np.stack([T_enu @ r, T_enu @ u], -1)
    D = T_enu @ zc                           # depth toward the eye
    x0, y0, x1, y1 = P[...,0].min(), P[...,1].min(), P[...,0].max(), P[...,1].max()
    s = min(W*(1-2*pad)/(x1-x0), Hh*(1-2*pad)/(y1-y0))
    ox = (W-(x1-x0)*s)/2 - x0*s; oy = (Hh-(y1-y0)*s)/2 + y1*s
    SX = P[...,0]*s + ox; SY = -P[...,1]*s + oy

    img = np.full((Hh, W, 3), 255, np.uint8)
    zb  = np.full((Hh, W), -1e18, np.float64)
    ob  = np.full((Hh, W), -1, np.int32)
    order = np.argsort(D.mean(1))          # far to near: ties resolve to the nearer face
    for i in order:
        ax, ay = SX[i], SY[i]
        a0, a1 = int(np.floor(ax.min())), int(np.ceil(ax.max()))+1
        b0, b1 = int(np.floor(ay.min())), int(np.ceil(ay.max()))+1
        a0, b0 = max(a0,0), max(b0,0); a1, b1 = min(a1,W), min(b1,Hh)
        if a1 <= a0 or b1 <= b0: continue
        xs = np.arange(a0,a1)+0.5; ys = np.arange(b0,b1)+0.5
        gx, gy = np.meshgrid(xs, ys)
        x1_,y1_ , x2_,y2_ , x3_,y3_ = ax[0],ay[0], ax[1],ay[1], ax[2],ay[2]
        den = (y2_-y3_)*(x1_-x3_) + (x3_-x2_)*(y1_-y3_)
        if abs(den) < 1e-9: continue
        l1 = ((y2_-y3_)*(gx-x3_) + (x3_-x2_)*(gy-y3_)) / den
        l2 = ((y3_-y1_)*(gx-x3_) + (x1_-x3_)*(gy-y3_)) / den
        l3 = 1.0 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any(): continue
        z = l1*D[i,0] + l2*D[i,1] + l3*D[i,2]
        sub = zb[b0:b1, a0:a1]
        sel = m & (z >= sub - 1e-6)
        if not sel.any(): continue
        sub[sel] = z[sel]
        ob[b0:b1, a0:a1][sel] = OID[i]
        img[b0:b1, a0:a1][sel] = C[i]
    if outline:
        e = np.zeros((Hh, W), bool)
        e[:, :-1] |= ob[:, :-1] != ob[:, 1:]
        e[:-1, :] |= ob[:-1, :] != ob[1:, :]
        d = np.abs(np.diff(zb, axis=1)); e[:, :-1] |= d > 6
        d = np.abs(np.diff(zb, axis=0)); e[:-1, :] |= d > 6
        e &= ob >= 0
        img[e] = (img[e]*0.35).astype(np.uint8)
    return img

if __name__ == "__main__":
    CUT = H.P(1250)
    jobs = [("AXO_0_TOP_northup", dict(bearing=180, el=89.5), "TOP, north up"),
            ("AXO_1_NE_full",  dict(bearing= 45, el=28), "camera NORTH-EAST, full height"),
            ("AXO_2_NW_full",  dict(bearing=315, el=28), "camera NORTH-WEST, full height"),
            ("AXO_3_NE_cut",   dict(bearing= 45, el=40, z_cut=CUT), "camera NORTH-EAST, cut 1250"),
            ("AXO_4_SE_cut",   dict(bearing=135, el=40, z_cut=CUT), "camera SOUTH-EAST, cut 1250"),
            ("AXO_5_SW_cut",   dict(bearing=225, el=40, z_cut=CUT), "camera SOUTH-WEST, cut 1250"),
            ("AXO_6_NW_cut",   dict(bearing=315, el=40, z_cut=CUT), "camera NORTH-WEST, cut 1250"),
            ("AXO_7_N_low",    dict(bearing=  0, el=20, z_cut=H.P(1600)), "camera due NORTH, cut 1600")]
    for nm, kw, note in jobs:
        im = render(**kw)
        cv2.putText(im, f"{nm}   {note}   ORTHOGRAPHIC - balcony faces NORTH",
                    (14,26), cv2.FONT_HERSHEY_SIMPLEX, .50, (110,110,110), 1, cv2.LINE_AA)
        cv2.imwrite(f"out/{nm}.png", im); print("rendered", nm)
