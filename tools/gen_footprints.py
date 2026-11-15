"""Write the custom footprints (pcb/bbase.pretty).

Board convention: the KiCad top side (F) is the electronics side, which faces the CoreInk (or the P1-BASE) when
the BatteryBASE is plugged in; the bottom side (B) carries the cells. Seen from the top (KiCad view), x runs the
other way than in the enclosure frame (which is seen from the back): x_kicad = 40 - x_enclosure.

* CoreInk_Bus_2x08_P2.54mm: the CoreInk 2x8 socket positions, seen from the CoreInk side (mirrored from the
  P1-BASE footprint, which is seen from the back). Part: XKB X6521WV-2x08H-C60D30 (C706898), a plain 2x8 male
  header, plastic (2.5 mm) on the top side, 6.0 mm pins into the CoreInk, 3.0 mm PCB tails.
* PegHole_2.2mm_NPTH: as on the P1-BASE, but the tray's corner post is on the top side here.
* MYOUNG_MY-AAA-15-J / MYOUNG_MY-AAA-16-J: one plated slot for the contact plate's 4.0 mm tab; placed on the
  bottom side (flipped). The plate stands across the footprint's x axis, its contact facing +y (local, top side
  view before flipping). The courtyard on the far side covers the tab's solder joint.

Run with any Python 3:  python tools/gen_footprints.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "pcb", "bbase.pretty")
P1 = os.environ.get("P1BASE", os.path.join(ROOT, "..", "needforheat-p1-base-hardware"))


def _model(name, rot=(0, 0, 0)):
    return (f'\t(model "${{KIPRJMOD}}/bbase.3dshapes/{name}.step"\n\t\t(offset (xyz 0 0 0))\n'
            f'\t\t(scale (xyz 1 1 1))\n\t\t(rotate (xyz {rot[0]} {rot[1]} {rot[2]}))\n\t)\n')


def bus():
    src = open(os.path.join(P1, "pcb", "p1base.pretty", "CoreInk_Bus_2x08_P2.54mm.kicad_mod"), encoding="utf8").read()
    # mirror x: pads, the silkscreen pin-1 mark and its label
    def flip(m):
        return f"(at {-float(m.group(1)):g} {m.group(2)}"
    s = re.sub(r"\(at (-?[0-9.]+) (-?[0-9.]+)(?=[ )])", flip, src)
    s = re.sub(r"\(start (-?[0-9.]+) (-?[0-9.]+)\)", lambda m: f"(start {-float(m.group(1)):g} {m.group(2)})", s)
    s = re.sub(r"\(end (-?[0-9.]+) (-?[0-9.]+)\)", lambda m: f"(end {-float(m.group(1)):g} {m.group(2)})", s)
    s = re.sub(r'\(descr "[^"]*"\)', '(descr "M5Stack CoreInk 2x8 back connector (MI-BUS), seen from the CoreInk side '
               '(the BatteryBASE top side faces the CoreInk). Pads named after the CoreInk signals. Part: XKB '
               'X6521WV-2x08H-C60D30 (C706898): plain 2x8 male header, 2.5 mm plastic on the top side, 6.0 mm '
               'pins into the CoreInk, 3.0 mm PCB tails.")', s)
    s = re.sub(r'\(model "[^"]*"', '(model "${KIPRJMOD}/bbase.3dshapes/PinHeader_2x08_C60D30_approx.step"', s)
    s = s.replace('(tags "M5Stack CoreInk MI-BUS 2x8 2.54mm stacking header")',
                  '(tags "M5Stack CoreInk MI-BUS 2x8 2.54mm pin header")')
    return s


def peg():
    src = open(os.path.join(P1, "pcb", "p1base.pretty", "PegHole_2.2mm_NPTH.kicad_mod"), encoding="utf8").read()
    s = src.replace("F.CrtYd", "@@").replace("B.CrtYd", "F.CrtYd").replace("@@", "B.CrtYd")
    return s.replace("The peg comes from the corner post under the board, so the bottom courtyard covers the post",
                     "The peg comes from the corner post on the top side (BatteryBASE: the top side faces the CoreInk), "
                     "so the top courtyard covers the post")


def plate(plus):
    name = "MYOUNG_MY-AAA-15-J" if plus else "MYOUNG_MY-AAA-16-J"
    part = "MY-AAA-15-J (C51889749), + plate with a 1.43 mm button" if plus else \
        "MY-AAA-16-J (C51889750), - plate with a 10.5 mm spring"
    mark = "+" if plus else "-"
    return f'''(footprint "{name}"
\t(version 20240108)
\t(generator "gen_footprints.py")
\t(layer "F.Cu")
\t(descr "MYOUNG {part}: 9.0 x 8.8 x 0.3 mm plate standing on the board, one 4.0 mm tab in a plated slot, soldered on the far side. Contact faces +y. Slot from the EasyEDA footprint (4.7 x 1.1 pad); VERIFY the tab with a sample.")
\t(tags "AAA battery contact MYOUNG")
\t(property "Reference" "BC**" (at 0 -2.2 0) (layer "F.SilkS") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
\t(property "Value" "{name}" (at 0 2.2 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
\t(attr through_hole)
\t(fp_rect (start -4.5 -0.15) (end 4.5 0.15) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t(fp_line (start -4.6 -0.8) (end 4.6 -0.8) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
\t(fp_rect (start -4.75 -0.6) (end 4.75 {1.6 if plus else 1.0}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t(fp_rect (start -2.85 -1.0) (end 2.85 1.0) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"))
\t(pad "1" thru_hole oval (at 0 0) (size 4.7 1.1) (drill oval 4.3 0.6) (layers "*.Cu" "*.Mask"))
{_model(name + "_approx")})
'''


def main():
    os.makedirs(LIB, exist_ok=True)
    for name, text in (("CoreInk_Bus_2x08_P2.54mm", bus()), ("PegHole_2.2mm_NPTH", peg()),
                       ("MYOUNG_MY-AAA-15-J", plate(True)), ("MYOUNG_MY-AAA-16-J", plate(False))):
        with open(os.path.join(LIB, name + ".kicad_mod"), "w", encoding="utf8", newline="\n") as f:
            f.write(text)
        print("wrote", name)


if __name__ == "__main__":
    main()
