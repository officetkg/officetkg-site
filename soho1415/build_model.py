# -*- coding: utf-8 -*-
"""
GEOMETRY MASTER -> 実 3D シーン (trimesh)

geometry_master.py の XY をそのまま使用し、Z のみを与えて立体化する。
各要素は独立したオブジェクトとして Scene に登録される。
出力: out/soho1415_master.glb / .obj / out/objects.json
"""
import json
import os

import numpy as np
import trimesh

import geometry_master as GM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

GROUP_COLOR = {
    "外周壁":            (214, 210, 202),
    "内壁":              (226, 222, 214),
    "柱":                (188, 184, 176),
    "バルコニー床":      (176, 174, 170),
    "バルコニー手摺":    (150, 166, 178),
    "玄関":              (168, 160, 150),
    "PS":                (200, 196, 190),
    "SC":                (198, 174, 146),
    "Powder Room":       (224, 224, 226),
    "Shower":            (196, 210, 216),
    "W/D":               (232, 232, 232),
    "Toilet":            (238, 238, 238),
    "Kitchen":           (206, 182, 152),
    "Refrigerator":      (214, 214, 216),
    "Closet":            (198, 174, 146),
    "既存Book Shelf":    (186, 154, 116),
    "可動収納壁／レール": (205, 186, 162),
    "窓／サッシ":        (168, 190, 200),
    "2人用ワークデスク":  (152, 120,  86),
    "執務チェア2脚":      ( 74,  80,  88),
    "6人用ミーティングテーブル": (152, 120, 86),
    "会議チェア6脚":      ( 92,  98, 106),
    "55インチモニター":   ( 46,  48,  52),
    "床・天井":          (238, 236, 232),
}


def _box(b):
    x0, x1, y0, y1, z0, z1 = b
    ext = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    if min(ext) <= 0:
        return None
    T = trimesh.transformations.translation_matrix(
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    return trimesh.creation.box(extents=ext, transform=T)


def _cyl(c):
    h = c["z1"] - c["z0"]
    if h <= 0 or c["r"] <= 0:
        return None
    T = trimesh.transformations.translation_matrix(
        (c["cx"], c["cy"], (c["z0"] + c["z1"]) / 2.0))
    return trimesh.creation.cylinder(radius=c["r"], height=h, sections=24,
                                     transform=T)


def build():
    scene = trimesh.Scene()
    meta = []
    for p in GM.parts():
        pieces = [m for m in (_box(b) for b in p["boxes"]) if m is not None]
        pieces += [m for m in (_cyl(c) for c in p["cylinders"]) if m is not None]
        if not pieces:
            continue
        mesh = trimesh.util.concatenate(pieces)
        rgb = p.get("color") or GROUP_COLOR.get(p["group"], (200, 200, 200))
        mesh.visual.face_colors = np.tile(np.array(rgb + (255,), np.uint8),
                                          (len(mesh.faces), 1))
        mesh.metadata["group"] = p["group"]
        scene.add_geometry(mesh, node_name=p["object"], geom_name=p["object"])
        b = mesh.bounds
        meta.append(dict(object=p["object"], group=p["group"],
                         bbox_min=[round(float(v), 1) for v in b[0]],
                         bbox_max=[round(float(v), 1) for v in b[1]],
                         triangles=int(len(mesh.faces))))
    return scene, meta


def main():
    os.makedirs(OUT, exist_ok=True)
    scene, meta = build()
    scene.export(os.path.join(OUT, "soho1415_master.glb"))
    with open(os.path.join(OUT, "objects.json"), "w", encoding="utf-8") as f:
        json.dump(dict(unit="mm",
                       coordinate_system="X=east(plan right), Y=north(plan up), Z=up, FL=0",
                       areas=GM.areas(), objects=meta), f,
                  ensure_ascii=False, indent=2)

    print("objects : %d" % len(meta))
    print("faces   : %d" % sum(m["triangles"] for m in meta))
    a = GM.areas()
    print("gross   : %.2f m2 (spec 40.76)" % a["gross_m2"])
    print("balcony : %.2f m2 (spec 6.40)" % a["balcony_m2"])
    print("-> out/soho1415_master.glb")
    groups = {}
    for m in meta:
        groups.setdefault(m["group"], []).append(m["object"])
    for g in GROUP_COLOR:
        if g in groups:
            print("  [%-22s] %s" % (g, ", ".join(groups[g])))


if __name__ == "__main__":
    main()
