# TODO – needforheat-battery-base-hardware

Open work for this repository. Status on 17 November 2026: the design is complete (schematic, routed PCB,
fabrication files, enclosure; DRC and fit checks clean), with the fixes from the independent review of 17 November
2026 (boost layout, pads and rule areas under the contacts' feet, fuse F1, PCA9536 power-up, latch resistors,
enclosure play) on branch `feature/review-fixes`; not built yet. How the
design is generated and checked: [README § Developing](README.md#developing).

## Soon

- [ ] Decide whether the vendor's 3D model of the MY-AAA-01 (`pcb/bbase.3dshapes/MYOUNG_MY-AAA-01.step`, from
  LCSC/EasyEDA, no licence stated) may stay in the repository, or is fetched locally by
  `tools/import_leaf_model.py`.
- [ ] Verify on the first board and with samples: see [docs/design.md § 7](docs/design.md#7-open-points-to-verify)
  (SW overshoot, a module with cells but not on a CoreInk, the MY-AAA-01 pin spacing, spring travel and solder
  joints, the off-state current, the charge current) and
  [enclosure/README.md](enclosure/README.md#assumptions-to-verify).
- [ ] Order with the P1-BASE v3 prototype (JLCPCB, around 8 December 2026). Re-quoted on 17 November 2026 with the
  review fixes: 5 boards, PCBA on both sides, LF-HASL (€ 139.93; F1 is now the Brightking SMD0805B050TF, C269104,
  because the JK-SMD0805-050 was out of stock), and one printed set (tray, lid, cradle; $ 4.57) plus the spare lid
  `battery-base-lid-loose` ($ 1.46). **Submitted on 18 November 2026, not yet paid: order W2026111819155859**
  (PCB + PCBA Y7 x5 with the assembly remark from [README § Printed Circuit Board](README.md#printed-circuit-board),
  prints: tray 5, cradle 5, lid 3, lid-loose 2, and the P1-BASE tray 5, lid 3, lid-snap050 2). In review; open
  points: the assembly remark may add a surcharge, and customs duties & taxes show $ 68.20 (checkout said $ 52.04).
  JLC3DP's thin-wall review (18 November): the BatteryBASE parts (lid tongues 0.5-0.7 mm, cradle 0.8 mm, thin left
  wall) are accepted as intended; the P1-BASE tray's 0.15 mm ledge above the snap grooves was a design error, fixed in
  the P1-BASE repo (longer lip, 0.85 mm ledge): replace those three P1-BASE files in the order. Check the DFM result
  for the 1.5 mm contact pins in the 1.6 mm board after ordering.
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
