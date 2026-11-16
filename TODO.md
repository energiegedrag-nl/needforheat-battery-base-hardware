# TODO – needforheat-battery-base-hardware

Open work for this repository. Status on 16 November 2026 (branch `feature/enclosure-slide-lid`, PR #3).

## Status

Done: enclosure (tray with a sliding lid from the top, cradle, contacts; fit check clean), charge-control circuit
with ngspice simulations, schematic (netlist check and ERC clean), footprints and 3D models, PCB placement, JLCPCB
rotation corrections (checked in the placement preview on 16 November).

16 November: the contact plates stand on the PCB (JLCPCB pushes THT parts home), so the cells now **lie on the PCB**,
packed to the left, away from the bus header's tails (cell 3's curve clears them); the left wall is thinner where
cell 1 bulges, the cradle has stops right of cell 3 instead of saddles, one peg moved to (3.6, 50.4). See
[the sketch](docs/images/sketch-aaa-contacts.png). The PCB (`pcb/needforheat-battery-base-hardware.kicad_pcb`) is
**placed again but not routed** (the earlier routing no longer fits the moved contacts).

## Soon

- [ ] <a id="route"></a>**Route the PCB.** Freerouting needs a few GB of free memory; inside Claude Code it was
  stopped twice for lack of memory. Run it from a plain PowerShell window with the other programs closed:

  ```powershell
  cd C:\dev\needforheat-battery-base-hardware
  $py  = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe"
  $cli = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe"
  $env:BBASE_JAVA_XMX = "1g"; $env:BBASE_ROUTE_TIMEOUT = "2400"
  foreach ($v in 0..5) {
      $env:BBASE_VARIANT = "$v"
      & $py tools\gen_pcb.py *> "$env:TEMP\bbase-route-$v.log"
      if (Select-String -Path "$env:TEMP\bbase-route-$v.log" -Pattern '\(0 unrouted' -Quiet) { "variant ${v}: complete"; break }
      else { "variant ${v}: not complete" }
  }
  & $py tools\pcb_cleanup.py
  & $cli pcb drc --refill-zones --save-board --schematic-parity -o "$env:TEMP\bbase-drc.rpt" pcb\needforheat-battery-base-hardware.kicad_pcb
  Select-String -Path "$env:TEMP\bbase-drc.rpt" -Pattern 'Found|violations|unconnected'
  ```

  Each variant takes 2–5 minutes; Freerouting's result differs from run to run (it once routed everything with
  variant 0, twice it left one connection open). Then: fix the DRC findings (`tools/pcb_bridge_gnd.py` for GND
  islands, as on the P1-BASE), `python tools/export_fab.py` (Gerbers, BOM, CPL, PDFs, renders, STEP), and check
  the 3D fit of the populated board against the enclosure.
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
- [ ] Order with the P1-BASE v3 prototype (JLCPCB, around 8 December 2026): PCBA, printed tray, lid and cradle
  (MJF PA12), a few loose MY-AAA-15-J / 16-J plates.
- [ ] Update the design brief (`docs/design-brief.md`, PR #1) to the design as built: plain 2x8 header pins down,
  electronics facing the CoreInk, firmware-started charging, I²C addresses 0x48 / 0x41.

## Later

- [ ] Firmware support in needforheat-generic-firmware: detect the BatteryBASE (0x48, 0x41), FORCE a charge below
  about 3.95 V, INHIBIT on USB or while a P1-BASE charges, cell voltage and remaining energy on the screen
  (docs/design.md § 4).
