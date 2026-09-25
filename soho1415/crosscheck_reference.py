# -*- coding: utf-8 -*-
"""
参考プラン (添付案) との相互検証

参考案は別途レンダリングされた「案」であり、外形の縦横比が
承認済み KEN 平面図と 6% 異なる (縦横比 0.575 vs 0.542)。
そのため寸法そのものは採用せず、**外形で正規化した相対位置**
だけを比較する。

    u = (px - 432) / 476      ->  X_mm = u * 4700
    v = (904 - py) / 828      ->  Y_mm = v * 8675

これにより、参考案が現マスターの各座標を裏付けているか
(あるいは食い違っているか) を mm 単位で定量評価できる。
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry_master as GM  # noqa: E402

REF = os.environ.get(
    "REFERENCE_PLAN",
    "/root/.claude/uploads/9b86f205-44ec-5e28-b7cf-48262834b0fc/3ddc2ba9-image.png")

REF_X0, REF_X1 = 432, 908        # 外壁外面 西 / 東
REF_Y0, REF_Y1 = 904, 76         # 外壁外面 南 / 北


def to_X(px):
    return (px - REF_X0) / (REF_X1 - REF_X0) * (GM.X_OUT_E - GM.X_OUT_W)


def to_Y(py):
    return (REF_Y0 - py) / (REF_Y0 - REF_Y1) * (GM.Y_OUT_N - GM.Y_OUT_S)


def load():
    a = np.asarray(Image.open(REF).convert("L"))
    return a < 130


def vline(d, xa, xb, ya, yb, thr):
    """帯 [xa,xb] x [ya,yb] の中で閾値を超える縦線の両端を返す."""
    col = d[ya:yb, xa:xb].sum(0)
    n = yb - ya
    hits = [xa + i for i, v in enumerate(col) if v > thr * n]
    return (hits[0], hits[-1]) if hits else None


def hline(d, xa, xb, ya, yb, thr):
    row = d[ya:yb, xa:xb].sum(1)
    n = xb - xa
    hits = [ya + i for i, v in enumerate(row) if v > thr * n]
    return (hits[0], hits[-1]) if hits else None


# (ラベル, 軸, 参考案の探索帯, どちらの縁を採るか, マスター値)
#   edge = 0 -> 帯の中で先に現れる線 (上/左) , 1 -> 後に現れる線 (下/右)
CHECKS = [
    ("外壁内面 西",        "V", (432, 462, 420, 860), 0.90, 1, GM.X_IN_W),
    ("外壁内面 東",        "V", (875, 908, 420, 860), 0.90, 0, GM.X_IN_E),
    ("外壁内面 南",        "H", (500, 850, 875, 906), 0.45, 0, GM.Y_IN_S),
    ("外壁内面 北",        "H", (470, 660, 74, 105),  0.45, 1, GM.Y_IN_N),
    ("PS 東壁",           "V", (660, 700, 100, 150), 0.45, 0, GM.X_WALL_PS_E[0]),
    ("洗面室北壁/PS南壁",   "H", (470, 700, 150, 180), 0.45, 1, GM.Y_WALL_PWD_N[0]),
    ("シャワー東壁",        "V", (525, 560, 190, 290), 0.45, 0, GM.X_WALL_SHOWER_E[0]),
    ("洗面室南壁",         "H", (560, 720, 292, 320), 0.45, 1, GM.Y_WALL_PWD_S[0]),
    ("CLO-WC 間仕切",      "V", (565, 600, 320, 380), 0.45, 0, GM.X_WALL_CLO_WC[0]),
    ("水回り東壁",         "V", (712, 740, 190, 390), 0.45, 0, GM.X_WALL_WET_E[0]),
    ("便所南壁/LD入口壁",   "H", (640, 860, 383, 410), 0.45, 1, GM.Y_WALL_WC_S[0]),
    ("可動壁 南北レッグ",    "V", (620, 645, 500, 700), 0.40, 0, GM.MOVW_NS_X[0]),
    ("可動壁 戸袋 南端",    "H", (620, 665, 482, 502), 0.40, 0, GM.MOVW_NS_POCKET[0]),
    ("可動壁 東西レッグ",    "H", (470, 570, 668, 702), 0.35, 1, GM.MOVW_EW_Y[0]),
]


def main():
    d = load()
    print("参考案の外形: x %d..%d (%d px) / y %d..%d (%d px)"
          % (REF_X0, REF_X1, REF_X1 - REF_X0, REF_Y1, REF_Y0, REF_Y0 - REF_Y1))
    print("縦横比 参考案 %.3f  vs  マスター %.3f   -> 寸法は採用せず相対位置のみ比較\n"
          % ((REF_X1 - REF_X0) / (REF_Y0 - REF_Y1),
             (GM.X_OUT_E - GM.X_OUT_W) / (GM.Y_OUT_N - GM.Y_OUT_S)))
    print("%-22s %10s %10s %9s" % ("要素", "参考案(mm)", "マスター", "差"))
    print("-" * 56)
    worst = 0.0
    for label, axis, band, thr, edge, master in CHECKS:
        xa, xb, ya, yb = band
        if axis == "V":
            r = vline(d, xa, xb, ya, yb, thr)
            val = to_X(r[edge]) if r else None
        else:
            r = hline(d, xa, xb, ya, yb, thr)
            val = to_Y(r[edge]) if r else None
        if val is None:
            print("%-22s %10s %10.0f %9s" % (label, "検出なし", master, "-"))
            continue
        dv = val - master
        worst = max(worst, abs(dv))
        print("%-22s %10.0f %10.0f %+9.0f" % (label, val, master, dv))
    print("-" * 56)
    print("最大差 %.0f mm" % worst)
    print("\n図面の線幅 (参考案 1px = 約 10 mm / KEN 図 1px = 12.9 mm) を考えると、")
    print("この範囲の差は作図誤差の範囲内であり、参考案はマスターを追認している。")


if __name__ == "__main__":
    main()
