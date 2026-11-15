# BatteryBASE enclosure

Generated with CadQuery by [`kuip.py`](kuip.py); the fit check is [`check_fit.py`](check_fit.py), its last result is in
[`fit-check.txt`](fit-check.txt).

```
python enclosure/kuip.py                                   # writes enclosure/fabrication/*.step / *.stl
python enclosure/check_fit.py ../needforheat-p1-base-hardware   # needs a checkout of the P1-BASE repository
python enclosure/callouts.py                                # pictures in docs/images (needs matplotlib, trimesh)
```

## What it is

* **Tray** (`battery-base-kuip`): outside exactly the CoreInk outline (40 x 56 mm, R3), walls inside it, like the
  P1-BASE v3; four LEGO-compatible posts underneath (7 mm, three crush ribs) at the CoreInk's LEGO holes; corner
  blocks that carry a 36.3 x 52.3 mm PCB 2.5 mm above the stand-on surface; three pegs at (36, 4), (4, 52), (36, 52)
  that key the PCB (as on the P1-BASE v3).
* **Sliding lid** (`battery-base-lid`), like a remote control's battery door. It slides out towards the bottom edge
  (the edge that faces down when the CoreInk hangs or stands) and clicks shut. Its tongue runs in grooves in the long
  walls and the top wall. A flexible tab (thinned, with grip ridges) carries a bump that drops into a dimple in the
  top of the bottom wall; both flanks are sloped, so a push on the ridges towards the bottom edge opens it, no
  pressing needed. The lid ends in a cap of the full CoreInk width that forms the top of the bottom wall: turned
  round, the cap leads and cannot enter between the long walls (it stops after 1 mm), so the lid fits one way only.
* **Polarity marks** are where the user looks while inserting the cells: on the PCB silkscreen under each cell (to
  do in the PCB design), and the spring is always the minus end. The lid's outside only says
  "3x AAA", with arrows at the tab for the slide direction.
* **Cell contacts** (option A of [the sketch](../docs/images/sketch-aaa-contacts.png)): MYOUNG plates standing on the
  PCB, tabs soldered in PCB slots by JLCPCB. Top: bridge MY-AAA-5214 (C5371791, + button and − spring 11.5 mm
  apart) for cells 1 and 2, + terminal MY-AAA-15-J (C51889749) for cell 3. Bottom: − terminal MY-AAA-16-J
  (C51889750) for cell 1, + plate 15-J for cell 2 and − spring 16-J for cell 3, the last two linked by a PCB track
  (a second bridge would have to be the mirror image of the 5214; it is not in the catalogue). Cell pitch 11.5 mm,
  cell axis 7.0 mm above the PCB (the bridge's contact centres), springs compressed to 3.2 mm (4.2 mm with a 43.5 mm
  cell).
* **Cradle** (`battery-base-cradle`, a third print): drops in on top of the PCB. End ribs back the contact plates
  (the spring force goes into the tray's short walls); two saddles hold the cells 1.75 mm above the PCB, so the
  electronics fit on the PCB's top side under the cells (parts up to 1.45 mm tall: single-sided assembly). The
  PCB's keep-outs, contact and cell positions are in [`pcb_constraints.json`](pcb_constraints.json).
* **Fit model** (`battery-base-fit.step`): tray, lid, cradle, contact placeholders, a PCB placeholder, three AAA cells
  and the 2x8 header.
* **Pictures** (`callouts.py`, adapted from the P1-BASE): `docs/images/enclosure-*-callouts.png` and
  `docs/images/enclosure-lid-sliding.png`.

![Lid half open](../docs/images/enclosure-lid-sliding.png)

Height: 18.9 mm above the surface it stands on (the CoreInk's back or the lid of a P1-BASE v3).

**Shipping:** modules ship loose (not stacked) in a PostNL letterbox parcel (max. 38 × 26.5 × 3.2 cm), without
cells. Each module must stay ≤ 27 mm thick from the lid top to the tips of its LEGO posts (≥ 5 mm left for box and
padding); `kuip.py` asserts this. BatteryBASE: 25.9 mm.

## Assumptions to verify

1. **Contacts** (from the MYOUNG drawings, not from parts in hand): the 5214's button and spring face the same way;
   the 4.0 mm tab of the 15-J / 16-J reaches a PCB slot with the plate 2.6 mm above the board (the drawing shows the
   tab bent 90°, the EasyEDA footprint is a 4.7 x 1.1 slot); the 15-J button stands about 1.1 mm proud, the model
   uses 0.8 (`BTN_H`); spring free lengths 7.5 ± 0.8 (5214) and 10.5 ± 1 (16-J). Ask JLCPCB whether they solder
   these tabs (THT) and order a few loose for the print check.
2. Nothing on the PCB under the cells taller than 1.45 mm; nothing under the cradle's ribs, saddles and rails.
   The bus header is a plain 2x8 male header, pins down (the BatteryBASE ends the stack: no socket on top, unlike the
   P1-BASE's stacking J1). Its tails stand 1.4 mm above the PCB top (standard 2.5 / 6.0 / 3.0 header, `HDR_TAIL`,
   VERIFY with the chosen part) under cell 3, 0.42 mm clear of it; the saddle at y = 40 has a notch over it.
3. Sliding fit and click (MJF PA12): 0.2 mm play per side (`SL_CLR`), bump 0.4 mm (`DET_H`), tab 1.3 mm thick and
   about 9.5 mm free (`TAB_T`, `TAB_L`). Estimated: about 4 N on the tab's bump, about 6 N to pull the lid open.
   Adjust after a test print.

## Printed fit check (November 2026)

Five sets of tray + lid (`fabrication/*.stl` as of 15 November 2026) go into the same JLCPCB order as the P1-BASE v3
prototype: JLC3DP, MJF PA12 black, $ 18.70 for five sets. Purpose: check the stack CoreInk – P1-BASE – BatteryBASE
in hand (LEGO posts, snap fit, header reach) before the BatteryBASE PCB is designed. If the PCB later needs other
dimensions, the enclosure is reprinted.

## Fit check (sliding lid)

`check_fit.py`, result in [`fit-check.txt`](fit-check.txt): no collisions inside the BatteryBASE, on a CoreInk or on
a P1-BASE v3 (current `feature/p1-base-v3` checkout). The lid slides out over its whole length without touching the
tray, the cradle, the contacts or the cells (the flexing tab left out), and a lid turned round stops 1 mm after entering. The header pins reach
6.0 mm into the bus socket below.

## Next: follow the P1-BASE v3 changes of 15 November 2026

Done in the sliding-lid version: points 1 (outline; clip choice still open), 2 (pegs as on the P1-BASE v3), 3 (the
lid fits one way only, by its cap) and 4 (fit check against the current P1-BASE). The original notes: What changed in the P1-BASE repository
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
