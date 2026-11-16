"""Generate simple 3D models (STEP) for parts without a model in the KiCad library (pcb/bbase.3dshapes).

Adapted from tools/gen_3d_models.py of needforheat-p1-base-hardware.

- 2x8 2.54 mm male pin header XKB X6521WV-2x08H-C60D30 (C706898): 2.5 mm plastic on the board, 6.0 mm pins above
  it, 3.0 mm tails through the board.
- MYOUNG MY-AAA-01 leaf contact: foot on the board, two pins down into it, the leaf at the outer end (free
  position) with its dimple. Dimensions from enclosure/kuip.py.

Models are approximations for renders and fit checks. Origin = footprint origin, z = 0 at the board surface on the
footprint's side. Shapes are drawn in footprint coordinates (y down) and mirrored, because KiCad model y points up.

Needs CadQuery:  python tools/gen_3d_models.py
"""
import os
import sys

import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pcb", "bbase.3dshapes")
sys.path.insert(0, os.path.join(ROOT, "enclosure"))
import kuip as K  # noqa: E402

BLACK = cq.Color(0.10, 0.10, 0.10)
GOLD = cq.Color(0.85, 0.70, 0.25)
NICKEL = cq.Color(0.78, 0.78, 0.76)


def pin_header():
    p, rows, cols, plastic, pin, tail = 2.54, 8, 2, 2.5, 6.0, 3.0
    body = cq.Workplane("XY").box(cols * p, rows * p, plastic, centered=(True, True, False))
    pts = [((c - 0.5) * p, (r - 3.5) * p) for c in range(cols) for r in range(rows)]
    # one straight pin per position: tail (-tail..0) through the board, then plastic + mating pin (0..plastic + pin)
    pins = cq.Workplane("XY").pushPoints(pts).rect(0.64, 0.64).extrude(tail + plastic + pin).translate((0, 0, -tail))
    asm = cq.Assembly(name="PinHeader_2x08")
    asm.add(body.mirror("XZ"), name="body", color=BLACK)
    asm.add(pins.mirror("XZ"), name="pins", color=GOLD)
    return asm


def leaf():
    """Origin = outer pin, the foot and the inner pin along +y (footprint frame, y down), leaf at y = -PIN_OUT."""
    w, yb = K.LEAF_W, -K.PIN_OUT
    t = K.FOOT_T
    foot = cq.Workplane("XY").box(w, K.FOOT_L, t, centered=(True, False, False)).translate((0, yb, 0))
    lean = K.LEAF_LEAN
    pts = [(yb, 0), (yb + K.LEAF_T, 0), (yb + K.LEAF_T + lean, K.LEAF_H + t), (yb + lean, K.LEAF_H + t)]
    blade = cq.Workplane("YZ").workplane(offset=-w / 2).polyline(pts).close().extrude(w)
    yd = yb + K.LEAF_T + lean * K.DIMPLE_Z / K.LEAF_H
    dimple = cq.Workplane("XZ").workplane(offset=-yd).center(0, t + K.DIMPLE_Z).circle(1.25).extrude(-K.DIMPLE_H)
    pins = cq.Workplane("XY").pushPoints([(0, 0), (0, K.PIN_PITCH)]).circle(K.PIN_D / 2).extrude(-K.PIN_LEN)
    metal = foot.union(blade).union(dimple).union(pins)
    asm = cq.Assembly(name="MY_AAA_01")
    asm.add(metal.mirror("XZ"), name="leaf", color=NICKEL)
    return asm


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, asm in (("PinHeader_2x08_C60D30_approx", pin_header()),
                      ("MYOUNG_MY-AAA-01_approx", leaf())):
        path = os.path.join(OUT, name + ".step")
        asm.save(path, exportType="STEP")
        print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
