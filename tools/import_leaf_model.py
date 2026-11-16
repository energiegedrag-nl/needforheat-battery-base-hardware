"""Place the vendor 3D model of the MYOUNG MY-AAA-01 leaf contact (C964855) in the footprint's frame.

Source: the STEP model that LCSC/EasyEDA links to C964855 ("BAT-SMD_MY-AAA-01", SolidWorks 2020, 2022-06-16),
downloaded from modules.easyeda.com (3D model uuid 2dbab2f565534596a312e285c5bc1598). In that file the foot runs
along x, the leaf rises at +x, z = 0 is the board; the outer pin is at x = 4.23, the inner pin at x = -6.02.

The footprint (tools/gen_footprints.py) has its origin on the outer pin, the inner pin at y = +10.25 (KiCad y down)
and the leaf at negative y. KiCad model y points up, so: rotate +90 deg about z (leaf to +y), outer pin to the origin.

Needs CadQuery:  python tools/import_leaf_model.py <downloaded.step>
"""
import os
import sys

import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pcb", "bbase.3dshapes", "MYOUNG_MY-AAA-01.step")
PIN_OUT_X, PIN_IN_X = 4.23, -6.02  # pin centres in the vendor file
NICKEL = cq.Color(0.78, 0.78, 0.76)


def main(src):
    shape = cq.importers.importStep(src).val()
    pins = shape.intersect(cq.Solid.makeBox(40, 20, 0.5, cq.Vector(-20, -10, -1.2))).Solids()
    xs = sorted(round(p.BoundingBox().center.x, 2) for p in pins)
    assert xs == [PIN_IN_X, PIN_OUT_X], f"unexpected pin positions {xs}"
    placed = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).translate(cq.Vector(0, -PIN_OUT_X, 0))
    asm = cq.Assembly(name="MY_AAA_01")
    asm.add(placed, name="leaf", color=NICKEL)
    asm.save(OUT, exportType="STEP")
    b = placed.BoundingBox()
    print("wrote", os.path.normpath(OUT), f"bbox x {b.xmin:.2f}..{b.xmax:.2f} y {b.ymin:.2f}..{b.ymax:.2f} "
          f"z {b.zmin:.2f}..{b.zmax:.2f}")


if __name__ == "__main__":
    main(sys.argv[1])
