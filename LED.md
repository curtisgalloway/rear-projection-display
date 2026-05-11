* URL: https://www.amazon.com/dp/B01CI6EWHK?th=1
* Overview: Tricolor Red(R) Green(G) Blue(B) Common Cathode(CC), R:620nm-625nm / G:515nm-520nm / B:450nm-455nm, Luminous Intensity(Brightness): R:1000-2000mcd / G:4000-5000mcd / B:3000-4000mcd, Viewing Angle: 20 Degrees,Super Bright
* * * * * * * * * Parameters : DC 2V-2.2V(R) 3V-3.2V (G/B) Volt 20mA, Polarity (2 V) : Cathode "-" (Longer Leg) | Anode "+" (Shorter Leg),Foggy Round Small Lens
* Shipping Weight: 2.84oz / 0.08kg, Package: Pack of 50 Pieces Leddiode(Through Hole DIP 4pins leads mini LEDs Set) Three Colour
* Compatible with: DIY PCB Board Circuit, Arduino, Raspberry Pi, Hobby, Science Experiments, Throwies Project, Breadboard, Bulb, Bulk Parts Replacement
* Micro 10 mm Diameter, 4pin 4 pin, Tiny Bright Light, Low Voltage & Low Power Consumption, 2.2v 2.5v 3.2v 3.3v

## Dimensional Analysis (from manufacturer datasheet image)

### Body
| Parameter | Value |
|-----------|-------|
| Lens diameter | 10.0 mm |
| Flange/rim diameter | 10.8 mm |
| Dome height | 11.65 mm |
| Base collar height | 2.0 mm |

### Pins
| Parameter | Value |
|-----------|-------|
| Number of pins | 4 |
| Pin pitch (center-to-center) | **1.0 mm** |
| Total pin span (outer-to-outer) | 3.0 mm |
| Pin wire diameter | ~0.5 mm |
| R pin length (longest, key pin) | 28.0 mm |
| G/B pin length | ~26.5 mm |
| K pin length | ~25.5 mm |

### Pin Order (left to right, flat side of LED facing you)
```
Pin 1   Pin 2   Pin 3   Pin 4
  R       K       G       B
 (+)     (-)     (+)     (+)
longest  short  medium  medium
```
- **R** = Red anode (longest pin — orientation key)
- **K** = Common cathode
- **G** = Green anode
- **B** = Blue anode

### KiCAD Footprint Parameters
- Drill hole diameter: **0.8 mm** (0.5 mm wire + 0.15 mm clearance each side)
- Pad outer diameter: **1.0 mm** (maximum for non-overlapping at 1.0 mm pitch)
- Pad shape: circular through-hole
- Silkscreen body circle: 10.0 mm diameter
- Cathode (K) marking: square pad on pin 2, or notch on silkscreen ring
- Footprint origin: center of 4-pad array (between pins 2 and 3), coincident with LED body center

> **Note:** The product listing text says "Cathode = Longer Leg" but the manufacturer's own datasheet image shows ⊕ (R anode) at the leftmost/longest pin position. Verify pin identity with a multimeter (continuity or diode-test mode) before soldering. The R anode is the standard "key pin" for orientation on RGB LEDs from this manufacturer.

