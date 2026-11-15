"""Parametric enclosure ("kuip") for the NeedForHeat BatteryBASE: tray with a sliding battery lid.

Build with CadQuery 2.x:  python enclosure/kuip.py
Writes enclosure/fabrication/battery-base-kuip.{step,stl}, battery-base-lid.{step,stl} and
battery-base-fit.step (tray, lid, PCB placeholder, cells and header, for a visual check).

Frame (same as the P1-BASE v3 enclosure): x to the right, y down from the top left corner of the CoreInk's back
(HAT edge up, as seen from behind), z up from the surface the BatteryBASE stands on: the CoreInk's back, or the
lid of a P1-BASE v3, which repeats the CoreInk's back (LEGO holes and a flush 2x8 bus socket at the same places).

* The outside is exactly the CoreInk outline (40 x 56 mm, R3), walls inside it, like the P1-BASE v3.
* Four LEGO posts underneath (at the CoreInk's LEGO holes), 7 mm long, three crush ribs.
* A 36.3 x 52.3 mm PCB on corner blocks, 2.5 mm above z = 0, keyed by three pegs (same places as the P1-BASE v3).
* Three AAA cells lying on the PCB in PCB-mounted clips (ASSUMED lift and clip length, VERIFY with the chosen part).
* A sliding lid, like a remote control's battery door. It slides out towards the bottom edge (the edge that faces
  down when the CoreInk hangs or stands) and clicks shut: a flexible tab in the lid carries a bump that drops into a
  dimple in the top of the bottom wall. The lid's long edges run in grooves in the long walls and the top wall.
  The lid ends in a cap of the full outline width that forms the top of the bottom wall and its two corners.
  Turned round, that cap leads and is wider than the opening between the long walls: it stops at first touch, so
  the lid fits one way only.
* The polarity of each cell is shown where the user looks while inserting the cells: on the PCB silkscreen under
  each cell (and by the spring = minus convention of the clips). The lid's outside only shows "3x AAA" and an
  arrow at the grip tab that points the way the lid slides out.
The BatteryBASE is the end of a stack: the lid has no LEGO holes and no bus socket.

All dimensions in mm. Values marked VERIFY are assumptions, not measured parts.
"""
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fabrication")

# --- CoreInk back / P1-BASE v3 lid (from needforheat-p1-base-hardware enclosure/kuip.py) ---------------------
CI_W, CI_H, CI_R = 40.0, 56.0, 3.0
LEGO_HOLES = [(4, 4), (36, 4), (4, 52), (36, 52)]
LEGO_D = 4.85
BUS = (33.97, 36.87)  # centre of the 2x8 bus socket
BUS_W, BUS_H = 5.08, 20.32

# --- enclosure (same values as the P1-BASE v3) ---------------------------------------------------------------
CLR = 0.25  # walls to PCB
WALL = 1.6
POST = 6.0
POST_D, POST_L = 4.6, 7.0
RIB_D, RIB_W = 4.95, 0.45
PEG_D = 2.0

# --- BatteryBASE board and cells --------------------------------------------------------------------------
GAP = 2.5  # stand-on surface -> PCB bottom = plastic of a standard 2x8 male header
PCB_T = 1.6
INSET = WALL + CLR  # PCB = CoreInk outline minus INSET on every side: 36.3 x 52.3 mm (as the P1-BASE v3)
PEGS = [(36, 4), (4, 52), (36, 52)]  # Ø2.2 NPTH in the PCB, as on the P1-BASE v3; the top-left corner keys the PCB
HDR_PIN = 6.0  # header pins below the plastic, into the socket below
AAA_D, AAA_L = 10.5, 44.5
CELL_PITCH = 11.2  # cells side by side along x (0.7 mm between them, VERIFY with the clips)
CELL_X = [CI_W / 2 - CELL_PITCH, CI_W / 2, CI_W / 2 + CELL_PITCH]
CELL_Y0 = (CI_H - AAA_L) / 2  # cells centred along y
CELL_LIFT = 1.0  # cell surface above the PCB top (VERIFY with the clips)
CLIP_L = CELL_Y0 - WALL - 0.15  # room at each end of a cell for its contact: 4.0 mm (VERIFY with the clips)
CELL_TOP = GAP + PCB_T + CELL_LIFT + AAA_D

# --- sliding lid -------------------------------------------------------------------------------------------
LID_T = 2.0
Z_TOP = CELL_TOP + 0.5  # lid underside: flat, 0.5 mm above the cells. The clips hold the cells; the lid only stops
# them from jumping out. No ribs under the lid: they would hit the bottom wall when the lid slides out.
Z_LID = Z_TOP + LID_T  # outer face
GR_D = 0.7  # groove depth into the long walls and the top wall (the lid's tongue runs in it)
TONGUE_H = 0.8  # tongue: the lower part of the lid's edge
GR_H = TONGUE_H + 0.2  # groove height (0.2 mm vertical play)
SL_CLR = 0.2  # sideways play of the lid in the walls and grooves, per side (MJF PA12, VERIFY on the print)
CAP_GAP = 0.1  # seam between the cap and the ends of the long walls
# click: tab in the lid, open towards the bottom edge, thinned from the outside so it flexes (and as a thumb rest)
TAB_W, TAB_L = 10.0, 12.0
TAB_SLOT = 0.8
TAB_T = 1.3  # tab thickness; the rest of LID_T is a recess for the thumb
DET_H = 0.4  # bump height below the lid's underside (VERIFY: more = firmer click)
DET_B = 1.0  # bump base length along y (both flanks ≈ 39°, so a firm pull opens it without pressing)
DET_Y = CI_H - WALL / 2  # bump centre, over the bottom wall
assert WALL - GR_D >= 0.8, "wall too thin behind the groove"
assert LID_T - GR_H >= 0.9, "wall overhang above the groove too thin"

# shipping: each module goes loose (not stacked) in a letterbox parcel (PostNL brievenbuspakje, max. 32 mm thick);
# 27 mm leaves ≥ 5 mm for the box and padding. Thickness = lid top to the tips of the LEGO posts.
SHIP_MAX = 27.0
SHIP_T = Z_LID + POST_L
assert SHIP_T <= SHIP_MAX, f"BatteryBASE is {SHIP_T:.1f} mm thick, more than {SHIP_MAX} mm for a letterbox parcel"


def slab(w, h, r, z0, z1, off=0.0):
    """Rounded rectangle around the CoreInk outline grown by `off`, from z0 to z1."""
    return (cq.Workplane("XY").workplane(offset=z0)
            .center(CI_W / 2, -CI_H / 2).rect(w + 2 * off, h + 2 * off)
            .extrude(z1 - z0).edges("|Z").fillet(r + off if r + off > 0.2 else 0.2))


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box in board coordinates (y down)."""
    return (cq.Workplane("XY").workplane(offset=z0).center((x0 + x1) / 2, -(y0 + y1) / 2)
            .rect(x1 - x0, y1 - y0).extrude(z1 - z0))


def channel(off, z0, z1, y_end):
    """Inside outline grown by `off` (negative = inward from the CoreInk outline), with a square end at y_end
    instead of the rounded bottom corners: the shape of the lid and of the slot it slides in."""
    half = CI_W / 2 + off
    return slab(CI_W, CI_H, CI_R, z0, z1, off).union(box(CI_W / 2 - half, CI_W / 2 + half, CI_H / 2, y_end, z0, z1))


def ridge(y, x0, x1, z, h, b, up=False):
    """Triangular ridge along x, base b along y centred on y, apex h below (or above) z."""
    s = 1 if up else -1
    return (cq.Workplane("YZ").workplane(offset=x0)
            .polyline([(-(y - b / 2), z), (-(y + b / 2), z), (-y, z + s * h)]).close()
            .extrude(x1 - x0))


def P(x, y):
    """Board coordinates to CadQuery XY (y up)."""
    return (x, -y)


def lego_post(x, y, z0, length=POST_L):
    """LEGO-compatible post pointing down from z0: core, three crush ribs, a lead-in at the tip."""
    c = P(x, y)
    core = cq.Workplane("XY").workplane(offset=z0 + 0.5).center(*c).circle(POST_D / 2).extrude(-(length - 0.8 + 0.5))
    tip = (cq.Workplane("XY").workplane(offset=z0 - (length - 0.8)).center(*c).circle(POST_D / 2)
           .workplane(offset=-0.8).circle(POST_D / 2 - 0.6).loft())
    post = core.union(tip)
    for k in range(3):
        rib = (cq.Workplane("XY").workplane(offset=z0 - 0.8).center(*c)
               .center((POST_D / 2 - 0.1 + RIB_D / 2) / 2, 0).rect((RIB_D - POST_D) / 2 + 0.1, RIB_W)
               .extrude(-(length - 2.4)).rotate((c[0], c[1], 0), (c[0], c[1], 1), 120 * k))
        post = post.union(rib)
    return post


def kuip():
    body = slab(CI_W, CI_H, CI_R, 0.0, Z_LID).cut(slab(CI_W, CI_H, CI_R, -1, Z_LID + 1, -WALL))
    for (x, y) in LEGO_HOLES:
        x0, x1 = (0.0, x + POST / 2) if x < CI_W / 2 else (x - POST / 2, CI_W)
        y0, y1 = (0.0, y + POST / 2) if y < CI_H / 2 else (y - POST / 2, CI_H)
        block = box(x0, x1, y0, y1, 0.0, GAP).intersect(slab(CI_W, CI_H, CI_R, 0.0, GAP))
        body = body.union(block).union(lego_post(x, y, 0.0))
        if (x, y) in PEGS:
            body = body.union(cq.Workplane("XY").workplane(offset=GAP).center(*P(x, y)).circle(PEG_D / 2)
                              .extrude(PCB_T - 0.2))
    # square ends at the open bottom end (no inner corner radius in the way of the lid)
    body = body.cut(channel(-WALL, Z_TOP, Z_LID + 1, CI_H + 1))
    # groove for the lid's tongue in the long walls and the top wall, open at the bottom end
    body = body.cut(channel(-WALL + GR_D, Z_TOP, Z_TOP + GR_H, CI_H + 1))
    # the lid's cap replaces the top of the bottom wall and its corners
    body = body.cut(box(-1, CI_W + 1, CI_H - WALL, CI_H + 1, Z_TOP, Z_LID + 1))
    # dimple for the click bump in the top of the bottom wall, under the tab
    body = body.cut(ridge(DET_Y, CI_W / 2 - TAB_W / 2 + 0.5, CI_W / 2 + TAB_W / 2 - 0.5, Z_TOP + 0.01,
                          DET_H + 0.15, DET_B + 0.3))
    # lead-in on the outer top edge of the bottom wall, where the bump climbs on
    body = body.cut(ridge(CI_H, CI_W / 2 - TAB_W / 2 + 0.5, CI_W / 2 + TAB_W / 2 - 0.5, Z_TOP + 0.01, 0.4, 0.8))
    # orientation mark on the top edge (HAT side), like the P1-BASE
    body = body.cut(cq.Workplane("XY").workplane(offset=Z_LID).center(*P(CI_W / 2, WALL / 2))
                    .polygon(3, 1.4).extrude(-0.4))
    return body


def lid():
    y_cap = CI_H - WALL + CAP_GAP
    plate = channel(-WALL - SL_CLR, Z_TOP, Z_LID, y_cap + 0.01)
    tongue = channel(-WALL + GR_D - SL_CLR, Z_TOP, Z_TOP + TONGUE_H, y_cap + 0.01)
    cap = box(-1, CI_W + 1, y_cap, CI_H + 1, Z_TOP, Z_LID).intersect(slab(CI_W, CI_H, CI_R, Z_TOP, Z_LID))
    body = plate.union(tongue).union(cap)
    # tab: two slots open at the bottom edge, thinned from the outside (thumb rest), grip ridges, click bump below
    tx0, tx1 = CI_W / 2 - TAB_W / 2, CI_W / 2 + TAB_W / 2
    for x in (tx0 - TAB_SLOT / 2, tx1 + TAB_SLOT / 2):
        body = body.cut(box(x - TAB_SLOT / 2, x + TAB_SLOT / 2, CI_H - TAB_L, CI_H + 1, Z_TOP - 1, Z_LID + 1))
    body = body.cut(box(tx0 - TAB_SLOT, tx1 + TAB_SLOT, CI_H - TAB_L + 1.5, CI_H - 1.0, Z_TOP + TAB_T, Z_LID + 1))
    for k in range(4):
        body = body.union(ridge(CI_H - 3.0 - 1.6 * k, tx0 + 1, tx1 - 1, Z_TOP + TAB_T - 0.01, 0.5, 0.8, up=True))
    body = body.union(ridge(DET_Y, tx0 + 1, tx1 - 1, Z_TOP + 0.01, DET_H + 0.01, DET_B))
    assert Z_TOP - DET_H > CELL_TOP, "the click bump would rub over the middle cell"  # it slides over it
    # outside: arrow next to the tab pointing the way the lid slides out, and "3x AAA"
    for sx in (tx0 - 5.0, tx1 + 5.0):
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_LID - 0.4).center(*P(sx, CI_H - 6.0))
                        .transformed(rotate=(0, 0, -90)).polygon(3, 4.0).extrude(0.5))
    try:
        txt = (cq.Workplane("XY").workplane(offset=Z_LID - 0.4).center(*P(CI_W / 2, 18.0))
               .text("3x AAA", 5.0, 0.5, combine=False, halign="center", valign="center"))
        body = body.cut(txt.val().fuse())  # fuse the glyphs first: a cut with the raw text compound goes wrong
    except Exception as e:  # no font available: leave the text off
        print("no text on the lid:", e)
    return body


def fit_parts():
    """Placeholders for the fit check: PCB, cells and the header (plastic + pins)."""
    pcb = (cq.Workplane("XY").workplane(offset=GAP).center(*P(CI_W / 2, CI_H / 2))
           .rect(CI_W - 2 * INSET, CI_H - 2 * INSET).extrude(PCB_T).edges("|Z").fillet(CI_R - INSET + 0.5))
    for (x, y) in PEGS:
        pcb = pcb.cut(cq.Workplane("XY").workplane(offset=GAP - 0.1).center(*P(x, y)).circle(1.1).extrude(PCB_T + 0.2))
    cells = None
    for x in CELL_X:
        c = cq.Workplane("XY").add(cq.Solid.makeCylinder(
            AAA_D / 2, AAA_L, cq.Vector(x, -CELL_Y0, GAP + PCB_T + CELL_LIFT + AAA_D / 2), cq.Vector(0, -1, 0)))
        cells = c if cells is None else cells.union(c)
    hdr = cq.Workplane("XY").center(*P(*BUS)).rect(BUS_W, BUS_H).extrude(GAP)
    pts = [(BUS[0] + (c - 0.5) * 2.54, BUS[1] + (r - 3.5) * 2.54) for c in range(2) for r in range(8)]
    pins = cq.Workplane("XY").pushPoints([P(*p) for p in pts]).rect(0.64, 0.64).extrude(-HDR_PIN)
    return pcb, cells, hdr.union(pins)


def main():
    os.makedirs(OUT, exist_ok=True)
    k, l = kuip(), lid()
    for name, part in (("battery-base-kuip", k), ("battery-base-lid", l)):
        cq.exporters.export(part, os.path.join(OUT, name + ".step"))
        cq.exporters.export(part, os.path.join(OUT, name + ".stl"), tolerance=0.02, angularTolerance=0.1)
        print("wrote", name)
    pcb, cells, hdr = fit_parts()
    asm = cq.Assembly(name="battery-base-fit")
    asm.add(k, name="tray", color=cq.Color(0.9, 0.9, 0.9))
    asm.add(l, name="lid", color=cq.Color(0.3, 0.3, 0.3))
    asm.add(pcb, name="pcb", color=cq.Color(0.1, 0.4, 0.1))
    asm.add(cells, name="cells", color=cq.Color(0.8, 0.5, 0.1))
    asm.add(hdr, name="header", color=cq.Color(0.1, 0.1, 0.1))
    asm.save(os.path.join(OUT, "battery-base-fit.step"), exportType="STEP")
    print("wrote battery-base-fit")
    print(f"thickness for shipping (lid top to post tips): {SHIP_T:.1f} mm (max. {SHIP_MAX} mm)")
    print(f"height above the stand-on surface: {Z_LID:.1f} mm (lid top), cells end at z = {CELL_TOP:.1f}")
    print(f"room for the contacts at each cell end: {CLIP_L:.2f} mm")


if __name__ == "__main__":
    main()
