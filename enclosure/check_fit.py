"""Fit check of the BatteryBASE enclosure (CadQuery):
1. inside the BatteryBASE: tray, lid and cradle against the PCB placeholder, the contacts, the cells and the
   header;
2. on a CoreInk (proxy body: 40 x 56 mm, LEGO through holes, bus socket 8 mm deep, flush);
3. the sliding lid: it slides out over its whole length without touching the tray or the cells (the click tab
   flexes, so it is left out of this check), and a lid turned round stops within 2 mm of entering;
4. on a P1-BASE v3: its lid and populated board from a checkout of needforheat-p1-base-hardware
   (enclosure/fabrication/p1-base-lid.step and enclosure/p1-base-v3-pcb.step), moved so that the P1-BASE lid top is
   the stand-on surface (z = 0).
Usage: python enclosure/check_fit.py [path to needforheat-p1-base-hardware]
The crush ribs of the LEGO posts press 0.05 mm into a 4.85 mm hole by design; the proxy holes are cut at the rib
diameter so they do not count as collisions.
"""
import os
import sys

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kuip as K  # noqa: E402

P1 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "needforheat-p1-base-hardware")


def vol(s):
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(s, p); return p.Mass()


def bbox(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b); return b.Get()


def overlap(a, b):
    c = BRepAlgoAPI_Common(a, b); c.Build()
    return vol(c.Shape()) if c.IsDone() else float("nan")


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a, b); return d.Value() if d.IsDone() else float("nan")


w = lambda wp: wp.val().wrapped  # noqa: E731
tray, lid = w(K.kuip()), w(K.lid())
pcb, cells, hdr = (w(x) for x in K.fit_parts())
cradle, cont = w(K.cradle()), w(K.contacts())
report, clear = [], []


def chk(an, a, bn, b):
    v = overlap(a, b)
    if v > 0.005:
        report.append(f"COLLISION {an} x {bn}: {v:.3f} mm3")
    d = dist(a, b)
    if v <= 0.005 and d < 0.5:
        clear.append((round(d, 2), an, bn))


# 1. inside
for an, a in (("tray", tray), ("lid", lid)):
    for bn, b in (("PCB", pcb), ("cells", cells), ("header", hdr)):
        chk(an, a, bn, b)
chk("tray", tray, "lid", lid)
# cradle and contacts: the cradle sits on the PCB and backs the plates; buttons and springs touch the cells
for bn, b in (("tray", tray), ("lid", lid), ("PCB", pcb), ("cells", cells), ("contacts", cont), ("header", hdr)):
    chk("cradle", cradle, bn, b)
for bn, b in (("tray", tray), ("lid", lid), ("PCB", pcb), ("cells", cells)):
    chk("contacts", cont, bn, b)
chk("header (tails on top)", hdr, "cells", cells)
chk("header (tails on top)", hdr, "contacts", cont)

# the sliding lid: path out towards the bottom edge (board +y = CadQuery -y), and the key against turning it round
tab = K.box(K.CI_W / 2 - K.TAB_W / 2 - 0.1, K.CI_W / 2 + K.TAB_W / 2 + 0.1, K.CI_H - K.TAB_L, K.CI_H + 1,
            K.Z_TOP - 1, K.Z_LID + 1)
rigid = K.lid().cut(tab).val()
for s in (0.5, 1, 2, 5, 10, 20, 30, 40, 50, K.CI_H):
    m = rigid.moved(cq.Location(cq.Vector(0, -s, 0))).wrapped
    for bn, b in (("tray", tray), ("cells", cells), ("cradle", cradle), ("contacts", cont)):
        v = overlap(m, b)
        if v > 0.005:
            report.append(f"COLLISION lid slid out {s} mm x {bn}: {v:.3f} mm3")
turned = K.lid().val().rotate(cq.Vector(K.CI_W / 2, -K.CI_H / 2, 0), cq.Vector(K.CI_W / 2, -K.CI_H / 2, 1), 180)
key_in = next((d for d in (0.5, 1.0, 1.5, 2.0)
               if overlap(turned.moved(cq.Location(cq.Vector(0, -(K.CI_H - d), 0))).wrapped, tray) > 0.005), None)
if key_in is None:
    report.append("KEY: a lid turned round enters more than 2 mm")

# 2. on a CoreInk
core = cq.Workplane("XY").center(K.CI_W / 2, -K.CI_H / 2).rect(K.CI_W, K.CI_H).extrude(-16).edges("|Z").fillet(K.CI_R)
for (x, y) in K.LEGO_HOLES:
    core = core.cut(cq.Workplane("XY").center(x, -y).circle(K.RIB_D / 2 + 0.02).extrude(-16))
core = core.cut(cq.Workplane("XY").center(*K.P(*K.BUS)).rect(K.BUS_W + 0.4, K.BUS_H + 0.4).extrude(-8.0))
core = w(core)
chk("tray", tray, "CoreInk", core)
chk("header", hdr, "CoreInk", core)
pins_in = -min(bbox(hdr)[2], 0)

# 4. on a P1-BASE v3
p1_lid_f = os.path.join(P1, "enclosure", "fabrication", "p1-base-lid.step")
p1 = None
if os.path.exists(p1_lid_f):
    sys.path.insert(0, os.path.join(P1, "enclosure"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("p1kuip", os.path.join(P1, "enclosure", "kuip.py"))
    PK = importlib.util.module_from_spec(spec); spec.loader.exec_module(PK)
    top = PK.Z_TOP + PK.LID_T  # P1-BASE lid top in its own frame
    mv = cq.Location(cq.Vector(0, 0, -top))
    p1_lid = cq.importers.importStep(p1_lid_f).val().moved(mv).wrapped
    # the P1-BASE lid's LEGO holes are 4.85 mm like the CoreInk's: the crush ribs press into them by design
    ring = None
    for (x, y) in K.LEGO_HOLES:
        r = (cq.Workplane("XY").workplane(offset=-K.POST_L - 1).center(*K.P(x, y)).circle(K.RIB_D / 2 + 0.05)
             .circle(K.LEGO_D / 2).extrude(K.POST_L + 1))
        ring = r if ring is None else ring.union(r)
    ribs = overlap(tray, w(ring))
    v = overlap(tray, p1_lid)
    if v - ribs > 0.005:
        report.append(f"COLLISION tray x P1-BASE lid: {v - ribs:.3f} mm3 (plus {ribs:.3f} mm3 of crush ribs, by design)")
    else:
        clear.append((0.0, "tray (crush ribs only, %.2f mm3)" % ribs, "P1-BASE lid"))
    chk("header", hdr, "P1-BASE lid", p1_lid)
    # the P1-BASE's J1 socket body (from its populated board STEP), moved into this frame
    sys.path.insert(0, os.path.join(P1, "tools", "checks"))
    import stepnames
    j1 = [cq.Shape.cast(s).moved(cq.Location(cq.Vector(-100, 100, PK.GAP - top))).wrapped
          for n, s in stepnames.read(os.path.join(P1, "enclosure", "p1-base-v3-pcb.step")) if n.split("/")[0] == "J1"]
    for s in j1:
        chk("tray", tray, "P1 J1 socket", s)
    j1_top = max(bbox(s)[5] for s in j1)
    p1 = (top, j1_top)

print("COLLISIONS:", "\n  ".join([""] + report) if report else "none")
print("closest approach < 0.5 mm:", sorted(clear))
print(f"lid top {K.Z_TOP + K.LID_T:.1f} mm above the stand-on surface; cells {K.AAA_D} mm, top at z = {K.CELL_TOP:.1f}")
print(f"sliding lid: slides out freely; turned round it stops after {key_in} mm")
print(f"header pins reach {pins_in:.1f} mm below the stand-on surface (CoreInk socket 8.0 mm deep)")
if p1:
    print(f"on a P1-BASE: its J1 socket top at z = {p1[1]:.2f} (0 = flush with the P1-BASE lid)")
else:
    print("P1-BASE checkout not found: step 3 skipped")
