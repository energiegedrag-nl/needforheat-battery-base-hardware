"""Write the custom footprints (pcb/bbase.pretty).

Board convention: the KiCad top side (F) is the electronics side, which faces the CoreInk (or the P1-BASE) when
the BatteryBASE is plugged in; the bottom side (B) carries the cells. Seen from the top (KiCad view), x runs the
other way than in the enclosure frame (which is seen from the back): x_kicad = 40 - x_enclosure.

* CoreInk_Bus_2x08_P2.54mm: the CoreInk 2x8 socket positions, seen from the CoreInk side (mirrored from the
  P1-BASE footprint, which is seen from the back). Part: XKB X6521WV-2x08H-C60D30 (C706898), a plain 2x8 male
  header, plastic (2.5 mm) on the top side, 6.0 mm pins into the CoreInk, 3.0 mm PCB tails.
* PegHole_2.4mm_NPTH: as the P1-BASE's 2.2 mm one, with 0.2 mm more play, but the tray's corner post is on the top side here.
* MYOUNG_MY-AAA-01: leaf contact (C964855), placed on the bottom side (flipped). Origin = the outer pin (next to
  the leaf); the inner pin is 10.25 mm along +y, under the cell. Two Ø1.2 plated holes for the Ø1.0 x 1.5 mm pins
  (they end just inside the 1.6 mm board; solder from the far side) and a copper pad under each end of the foot on
  the cell side, without paste (MYOUNG layout MY-CP-0095). The courtyard on the far side covers the solder joints.

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
    # the back side has only the tails and their solder fillets (Ø1.7): a tight courtyard there, so the cell contacts'
    # feet can come close
    s = s.replace('(fp_rect (start 3.1 -10.7) (end -3.1 10.7) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"))',
                  '(fp_rect (start 2.4 -10.0) (end -2.4 10.0) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"))')
    s = s.replace('(tags "M5Stack CoreInk MI-BUS 2x8 2.54mm stacking header")',
                  '(tags "M5Stack CoreInk MI-BUS 2x8 2.54mm pin header")')
    return s


def peg():
    src = open(os.path.join(P1, "pcb", "p1base.pretty", "PegHole_2.2mm_NPTH.kicad_mod"), encoding="utf8").read()
    s = src.replace("F.CrtYd", "@@").replace("B.CrtYd", "F.CrtYd").replace("@@", "B.CrtYd")
    s = s.replace("The peg comes from the corner post under the board, so the bottom courtyard covers the post",
                  "The peg comes from the corner post on the top side (BatteryBASE: the top side faces the CoreInk), "
                  "so the top courtyard covers the post")
    # Ø2.4 instead of 2.2: 0.2 mm radial play for the printed pegs (± 0.2 mm on their spacing)
    s = s.replace("PegHole_2.2mm_NPTH", "PegHole_2.4mm_NPTH").replace("2.2 mm non-plated hole", "2.4 mm non-plated hole")
    s = s.replace("(size 2.2 2.2) (drill 2.2)", "(size 2.4 2.4) (drill 2.4)").replace("(end 1.35 0)", "(end 1.45 0)")
    s = s.replace("(end 1.0 0) (stroke (width 0.1)", "(end 1.2 0) (stroke (width 0.1)")
    s = s.replace("and the top courtyard only the hole plus 0.25 mm", "and the bottom courtyard only the hole plus 0.25 mm")
    assert "drill 2.4" in s and "PegHole_2.4mm_NPTH" in s
    return s


def leaf():
    name = "MYOUNG_MY-AAA-01"
    pad = "(layers \"*.Cu\" \"*.Mask\"))"
    return f'''(footprint "{name}"
	(version 20240108)
	(generator "gen_footprints.py")
	(layer "F.Cu")
	(descr "MYOUNG MY-AAA-01 (C964855) AAA leaf contact, same part at both ends: foot 6.35 wide under the cell's end (top 0.50 above the board), from a 2.33 wide tab behind the leaf (y = -2.66) to the inner end (y = 12.91); leaf 10.1 high rising at y = -1.0 with a dimple facing +y; two flat pins 10.25 apart (1.0 x 0.25 x 1.5 mm, in a 1.6 mm board they end just inside the hole). MYOUNG drawing MY-CP-0095, dimensions from the vendor 3D model. The foot touches the board only at the tab (y = -2.66 ... 0.84) and at the inner end (y = 9.36 ... 12.91); the pads cover both, as in the vendor layout (the tab's pad 2.5 wide: 0.25 from the Ø2.4 peg hole next to BC2), so no metal of the contact rests on solder mask over other copper. gen_pcb.py adds a rule area under each foot (no other copper on that side). On the far side only the pins come through (they end inside the hole), so the courtyard there is each pin's pad plus 0.25.")
	(tags "AAA battery contact leaf MYOUNG")
	(property "Reference" "BC**" (at 3.8 5.1 90) (layer "F.SilkS") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Value" "{name}" (at -3.8 5.1 90) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
	(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
	(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27) (thickness 0.15))))
	(attr through_hole)
	(fp_rect (start -3.175 -1.15) (end 3.175 12.91) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
	(fp_rect (start -1.165 -2.66) (end 1.165 -1.15) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
	(fp_line (start -3.175 -1.0) (end 3.175 -1.0) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
	(fp_rect (start -3.45 -3.15) (end 3.45 13.35) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
	(fp_rect (start -1.35 -1.35) (end 1.35 1.35) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"))
	(fp_rect (start -1.35 8.9) (end 1.35 11.6) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"))
	(pad "1" thru_hole circle (at 0 0) (size 2.2 2.2) (drill 1.2) {pad}
	(pad "1" thru_hole circle (at 0 10.25) (size 2.2 2.2) (drill 1.2) {pad}
	(pad "1" smd rect (at 0 -0.92) (size 2.5 3.96) (layers "F.Cu" "F.Mask"))
	(pad "1" smd rect (at 0 10.675) (size 5.4 4.85) (layers "F.Cu" "F.Mask"))
{_model(name)})
'''


def main():
    os.makedirs(LIB, exist_ok=True)
    for name, text in (("CoreInk_Bus_2x08_P2.54mm", bus()), ("PegHole_2.4mm_NPTH", peg()),
                       ("MYOUNG_MY-AAA-01", leaf())):
        with open(os.path.join(LIB, name + ".kicad_mod"), "w", encoding="utf8", newline="\n") as f:
            f.write(text)
        print("wrote", name)


if __name__ == "__main__":
    main()
