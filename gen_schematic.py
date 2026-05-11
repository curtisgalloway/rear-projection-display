#!/usr/bin/env python3
"""Generate KiCAD schematic for rear-projection display LED board.

Coordinate convention:
  Symbol files (.kicad_sym) use y-up (positive y = up on screen).
  Schematic files (.kicad_sch) use y-down (positive y = down on screen).
  When placing a symbol at (sx, sy) with rotation 0, a pin at symbol
  position (px, py) connects at schematic point (sx+px, sy-py).
"""

import os
import uuid

KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
PROJ_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rear-projection-display")
SNAPMAGIC_SYM = f"{PROJ_DIR}/IS31FL3236A-QFLS2-TR.kicad_sym"
OUTPUT_SCH = f"{PROJ_DIR}/rear-projection-display.kicad_sch"

STUB = 2.54


def extract_symbol(filepath, symbol_name, embed_as=None):
    """Extract symbol block and optionally rename it for embedding in lib_symbols.

    embed_as: if given, rename all occurrences of the symbol name (including
    sub-symbol names like symbol_name_0_1 → embed_as_0_1) so that KiCAD can
    match the embedded definition to the instance's lib_id.
    """
    with open(filepath) as f:
        content = f.read()
    for prefix in [f"\t(symbol \"{symbol_name}\"", f"  (symbol \"{symbol_name}\""]:
        start = content.find(prefix)
        if start != -1:
            break
    if start == -1:
        raise ValueError(f"Symbol '{symbol_name}' not found in {filepath}")
    depth = 0
    i = start
    while i < len(content):
        if content[i] == "(":
            depth += 1
        elif content[i] == ")":
            depth -= 1
            if depth == 0:
                block = content[start : i + 1]
                if embed_as and embed_as != symbol_name:
                    block = block.replace(
                        f'(symbol "{symbol_name}"',
                        f'(symbol "{embed_as}"',
                        1,
                    )
                return block
        i += 1
    raise ValueError(f"Unmatched parens for '{symbol_name}'")


_uuid_counter = 0


def new_uuid():
    global _uuid_counter
    _uuid_counter += 1
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"rpd-{_uuid_counter}"))


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


# ---------------------------------------------------------------------------
# Schematic element generators
# ---------------------------------------------------------------------------


def sym_instance(lib_id, ref, value, sx, sy, angle=0, footprint="", extra="", pins=None):
    pins_str = ("\n" + pin_uuids(pins)) if pins else ""
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {fmt(sx)} {fmt(sy)} {angle})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{new_uuid()}")
\t\t(property "Reference" "{ref}" (at {fmt(sx + 2.54)} {fmt(sy - 2.54)} 0)
\t\t\t(effects (font (size 1.27 1.27))))
\t\t(property "Value" "{value}" (at {fmt(sx + 2.54)} {fmt(sy + 2.54)} 0)
\t\t\t(effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "{footprint}" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
{extra}{pins_str}
\t\t(instances
\t\t\t(project "rear-projection-display"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def pwr_sym(name, x, y, ref_n):
    ref = f"#PWR{ref_n:03d}"
    return f"""\t(symbol
\t\t(lib_id "power:{name}")
\t\t(at {fmt(x)} {fmt(y)} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{new_uuid()}")
\t\t(property "Reference" "{ref}" (at {fmt(x)} {fmt(y + 2.54)} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(property "Value" "{name}" (at {fmt(x)} {fmt(y - 2.54)} 0)
\t\t\t(effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(pin "1"
\t\t\t(uuid "{new_uuid()}")
\t\t)
\t\t(instances
\t\t\t(project "rear-projection-display"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def net_label(name, x, y, angle=0):
    """Net label — connection point is at (x, y). angle=0 → text goes right."""
    return f"""\t(label "{name}"
\t\t(at {fmt(x)} {fmt(y)} {angle})
\t\t(fields_autoplaced yes)
\t\t(effects (font (size 1.27 1.27)) (justify left bottom))
\t\t(uuid "{new_uuid()}")
\t)"""


def no_connect(x, y):
    return f'\t(no_connect (at {fmt(x)} {fmt(y)}) (uuid "{new_uuid()}"))\n'


def pin_uuids(pin_nums):
    lines = [f'\t\t(pin "{n}"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)' for n in pin_nums]
    return "\n".join(lines)


def wire(x1, y1, x2, y2):
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)})
\t\t)
\t\t(stroke (width 0) (type default))
\t\t(uuid "{new_uuid()}")
\t)"""


# ---------------------------------------------------------------------------
# Pin position helper  (applies y-negation: sch_y = sym_y - pin_py)
# ---------------------------------------------------------------------------


def pin_pos(sym_x, sym_y, pin_px, pin_py):
    """Schematic position of a pin given symbol origin and pin's symbol coords."""
    return sym_x + pin_px, sym_y - pin_py


# ---------------------------------------------------------------------------
# Component positions (mm, snapped to 2.54 mm grid)
# ---------------------------------------------------------------------------

# U1: IS31FL3236A-QFLS2-TR  origin = (60×2.54, 40×2.54) = (152.4, 101.6)
U1X, U1Y = 152.4, 101.6

# U1 pin endpoints in schematic coords — from SnapMagic symbol (y-negated)
# Right side (pin_px=+17.78):
U1_RIGHT_X = U1X + 17.78  # 170.18

# Symbol y-offsets for U1 output pins (from .kicad_sym, will be negated)
OUT_SYM_Y = {
    "OUT1": 43.18,  "OUT2": 40.64,  "OUT3": 38.10,
    "OUT4": 35.56,  "OUT5": 33.02,  "OUT6": 30.48,
    "OUT7": 27.94,  "OUT8": 25.40,  "OUT9": 22.86,
    "OUT10": 20.32, "OUT11": 17.78, "OUT12": 15.24,
    "OUT13": 12.70, "OUT14": 10.16, "OUT15":  7.62,
    "OUT16":  5.08, "OUT17":  2.54, "OUT18":  0.00,
    "OUT19": -2.54, "OUT20": -5.08, "OUT21": -7.62,
    "OUT22":-10.16, "OUT23":-12.70, "OUT24":-15.24,
    "OUT25":-17.78, "OUT26":-20.32, "OUT27":-22.86,
    "OUT28":-25.40, "OUT29":-27.94, "OUT30":-30.48,
    "OUT31":-33.02, "OUT32":-35.56, "OUT33":-38.10,
    "OUT34":-40.64, "OUT35":-43.18, "OUT36":-45.72,
}
# Schematic y for each output channel:
U1_OUT_SCH_Y = {k: U1Y - v for k, v in OUT_SYM_Y.items()}

# Left-side control pins (pin_px=-17.78)
U1_LEFT_X = U1X - 17.78  # 134.62
U1_REXT_Y  = U1Y -  5.08  # 96.52
U1_SDB_Y   = U1Y -  2.54  # 99.06
U1_SCL_Y   = U1Y -  0.00  # 101.6
U1_SDA_Y   = U1Y - (-5.08) # 106.68
U1_AD_Y    = U1Y - (-7.62) # 109.22

# Right-side power pins
U1_VCC_Y  = U1Y -  48.26  # 53.34
U1_GND_Y  = U1Y - (-50.8) # 152.4
U1_EPAD_Y = U1Y - (-53.34) # 154.94

# J1: QWIIC connector (Conn_01x04)  ----------------------------------------
# QWIIC pinout: 1=GND, 2=3.3V, 3=SDA, 4=SCL
# Conn_01x04 pins (symbol coords): P1(-5.08,2.54) P2(-5.08,0) P3(-5.08,-2.54) P4(-5.08,-5.08)
J1X, J1Y = 50.8, 99.06
J1_P_X = J1X - 5.08  # 45.72 — schematic x for all J1 pins
J1_P1_Y = J1Y - 2.54   # GND
J1_P2_Y = J1Y - 0      # +3V3
J1_P3_Y = J1Y + 2.54   # SDA
J1_P4_Y = J1Y + 5.08   # SCL

# J2: 5V power header (Conn_01x02) ------------------------------------------
# Conn_01x02 pins: P1(-5.08, 0)  P2(-5.08, -2.54)
J2X, J2Y = 50.8, 127.0
J2_P_X = J2X - 5.08   # 45.72
J2_P1_Y = J2Y - 0      # GND
J2_P2_Y = J2Y + 2.54   # +5V

# R1: REXT 2.2kΩ  (Device:R, vertical; P1 top, P2 bottom) ------------------
# P1(0,3.81) → sch (lx, ly-3.81);  P2(0,-3.81) → sch (lx, ly+3.81)
R1X, R1Y = 119.38, 96.52
R1_P1 = (R1X, R1Y - 3.81)  # top  → REXT net
R1_P2 = (R1X, R1Y + 3.81)  # bottom → GND

# R2: SDA pull-up 4.7kΩ vertical
R2X, R2Y = 109.22, 111.76
R2_P1 = (R2X, R2Y - 3.81)  # top  → +3V3
R2_P2 = (R2X, R2Y + 3.81)  # bottom → SDA

# R3: SCL pull-up 4.7kΩ vertical
R3X, R3Y = 109.22, 93.98
R3_P1 = (R3X, R3Y - 3.81)  # top  → +3V3
R3_P2 = (R3X, R3Y + 3.81)  # bottom → SCL

# R4: AD pull-down 10kΩ vertical — top pin at same y as U1_AD_Y (109.22)
R4X, R4Y = 119.38, 113.03
R4_P1 = (R4X, R4Y - 3.81)  # top  → AD pin
R4_P2 = (R4X, R4Y + 3.81)  # bottom → GND

# C1: 100nF decoupling  (Device:C, vertical; P1 top +, P2 bottom -)
# P1(0,3.81) P2(0,-3.81)
C1X, C1Y = 180.34, 53.34
C1_P1 = (C1X, C1Y - 3.81)  # → +5V
C1_P2 = (C1X, C1Y + 3.81)  # → GND

# C2: 10µF bulk decoupling
C2X, C2Y = 193.04, 53.34
C2_P1 = (C2X, C2Y - 3.81)  # → +5V
C2_P2 = (C2X, C2Y + 3.81)  # → GND

# LEDs: 4 columns × 3 rows, Device:LED_RGBK
# Pins: RA(5.08,5.08) GA(5.08,0) BA(5.08,-5.08) K(-5.08,0) — all y-negated
# RA → sch (lx+5.08, ly-5.08)  [top]
# GA → sch (lx+5.08, ly)
# BA → sch (lx+5.08, ly+5.08)  [bottom]
# K  → sch (lx-5.08, ly)
LED_GRID = []
for row in range(3):
    for col in range(4):
        led_num = row * 4 + col + 1
        lx = 208.28 + col * 25.4
        ly = 71.12 + row * 25.4
        LED_GRID.append((led_num, lx, ly))


def channel_nets(led_num):
    """Return (R_net, G_net, B_net) for LED 1-12."""
    b = (led_num - 1) * 3 + 1
    return f"LED{led_num}_R", f"LED{led_num}_G", f"LED{led_num}_B"


# ---------------------------------------------------------------------------
# Load symbol definitions from KiCAD libraries
# ---------------------------------------------------------------------------
print("Loading library symbols...")
POWER_LIB = f"{KICAD_SYMBOLS}/power.kicad_sym"
sym_R = extract_symbol(f"{KICAD_SYMBOLS}/Device.kicad_sym", "R", embed_as="Device:R")
sym_C = extract_symbol(f"{KICAD_SYMBOLS}/Device.kicad_sym", "C", embed_as="Device:C")
sym_LED_RGBK = extract_symbol(
    f"{KICAD_SYMBOLS}/Device.kicad_sym", "LED_RGBK",
    embed_as="Device:LED_RGBK",
)
sym_C1x04 = extract_symbol(
    f"{KICAD_SYMBOLS}/Connector_Generic.kicad_sym", "Conn_01x04",
    embed_as="Connector_Generic:Conn_01x04",
)
sym_C1x02 = extract_symbol(
    f"{KICAD_SYMBOLS}/Connector_Generic.kicad_sym", "Conn_01x02",
    embed_as="Connector_Generic:Conn_01x02",
)
sym_GND      = extract_symbol(POWER_LIB, "GND",      embed_as="power:GND")
sym_5V       = extract_symbol(POWER_LIB, "+5V",      embed_as="power:+5V")
sym_3V3      = extract_symbol(POWER_LIB, "+3V3",     embed_as="power:+3V3")
sym_PWRFLAG  = extract_symbol(POWER_LIB, "PWR_FLAG", embed_as="power:PWR_FLAG")

sym_IS31 = extract_symbol(SNAPMAGIC_SYM, "IS31FL3236A-QFLS2-TR",
                         embed_as="IS31FL3236A-QFLS2-TR:IS31FL3236A-QFLS2-TR")

print("Done.")

# ---------------------------------------------------------------------------
# Assemble schematic sections
# ---------------------------------------------------------------------------
ROOT_UUID = new_uuid()
symbols = []
pwrs = []
labels = []
wires = []
no_conns = []
pwr_n = 1


def add_pwr(name, pin_x, pin_y, dx, dy):
    global pwr_n
    px, py = pin_x + dx * STUB, pin_y + dy * STUB
    pwrs.append(pwr_sym(name, px, py, pwr_n))
    wires.append(wire(pin_x, pin_y, px, py))
    pwr_n += 1


def add_label(name, pin_x, pin_y, dx, dy):
    lx, ly = pin_x + dx * STUB, pin_y + dy * STUB
    angle = 180 if dx < 0 else 0
    labels.append(net_label(name, lx, ly, angle))
    wires.append(wire(pin_x, pin_y, lx, ly))


# --- U1: IS31FL3236A-QFLS2-TR ---
_u1_pins = pin_uuids([str(n) for n in range(1, 46)])
symbols.append(
    f"""\t(symbol
\t\t(lib_id "IS31FL3236A-QFLS2-TR:IS31FL3236A-QFLS2-TR")
\t\t(at {fmt(U1X)} {fmt(U1Y)} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{new_uuid()}")
\t\t(property "Reference" "U1" (at {fmt(U1X - 12.72)} {fmt(U1Y + 55)} 0)
\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Value" "IS31FL3236A-QFLS2-TR" (at {fmt(U1X - 12.72)} {fmt(U1Y + 57.5)} 0)
\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Footprint" "IS31FL3236A-QFLS2-TR:QFN40P500X500X80-45N" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
\t\t(property "LCSC" "C246443" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide))
{_u1_pins}
\t\t(instances
\t\t\t(project "rear-projection-display"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "U1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""
)

# U1 power connections
add_pwr("+5V", U1_RIGHT_X, U1_VCC_Y, 0, -1)
add_pwr("GND", U1_RIGHT_X, U1_GND_Y, 0, 1)
add_pwr("GND", U1_RIGHT_X, U1_EPAD_Y, 0, 1)

# U1 control pins
add_pwr("+5V", U1_LEFT_X, U1_SDB_Y, -1, 0)
# AD tied to GND via R4 pull-down (decouples bidirectional AD from the power rail)
wires.append(wire(U1_LEFT_X, U1_AD_Y, R4_P1[0], R4_P1[1]))

# U1 REXT and I2C via net labels
add_label("REXT", U1_LEFT_X, U1_REXT_Y, -1, 0)
add_label("SDA", U1_LEFT_X, U1_SDA_Y, -1, 0)
add_label("SCL", U1_LEFT_X, U1_SCL_Y, -1, 0)

# U1 output pins → LED channel net labels
for out_name, sch_y in U1_OUT_SCH_Y.items():
    n = int(out_name[3:])
    led = (n - 1) // 3 + 1
    color = ["R", "G", "B"][(n - 1) % 3]
    add_label(f"LED{led}_{color}", U1_RIGHT_X, sch_y, 1, 0)

# --- J1: QWIIC connector ---
symbols.append(
    sym_instance(
        "Connector_Generic:Conn_01x04",
        "J1",
        "QWIIC",
        J1X,
        J1Y,
        footprint="Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
        pins=["1", "2", "3", "4"],
    )
)
add_pwr("GND", J1_P_X, J1_P1_Y, -1, 0)
add_pwr("+3V3", J1_P_X, J1_P2_Y, -1, 0)
add_label("SDA", J1_P_X, J1_P3_Y, -1, 0)
add_label("SCL", J1_P_X, J1_P4_Y, -1, 0)

# --- J2: 5V power header ---
symbols.append(
    sym_instance(
        "Connector_Generic:Conn_01x02",
        "J2",
        "+5V Power",
        J2X,
        J2Y,
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        pins=["1", "2"],
    )
)
add_pwr("GND", J2_P_X, J2_P1_Y, -1, 0)
add_pwr("+5V", J2_P_X, J2_P2_Y, -1, 0)

# PWR_FLAG: mark each externally-supplied rail as driven
# Place at the same point as the connector power symbols (J1 for +3V3/GND, J2 for +5V/GND)
pwrs.append(pwr_sym("PWR_FLAG", J1_P_X - STUB, J1_P2_Y, pwr_n)); pwr_n += 1  # +3V3 rail
pwrs.append(pwr_sym("PWR_FLAG", J2_P_X - STUB, J2_P2_Y, pwr_n)); pwr_n += 1  # +5V rail
pwrs.append(pwr_sym("PWR_FLAG", J2_P_X - STUB, J2_P1_Y, pwr_n)); pwr_n += 1  # GND rail

# --- R1: REXT 2.2kΩ ---
symbols.append(
    sym_instance("Device:R", "R1", "2.2k", R1X, R1Y,
                 footprint="Resistor_SMD:R_0603_1608Metric", pins=["1", "2"])
)
add_label("REXT", R1_P1[0], R1_P1[1], 0, -1)
add_pwr("GND", R1_P2[0], R1_P2[1], 0, 1)

# --- R2: SDA pull-up 4.7kΩ ---
symbols.append(
    sym_instance("Device:R", "R2", "4.7k", R2X, R2Y,
                 footprint="Resistor_SMD:R_0603_1608Metric", pins=["1", "2"])
)
add_pwr("+3V3", R2_P1[0], R2_P1[1], 0, -1)
add_label("SDA", R2_P2[0], R2_P2[1], 0, 1)

# --- R3: SCL pull-up 4.7kΩ ---
symbols.append(
    sym_instance("Device:R", "R3", "4.7k", R3X, R3Y,
                 footprint="Resistor_SMD:R_0603_1608Metric", pins=["1", "2"])
)
add_pwr("+3V3", R3_P1[0], R3_P1[1], 0, -1)
add_label("SCL", R3_P2[0], R3_P2[1], 0, 1)

# --- R4: AD pull-down 10kΩ ---
symbols.append(
    sym_instance("Device:R", "R4", "10k", R4X, R4Y,
                 footprint="Resistor_SMD:R_0603_1608Metric", pins=["1", "2"])
)
add_pwr("GND", R4_P2[0], R4_P2[1], 0, 1)

# --- C1: 100nF VCC decoupling ---
symbols.append(
    sym_instance("Device:C", "C1", "100nF", C1X, C1Y,
                 footprint="Capacitor_SMD:C_0402_1005Metric", pins=["1", "2"])
)
add_pwr("+5V", C1_P1[0], C1_P1[1], 0, -1)
add_pwr("GND", C1_P2[0], C1_P2[1], 0, 1)

# --- C2: 10µF bulk decoupling ---
symbols.append(
    sym_instance("Device:C", "C2", "10uF", C2X, C2Y,
                 footprint="Capacitor_SMD:C_0805_2012Metric", pins=["1", "2"])
)
add_pwr("+5V", C2_P1[0], C2_P1[1], 0, -1)
add_pwr("GND", C2_P2[0], C2_P2[1], 0, 1)

# --- D1–D12: RGB LEDs ---
for led_num, lx, ly in LED_GRID:
    r_net, g_net, b_net = channel_nets(led_num)
    symbols.append(
        sym_instance(
            "Device:LED_RGBK",
            f"D{led_num}",
            "LED_RGB_10mm",
            lx,
            ly,
            footprint="LED_RGB_10mm:LED_RGB_10mm_4pin",
            pins=["1", "2", "3", "4"],
        )
    )
    add_label(r_net, lx + 5.08, ly - 5.08, 1, 0)
    add_label(g_net, lx + 5.08, ly, 1, 0)
    add_label(b_net, lx + 5.08, ly + 5.08, 1, 0)
    add_pwr("GND", lx - 5.08, ly, -1, 0)

# ---------------------------------------------------------------------------
# Build lib_symbols block (embed all used symbols)
# ---------------------------------------------------------------------------
def indent(text, prefix="\t"):
    return "\n".join(prefix + line if line else line for line in text.split("\n"))

lib_body = "\n".join([
    indent(sym_R),
    indent(sym_C),
    indent(sym_LED_RGBK),
    indent(sym_C1x04),
    indent(sym_C1x02),
    indent(sym_GND),
    indent(sym_5V),
    indent(sym_3V3),
    indent(sym_PWRFLAG),
    indent(sym_IS31),
])

# ---------------------------------------------------------------------------
# Write schematic
# ---------------------------------------------------------------------------
sch = f"""(kicad_sch
\t(version 20250316)
\t(generator "rpd-gen")
\t(uuid "{ROOT_UUID}")
\t(paper "A2")
\t(lib_symbols
{lib_body}
\t)

"""
sch += "\n".join(symbols) + "\n\n"
sch += "\n".join(pwrs) + "\n\n"
sch += "\n".join(labels) + "\n\n"
sch += "\n".join(wires) + "\n\n"
sch += ")\n"

with open(OUTPUT_SCH, "w") as f:
    f.write(sch)

print(f"Schematic written: {OUTPUT_SCH}")
total_syms = len(symbols) + len(pwrs)
print(f"  {len(symbols)} component symbols, {len(pwrs)} power symbols, {len(labels)} net labels")
