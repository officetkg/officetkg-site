# -*- coding: utf-8 -*-
"""Export the 2D MASTER as SVG (master px = SVG user units, 1:1)."""
import geometry_master as G
O=[]
def r(rc,cls):
    O.append(f'<rect class="{cls}" x="{rc["x0"]}" y="{rc["y0"]}" '
             f'width="{rc["x1"]-rc["x0"]}" height="{rc["y1"]-rc["y0"]}"/>')
def l(p,q,cls): O.append(f'<line class="{cls}" x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}"/>')
def pl(pts,cls): O.append(f'<polyline class="{cls}" points="{" ".join(f"{a},{b}" for a,b in pts)}"/>')

ow=G.OUTER_WALLS
pl(ow["envelope_outline"],"outer")
for s in ow["north"]["segments"]: l((s["x0"],s["inner_y"]),(s["x1"],s["inner_y"]),"outer")
for s in ow["west"]["segments"]:  l((s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]),"outer")
for s in ow["east"]["segments"]:  l((s["inner_x"],s["y0"]),(s["inner_x"],s["y1"]),"outer")
r(ow["south"]["solid_segment"],"outer")
for k,v in G.COLUMNS.items(): r(v,"column")
for k,v in G.PS.items():
    if isinstance(v,dict) and "y0" in v: r(v,"ps")
for k,v in G.INNER_WALLS.items(): r(v,"inner")
for tag,run in (("EAST",G.STORAGE_WALL["run_EAST"]),("SOUTH",G.STORAGE_WALL["run_SOUTH"])):
    r(run["pocket"],"pocket")
    for p in run["panels_parked"]: r(p,"panel")
    rl=run["rail_line"]
    l((rl["x"],rl["y0"]),(rl["x"],rl["y1"]),"rail") if run["axis"]=="vertical" \
        else l((rl["x0"],rl["y"]),(rl["x1"],rl["y"]),"rail")
for v in (G.SC,G.SHOWER,G.WD,G.VANITY,G.VANITY_BOWL,G.REFRIGERATOR,
          G.ENTRANCE_NICHE_UNIDENTIFIED,G.BOOK_SHELF["body"]): r(v,"case")
for v in G.CLOSETS.values(): r(v,"case")
for d in (G.TOILET,G.KITCHEN):
    for k,v in d.items():
        if isinstance(v,dict) and "y0" in v: r(v,"case")
bs=G.BOOK_SHELF["body"]
for y in G.BOOK_SHELF["shelf_lines_y"]: l((bs["x0"],y),(bs["x1"],y),"case")
wb=G.WINDOWS["W_BALCONY"]; r(wb["opening"],"win")
l((wb["mullion_x"],wb["opening"]["y0"]),(wb["mullion_x"],wb["opening"]["y1"]),"win")
for k,d in G.DOORS.items():
    if "hinge" in d:
        l(d["hinge"],d["open_leaf_to"],"door"); l(d["hinge"],d["closed_leaf_to"],"doorthin")
    else:
        o=d["opening"]
        l((o["x0"],o["y"]),(o["x1"],o["y"]),"door") if "x0" in o else l((o["x"],o["y0"]),(o["x"],o["y1"]),"door")
b=G.BALCONY
l((b["north_edge_x"][0],b["north_edge_y"]),(b["north_edge_x"][1],b["north_edge_y"]),"bal")
l(*b["side_west"]["vertical_stub"],cls="bal") if False else l(b["side_west"]["vertical_stub"][0],b["side_west"]["vertical_stub"][1],"bal")
l(b["side_west"]["raked"][0],b["side_west"]["raked"][1],"bal")
l(b["side_east"]["raked"][0],b["side_east"]["raked"][1],"bal")
r(b["railing"],"bal")

svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -40 420 850" width="840" height="1700">
<style>
 *{{fill:none;stroke-width:1;vector-effect:non-scaling-stroke}}
 .outer{{stroke:#c00;stroke-width:1.6}} .column{{stroke:#a000c8;stroke-width:1.6}}
 .ps{{stroke:#888}} .inner{{stroke:#e08000}} .pocket{{stroke:#00a000;stroke-width:1.6}}
 .panel{{stroke:#00c000;fill:#00c000;fill-opacity:.55}} .rail{{stroke:#00a000;stroke-dasharray:4 3}}
 .case{{stroke:#b08000}} .door{{stroke:#0040c8;stroke-width:1.4}} .doorthin{{stroke:#0040c8;stroke-dasharray:3 2}}
 .win{{stroke:#c800b4;stroke-width:1.6}} .bal{{stroke:#ff5a00;stroke-width:1.4}}
</style>
<!-- OIMACHI TRACKS RESIDENCE (SOHO) 1415 - 2D GEOMETRY MASTER, unit = source px -->
{chr(10).join(O)}
</svg>'''
open('out/geometry_master.svg','w').write(svg)
print('svg elements:',len(O))
