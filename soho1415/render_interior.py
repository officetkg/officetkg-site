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

# ---------------------------------------------------------------------
# 照明 (工程 "光" -- ジオメトリは変更しない)
#
# 竣工写真の天井を実測すると、LD は折上げ天井でダウンライトが
# **ペア** で周囲のバンドに多数入っている。熱感知器も 1 個見える。
# 照明「器具」の造形はジオメトリ変更にあたるため作っていない。
# ここで与えているのは光源位置と配光だけである。
# 電気図が入手できれば下の座標を差し替えればよい。
# ---------------------------------------------------------------------
DL_Z = 2430.0
DL_WARM = (1.00, 0.91, 0.79)     # 電球色 3000K 相当


def _pair(x, y, axis="x", gap=260.0, inten=1.9):
    o = gap / 2.0
    if axis == "x":
        pts = [(x - o, y), (x + o, y)]
    else:
        pts = [(x, y - o), (x, y + o)]
    return [dict(pos=(px, py, DL_Z), color=DL_WARM, intensity=inten) for px, py in pts]


DOWNLIGHTS = (
    # Living Dining : 周囲バンドにペア配置
    _pair(2700, 1000) + _pair(3900, 1000)
    + _pair(2600, 2300) + _pair(3900, 2300)
    + _pair(2700, 4300) + _pair(3900, 4300)
    # 西ベイ (Book Shelf 側)
    + _pair(800, 900, "y") + _pair(800, 1900, "y")
    # ワークスペース (Master Bedroom 側)
    + _pair(750, 3150, "y") + _pair(750, 4450, "y")
    # 廊下・キッチン
    + _pair(3350, 5900) + _pair(4100, 6850) + _pair(3350, 7850)
    # 水回り・玄関
    + [dict(pos=(1900, 6900, 2180.0), color=DL_WARM, intensity=2.0),
       dict(pos=(2100, 5750, 2180.0), color=DL_WARM, intensity=1.4),
       dict(pos=(580, 7000, 1980.0), color=DL_WARM, intensity=1.6),
       dict(pos=(3500, 8100, 2180.0), color=DL_WARM, intensity=2.0)]
)

# 掃き出し窓を面光源として扱う (室内の主光源)
WINDOW_PORTAL = dict(
    center=((GM.OPEN_WINDOW[0] + GM.OPEN_WINDOW[1]) / 2.0, 120.0,
            GM.WIN_HEAD / 2.0),
    normal=(0.0, -1.0, 0.0),
    size=(GM.OPEN_WINDOW[1] - GM.OPEN_WINDOW[0]) * GM.WIN_HEAD / 1.0e6,  # m2
    color=(1.00, 1.00, 1.04),     # 昼光 (北向きの空 = ニュートラル)
    intensity=13.0)

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
    n_src = len(tris)
    tris, rgb, alpha = softrender.tessellate(tris, rgb, alpha, max_edge=380.0)
    print("scene: %d objects / %d triangles  (A/B 承認時と同一)" % (len(meta), n_src))
    print("照明用に %d 面へ細分 (形状は不変) / 光源 %d 灯 + 窓 %.1f m2"
          % (len(tris), len(DOWNLIGHTS), WINDOW_PORTAL["size"]))
    lit = softrender.light_vertices(tris, rgb, WINDOW_PORTAL, DOWNLIGHTS,
                                    exposure=1.0)
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
            width=1800, height=1200, prelit=True, vertex_rgb=lit,
            bg_top=(196, 214, 236), bg_bot=(236, 241, 244))
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
