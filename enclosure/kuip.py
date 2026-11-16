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
  The electronics sit on the PCB's underside, in the 2.5 mm under it (the side that faces the CoreInk or the
  P1-BASE), so a single-sided SMD assembly does; the 2x8 bus header (THT, pins down) is there too.
* Three AAA cells in series on the PCB's back side, packed to the left (away from the bus header's tails, which the
  cells' curve clears), between six MYOUNG MY-AAA-01 leaf contacts: a foot under each cell's end (the cell lies on
  it), two pins through the PCB soldered by JLCPCB (THT), a leaf with a dimple against the cell's end. Linked by PCB
  tracks. The left long wall is thinner where cell 1 bulges.
* A cradle (separate print) on the PCB: end ribs behind the leaves (a stop for a leaf pushed too far), two low bars
  between the cells, and three stops right of cell 3 that keep it off the bus header's tails.
  The PCB's keep-outs go to enclosure/pcb_constraints.json.
* A sliding lid, like a remote control's battery door. It slides in from the top edge (HAT side) and stops against
  the bottom wall, so it stays in when the CoreInk hangs or stands, even without its click; a flexible tab at the
  top end clicks a bump into a dimple in the top of the top wall. The lid's long edges run in grooves in the long
  walls and the bottom wall. The lid's top end is a cap of the full outline width that forms the top of the top wall
  and its two corners: turned round, that cap leads and is wider than the opening between the long walls, so it
  stops at first touch and the lid fits one way only.
* The polarity of each cell is shown where the user looks while inserting the cells: on the PCB silkscreen under
  each cell (the leaf contacts are the same at both ends). The lid's outside only shows "3x AAA" and arrows at the grip
  tab that point the way the lid slides out.
The BatteryBASE is always the last module of a stack (its cells must stay reachable): the lid has no LEGO holes
and no bus socket.

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
# Ø2.2 NPTH in the PCB on the corner blocks, at the same places as on the P1-BASE v3; the top-left corner keys the PCB
PEGS = [(36, 4), (4, 52), (36, 52)]
HDR_PIN = 6.0  # header pins below the plastic, into the socket below
# The bus header: a plain 2x8 male pin header, pins down (the BatteryBASE ends the stack, so no socket on top, unlike
# the P1-BASE's stacking J1), inserted from the underside. Through-hole: its tails stick out on the back side,
# under cell 3, and set how low the cells can lie (CELL_LIFT). Part: XKB X6521WV-2x08H-C60D30 (C706898): 2.5 mm
# plastic, 6.0 mm pins, 3.0 mm PCB tail. No shorter tail is in stock at JLCPCB, and the SMD version does not fit:
# its feet reach 4.2 mm out from the centre line, past the PCB edge next to the tray wall.
HDR_TAIL = 3.0 - PCB_T  # 1.4 mm proud of the PCB's back side
HDR_FILLET = 0.5  # solder fillet around each tail, Ø1.7
HDR_PIN_W = 0.64  # square pins
BOTTOM_PART_H = GAP - 0.3  # tallest part on the PCB's underside (it faces the CoreInk's back or the P1-BASE's lid)
AAA_D, AAA_L = 10.5, 44.5  # nominal (IEC LR03: diameter 10.5 max, length 44.5 max)
# cells as they come (labels, NiMH, manufacturing): the enclosure must take all of these (VERIFY with real cells)
AAA_D_MIN, AAA_D_MAX = 10.1, 10.7
AAA_L_MIN, AAA_L_MAX = 43.5, 45.0
Z_PCB = GAP + PCB_T  # PCB top

# --- cell contacts: six MYOUNG MY-AAA-01 leaf contacts (C964855), soldered by JLCPCB (THT, from the far side) -----
# Series chain: - terminal (cell 1, bottom) -> cell 1 -> + top -> PCB -> - top of cell 2 -> cell 2 -> + bottom ->
# PCB -> - bottom of cell 3 -> cell 3 -> + terminal (cell 3, top).
# MYOUNG drawing MY-CP-0095 (TER-151, 2017-07-19), one part for both ends. Dimensions below are measured from the
# vendor's 3D model (LCSC/EasyEDA, see tools/import_leaf_model.py), which matches the drawing: a foot 15.57 long and
# 6.35 wide, raised 0.25 off the PCB (its top 0.50 above it) and standing on two narrow ends: the inner end (5.08
# wide) and a tab behind the leaf (2.33 wide, 2.66 beyond the outer pin). Two flat pins (1.0 x 0.25, 1.5 long) 10.25
# apart go into the PCB. Next to the outer pin a leaf rises to 10.1 above the PCB, leaning in towards the cell, with
# a Ø2.5 dimple (0.88 proud) that touches the cell's end and gives way when the cell goes in. Free, the dimple's tip
# is 1.34 inside the outer pin. MYOUNG's (and Keystone 56's) layout for AAA: 42.4 mm between the outer pads' inner
# edges, which lie 1.3 inside the outer pins, so the outer pins are 45.0 apart and the free dimples about 42.3: each
# leaf gives way 0.6 to 1.3 mm. The cell lies on the two feet (CELL_LIFT). The part has no polarity: + and - are
# marked on the PCB under each cell.
# (Until 16 November 2026: MY-AAA-15-J/16-J plates in slots; their tab turned out to be bent 90 deg. Until the vendor
# model was measured the outer pins were 42.4 apart, which would have pressed each leaf back 1.9 to 2.6 mm.)
PLUS_TOP = [True, False, True]  # where each cell's + end is (top = HAT edge)
LEAF_PART = "MY-AAA-01"
FOOT_L, LEAF_W, FOOT_T = 15.57, 6.35, 0.50  # FOOT_T: top of the raised foot above the PCB
FTAB_W, FTAB_OUT, FTAB_T = 2.33, 2.66, 0.25  # the foot's tab behind the leaf: width, beyond the outer pin, height
PIN_PITCH, PIN_D, PIN_LEN = 10.25, 1.0, 1.5
PIN_OUT = 1.01  # outer pin to the leaf's inner face where it leaves the foot
LEAF_T = 0.20
LEAF_H = 9.64  # leaf above the foot's top
DIMPLE_Z = 5.51  # dimple centre above the foot's top (6.01 above the PCB)
DIMPLE_H = 0.88  # how far the dimple stands out of the leaf towards the cell
LEAF_LEAN = 1.47 * LEAF_H / DIMPLE_Z  # straight-leaf model: leans 1.47 in at the dimple (the real top bends back)
PAIR_PITCH = 42.4 + 2 * 1.3  # outer pin to outer pin of one cell (MYOUNG layout for AAA, see above)
LEAF_DEFL_MAX = 2.0  # how far a leaf may give way at the dimple (VERIFY with samples)
# pocket in the tray's corner blocks under a pin's solder joint (the PCB rests on the blocks): x, y, depth
PIN_POCKET = (3.0, 3.0, 0.8)
TAB_NOTCH_CLR = 0.3  # notch in a cradle rib around a contact's tab
# recess in a cradle rib behind each leaf's top, which swings back when a long cell presses the leaf (checked with
# the vendor model in check_leaf.py): depth, from this height above the PCB to the rib's top
LEAF_RECESS_D, LEAF_RECESS_Z = 0.4, 7.5
CELL_LIFT = FOOT_T  # the cells lie on the contacts' feet
Y_PIN_OUT = [CI_H / 2 - PAIR_PITCH / 2, CI_H / 2 + PAIR_PITCH / 2]  # outer pins, top and bottom end
Y_BEND = [Y_PIN_OUT[0] - PIN_OUT, Y_PIN_OUT[1] + PIN_OUT]  # where the leaves rise
_lean_dimple = LEAF_LEAN * DIMPLE_Z / LEAF_H
Y_FACE_FREE = [Y_BEND[0] + _lean_dimple + DIMPLE_H, Y_BEND[1] - _lean_dimple - DIMPLE_H]  # dimple tips, no cell
LEAF_DEFL = ((AAA_L_MIN - (Y_FACE_FREE[1] - Y_FACE_FREE[0])) / 2, (AAA_L_MAX - (Y_FACE_FREE[1] - Y_FACE_FREE[0])) / 2)
assert LEAF_DEFL[0] >= 0.2 and LEAF_DEFL[1] <= LEAF_DEFL_MAX, f"leaf deflection {LEAF_DEFL}"

# --- cells: lying on the contacts' feet, packed to the left, away from the bus header's tails ---------------------
# The cells rest on the feet of their contacts (CELL_LIFT above the PCB). The header's tails (1.4 mm proud) are under
# cell 3; the curve of the cell clears them once the inner pin row is far enough from the cell's axis. A stop in the
# cradle (right of cell 3) keeps cell 3 there; the long wall on the left is thinner where cell 1 bulges (WALL_THIN),
# so the three cells, with some play, fit between that wall and the stop.
HDR_CLR = 0.3  # any cell 3 (AAA_D_MIN to AAA_D_MAX, against the stop) above the header's tails
PIN_X_IN = BUS[0] - 2.54 / 2  # inner pin row, under cell 3


def cell_clear_x(r, clr):
    """Smallest distance from a cell's axis (cell CELL_LIFT above the PCB, radius r) to the edge of a tail that is
    HDR_TAIL + clr under the cell's surface."""
    h = HDR_TAIL - CELL_LIFT + clr
    return (r * r - (r - h) ** 2) ** 0.5


# cradle stop, right of cell 3: set by the cell that gets closest to the tails against it (a thin one)
# and by cell 3's contacts, which sit left of the header (FOOT_HDR_CLR below): a nominal cell 3 against the stop keeps
# its axis within DIMPLE_OFF of their dimples
FOOT_HDR_CLR = 0.8
DIMPLE_OFF = 0.75
X_STOP = min([PIN_X_IN - HDR_PIN_W / 2 - cell_clear_x(d / 2, HDR_CLR) + d / 2 for d in (AAA_D_MIN, AAA_D, AAA_D_MAX)]
             + [PIN_X_IN - 0.85 - FOOT_HDR_CLR - LEAF_W / 2 + DIMPLE_OFF + AAA_D / 2])
for _d in (AAA_D_MIN, AAA_D, AAA_D_MAX):  # any cell against the stop: tails' clearance
    _r = _d / 2
    _dx = PIN_X_IN - HDR_PIN_W / 2 - (X_STOP - _r)
    assert CELL_LIFT + _r - (_r * _r - _dx * _dx) ** 0.5 - HDR_TAIL >= HDR_CLR - 1e-6, f"cell {_d} on the header's tails"
WALL_THIN = 1.0  # long wall on the left where the cells bulge (MJF PA12: about 0.8 minimum, VERIFY)
X_LEFT = WALL_THIN  # inner face of the thin part
CELL_FREE = X_STOP - X_LEFT - 3 * AAA_D  # play left for three nominal cells
assert X_STOP - X_LEFT - 3 * AAA_D_MAX >= 0.2, "three thick cells do not fit"
CELL_GAP = CELL_FREE / 3  # nominal: the play spread over wall-1, 1-2 and 2-3
CELL_PITCH = AAA_D + CELL_GAP
CELL_X = [X_LEFT + CELL_GAP + AAA_D / 2 + k * CELL_PITCH for k in range(3)]  # cell 3 ends against the stop
CONTACT_Z = CELL_LIFT + AAA_D / 2  # cell axis above the PCB top
AXIS_Z = Z_PCB + CONTACT_Z
CELL_TOP = AXIS_Z + AAA_D / 2
CELL_TOP_MAX = Z_PCB + CELL_LIFT + AAA_D_MAX
CONTACT_C = FOOT_T + DIMPLE_Z  # dimple centre above the PCB
CONTACT_DROP = CONTACT_Z - CONTACT_C  # dimple centre below the cell axis (negative: above it)
# contact x: under the cell's axis, except cell 3, whose bottom foot lies next to the bus header's inner pin row (its
# tails and solder fillets stick out on this side): that foot keeps FOOT_HDR_CLR from the fillets, so both contacts
# of cell 3 move left. The dimple (Ø2.5) still meets the + nub (Ø3.8 min. 2.0) and the flat - end off centre.
CONTACT_X = [CELL_X[0], CELL_X[1], min(CELL_X[2], PIN_X_IN - 0.85 - FOOT_HDR_CLR - LEAF_W / 2)]
assert all(abs(cx - x) <= 1.0 for cx, x in zip(CONTACT_X, CELL_X)), "dimple too far off the cell's axis"
assert (CELL_LIFT + AAA_D / 2 - CONTACT_C) ** 2 + max(abs(cx - x) for cx, x in zip(CONTACT_X, CELL_X)) ** 2 <= 1.25 ** 2,     "dimple off the + nub"

# --- cradle: separate printed insert on the PCB ----------------------------------------------------------------
# End ribs behind the contacts' leaves: a stop for a leaf pushed too far while a cell goes in (the leaves carry the
# cells' end force through their pins into the PCB), stops right of cell 3, a side rail and two low bars. It drops
# in on top of the PCB and the lid keeps it down; the ribs reach up to just under the lid.
CR_CLR = 0.15  # cradle to the tray walls
RIB_T = 1.2  # end rib thickness
Y_RIB = WALL + CR_CLR + RIB_T  # inner face of the top rib
# a leaf pressed by the longest cell (its top swings out about the bend) stays this far off the rib
LEAF_RIB_CLR = Y_BEND[0] - LEAF_T - (LEAF_DEFL[1] - _lean_dimple) * LEAF_H / DIMPLE_Z - Y_RIB
assert LEAF_RIB_CLR >= 0.5, f"leaf {LEAF_RIB_CLR:.2f} mm from the rib"
assert Y_BEND[0] - Y_RIB >= 1.0, "no room behind the leaf's bend"
# cradle stops right of cell 3 (2 mm wide, keep-out strips on the PCB), clear of the bus header's pins: two above
# them and one just below them. No saddles or arcs under or between the cells: they lie on their feet and can roll
# left into the play (CELL_FREE) while they go in.
SADDLE_Y = [14.0, 25.5, 48.0]
SADDLE_W = 2.0
STOP_H = AAA_D_MAX / 2 + 1.5  # above the PCB: past the equator of the thickest cell
HDR_Y = (BUS[1] - 3.5 * 2.54 - 0.85, BUS[1] + 3.5 * 2.54 + 0.85)  # first and last pin, solder fillets included
assert all(y + SADDLE_W / 2 + 0.3 < HDR_Y[0] or y - SADDLE_W / 2 - 0.3 > HDR_Y[1] for y in SADDLE_Y), "stop on the header"
# one side rail, along the right long wall, ties the ribs and stops together. No rail on the left: room there is for
# cell 1's bulge.
RAIL_W, RAIL_H = 1.5, 4.0
# two low bars on the PCB between the cells (1-2 and 2-3), from rib to rib: they tie the end ribs together on the
# left part of the cradle, where a rail along the wall does not fit. They run between the contacts' feet and lie in
# the wedge under two round cells, so they are not in the way when a cell goes in. A cell on its feet, rolled against
# a bar, must still lie flat: checked for the cell sizes and the cells pushed against the wall or the stop.
BAR_W, BAR_H = 1.4, 2.0
BAR_X = [(CELL_X[k] + CELL_X[k + 1]) / 2 for k in range(2)]
BAR_FOOT_CLR = 0.5  # bar to the edge of a contact's foot or leaf
for _k, _xb in enumerate(BAR_X):
    assert _xb - BAR_W / 2 - (CONTACT_X[_k] + LEAF_W / 2) >= BAR_FOOT_CLR - 1e-6, "bar on a contact"
    assert CONTACT_X[_k + 1] - LEAF_W / 2 - (_xb + BAR_W / 2) >= BAR_FOOT_CLR - 1e-6, "bar on a contact"


def _bar_reach(r):
    """Horizontal distance from a cell's axis to the top corner of a bar it touches (cell CELL_LIFT above the PCB)."""
    return (r * r - (r - (BAR_H - CELL_LIFT)) ** 2) ** 0.5


for _d in (AAA_D_MIN, AAA_D, AAA_D_MAX):
    _r = _d / 2
    # left of bar 1: cell 1 against the wall; right of bar 1: cells 2 and 3 against the stop
    assert BAR_X[0] - BAR_W / 2 >= X_LEFT + _r + _bar_reach(_r) - 1e-6, f"cell {_d}: no room left of bar 1"
    assert BAR_X[0] + BAR_W / 2 <= X_STOP - 3 * _r - _bar_reach(_r) + 1e-6, f"cell {_d}: no room right of bar 1"
    assert BAR_X[1] - BAR_W / 2 >= X_LEFT + 3 * _r + _bar_reach(_r) - 1e-6, f"cell {_d}: no room left of bar 2"
    assert BAR_X[1] + BAR_W / 2 <= X_STOP - _r - _bar_reach(_r) + 1e-6, f"cell {_d}: no room right of bar 2"
# key: a lip on the top rib, off centre, in a vertical groove in the tray's top wall (open at the top, where the
# cradle drops in). Turned 180 deg about any axis, the lip lands where there is no groove and the cradle does not go
# in. Clear of the click dimple in the middle of the top wall.
KEY_X, KEY_W, KEY_D = 30.0, 3.0, 0.8  # centre, width, how far the lip sticks out of the rib
KEY_CLR = 0.15
KEY_Y0 = WALL + CR_CLR - KEY_D - KEY_CLR  # groove floor in the top wall
assert KEY_Y0 >= 0.8 - 1e-6, "top wall too thin behind the key groove"

# --- sliding lid -------------------------------------------------------------------------------------------
LID_T = 2.0
Z_TOP = CELL_TOP_MAX + 0.5  # lid underside: flat, 0.5 mm above the thickest cells; it keeps them on the PCB.
# No ribs under the lid: they would hit the bottom wall when the lid slides out.
# thin part of the left long wall: where cell 1 can bulge into it, from well under the equator of a thick cell up to
# 1 mm under the lid's groove (a ledge stays under the groove); over the cells' whole length between the end ribs,
# so they can slide into the spring
THIN_Z = (Z_PCB + AAA_D_MAX / 2 - 3.3, Z_TOP - 1.0)
# Cradle end ribs reach up to just under the lid: the cradle is the clamp between the lid and the PCB. Pushing the
# module onto the CoreInk: tray -> grooves -> lid tongue -> lid -> ribs -> PCB -> header pins (and pushing on the lid
# goes straight lid -> ribs). Pulling it off: tray -> corner blocks under the PCB -> header pins. Play in the chain:
# groove 0.2 + RIB_GAP.
RIB_GAP = 0.1  # rib top to lid underside: the lid slides over the ribs
RIB_TOP = Z_TOP - RIB_GAP
Z_LID = Z_TOP + LID_T  # outer face
GR_D = 0.7  # groove depth into the long walls and the top wall (the lid's tongue runs in it)
TONGUE_H = 0.8  # tongue: the lower part of the lid's edge
GR_H = TONGUE_H + 0.2  # groove height (0.2 mm vertical play)
SL_CLR = 0.2  # sideways play of the lid in the walls and grooves, per side (MJF PA12, VERIFY on the print)
CAP_GAP = 0.1  # seam between the cap and the ends of the long walls
# The lid and its slot are drawn with the open end at the bottom and then mirrored top <-> bottom (lid_mirror), so
# the lid slides in from the top edge. LID_OUT: CadQuery y direction in which the lid slides out (+1 = up).
LID_OUT = +1
# click: tab in the lid, open towards the open end, thinned from the outside so it flexes (and as a thumb rest)
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


def lid_mirror(wp):
    """Mirror top <-> bottom: the lid and its slot are drawn with the open end at the bottom edge."""
    return wp.mirror(mirrorPlane="XZ", basePointVector=(0, -CI_H / 2, 0))


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
    for (x, y) in PEGS:
        body = body.union(cq.Workplane("XY").workplane(offset=GAP).center(*P(x, y)).circle(PEG_D / 2)
                          .extrude(PCB_T - 0.2))
    # thin part of the left long wall, where cell 1 bulges
    body = body.cut(box(X_LEFT, WALL + 0.01, Y_RIB, CI_H - Y_RIB, THIN_Z[0], THIN_Z[1]))
    # key groove for the cradle's lip, in the top wall, open at the top
    assert abs(KEY_X - CI_W / 2) > TAB_W / 2 + KEY_W, "key groove on the click dimple"
    kx = KEY_W / 2 + KEY_CLR
    body = body.cut(box(KEY_X - kx, KEY_X + kx, KEY_Y0, WALL + 0.01, Z_PCB, Z_LID + 1))
    # contact pins over a corner block: a pocket for the solder joint on the PCB's underside
    for xc, yp in pocket_pins():
        body = body.cut(box(xc - PIN_POCKET[0] / 2, xc + PIN_POCKET[0] / 2, yp - PIN_POCKET[1] / 2,
                            yp + PIN_POCKET[1] / 2, GAP - PIN_POCKET[2], GAP + 0.01))
    # the lid's slot, drawn with the open end at the bottom and mirrored: square ends at the open end (no inner corner
    # radius in the way of the lid), the groove for the lid's tongue, the cap's place on the end wall and its
    # corners, the dimple for the click bump and a lead-in where the bump climbs on
    cuts = channel(-WALL, Z_TOP, Z_LID + 1, CI_H + 1)
    cuts = cuts.union(channel(-WALL + GR_D, Z_TOP, Z_TOP + GR_H, CI_H + 1))
    cuts = cuts.union(box(-1, CI_W + 1, CI_H - WALL, CI_H + 1, Z_TOP, Z_LID + 1))
    cuts = cuts.union(ridge(DET_Y, CI_W / 2 - TAB_W / 2 + 0.5, CI_W / 2 + TAB_W / 2 - 0.5, Z_TOP + 0.01,
                            DET_H + 0.15, DET_B + 0.3))
    cuts = cuts.union(ridge(CI_H, CI_W / 2 - TAB_W / 2 + 0.5, CI_W / 2 + TAB_W / 2 - 0.5, Z_TOP + 0.01, 0.4, 0.8))
    body = body.cut(lid_mirror(cuts))
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
    assert Z_TOP - DET_H > CELL_TOP_MAX, "the click bump would rub over the middle cell"  # it slides over it
    # outside: arrow next to the tab pointing the way the lid slides out, and "3x AAA"
    for sx in (tx0 - 5.0, tx1 + 5.0):
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_LID - 0.4).center(*P(sx, CI_H - 6.0))
                        .transformed(rotate=(0, 0, -90)).polygon(3, 4.0).extrude(0.5))
    body = lid_mirror(body)  # open end at the top edge; the text goes on after this, so it reads the right way
    try:
        txt = (cq.Workplane("XY").workplane(offset=Z_LID - 0.4).center(*P(CI_W / 2, CI_H - 18.0))
               .text("3x AAA", 5.0, 0.5, combine=False, halign="center", valign="center"))
        body = body.cut(txt.val().fuse())  # fuse the glyphs first: a cut with the raw text compound goes wrong
    except Exception as e:  # no font available: leave the text off
        print("no text on the lid:", e)
    return body


def cell_y0(i, length=AAA_L):
    """Top end of cell i: the two leaves centre it between them."""
    return CI_H / 2 - length / 2


def contact_list():
    """The six contacts: (end, x of the pins, polarity, y of the outer pin, y of the inner pin)."""
    out = []
    for i, x in enumerate(CONTACT_X):
        for k, end in enumerate(("top", "bottom")):
            plus = PLUS_TOP[i] == (end == "top")
            yo = Y_PIN_OUT[k]
            out.append((end, x, "+" if plus else "-", yo, yo + PIN_PITCH if end == "top" else yo - PIN_PITCH))
    return out


def contact_pins():
    """(x, y) of all twelve contact pins."""
    return [(x, y) for _, x, _, yo, yi in contact_list() for y in (yo, yi)]


def _in_corner_block(x, y, margin):
    """Whether (x, y) lies on a corner block of the tray (as in kuip()), grown by margin."""
    for bx, by in LEGO_HOLES:
        x0, x1 = (0.0, bx + POST / 2) if bx < CI_W / 2 else (bx - POST / 2, CI_W)
        y0, y1 = (0.0, by + POST / 2) if by < CI_H / 2 else (by - POST / 2, CI_H)
        if x0 - margin < x < x1 + margin and y0 - margin < y < y1 + margin:
            return True
    return False


def pocket_pins():
    """Contact pins whose solder joint (under the PCB) lands on a corner block of the tray."""
    return [(x, y) for x, y in contact_pins() if _in_corner_block(x, y, PIN_POCKET[0] / 2)]


def leaf(end, xc, cell_end=None):
    """One MY-AAA-01: foot on the PCB, two pins through it, leaf with its dimple. With cell_end (board y of the cell's
    end) the leaf is drawn pressed back so that the dimple just touches it; without, in its free position."""
    k = 0 if end == "top" else 1
    s = 1 if end == "top" else -1  # towards the cell, in board y
    yb, yo = Y_BEND[k], Y_PIN_OUT[k]
    z0 = Z_PCB + FOOT_T
    yf = yo - s * FTAB_OUT + s * FOOT_L  # inner end of the foot
    foot = box(xc - LEAF_W / 2, xc + LEAF_W / 2, min(yb, yf), max(yb, yf), Z_PCB, z0)
    yt = yo - s * FTAB_OUT  # outer end of the tab
    foot = foot.union(box(xc - FTAB_W / 2, xc + FTAB_W / 2, min(yt, yb), max(yt, yb), Z_PCB, Z_PCB + FTAB_T))
    lean = _lean_dimple if cell_end is None else s * (cell_end - yb) - DIMPLE_H - 0.05
    top = lean * LEAF_H / DIMPLE_Z  # how far the leaf's top leans towards the cell
    pts = [(-yb, z0 - FOOT_T), (-(yb - s * LEAF_T), z0 - FOOT_T), (-(yb + s * (top - LEAF_T)), z0 + LEAF_H),
           (-(yb + s * top), z0 + LEAF_H)]
    blade = cq.Workplane("YZ").workplane(offset=xc - LEAF_W / 2).polyline(pts).close().extrude(LEAF_W)
    yd = yb + s * lean  # dimple root on the leaf at DIMPLE_Z
    dimple = cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, DIMPLE_H, cq.Vector(xc, -yd, z0 + DIMPLE_Z),
                                                          cq.Vector(0, -s, 0)))
    part = foot.union(blade).union(dimple)
    for y in (yo, yo + s * PIN_PITCH):
        part = part.union(cq.Workplane("XY").workplane(offset=Z_PCB - PIN_LEN).center(*P(xc, y)).circle(PIN_D / 2)
                          .extrude(PIN_LEN))
        # solder joint under the PCB
        part = part.union(cq.Workplane("XY").workplane(offset=GAP - 0.4).center(*P(xc, y)).circle(1.0).extrude(0.4))
    return part


def contacts():
    """The six leaf contacts, pressed back by nominal cells."""
    out = None
    for i, (end, x, pol, yo, yi) in enumerate(contact_list()):
        cell = i // 2
        ce = cell_y0(cell) if end == "top" else cell_y0(cell) + AAA_L
        p = leaf(end, x, ce)
        out = p if out is None else out.union(p)
    return out


def cradle():
    """Printed insert on the PCB: end ribs behind the contact plates, stops right of cell 3, a side rail and two low
    bars between the cells."""
    inside = slab(CI_W, CI_H, CI_R, Z_PCB, RIB_TOP, -WALL - CR_CLR)
    x0, x1 = WALL + CR_CLR, CI_W - WALL - CR_CLR
    body = inside.intersect(box(x0 - 1, x1 + 1, 0, Y_RIB, Z_PCB, RIB_TOP)).union(
        inside.intersect(box(x0 - 1, x1 + 1, CI_H - Y_RIB, CI_H, Z_PCB, RIB_TOP)))
    for y in SADDLE_Y:
        body = body.union(box(X_STOP, x1, y - SADDLE_W / 2, y + SADDLE_W / 2, Z_PCB, Z_PCB + STOP_H))
    body = body.union(box(x1 - RAIL_W, x1, Y_RIB - 0.5, CI_H - Y_RIB + 0.5, Z_PCB, Z_PCB + RAIL_H))
    for xb in BAR_X:  # low bars between the cells, rib to rib
        body = body.union(box(xb - BAR_W / 2, xb + BAR_W / 2, Y_RIB - 0.5, CI_H - Y_RIB + 0.5, Z_PCB, Z_PCB + BAR_H))
    # key: lip on the top rib, into the groove in the top wall
    body = body.union(box(KEY_X - KEY_W / 2, KEY_X + KEY_W / 2, WALL + CR_CLR - KEY_D, WALL + CR_CLR + 0.01,
                          Z_PCB + 0.3, RIB_TOP))
    # recess in the end ribs behind each leaf's top
    for _, xc, _, yo, _ in contact_list():
        top = yo < CI_H / 2
        y0, y1 = (Y_RIB - LEAF_RECESS_D, Y_RIB + 0.01) if top else (CI_H - Y_RIB - 0.01, CI_H - Y_RIB + LEAF_RECESS_D)
        body = body.cut(box(xc - LEAF_W / 2 - 0.3, xc + LEAF_W / 2 + 0.3, y0, y1, Z_PCB + LEAF_RECESS_Z, RIB_TOP + 0.01))
    # notch in the end ribs over each contact's tab (it reaches under the rib)
    for _, xc, _, yo, _ in contact_list():
        s = 1 if yo < CI_H / 2 else -1
        yt = yo - s * FTAB_OUT
        if (yt < Y_RIB + TAB_NOTCH_CLR) if s > 0 else (yt > CI_H - Y_RIB - TAB_NOTCH_CLR):
            y0, y1 = (0, Y_RIB + 0.01) if s > 0 else (CI_H - Y_RIB - 0.01, CI_H)
            body = body.cut(box(xc - FTAB_W / 2 - TAB_NOTCH_CLR, xc + FTAB_W / 2 + TAB_NOTCH_CLR, y0, y1, Z_PCB - 0.01,
                                Z_PCB + FTAB_T + TAB_NOTCH_CLR))
    return body


def fit_parts():
    """Placeholders for the fit check: PCB, cells and the header (plastic + pins)."""
    pcb = (cq.Workplane("XY").workplane(offset=GAP).center(*P(CI_W / 2, CI_H / 2))
           .rect(CI_W - 2 * INSET, CI_H - 2 * INSET).extrude(PCB_T).edges("|Z").fillet(CI_R - INSET + 0.5))
    for (x, y) in PEGS:
        pcb = pcb.cut(cq.Workplane("XY").workplane(offset=GAP - 0.1).center(*P(x, y)).circle(1.1).extrude(PCB_T + 0.2))
    for xc, yp in contact_pins():  # the contacts' holes (Ø1.2 drill)
        pcb = pcb.cut(cq.Workplane("XY").workplane(offset=GAP - 0.1).center(*P(xc, yp)).circle(0.6)
                      .extrude(PCB_T + 0.2))
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
    written to enclosure/pcb_constraints.json for the PCB generator. "back" = the cell side (towards the lid),
    "underside" = the electronics side (towards the CoreInk or the P1-BASE)."""
    x0, x1 = WALL + CR_CLR, CI_W - WALL - CR_CLR
    back = [dict(what="cradle rib (top)", x=[x0, x1], y=[INSET, Y_RIB]),
            dict(what="cradle rib (bottom)", x=[x0, x1], y=[CI_H - Y_RIB, CI_H - INSET])]
    back += [dict(what="cradle stop (right of cell 3)", x=[X_STOP, x1], y=[y - SADDLE_W / 2, y + SADDLE_W / 2])
             for y in SADDLE_Y]
    back += [dict(what="cradle side rail", x=[x1 - RAIL_W, x1], y=[Y_RIB - 0.5, CI_H - Y_RIB + 0.5])]
    back += [dict(what="cradle bar between cells", x=[xb - BAR_W / 2, xb + BAR_W / 2], y=[Y_RIB - 0.5, CI_H - Y_RIB + 0.5])
             for xb in BAR_X]
    under = []
    for (x, y) in LEGO_HOLES:
        bx = (INSET, x + POST / 2) if x < CI_W / 2 else (x - POST / 2, CI_W - INSET)
        by = (INSET, y + POST / 2) if y < CI_H / 2 else (y - POST / 2, CI_H - INSET)
        under.append(dict(what="corner block of the tray (PCB rests on it)", x=list(bx), y=list(by)))
    under.append(dict(what="bus header body (2x8, 2.5 mm)", x=[BUS[0] - BUS_W / 2, BUS[0] + BUS_W / 2],
                      y=[BUS[1] - BUS_H / 2, BUS[1] + BUS_H / 2]))
    cons = []
    for end, xc, pol, yo, yi in contact_list():
        yb = Y_BEND[0 if end == "top" else 1]
        s = 1 if end == "top" else -1
        cons.append(dict(part=f"MYOUNG {LEAF_PART} leaf contact", end=end, polarity=pol, x=round(xc, 3),
                         y_pin_outer=round(yo, 3), y_pin_inner=round(yi, 3),
                         foot=dict(x=[round(xc - LEAF_W / 2, 3), round(xc + LEAF_W / 2, 3)],
                                   y=sorted([round(yo - s * FTAB_OUT, 3), round(yo - s * FTAB_OUT + s * FOOT_L, 3)])),
                         pins=f"2 x Ø{PIN_D} x {PIN_LEN} in Ø1.2 holes, soldered from the underside"))
    for xc, yp in pocket_pins():
        under.append(dict(what="contact pin solder joint (pocket in the corner block)",
                          x=[xc - PIN_POCKET[0] / 2, xc + PIN_POCKET[0] / 2],
                          y=[yp - PIN_POCKET[1] / 2, yp + PIN_POCKET[1] / 2]))
    return dict(frame="board: x right, y down from the CoreInk outline's top-left corner; the PCB is "
                      f"{CI_W - 2 * INSET:.1f} x {CI_H - 2 * INSET:.1f} from ({INSET}, {INSET})",
                underside_max_part_height=round(BOTTOM_PART_H, 2), keepout_underside=under,
                back_side="cells, contacts and cradle only; no parts", keepout_back=back,
                bus_header=dict(centre=BUS, side="underside, THT, tails on the back side",
                                max_tail_above_back=HDR_TAIL),
                contacts=cons,
                cells=[dict(x=x, y_top=round(cell_y0(i), 2), plus_end="top" if PLUS_TOP[i] else "bottom")
                       for i, x in enumerate(CELL_X)], pegs=PEGS)


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
    print(f"cells on the PCB at x = {', '.join(f'{x:.2f}' for x in CELL_X)} (pitch {CELL_PITCH:.2f}, play "
          f"{CELL_FREE:.2f} mm nominal, {X_STOP - X_LEFT - 3 * AAA_D_MAX:.2f} mm with {AAA_D_MAX} mm cells); axis "
          f"{CONTACT_Z:.2f} mm above the PCB, dimple centre {CONTACT_C:.2f}; contact x "
          f"{', '.join(f'{x:.2f}' for x in CONTACT_X)}")
    print(f"cradle stop at x = {X_STOP:.2f}; left wall {WALL_THIN} mm thin from z = {THIN_Z[0]:.1f} to {THIN_Z[1]:.1f}")
    for d in (AAA_D_MIN, AAA_D, AAA_D_MAX):
        r = d / 2
        dx = PIN_X_IN - HDR_PIN_W / 2 - (X_STOP - r)
        print(f"  cell {d} mm against the stop: {CELL_LIFT + r - (r * r - dx * dx) ** 0.5 - HDR_TAIL:.2f} mm over the header's tails")
    print(f"leaves: free gap {Y_FACE_FREE[1] - Y_FACE_FREE[0]:.2f} mm, each gives way {LEAF_DEFL[0]:.2f} to "
          f"{LEAF_DEFL[1]:.2f} mm for {AAA_L_MIN} to {AAA_L_MAX} mm cells; pressed leaf {LEAF_RIB_CLR:.2f} mm off the rib; "
          f"{len(pocket_pins())} pin pockets; parts on the PCB's underside up to {BOTTOM_PART_H:.1f} mm")


if __name__ == "__main__":
    main()
