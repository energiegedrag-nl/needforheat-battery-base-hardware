"""Generate simple 3D models (STEP) for parts without a model in the KiCad library (pcb/bbase.3dshapes).

Adapted from tools/gen_3d_models.py of needforheat-p1-base-hardware.

- 2x8 2.54 mm male pin header XKB X6521WV-2x08H-C60D30 (C706898): 2.5 mm plastic on the board, 6.0 mm pins above
  it, 3.0 mm tails through the board.
- MYOUNG MY-AAA-15-J (+ plate, 1.43 mm button) and MY-AAA-16-J (- plate with spring, shown compressed as in the
  enclosure): 9.0 x 8.0 x 0.3 mm plate standing on the board, its 4.0 mm wide tab down through the board and
  trimmed (TAB_BELOW).
  Heights and the compressed spring length come from enclosure/kuip.py.

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
    pins = cq.Workplane("XY").pushPoints(pts).rect(0.64, 0.64).extrude(plastic + pin).translate((0, 0, -tail + 0.0))
    pins = pins.union(cq.Workplane("XY").pushPoints(pts).rect(0.64, 0.64).extrude(tail).translate((0, 0, -tail)))
    asm = cq.Assembly(name="PinHeader_2x08")
    asm.add(body.mirror("XZ"), name="body", color=BLACK)
    asm.add(pins.mirror("XZ"), name="pins", color=GOLD)
    return asm


def plate(plus):
    z0, h, w, t = 0.0, K.PLATE_BODY, K.PLATE_W, 0.3
    zc = K.CONTACT_C
    body = cq.Workplane("XY").box(w, t, h, centered=(True, True, False)).translate((0, 0, z0))
    below = K.PCB_T + K.TAB_BELOW  # tab through the board, trimmed
    tab = cq.Workplane("XY").box(4.0, t, below, centered=(True, True, False)).translate((0, 0, z0 - below + 0.01))
    metal = body.union(tab)
    if plus:  # button facing +y (footprint frame)
        button = (cq.Workplane("XZ").workplane(offset=-t / 2).center(0, zc).circle(2.0).extrude(-(K.BTN_H)))
        metal = metal.union(button)
    else:  # spring, compressed to the length it has in the enclosure, as five rings on a cone
        L = K.SPRING_LEN
        for k in range(5):
            r = 3.6 - 0.35 * k
            y = t / 2 + 0.3 + (L - 0.6) * k / 4
            ring = cq.Workplane("XZ").workplane(offset=-y).center(0, zc).circle(r).circle(r - 0.6).extrude(-0.6)
            metal = metal.union(ring)
    asm = cq.Assembly(name="MY_AAA_15_J" if plus else "MY_AAA_16_J")
    asm.add(metal.mirror("XZ"), name="plate", color=NICKEL)
    return asm


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, asm in (("PinHeader_2x08_C60D30_approx", pin_header()),
                      ("MYOUNG_MY-AAA-15-J_approx", plate(True)), ("MYOUNG_MY-AAA-16-J_approx", plate(False))):
        path = os.path.join(OUT, name + ".step")
        asm.save(path, exportType="STEP")
        print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
