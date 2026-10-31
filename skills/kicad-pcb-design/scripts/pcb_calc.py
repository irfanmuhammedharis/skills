#!/usr/bin/env python3
"""
pcb_calc.py - PCB engineering calculations for KiCad design work.

Pure standard library. Every subcommand prints the inputs it used, the model it
applied, and the result, so the numbers can be pasted into a design record and
checked by a reviewer.

Run `python3 pcb_calc.py list` for the catalogue.
"""

import argparse
import math
import sys

# ---------------------------------------------------------------- constants
RHO_CU_20C = 1.72e-8          # ohm-metre
ALPHA_CU = 0.00393            # per K
K_CU = 390.0                  # W/(m K)
K_FR4 = 0.3                   # W/(m K)
C0_MM_PS = 0.299792458        # mm per ps
OZ_TO_MM = 0.0348             # 1 oz copper thickness in mm (~1.37 mil)
MM_TO_MIL = 39.3701


def banner(title, inputs, model):
    print(f"\n=== {title} ===")
    print("Inputs:")
    for k, v in inputs.items():
        print(f"  {k:<28} {v}")
    print(f"Model:  {model}")
    print("Result:")


def out(label, value, unit=""):
    print(f"  {label:<28} {value}{(' ' + unit) if unit else ''}")


def note(text):
    print(f"  ! {text}")


# ---------------------------------------------------------------- elliptic K
def ellip_k(k):
    """Complete elliptic integral of the first kind via AGM."""
    k = min(max(k, 0.0), 1.0 - 1e-15)
    a, b = 1.0, math.sqrt(1.0 - k * k)
    while abs(a - b) > 1e-15:
        a, b = (a + b) / 2.0, math.sqrt(a * b)
    return math.pi / (2.0 * a)


def k_ratio(k):
    """K(k)/K(k') with k' = sqrt(1-k^2)."""
    return ellip_k(k) / ellip_k(math.sqrt(max(0.0, 1.0 - k * k)))


# ---------------------------------------------------------------- trace width
def ipc2221_width_mm(current, rise_c, copper_oz, external):
    """IPC-2221 curve fit. Returns required width in mm."""
    k = 0.048 if external else 0.024
    area_mil2 = (current / (k * rise_c ** 0.44)) ** (1 / 0.725)
    thickness_mil = copper_oz * OZ_TO_MM * MM_TO_MIL
    return (area_mil2 / thickness_mil) / MM_TO_MIL


def ipc2221_current(width_mm, rise_c, copper_oz, external):
    k = 0.048 if external else 0.024
    area_mil2 = width_mm * MM_TO_MIL * copper_oz * OZ_TO_MM * MM_TO_MIL
    return k * rise_c ** 0.44 * area_mil2 ** 0.725


def cmd_trace_width(a):
    external = a.layer == "external"
    banner("Trace width (IPC-2221)",
           {"current": f"{a.current} A", "temperature rise": f"{a.rise} C",
            "copper weight": f"{a.copper_oz} oz ({a.copper_oz * OZ_TO_MM:.4f} mm)",
            "layer": a.layer},
           "IPC-2221 A = (I / (k dT^0.44))^(1/0.725), k = 0.048 external / 0.024 internal")
    w = ipc2221_width_mm(a.current, a.rise, a.copper_oz, external)
    out("required width", f"{w:.3f}", "mm")
    out("             ", f"{w * MM_TO_MIL:.1f}", "mil")
    out("with 2x margin", f"{2 * w:.3f}", "mm")
    for extra in (0.25, 0.5, 1.0, 2.0):
        i = ipc2221_current(extra, a.rise, a.copper_oz, external)
        out(f"capacity of {extra:.2f} mm", f"{i:.2f}", "A")
    note("DC heating only; check voltage drop separately (subcommand: voltage-drop).")
    note("Internal layers and copper under components run hotter than this model predicts.")
    if not external:
        note("Internal-layer rule needs roughly 2x the width of an external trace.")


# ---------------------------------------------------------------- voltage drop
def cmd_voltage_drop(a):
    t_mm = a.copper_oz * OZ_TO_MM
    rho = RHO_CU_20C * (1 + ALPHA_CU * (a.temp - 20.0))
    area_m2 = (a.width / 1000.0) * (t_mm / 1000.0)
    r = rho * (a.length / 1000.0) / area_m2
    banner("Voltage drop / trace resistance",
           {"current": f"{a.current} A", "length": f"{a.length} mm",
            "width": f"{a.width} mm", "copper weight": f"{a.copper_oz} oz",
            "conductor temperature": f"{a.temp} C"},
           "R = rho(T) * L / (w * t), rho_20 = 1.72e-8 ohm.m, alpha = 0.00393/K")
    out("resistance", f"{r * 1000:.2f}", "mohm")
    out("voltage drop", f"{r * a.current * 1000:.1f}", "mV")
    out("power dissipated", f"{r * a.current ** 2 * 1000:.1f}", "mW")
    if a.rail:
        out("drop as % of rail", f"{100 * r * a.current / a.rail:.2f}", "%")
    note("Round trip: add the return path drop unless the return is a solid plane.")


# ---------------------------------------------------------------- microstrip
def microstrip_z0(w, h, t, er):
    """Hammerstad microstrip with thickness correction. mm, mm, mm, -"""
    if t > 0 and w / h > 1 / (2 * math.pi):
        w = w + (t / math.pi) * (1 + math.log(2 * h / t))
    elif t > 0:
        w = w + (t / math.pi) * (1 + math.log(4 * math.pi * w / t))
    u = w / h
    if u <= 1:
        eeff = (er + 1) / 2 + (er - 1) / 2 * ((1 + 12 / u) ** -0.5 + 0.04 * (1 - u) ** 2)
        z0 = 60 / math.sqrt(eeff) * math.log(8 / u + u / 4)
    else:
        eeff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / u) ** -0.5
        z0 = 120 * math.pi / (math.sqrt(eeff) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
    return z0, eeff


def solve_width(fn, target, lo=0.02, hi=20.0):
    """Bisection on width for a monotonically decreasing Z0(w)."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if fn(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cmd_microstrip(a):
    if a.z0 and not a.w:
        w = solve_width(lambda x: microstrip_z0(x, a.h, a.t, a.er)[0], a.z0)
        mode = f"solved width for Z0 = {a.z0} ohm"
    else:
        w = a.w
        mode = "computed Z0 from width"
    z0, eeff = microstrip_z0(w, a.h, a.t, a.er)
    tpd = math.sqrt(eeff) / C0_MM_PS
    banner("Microstrip (outer layer over one plane)",
           {"dielectric height h": f"{a.h} mm", "copper thickness t": f"{a.t} mm",
            "er": a.er, "mode": mode},
           "Hammerstad/Jensen with thickness correction")
    out("trace width", f"{w:.3f}", "mm")
    out("           ", f"{w * MM_TO_MIL:.1f}", "mil")
    out("Z0", f"{z0:.1f}", "ohm")
    out("effective er", f"{eeff:.2f}")
    out("propagation delay", f"{tpd:.2f}", "ps/mm")
    out("velocity", f"{100 / math.sqrt(eeff):.0f}", "% of c")
    note("Solder mask over the trace lowers Z0 by roughly 1-3 ohm; the fab's calculator")
    note("includes it. Confirm the final width with the fab before an impedance-controlled order.")


def cmd_stripline(a):
    """Symmetric stripline, IPC-2141: b = plane-to-plane dielectric thickness."""
    b = a.h
    if a.z0 and not a.w:
        def z(w):
            return 60 / math.sqrt(a.er) * math.log(4 * b / (0.67 * math.pi * w * (0.8 + a.t / w)))
        w = solve_width(z, a.z0, 0.02, b)
        mode = f"solved width for Z0 = {a.z0} ohm"
    else:
        w = a.w
        mode = "computed Z0 from width"
    z0 = 60 / math.sqrt(a.er) * math.log(4 * b / (0.67 * math.pi * w * (0.8 + a.t / w)))
    tpd = math.sqrt(a.er) / C0_MM_PS
    banner("Stripline (inner layer between two planes)",
           {"plane-to-plane b": f"{b} mm", "copper thickness t": f"{a.t} mm",
            "er": a.er, "mode": mode},
           "IPC-2141 symmetric stripline")
    out("trace width", f"{w:.3f}", "mm")
    out("Z0", f"{z0:.1f}", "ohm")
    out("propagation delay", f"{tpd:.2f}", "ps/mm")
    if w / (b - a.t) > 0.35:
        note("w/(b-t) > 0.35: outside the formula's validated range, treat as indicative.")
    note("Stripline is slower than microstrip: mixing layers in a matched group needs")
    note("time-domain tuning, not length matching.")


def cmd_cpwg(a):
    """Grounded coplanar waveguide."""
    w, s, h, er = a.w, a.s, a.h, a.er
    k = w / (w + 2 * s)
    k3 = math.tanh(math.pi * w / (4 * h)) / math.tanh(math.pi * (w + 2 * s) / (4 * h))
    r1, r3 = k_ratio(k), k_ratio(k3)
    eeff = (1 + er * (r3 / r1)) / (1 + (r3 / r1)) if r1 else er
    z0 = 60 * math.pi / (math.sqrt(eeff) * (r1 + r3))
    banner("Coplanar waveguide with ground (CPWG)",
           {"trace width w": f"{w} mm", "gap to coplanar ground s": f"{s} mm",
            "height to lower ground h": f"{h} mm", "er": er},
           "Conformal mapping, complete elliptic integrals (AGM)")
    out("Z0", f"{z0:.1f}", "ohm")
    out("effective er", f"{eeff:.2f}")
    out("propagation delay", f"{math.sqrt(eeff) / C0_MM_PS:.2f}", "ps/mm")
    note("Fence the coplanar grounds with vias at <= lambda/20 spacing or the structure")
    note("behaves like a slot antenna at the top of its band.")


def cmd_diff_microstrip(a):
    z0, eeff = microstrip_z0(a.w, a.h, a.t, a.er)
    zdiff = 2 * z0 * (1 - 0.48 * math.exp(-0.96 * a.s / a.h))
    banner("Edge-coupled differential microstrip",
           {"width w": f"{a.w} mm", "gap s": f"{a.s} mm", "height h": f"{a.h} mm",
            "copper t": f"{a.t} mm", "er": a.er},
           "IPC-2141: Zdiff = 2*Z0*(1 - 0.48*exp(-0.96*s/h))")
    out("single-ended Z0", f"{z0:.1f}", "ohm")
    out("differential Zdiff", f"{zdiff:.1f}", "ohm")
    out("propagation delay", f"{math.sqrt(eeff) / C0_MM_PS:.2f}", "ps/mm")
    note("Width and gap trade against each other; fix width from routing density, then")
    note("solve the gap. Verify with the fab's impedance calculator before ordering.")


def cmd_diff_stripline(a):
    b = a.h
    z0 = 60 / math.sqrt(a.er) * math.log(4 * b / (0.67 * math.pi * a.w * (0.8 + a.t / a.w)))
    zdiff = 2 * z0 * (1 - 0.347 * math.exp(-2.9 * a.s / b))
    banner("Edge-coupled differential stripline",
           {"width w": f"{a.w} mm", "gap s": f"{a.s} mm", "plane-to-plane b": f"{b} mm",
            "copper t": f"{a.t} mm", "er": a.er},
           "IPC-2141: Zdiff = 2*Z0*(1 - 0.347*exp(-2.9*s/b))")
    out("single-ended Z0", f"{z0:.1f}", "ohm")
    out("differential Zdiff", f"{zdiff:.1f}", "ohm")
    out("propagation delay", f"{math.sqrt(a.er) / C0_MM_PS:.2f}", "ps/mm")


# ---------------------------------------------------------------- timing
def cmd_prop_delay(a):
    if a.mode == "microstrip":
        eeff = (a.er + 1) / 2 + (a.er - 1) / 2 * (1 + 12 / 2.0) ** -0.5  # w/h ~ 2 typical
        label = "microstrip (eeff from er, w/h ~ 2)"
    else:
        eeff = a.er
        label = "stripline (fully embedded)"
    tpd = math.sqrt(eeff) / C0_MM_PS
    banner("Propagation delay and critical length",
           {"er": a.er, "mode": a.mode,
            "length": f"{a.length} mm" if a.length else "-",
            "rise time": f"{a.rise_ps} ps" if a.rise_ps else "-"},
           f"tpd = sqrt(eeff)/c, {label}")
    out("effective er", f"{eeff:.2f}")
    out("delay", f"{tpd:.2f}", "ps/mm")
    out("length per 100 ps", f"{100 / tpd:.1f}", "mm")
    if a.length:
        out(f"delay over {a.length} mm", f"{tpd * a.length:.0f}", "ps")
    if a.rise_ps:
        lcrit = a.rise_ps / (3 * tpd)
        out("critical length (tr/3)", f"{lcrit:.1f}", "mm")
        out("conservative (tr/6)", f"{lcrit / 2:.1f}", "mm")
        note("Beyond the critical length, treat the net as a transmission line:")
        note("controlled impedance, matched termination, continuous reference plane.")


def cmd_bulk_cap(a):
    c = a.di * (a.dt_us * 1e-6) / a.dv
    esr = a.dv / a.di
    banner("Bulk capacitance for a load step",
           {"current step": f"{a.di} A", "step duration": f"{a.dt_us} us",
            "allowed droop": f"{a.dv} V"},
           "C = I*dt/dV ; ESR_max = dV/dI (the ESR limit usually binds first)")
    out("minimum capacitance", f"{c * 1e6:.1f}", "uF")
    out("with 2x derating margin", f"{c * 2e6:.1f}", "uF")
    out("maximum ESR", f"{esr * 1000:.0f}", "mohm")
    note("MLCC capacitance falls with DC bias and temperature: size from the vendor's")
    note("bias curve at the working voltage, not from the printed value.")


# ---------------------------------------------------------------- vias
def cmd_via_current(a):
    d = a.drill / 1000.0
    p = a.plating / 1000.0
    length = a.length / 1000.0
    area = math.pi * p * (d + p)
    r = RHO_CU_20C * length / area
    eq_width_mm = math.pi * a.drill
    cap = ipc2221_current(eq_width_mm, a.rise, a.plating / OZ_TO_MM, external=False)
    banner("Via resistance and current capacity",
           {"drill diameter": f"{a.drill} mm", "plating thickness": f"{a.plating} mm",
            "barrel length (board thickness)": f"{a.length} mm",
            "current": f"{a.current} A", "temperature rise": f"{a.rise} C"},
           "R = rho*L/A with A = pi*p*(d+p); capacity from IPC-2221 on the unrolled barrel")
    out("barrel cross-section", f"{area * 1e6:.4f}", "mm^2")
    out("resistance per via", f"{r * 1e6:.0f}", "uohm")
    out("capacity per via", f"{cap:.2f}", "A")
    n = max(1, math.ceil(a.current / cap))
    out("vias needed for current", f"{n}")
    out("recommended (2x margin)", f"{2 * n}")
    out(f"drop through {2 * n} vias", f"{a.current * r / (2 * n) * 1000:.3f}", "mV")
    note("Spread the vias so current divides evenly; a via under a hot component runs")
    note("hotter than this model. Never carry a power net through a single via.")


def cmd_thermal_vias(a):
    d = a.drill / 1000.0
    p = a.plating / 1000.0
    length = a.thickness / 1000.0
    a_cu = math.pi * p * (d + p)
    a_fill = math.pi * (d / 2 - p) ** 2 if d / 2 > p else 0.0
    r_one = length / (K_CU * a_cu + K_FR4 * a_fill)
    r_array = r_one / a.count
    banner("Thermal via array",
           {"power to move": f"{a.power} W", "via drill": f"{a.drill} mm",
            "plating": f"{a.plating} mm", "board thickness": f"{a.thickness} mm",
            "via count": a.count},
           "R = L/(k_cu*A_cu + k_fill*A_fill), N vias in parallel")
    out("R_th per via", f"{r_one:.1f}", "K/W")
    out("R_th of array", f"{r_array:.2f}", "K/W")
    out("rise across the array", f"{a.power * r_array:.1f}", "K")
    note("This is only the path through the board. Total junction-to-ambient is dominated")
    note("by the copper area and airflow on the far side: 1 sq inch of 1 oz copper in still")
    note("air is worth roughly 60-80 K/W, so plan the pour, not just the vias.")
    note("Cap or fill vias in a paste-printed pad or solder wicks through and starves the joint.")


# ---------------------------------------------------------------- safety
IEC60664_PD2_CREEPAGE = {  # working voltage V -> (group I, group II, group IIIa/IIIb) mm
    50: (0.60, 0.85, 1.20), 100: (0.71, 1.00, 1.40), 125: (0.75, 1.05, 1.50),
    160: (0.80, 1.10, 1.60), 200: (1.00, 1.40, 2.00), 250: (1.25, 1.80, 2.50),
    320: (1.60, 2.20, 3.20), 400: (2.00, 2.80, 4.00), 500: (2.50, 3.60, 5.00),
    630: (3.20, 4.50, 6.30), 800: (4.00, 5.60, 8.00), 1000: (5.00, 7.10, 10.00),
}
IPC2221_B1_CLEARANCE = [(15, 0.05), (30, 0.05), (50, 0.13), (100, 0.13), (150, 0.40),
                        (170, 0.40), (250, 0.40), (300, 0.40), (500, 0.80)]


def cmd_creepage(a):
    rows = sorted(IEC60664_PD2_CREEPAGE)
    row = next((r for r in rows if r >= a.voltage), rows[-1])
    idx = {"I": 0, "II": 1, "IIIa": 2, "IIIb": 2}[a.material]
    creep = IEC60664_PD2_CREEPAGE[row][idx]
    clear = next((v for lim, v in IPC2221_B1_CLEARANCE if a.voltage <= lim),
                 0.00305 * a.voltage)
    banner("Creepage and clearance (first pass)",
           {"working voltage": f"{a.voltage} V", "pollution degree": a.pollution,
            "material group": a.material, "table row used": f"{row} V"},
           "IEC 60664-1 basic-insulation creepage (pollution degree 2) + IPC-2221 B1 clearance")
    out("creepage (basic, PD2)", f"{creep:.2f}", "mm")
    out("creepage (reinforced)", f"{2 * creep:.2f}", "mm")
    out("clearance (IPC-2221 B1)", f"{clear:.2f}", "mm")
    if a.pollution != 2:
        note(f"Values shown are pollution degree 2. PD{a.pollution} differs - read the table")
        note("in IEC 60664-1 directly; do not scale these numbers.")
    note("Reinforced insulation is conventionally twice the basic creepage, but the")
    note("governing product standard (IEC 62368-1, 61010, 60335 ...) decides. Verify there.")
    note("Enforce in KiCad with (constraint creepage (min X)) on the mains netclass, and")
    note("extend the path with a milled slot where the distance cannot be met on copper.")


# ---------------------------------------------------------------- catalogue
CATALOGUE = """
trace-width      Conductor width for a current and temperature rise (IPC-2221)
voltage-drop     Resistance, drop and dissipation of a track
microstrip       Outer-layer impedance: Z0 from width, or width from target Z0
stripline        Inner-layer impedance between two planes
cpwg             Grounded coplanar waveguide (RF feed lines)
diff-microstrip  Differential impedance, outer layer
diff-stripline   Differential impedance, inner layer
prop-delay       Propagation delay, and the critical length for a given rise time
bulk-cap         Bulk capacitance and maximum ESR for a load step
via-current      Via resistance, current capacity, and how many you need
thermal-vias     Thermal resistance of a via array under a power part
creepage         Creepage and clearance first pass for a working voltage
"""


def main():
    p = argparse.ArgumentParser(description="PCB engineering calculations")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="list all subcommands")

    s = sub.add_parser("trace-width")
    s.add_argument("--current", type=float, required=True)
    s.add_argument("--rise", type=float, default=10.0, help="temperature rise, C")
    s.add_argument("--copper-oz", type=float, default=1.0)
    s.add_argument("--layer", choices=["external", "internal"], default="external")
    s.set_defaults(fn=cmd_trace_width)

    s = sub.add_parser("voltage-drop")
    s.add_argument("--current", type=float, required=True)
    s.add_argument("--length", type=float, required=True, help="mm")
    s.add_argument("--width", type=float, required=True, help="mm")
    s.add_argument("--copper-oz", type=float, default=1.0)
    s.add_argument("--temp", type=float, default=25.0, help="conductor temperature C")
    s.add_argument("--rail", type=float, help="rail voltage, for % drop")
    s.set_defaults(fn=cmd_voltage_drop)

    s = sub.add_parser("microstrip")
    s.add_argument("--er", type=float, default=4.4)
    s.add_argument("--h", type=float, required=True, help="dielectric height, mm")
    s.add_argument("--t", type=float, default=0.035, help="copper thickness, mm")
    s.add_argument("--w", type=float, help="trace width, mm")
    s.add_argument("--z0", type=float, help="target impedance, ohm")
    s.set_defaults(fn=cmd_microstrip)

    s = sub.add_parser("stripline")
    s.add_argument("--er", type=float, default=4.4)
    s.add_argument("--h", type=float, required=True, help="plane-to-plane spacing b, mm")
    s.add_argument("--t", type=float, default=0.0152)
    s.add_argument("--w", type=float)
    s.add_argument("--z0", type=float)
    s.set_defaults(fn=cmd_stripline)

    s = sub.add_parser("cpwg")
    s.add_argument("--er", type=float, default=4.4)
    s.add_argument("--h", type=float, required=True)
    s.add_argument("--w", type=float, required=True)
    s.add_argument("--s", type=float, required=True, help="gap to coplanar ground, mm")
    s.set_defaults(fn=cmd_cpwg)

    for name, fn in (("diff-microstrip", cmd_diff_microstrip),
                     ("diff-stripline", cmd_diff_stripline)):
        s = sub.add_parser(name)
        s.add_argument("--er", type=float, default=4.4)
        s.add_argument("--h", type=float, required=True)
        s.add_argument("--t", type=float, default=0.035)
        s.add_argument("--w", type=float, required=True)
        s.add_argument("--s", type=float, required=True)
        s.set_defaults(fn=fn)

    s = sub.add_parser("prop-delay")
    s.add_argument("--er", type=float, default=4.4)
    s.add_argument("--mode", choices=["microstrip", "stripline"], default="microstrip")
    s.add_argument("--length", type=float, help="mm")
    s.add_argument("--rise-ps", type=float, help="signal rise time, ps")
    s.set_defaults(fn=cmd_prop_delay)

    s = sub.add_parser("bulk-cap")
    s.add_argument("--di", type=float, required=True, help="current step, A")
    s.add_argument("--dt-us", type=float, required=True, help="step duration, us")
    s.add_argument("--dv", type=float, required=True, help="allowed droop, V")
    s.set_defaults(fn=cmd_bulk_cap)

    s = sub.add_parser("via-current")
    s.add_argument("--drill", type=float, default=0.3, help="mm")
    s.add_argument("--plating", type=float, default=0.025, help="mm")
    s.add_argument("--length", type=float, default=1.6, help="board thickness, mm")
    s.add_argument("--current", type=float, required=True)
    s.add_argument("--rise", type=float, default=10.0)
    s.set_defaults(fn=cmd_via_current)

    s = sub.add_parser("thermal-vias")
    s.add_argument("--power", type=float, required=True, help="W")
    s.add_argument("--drill", type=float, default=0.3)
    s.add_argument("--plating", type=float, default=0.025)
    s.add_argument("--thickness", type=float, default=1.6)
    s.add_argument("--count", type=int, default=9)
    s.set_defaults(fn=cmd_thermal_vias)

    s = sub.add_parser("creepage")
    s.add_argument("--voltage", type=float, required=True, help="working voltage, V")
    s.add_argument("--pollution", type=int, default=2, choices=[1, 2, 3])
    s.add_argument("--material", default="IIIa", choices=["I", "II", "IIIa", "IIIb"])
    s.set_defaults(fn=cmd_creepage)

    a = p.parse_args()
    if not a.cmd or a.cmd == "list":
        print(__doc__.strip())
        print(CATALOGUE)
        return 0
    a.fn(a)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
