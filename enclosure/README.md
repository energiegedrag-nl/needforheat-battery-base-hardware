# BatteryBASE enclosure (first version, for a fit check)

Generated with CadQuery by [`kuip.py`](kuip.py); the fit check is [`check_fit.py`](check_fit.py), its last result is in
[`fit-check.txt`](fit-check.txt).

```
python enclosure/kuip.py                                   # writes enclosure/fabrication/*.step / *.stl
python enclosure/check_fit.py ../needforheat-p1-base-hardware   # needs a checkout of the P1-BASE repository
```

## What it is

* **Tray** (`battery-base-kuip`): walls around the CoreInk outline (same outside as the P1-BASE v3 tray), four
  LEGO-compatible posts underneath (7 mm, three crush ribs) at the CoreInk's LEGO holes, corner blocks that carry a
  40 x 56 mm PCB 2.5 mm above the stand-on surface, three pegs that key the PCB.
* **Lid** (`battery-base-lid`): clicks on like the P1-BASE lid (thin lip with two bumps per long side, grooves in the
  walls, pry notch in the bottom wall); ribs under it keep the three AAA cells in their clips; the polarity of each
  cell is engraved on the outside. The BatteryBASE is the end of a stack, so the lid has no LEGO holes or bus socket.
* **Fit model** (`battery-base-fit.step`): tray, lid, a PCB placeholder, three AAA cells and the 2x8 header (2.5 mm
  plastic, 6 mm pins), to look at in a STEP viewer.

Height: 17.6 mm above the surface it stands on (the CoreInk's back or the lid of a P1-BASE v3).

**Shipping:** modules ship loose (not stacked) in a PostNL letterbox parcel (max. 38 × 26.5 × 3.2 cm), without
cells. Each module must stay ≤ 27 mm thick from the lid top to the tips of its LEGO posts (≥ 5 mm left for box and
padding); `kuip.py` asserts this. BatteryBASE: 24.6 mm.

## Assumptions to verify (the PCB is not designed yet)

1. Cells lie on the PCB in PCB-mounted clips or a holder, 1.0 mm above the board surface, 11.2 mm apart, with 5.75 mm at
   each end for the contacts. Change `CELL_LIFT`, `CELL_PITCH` and `CLIP_L` once the clips are chosen.
2. No parts on the PCB under the cells taller than the clip lift; the electronics go next to the cells or on the
   bottom side (the bottom is open between the corner blocks, 2.5 mm high, minus the header).
3. Snap fit (bump 0.35 mm, groove 0.55 mm): same values as the P1-BASE; adjust `SNAP_P` after a test print.

## Printed fit check (November 2026)

Five sets of tray + lid (`fabrication/*.stl` as of 15 November 2026) go into the same JLCPCB order as the P1-BASE v3
prototype: JLC3DP, MJF PA12 black, $ 18.70 for five sets. Purpose: check the stack CoreInk – P1-BASE – BatteryBASE
in hand (LEGO posts, snap fit, header reach) before the BatteryBASE PCB is designed. If the PCB later needs other
dimensions, the enclosure is reprinted.

## Fit check (15 November 2026)

No collisions inside the BatteryBASE, on a CoreInk (proxy body) or on a P1-BASE v3 (its lid and raised J1 socket from
the P1-BASE repository). The crush ribs press 0.05 mm into the 4.85 mm LEGO holes by design. The header pins reach
6.0 mm into the bus socket below (CoreInk socket 8 mm deep; the P1-BASE socket top is flush with its lid).
