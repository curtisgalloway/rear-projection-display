I need you to generate a KiCad 8 schematic for an addressable RGBW LED indicator board. Please create the project files (.kicad_pro, .kicad_sch, and an empty .kicad_pcb) in a new directory called `led-indicator`.

## Project overview
This board replaces incandescent bulbs in a rear-projection indicator panel. It has 12 addressable RGBW LEDs in fixed physical positions (I'll set the actual positions during PCB layout — for the schematic, just place them in a logical grid). Board target size is ~2x3 inches, 2-layer, for fabrication and assembly at JLCPCB.

## Components

**LEDs**: 12x SK6812 RGBW in 5050 SMT package, daisy-chained
- VCC, GND, Data In, Data Out pads
- One LED's DOUT connects to the next LED's DIN

**Per-LED decoupling**: 0.1µF ceramic capacitor (0603 SMT) across VCC/GND of each LED, placed close to each LED

**Bulk decoupling**: 1x 1000µF electrolytic capacitor across the 5V input rail (through-hole or SMT, your choice — pick what's in JLCPCB's Basic parts library if you can)

**Data line protection**: 330Ω resistor (0603 SMT) inline between the data input connector and the first LED's DIN

**Level shifter**: 74AHCT125 (SOIC-14) to shift 3.3V data from a Raspberry Pi or 3.3V MCU up to 5V logic level for the first LED. Use one of the four channels; tie the other three /OE pins high (disable). Power the level shifter from 5V.

**Connectors**:
- Power input: barrel jack, 2.1mm x 5.5mm, center-positive, through-hole (e.g., PJ-102AH or similar)
- Data + GND input: 3-pin JST-XH header, through-hole, 2.5mm pitch (5V, GND, DATA from controller). Even though power is on a separate connector, include 5V on this header too so it can optionally power from the controller side for low-power testing — but make this 5V pin connectable via a solder jumper (SJ) that defaults to OPEN, so the two power sources are isolated unless the user closes the jumper.

## Schematic requirements

- Use the standard KiCad symbol libraries where possible. For the SK6812, if there's no built-in symbol, create a simple 4-pin symbol (VCC, GND, DIN, DOUT) and note that I'll need to assign a footprint manually.
- Group the 12 LEDs visually so the daisy-chain flow is obvious. Show DOUT of LED1 → DIN of LED2 → ... → DOUT of LED12 left dangling (or to a test point).
- Add power flags (+5V, GND) and net labels for clarity rather than running wires across the whole sheet.
- Add a title block: title "RGBW Indicator Board", revision A, my initials as designer, today's date.
- Include a few comment text blocks on the schematic explaining: the daisy chain direction, the purpose of the 330Ω data resistor, and the solder jumper behavior.

## Deliverables

1. The KiCad project files in `led-indicator/`
2. A short README.md in the same directory listing the BOM with quantities, JLCPCB Basic part suggestions where you know them, and any footprints I'll need to assign manually before PCB layout
3. Run ERC (electrical rules check) and report any warnings/errors — fix anything that's a real issue, explain anything that's a false positive

After you generate the files, summarize what you built and what decisions you made (e.g., which library symbols you used, any assumptions about pin assignments).
