"""Parametric enclosure ("kuip") for the NeedForHeat BatteryBASE, first version for a fit check.

Build with CadQuery 2.x:  python enclosure/kuip.py
Writes enclosure/fabrication/battery-base-kuip.{step,stl}, battery-base-lid.{step,stl} and
battery-base-fit.step (tray, lid, PCB placeholder, cells and header, for a visual check).

Frame (same as the P1-BASE v3 enclosure): x to the right, y down from the top left corner of the CoreInk's back
(HAT edge up, as seen from behind), z up from the surface the BatteryBASE stands on: the CoreInk's back, or the
lid of a P1-BASE v3, which repeats the CoreInk's back (LEGO holes and a flush 2x8 bus socket at the same places).

The PCB is not designed yet. This version fixes the mechanics around it, so a print can be tried on a CoreInk and on
a P1-BASE:
* four LEGO posts underneath (at the CoreInk's LEGO holes), 7 mm long, three crush ribs, no flared root (the post
  grows out of a corner block; anything wider below z = 0 would sit in the CoreInk's back);
* a 40 x 56 mm PCB on the corner blocks, 2.5 mm above z = 0, keyed by three pegs (like the P1-BASE);
* a plain 2x8 male header under the PCB (2.5 mm plastic = the gap, 6 mm pins into the socket below);
* three AAA cells lying on the PCB, held by PCB-mounted clips (ASSUMED: cell axis 1.0 mm above the board surface
  plus the cell radius; VERIFY with the chosen clips or holder);
* a lid that clicks on (same snap fit as the P1-BASE lid) and holds the cells down with ribs; it comes off without
  tools (pry notch) to replace the cells.
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

# --- BatteryBASE board and cells --------------------------------------------------------------------------
GAP = 2.5  # stand-on surface -> PCB bottom = plastic of a standard 2x8 male header
PCB_T = 1.6
PEGS = [(4, 4), (36, 4), (4, 52)]  # Ø2.2 NPTH in the PCB, as on the P1-BASE; the 4th corner keys the PCB
HDR_PIN = 6.0  # header pins below the plastic, into the socket below
AAA_D, AAA_L = 10.5, 44.5
CELL_PITCH = 11.2  # cells side by side along x (0.7 mm between them for the clip tabs, VERIFY)
CELL_X = [CI_W / 2 - CELL_PITCH, CI_W / 2, CI_W / 2 + CELL_PITCH]
CELL_Y0 = (CI_H - AAA_L) / 2  # cells centred along y; 5.75 mm at each end for the clips
CELL_LIFT = 1.0  # cell surface above the PCB top (VERIFY with the clips)
CLIP_L = 4.5  # room at each end of a cell for a spring/plate clip (VERIFY)

# --- enclosure (same values as the P1-BASE v3) ---------------------------------------------------------------
CLR = 0.25
WALL = 1.6
POST = 6.0
POST_D, POST_L = 4.6, 7.0
RIB_D, RIB_W = 4.95, 0.45
PEG_D = 2.0
LIP_H, LIP_T = 1.8, 1.0
SNAP_R, SNAP_P = 0.6, 0.35
SNAP_L = 7.0
SNAP_Y = [14.0, 42.0]
GROOVE_D = 0.55
LID_T = 1.4
CELL_TOP = GAP + PCB_T + CELL_LIFT + AAA_D
Z_TOP = CELL_TOP + 0.6  # lid underside: 0.6 mm above the cells; ribs under the lid close the gap to 0.2 mm
# shipping: each module goes loose (not stacked) in a letterbox parcel (PostNL brievenbuspakje, max. 32 mm thick);
# 27 mm leaves ≥ 5 mm for the box and padding. Thickness = lid top to the tips of the LEGO posts.
SHIP_MAX = 27.0
SHIP_T = Z_TOP + LID_T + POST_L
assert SHIP_T <= SHIP_MAX, f"BatteryBASE is {SHIP_T:.1f} mm thick, more than {SHIP_MAX} mm for a letterbox parcel"


def slab(w, h, r, z0, z1, off=0.0):
    """Rounded rectangle around the CoreInk outline grown by `off`, from z0 to z1."""
    return (cq.Workplane("XY").workplane(offset=z0)
            .center(CI_W / 2, -CI_H / 2).rect(w + 2 * off, h + 2 * off)
            .extrude(z1 - z0).edges("|Z").fillet(r + off if r + off > 0.2 else 0.2))


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
    outer = slab(CI_W, CI_H, CI_R, 0.0, Z_TOP, CLR + WALL)
    inner = slab(CI_W, CI_H, CI_R, -1, Z_TOP + 1, CLR)
    body = outer.cut(inner)
    for (x, y) in LEGO_HOLES:
        x0, x1 = (-CLR - 0.3, x + POST / 2) if x < CI_W / 2 else (x - POST / 2, CI_W + CLR + 0.3)
        y0, y1 = (-CLR - 0.3, y + POST / 2) if y < CI_H / 2 else (y - POST / 2, CI_H + CLR + 0.3)
        block = cq.Workplane("XY").center(*P((x0 + x1) / 2, (y0 + y1) / 2)).rect(x1 - x0, y1 - y0).extrude(GAP)
        body = body.union(block).union(lego_post(x, y, 0.0))
        if (x, y) in PEGS:
            body = body.union(cq.Workplane("XY").workplane(offset=GAP).center(*P(x, y)).circle(PEG_D / 2)
                              .extrude(PCB_T - 0.2))
    # snap-fit grooves (inner face of the long walls) and a pry notch in the top of the bottom wall
    zb = Z_TOP - LIP_H / 2
    for x in (-CLR - GROOVE_D / 2, CI_W + CLR + GROOVE_D / 2):
        for y in SNAP_Y:
            body = body.cut(cq.Workplane("XY").workplane(offset=zb - SNAP_R - 0.15).center(*P(x, y))
                            .rect(GROOVE_D + 0.02, SNAP_L + 1.0).extrude(2 * SNAP_R + 0.3))
    body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP - 0.8).center(*P(CI_W / 2, CI_H + CLR + WALL / 2))
                    .rect(6.0, WALL + 1.0).extrude(1.0))
    # orientation mark on the top edge (HAT side), like the P1-BASE
    body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP).center(*P(CI_W / 2, -CLR - WALL / 2))
                    .polygon(3, 2.4).extrude(-0.4))
    return body


def lid():
    plate = slab(CI_W, CI_H, CI_R, Z_TOP, Z_TOP + LID_T, CLR + WALL)
    lip = slab(CI_W, CI_H, CI_R, Z_TOP - LIP_H, Z_TOP, CLR - 0.15).cut(
        slab(CI_W, CI_H, CI_R, Z_TOP - LIP_H - 0.5, Z_TOP + 1, CLR - 0.15 - LIP_T))
    zb = Z_TOP - LIP_H / 2
    for x, sgn in ((-(CLR - 0.15), -1), (CI_W + CLR - 0.15, 1)):
        for y in SNAP_Y:
            cx = x + sgn * (SNAP_P - SNAP_R)
            lip = lip.union(cq.Workplane("XY").add(cq.Solid.makeCylinder(
                SNAP_R, SNAP_L, cq.Vector(cx, -y - SNAP_L / 2, zb), cq.Vector(0, 1, 0))))
    body = plate.union(lip)
    # ribs over each cell that keep it in its clips (0.2 mm above the cell)
    for x in CELL_X:
        for y in (CELL_Y0 + 8, CELL_Y0 + AAA_L - 8):
            body = body.union(cq.Workplane("XY").workplane(offset=Z_TOP).center(*P(x, y)).rect(4.0, 2.0)
                              .extrude(-(Z_TOP - CELL_TOP - 0.2)))
    # cell outline and polarity on the outside of the lid (engraved 0.4 mm), so the user knows what is inside
    for i, x in enumerate(CELL_X):
        plus_at_top = i % 2 == 0
        y_plus = CELL_Y0 + 3 if plus_at_top else CELL_Y0 + AAA_L - 3
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP + LID_T - 0.4).center(*P(x, y_plus))
                        .rect(3.0, 0.7).extrude(0.4))
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP + LID_T - 0.4).center(*P(x, y_plus))
                        .rect(0.7, 3.0).extrude(0.4))
        y_min = CELL_Y0 + AAA_L - 3 if plus_at_top else CELL_Y0 + 3
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP + LID_T - 0.4).center(*P(x, y_min))
                        .rect(3.0, 0.7).extrude(0.4))
    return body


def fit_parts():
    """Placeholders for the fit check: PCB, cells and the header (plastic + pins)."""
    pcb = cq.Workplane("XY").workplane(offset=GAP).center(*P(CI_W / 2, CI_H / 2)).rect(CI_W - 0.2, CI_H - 0.2).extrude(PCB_T)
    pcb = pcb.edges("|Z").fillet(CI_R - 0.1)
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
    print(f"height above the stand-on surface: {Z_TOP + LID_T:.1f} mm (lid top), cells end at z = {CELL_TOP:.1f}")


if __name__ == "__main__":
    main()
