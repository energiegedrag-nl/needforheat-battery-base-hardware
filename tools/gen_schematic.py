"""Generate the BatteryBASE schematic (pcb/needforheat-battery-base-hardware.kicad_sch).

Adapted from tools/gen_schematic.py of needforheat-p1-base-hardware (same drawing primitives and netlist self-check).

Two parts:
* PARTS: every part with its symbol, value, footprint, LCSC number and the net on each pin.
  This is the source of truth for the netlist.
* draw(): the drawing. Parts are placed per function block; every pin gets a short wire ending in a net label or a
  power symbol, so the drawing reads like a netlist with notes.

After writing, the script exports the netlist with kicad-cli and checks that it equals PARTS, so the drawing can
never silently differ from the intended circuit.

Run with any Python 3:  python tools/gen_schematic.py
"""
import collections
import copy
import os
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexpr import Sym as S, dump, parse, find, first  # noqa: E402
import kicadlib  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "pcb")
PROJECT = "needforheat-battery-base-hardware"
CUSTOM_LIB = os.path.join(PCB, "bbase.kicad_sym")
CLI = os.environ.get("KICAD_CLI", os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe"))
NS = uuid.UUID("3b0c9e27-55d1-4a3c-9a7e-0b5f8e2d6c41")
POWER_NETS = ("GND", "VCELL", "V5B", "VLIPO", "V3V3")  # drawn with power symbols (global nets)


def uid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


# --------------------------------------------------------------------------
# Custom symbols (written to pcb/bbase.kicad_sym); all pins on the 2.54 mm grid
# --------------------------------------------------------------------------
def _pin(typ, x, y, ang, name, num, length=2.54):
    font_ = [S("effects"), [S("font"), [S("size"), 1.27, 1.27]]]
    return [S("pin"), S(typ), S("line"), [S("at"), x, y, ang], [S("length"), length],
            [S("name"), name, font_], [S("number"), num, font_]]


def _prop(k, v, x, y, hide=False):
    eff = [S("effects"), [S("font"), [S("size"), 1.27, 1.27]]]
    if hide:
        eff.append([S("hide"), S("yes")])
    return [S("property"), k, v, [S("at"), x, y, 0], eff]


def _box_symbol(name, ref, value, fp, desc, left, right, bottom=(), half_w=5.08, hide_numbers=False):
    """left/right: (num, name, type) from top to bottom, 2.54 mm apart; bottom: left to right."""
    n = max(len(left), len(right))
    top_y = 2.54 * ((n - 1) // 2)
    ys = [round(top_y - 2.54 * i, 2) for i in range(n)]
    y0, y1 = top_y + 2.54, ys[-1] - (5.08 if bottom else 2.54)
    pins = [_pin(t, -half_w - 2.54, ys[i], 0, nm, num) for i, (num, nm, t) in enumerate(left)]
    pins += [_pin(t, half_w + 2.54, ys[i], 180, nm, num) for i, (num, nm, t) in enumerate(right)]
    pins += [_pin(t, round(2.54 * (i - len(bottom) // 2), 2), y1 - 2.54, 90, nm, num)
             for i, (num, nm, t) in enumerate(bottom)]
    body = [S("symbol"), name + "_0_1",
            [S("rectangle"), [S("start"), -half_w, y0], [S("end"), half_w, y1],
             [S("stroke"), [S("width"), 0.254], [S("type"), S("default")]], [S("fill"), [S("type"), S("background")]]]]
    extra = [[S("pin_numbers"), [S("hide"), S("yes")]]] if hide_numbers else []
    return [S("symbol"), name, [S("pin_names"), [S("offset"), 1.016]]] + extra + [
            [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes")], [S("on_board"), S("yes")],
            _prop("Reference", ref, 0, y0 + 1.27), _prop("Value", value, 0, y1 - 1.27),
            _prop("Footprint", fp, 0, y1 - 3.81, True), _prop("Datasheet", "", 0, 0, True),
            _prop("Description", desc, 0, 0, True),
            body, [S("symbol"), name + "_1_1"] + pins]


def _rename(e, old, new):
    if isinstance(e, list):
        return [_rename(x, old, new) for x in e]
    if isinstance(e, str) and not isinstance(e, S):
        return e.replace(old, new)
    return e


def _power_symbol(net):
    """A supply symbol (arrow up) for `net`, derived from KiCad's power:+5V."""
    s = copy.deepcopy(kicadlib.load_symbol("power:+5V"))
    s[1] = "+5V"
    s = _rename(s, "+5V", net)
    return s


def write_custom_lib():
    tp = _box_symbol(
        "TP4056", "U", "TP4056", "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
        "1 A linear Li-ion charger, charge current set by PROG (I = 1200 V / R_PROG)",
        left=[("4", "VCC", "power_in"), ("8", "CE", "input"), ("2", "PROG", "passive"), ("1", "TEMP", "input")],
        right=[("5", "BAT", "power_out"), ("7", "~{CHRG}", "open_collector"), ("6", "~{STDBY}", "open_collector")],
        bottom=[("3", "GND", "power_in"), ("9", "EP", "passive")], half_w=7.62)
    boost = _box_symbol(
        "TPS61023", "U", "TPS61023", "Package_TO_SOT_SMD:SOT-563",
        "Synchronous boost converter, 0.5-5.5 V in, load disconnect in shutdown (TI TPS61023DRL)",
        left=[("3", "VIN", "power_in"), ("2", "EN", "input")],
        right=[("5", "SW", "passive"), ("6", "VOUT", "power_out"), ("1", "FB", "input")],
        bottom=[("4", "GND", "power_in")], half_w=5.08)
    det = _box_symbol(
        "TPS3840DL", "U", "TPS3840DL", "Package_TO_SOT_SMD:SOT-23-5",
        "Nano-power voltage detector, 300 nA, monitors its own VDD; open-drain ~{RESET} low when VDD < VIT- "
        "(released at VIT+ = VIT- + 200 mV), TI TPS3840DLxx",
        left=[("2", "VDD", "power_in"), ("4", "~{MR}", "input"), ("5", "CT", "passive")],
        right=[("1", "~{RESET}", "open_collector")],
        bottom=[("3", "GND", "power_in")], half_w=5.08)
    bus = _box_symbol(
        "CoreInk_Bus", "J", "CoreInk bus", "bbase:CoreInk_Bus_2x08_P2.54mm",
        "M5Stack CoreInk 2x8 back connector (CoreInk-Bus); pads named after the CoreInk signals",
        left=[("GND", "GND", "passive"), ("5VIN", "5V_IN", "passive"), ("RST", "EXT_RST", "passive"),
              ("G13", "G13", "passive"), ("G21", "G21/SDA", "passive"), ("G18", "G18/SCK", "passive"),
              ("G34", "G34", "passive"), ("G23", "G23/MOSI", "passive")],
        right=[("BAT", "BAT", "passive"), ("5VOUT", "5V_OUT", "passive"), ("3V3", "3V3", "passive"),
               ("G14", "G14", "passive"), ("G22", "G22/SCL", "passive"), ("G36", "G36", "passive"),
               ("G26", "G26", "passive"), ("G25", "G25", "passive")], half_w=10.16, hide_numbers=True)
    contact = _box_symbol(
        "CellContact", "BC", "cell contact", "bbase:MYOUNG_MY-AAA-15-J",
        "AAA cell contact plate (MYOUNG MY-AAA-15-J + button or MY-AAA-16-J - spring), one tab in a PCB slot",
        left=[("1", "C", "passive")], right=[], half_w=3.81)
    lib = [S("kicad_symbol_lib"), [S("version"), 20231120], [S("generator"), "gen_schematic.py"],
           [S("generator_version"), "1.0"], tp, boost, det, bus, contact] + [_power_symbol(n) for n in POWER_NETS[1:]]
    with open(CUSTOM_LIB, "w", encoding="utf8", newline="\n") as f:
        f.write(dump(lib) + "\n")


# --------------------------------------------------------------------------
# The circuit (source of truth for the netlist)
# --------------------------------------------------------------------------
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
TP_FP = "TestPoint:TestPoint_Pad_D1.0mm"

RES_LCSC = {"10k": "C25804", "20k": "C4184", "68k": "C23231", "100k": "C25803", "470k": "C23178", "1M": "C22935",
            "10M": "C7250"}


def R(ref, val, n1, n2):
    return dict(ref=ref, lib="Device:R", value=val, fp=R0603, lcsc=RES_LCSC[val], nets={"1": n1, "2": n2})


def C(ref, val, n1, n2):
    lc = {"100n": ("C14663", C0603), "1u": ("C15849", C0603), "10u": ("C15850", C0805)}[val]
    return dict(ref=ref, lib="Device:C", value=val, fp=lc[1], lcsc=lc[0], nets={"1": n1, "2": n2})


def NMOS(ref, g, d, s):
    return dict(ref=ref, lib="Transistor_FET:2N7002", value="2N7002", fp=SOT23, lcsc="C8545", nets={"1": g, "2": s, "3": d})


def PMOS(ref, g, d, s):
    return dict(ref=ref, lib="Transistor_FET:AO3401A", value="AO3401A", fp=SOT23, lcsc="C15127", nets={"1": g, "2": s, "3": d})


def CONTACT(ref, plus, net, where):
    if plus:
        return dict(ref=ref, lib="bbase:CellContact", value=f"+ plate, {where}", fp="bbase:MYOUNG_MY-AAA-15-J",
                    lcsc="C51889749", nets={"1": net})
    return dict(ref=ref, lib="bbase:CellContact", value=f"- spring, {where}", fp="bbase:MYOUNG_MY-AAA-16-J",
                lcsc="C51889750", nets={"1": net})


def TP(ref, net):
    return dict(ref=ref, lib="Connector:TestPoint", value=net, fp=TP_FP, lcsc="", nets={"1": net}, bom=False)


PARTS = [
    # 1. cells, contacts, reverse-polarity protection. Series: GND - cell 1 - N12 - cell 2 - N23 - cell 3 - BAT_RAW
    CONTACT("BC1", True, "N12", "cell 1 top"),
    CONTACT("BC2", False, "GND", "cell 1 bottom"),
    CONTACT("BC3", False, "N12", "cell 2 top"),
    CONTACT("BC4", True, "N23", "cell 2 bottom"),
    CONTACT("BC5", False, "N23", "cell 3 bottom"),
    CONTACT("BC6", True, "BAT_RAW", "cell 3 top"),
    PMOS("Q1", "GND", "BAT_RAW", "VCELL"),
    C("C1", "10u", "VCELL", "GND"),
    # 2. boost to 4.7 V, only while charging (EN); load disconnect when off
    dict(ref="U1", lib="bbase:TPS61023", value="TPS61023DRL", fp="Package_TO_SOT_SMD:SOT-563", lcsc="C919459",
         nets={"3": "VCELL", "2": "EN", "5": "SW", "6": "V5B", "1": "FB", "4": "GND"}),
    dict(ref="L1", lib="Device:L", value="1u", fp="Inductor_SMD:L_Sunlord_SWPA3015S", lcsc="C43388",
         nets={"1": "VCELL", "2": "SW"}),
    R("R1", "470k", "V5B", "FB"),
    R("R2", "68k", "FB", "GND"),
    C("C2", "10u", "V5B", "GND"),
    C("C3", "10u", "V5B", "GND"),
    # 3. charger 60 mA and its isolation from the LiPo when off
    dict(ref="U2", lib="bbase:TP4056", value="TP4056", fp="Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
         lcsc="C16581", nets={"4": "V5B", "8": "V5B", "2": "PROG", "1": "GND", "5": "TPBAT", "7": None,
                              "6": "STDBY", "3": "GND", "9": "GND"}),
    R("R3", "20k", "PROG", "GND"),
    C("C4", "10u", "TPBAT", "GND"),
    PMOS("Q7", "ISOG", "TPBAT", "VLIPO"),
    R("R9", "1M", "ISOG", "VLIPO"),
    NMOS("Q8", "EN", "ISOG", "GND"),
    # 4. charge latch
    PMOS("Q2", "HOLDG", "ENP", "VCELL"),
    R("R10", "10M", "HOLDG", "VCELL"),
    R("R11", "10k", "ENP", "EN"),
    R("R12", "10M", "EN", "GND"),
    R("R13", "1M", "EN", "HG"),
    C("C5", "100n", "HG", "GND"),
    NMOS("Q3", "HG", "HD", "GND"),
    R("R14", "100k", "HD", "HOLDG"),
    NMOS("Q4", "FORCE", "HD", "GND"),
    R("R15", "1M", "FORCE", "GND"),
    NMOS("Q5", "INHIBIT", "EN", "GND"),
    R("R16", "1M", "INHIBIT", "GND"),
    R("R17", "100k", "STDBY", "HG"),
    dict(ref="U3", lib="bbase:TPS3840DL", value="TPS3840DL35", fp=SOT235, lcsc="C2866251",
         nets={"2": "VLIPO", "4": None, "5": None, "1": "LOWBAT", "3": "GND"}),
    C("C6", "100n", "VLIPO", "GND"),
    R("R18", "1M", "LOWBAT", "HOLDG"),
    dict(ref="U4", lib="bbase:TPS3840DL", value="TPS3840DL28", fp=SOT235, lcsc="C2066416",
         nets={"2": "VCELL", "4": None, "5": None, "1": "UVG", "3": "GND"}),
    R("R19", "10M", "UVG", "VCELL"),
    PMOS("Q6", "UVG", "HOLDG", "VCELL"),
    # 5. firmware interface, powered only from the CoreInk's 3V3
    dict(ref="U5", lib="Analog_ADC:ADS1115IDGS", value="ADS1115", fp="Package_SO:MSOP-10_3x3mm_P0.5mm", lcsc="C37593",
         nets={"1": "GND", "2": None, "3": "GND", "4": "AIN_CELL", "5": "AIN_PROG", "6": "GND", "7": "GND",
               "8": "V3V3", "9": "SDA", "10": "SCL"}),
    C("C7", "100n", "V3V3", "GND"),
    PMOS("Q9", "DIVG", "DIVT", "VCELL"),
    R("R20", "1M", "DIVG", "VCELL"),
    NMOS("Q10", "V3V3", "DIVG", "GND"),
    R("R21", "100k", "DIVT", "AIN_CELL"),
    R("R22", "100k", "AIN_CELL", "GND"),
    NMOS("Q11", "V3V3", "PROG", "AIN_PROG"),
    R("R23", "1M", "AIN_PROG", "GND"),
    dict(ref="U6", lib="Interface_Expansion:PCA9536D", value="PCA9536", fp="Package_SO:VSSOP-8_3x3mm_P0.65mm",
         lcsc="C2649389", nets={"1": "INHIBIT", "2": "FORCE", "3": None, "4": "GND", "5": None, "6": "SCL", "7": "SDA",
                                "8": "V3V3"}),
    C("C9", "100n", "V3V3", "GND"),
    # 6. CoreInk bus
    dict(ref="J1", lib="bbase:CoreInk_Bus", value="CoreInk bus", fp="bbase:CoreInk_Bus_2x08_P2.54mm", lcsc="C706898",
         nets={"GND": "GND", "BAT": "VLIPO", "5VIN": None, "5VOUT": None, "RST": None, "3V3": "V3V3", "G13": None,
               "G14": None, "G21": "SDA", "G22": "SCL", "G18": None, "G36": None, "G34": None, "G26": None,
               "G23": None, "G25": None}),
    # 7. test points, peg holes
    TP("TP1", "VCELL"), TP("TP2", "V5B"), TP("TP3", "EN"), TP("TP4", "PROG"), TP("TP5", "GND"),
] + [dict(ref=f"H{i}", lib="Mechanical:MountingHole", value="Peg hole 2.2 mm", fp="bbase:PegHole_2.2mm_NPTH",
          lcsc="", nets={}, bom=False) for i in (1, 2, 3)]



# --------------------------------------------------------------------------
# Drawing primitives
# --------------------------------------------------------------------------
def rot_pt(x, y, rot):
    return {0: (x, y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)}[rot]


def font(size=1.27, justify=None, hide=False, bold=False):
    f = [S("font"), [S("size"), size, size]]
    if bold:
        f.append([S("bold"), S("yes")])
    e = [S("effects"), f]
    if justify and justify != "center":
        e.append([S("justify")] + [S(x) for x in justify.split()])
    if hide:
        e.append([S("hide"), S("yes")])
    return e


def r2(v):
    return round(v + 0.0, 2)


class Sheet:
    def __init__(self):
        self.parts = {p["ref"]: p for p in PARTS}
        self.lib = {}
        self.items = []
        self.placed = {}
        self.wires = []      # (a, b)
        self.anchors = []    # connection points of power symbols and flags (for junctions)
        self.labels = []     # (name, point): checked to sit on a wire end or a pin
        self.npwr = 0
        self.dx = self.dy = 0.0

    # ---- coordinates -----------------------------------------------------
    def at(self, x, y):
        return (r2(x + self.dx), r2(y + self.dy))

    def block(self, title, x0, y0, x1, y1, dx=0.0, dy=0.0):
        """Dashed frame with a title; following coordinates are shifted by (dx, dy)."""
        self.dx, self.dy = dx, dy
        self.items.append([S("rectangle"), [S("start"), x0, y0], [S("end"), x1, y1],
                           [S("stroke"), [S("width"), 0.2], [S("type"), S("dash")], [S("color"), 0, 0, 132, 1]],
                           [S("fill"), [S("type"), S("none")]], [S("uuid"), uid("frame", title)]])
        self.items.append([S("text"), title, [S("exclude_from_sim"), S("no")], [S("at"), x0 + 2.54, y0 + 5.08, 0],
                           font(2.54, "left bottom", bold=True), [S("uuid"), uid("blk", title)]])

    def note(self, text, x, y, size=1.27):
        x, y = self.at(x, y)
        self.items.append([S("text"), text, [S("exclude_from_sim"), S("no")], [S("at"), x, y, 0],
                           font(size, "left bottom"), [S("uuid"), uid("note", text[:40], x, y)]])

    def _sym(self, lid):
        if lid not in self.lib:
            self.lib[lid] = kicadlib.load_symbol(lid, {"bbase": CUSTOM_LIB})
        return self.lib[lid]

    # ---- parts -----------------------------------------------------------
    def place(self, ref, x, y, rot=0, mirror=None, side=None):
        p = self.parts[ref]
        lid = p["lib"]
        sym = self._sym(lid)
        X, Y = self.at(x, y)
        pins = {}
        for pin in kicadlib.pins(sym):
            if pin["unit"] not in (0, 1):
                continue
            px, py = pin["x"], pin["y"]
            if mirror == "x":
                py = -py
            elif mirror == "y":
                px = -px
            dx, dy = rot_pt(px, py, rot)
            pins[pin["number"]] = (r2(X + dx), r2(Y - dy))
        self.placed[ref] = dict(X=X, Y=Y, rot=rot, mirror=mirror, pins=pins)
        for num, net in p["nets"].items():
            if net is None:
                x_, y_ = pins[num]
                self.items.append([S("no_connect"), [S("at"), x_, y_], [S("uuid"), uid(ref, "nc", num)]])
        fields = self._fields(p, X, Y, rot, mirror, side)
        props = []
        for k, v, (fx, fy), ang, just, hide in fields:
            props.append([S("property"), k, v, [S("at"), r2(fx), r2(fy), ang], font(justify=just, hide=hide)])
        dnp = bool(p.get("dnp"))
        in_bom = p.get("bom", True) and not dnp
        s = [S("symbol"), [S("lib_id"), lid], [S("at"), X, Y, rot]]
        if mirror:
            s.append([S("mirror"), S(mirror)])
        s += [[S("unit"), 1], [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes" if in_bom else "no")],
              [S("on_board"), S("yes")], [S("dnp"), S("yes" if dnp else "no")], [S("uuid"), uid(ref, "sym")]] + props
        s += [[S("pin"), n, [S("uuid"), uid(ref, "pin", n)]] for n in pins]
        s.append([S("instances"), [S("project"), PROJECT, [S("path"), "/" + uid("sheet"), [S("reference"), ref],
                                                             [S("unit"), 1]]]])
        self.items.append(s)

    def _fields(self, p, X, Y, rot, mirror, side):
        """Reference and value placement, always horizontal and clear of the pins."""
        lid, ref, val = p["lib"], p["ref"], p["value"]
        hid = [("Footprint", p["fp"], (X, Y), 0, None, True), ("Datasheet", "", (X, Y), 0, None, True)]
        if p.get("lcsc"):
            hid.append(("LCSC", p["lcsc"], (X, Y), 0, None, True))
        ang = 90 if rot in (90, 270) else 0
        # KiCad keeps text readable, which mirrors the justification for rotation 90/180 and for mirror y
        flip = (rot in (90, 180)) != (mirror == "y")
        L, Rj = ("right", "left") if flip else ("left", "right")
        two = lid in ("Device:R", "Device:C", "Device:L")
        diode = lid in ("Device:LED", "Device:D_TVS", "Device:D_Zener", "Diode:1N5819WS")
        hide_val = lid == "Connector:TestPoint"
        right = [((X + 2.54, Y - 0.635), L), ((X + 2.54, Y + 1.905), L)]
        left = [((X - 2.54, Y - 0.635), Rj), ((X - 2.54, Y + 1.905), Rj)]
        if (two and rot in (0, 180)) or (diode and rot in (90, 270)):
            f = left if side == "left" else right
        elif two:
            f = [((X, Y - 3.81), "center"), ((X, Y - 1.905), "center")] if side == "above" else \
                [((X, Y - 1.905), "center"), ((X, Y + 3.175), "center")]
        elif diode:
            f = [((X, Y - 2.54), "center"), ((X, Y + 3.81), "center")]
        elif lid.startswith("Transistor_FET"):
            if rot == 90:      # gate down
                f = [((X + 1.27, Y + 3.81), L), ((X + 1.27, Y + 6.35), L)]
            elif rot == 270:   # gate up
                f = [((X, Y + 6.35), "center"), ((X, Y + 8.89), "center")]
            elif side == "below_l":
                f = [((X + 1.27, Y + 7.62), Rj), ((X + 1.27, Y + 9.525), Rj)]
            elif side == "top_r":
                f = [((X + 3.81, Y - 6.35), L), ((X + 3.81, Y - 4.445), L)]
            elif side == "top" and mirror == "y":
                f = [((X - 3.81, Y - 6.35), Rj), ((X - 3.81, Y - 4.445), Rj)]
            elif side == "top":
                f = [((X + 3.81, Y - 6.35), L), ((X + 3.81, Y - 4.445), L)]
            elif (side == "left") != (mirror == "y"):
                f = [((X - 5.08, Y - 0.635), Rj), ((X - 5.08, Y + 1.905), Rj)]
            else:
                f = [((X + 5.08, Y - 0.635), L), ((X + 5.08, Y + 1.905), L)]
        elif lid == "Diode:BAT54C":
            f = [((X, Y - 6.35), "center"), ((X, Y - 4.445), "center")]
        elif lid in ("74xGxx:74LVC1G14", "74xGxx:74LVC1G17"):
            f = [((X + 2.54, Y + 5.715), "left"), ((X + 2.54, Y + 7.62), "left")]
        elif lid == "bbase:PCA9633_8pin":
            f = [((X, Y - 6.35), "center"), ((X + 1.27, Y + 12.065), "left")]
        elif lid == "Regulator_Linear:XC6206PxxxMR":
            f = [((X, Y - 7.62), "center"), ((X, Y - 5.715), "center")]
        elif lid in ("bbase:TPS61023", "bbase:TPS3840DL"):
            f = [((X, Y - 6.35), "center"), ((X, Y + 10.16), "center")]
        elif lid == "bbase:CellContact":
            f = [((X, Y - 2.54), "center"), ((X, Y + 3.81), "center")]
        elif lid in ("Analog_ADC:ADS1115IDGS", "Interface_Expansion:PCA9536D"):
            f = [((X + 2.54, Y - 10.16), "left"), ((X + 2.54, Y - 8.255), "left")]
        elif lid == "bbase:TP4056":
            f = [((X, Y - 8.89), "center"), ((X, Y - 6.35), "center")]
        elif lid == "bbase:CoreInk_Bus":
            f = [((X, Y - 13.97), "center"), ((X, Y + 15.24), "center")]
        elif lid == "Connector:6P6C":
            f = [((X - 2.54, Y - 15.24), "center"), ((X - 2.54, Y - 13.335), "center")]
        elif lid == "Connector:TestPoint":
            f = [((X, Y - 5.715), "center"), ((X, Y - 7.62), "center")]
        elif lid == "Mechanical:MountingHole":
            f = [((X + 3.81, Y - 0.635), "left"), ((X + 3.81, Y + 1.905), "left")]
        else:
            f = right
        ang_ = ang if (two or diode or lid.startswith("Transistor_FET")) else 0
        return [("Reference", ref, f[0][0], ang_, f[0][1], False),
                ("Value", val, f[1][0], ang_, f[1][1], hide_val)] + hid

    def pin(self, spec):
        """'R1.2' -> absolute pin position; tuples are shifted by the current block offset."""
        if isinstance(spec, str):
            ref, num = spec.split(".", 1)
            return self.placed[ref]["pins"][num]
        return self.at(*spec)

    # ---- connections -----------------------------------------------------
    def wire(self, *pts, first="h"):
        """Wire through the points; an L-corner is added between points that are not aligned."""
        P = [self.pin(p) for p in pts]
        seq = [P[0]]
        for b in P[1:]:
            a = seq[-1]
            if a[0] != b[0] and a[1] != b[1]:
                seq.append((b[0], a[1]) if first == "h" else (a[0], b[1]))
            seq.append(b)
        for a, b in zip(seq, seq[1:]):
            if a != b:
                self.wires.append((a, b))
                self.items.append([S("wire"), [S("pts"), [S("xy"), *a], [S("xy"), *b]],
                                   [S("stroke"), [S("width"), 0], [S("type"), S("default")]],
                                   [S("uuid"), uid("w", a, b)]])
        return seq[-1]

    def label(self, name, pt, d="r", size=1.27):
        x, y = self.pin(pt)
        ang, just = {"r": (0, "left bottom"), "l": (180, "right bottom"), "u": (90, "left bottom"),
                     "d": (270, "right bottom")}[d]
        self.labels.append((name, (x, y)))
        self.items.append([S("label"), name, [S("at"), x, y, ang], font(size, just), [S("uuid"), uid("lbl", name, x, y)]])

    def stub(self, pin, name, length=5.08, d="r"):
        """Short wire from a pin, ending in a net label."""
        x, y = self.pin(pin)
        dx, dy = {"r": (length, 0), "l": (-length, 0), "u": (0, -length), "d": (0, length)}[d]
        end = (r2(x + dx), r2(y + dy))
        self.wire((x - self.dx, y - self.dy), (end[0] - self.dx, end[1] - self.dy))
        self.label(name, (end[0] - self.dx, end[1] - self.dy), d)

    def power(self, net, pt):
        x, y = self.pin(pt)
        self.npwr += 1
        ref = f"#PWR{self.npwr:03d}"
        if net == "GND":
            lid, vpos, rot = "power:GND", (x, y + 4.445), 0
        elif net == "PWR_FLAG":
            lid, vpos, rot = "power:PWR_FLAG", (x, y - 4.445), 0
            ref = f"#FLG{self.npwr:03d}"
        else:
            lid, vpos, rot = "bbase:" + net, (x, y - 4.445), 0
        self._sym(lid)
        self.anchors.append((x, y))
        sym = self.lib[lid]
        pins = [p["number"] for p in kicadlib.pins(sym)]
        self.items.append([S("symbol"), [S("lib_id"), lid], [S("at"), x, y, rot], [S("unit"), 1],
                           [S("exclude_from_sim"), S("no")], [S("in_bom"), S("no")], [S("on_board"), S("yes")],
                           [S("dnp"), S("no")], [S("uuid"), uid(ref, "sym")],
                           [S("property"), "Reference", ref, [S("at"), x, y, 0], font(hide=True)],
                           [S("property"), "Value", "PWR_FLAG" if net == "PWR_FLAG" else net,
                            [S("at"), vpos[0], vpos[1], 0], font(justify="center", hide=net == "GND")],
                           [S("property"), "Footprint", "", [S("at"), x, y, 0], font(hide=True)],
                           [S("property"), "Datasheet", "", [S("at"), x, y, 0], font(hide=True)]]
                          + [[S("pin"), n, [S("uuid"), uid(ref, "pin", n)]] for n in pins]
                          + [[S("instances"), [S("project"), PROJECT, [S("path"), "/" + uid("sheet"),
                                                                         [S("reference"), ref], [S("unit"), 1]]]]])

    def check_labels(self):
        ends = {pt for w in self.wires for pt in w}
        pinpts = {pt for pl in self.placed.values() for pt in pl["pins"].values()}
        bad = [f"{n} at {pt}" for n, pt in self.labels if pt not in ends and pt not in pinpts]
        if bad:
            raise SystemExit("labels not on a wire end or pin: " + ", ".join(bad))

    def junctions(self):
        pinpts = collections.Counter(pt for pl in self.placed.values() for pt in pl["pins"].values())
        ends = collections.Counter(pt for w in self.wires for pt in w)
        pts = set(ends)
        for pt in pts:
            n = ends[pt] + pinpts[pt] + self.anchors.count(pt)
            for a, b in self.wires:
                if pt not in (a, b) and (min(a[0], b[0]) <= pt[0] <= max(a[0], b[0])) and \
                        (min(a[1], b[1]) <= pt[1] <= max(a[1], b[1])):
                    n += 2
            if n >= 3:
                self.items.append([S("junction"), [S("at"), *pt], [S("diameter"), 0], [S("color"), 0, 0, 0, 0],
                                   [S("uuid"), uid("j", pt)]])




# --------------------------------------------------------------------------
# The drawing (A3, mm, y down)
# --------------------------------------------------------------------------
def auto(s, ref, x, y, rot=0, mirror=None, side=None, length=5.08):
    """Place a part and give every connected pin a short wire ending in a net label or a power symbol."""
    s.place(ref, x, y, rot, mirror, side)
    pl = s.placed[ref]
    for num, net in s.parts[ref]["nets"].items():
        if not net:
            continue
        px, py = pl["pins"][num]
        dx, dy = px - pl["X"], py - pl["Y"]
        d = ("r" if dx > 0 else "l") if abs(dx) >= abs(dy) else ("d" if dy > 0 else "u")
        if net in POWER_NETS:
            ex, ey = {"r": (length, 0), "l": (-length, 0), "u": (0, -length), "d": (0, length)}[d]
            if net == "GND" and d == "u":
                ex, ey = (length, 0)
            elif net != "GND" and d == "d":
                ex, ey = (length, 0)
            end = (r2(px + ex), r2(py + ey))
            s.wire((px - s.dx, py - s.dy), (end[0] - s.dx, end[1] - s.dy))
            s.power(net, (end[0] - s.dx, end[1] - s.dy))
        else:
            s.stub(f"{ref}.{num}", net, length, d)


def notes(s, x, y, lines, size=1.27):
    for i, t in enumerate(lines):
        s.note(t, x, y + 2.54 * i, size)


def grid(s, refs, x0, y0, dx, dy, ncol, **kw):
    for i, ref in enumerate(refs):
        auto(s, ref, x0 + dx * (i % ncol), y0 + dy * (i // ncol), **kw)


def draw(s):
    # 1 ---------------------------------------------------------------------
    s.block("1  Cells, contacts, reverse-polarity protection", 15.24, 15.24, 132.08, 119.38)
    grid(s, ["BC1", "BC3", "BC6", "BC2", "BC4", "BC5"], 33.02, 35.56, 33.02, 17.78, 3)
    auto(s, "Q1", 40.64, 76.2, rot=90, side="left")
    auto(s, "C1", 81.28, 76.2)
    notes(s, 20.32, 96.52, [
        "Three AAA cells in series: GND (BC2) - cell 1 - N12 (BC1 = BC3) - cell 2 - N23 (BC4 = BC5) - cell 3 - BAT_RAW (BC6).",
        "Contacts: MYOUNG MY-AAA-15-J (+ plate) and MY-AAA-16-J (- spring), tabs soldered in PCB slots (THT);",
        "they stand on the PCB's back side and lean on the printed cradle. The spring is always the minus end.",
        "Q1: reverse-polarity protection (the whole pack in backwards). VCELL = 2.7 ... 4.8 V (alkaline), 3.0 ... 4.2 V (NiMH).",
        "No current flows from the cells unless the latch (block 4) switches the boost on: about 0.4 uA in total."])

    # 2 ---------------------------------------------------------------------
    s.block("2  Boost to 4.7 V, on only while charging", 137.16, 15.24, 254.0, 119.38)
    auto(s, "U1", 175.26, 50.8)
    auto(s, "L1", 162.56, 30.48, rot=90)
    grid(s, ["R1", "R2"], 210.82, 35.56, 0, 25.4, 1)
    grid(s, ["C2", "C3"], 233.68, 35.56, 0, 25.4, 1)
    notes(s, 142.24, 88.9, [
        "U1 TPS61023: VOUT = 0.595 V x (1 + R1/R2) = 4.71 V; just above the 4.2 V the charger needs,",
        "so the linear charger (block 3) loses little: about 0.9 x 4.0/4.7 = 77 % from the cells to the LiPo.",
        "EN low: shutdown with load disconnect (no path from VIN to VOUT), about 0.1 uA from the cells.",
        "Fresh alkaline cells (4.8 V) above 4.7 V: U1 passes the input through; the charger copes."])

    # 3 ---------------------------------------------------------------------
    s.block("3  Charger 60 mA into the CoreInk battery, isolated when off", 259.08, 15.24, 405.13, 119.38)
    auto(s, "U2", 289.56, 50.8)
    grid(s, ["R3", "C4"], 320.04, 76.2, 15.24, 0, 2)
    auto(s, "Q7", 358.14, 45.72, rot=90, side="left")
    auto(s, "R9", 383.54, 38.1)
    auto(s, "Q8", 383.54, 66.04)
    notes(s, 264.16, 96.52, [
        "U2 TP4056: 60 mA (R3 = 20k: I = 1200 V / R3), CC/CV to 4.2 V, ~STDBY low = charge done (C/10).",
        "PROG voltage = 1.0 V x I / 60 mA: the firmware reads the charge current there (block 5).",
        "Q7/Q8: the TP4056 is cut off from the CoreInk battery (VLIPO) while not charging, so no current",
        "leaks out of the LiPo into the unpowered charger (the TP4056 alone allows up to 2 uA)."])

    # 4 ---------------------------------------------------------------------
    s.block("4  Charge latch: on by the firmware or a low LiPo, off when done, cells empty or inhibited",
            15.24, 124.46, 254.0, 241.3)
    grid(s, ["Q2", "R10", "R11", "R12", "R13", "C5"], 30.48, 142.24, 30.48, 0, 6)
    grid(s, ["Q3", "R14", "Q4", "R15", "Q5", "R16", "R17"], 30.48, 167.64, 30.48, 0, 7)
    auto(s, "U3", 40.64, 195.58)
    grid(s, ["C6", "R18"], 76.2, 195.58, 20.32, 0, 2)
    auto(s, "U4", 132.08, 195.58)
    auto(s, "R19", 167.64, 195.58)
    auto(s, "Q6", 193.04, 195.58)
    notes(s, 20.32, 215.9, [
        "Off: Q2 off (R10), EN low (R12), everything off; the latch itself draws nothing (gates only).",
        "On: Q2 pulls EN up (R11) -> U1 boost, Q8/Q7 connect the charger; EN holds Q3 on through R13 (C5: 0.1 s),",
        "Q3 keeps Q2's gate low through R14. Set: FORCE pulse from the firmware (Q4), or U3 (TPS3840DL35) when the",
        "LiPo is below 3.5 V (released at 3.7 V, well under full). Reset: ~STDBY (done) pulls HG low through R17;",
        "C5 rides through the undefined ~STDBY while the TP4056 powers up. INHIBIT (Q5) pulls EN low. U4 (TPS3840DL28):",
        "cells below 2.8 V -> Q6 pulls HOLDG up: no start, a running charge stops. Off-state current: U3 0.3 uA",
        "(from the LiPo), U4 0.3 uA and U1 0.1 uA (from the cells). Simulated: docs/simulation."])

    # 5 ---------------------------------------------------------------------
    s.block("5  Firmware interface (I2C), powered only from the CoreInk's 3V3", 259.08, 124.46, 405.13, 241.3)
    auto(s, "U5", 289.56, 152.4)
    auto(s, "C7", 320.04, 139.7)
    auto(s, "U6", 289.56, 198.12)
    auto(s, "C9", 320.04, 187.96)
    grid(s, ["Q9", "R20", "Q10"], 340.36, 142.24, 22.86, 0, 3)
    grid(s, ["R21", "R22"], 340.36, 167.64, 22.86, 0, 2)
    grid(s, ["Q11", "R23"], 340.36, 195.58, 22.86, 0, 2)
    notes(s, 264.16, 220.98, [
        "U5 ADS1115 (0x48): AIN0 = VCELL / 2 through Q9 (connected only while 3V3 is on), AIN1 = PROG through Q11.",
        "U6 PCA9536 (0x41): IO0 = INHIBIT, IO1 = FORCE (pulse) to block 4. Both chips and Q9-Q11 are off with the CoreInk:",
        "no current from the cells, and no pin can feed the unpowered CoreInk (gates, or nodes at 0 V).",
        "No I2C pull-ups here: the CoreInk has them."])

    # 6 ---------------------------------------------------------------------
    s.block("6  CoreInk bus", 15.24, 246.38, 132.08, 284.48)
    x, y = 60.96, 266.7
    s.place("J1", x, y)
    s.stub("J1.G21", "SDA", 7.62, "l")
    px, py = s.pin("J1.GND")
    s.wire((px, py), (px - 7.62, py))
    s.power("GND", (px - 7.62, py))
    for pin, net in (("BAT", "VLIPO"), ("3V3", "V3V3"), ("G22", "SCL")):
        if net in POWER_NETS:
            px, py = s.pin("J1." + pin)
            s.wire((px, py), (px + 7.62, py))
            s.power(net, (px + 7.62, py))
        else:
            s.stub("J1." + pin, net, 7.62, "r")

    # 7 ---------------------------------------------------------------------
    s.block("7  Test points, peg holes, ERC flags", 137.16, 246.38, 254.0, 284.48)
    for i, tp in enumerate(["TP1", "TP2", "TP3", "TP4", "TP5"]):
        auto(s, tp, 144.78 + 15.24 * i, 259.08)
    for i in (1, 2, 3):
        s.place(f"H{i}", 144.78 + 22.86 * (i - 1), 276.86)
    for i, net in enumerate(["GND", "VCELL", "VLIPO", "V3V3"]):
        x = 213.36 + 10.16 * i
        s.power("PWR_FLAG", (x, 276.86))
        s.wire((x, 276.86), (x, 279.4))
        if net == "GND":
            s.power("GND", (x, 279.4))
        else:
            s.wire((x, 279.4), (x + 5.08, 279.4))
            s.power(net, (x + 5.08, 279.4))

    # firmware interface, revision history ------------------------------------
    s.dx = s.dy = 0.0
    notes(s, 259.08, 251.46, [
        "Firmware interface (CoreInk ESP32, I2C G21/G22, shared with the RTC 0x51):",
        "0x48 ADS1115: cells = 2 x AIN0; charge current = 60 mA x AIN1 / 1.0 V",
        "0x41 PCA9536: IO0 = INHIBIT (keep charging off while awake), IO1 = FORCE (pulse: start a charge)",
        "BAT: CoreInk battery (charged by U2). 3V3: powers block 5 only.",
        "Revision 1.0, 2026-11: first design. Rationale: docs/design.md."])


# --------------------------------------------------------------------------
# Writer and self-check
# --------------------------------------------------------------------------
def build():
    write_custom_lib()
    s = Sheet()
    draw(s)
    missing = set(s.parts) - set(s.placed)
    if missing:
        raise SystemExit(f"parts not placed: {sorted(missing)}")
    s.check_labels()
    s.junctions()
    sch = [S("kicad_sch"), [S("version"), 20231120], [S("generator"), "eeschema"], [S("generator_version"), "8.0"],
           [S("uuid"), uid("sheet")], [S("paper"), "A3"],
           [S("title_block"), [S("title"), "NeedForHeat BatteryBASE"], [S("date"), "2026-11-15"], [S("rev"), "1.0"],
            [S("company"), "energiegedrag.nl"],
            [S("comment"), 1, "M5Stack CoreInk extension: 3 x AAA cells charge the CoreInk battery"],
            [S("comment"), 2, "Licensed under CERN-OHL-P v2"],
            [S("comment"), 3, "Companion of the NeedForHeat P1-BASE v3"]],
           [S("lib_symbols")] + list(s.lib.values())] + s.items + [
           [S("sheet_instances"), [S("path"), "/", [S("page"), "1"]]]]
    out = os.path.join(PCB, PROJECT + ".kicad_sch")
    with open(out, "w", encoding="utf8", newline="\n") as f:
        f.write(dump(sch) + "\n")
    print("wrote", out)
    verify(out)


def verify(sch):
    """Export the netlist with kicad-cli and compare it with PARTS."""
    with tempfile.TemporaryDirectory() as tmp:
        net = os.path.join(tmp, "n.net")
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, sch], check=True,
                       capture_output=True)
        n = parse(open(net, encoding="utf8").read())
    got = {}
    for nt in find(first(n, "nets"), "net"):
        name = first(nt, "name")[1]
        nodes = frozenset((first(x, "ref")[1], first(x, "pin")[1]) for x in find(nt, "node"))
        got[name] = nodes
    want = collections.defaultdict(set)
    for p in PARTS:
        for pin, netname in p["nets"].items():
            if netname:
                want[netname if netname in POWER_NETS else "/" + netname].add((p["ref"], pin))
    errors = []
    for name, nodes in want.items():
        if got.get(name) != nodes:
            errors.append(f"{name}: drawing has {sorted(got.get(name, []))}, circuit wants {sorted(nodes)}")
    extra = [k for k, v in got.items() if k not in want and not k.startswith("unconnected-")]
    for k in extra:
        errors.append(f"unexpected net {k}: {sorted(got[k])}")
    if errors:
        raise SystemExit("netlist check FAILED:\n  " + "\n  ".join(errors))
    print(f"netlist check: {len(want)} nets equal to the circuit description")


if __name__ == "__main__":
    build()
