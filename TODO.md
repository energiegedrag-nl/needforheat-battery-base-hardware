# TODO – needforheat-battery-base-hardware

Open work for this repository. Status on 16 November 2026: the design is complete (schematic, routed PCB,
fabrication files, enclosure; DRC and fit checks clean) on branch `feature/leaf-contacts`, not built yet. How the
design is generated and checked: [README § Developing](README.md#developing).

## Soon

- [ ] JLCPCB placement preview with **both sides**: the six MY-AAA-01 on the bottom (rotation; add a `JLC_CORR`
  entry in `tools/export_fab.py` if needed), and the DFM check of the 1.5 mm pins in the 1.6 mm board. Re-quote 5
  and 10 boards (both sides) for the cost table.
- [ ] Decide whether the vendor's 3D model of the MY-AAA-01 (`pcb/bbase.3dshapes/MYOUNG_MY-AAA-01.step`, from
  LCSC/EasyEDA, no licence stated) may stay in the repository, or is fetched locally by
  `tools/import_leaf_model.py`.
- [ ] Verify with datasheets and samples: see [docs/design.md § 7](docs/design.md#7-open-points-to-verify) (TPS3840
  open-drain output above VDD, TPS61023 shutdown current and EN, the MY-AAA-01 pin spacing and spring travel, the
  off-state current of a real board) and [enclosure/README.md](enclosure/README.md#assumptions-to-verify).
- [ ] Order with the P1-BASE v3 prototype (JLCPCB, around 8 December 2026): PCBA on both sides (5 or 10 boards; the
  cart still holds the earlier quote with the old contacts: replace it), printed tray, lid and cradle (MJF PA12; the
  $ 4.52 per set predates the leaf contacts: re-quote).
- [ ] After the print: check the leaf contacts with real cells (contact force, the leaf's top clear of the cradle's
  rib), the cradle bars (each cell must lie flat in its lane), the thin left wall, the sliding fit and click. If
  cells rattle under the lid: a strip of felt or soft foam (1–1.5 mm) on the lid's underside between the cradle's end
  ribs; no ribs under the lid (they would hit the cradle's top rib and the top wall when the lid slides out).
- [ ] Update the design brief (`docs/design-brief.md`, PR #1) to the design as built: plain 2x8 header pins down,
  electronics facing the CoreInk, firmware-started charging, I²C addresses 0x48 / 0x41, MY-AAA-01 leaf contacts.

## Later

- [ ] Firmware support in needforheat-generic-firmware: detect the BatteryBASE (0x48, 0x41), FORCE a charge below
  about 3.95 V, INHIBIT on USB or while a P1-BASE charges, cell voltage and remaining energy on the screen
  (docs/design.md § 4).
