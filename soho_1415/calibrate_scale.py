# -*- coding: utf-8 -*-
"""px -> mm calibration, run AFTER 2D GEOMETRY APPROVED.  Does not alter geometry."""
import numpy as np
CANDIDATES = [   # (label, measured px, assumed real mm, basis)
 ("Refrigerator alcove width",  53, 700, "standard 700 mm fridge bay"),
 ("Refrigerator alcove depth",  48, 650, "standard 650 mm"),
 ("Kitchen counter depth",      50, 650, "system kitchen 650 mm"),
 ("LD door clear opening",      62, 820, "interior door frame 820 mm"),
 ("Toilet door clear opening",  49, 650, "WC door frame 650 mm"),
 ("Powder door clear opening",  55, 730, "door frame 730 mm"),
 ("Entrance door clear opening",67, 880, "front door frame 880 mm"),
 ("W/D appliance bay width",    51, 680, "washer bay 640-700 mm"),
 ("West party wall thickness",  15, 200, "RC party wall 200 mm"),
 ("NE column width",            74, 975, "column ~1000 mm"),
 ("Partition panel thickness",   4,  53, "movable panel 45-55 mm"),
]
AREA_CHECK = [("wall-centre polygon, PS excluded", 233097, 40.76),
              ("wall-centre polygon, PS included", 235098, 40.76)]
ADOPTED = 13.2   # mm per px, provisional, +/-5%

if __name__ == "__main__":
    v=[]
    print(f'{"basis":32s} {"px":>4s} {"mm":>6s} {"mm/px":>7s}')
    for nm,px,mm,note in CANDIDATES:
        s=mm/px; v.append(s); print(f'{nm:32s} {px:4d} {mm:6d} {s:7.3f}   {note}')
    v=np.array(v)
    print(f'\nfixture median {np.median(v):.3f}  IQR {np.percentile(v,25):.2f}-{np.percentile(v,75):.2f}')
    for nm,a,m in AREA_CHECK:
        print(f'{nm:34s} {np.sqrt(m*1e6/a):.3f} mm/px')
    print(f'\nADOPTED {ADOPTED} mm/px  (1 m = {1000/ADOPTED:.2f} px).  Provisional, +/-5%.')
    print('No certain linear dimension is printed on the sheet; replace this with a '
          'site measurement before anything is fabricated.')
