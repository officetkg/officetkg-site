# -*- coding: utf-8 -*-
"""
SOHO / 1415  ORTHOGRAPHIC COORDINATE MODEL  --  GEOMETRY MASTER
================================================================

OIMACHI TRACKS RESIDENCE (SOHO フロア) 1415 号室
物件番号 2025110085 / 1LDK / 専有面積 40.76 m2 / バルコニー 6.4 m2 / 14F

このファイルが唯一の座標マスターである。
THIS FILE IS THE SINGLE SOURCE OF TRUTH FOR ALL XY COORDINATES.

    X = LOCK        (mm, 平面図の右方向 = 東)
    Y = LOCK        (mm, 平面図の上方向 = 北)
    Z = 追加分のみ   (mm, 床仕上面 FL = 0)

承認済みモデル(平面)からの座標取得方法 / HOW XY WAS DERIVED
-----------------------------------------------------------
承認済み平面図画像のピクセル座標を投影プロファイル(dark-line detection)で
実測し、次の一次変換で mm に変換した。

    X_mm = (px_x - 643) * 12.875
    Y_mm = (942 - px_y) * 12.875

原点   : 平面図左下(南西)外壁外面の交点
縮尺   : 12.875 mm/px

縮尺の検証 (SCALE VERIFICATION)
    外形     4700 mm x 8675 mm = 40.77 m2   <-> 表記 専有面積 40.76 m2   (+0.02%)
    バルコニー 4700 mm x 1385 mm =  6.51 m2   <-> 表記 バルコニー  6.4 m2   (+1.7%)
    2 つの独立した面積がともに一致するため、縮尺は確定とみなす。

Z 値について / ABOUT Z
    平面図は Z を持たないため、Z のみを新規に与えた。
    Z を与える際に XY を一切変更していない。
    CH 2450 (居室) / 2200 (水回り・玄関) は一般的なマンション天井高。

家具の XY について / FURNITURE XY  -- 要確認 / NEEDS CONFIRMATION
    本セッションに添付されたのは KEN 物件資料 PDF の 3 ページ
    (内観写真 2 枚 + 平面図 1 枚) のみで、家具位置を確定した
    「承認済み ORTHOGRAPHIC COORDINATE MODEL」の画像は含まれていない。
    したがって建築躯体の XY は平面図から実測して確定しているが、
    家具 (ワークデスク / チェア / ミーティングテーブル / モニター) の XY は
    下の FURNITURE_XY_LOCK ブロックで暫定値として定義している。
    承認済みモデルの値が判明した場合、このブロックの数値だけを
    差し替えれば他は一切変更不要。
"""

# =====================================================================
#  0.  GLOBAL
# =====================================================================
MM = 1.0
PX_TO_MM = 12.875
PX_ORIGIN = (643, 942)          # (px_x, px_y) -> (X=0, Y=0)

FL            = 0               # 床仕上面
CH_MAIN       = 2450            # 居室天井高
CH_WET        = 2200            # 水回り・玄関・廊下天井高
SLAB_TOP      = 2650            # スラブ上端 (天井懐 200)
DOOR_H        = 2000            # 建具開口高
WIN_HEAD      = 2100            # 掃き出し窓 上端
BAL_FL        = -150            # バルコニー床レベル (室内 FL からの段差)
BAL_RAIL_TOP  = 1050            # 手摺天端 (バルコニー床 +1200)
GENKAN_FL     = -120            # 玄関土間レベル

# =====================================================================
#  1.  ENVELOPE  --  X / Y LOCK
# =====================================================================
X_OUT_W, X_OUT_E = 0.0, 4700.0          # 外壁外面 西 / 東
Y_OUT_S, Y_OUT_N = 0.0, 8675.0          # 外壁外面 南(バルコニー側) / 北(共用廊下側)

X_IN_W,  X_IN_E  = 195.0, 4495.0        # 外壁内面 西 / 東
Y_IN_S,  Y_IN_N  = 195.0, 8495.0        # 外壁内面 南 / 北

BAL_Y_OUT = -1385.0                     # バルコニー先端(手摺芯)

W_EXT = 195.0                           # 外壁厚
W_INT = 90.0                            # 内壁厚

# ---- 主要内壁ライン (実測値) -------------------------------------------------
Y_WALL_MBR_S   = (2320.0, 2410.0)       # MBR 南壁               px y 755-759
Y_WALL_WC_S    = (5280.0, 5370.0)       # 便所南壁 / LD-廊下間仕切 px y 523-528
Y_CLO_S, Y_CLO_N = 5600.0, 6180.0       # クローゼット           px y 507-462
Y_WALL_PWD_S   = (6180.0, 6270.0)       # 洗面室南壁             px y 462
Y_SHOWER_S     = (6180.0, 6465.0)       # シャワー南側 PS/チェース px y 462-440
Y_WALL_PWD_N   = (7620.0, 7710.0)       # 洗面室北壁 / PS 南壁    px y 347-340

X_WALL_SHOWER_E = (966.0, 1056.0)       # シャワー東壁           px x 718-725
X_WALL_CLO_WC   = (1365.0, 1465.0)      # CLO-WC 間              px x 750-755
X_WALL_MBR_E    = (1975.0, 2095.0)      # MBR / LD 間仕切(可動壁) px x 795-807
X_WALL_PS_E     = (2405.0, 2495.0)      # PS 東壁                px x 830-840
X_WALL_WET_E    = (2835.0, 2925.0)      # 洗面・便所 東壁         px x 863-870

# ---- 開口 ------------------------------------------------------------------
OPEN_ENTRANCE_DOOR = (3010.0, 3810.0)   # 玄関ドア (北外壁)       px x 877-937
OPEN_LD_DOOR       = (2925.0, 3785.0)   # LD 入口ドア (Y_WALL_WC_S)
OPEN_WC_DOOR       = (5470.0, 6180.0)   # 便所ドア (X_WALL_WET_E)
OPEN_PWD_DOOR      = (6900.0, 7620.0)   # 洗面室ドア (X_WALL_WET_E)
OPEN_SHOWER_DOOR   = (6860.0, 7560.0)   # シャワードア (X_WALL_SHOWER_E)
OPEN_WINDOW        = (1740.0, 4080.0)   # 掃き出し窓 (南外壁)     px x 778-960

# =====================================================================
#  2.  FURNITURE  XY  LOCK   ( ※暫定値 -- 上記ヘッダ参照 )
# =====================================================================
FURNITURE_XY_LOCK = {
    # 2 人用ワークデスク : 1600 x 700 / バルコニーを向いて着座
    "DESK_2P":        dict(x0=500.0,  x1=2100.0, y0=430.0,  y1=1130.0),
    "TASK_CHAIR_1":   dict(cx=900.0,  cy=1500.0, facing="S"),
    "TASK_CHAIR_2":   dict(cx=1700.0, cy=1500.0, facing="S"),

    # 6 人用ミーティングテーブル : 1000 x 2100
    "MEETING_TABLE":  dict(x0=2900.0, x1=3900.0, y0=1350.0, y1=3450.0),
    "MTG_CHAIR_W1":   dict(cx=2620.0, cy=1875.0, facing="E"),
    "MTG_CHAIR_W2":   dict(cx=2620.0, cy=2925.0, facing="E"),
    "MTG_CHAIR_E1":   dict(cx=4180.0, cy=1875.0, facing="W"),
    "MTG_CHAIR_E2":   dict(cx=4180.0, cy=2925.0, facing="W"),
    "MTG_CHAIR_S":    dict(cx=3400.0, cy=1050.0, facing="N"),
    "MTG_CHAIR_N":    dict(cx=3400.0, cy=3750.0, facing="S"),

    # 55 インチモニター : 有効画面 1218 x 685 / 南(テーブル側)を向く
    "MONITOR_55":     dict(cx=3400.0, cy=4300.0, facing="S"),
}

# ---------------------------------------------------------------------
# 可動収納壁 (ベッドルーム間仕切) -- L 字 / 常時開放
#
# 平面図実測 (投影プロファイルによる画素実測):
#   南北レッグ (MBR 東側)
#     建具ライン x=799 (X 2008) / 吊り金物 y 651-654, 696-700
#     戸袋(破線) y 551-606        -> Y 4330-5035 (705)
#     走行範囲                    -> Y 2360-4330 (1970) = 3 枚 x 657
#   東西レッグ (MBR 南側)
#     建具ライン y=759,762        -> Y 2318-2356 (薄い引戸の二重線)
#     戸袋(破線) x 658-709        -> X  195- 850 (655)
#     走行範囲                    -> X  850-1975 (1125) = 2 枚 x 563
#
#   2 本のレッグは MBR 南東コーナーで直交し、戸袋はそれぞれコーナーから
#   最も遠い端 (北端 / 西端) にある。両方を引き込むとコーナーが完全に開き、
#   MBR は南側と東側の 2 面が開放される = L 字開放。
#
#   ※ 旧版ではこの東西レッグを固定内壁と誤判断していた。躯体壁ではない。
#
#   MOVABLE_WALL_STATE = "OPEN"   -> 常時開放 (既定)
#                        "CLOSED" -> 参考用
#   いずれの状態でもレール・戸袋・袖壁の XY は不変。
# ---------------------------------------------------------------------
MOVABLE_WALL_STATE = "OPEN"          # ベッドルーム間仕切壁は常時開放 (L 字)

# 南北レッグ (MBR 東側)
MOVW_NS_X       = (1975.0, 2095.0)   # 建具ゾーン
MOVW_NS_LANES   = [(1983.0, 2015.0), (2023.0, 2055.0), (2063.0, 2095.0)]
MOVW_NS_TRAVEL  = (2360.0, 4330.0)   # 閉時に塞ぐ範囲
MOVW_NS_POCKET  = (4330.0, 5035.0)   # 戸袋 (北端)
MOVW_NS_PANELS  = 3

# 東西レッグ (MBR 南側)
MOVW_EW_Y       = (2290.0, 2360.0)   # 建具ゾーン
MOVW_EW_LANES   = [(2292.0, 2324.0), (2328.0, 2360.0)]
MOVW_EW_TRAVEL  = (850.0, 1975.0)    # 閉時に塞ぐ範囲
MOVW_EW_POCKET  = (195.0, 850.0)     # 戸袋 (西端)
MOVW_EW_PANELS  = 2

MOVW_PANEL_H    = 2400.0
MOVW_PIER_Y     = (5035.0, 5280.0)   # 北端の固定袖壁

# 既存 Book Shelf : 承認済み平面図の実測値 -- 変更禁止
BOOK_SHELF = dict(x0=205.0, x1=490.0, y0=425.0, y1=2190.0, z1=2100.0,
                  dividers_y=[785.0, 1146.0, 1481.0, 1828.0])


# =====================================================================
#  3.  PART LIST BUILDER
# =====================================================================
def _b(x0, x1, y0, y1, z0, z1):
    return (float(x0), float(x1), float(y0), float(y1), float(z0), float(z1))


def _task_chair(cx, cy, facing):
    """執務チェア : 円盤ベース + 支柱 + 座 + 背."""
    boxes, cyls = [], []
    cyls.append(dict(r=320, z0=0, z1=60, cx=cx, cy=cy))
    cyls.append(dict(r=45, z0=60, z1=420, cx=cx, cy=cy))
    boxes.append(_b(cx - 240, cx + 240, cy - 240, cy + 240, 420, 500))
    d = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[facing]
    bx, by = cx - d[0] * 240, cy - d[1] * 240
    if d[0]:
        boxes.append(_b(bx - 30, bx + 30, cy - 240, cy + 240, 500, 1060))
    else:
        boxes.append(_b(cx - 240, cx + 240, by - 30, by + 30, 500, 1060))
    # 肘掛
    for s in (-1, 1):
        if d[0]:
            boxes.append(_b(cx - 180, cx + 180, cy + s * 235 - 25, cy + s * 235 + 25, 500, 660))
        else:
            boxes.append(_b(cx + s * 235 - 25, cx + s * 235 + 25, cy - 180, cy + 180, 500, 660))
    return boxes, cyls


def _meeting_chair(cx, cy, facing):
    """会議チェア : 4 本脚 + 座 + 背."""
    boxes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            boxes.append(_b(cx + sx * 200 - 20, cx + sx * 200 + 20,
                            cy + sy * 200 - 20, cy + sy * 200 + 20, 0, 430))
    boxes.append(_b(cx - 230, cx + 230, cy - 230, cy + 230, 430, 470))
    d = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[facing]
    bx, by = cx - d[0] * 230, cy - d[1] * 230
    if d[0]:
        boxes.append(_b(bx - 25, bx + 25, cy - 230, cy + 230, 470, 900))
    else:
        boxes.append(_b(cx - 230, cx + 230, by - 25, by + 25, 470, 900))
    return boxes, []


def parts():
    """全オブジェクトを独立したパーツとして返す.

    returns: list of dict(object=..., group=..., boxes=[...], cylinders=[...])
    """
    P = []

    def add(obj, group, boxes, cylinders=None):
        P.append(dict(object=obj, group=group, boxes=list(boxes),
                      cylinders=list(cylinders or [])))

    # -----------------------------------------------------------------
    # 外周壁  EXTERIOR WALLS
    # -----------------------------------------------------------------
    add("WALL_EXT_WEST", "外周壁",
        [_b(X_OUT_W, X_IN_W, Y_OUT_S, Y_OUT_N, FL, CH_MAIN)])
    add("WALL_EXT_EAST", "外周壁",
        [_b(X_IN_E, X_OUT_E, 630, 8199, FL, CH_MAIN)])   # 柱位置(630/8199)で分割
    add("WALL_EXT_NORTH", "外周壁",
        [_b(X_IN_W, OPEN_ENTRANCE_DOOR[0], Y_IN_N, Y_OUT_N, FL, CH_WET),
         _b(OPEN_ENTRANCE_DOOR[1], 4145, Y_IN_N, Y_OUT_N, FL, CH_WET),
         _b(OPEN_ENTRANCE_DOOR[0], OPEN_ENTRANCE_DOOR[1], Y_IN_N, Y_OUT_N,
            DOOR_H, CH_WET)])
    # 南外壁 : 窓開口を残す (腰壁側は Book Shelf の背面壁)
    add("WALL_EXT_SOUTH", "外周壁",
        [_b(X_IN_W, OPEN_WINDOW[0], Y_OUT_S, Y_IN_S, FL, CH_MAIN),
         _b(OPEN_WINDOW[1], 4145, Y_OUT_S, Y_IN_S, FL, CH_MAIN),
         _b(OPEN_WINDOW[0], OPEN_WINDOW[1], Y_OUT_S, Y_IN_S, WIN_HEAD, CH_MAIN)])

    # -----------------------------------------------------------------
    # 柱  COLUMNS   (平面図で外壁より出張る躯体)
    # -----------------------------------------------------------------
    add("COLUMN_SE", "柱", [_b(4145, X_OUT_E, -360, 630, FL, CH_MAIN)])
    add("COLUMN_NE", "柱", [_b(4145, X_OUT_E, 8199, 9037, FL, CH_MAIN)])

    # -----------------------------------------------------------------
    # 内壁  INTERIOR WALLS
    # -----------------------------------------------------------------
    iw = []
    # ※ MBR 南側は固定壁ではなく可動収納壁の東西レッグ (MOVABLE_WALL を参照)
    # 便所南壁 + LD 入口壁 (開口部を残す)
    iw.append(_b(X_WALL_CLO_WC[0], OPEN_LD_DOOR[0], Y_WALL_WC_S[0], Y_WALL_WC_S[1], FL, CH_MAIN))
    iw.append(_b(OPEN_LD_DOOR[1], X_IN_E, Y_WALL_WC_S[0], Y_WALL_WC_S[1], FL, CH_MAIN))
    iw.append(_b(OPEN_LD_DOOR[0], OPEN_LD_DOOR[1], Y_WALL_WC_S[0], Y_WALL_WC_S[1], DOOR_H, CH_MAIN))
    # CLO - WC 間
    iw.append(_b(X_WALL_CLO_WC[0], X_WALL_CLO_WC[1], Y_WALL_WC_S[1], Y_WALL_PWD_S[1], FL, CH_WET))
    # 洗面室南壁
    iw.append(_b(X_WALL_CLO_WC[1], X_WALL_WET_E[1], Y_WALL_PWD_S[0], Y_WALL_PWD_S[1], FL, CH_WET))
    # シャワー南 チェース
    iw.append(_b(X_IN_W, X_WALL_SHOWER_E[1], Y_SHOWER_S[0], Y_SHOWER_S[1], FL, CH_WET))
    # シャワー東壁 (ドア開口)
    iw.append(_b(X_WALL_SHOWER_E[0], X_WALL_SHOWER_E[1], Y_SHOWER_S[1], OPEN_SHOWER_DOOR[0], FL, CH_WET))
    iw.append(_b(X_WALL_SHOWER_E[0], X_WALL_SHOWER_E[1], OPEN_SHOWER_DOOR[0], OPEN_SHOWER_DOOR[1], DOOR_H, CH_WET))
    iw.append(_b(X_WALL_SHOWER_E[0], X_WALL_SHOWER_E[1], OPEN_SHOWER_DOOR[1], Y_WALL_PWD_N[0], FL, CH_WET))
    # 洗面・便所 東壁 (2 開口)
    iw.append(_b(X_WALL_WET_E[0], X_WALL_WET_E[1], Y_WALL_WC_S[1], OPEN_WC_DOOR[0], FL, CH_WET))
    iw.append(_b(X_WALL_WET_E[0], X_WALL_WET_E[1], OPEN_WC_DOOR[0], OPEN_WC_DOOR[1], DOOR_H, CH_WET))
    iw.append(_b(X_WALL_WET_E[0], X_WALL_WET_E[1], OPEN_PWD_DOOR[0], OPEN_PWD_DOOR[1], DOOR_H, CH_WET))
    iw.append(_b(X_WALL_WET_E[0], X_WALL_WET_E[1], OPEN_WC_DOOR[1], OPEN_PWD_DOOR[0], FL, CH_WET))
    # 洗面室北壁 / PS 南壁 (玄関土間まで)
    iw.append(_b(X_IN_W, X_WALL_WET_E[1], Y_WALL_PWD_N[0], Y_WALL_PWD_N[1], FL, CH_WET))
    # MBR 東 : 可動壁の戸袋側 袖壁
    iw.append(_b(MOVW_NS_X[0], MOVW_NS_X[1], MOVW_PIER_Y[0], Y_WALL_WC_S[0], FL, CH_MAIN))
    add("WALL_INT", "内壁", iw)

    # -----------------------------------------------------------------
    # PS  (パイプスペース)
    # -----------------------------------------------------------------
    add("PS", "PS",
        [_b(X_IN_W, X_WALL_PS_E[0], Y_WALL_PWD_N[1], Y_IN_N, FL, CH_WET),          # 内部躯体
         _b(X_WALL_PS_E[0], X_WALL_PS_E[1], Y_WALL_PWD_N[1], Y_IN_N, FL, CH_WET)]) # 東壁

    # -----------------------------------------------------------------
    # 玄関  ENTRANCE  (土間 + 上り框)
    # -----------------------------------------------------------------
    add("ENTRANCE", "玄関",
        [_b(2950, 4170, 7655, Y_IN_N, GENKAN_FL, GENKAN_FL + 20),  # 土間仕上
         _b(2950, 4170, 7655, 7695, FL - 120, FL)])           # 上り框

    # -----------------------------------------------------------------
    # SC  (シューズクローゼット)
    # -----------------------------------------------------------------
    add("SC", "SC", [_b(2575, 2945, 7780, 8345, FL, 2100)])

    # -----------------------------------------------------------------
    # Powder Room  (洗面化粧台 + 鏡)
    # -----------------------------------------------------------------
    add("POWDER_ROOM", "Powder Room",
        [_b(1765, 2835, 6270, 6850, FL, 800),          # カウンター本体
         _b(1765, 2835, 6270, 6860, 800, 830),         # 天板
         _b(1765, 2835, 6270, 6420, 1400, 2000)],      # 三面鏡 + ミラーキャビネット
        [dict(r=190, z0=760, z1=830, cx=2300, cy=6570)])  # 洗面ボウル

    # -----------------------------------------------------------------
    # Shower  (シャワーブース : パン + ガラス)
    # -----------------------------------------------------------------
    add("SHOWER", "Shower",
        [_b(X_IN_W, 966, 6465, Y_WALL_PWD_N[0], FL, 120),          # 防水パン
         _b(946, 966, 6465, Y_WALL_PWD_N[0], 120, 2000),           # 東面ガラス
         _b(X_IN_W, 966, 6465, 6485, 120, 2000),                   # 南面ガラス
         _b(300, 360, Y_WALL_PWD_N[0] - 120, Y_WALL_PWD_N[0] - 60, 900, 2050)])  # シャワーバー

    # -----------------------------------------------------------------
    # W/D  (室内洗濯機置場)
    # -----------------------------------------------------------------
    add("WD", "W/D", [_b(1085, 1725, 6270, 7010, FL, 1050)])

    # -----------------------------------------------------------------
    # Toilet  (便器 + 手洗)
    # -----------------------------------------------------------------
    add("TOILET", "Toilet",
        [_b(1530, 1780, 5600, 5985, FL, 800),          # ロータンク
         _b(1780, 2175, 5660, 5925, 120, 420),         # 便器ボウル
         _b(1780, 2175, 5660, 5925, 420, 460),         # 便座
         _b(2405, 2795, 5400, 5565, 780, 830)])        # 手洗カウンター

    # -----------------------------------------------------------------
    # Kitchen  (システムキッチン + トールユニット + レンジフード)
    # -----------------------------------------------------------------
    add("KITCHEN", "Kitchen",
        [_b(3875, X_IN_E, 6130, 7595, FL, 820),        # キャビネット
         _b(3875, X_IN_E, 6130, 7595, 820, 850),       # 天板
         _b(3945, 4430, 7130, 7440, 850, 880),         # ガスコンロ 2 口
         _b(3978, 4378, 6235, 6710, 760, 790),         # シンク底
         _b(3900, X_IN_E, 7080, 7490, 1500, 2100),     # レンジフード
         _b(4170, X_IN_E, 7660, 8010, FL, 2100)])      # トールユニット

    # -----------------------------------------------------------------
    # Refrigerator
    # -----------------------------------------------------------------
    add("REFRIGERATOR", "Refrigerator", [_b(3800, X_IN_E, 5525, 6090, FL, 1800)])

    # -----------------------------------------------------------------
    # Closet  (Clo. x 2)
    # -----------------------------------------------------------------
    add("CLOSET_1", "Closet", [_b(X_IN_W, 780, Y_CLO_S, Y_CLO_N, FL, 2300)])
    add("CLOSET_2", "Closet", [_b(780, 1365, Y_CLO_S, Y_CLO_N, FL, 2300)])

    # -----------------------------------------------------------------
    # 既存 Book Shelf  --  大型化・延長・床天井収納化 禁止
    # -----------------------------------------------------------------
    bs = BOOK_SHELF
    bx = [_b(bs["x0"], bs["x1"], bs["y0"], bs["y0"] + 25, FL, bs["z1"]),   # 左側板
          _b(bs["x0"], bs["x1"], bs["y1"] - 25, bs["y1"], FL, bs["z1"]),   # 右側板
          _b(bs["x0"], bs["x0"] + 20, bs["y0"], bs["y1"], FL, bs["z1"]),   # 背板
          _b(bs["x0"], bs["x1"], bs["y0"], bs["y1"], FL, FL + 25),         # 地板
          _b(bs["x0"], bs["x1"], bs["y0"], bs["y1"], bs["z1"] - 25, bs["z1"])]  # 天板
    for yd in bs["dividers_y"]:                                            # 方立
        bx.append(_b(bs["x0"], bs["x1"], yd - 12, yd + 12, FL, bs["z1"]))
    n_shelf = 6
    for i in range(1, n_shelf + 1):                                        # 棚板
        z = bs["z1"] * i / (n_shelf + 1)
        bx.append(_b(bs["x0"], bs["x1"], bs["y0"], bs["y1"], z - 10, z + 10))
    add("BOOK_SHELF_EXISTING", "既存Book Shelf", bx)

    # -----------------------------------------------------------------
    # 可動収納壁 / レール
    # -----------------------------------------------------------------
    mw = []
    ns_len = (MOVW_NS_TRAVEL[1] - MOVW_NS_TRAVEL[0]) / MOVW_NS_PANELS
    ew_len = (MOVW_EW_TRAVEL[1] - MOVW_EW_TRAVEL[0]) / MOVW_EW_PANELS
    if MOVABLE_WALL_STATE == "OPEN":
        # 常時開放 : 各レッグの建具はコーナーから最も遠い戸袋へ引き込む
        c = (MOVW_NS_POCKET[0] + MOVW_NS_POCKET[1]) / 2.0
        for x0, x1 in MOVW_NS_LANES:
            mw.append(_b(x0, x1, c - ns_len / 2, c + ns_len / 2, FL, MOVW_PANEL_H))
        c = (MOVW_EW_POCKET[0] + MOVW_EW_POCKET[1]) / 2.0
        for y0, y1 in MOVW_EW_LANES:
            mw.append(_b(c - ew_len / 2, c + ew_len / 2, y0, y1, FL, MOVW_PANEL_H))
    else:
        # 参考 : 閉。L 字に建具が並び MBR が閉じる
        for i in range(MOVW_NS_PANELS):
            y0 = MOVW_NS_TRAVEL[0] + i * ns_len
            mw.append(_b(MOVW_NS_X[0] + 15, MOVW_NS_X[1] - 15, y0, y0 + ns_len,
                         FL, MOVW_PANEL_H))
        for i in range(MOVW_EW_PANELS):
            x0 = MOVW_EW_TRAVEL[0] + i * ew_len
            mw.append(_b(x0, x0 + ew_len, MOVW_EW_Y[0] + 15, MOVW_EW_Y[1] - 15,
                         FL, MOVW_PANEL_H))
    # レール (L 字・状態によらず不変)
    mw.append(_b(MOVW_NS_X[0] + 30, MOVW_NS_X[1] - 30,
                 MOVW_NS_TRAVEL[0], MOVW_NS_POCKET[1], MOVW_PANEL_H, CH_MAIN))
    mw.append(_b(MOVW_EW_POCKET[0], MOVW_EW_TRAVEL[1],
                 MOVW_EW_Y[0] + 15, MOVW_EW_Y[1] - 15, MOVW_PANEL_H, CH_MAIN))
    add("MOVABLE_WALL", "可動収納壁／レール", mw)

    # -----------------------------------------------------------------
    # 窓 / サッシ  (掃き出し窓 : 2 枚引違い)
    # -----------------------------------------------------------------
    w0, w1 = OPEN_WINDOW
    wm = (w0 + w1) / 2.0
    add("WINDOW_SASH", "窓／サッシ",
        [_b(w0, w1, Y_OUT_S + 40, Y_IN_S - 40, FL, FL + 70),        # 下枠
         _b(w0, w1, Y_OUT_S + 40, Y_IN_S - 40, WIN_HEAD - 70, WIN_HEAD),  # 上枠
         _b(w0, w0 + 60, Y_OUT_S + 40, Y_IN_S - 40, FL, WIN_HEAD),  # 縦枠 西
         _b(w1 - 60, w1, Y_OUT_S + 40, Y_IN_S - 40, FL, WIN_HEAD),  # 縦枠 東
         _b(wm - 40, wm + 40, Y_OUT_S + 40, Y_IN_S - 40, FL, WIN_HEAD),   # 召し合せ
         _b(w0 + 60, wm + 40, 95, 125, FL + 70, WIN_HEAD - 70),     # ガラス 西
         _b(wm - 40, w1 - 60, 135, 165, FL + 70, WIN_HEAD - 70)])   # ガラス 東

    # -----------------------------------------------------------------
    # バルコニー床
    # -----------------------------------------------------------------
    add("BALCONY_SLAB", "バルコニー床",
        [_b(X_OUT_W, X_OUT_E, BAL_Y_OUT, Y_OUT_S, BAL_FL - 200, BAL_FL)])

    # -----------------------------------------------------------------
    # バルコニー手摺  (ガラス手摺 + 笠木 + 隔て板)
    # -----------------------------------------------------------------
    add("BALCONY_RAILING", "バルコニー手摺",
        [_b(X_OUT_W, X_OUT_E, BAL_Y_OUT, BAL_Y_OUT + 60, BAL_FL, BAL_RAIL_TOP - 60),   # ガラス
         _b(X_OUT_W, X_OUT_E, BAL_Y_OUT - 20, BAL_Y_OUT + 80, BAL_RAIL_TOP - 60, BAL_RAIL_TOP),  # 笠木
         _b(X_OUT_W, X_OUT_W + 60, BAL_Y_OUT, Y_OUT_S, BAL_FL, BAL_RAIL_TOP),          # 隔て板 西
         _b(X_OUT_E - 60, X_OUT_E, BAL_Y_OUT + 60, -360, BAL_FL, BAL_RAIL_TOP)])            # 隔て板 東

    # -----------------------------------------------------------------
    # 床 / 天井  (Z のみの補助オブジェクト)
    # -----------------------------------------------------------------
    add("FLOOR_SLAB", "床・天井",
        [_b(X_OUT_W, X_OUT_E, Y_OUT_S, 7655, FL - 200, FL),
         _b(X_OUT_W, 2950, 7655, Y_OUT_N, FL - 200, FL),
         _b(4170, X_OUT_E, 7655, Y_OUT_N, FL - 200, FL),
         _b(2950, 4170, Y_IN_N, Y_OUT_N, FL - 200, FL),
         _b(2950, 4170, 7655, Y_IN_N, FL - 200, GENKAN_FL)])   # 土間をくり抜く
    add("CEILING", "床・天井",
        [_b(X_IN_W, X_IN_E, Y_IN_S, Y_IN_N, CH_MAIN, SLAB_TOP)])

    # =================================================================
    #  FURNITURE   ( XY = FURNITURE_XY_LOCK )
    # =================================================================
    F = FURNITURE_XY_LOCK

    d = F["DESK_2P"]
    desk = [_b(d["x0"], d["x1"], d["y0"], d["y1"], 700, 740)]
    for sx in (d["x0"] + 60, d["x1"] - 120):
        for sy in (d["y0"] + 40, d["y1"] - 100):
            desk.append(_b(sx, sx + 60, sy, sy + 60, FL, 700))
    desk.append(_b(d["x0"] + 40, d["x1"] - 40, d["y0"] + 40, d["y0"] + 70, 420, 690))  # 幕板
    add("DESK_2P", "2人用ワークデスク", desk)

    for k in ("TASK_CHAIR_1", "TASK_CHAIR_2"):
        c = F[k]
        bx, cy = _task_chair(c["cx"], c["cy"], c["facing"])
        add(k, "執務チェア2脚", bx, cy)

    m = F["MEETING_TABLE"]
    tbl = [_b(m["x0"], m["x1"], m["y0"], m["y1"], 700, 740)]
    for sx in (m["x0"] + 80, m["x1"] - 160):
        for sy in (m["y0"] + 80, m["y1"] - 160):
            tbl.append(_b(sx, sx + 80, sy, sy + 80, FL, 700))
    add("MEETING_TABLE", "6人用ミーティングテーブル", tbl)

    for k in ("MTG_CHAIR_W1", "MTG_CHAIR_W2", "MTG_CHAIR_E1",
              "MTG_CHAIR_E2", "MTG_CHAIR_S", "MTG_CHAIR_N"):
        c = F[k]
        bx, cy = _meeting_chair(c["cx"], c["cy"], c["facing"])
        add(k, "会議チェア6脚", bx, cy)

    mo = F["MONITOR_55"]
    cx, cy = mo["cx"], mo["cy"]
    add("MONITOR_55", "55インチモニター",
        [_b(cx - 640, cx + 640, cy - 30, cy + 30, 700, 1445),   # 筐体 (55" = 1218x685)
         _b(cx - 609, cx + 609, cy - 45, cy - 30, 730, 1415),   # 画面
         _b(cx - 120, cx + 120, cy - 10, cy + 70, 40, 700),     # 支柱
         _b(cx - 350, cx + 350, cy - 175, cy + 175, FL, 40)])   # ベース

    return P


# 検証用 : 面積
def areas():
    gross = (X_OUT_E - X_OUT_W) * (Y_OUT_N - Y_OUT_S) / 1e6
    bal = (X_OUT_E - X_OUT_W) * (Y_OUT_S - BAL_Y_OUT) / 1e6
    return dict(gross_m2=gross, balcony_m2=bal)


if __name__ == "__main__":
    a = areas()
    print("専有面積(外形) = %.2f m2   (表記 40.76)" % a["gross_m2"])
    print("バルコニー      = %.2f m2   (表記  6.40)" % a["balcony_m2"])
    print("オブジェクト数  =", len(parts()))
