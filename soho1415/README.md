# SOHO / 1415 — 3D GEOMETRY MODEL

OIMACHI TRACKS RESIDENCE（SOHOフロア）1415号室 / 物件番号 2025110085
1LDK / 専有面積 40.76㎡ / バルコニー 6.4㎡ / 14階

承認済みモデルを **実際の3Dシーンとして再構築** したもの。
画像生成AI（image generation / DALL-E 等）は一切使用していない。
検証レンダリングは、構築した実ジオメトリの三角形を
Pythonのz-bufferラスタライザでそのまま投影したものである。

---

## 現在の工程

**3Dモデル構築 + A/B検証レンダリングまで完了。ここで停止している。**
「3D GEOMETRY APPROVED」の指示があるまで室内パースには進まない。

---

## ファイル

| ファイル | 役割 |
|---|---|
| `geometry_master.py` | **座標マスター（唯一の真実）**。全XY・Z・開口・家具位置 |
| `build_model.py` | マスター → trimeshシーン → `out/soho1415_master.glb` |
| `softrender.py` | 正投影z-bufferソフトレンダラ（決定論的・画像生成なし） |
| `render_validation.py` | 検証レンダ A / B と承認済み平面図との重ね合わせ C |
| `blender_build.py` | 同一マスター → Blenderシーン（承認後のフォトリアル用） |
| `out/` | 出力（GLB / objects.json / 検証画像3枚） |

```bash
pip install numpy trimesh pillow scipy
python3 build_model.py          # モデル構築 + GLB書き出し
python3 render_validation.py    # A / B / C レンダリング + 自動検証
blender --background --python blender_build.py -- --save out/soho1415_master.blend
```

---

## 座標系

```
X = 平面図の右方向（東）      LOCK
Y = 平面図の上方向（北）      LOCK
Z = 上方向（FL = 0）          今回追加した唯一の次元
単位 = mm
原点 = 平面図 左下（南西）外壁外面の交点
```

### XYの取得方法

承認済み平面図のピクセル座標を投影プロファイル（dark-line detection）で
実測し、一次変換でmmへ換算した。**目視トレースではない。**

```
X_mm = (px_x - 643) × 12.875
Y_mm = (942 - px_y) × 12.875
```

### 縮尺の検証（独立した2つの面積が一致）

| 項目 | モデル | 表記 | 差 |
|---|---|---|---|
| 専有面積（外形 4700 × 8675） | 40.77㎡ | 40.76㎡ | **+0.03%** |
| バルコニー（4700 × 1385） | 6.51㎡ | 6.40㎡ | +1.7% |

2つの独立した面積がともに一致するため、縮尺 12.875 mm/px は確定とみなす。

### Zについて

平面図はZを持たないため、Zのみを新規に与えた。
**Zを与える際にXYは一切変更していない。**

| 項目 | 値 |
|---|---|
| 天井高（居室） | 2450 |
| 天井高（水回り・玄関） | 2200 |
| 建具開口高 | 2000 |
| 掃き出し窓 上端 | 2100 |
| バルコニー床 / 手摺天端 | −150 / +1050 |
| 玄関土間 | −120 |

---

## オブジェクト（36個・すべて独立）

| 指定要素 | オブジェクト名 |
|---|---|
| 外周壁 | `WALL_EXT_WEST` `WALL_EXT_EAST` `WALL_EXT_NORTH` `WALL_EXT_SOUTH` |
| 内壁 | `WALL_INT` |
| 柱 | `COLUMN_SE` `COLUMN_NE` |
| バルコニー床 | `BALCONY_SLAB` |
| バルコニー手摺 | `BALCONY_RAILING` |
| 玄関 | `ENTRANCE` |
| PS | `PS` |
| SC | `SC` |
| Powder Room | `POWDER_ROOM` |
| Shower | `SHOWER` |
| W/D | `WD` |
| Toilet | `TOILET` |
| Kitchen | `KITCHEN` |
| Refrigerator | `REFRIGERATOR` |
| Closet | `CLOSET_1` `CLOSET_2` |
| 既存Book Shelf | `BOOK_SHELF_EXISTING` |
| 可動収納壁／レール | `MOVABLE_WALL` |
| 窓／サッシ | `WINDOW_SASH` |
| 2人用ワークデスク | `DESK_2P` |
| 執務チェア2脚 | `TASK_CHAIR_1` `TASK_CHAIR_2` |
| 6人用ミーティングテーブル | `MEETING_TABLE` |
| 会議チェア6脚 | `MTG_CHAIR_W1` `W2` `E1` `E2` `S` `N` |
| 55インチモニター | `MONITOR_55` |
| （Z補助） | `FLOOR_SLAB` `CEILING` |

`FLOOR_SLAB` / `CEILING` はZを与えた結果必要になった床・天井スラブで、
壁・収納・家具のいずれでもない。検証レンダAでは天井を非表示にしている。

---

## 禁止事項の遵守

追加していない要素：
ベッド / ソファ / ラウンジ / ローテーブル / 追加収納 /
追加Book Shelf / 追加壁 / 追加窓 / 追加ドア

- 既存Book Shelfは **X 205–490 / Y 425–2190 / H 2100** のまま。
  大型化・延長・床天井収納化はしていない（`render_validation.py` が毎回自動照合）。
- Master Bedroomは意図的に空。ベッドは禁止要素のため置いていない。
- 建具は**開口部のみ**をモデル化し、扉パネルは作っていない
  （新規ドアを足したと誤解される余地をなくすため）。

`render_validation.py` は実行のたびに次を自動チェックする：

```
--- XY LOCK check ---            全オブジェクトが外形内にあるか
out-of-envelope objects: none
--- forbidden object check ---   禁止要素名の混入
forbidden names found: none
BOOK SHELF bbox: [205.0, 425.0, 0.0] [490.0, 2190.0, 2100.0]  大型化なし
--- area check ---
gross   40.77 m2 (spec 40.76)  diff +0.03%
balcony  6.51 m2 (spec  6.40)  diff +1.71%
```

---

## 検証レンダリング

| 画像 | 内容 |
|---|---|
| `out/view_A_axonometric.png` | 平面図と同じ向き（北が上）を保った俯瞰アクソメ / 正投影・天井非表示 |
| `out/view_B_top_ortho.png` | 完全真上からの正投影 TOP VIEW |
| `out/view_C_overlay_vs_approved_plan.png` | **B を承認済み平面図に同一縮尺・同一原点で重ねたもの** |

Cでは、モデルの立ち上がり部材だけを赤で承認済み平面図に重ねている。
外周壁・内壁・PS・SC・Shower・W/D・洗面台・Closet・Toilet・
Kitchen（コンロ／シンク）・Refrigerator・Book Shelf・可動収納壁・柱・
バルコニーが、いずれも平面図の作図線上に乗ることを確認できる。

---

## ⚠ 要確認 — 家具のXY

本作業に添付されたのはKEN物件資料PDFの3ページ
（内観写真2枚 + 平面図1枚）のみで、家具位置を確定した
**「承認済み ORTHOGRAPHIC COORDINATE MODEL」の画像は含まれていなかった**。

そのため：

- **建築躯体のXY** … 平面図から実測。確定値。
- **家具のXY** … 承認済みモデルが参照できないため、
  `geometry_master.py` の `FURNITURE_XY_LOCK` に暫定値として定義。

暫定値（mm）：

| 要素 | XY |
|---|---|
| 2人用ワークデスク 1600×700 | X 500–2100 / Y 430–1130（Book Shelf脇・バルコニーを向いて着座） |
| 執務チェア2脚 | (900, 1500) (1700, 1500) 南向き |
| 6人用ミーティングテーブル 1000×2100 | X 2900–3900 / Y 1350–3450 |
| 会議チェア6脚 | 西 (2620,1875)(2620,2925) / 東 (4180,1875)(4180,2925) / 南 (3400,1050) / 北 (3400,3750) |
| 55インチモニター | (3400, 4300) 南向き・テーブル北端に正対 |

承認済みモデルの数値が判明した場合、**このブロックの数値だけ**を
差し替えれば他は一切変更不要（躯体・検証・レンダは自動追従する）。

---

## 承認後の手順（GEOMETRY APPROVED後）

新しいシーンは作らず、`out/soho1415_master.glb`（または
`blender_build.py` が生成する同一座標の`.blend`）に
**カメラだけを追加**して撮影する。

| カメラ | 位置・方向 |
|---|---|
| CAMERA 1 | バルコニー側 → 入口方向 |
| CAMERA 2 | 入口側 → バルコニー方向 |
| CAMERA 3 | 6人用ミーティングテーブル付近 → 2人用ワークスペース方向 |
| CAMERA 4 | ワークスペース → Living Dining方向 |

カメラ高 1500–1600mm 相当 / フルサイズ換算 28–35mm / 超広角禁止。

同一モデルの別カメラレンダリングであるため、壁が増える・Book Shelfが変わる・
ベッドが出現する・家具が移動する・部屋が広くなることは構造上起こらない。

最終工程でAIを使うのは **材質・光・質感・フォトリアリズムのみ**。
AIによるgeometry変更は禁止。
