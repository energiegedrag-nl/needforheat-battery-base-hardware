# TODO – needforheat-battery-base-hardware

Open work for this repository. Status on 16 November 2026 (branch `feature/enclosure-slide-lid`, PR #3).

## Status

Done: enclosure (tray with a sliding lid from the top, cradle, contacts; fit check clean), charge-control circuit
with ngspice simulations, schematic (netlist check and ERC clean), footprints and 3D models, **PCB routed** (DRC
clean, 0 unconnected), fabrication files in `pcb/jlcpcb/` checked in the JLCPCB preview, cost table in the README.

16 November: the contact plates stand on the PCB (JLCPCB pushes THT parts home), so the cells now **lie on the PCB**,
packed to the left, away from the bus header's tails (cell 3's curve clears them); the left wall is thinner where
cell 1 bulges, the cradle has stops right of cell 3 instead of saddles, one peg moved to (3.6, 50.4). The cradle got
two low bars between the cells (stiffer; each cell rolls in its own lane). See
[the sketch](docs/images/sketch-aaa-contacts.png). BatteryBASE PCBA, 5 pieces, is in the JLCPCB cart (not ordered).

## Soon

- [x] Route the PCB (Freerouting, outside Claude Code: `tools/gen_pcb.py` with `BBASE_VARIANT` 0–5, then
  `tools/pcb_cleanup.py`, `tools/pcb_bridge_gnd.py`, DRC with `kicad-cli pcb drc --refill-zones --save-board
  --schematic-parity`, `tools/export_fab.py`). Done 16 November; the /SW track around U1 pin 4 was rerouted by hand.
  Rerouting after a change: same steps; Freerouting needs a few GB of memory and differs from run to run.
- [x] Check every part in the JLCPCB placement preview (`JLC_CORR` / `JLC_CORR_VALUE` in `tools/export_fab.py`):
  all 19 top-side parts checked on 16 November (SOT-563 +180, MSOP-10 and VSSOP-8 +270, TPS3840DL28 +270).
  The six contacts were not in that preview (top-side assembly only).
- [ ] **MYOUNG contacts: tab straight or bent?** The drawings show the 4.0 mm tab bent 90° ("L-type"); the design
  assumes it goes straight through the slot with the plate standing on the PCB, trimmed to 1.6 mm underneath. Order a
  few loose (also to try 3 x AAA in a printed tray); if the tab is bent, another footprint or part is needed. For the
  prototype, consider leaving the contacts out of the PCBA and soldering them by hand.
- [ ] Verify with datasheets and samples: see [docs/design.md § 7](docs/design.md#7-open-points-to-verify) (TPS3840
  open-drain output above VDD, TPS61023 shutdown current and EN, the MYOUNG plates' tabs, the off-state current of a
  real board) and [enclosure/README.md](enclosure/README.md#assumptions-to-verify).
- [ ] Order with the P1-BASE v3 prototype (JLCPCB, around 8 December 2026): PCBA (5 pieces in the cart, € 93.07),
  printed tray, lid and cradle (MJF PA12, $ 4.52 per set, quote with the cradle bars), a few loose MY-AAA-15-J / 16-J
  plates. The contacts are soldered by hand on the prototype.
- [ ] After the print: check the cradle bars against real cells (each cell must lie flat in its lane), the thin left
  wall, the sliding fit and click. If cells rattle under the lid: a strip of felt or soft foam (1–1.5 mm) on the
  lid's underside between the cradle's end ribs; no ribs under the lid (they would hit the cradle's top rib and the
  top wall when the lid slides out).
- [ ] Update the design brief (`docs/design-brief.md`, PR #1) to the design as built: plain 2x8 header pins down,
  electronics facing the CoreInk, firmware-started charging, I²C addresses 0x48 / 0x41.

## Later

- [ ] Firmware support in needforheat-generic-firmware: detect the BatteryBASE (0x48, 0x41), FORCE a charge below
  about 3.95 V, INHIBIT on USB or while a P1-BASE charges, cell voltage and remaining energy on the screen
  (docs/design.md § 4).
