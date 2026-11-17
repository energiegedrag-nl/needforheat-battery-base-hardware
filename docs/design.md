# BatteryBASE v1.0 – design

Design rationale for the first BatteryBASE board and enclosure. Requirements: [design-brief.md](design-brief.md)
(branch `docs/design-brief`). Schematic: [needforheat-battery-base-hardware-sch.pdf](needforheat-battery-base-hardware-sch.pdf).
Enclosure: [../enclosure/README.md](../enclosure/README.md).

## 1. Architecture

```
3 x AAA ─► F1 (PTC) ─► Q1 (reverse polarity) ─► VCELL ─► U1 TPS61023 boost (EN) ─► 4.7 V ─► U2 TP4056 60 mA ─► Q7 ─► CoreInk BAT
                                                     ▲                                  │ ~STDBY
                                   charge latch ─────┘◄─────────────────────────────────┘
                 set: FORCE pulse (firmware, via U6) or U3 (LiPo < 3.5 V)
                 reset: ~STDBY (done), INHIBIT (firmware, via U6), U4 (cells < 2.8 V)

CoreInk 3V3 ─► U5 ADS1115 (cell voltage, charge current) + U6 PCA9536 (FORCE, INHIBIT)   [only while the CoreInk is on]
```

The cells never power the CoreInk directly: they charge its LiPo at 60 mA, and the LiPo supplies the Wi-Fi peaks
(design brief § 3.1).

## 2. Energy efficiency: everything off between charges

The living-room firmware switches the CoreInk off completely between measurements; then only its RTC draws about
0.6 µA. The BatteryBASE must not spoil that:

* **The charger runs on its own.** A charge must continue while the CoreInk is off (it is awake only seconds at a
  time). A latch of four small MOSFETs (Q2–Q6) switches the boost on and keeps it on; it draws nothing itself
  (only FET gates). It is set by a FORCE pulse from the firmware, or by U3 (TPS3840DL35) when the LiPo falls below
  3.5 V; it is reset when the TP4056 reports "done" (~STDBY), when the firmware asserts INHIBIT, or when U4
  (TPS3840DL28) sees the cells below 2.8 V.
* **Off means off.** U1 TPS61023 has a load disconnect: in shutdown no path from the cells to its output. Q7/Q8 cut
  the TP4056 off from the LiPo, so the LiPo does not leak into the unpowered charger (up to 2 µA otherwise).
* **The firmware interface is powered from the CoreInk's 3V3 only.** U5 and U6 draw nothing while the CoreInk is
  off, and none of their pins can feed the unpowered CoreInk: the cell divider is switched by Q9/Q10 and the PROG
  signal by Q11 (behind R24, 100 kΩ, which also keeps the switch and its track off the charger's PROG node), both
  on only while 3V3 is on; U6 only drives FET gates.
* **The PCA9536 powers up with pull-ups.** Until the firmware has configured it, its pins are inputs with internal
  pull-ups (about 100 kΩ, TI SCPS125). The pull-downs on FORCE and INHIBIT (R15, R16) are therefore 4.7 kΩ: they keep
  both gates below 0.5 V, under the 2N7002's threshold, so a wake-up of the CoreInk neither starts nor stops a
  charge (simulated, case 5; with 1 MΩ a running charge stopped at every wake-up). The firmware must write the output
  register (0) before it makes the pins outputs: the register powers up as 1.
* **No 10 MΩ nodes.** The latch's high-impedance nodes are 1 MΩ (R10 on Q2's gate, R12 on EN, R19 on Q6's gate) and
  R18 is 470 kΩ. At 10 MΩ a few tens of nA (U3's open-drain leakage is specified up to 90 nA, flux residue, moisture)
  could set the latch or switch the boost on (EN's low threshold is 0.35 V). These resistors carry current only while
  charging, or (R19) when the cells are empty. R12 also lets EN fall within 0.2 s after Q2 switches off.
* **Result (simulated):** 0.40 µA from the cells (two TPS3840 at 0.3 µA typ, of which one is on the cells, and the
  boost's shutdown current, 0.1 µA typ) and 0.30 µA from the LiPo (U3); nothing into the CoreInk's 3V3 rail. With
  empty cells (below 2.8 V) 3.1 µA from the cells: U4 pulls R19 low.

Why the firmware starts the charge: the TPS3840 has 200 mV hysteresis from 3.1 V up (100 mV below: U4, the DL28,
releases at 2.9 V; TI SNVSB03), so the 4.0 V
version would only release at about 4.2 V, which is a full LiPo: the latch could restart forever. No 3.9 V
detector is in stock at JLCPCB. So the threshold lives in the firmware (e.g. start below 3.95 V), and U3 at 3.5 V
(released at 3.7 V) is only a safety net for a CoreInk without BatteryBASE support.

Efficiency of a charge: boost about 90 %, linear charger 4.0 / 4.7 = 85 % (that is why the boost makes 4.7 V, not
5 V): about 77 % from the cells into the LiPo.

## 3. Simulations

[docs/simulation](simulation/README.md), `tools/sim/run_sims.py` (ngspice from KiCad 10, behavioural models of U1,
U2, U3, U4; time-compressed LiPo). Checked: firmware start with the CoreInk off afterwards; the latch rides through
an undefined ~STDBY while the TP4056 powers up (C5, 0.1 s); stop at "done" without restart; the 3.5 V safety net;
empty cells during a charge; INHIBIT; a wake-up of the CoreInk during a charge with the PCA9536 still
unconfigured (pull-ups); the weakest FORCE pulse (300 ms, cells at 3.1 V, Q3 at the top of its threshold range,
2.5 V); the off-state currents and back-feeding. The boost switches on above 1.2 V on EN and off below 0.4 V.

A finding from the simulation: if the CoreInk's average load reached the TP4056's termination current (C/10 =
6 mA), "done" would never come. The CoreInk sleeps at microamperes, so this does not happen in practice; the firmware
can still use INHIBIT as a time-out.

## 4. Firmware interface

| What | How |
|---|---|
| Detect the BatteryBASE | ADS1115 answers at 0x48 and PCA9536 at 0x41 (I²C on G21/G22, shared with the RTC at 0x51; the P1-BASE uses 0x62 and its all-call 0x70) |
| Cell voltage | ADS1115 AIN0 = VCELL / 2 (100k/100k), FSR ±4.096 V |
| Charging and its current | ADS1115 AIN1 = TP4056 PROG x R23 / (R23 + R24) = 0.91 x PROG: 0.91 V = 60 mA, 0 V = not charging (an indication: Q11 has only 2.3 V of gate drive) |
| Set up | PCA9536: write the output register (0x01) = 0 first, then the configuration register (0x03): IO0 and IO1 outputs |
| Start a charge | PCA9536 IO1 (FORCE) high for ≥ 300 ms, then low (the latch holds once C5 has charged through R13) |
| Stop a charge, keep charging off while awake | PCA9536 IO0 (INHIBIT) high (≥ 300 ms to stop a running charge); released automatically when the CoreInk switches off |

Firmware tasks (needforheat-generic-firmware): at each wake-up read the LiPo voltage (the CoreInk's own ADC) and the
cell voltage; if the LiPo is below about 3.95 V and the cells are above about 3.0 V, give a FORCE pulse; set
INHIBIT while the CoreInk is on USB, or while a P1-BASE charges (at most one charger at a time, design brief § 3.3);
count the charges (each tops up about 40 mAh, from 3.95 to 4.2 V) and estimate the remaining energy from the cell
voltage at rest.

## 5. PCB

* 36.3 x 52.3 mm, 2 layers, inside the CoreInk outline like the P1-BASE v3 (`INSET` 1.85 mm).
* **Top side (KiCad F) = electronics**, facing the CoreInk or the P1-BASE in the 2.5 mm under the board (parts up to
  2.2 mm): SMD assembly. The tray's corner blocks (7 x 7 mm) are on this side too, and the contacts' pins are
  soldered from this side (Ø2.2 pads).
* **Boost layout**: placed by hand as in TI's layout example (`BOOST` in `tools/gen_pcb.py`): C2 sits right at
  VOUT and GND and straddles the 2.4 mm SW track from pin 5 to L1 (turned so that its SW pad faces U1), C1 at VIN
  and GND, R1/R2 at FB on the side away from SW, two GND vias next to the capacitors. These tracks are laid by the
  script and locked before routing.
* **Under the contacts' feet**: the pads cover every place where a foot touches the board (the tab behind the leaf
  and the inner end), as in the vendor's layout; around each foot (+ 0.3 mm) a rule area on the cell side keeps all
  other copper out (no tracks, vias or GND pour). The stamped steel foot moves a little with every cell and must not
  rest on solder mask over another net. F1 (resettable fuse, 0.5 A hold) right at the stack's + (BC6) covers the
  rest of the board.
* Power tracks 0.35 mm (`Power` net class; 0.5 mm did not route between the small pads), the boost's pins by hand. Surface finish LF-HASL (better wetting than OSP
  for the contacts' pins, which are soldered after two reflow passes).
* **Bottom side (KiCad B) = cells**: the six MY-AAA-01 leaf contacts (THT, two pins each, a copper pad under each end
  of the foot; JLCPCB assembles both sides, Standard PCBA), the bus header's tails, and per cell a small battery with
  + and - on the silkscreen between the contacts' feet, where the user looks while inserting the cells.
* Coordinates: the enclosure frame is seen from the back; the PCB from its top side, i.e. from the CoreInk:
  x_pcb = 40 - x_enclosure. `tools/gen_pcb.py` reads the contact and cell positions from
  `enclosure/pcb_constraints.json`.
* Bus header: XKB X6521WV-2x08H-C60D30 (C706898), 2.5 mm plastic, 6.0 mm pins, 3.0 mm tails (1.4 mm proud on the
  cell side; cell 3's curve clears them). The SMD version does not fit: its feet reach past the board edge.

## 6. Parts (JLCPCB, 15 November 2026)

| Ref | Part | LCSC | Stock |
|---|---|---|---:|
| U1 | TPS61023DRLR | C919459 | 3 778 |
| U2 | TP4056 | C16581 | (P1-BASE part) |
| U3 / U4 | TPS3840DL35 / TPS3840DL28 | C2866251 / C2066416 | 188 / 573 |
| U5 | ADS1115IDGSR | C37593 | 12 546 |
| U6 | PCA9536DGKR | C2649389 | 2 044 |
| L1 | Sunlord SWPA3015S1R0NT, 1 µH, 3 x 3 x 1.5 mm | C43388 | 5 638 |
| BC1–BC6 | MYOUNG MY-AAA-01 leaf contact (same part at both ends) | C964855 | 1 231 |
| F1 | Brightking SMD0805B050TF, resettable fuse 0.5 A hold / 1 A trip, 6 V, 0805 | C269104 | |
| J1 | XKB X6521WV-2x08H-C60D30 | C706898 | 319 |
| Q1, Q2, Q6, Q7, Q9 / Q3–Q5, Q8, Q10, Q11 | AO3401A / 2N7002 (basic) | C15127 / C8545 | |
| R, C | 0603/0805 basic parts (4.7k C23162, 470k C23178, 1M C22935, ...) | | |

## 7. Open points to verify

Checked in the datasheets (review of 17 November 2026): the TPS3840's open-drain output may be pulled up to 10 V
independent of its VDD (U3's ~RESET sits at up to VCELL while its VDD is the LiPo); hysteresis 100 mV below 3.1 V,
200 mV above. TPS61023: shutdown current 0.1 µA typ / 0.2 µA max, EN thresholds 0.35 ... 1.2 V, no internal EN
pull-down specified. PCA9536: I/Os are inputs with pull-ups at power-up (handled, § 2).

1. The boost's SW node and VOUT on the first board (scope): overshoot well under the 7 V (SW 8 V for 10 ns) rating.
2. A BatteryBASE with cells but not on a CoreInk: VLIPO is then only C4 and C6, discharged by leakage; when it passes
   3.5 V, U3 sets the latch, the charger tops up the capacitors, "done" follows, and so on. Measure how often this
   repeats and the average current from the cells (scope on EN). If it matters: note "take the cells out of a
   BatteryBASE that is not on a CoreInk", or an interlock in a later revision.
3. MYOUNG MY-AAA-01: shape measured from the vendor's 3D model; outer pins 45.0 mm apart (the layout's 42.4 mm
   read as the outer pads' inner edges); the 1.5 mm pins end just inside the 1.6 mm PCB (JLCPCB's DFM check). Check
   the contact pressure with real cells (each leaf gives way 0.6–1.3 mm). (The earlier MY-AAA-15-J/16-J plates have their tab bent 90°: they would lie flat.)
4. JLCPCB placement preview of every part (rotation corrections in `tools/export_fab.py`, `JLC_CORR`), especially the
   new packages (SOT-563, MSOP-10, VSSOP-8, the inductor, the header) and the bottom-side contacts.
5. Measure the off-state current of an assembled board (expected < 1 µA in total).
6. The charge current (60 mA with R3 = 20 kΩ, outside the TP4056 datasheet's table of 1.2–10 kΩ but common) and
   AIN1 against a multimeter on TP4 (PROGM, behind R24).
7. The contacts' solder joints: JLCPCB solders the pins from the electronics side; check that the solder reaches the
   pads on the cell side (order remark), and the contacts' hold with a cell pressed in.
