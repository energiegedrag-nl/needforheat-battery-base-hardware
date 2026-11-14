# NeedForHeat BatteryBASE

Open hardware for the **NeedForHeat BatteryBASE**: an extension for the M5Stack CoreInk that holds three AAA cells
(alkaline or NiMH rechargeable) to extend the battery life of the NeedForHeat living-room module.

**Status: concept.** Nothing has been designed or built yet; the requirements and first technical choices are in
[docs/design-brief.md](./docs/design-brief.md).

## Table of contents
* [General info](#general-info)
* [Producing](#producing)
* [Developing](#developing)
* [Status](#status)
* [License](#license)
* [Credits](#credits)

## General info

The cells do not power the CoreInk directly: they charge the CoreInk's internal LiPo battery at a low, constant
current through the `BAT` pin of the CoreInk bus. The LiPo supplies the current peaks of Wi-Fi, which AAA cells
cannot deliver. The firmware recognises the BatteryBASE, estimates the remaining energy and warns in time to replace
or recharge the cells.

The BatteryBASE is the end item of a stack: it fits directly on a CoreInk, or behind a
[NeedForHeat P1-BASE v3](https://github.com/energiegedrag-nl/needforheat-p1-base-hardware).

Firmware support is planned in [needforheat-generic-firmware](https://github.com/energiegedrag-nl/needforheat-generic-firmware),
the shared library of the NeedForHeat device firmware.

## Producing

Not available yet. The design will follow the P1-BASE v3: a PCB assembled by JLCPCB (files in `pcb/jlcpcb`) and a
3D-printed enclosure (files in `enclosure/fabrication`).

## Developing

The design will be generated with scripts, like the P1-BASE v3: KiCad schematic and PCB, autorouting with
Freerouting, independent checks, and a parametric CadQuery enclosure.

## Status

Project is _in progress_ (concept).

## License

The hardware designs in this repository are available under the [CERN-OHL-P v2 license](./LICENSE),
Copyright 2026 Henri ter Hofte.

## Credits

Designed by:
* Henri ter Hofte · [@henriterhofte](https://github.com/henriterhofte)

The BatteryBASE builds on the NeedForHeat P1-BASE and other NeedForHeat hardware, originally developed by the
Research group Energy Transition of Windesheim University of Applied Sciences.

### AI assistance

Parts of this repository were made with [Claude Code](https://claude.com/claude-code) (Anthropic), under the author's
direction and review. Commits made this way carry a `Co-Authored-By:` trailer. The author remains responsible for all
content.
