# BatteryBASE – design brief

Status: **concept, nothing designed or built yet.** This brief collects the requirements and the first technical
choices, so the design can start from them.

## 1. Goal

The NeedForHeat living-room module (M5Stack CoreInk with a CO2L/SCD41 sensor) runs on the CoreInk's internal
390 mAh LiPo battery. For some homes that gives too short a battery life, or forces measurement intervals that are
too long. The BatteryBASE is a CoreInk BASE extension that holds three AAA cells to extend the battery life.

The idea dates from the NeedForHeat DataGear backlog (2022); this repository continues it.

## 2. Requirements

1. Holds **3 × AAA** cells in a CoreInk BASE outline: 56 × 40 mm, as deep as the cells need.
2. The user can **replace the cells** without tools.
3. One design accepts both **alkaline** (1.5 V nominal) and **NiMH** rechargeable cells (1.2 V nominal, e.g. Eneloop).
4. It **powers the CoreInk**.
5. The CoreInk's internal LiPo absorbs the **current peaks** of the ESP32 (Wi-Fi), which AAA cells (alkaline in
   particular, with their high internal resistance) cannot deliver.
6. The firmware can **recognise** the BatteryBASE and **estimate the remaining energy** (state of charge, remaining
   hours), and warns the user in time to replace or recharge the cells.
7. **Stacking:** the BatteryBASE is the **end item** of a stack. It can sit directly on the CoreInk, or behind a
   NeedForHeat P1-BASE v3 (CoreInk – P1-BASE – BatteryBASE). The BatteryBASE itself is not stackable.
8. Never charges the AAA cells (alkaline must never be charged; NiMH is charged outside the device).
9. Same production approach as the P1-BASE v3: JLCPCB assembly, a 3D-printed enclosure, no soldering by the user.

## 3. Concept

### 3.1 Power path: charge the CoreInk battery, not its 5 V input

The cells do **not** power the CoreInk directly. They **charge the CoreInk's LiPo** through the `BAT` pin of the
CoreInk bus, at a low constant current; the LiPo then supplies the Wi-Fi peaks (requirement 5) and the cells only see
a small, steady load. This is the same approach as the P1 charging of the P1-BASE v3, whose charger circuit can be
reused:

```
3 × AAA (2.7–4.8 V) ──► reverse-polarity protection ──► boost to 5 V (enabled by firmware)
   ──► TP4056 linear charger, 60 mA, soft start ──► CoreInk BAT (= battery node SYS_BAT)
```

Why not the CoreInk's `5V_IN` pin, from the CoreInk schematic (M5Stack, `coreink_sch.pdf`):

* `5V_IN` (net `EXT_5VI`) feeds the CoreInk's own TP4057 charger (≈ 200 mA, R45 = 5.1 kΩ) **and**, through D9, the
  5 V boost converter of the whole system: the cells would carry the full system load including the Wi-Fi peaks.
* USB 5 V reaches `5V_IN` through D8: with USB connected, current would flow back into the cells (charging alkaline
  cells is dangerous).
* `BAT` on the bus is net `SYS_BAT`, wired straight to the battery connector and to the TP4057's `BAT` pin.

Points to work out:

* Boost converter for 2.7–4.8 V in, 5 V out, ≈ 100 mA, with true shutdown (no leakage path from input to output when
  disabled) and low quiescent current; or a charger IC that works directly from 2.7–4.8 V (buck-boost), which would
  skip the 5 V step and be more efficient.
* Efficiency: boost (≈ 90 %) × linear charger (≈ 4.0/5.0) ≈ 70 %.
* Energy: 3 × AAA alkaline ≈ 1000–1200 mAh at 4.5 → 2.7 V (≈ 4 Wh); 3 × Eneloop AAA ≈ 800 mAh at 3.6 V (≈ 2.9 Wh);
  the CoreInk LiPo ≈ 1.4 Wh. Expected battery life: roughly 2 to 3 times that of the CoreInk alone (to be confirmed
  with a measured average consumption of the living-room module).
* Reverse-polarity protection for cells inserted the wrong way (P-MOSFET ideal diode).

### 3.2 Bus pins

The BatteryBASE must not use the pins of the P1-BASE v3 (G13, G14, G25, G26, G34, G36, BAT charging is shared):

| Pin | Use |
|---|---|
| `BAT`, `GND` | charge current into the CoreInk battery |
| `G21`/`G22` (I²C) | detection and measurement: an I²C device with a fixed address on the CoreInk's internal I²C bus (shared with the RTC) |
| one free GPIO (e.g. `G18` or `G23`) | charger on/off |
| `5V_IN`, `5V_OUT`, `3V3` | not used |

The CoreInk's free ADC1 pins are taken by the P1-BASE, so the cell voltage is measured on the BatteryBASE (I²C ADC or
a current/voltage monitor), which also gives the firmware a way to recognise the BASE by its I²C address.

### 3.3 Charging together with the P1-BASE and USB

The P1-BASE (60/120 mA), the BatteryBASE (60 mA) and the CoreInk's own charger on USB (≈ 200 mA) all charge the same
390 mAh cell. The firmware coordinates them: at most one BASE charges at a time, and the total stays below ≈ 0.5 C.

### 3.4 State of charge and battery type

* Battery type from the open-circuit voltage at insertion: above ≈ 4.4 V for three cells is alkaline, below ≈ 4.2 V
  is NiMH; in between, the firmware asks once on the screen.
* Energy taken from the cells: the firmware knows how long it charged at a known current; together with the voltage
  curve of the chemistry this gives a state of charge, remaining hours, and a timely warning on the e-ink screen.

### 3.5 Mechanics

* AAA cells are 10.5 mm in diameter and 44.5 mm long: three side by side take ≈ 32 × 45 mm, inside 40 × 56 mm.
* Cells replaceable from the back; spring contacts or a 3 × AAA holder (to select from the JLCPCB library).
* Connector to the stack: a plain 2 × 8 male header (end item). Directly on the CoreInk it must reach 5–8 mm into the
  8 mm deep, flush CoreInk socket; behind a P1-BASE it plugs into the P1-BASE's stacking header.
* Enclosure generated with CadQuery, reusing `enclosure/kuip.py` of the P1-BASE v3 (corner nocks in the LEGO holes,
  PCB pegs, magnets optional).

## 4. Firmware

Support belongs in the shared library `needforheat-generic-firmware`, so every CoreInk device (living-room module,
P1 reader) gets it: detect the BatteryBASE, control its charger, estimate state of charge and remaining hours, and
show them in the status bar of the e-ink screen.

## 5. Open questions

1. Average and peak consumption of the living-room module (measure), to size the charge current and predict battery
   life.
2. Boost converter or buck-boost charger: parts in the JLCPCB library, quiescent current, shutdown behaviour.
3. Cell holder or spring contacts available at JLCPCB; contact resistance; how the user opens the enclosure.
4. Alkaline cells leaking when left in for years: advice in the manual, and a cell compartment that keeps leakage away
   from the electronics.
5. Shipping by letterbox post: without cells.

## 6. Reuse from the P1-BASE v3

From [needforheat-p1-base-hardware](https://github.com/energiegedrag-nl/needforheat-p1-base-hardware):
charger circuit with soft start (§ 4.5 of its design document), schematic generator with netlist self-check,
PCB generator with autorouting, the independent checks (`tools/checks/`), the enclosure generator and the CoreInk
measurements (outline, MI-BUS position, socket depth).
