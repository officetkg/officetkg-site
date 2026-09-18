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

## Coordinate system

* `work  = source_pixel - (240, 120)`
* `MX = work_x - 403`, `MY = work_y - 150` — origin at the NW corner of the building
  outline (exterior faces)
* X right (plan east), Y down (plan south, balcony side)
* **Unit = 1 source-image pixel. No mm conversion.** mm calibration is deferred until
  after `2D GEOMETRY APPROVED`, and must use a real dimension, not the floor area.

## Rules carried through every phase

* The original 2D plan is the only geometry source; photos are used for finishes only.
* Master Bedroom / Living Dining storage wall is **L-shaped** (east run: 3 panels,
  north pocket; south run: 2 panels, west pocket) and is always modelled
  **OPEN / PARKED** — rails and pockets kept, openings permanently clear.
* Heights exist only as provisional variables in `heights.py`; no section was
  ever supplied. Changing a Z can never change an X or a Y.
* Balcony side partitions are **parallel** (19.43° / 19.60° from vertical): the
  balcony is a raked parallelogram. Never squared off, symmetrised or curved.
