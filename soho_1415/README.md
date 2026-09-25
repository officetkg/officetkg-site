# OIMACHI TRACKS RESIDENCE (SOHO floor) 1415 — SOHO office fit-out

Coordinate-model based workflow. **No image generation is used for architectural geometry.**

## Status

| Phase | Content | State |
|---|---|---|
| 1 | Original plan reading | done |
| 2 | Photographic distortion correction | done — **no correction needed / none applied** |
| 3 | 2D coordinate trace | done |
| 4 | Overlay verification | done — **awaiting `2D GEOMETRY APPROVED`** |
| 5 | Furniture layout | done — `FURNITURE APPROVED` |
| 6 | 3D geometry from the 2D master | done |
| 7 | Orthographic top-view validation | done — **awaiting `3D GEOMETRY APPROVED`** |
| 8–10 | Cameras, materials, render | blocked |

## Files

```
geometry_master.py     2D GEOMETRY MASTER (single source of truth, pixel coordinates)
render_2d.py           renders A / B / C
verify_overlay.py      numeric residual check (traced line -> nearest printed ink)
export_svg.py          SVG export
make_review_sheet.py   PHASE 4 review sheet
calibrate_scale.py     px -> mm calibration record (13.2 mm/px, provisional)
furniture.py           PHASE 5 furniture, XY only additive
check_layout.py        clash + circulation check
heights.py             PHASE 6 Z variables, ALL PROVISIONAL
build_3d.py            PHASE 6 3D build, XY read from the 2D master only
topview_ortho.py       PHASE 7 orthographic top view (perspective 0, -Z)
verify_3d.py           PHASE 7 3D bounds vs 2D master bounds
verify_topview.py      PHASE 7 line check + mechanical residual classification
make_phase7_sheet.py   PHASE 7 review sheet
phase2/
  00_BEFORE_source.png
  01_AFTER_rectified.png     (bit identical to BEFORE — identity transform)
  PHASE2_record.json         angle evidence + sha256 of both images
out/
  A_source_plan.png
  B_vector_trace_OPEN.png       storage wall PARKED (design state)
  B_vector_trace_asdrawn.png    storage wall as printed (closed) — verification only
  C_overlay_OPEN.png
  C_overlay_asdrawn.png
  PHASE4_2D_GEOMETRY_REVIEW.png
  PHASE4_residuals.txt
  geometry_master.json
  geometry_master.svg
```

## Orientation — corrected

The compass rose on the sheet carries its "N" at the **lower** tip of the needle
and nothing at all above the upper tip, so **north points down the page**:

| MASTER axis | sheet | compass |
|---|---|---|
| +Y | down | **NORTH** — the balcony side |
| −Y | up | SOUTH — entrance / common corridor |
| +X | right | **WEST** — kitchen, 55" monitor |
| −X | left | EAST — Book Shelf, work desks |

`orientation.py` holds the pixel evidence and the conversion helpers. Every
identifier in `geometry_master.py` ("north", "run_EAST", `W_shower_east_thick`…)
is a **plan-relative** name frozen at PHASE 3; read them as sheet directions, not
compass directions.

The MASTER tuple (right, down, up) is left-handed, so any right-handed renderer
must reflect it. `orientation.to_enu` and the viewer's `scale.x = -1` do exactly
that; without it a 3D view comes out mirrored.

## Photoreal pass

`photoreal.py` raises the render quality without touching a coordinate. Same
triangles, better image synthesis:

* 2x supersampled rasterising
* a shadow map cast from the north window, so the sash frame, the mullion, the
  furniture and the balustrade actually block light
* world-space procedural texture — oak planks and grain, plaster tooth, concrete
* planar reflection in the timber floor, with a Fresnel weight
* gloss highlights and a small bloom on the window and the downlights

No AI image generation is used anywhere in this project. `PR_A..E.png` are the
photoreal outputs; `CAM_A..E.png` are the plain shaded views they came from.

## Architectural lighting

`lighting.py` carries the coffered ceiling and the downlights, read from the
listing photos: a dropped 450 mm perimeter band round the living zone, recessed
downlights in PAIRS set into that band, plus downlights in the kitchen and inner
hall. **The sheet has no reflected ceiling plan**, so every position there is
photo-derived and provisional. It is deliberately kept out of
`geometry_master.py` — the approved architectural XY is untouched.

Daylight stays primary: the balcony faces north, so the north window carries the
rooms and the downlights are a secondary layer.

## Coordinate system

* `work  = source_pixel - (240, 120)`
* `MX = work_x - 403`, `MY = work_y - 150` — origin at the NW corner of the building
  outline (exterior faces)
* X right (plan east), Y down (plan south, balcony side)
* **Unit = 1 source-image pixel. No mm conversion.** mm calibration is deferred until
  after `2D GEOMETRY APPROVED`, and must use a real dimension, not the floor area.
* The balcony sash, the balustrade and the balcony partitions are modelled from
  the listing photos: 2 unequal sliding leaves (wide WEST, narrow EAST) with the
  head **below** the ceiling, a **clear glass** balustrade with a dark capping and
  posts, full-height maroon escape partitions on both raked sides, and the
  rainwater downpipe that the plan draws as a small circle.
* `BOOKSHELF_HEIGHT` is set to ceiling height because the photos show the existing
  shelf running floor to ceiling. The brief says not to expand the Book Shelf into
  a floor-to-ceiling unit — revert this one variable to 2000 if the brief wins.
* The balcony faces **north**: no direct sun reaches the living zone. PHASE 9
  lighting must be built on even north daylight, not on a south-facing model.

## Rules carried through every phase

* The original 2D plan is the only geometry source; photos are used for finishes only.
* Master Bedroom / Living Dining storage wall is **L-shaped** (east run: 3 panels,
  north pocket; south run: 2 panels, west pocket) and is always modelled
  **OPEN / PARKED** — rails and pockets kept, openings permanently clear.
* Heights exist only as provisional variables in `heights.py`; no section was
  ever supplied. Changing a Z can never change an X or a Y.
* Balcony side partitions are **parallel** (19.43° / 19.60° from vertical): the
  balcony is a raked parallelogram. Never squared off, symmetrised or curved.
