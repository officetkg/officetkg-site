# -*- coding: utf-8 -*-
"""
室内パース CAMERA 1-4  (3D GEOMETRY APPROVED 後)

新しいシーンは作らない。build_model.py が geometry_master.py から
組み立てる **同一の 3D シーン** を読み込み、カメラだけを移動して
通常の透視投影レンダリングを行う。画像生成 AI は使用しない。

そのため構造上、
  壁が増える / Book Shelf が変わる / ベッドが出現する /
  家具が移動する / 部屋が広くなる
ことは起こり得ない (ジオメトリは A/B 承認時と同一バイト列)。

カメラ高   1550 mm        (指定 1500-1600)
レンズ     フルサイズ換算 30-32 mm  (指定 28-35 / 超広角禁止)
センサー   36 x 24 mm 相当、出力 1800 x 1200 (3:2)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import geometry_master as GM  # noqa: E402
from build_model import build  # noqa: E402
import softrender  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

EYE_H = 1550.0          # カメラ高
TGT_H = 1300.0          # 注視点高 (わずかに見下ろし)

# 透明度 (ガラスのみ)
ALPHA = {"WINDOW_GLASS": 0.20, "BALCONY_GLASS": 0.26}

CAMERAS = [
    dict(name="CAMERA_1_balcony_to_entrance",
         title="CAMERA 1  バルコニー側 -> 入口方向",
         eye=(2700.0, 900.0), target=(3450.0, 5250.0), focal=28.0),
    dict(name="CAMERA_2_entrance_to_balcony",
         title="CAMERA 2  入口側 -> バルコニー方向",
         eye=(3300.0, 5050.0), target=(2850.0, 800.0), focal=32.0),
    dict(name="CAMERA_3_meeting_to_workspace",
         title="CAMERA 3  ミーティングテーブル付近 -> 2 人用ワークスペース方向",
         eye=(3400.0, 3900.0), target=(600.0, 4150.0), focal=28.0),
    dict(name="CAMERA_4_workspace_to_LD",
         title="CAMERA 4  ワークスペース -> Living Dining 方向",
         eye=(1250.0, 3700.0), target=(3500.0, 1800.0), focal=30.0),
]


def collect():
    """承認済みシーンをそのまま三角形に展開する (除外なし)."""
    scene, meta = build()
    tris, rgb, alpha = [], [], []
    for name, geom in scene.geometry.items():
        f = np.asarray(geom.faces, int)
        tris.append(np.asarray(geom.vertices, float)[f])
        rgb.append(np.asarray(geom.visual.face_colors)[:, :3])
        alpha.append(np.full(len(f), ALPHA.get(name, 1.0)))
    return (np.concatenate(tris), np.concatenate(rgb).astype(np.uint8),
            np.concatenate(alpha), meta)


def main():
    os.makedirs(OUT, exist_ok=True)
    tris, rgb, alpha, meta = collect()
    print("scene: %d objects / %d triangles  (A/B 承認時と同一)"
          % (len(meta), len(tris)))
    print("方位: 平面 +Y = N%.0fE / バルコニー = S%.0fW\n"
          % (GM.PLAN_UP_BEARING_DEG, GM.PLAN_UP_BEARING_DEG))

    # 日射方向: バルコニー (南) から。PLAN_UP_BEARING_DEG を反映。
    th = np.radians(GM.PLAN_UP_BEARING_DEG)
    sun = (-np.sin(th) * 0.25 + np.cos(th) * 0.0,
           -np.cos(th) * 0.95, 0.30)

    for c in CAMERAS:
        eye = (c["eye"][0], c["eye"][1], EYE_H)
        tgt = (c["target"][0], c["target"][1], TGT_H)
        fov = 2 * np.degrees(np.arctan(18.0 / c["focal"]))
        img = softrender.render_perspective(
            tris, rgb, alpha, eye=eye, target=tgt, focal_mm=c["focal"],
            width=1800, height=1200, key=sun)
        p = os.path.join(OUT, c["name"] + ".png")
        Image.fromarray(img).save(p)
        d = np.hypot(tgt[0] - eye[0], tgt[1] - eye[1])
        print("%-58s" % c["title"])
        print("   eye (%5.0f, %5.0f, %4.0f) -> target (%5.0f, %5.0f, %4.0f)"
              % (eye + tgt))
        print("   焦点距離 %.0f mm (画角 %.1f deg 水平) / 注視距離 %.0f mm"
              % (c["focal"], fov, d))
        print("   -> %s\n" % p)


if __name__ == "__main__":
    main()
