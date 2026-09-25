# -*- coding: utf-8 -*-
"""
モデル検証レンダリング (A / B) + 承認済み平面図との重ね合わせ

A. 承認済みモデルと同方向の ORTHOGRAPHIC / AXONOMETRIC VIEW
B. 完全真上からの ORTHOGRAPHIC TOP VIEW
C. B と承認済み平面図の重ね合わせ (XY 一致検証)

いずれも画像生成ではなく、build_model.py が作った実ジオメトリの
三角形をそのままラスタライズしたものである。
"""
import os
import sys

import numpy as np
from PIL import Image

import geometry_master as GM
from build_model import build
import softrender

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# 承認済み平面図 (KEN 物件資料 p.3) と、その中の座標原点
# 指定家具配置図 (FURNITURE CONTACT & CLEARANCE REVIEW)
FURNITURE_PLAN = os.environ.get(
    "FURNITURE_PLAN",
    "/root/.claude/uploads/9b86f205-44ec-5e28-b7cf-48262834b0fc/82ab60a7-image.png")
FURN_X0, FURN_X1 = 321, 1089      # 外壁外面 西 / 東 (px)
FURN_Y0, FURN_Y1 = 1735, 318      # 外壁外面 南 / 北 (px)

APPROVED_PLAN = os.environ.get(
    "APPROVED_PLAN",
    "/root/.claude/uploads/9b86f205-44ec-5e28-b7cf-48262834b0fc/3241b6ab-image.png")
PLAN_ORIGIN_PX = GM.PX_ORIGIN          # (643, 942) -> X=0, Y=0
PLAN_MM_PER_PX = GM.PX_TO_MM           # 12.875


def collect(exclude=()):
    scene, meta = build()
    tris, rgb, oid = [], [], []
    names = []
    for i, (name, geom) in enumerate(scene.geometry.items()):
        if name in exclude:
            continue
        v = np.asarray(geom.vertices, float)
        f = np.asarray(geom.faces, int)
        t = v[f]
        c = np.asarray(geom.visual.face_colors)[:, :3]
        tris.append(t)
        rgb.append(c)
        oid.append(np.full(len(f), len(names)))
        names.append(name)
    return (np.concatenate(tris), np.concatenate(rgb).astype(np.uint8),
            np.concatenate(oid), names)


def view_a():
    tris, rgb, oid, _ = collect(exclude=("CEILING",))
    img, _ = softrender.render(
        tris, rgb, oid,
        eye_dir=(0.40, -0.42, 0.815),     # 平面図と同じ向き(北が上)を保った俯瞰アクソメ
        width=2000, height=2400, margin=0.05,
        light=(0.40, -0.50, 0.77))
    p = os.path.join(OUT, "view_A_axonometric.png")
    Image.fromarray(img).save(p)
    return p


def view_b(px_per_mm=0.31):
    tris, rgb, oid, _ = collect(exclude=("CEILING",))
    cx = (GM.X_OUT_W + GM.X_OUT_E) / 2.0
    cy = (GM.BAL_Y_OUT + GM.Y_OUT_N) / 2.0
    w = int(round((GM.X_OUT_E - GM.X_OUT_W + 900) * px_per_mm))
    h = int(round((GM.Y_OUT_N - GM.BAL_Y_OUT + 900) * px_per_mm))
    img, k = softrender.render(
        tris, rgb, oid,
        eye_dir=(0.0, 0.0, 1.0), up_hint=(0, 1, 0),
        width=w, height=h, px_per_mm=px_per_mm, center=(cx, cy, 0),
        light=(0.30, -0.45, 0.84))
    p = os.path.join(OUT, "view_B_top_ortho.png")
    Image.fromarray(img).save(p)
    return p, (img, k, cx, cy, w, h)


def view_b_walls(px_per_mm):
    """重ね合わせ用: 床スラブを除いた立ち上がり部材のみの真上投影."""
    tris, rgb, oid, _ = collect(exclude=("CEILING", "FLOOR_SLAB", "BALCONY_SLAB"))
    cx = (GM.X_OUT_W + GM.X_OUT_E) / 2.0
    cy = (GM.BAL_Y_OUT + GM.Y_OUT_N) / 2.0
    w = int(round((GM.X_OUT_E - GM.X_OUT_W + 900) * px_per_mm))
    h = int(round((GM.Y_OUT_N - GM.BAL_Y_OUT + 900) * px_per_mm))
    img, k = softrender.render(
        tris, rgb, oid, eye_dir=(0.0, 0.0, 1.0), up_hint=(0, 1, 0),
        width=w, height=h, px_per_mm=px_per_mm, center=(cx, cy, 0),
        outline=False)
    return img, k, cx, cy, w, h


def overlay(bdata):
    """B を承認済み平面図と同一縮尺・同一原点に合わせて重ねる."""
    _, k0, _, _, _, _ = bdata
    img, k, cx, cy, w, h = view_b_walls(k0)
    if not os.path.exists(APPROVED_PLAN):
        print("!! approved plan image not found, skipping overlay")
        return None
    plan = Image.open(APPROVED_PLAN).convert("L")

    # 平面図を モデル画素尺度 に合わせて拡大
    f = k * PLAN_MM_PER_PX                      # plan px -> model px
    pw, ph = plan.size
    plan_s = plan.resize((int(pw * f), int(ph * f)), Image.LANCZOS)

    # 原点 (X=0,Y=0) の位置を両者で合わせる
    ox_model = w * 0.5 + (0.0 - cx) * k
    oy_model = h * 0.5 - (0.0 - cy) * k
    ox_plan = PLAN_ORIGIN_PX[0] * f
    oy_plan = PLAN_ORIGIN_PX[1] * f
    dx = int(round(ox_model - ox_plan))
    dy = int(round(oy_model - oy_plan))

    base = Image.new("L", (w, h), 255)
    base.paste(plan_s, (dx, dy))
    base = np.asarray(base).astype(np.float32)

    # モデル側の輪郭 (背景でない画素の縁) を赤で重ねる
    m = np.asarray(Image.fromarray(img).convert("L")).astype(np.float32)
    solid = m < 248
    edge = np.zeros_like(solid)
    edge[:, 1:] |= solid[:, 1:] != solid[:, :-1]
    edge[1:, :] |= solid[1:, :] != solid[:-1, :]
    # 内部の面も薄く見せる
    out = np.stack([base, base, base], -1)
    out[solid] = out[solid] * 0.80 + np.array([255, 60, 60], np.float32) * 0.20
    out[edge] = np.array([210, 0, 0], np.float32)

    p = os.path.join(OUT, "view_C_overlay_vs_approved_plan.png")
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(p)
    return p


def overlay_furniture():
    """指定家具配置図に、モデルの家具だけを重ねて位置一致を確認する."""
    if not os.path.exists(FURNITURE_PLAN):
        print("!! furniture plan not found, skipping")
        return None
    src = Image.open(FURNITURE_PLAN).convert("L")
    w, h = src.size
    k = (FURN_X1 - FURN_X0) / (GM.X_OUT_E - GM.X_OUT_W)      # px per mm

    furn = ("DESK_2P", "TASK_CHAIR_1", "TASK_CHAIR_2", "MEETING_TABLE",
            "MTG_CHAIR_W1", "MTG_CHAIR_W2", "MTG_CHAIR_E1", "MTG_CHAIR_E2",
            "MTG_CHAIR_N", "MTG_CHAIR_S", "MONITOR_55", "STORAGE_04")
    scene, _ = build()
    keep = [n for n in scene.geometry if n in furn]
    tris, rgb, oid = [], [], []
    for i, n in enumerate(keep):
        g = scene.geometry[n]
        f = np.asarray(g.faces, int)
        tris.append(np.asarray(g.vertices, float)[f])
        rgb.append(np.asarray(g.visual.face_colors)[:, :3])
        oid.append(np.full(len(f), i))
    tris = np.concatenate(tris)

    cx = (GM.X_OUT_W + GM.X_OUT_E) / 2.0
    cy = (GM.Y_OUT_S + GM.Y_OUT_N) / 2.0
    img, _ = softrender.render(
        tris, np.concatenate(rgb).astype(np.uint8), np.concatenate(oid),
        eye_dir=(0, 0, 1), up_hint=(0, 1, 0),
        width=w, height=h, px_per_mm=k, outline=False,
        center=(cx, cy, 0))
    # モデル画像の中心は外形中心。図面上の外形中心 px に平行移動する。
    dx = int(round((FURN_X0 + FURN_X1) / 2.0 - w / 2.0))
    dy = int(round((FURN_Y0 + FURN_Y1) / 2.0 - h / 2.0))
    shifted = Image.fromarray(img).transform(
        (w, h), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=(252, 252, 250))

    m = np.asarray(shifted.convert("L")).astype(np.float32)
    solid = m < 248
    base = np.asarray(src).astype(np.float32)
    out = np.stack([base, base, base], -1)
    out[solid] = out[solid] * 0.45 + np.array([0, 90, 230], np.float32) * 0.55
    p = os.path.join(OUT, "view_D_overlay_vs_furniture_plan.png")
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(p)
    return p


def check_xy_lock():
    """XY LOCK の自己検証: 全オブジェクトが外形 + バルコニー内に収まるか."""
    scene, meta = build()
    bad = []
    for m in meta:
        x0, y0, _ = m["bbox_min"]
        x1, y1, _ = m["bbox_max"]
        if x0 < GM.X_OUT_W - 1 or x1 > GM.X_OUT_E + 1:
            if m["object"] not in ("COLUMN_SE", "COLUMN_NE"):
                bad.append((m["object"], "X", x0, x1))
        if y0 < GM.BAL_Y_OUT - 21 or y1 > GM.Y_OUT_N + 1:   # -20 は笠木の出
            if m["object"] not in ("COLUMN_NE",):
                bad.append((m["object"], "Y", y0, y1))
    return bad


FORBIDDEN = ["BED", "SOFA", "LOUNGE", "COFFEE_TABLE", "SIDEBOARD", "CABINET_ADD",
             "SHELF_ADD", "WALL_ADD", "WINDOW_ADD", "DOOR_ADD"]


def check_forbidden():
    _, meta = build()
    names = [m["object"].upper() for m in meta]
    hit = [n for n in names for f in FORBIDDEN if f in n]
    shelf = [m for m in meta if "BOOK_SHELF" in m["object"]]
    return hit, shelf


def main():
    os.makedirs(OUT, exist_ok=True)
    print("rendering A ...")
    pa = view_a()
    print("  ->", pa)
    print("rendering B ...")
    pb, bdata = view_b()
    print("  ->", pb)
    print("overlay C ...")
    pc = overlay(bdata)
    print("  ->", pc)
    print("overlay D (指定家具配置図) ...")
    pd = overlay_furniture()
    print("  ->", pd)

    print("\n--- XY LOCK check ---")
    bad = check_xy_lock()
    print("out-of-envelope objects:", bad if bad else "none")

    hit, shelf = check_forbidden()
    print("\n--- forbidden object check ---")
    print("forbidden names found:", hit if hit else "none")
    for s in shelf:
        bs = GM.BOOK_SHELF
        print("BOOK SHELF bbox:", s["bbox_min"], s["bbox_max"],
              "| master XY:", (bs["x0"], bs["x1"], bs["y0"], bs["y1"]),
              "| 大型化なし" if (abs(s["bbox_min"][0] - bs["x0"]) < 1 and
                                abs(s["bbox_max"][0] - bs["x1"]) < 1 and
                                abs(s["bbox_min"][1] - bs["y0"]) < 1 and
                                abs(s["bbox_max"][1] - bs["y1"]) < 1) else "!! CHANGED")

    print("\n--- movable wall (bedroom partition) ---")
    mw = [m for m in build()[1] if m["object"] == "MOVABLE_WALL"][0]
    print("state: %s (L 字)" % GM.MOVABLE_WALL_STATE)
    print("  南北レッグ 開口 Y %.0f-%.0f (%.0f mm) 素通し | 戸袋 Y %.0f-%.0f (%d 枚)"
          % (GM.MOVW_NS_TRAVEL[0], GM.MOVW_NS_TRAVEL[1],
             GM.MOVW_NS_TRAVEL[1] - GM.MOVW_NS_TRAVEL[0],
             GM.MOVW_NS_POCKET[0], GM.MOVW_NS_POCKET[1], GM.MOVW_NS_PANELS))
    print("  東西レッグ 開口 X %.0f-%.0f (%.0f mm) 素通し | 戸袋 X %.0f-%.0f (%d 枚)"
          % (GM.MOVW_EW_TRAVEL[0], GM.MOVW_EW_TRAVEL[1],
             GM.MOVW_EW_TRAVEL[1] - GM.MOVW_EW_TRAVEL[0],
             GM.MOVW_EW_POCKET[0], GM.MOVW_EW_POCKET[1], GM.MOVW_EW_PANELS))
    print("object bbox (panels + rail):", mw["bbox_min"], mw["bbox_max"])

    print("\n--- clearance check (指定家具配置図の主旨) ---")
    bb = {m["object"]: (m["bbox_min"], m["bbox_max"]) for m in build()[1]}

    def gap(a_obj, a_edge, b_val, axis, label):
        lo, hi = bb[a_obj]
        i = 0 if axis == "X" else 1
        v = hi[i] if a_edge == "max" else lo[i]
        print("  %-38s %6.0f mm" % (label, abs(b_val - v)))

    gap("DESK_2P", "min", GM.X_IN_W, "X", "デスク西端 -> 西壁内面 (flush 指示)")
    gap("TASK_CHAIR_1", "max", GM.MOVW_NS_X[0] + 30, "X",
        "執務チェア東端 -> 可動壁レール")
    gap("MTG_CHAIR_S", "min", GM.Y_IN_S, "Y", "会議チェア(南)南端 -> 南壁内面")
    gap("MTG_CHAIR_E1", "max", GM.FURNITURE_XY_LOCK["MONITOR_55"]["wall_x"] - 60,
        "X", "会議チェア(東)東端 -> ディスプレイ面")
    gap("MTG_CHAIR_W1", "min", GM.MOVW_NS_X[1], "X", "会議チェア(西)西端 -> 可動壁ゾーン")
    gap("MEETING_TABLE", "max", GM.X_IN_E, "X", "テーブル東端 -> 東壁内面")

    a = GM.areas()
    print("\n--- area check ---")
    print("gross   %.2f m2 (spec 40.76)  diff %+.2f%%"
          % (a["gross_m2"], (a["gross_m2"] / 40.76 - 1) * 100))
    print("balcony %.2f m2 (spec 6.40)   diff %+.2f%%"
          % (a["balcony_m2"], (a["balcony_m2"] / 6.40 - 1) * 100))


if __name__ == "__main__":
    sys.exit(main())
