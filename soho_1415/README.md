# OIMACHI TRACKS RESIDENCE (SOHO floor) 1415 — SOHO office fit-out

Coordinate-model based workflow. **No image generation is used for architectural geometry.**

## Status

| Phase | Content | State |
|---|---|---|
| 1 | Original plan reading | done |
| 2 | Photographic distortion correction | done — **no correction needed / none applied** |
| 3 | 2D coordinate trace | done |
| 4 | Overlay verification | done — `2D GEOMETRY APPROVED` |
| 5 | Furniture layout | done — `FURNITURE APPROVED` |
| 6 | 3D geometry from the 2D master | done |
| 7 | Orthographic top-view validation | done — `3D GEOMETRY APPROVED` |
| 8 | Cameras A–E | done |
| 9 | Materials + architectural lighting | done |
| 10 | Photoreal render | done |
| 10b | Decoration (permitted items only) | done — 44 items, 0 off an approved support |

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
orientation.py         compass evidence + left/right-handed conversion helpers
cameras.py             PHASE 8 cameras A-E, with an eye-inside-solid check
make_camera_plan.py    PHASE 8 camera plan + review sheet
render_persp.py        perspective rasteriser (levelled axis + lens shift, never tilt)
materials.py           PHASE 9 albedo palette (+ CLAY variant)
lighting.py            PHASE 9 coffered ceiling + downlights, photo-derived
make_rcp.py            PHASE 9 reflected ceiling plan
shading.py             north-daylight shading model
photoreal.py           PHASE 10 photoreal pass (shadow map, texture, reflection)
decoration.py          permitted decoration only, with an on-support verifier
make_photoreal_sheet.py  PHASE 10 contact sheet + decoration before/after
make_viewer.py         Three.js GLB viewer (viewer/index.html)

topview_ortho.SKIP_TOP leaves the ceiling slab, the coffer, the downlights and the
decoration out of the PHASE 7 top view: a plan is cut below the ceiling, and with
the slab left in it simply paints over everything underneath.
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

## Specified products

The client specified three products; `products.py` builds them from their
published dimensions and `heights.py` keeps those dimensions in a **SPECIFIED**
dict, separate from the provisional heights.

| | product | published |
|---|---|---|
| meeting table | NISHIKI **E-CAD-2190KW** | 2100 × 900 × H720, walnut, 30 mm melamine top with ABS edge, 60 × 30 polished steel pipe legs, wiring box, adjusters |
| work chairs ×2 | Herman Miller **Aeron**, size B | 658 W × 598 D × 1090 H, seat 406–521 (set 450) |
| meeting chairs ×6 | Herman Miller **Setu**, 5-star base, armless | 658 W × 658 D × 950–980 H, seat 399–551 (set 460) |

What is **not** published — the leg inset from the table ends, the wiring-box
lid size, the under-top cable tray, the exact arc of the Aeron back and the
Setu spine — is approximated, is marked as an approximation in `products.py`,
and never leaves the published envelope.

A 5-star base is a circle, so neither chair fills its rectangular planning
envelope: with one arm pointing straight back a 658 mm base measures
595 × 626 mm on the floor. The Aeron reaches its published 658 mm width at the
arm pads. Both are therefore verified by **containment**, not by outline match.

### What the longer table forced

The table grew 1800 → 2100 mm. The LD bay is only 2587 mm wide between the
partition line and the west wall, so the extra 300 mm had to go somewhere:

* the **west** end stays put, which keeps the 55″ viewing distance and the
  west aisle (3472 mm) unchanged;
* the extra 300 mm is taken on the **east** end, leaving 1300 mm of the Book
  Shelf route;
* three 658 mm Setu chairs then fill the 2100 mm side end to end (719 mm
  pitch), which pushed the east chair to within 304 mm of the Aeron at
  DESK_2 — below the 900 mm pull-out rule;
* so **both workstations moved 170 mm plan-up**. The Aeron at DESK_2 and the
  Setu at the table's east end no longer overlap in Y at all, and the pull-out
  behind DESK_2 is back to 2429 mm.

`check_layout.py` passes every route after the move; see the table it prints.

## Decoration

`decoration.py` adds only what the brief permits — laptops, keyboards, mice,
notebooks, pens, a small number of books, and one or two small plants. **48
items.** Nothing architectural and no piece of furniture is moved by it; it is a
purely additive layer read into `build_3d.py` after everything else is built.

`python3 decoration.py` prints the verification:

* every mesh must sit **on an approved support** — `WORK_DESK_1/2`,
  `MEETING_TABLE`, `BOOK_SHELF`, or a clear patch of Living Dining floor — and
  inside that support's footprint. Result: **0 items off an approved support**.
* every mesh must also **clash with nothing**: `_obstacles()` collects every
  wall, column, PS, casework, storage-wall and furniture rectangle in the
  master, and no item may overlap any of them but its own support. Result:
  **0 clashes**. This check was added after the floor plant was found standing
  inside `W_SEcol_return_head` — the support test alone had passed it, because
  the FLOOR rect then ran to x 355 / y 666 and swallowed the column return.
* the banned list (bed, sofa, lounge chair, coffee table, a bank of plants, large
  artwork, clutter, household goods) is asserted empty.

| group | items | z (mm) | support |
|---|---|---|---|
| Laptops | 2 | 720 – 736 | work desks |
| Laptop_Screens | 2 | 742 – 935 | work desks |
| Desk_Kit (keyboard, mouse) | 4 | 720 – 757 | work desks |
| Paper (notebook, pen) | 6 | 720 – 731 | work desks, meeting table |
| Books | 24 | 820 – 1869 | Book Shelf |
| Plant_Pots | 2 | 0 – 2135 | Book Shelf, LD floor |
| Plant_Foliage | 8 | 188 – 2366 | Book Shelf, LD floor |

`out/PHOTOREAL_BEFORE_AFTER.png` is the same five cameras rendered before and
after the layer, so the difference is decoration alone.

## Ambient occlusion — calibrated against the photos

An earlier pass drew a near-black hairline at every internal corner, along
every edge of the ceiling coffer and around every Book Shelf cubby. None of
that is in the listing photos. Measured off the reference photo of the Living
Dining and off the render:

| ratio | photo | render before | render after |
|---|---|---|---|
| internal wall/ceiling corner ÷ flat wall | 0.935 | **0.281** | 0.894 |
| Book Shelf cubby ÷ shelf board face | 0.679 | **0.462** | 0.730 |
| darkest interior pixel | 0.31 | 0.16 | — |

Three faults, all in the AO term:

1. **AO was multiplied in twice** — once as `ao**1.2` on the ambient terms and
   again as `ao**0.5` over the whole colour, a combined exponent of 1.7. It
   also darkened the window term, which `window_visibility()` already handles.
2. **The occlusion radius mixed screen and world units**: a 24-pixel screen
   radius was compared against a world distance of `radius*1.6`, so on a large
   flat wall every neighbour on the adjoining wall counted as an occluder.
   `AO_RADIUS_MM` now sets the world window in millimetres, sampled at three
   screen radii so near and far behave the same.
3. **No interreflection.** A 90° corner between two white surfaces hides half
   the hemisphere, yet the photo shows it only 6.5 % darker, because the light
   comes straight back off the facing wall. `ao_apply()` is that first-order
   correction: a bright surface keeps nearly all of its ambient in a corner, a
   darker recess loses more. Without it, every white corner goes black.

Disabling AO entirely gives a corner ratio of 0.913, so the remaining 0.894 is
within 2 % of the geometric floor — the rest is the genuine lighting difference
between two wall faces at 90°, not an artefact.

Separately, `Storage_Wall_Rail` was **matte black** in the palette. The photo
taken from the Master Bedroom into the Living Dining shows the partition head
at **1.21 × the ceiling luma** — a light head, not a black track — so the rail
is now (230, 228, 223) and the parked panels are the light oak the same photo
shows, not off-white.

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
