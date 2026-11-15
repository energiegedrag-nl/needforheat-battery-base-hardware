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
* Three AAA cells in series, 11.5 mm apart, their axes 7.0 mm above the PCB, between MYOUNG contact plates that stand
  on the PCB (option A in docs/images/sketch-aaa-contacts.png): one bridge (MY-AAA-5214), two + plates (MY-AAA-15-J)
  and two − springs (MY-AAA-16-J); the second link between cells is a PCB track.
* A cradle (separate print) on the PCB: end ribs behind the contact plates, which pass the spring force on to the
  tray's short walls, and two saddles that hold the cells 1.75 mm above the PCB, so the electronics fit on the PCB's
  top side under the cells (parts up to 1.45 mm tall). The PCB's keep-outs go to enclosure/pcb_constraints.json.
* A sliding lid, like a remote control's battery door. It slides out towards the bottom edge (the edge that faces
  down when the CoreInk hangs or stands) and clicks shut: a flexible tab in the lid carries a bump that drops into a
  dimple in the top of the bottom wall. The lid's long edges run in grooves in the long walls and the top wall.
  The lid ends in a cap of the full outline width that forms the top of the bottom wall and its two corners.
  Turned round, that cap leads and is wider than the opening between the long walls: it stops at first touch, so
  the lid fits one way only.
* The polarity of each cell is shown where the user looks while inserting the cells: on the PCB silkscreen under
  each cell, and the spring is always the minus end. The lid's outside only shows "3x AAA" and an
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
# The bus header: a plain 2x8 male pin header, pins down (the BatteryBASE ends the stack, so no socket on top, unlike
# the P1-BASE's stacking J1). Through-hole: the PCB-side tails stick out on the top side, under cell 3.
HDR_TAIL = 1.4  # tail above the PCB top: standard 2.5 / 6.0 / 3.0 header on a 1.6 mm board (VERIFY with the part)
HDR_FILLET = 0.5  # solder fillet around each tail, Ø1.7
AAA_D, AAA_L = 10.5, 44.5
AAA_L_MIN = 43.5  # shortest AAA cell to still make contact (IEC LR03: 43.3 to 44.5; VERIFY with real cells)
Z_PCB = GAP + PCB_T  # PCB top

# --- cell contacts (option A, docs/images/sketch-aaa-contacts.png): MYOUNG plates standing on the PCB ---------
# Series chain: − terminal (cell 1, bottom) → cell 1 → + top → bridge → − top of cell 2 → cell 2 → + bottom →
# PCB track → − bottom of cell 3 → cell 3 → + terminal (cell 3, top). Only one bridge: the second one would have to
# be the mirror image of the MY-AAA-5214 (three cells), which is not in the catalogue.
# MY-AAA-5214 (C5371791) bridge: 21 x 11 plate, T 0.5, + button and − spring 11.5 apart, centres 7.0 above the plate's
#   lower edge; two tabs 4.5 x 1.5 below it, in slots in the PCB.
# MY-AAA-15-J (C51889749) + plate and MY-AAA-16-J (C51889750) − spring: 9.0 x 8.8 plate, T 0.3, contact centred,
#   one 4.0 mm wide tab (VERIFY its shape and length: the drawing shows it bent 90 deg; the EasyEDA footprint is a
#   4.7 x 1.1 slot). They stand 2.6 mm above the PCB so that their centre meets the cell axis.
# Spring free lengths: 5214 7.5 ± 0.8, 16-J 10.5 ± 1.
CELL_PITCH = 11.5  # = the bridge's button-to-spring pitch
CELL_X = [CI_W / 2 - CELL_PITCH, CI_W / 2, CI_W / 2 + CELL_PITCH]
PLUS_TOP = [True, False, True]  # where each cell's + end is (top = HAT edge)
CONTACT_Z = 7.0  # cell axis above the PCB top = centre of the bridge's button and spring
CELL_LIFT = CONTACT_Z - AAA_D / 2  # 1.75 mm: room under the cells for the electronics on the PCB's top side
AXIS_Z = Z_PCB + CONTACT_Z
CELL_TOP = AXIS_Z + AAA_D / 2
PART_H = CELL_LIFT - 0.3  # tallest part on the PCB under a cell
BRIDGE_W, BRIDGE_H, BRIDGE_TAB = 21.0, 11.0, 1.5
SINGLE_W, SINGLE_H = 9.0, 8.8
PLATE_T = 0.5  # 5214 is 0.5 thick, 15-J/16-J 0.3: the pocket is made for 0.5
BTN_H = 0.8  # + button height in front of its plate (5214: 1.3 overall - 0.5 plate; 15-J: 1.43 - 0.3 ≈ 1.1, VERIFY)

# --- cradle: separate printed insert on the PCB ----------------------------------------------------------------
# End ribs that back the contact plates (the spring force goes through them into the tray's short walls) and two
# saddle bars that hold the cells CELL_LIFT above the PCB and apart. It drops in on top of the PCB (saddles fixed
# to the tray walls would block the PCB going in from above) and the lid keeps it down.
CR_CLR = 0.15  # cradle to the tray walls
RIB_T = 1.5  # end rib thickness: sets the spring compression
Y_RIB = WALL + CR_CLR + RIB_T  # inner face of the top rib = back of the top plates
Y_FACE = [Y_RIB + PLATE_T, CI_H - Y_RIB - PLATE_T]  # contact faces of the plates, top and bottom
SPRING_LEN = Y_FACE[1] - Y_FACE[0] - BTN_H - AAA_L  # compressed spring length with a full-length cell
assert 2.8 <= SPRING_LEN and SPRING_LEN + (AAA_L - AAA_L_MIN) <= 5.0, f"spring {SPRING_LEN:.1f} mm"
SADDLE_Y = [16.0, 40.0]  # saddle bars (2 mm wide): keep-out strips on the PCB
SADDLE_W = 2.0
RAIL_W = 1.0  # side rails along the long walls tie the ribs and saddles together

# --- sliding lid -------------------------------------------------------------------------------------------
LID_T = 2.0
Z_TOP = CELL_TOP + 0.5  # lid underside: flat, 0.5 mm above the cells; the lid stops them from jumping out of the
# saddles. No ribs under the lid: they would hit the bottom wall when the lid slides out.
RIB_TOP = Z_PCB + BRIDGE_H + 0.5  # cradle end ribs: just above the bridge plate, well under the lid and its bump
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


def cell_y0(i, length=AAA_L):
    """Top end of cell i: its + button end rests on a + contact, the spring takes up the rest."""
    return Y_FACE[0] + BTN_H if PLUS_TOP[i] else Y_FACE[1] - BTN_H - length


def contact_list():
    """The five contacts: (kind, end, x centre, width, plate bottom above the PCB, [(x, polarity), ...])."""
    top, bot = [], []
    top.append(("bridge MY-AAA-5214", "top", (CELL_X[0] + CELL_X[1]) / 2, BRIDGE_W, 0.0,
                [(CELL_X[0], "+"), (CELL_X[1], "-")]))
    s0 = CONTACT_Z - SINGLE_H / 2
    top.append(("+ terminal MY-AAA-15-J", "top", CELL_X[2], SINGLE_W, s0, [(CELL_X[2], "+")]))
    bot.append(("- terminal MY-AAA-16-J", "bottom", CELL_X[0], SINGLE_W, s0, [(CELL_X[0], "-")]))
    bot.append(("+ plate MY-AAA-15-J", "bottom", CELL_X[1], SINGLE_W, s0, [(CELL_X[1], "+")]))
    bot.append(("- spring MY-AAA-16-J", "bottom", CELL_X[2], SINGLE_W, s0, [(CELL_X[2], "-")]))
    # the chain must alternate: every cell has its + where PLUS_TOP says
    for name, end, xc, w, z0, pts in top + bot:
        for x, pol in pts:
            i = CELL_X.index(x)
            assert (pol == "+") == (PLUS_TOP[i] == (end == "top")), (name, x)
    return top + bot


def contacts():
    """Placeholders: plates (0.5 thick), + buttons (BTN_H) and − springs compressed to SPRING_LEN (Ø5)."""
    out = None
    for name, end, xc, w, z0, pts in contact_list():
        h = BRIDGE_H if name.startswith("bridge") else SINGLE_H
        if end == "top":
            plate = box(xc - w / 2, xc + w / 2, Y_RIB, Y_RIB + PLATE_T, Z_PCB + z0, Z_PCB + z0 + h)
        else:
            plate = box(xc - w / 2, xc + w / 2, CI_H - Y_RIB - PLATE_T, CI_H - Y_RIB, Z_PCB + z0, Z_PCB + z0 + h)
        out = plate if out is None else out.union(plate)
        s = 1 if end == "top" else -1
        yf = Y_FACE[0] if end == "top" else Y_FACE[1]
        for x, pol in pts:
            i = CELL_X.index(x)
            ln = BTN_H if pol == "+" else (cell_y0(i) - yf if end == "top" else yf - cell_y0(i) - AAA_L)
            out = out.union(cq.Workplane("XY").add(cq.Solid.makeCylinder(
                2.0 if pol == "+" else 2.5, ln, cq.Vector(x, -yf, AXIS_Z), cq.Vector(0, -s, 0))))
    return out


def cradle():
    """Printed insert on the PCB: end ribs behind the contact plates, saddles under the cells, side rails."""
    inside = slab(CI_W, CI_H, CI_R, Z_PCB, RIB_TOP, -WALL - CR_CLR)
    x0, x1 = WALL + CR_CLR, CI_W - WALL - CR_CLR
    body = inside.intersect(box(x0 - 1, x1 + 1, 0, Y_RIB, Z_PCB, RIB_TOP)).union(
        inside.intersect(box(x0 - 1, x1 + 1, CI_H - Y_RIB, CI_H, Z_PCB, RIB_TOP)))
    for y in SADDLE_Y:
        body = body.union(box(x0, x1, y - SADDLE_W / 2, y + SADDLE_W / 2, Z_PCB, AXIS_Z))
    # notch over the bus header's tails and solder fillets (the saddle at y = 40 crosses it)
    body = body.cut(box(BUS[0] - BUS_W / 2 - 0.6, BUS[0] + BUS_W / 2 + 0.6, BUS[1] - BUS_H / 2 - 0.6,
                        BUS[1] + BUS_H / 2 + 0.6, Z_PCB - 0.1, Z_PCB + HDR_TAIL + 0.4))
    for xa, xb in ((x0, x0 + RAIL_W), (x1 - RAIL_W, x1)):
        body = body.union(box(xa, xb, Y_RIB - 0.5, CI_H - Y_RIB + 0.5, Z_PCB, Z_PCB + 4.0))
    for x in CELL_X:  # cradles for the cells, between the end ribs only (the ribs back the plates over their full face)
        body = body.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(
            AAA_D / 2 + 0.15, CI_H - 2 * Y_RIB, cq.Vector(x, -Y_RIB, AXIS_Z), cq.Vector(0, -1, 0))))
    return body


def fit_parts():
    """Placeholders for the fit check: PCB, cells and the header (plastic + pins)."""
    pcb = (cq.Workplane("XY").workplane(offset=GAP).center(*P(CI_W / 2, CI_H / 2))
           .rect(CI_W - 2 * INSET, CI_H - 2 * INSET).extrude(PCB_T).edges("|Z").fillet(CI_R - INSET + 0.5))
    for (x, y) in PEGS:
        pcb = pcb.cut(cq.Workplane("XY").workplane(offset=GAP - 0.1).center(*P(x, y)).circle(1.1).extrude(PCB_T + 0.2))
    cells = None
    for i, x in enumerate(CELL_X):
        c = cq.Workplane("XY").add(cq.Solid.makeCylinder(
            AAA_D / 2, AAA_L, cq.Vector(x, -cell_y0(i), AXIS_Z), cq.Vector(0, -1, 0)))
        cells = c if cells is None else cells.union(c)
    hdr = cq.Workplane("XY").center(*P(*BUS)).rect(BUS_W, BUS_H).extrude(GAP)
    pts = [(BUS[0] + (c - 0.5) * 2.54, BUS[1] + (r - 3.5) * 2.54) for c in range(2) for r in range(8)]
    pins = (cq.Workplane("XY").workplane(offset=Z_PCB + HDR_TAIL).pushPoints([P(*p) for p in pts]).rect(0.64, 0.64)
            .extrude(-(Z_PCB + HDR_TAIL + HDR_PIN)))
    fillets = (cq.Workplane("XY").workplane(offset=Z_PCB).pushPoints([P(*p) for p in pts]).circle(0.85)
               .extrude(HDR_FILLET))
    pins = pins.union(fillets)
    return pcb, cells, hdr.union(pins)


def pcb_constraints():
    """What the PCB design must respect, in board coordinates (mm from the CoreInk's top-left corner, y down);
    written to enclosure/pcb_constraints.json for the PCB generator."""
    pcb_x0, pcb_y0 = INSET, INSET
    x0, x1 = WALL + CR_CLR, CI_W - WALL - CR_CLR
    keepout = [dict(what="cradle rib (top)", x=[x0, x1], y=[INSET, Y_RIB]),
               dict(what="cradle rib (bottom)", x=[x0, x1], y=[CI_H - Y_RIB, CI_H - INSET])]
    keepout += [dict(what="cradle saddle", x=[x0, x1], y=[y - SADDLE_W / 2, y + SADDLE_W / 2]) for y in SADDLE_Y]
    keepout += [dict(what="bus header (THT, tails and fillets on the top side)", x=[BUS[0] - BUS_W / 2, BUS[0] + BUS_W / 2],
                     y=[BUS[1] - BUS_H / 2, BUS[1] + BUS_H / 2])]
    keepout += [dict(what="cradle side rail", x=list(xr), y=[Y_RIB - 0.5, CI_H - Y_RIB + 0.5])
                for xr in ((x0, x0 + RAIL_W), (x1 - RAIL_W, x1))]
    cons = []
    for name, end, xc, w, z0, pts in contact_list():
        yp = Y_RIB + PLATE_T / 2 if end == "top" else CI_H - Y_RIB - PLATE_T / 2
        cons.append(dict(part=name, end=end, x=xc, y_plate_centre=round(yp, 3), width=w,
                         contacts=[dict(x=x, polarity=p) for x, p in pts]))
    return dict(frame="board: x right, y down from the CoreInk outline's top-left corner; the PCB is "
                      f"{CI_W - 2 * INSET:.1f} x {CI_H - 2 * INSET:.1f} from ({pcb_x0}, {pcb_y0})",
                top_side_max_part_height_under_cells=round(PART_H, 2), keepout_top=keepout, contacts=cons,
                cells=[dict(x=x, y_top=round(cell_y0(i), 2), plus_end="top" if PLUS_TOP[i] else "bottom")
                       for i, x in enumerate(CELL_X)], pegs=PEGS, bus_header_centre=BUS)


def main():
    os.makedirs(OUT, exist_ok=True)
    import json
    with open(os.path.join(HERE, "pcb_constraints.json"), "w", encoding="utf8") as f:
        json.dump(pcb_constraints(), f, indent=1)
    print("wrote pcb_constraints.json")
    k, l, cr = kuip(), lid(), cradle()
    for name, part in (("battery-base-kuip", k), ("battery-base-lid", l), ("battery-base-cradle", cr)):
        cq.exporters.export(part, os.path.join(OUT, name + ".step"))
        cq.exporters.export(part, os.path.join(OUT, name + ".stl"), tolerance=0.02, angularTolerance=0.1)
        print("wrote", name)
    pcb, cells, hdr = fit_parts()
    asm = cq.Assembly(name="battery-base-fit")
    asm.add(k, name="tray", color=cq.Color(0.9, 0.9, 0.9))
    asm.add(l, name="lid", color=cq.Color(0.3, 0.3, 0.3))
    asm.add(pcb, name="pcb", color=cq.Color(0.1, 0.4, 0.1))
    asm.add(cr, name="cradle", color=cq.Color(0.6, 0.6, 0.65))
    asm.add(contacts(), name="contacts", color=cq.Color(0.75, 0.75, 0.8))
    asm.add(cells, name="cells", color=cq.Color(0.8, 0.5, 0.1))
    asm.add(hdr, name="header", color=cq.Color(0.1, 0.1, 0.1))
    asm.save(os.path.join(OUT, "battery-base-fit.step"), exportType="STEP")
    print("wrote battery-base-fit")
    print(f"thickness for shipping (lid top to post tips): {SHIP_T:.1f} mm (max. {SHIP_MAX} mm)")
    print(f"height above the stand-on surface: {Z_LID:.1f} mm (lid top), cells end at z = {CELL_TOP:.1f}")
    print(f"cells: pitch {CELL_PITCH} mm, axis {CONTACT_Z} mm above the PCB, {CELL_LIFT:.2f} mm lift "
          f"(parts under the cells up to {PART_H:.2f} mm tall)")
    print(f"springs compressed to {SPRING_LEN:.1f} mm ({SPRING_LEN + AAA_L - AAA_L_MIN:.1f} mm with a "
          f"{AAA_L_MIN} mm cell)")


if __name__ == "__main__":
    main()
