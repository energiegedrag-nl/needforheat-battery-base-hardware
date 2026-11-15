# BatteryBASE v1.0 – design

Design rationale for the first BatteryBASE board and enclosure. Requirements: [design-brief.md](design-brief.md)
(branch `docs/design-brief`). Schematic: [needforheat-battery-base-hardware-sch.pdf](needforheat-battery-base-hardware-sch.pdf).
Enclosure: [../enclosure/README.md](../enclosure/README.md).

## 1. Architecture

```
3 x AAA ─► Q1 (reverse polarity) ─► VCELL ─► U1 TPS61023 boost (EN) ─► 4.7 V ─► U2 TP4056 60 mA ─► Q7 ─► CoreInk BAT
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
  signal by Q11, both on only while 3V3 is on; U6 only drives FET gates with 1 MΩ pull-downs.
* **Result (simulated):** 0.40 µA from the cells (two TPS3840 at 0.3 µA typ, of which one is on the cells, and the
  boost's shutdown current, 0.1 µA assumed) and 0.30 µA from the LiPo (U3); nothing into the CoreInk's 3V3 rail.

Why the firmware starts the charge: the TPS3840 has 200 mV hysteresis above 3.1 V (TI product page), so the 4.0 V
version would only release at about 4.2 V, which is a full LiPo: the latch could restart forever. No 3.9 V
detector is in stock at JLCPCB. So the threshold lives in the firmware (e.g. start below 3.95 V), and U3 at 3.5 V
(released at 3.7 V) is only a safety net for a CoreInk without BatteryBASE support.

Efficiency of a charge: boost about 90 %, linear charger 4.0 / 4.7 = 85 % (that is why the boost makes 4.7 V, not
5 V): about 77 % from the cells into the LiPo.

## 3. Simulations

[docs/simulation](simulation/README.md), `tools/sim/run_sims.py` (ngspice from KiCad 10, behavioural models of U1,
U2, U3, U4; time-compressed LiPo). Checked: firmware start with the CoreInk off afterwards; the latch rides through
an undefined ~STDBY while the TP4056 powers up (C5, 0.1 s); stop at "done" without restart; the 3.5 V safety net;
empty cells during a charge; INHIBIT; the off-state currents and back-feeding.

A finding from the simulation: if the CoreInk's average load reached the TP4056's termination current (C/10 =
6 mA), "done" would never come. The CoreInk sleeps at microamperes, so this does not happen in practice; the firmware
can still use INHIBIT as a time-out.

## 4. Firmware interface

| What | How |
|---|---|
| Detect the BatteryBASE | ADS1115 answers at 0x48 and PCA9536 at 0x41 (I²C on G21/G22, shared with the RTC at 0x51; the P1-BASE uses 0x62 and its all-call 0x70) |
| Cell voltage | ADS1115 AIN0 = VCELL / 2 (100k/100k), FSR ±4.096 V |
| Charging and its current | ADS1115 AIN1 = TP4056 PROG: 1.0 V = 60 mA, 0 V = not charging |
| Start a charge | PCA9536 IO1 (FORCE) high for ≥ 1 ms, then low |
| Keep charging off while awake | PCA9536 IO0 (INHIBIT) high; released automatically when the CoreInk switches off |

Firmware tasks (needforheat-generic-firmware): at each wake-up read the LiPo voltage (the CoreInk's own ADC) and the
cell voltage; if the LiPo is below about 3.95 V and the cells are above about 3.0 V, give a FORCE pulse; set
INHIBIT while the CoreInk is on USB, or while a P1-BASE charges (at most one charger at a time, design brief § 3.3);
count the charges (each tops up about 40 mAh, from 3.95 to 4.2 V) and estimate the remaining energy from the cell
voltage at rest.

## 5. PCB

* 36.3 x 52.3 mm, 2 layers, inside the CoreInk outline like the P1-BASE v3 (`INSET` 1.85 mm).
* **Top side (KiCad F) = electronics**, facing the CoreInk or the P1-BASE in the 2.5 mm under the board (parts up to
  2.2 mm): single-sided SMD assembly. The tray's corner blocks (7 x 7 mm) are on this side too.
* **Bottom side (KiCad B) = cells**: the six contact plates (THT, tabs soldered on the top side by JLCPCB, listed as
  "Wave Soldering, Economic and Standard PCBA"), the bus header's tails, and per cell an outline with + and - on the
  silkscreen, where the user looks while inserting the cells.
* Coordinates: the enclosure frame is seen from the back; the PCB from its top side, i.e. from the CoreInk:
  x_pcb = 40 - x_enclosure. `tools/gen_pcb.py` reads the contact and cell positions from
  `enclosure/pcb_constraints.json`.
* Bus header: XKB X6521WV-2x08H-C60D30 (C706898), 2.5 mm plastic, 6.0 mm pins, 3.0 mm tails (1.4 mm proud on the
  cell side; the cells lie 1.6 mm up for it). The SMD version does not fit: its feet reach past the board edge.

## 6. Parts (JLCPCB, 15 November 2026)

| Ref | Part | LCSC | Stock |
|---|---|---|---:|
| U1 | TPS61023DRLR | C919459 | 3 778 |
| U2 | TP4056 | C16581 | (P1-BASE part) |
| U3 / U4 | TPS3840DL35 / TPS3840DL28 | C2866251 / C2066416 | 188 / 573 |
| U5 | ADS1115IDGSR | C37593 | 12 546 |
| U6 | PCA9536DGKR | C2649389 | 2 044 |
| L1 | Sunlord SWPA3015S1R0NT, 1 µH, 3 x 3 x 1.5 mm | C43388 | 5 638 |
| BC1, BC4, BC6 | MYOUNG MY-AAA-15-J (+ plate) | C51889749 | 907 |
| BC2, BC3, BC5 | MYOUNG MY-AAA-16-J (- spring) | C51889750 | 805 |
| J1 | XKB X6521WV-2x08H-C60D30 | C706898 | 319 |
| Q1, Q2, Q6, Q7, Q9 / Q3–Q5, Q8, Q10, Q11 | AO3401A / 2N7002 (basic) | C15127 / C8545 | |
| R, C | 0603/0805 basic parts (10M C7250, 470k C23178, ...) | | |

## 7. Open points to verify

1. TPS3840 hysteresis and the open-drain output pulled above its VDD (U3's ~RESET sits at up to VCELL through R10,
   while its VDD is the LiPo): check in the datasheet (TI SNVSB03).
2. TPS61023: shutdown current, EN threshold and any internal EN pull-down (the latch drives EN through 10 kΩ).
3. MYOUNG MY-AAA-15-J/16-J tab: straight through a 4.7 x 1.1 mm slot, as assumed? Order loose samples; check the
   contact pressure with real cells (spring compressed to 3.2–4.2 mm).
4. JLCPCB placement preview of every part (rotation corrections in `tools/export_fab.py`, `JLC_CORR`), especially the
   new packages (SOT-563, MSOP-10, VSSOP-8, the inductor, the header) and the bottom-side contacts.
5. Measure the off-state current of an assembled board (expected < 1 µA in total).
