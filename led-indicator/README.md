# RGBW Indicator Board — LED Indicator

KiCad 8 schematic for a 12-LED addressable RGBW indicator panel. Replaces incandescent bulbs in a rear-projection indicator display. Target: ~2×3 inch, 2-layer, JLCPCB fabrication + assembly.

## Bill of Materials

| Ref | Qty | Value / Description | Package | JLCPCB Part | Notes |
|-----|-----|---------------------|---------|-------------|-------|
| D1–D12 | 12 | SK6812 RGBW addressable LED | 5050 SMD (5.0×5.0mm) | C2890364 (SK6812-EC15) | Assign footprint `LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm` |
| C1–C12 | 12 | 100nF ceramic capacitor | 0603 SMD | C14663 | Per-LED decoupling, place close to each LED |
| C13 | 1 | 1000µF 10V electrolytic | Radial 8mm dia, 3.5mm pitch | C6185 (100µF) or C6971 (1000µF SMD) | Bulk input decoupling; check JLCPCB Basic parts at order time |
| R1 | 1 | 330Ω resistor | 0603 SMD | C23138 | Data line series resistor (DIN protection) |
| U1 | 1 | 74AHCT125 quad 3-state buffer | SOIC-14 | C7084 | 3.3V→5V level shifter; Basic part |
| J1 | 1 | DC barrel jack 2.1mm×5.5mm, center-positive | Through-hole | — | PJ-102AH or equivalent; assign footprint manually |
| J2 | 1 | JST-XH 3-pin header (5V, GND, DATA) | Through-hole, 2.5mm pitch | C2681542 | Pin 1=5V (via SJ1), Pin 2=GND, Pin 3=DATA |
| SJ1 | 1 | Solder jumper, 2-pin, normally OPEN | — | — | Isolates J2 5V pin from main rail; close to back-power from controller |

## Schematic Notes

**Daisy-chain direction:** DATA_IN → R1 → D1.DIN → D1.DOUT → D2.DIN → … → D12.DOUT (leave D12.DOUT unconnected or add test point)

**330Ω resistor (R1):** Limits current transients and protects against transmission-line reflections on the data line. Place between U1 output and D1.DIN.

**Solder jumper SJ1:** Normally open. Connects the 5V pin on J2 to the main +5V rail. Close only when powering the board from the controller side (low-power testing). Leave open when using the barrel jack (J1) to avoid fighting two supplies.

**74AHCT125 (U1):**
- Channel 1 (pins 1/2/3): active — ~OE tied to GND (pin 1), A=DATA_IN (pin 2), Y=data out to R1 (pin 3)
- Channels 2–4: disabled — ~OE pins (4, 10, 13) tied to +5V; A inputs (5, 9, 12) tied to GND; Y outputs (6, 8, 11) no-connect

## Footprints to Assign Before PCB Layout

| Ref | Footprint |
|-----|-----------|
| D1–D12 | `LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm` *(already set)* |
| J1 | `Connector_BarrelJack:BarrelJack_Horizontal_PJ-102AH` or similar 2.1mm barrel |
| SJ1 | `Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm` |
| C13 | Verify package matches the part ordered (radial THT or SMD) |

## Power Budget (rough)

SK6812 at full white: ~60mA per LED × 12 = 720mA + 5V logic overhead. Use a ≥1A 5V supply on J1. The 1000µF bulk cap (C13) handles the high-frequency current draw of the WS2812-protocol burst updates.
