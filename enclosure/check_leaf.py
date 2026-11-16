"""Fit check of the real leaf contacts: the vendor's 3D model of the MY-AAA-01 (pcb/bbase.3dshapes, placed by
tools/import_leaf_model.py) at the six contact places, free and pressed back by the shortest and the longest cell,
against the tray, the lid, the cradle and each other.

The pressed leaf is the model's leaf (everything above the foot) turned about its bend, so that the dimple's tip
moves back as far as the cell pushes it. A real leaf bends along its length rather than only at the bend; turning
it whole swings its top out the most, which is the worst case for the rib behind it.

Run with the same Python as kuip.py:  python enclosure/check_leaf.py
"""
import math
import os

import cadquery as cq

import kuip as K

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(os.path.dirname(HERE), "pcb", "bbase.3dshapes", "MYOUNG_MY-AAA-01.step")
BEND_Y, BEND_Z = K.PIN_OUT, K.FOOT_T  # bend axis in the model's frame (leaf towards +y, outer pin at the origin)
TIP_Y, TIP_Z = -1.34, K.FOOT_T + K.DIMPLE_Z  # dimple tip, free
CUT_Z = K.FOOT_T + 0.1  # the leaf is everything above this


def leaf_model(defl):
    """The vendor model, its leaf turned back by defl at the dimple (model frame)."""
    m = cq.importers.importStep(MODEL).val()
    if defl == 0:
        return m
    hi = cq.Solid.makeBox(20, 20, 20, cq.Vector(-10, -10, CUT_Z))
    foot, leaf = m.cut(hi), m.intersect(hi)
    ang = -math.degrees(math.atan2(defl, TIP_Z - BEND_Z))  # about +x: the leaf's top moves to +y (outwards)
    leaf = leaf.rotate(cq.Vector(0, BEND_Y, BEND_Z), cq.Vector(1, BEND_Y, BEND_Z), ang)
    return foot.fuse(leaf)


def placed(m, end, xc, yo):
    """Model frame -> enclosure (CadQuery coordinates: y up = -board y). Top end: leaf towards the top edge."""
    if end == "bottom":
        m = m.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
    return m.translate(cq.Vector(xc, -yo, K.Z_PCB))


def gap(a, b):
    """Overlap volume (mm3), or the distance when they do not touch."""
    v = a.intersect(b).Volume()
    return (v, 0.0) if v > 1e-4 else (0.0, a.distance(b))


def main():
    tray, lid, cradle = K.kuip().val(), K.lid().val(), K.cradle().val()
    pcb = K.fit_parts()[0].val()
    defl_min, defl_max = K.LEAF_DEFL
    rows = []
    for label, defl in (("free", 0.0), (f"pressed {defl_min:.2f} mm (shortest cell)", defl_min),
                        (f"pressed {defl_max:.2f} mm (longest cell)", defl_max)):
        m = leaf_model(defl)
        parts = [placed(m, end, xc, yo) for end, xc, _, yo, _ in K.contact_list()]
        allc = parts[0]
        for p in parts[1:]:
            allc = allc.fuse(p)
        above = allc.intersect(cq.Solid.makeBox(60, 80, 30, cq.Vector(-10, -70, K.Z_PCB + 0.01)))
        for name, other in (("tray", tray), ("lid", lid), ("cradle", cradle), ("PCB (the feet rest on it)", pcb)):
            v, d = gap(above if name.startswith("PCB") else allc, other)
            rows.append((label, name, v, d))
        bb = above.BoundingBox()
        rows.append((label, "highest point above the PCB", 0.0, bb.zmax - K.Z_PCB))
        rows.append((label, "lid underside above the PCB", 0.0, K.Z_TOP - K.Z_PCB))
    bad = False
    for label, name, v, d in rows:
        if name.startswith("highest") or name.startswith("lid underside"):
            print(f"{label:38s} {name:30s} {d:6.2f} mm")
            continue
        flag = ""
        if v > 0 and not name.startswith("PCB"):
            flag, bad = "  COLLISION", True
        elif v == 0 and d < 0.25 and not name.startswith("PCB"):
            flag = "  tight"
        print(f"{label:38s} {name:30s} " + (f"overlap {v:.3f} mm3" if v else f"gap {d:.2f} mm") + flag)
    print("RESULT:", "COLLISION" if bad else "fits")


if __name__ == "__main__":
    main()
