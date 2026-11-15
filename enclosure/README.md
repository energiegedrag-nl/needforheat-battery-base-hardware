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

## Next: follow the P1-BASE v3 changes of 15 November 2026

The fit check above is out of date: the P1-BASE v3 changed after it, and the printed fit-check sets were taken out of
the JLCPCB cart (old outline). Redesign the enclosure first, then the PCB. What changed in the P1-BASE repository
(branch `feature/p1-base-v3`, PR #5; see its `enclosure/kuip.py`, `enclosure/README.md` and `TODO.md#batteryflush`):

1. **Outside exactly the CoreInk outline** (40 × 56 mm, R 3), walls inside it, no skirt, so any CoreInk BASE also fits
   behind a module. The P1-BASE PCB became 36.3 × 52.3 mm (`INSET = 1.85` in its `tools/gen_pcb.py`: wall 1.6 +
   clearance 0.25). For the BatteryBASE this is tight along the cells: inside length 56 − 2 × 1.6 = 52.8 mm against
   44.5 mm per AAA cell leaves ≈ 4.1 mm per end for the contacts (now `CLIP_L = 4.5`); across, 3 × 11.2 mm fits the
   36.8 mm inside width. Check real clips or holders that are in stock at JLCPCB before fixing the outline.
2. **PCB pegs** moved to (36, 4), (4, 52), (36, 52) on the P1-BASE (top-left free for its LED); here they are still at
   (4, 4), (36, 4), (4, 52). Either is fine, as long as one corner is free and the PCB fits one way only.
3. **The lid fits one way only.** The P1-BASE lid has an L-shaped corner pillar (`KEY_STRIPS`, 2.5 mm longer along both
   walls) that stops a turned lid on the tray's rim at first touch; snap bumps moved to y = 16 / 40 to make room.
   The BatteryBASE lid has no corner pillars, but it needs a key too, because the polarity marks on it must match the
   cells; a solid feature, not a thin tab.
4. **Stacking:** the P1-BASE lid now has LEGO Technic holes in four corner pillars (counterbore, snap groove at 7.8 mm)
   at the CoreInk's hole positions, and its raised J1 socket (Samtec ESQ-108-24-G-D) flush with the lid. Run
   `check_fit.py` against the current P1-BASE checkout.
5. **Order timing:** the P1-BASE prototype order waits for J1 (pre-ordered, reminder on 8 December 2026). New-user
   coupons expire 14 December 2026. BatteryBASE prints, and a PCBA if ready, can join that shipment.
6. **Tooling to reuse** from the P1-BASE repository: `tools/gen_pcb.py` (placement, Freerouting, stitching that keeps
   vias out of silkscreen text), `tools/pcb_cleanup.py`, `tools/pcb_bridge_gnd.py` (GND islands: via, maze track, or
   rip-up of one net), `tools/export_fab.py` (JLCPCB CPL rotation corrections in `JLC_CORR`), `tools/checks/` and
   `enclosure/callouts.py` (renders with callouts, lid keying picture).
