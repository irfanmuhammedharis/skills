#!/usr/bin/env python3
"""Embedded engineering calculators for firmware documentation.

Subcommands:
  link-budget  --tx-dbm N --tx-gain-dbi N --rx-gain-dbi N --freq-mhz N --distance-km N [--margin-db N]
  i2c-pullup   --vdd N --capacitance-pf N [--speed-khz N]
  baud-error   --clock-hz N --baud N [--div N]  (USART with 16x oversampling by default)
  battery-life --battery-mah N --sleep-ua N --sleep-pct N --active-ma N [--active-pct N] [--tx-ma N --tx-pct N]
  crc16        --data "hex bytes, e.g. 01 03 00 00 00 02" [--poly 0x1021] [--init 0xFFFF] [--refin] [--refout] [--xorout 0x0000]
"""

import argparse
import math


def link_budget(args):
    fspl = 20 * math.log10(args.distance_km) + 20 * math.log10(args.freq_mhz) + 32.44
    rx = args.tx_dbm + args.tx_gain_dbi - fspl + args.rx_gain_dbi
    print(f"FSPL:                {fspl:.1f} dB")
    print(f"RX power:            {rx:.1f} dBm")
    if args.margin_db is not None:
        sensitivity = rx - args.margin_db
        print(f"Required sensitivity for {args.margin_db} dB margin: {sensitivity:.1f} dBm")
    return rx


def i2c_pullup(args):
    tr_ns = 1000 if args.speed_khz <= 100 else 300
    iol_ma = 3.0
    rp_min = (args.vdd - 0.4) / (iol_ma / 1000.0)
    rp_max = tr_ns / (0.8473 * args.capacitance_pf * 1e-12) / 1e9  # ohms
    rp_max_ohm = tr_ns * 1e-9 / (0.8473 * args.capacitance_pf * 1e-12)
    print(f"Rise time budget:    {tr_ns} ns ({args.speed_khz} kHz mode)")
    print(f"Rp min (sink 3 mA):  {rp_min:.0f} ohm")
    print(f"Rp max (rise time):  {rp_max_ohm:.0f} ohm")
    if rp_min >= rp_max_ohm:
        print("WARNING: no valid pull-up range — reduce bus capacitance or speed")
    else:
        print(f"Recommended:         {math.sqrt(rp_min * rp_max_ohm):.0f} ohm (geometric mean)")


def baud_error(args):
    actual = args.clock_hz / (16 * args.div)
    err = (actual - args.baud) / args.baud * 100
    print(f"Divider: {args.div}  ->  actual baud: {actual:.2f}")
    print(f"Error: {err:+.3f}%  (budget: <2% total for both ends)")
    best_div, best_err = args.div, err
    for d in range(1, 65536):
        a = args.clock_hz / (16 * d)
        e = abs((a - args.baud) / args.baud * 100)
        if e < abs(best_err):
            best_div, best_err = d, (a - args.baud) / args.baud * 100
    print(f"Best divider: {best_div}  ->  error {best_err:+.4f}%")


def battery_life(args):
    sleep_pct = args.sleep_pct / 100.0
    active_pct = (args.active_pct if args.active_pct is not None else 100 - args.sleep_pct) / 100.0
    tx_pct = (args.tx_pct or 0) / 100.0
    avg_ua = (
        args.sleep_ua * sleep_pct
        + args.active_ma * 1000 * (active_pct - tx_pct)
        + (args.tx_ma or 0) * 1000 * tx_pct
    )
    days = args.battery_mah * 1000 / avg_ua / 24
    print(f"Average current:     {avg_ua:.1f} uA")
    print(f"Battery life:        {days:.0f} days  ({days / 365:.2f} years)")
    print(f"With 30% derating:   {days * 0.7:.0f} days")


def crc16(args):
    data = bytes(int(b, 16) for b in args.data.replace(",", " ").split())
    poly, init, xorout = args.poly, args.init, args.xorout
    crc = init
    if args.refin:
        # reflected algorithm (right shift), e.g. Modbus poly 0xA001
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ poly if crc & 1 else crc >> 1
    else:
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                crc = ((crc << 1) ^ poly) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    crc ^= xorout
    print(f"CRC16: 0x{crc:04X}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("link-budget")
    s.add_argument("--tx-dbm", type=float, required=True)
    s.add_argument("--tx-gain-dbi", type=float, default=0)
    s.add_argument("--rx-gain-dbi", type=float, default=0)
    s.add_argument("--freq-mhz", type=float, required=True)
    s.add_argument("--distance-km", type=float, required=True)
    s.add_argument("--margin-db", type=float)
    s.set_defaults(fn=link_budget)

    s = sub.add_parser("i2c-pullup")
    s.add_argument("--vdd", type=float, required=True)
    s.add_argument("--capacitance-pf", type=float, required=True)
    s.add_argument("--speed-khz", type=float, default=400)
    s.set_defaults(fn=i2c_pullup)

    s = sub.add_parser("baud-error")
    s.add_argument("--clock-hz", type=float, required=True)
    s.add_argument("--baud", type=float, required=True)
    s.add_argument("--div", type=int, default=None)
    s.set_defaults(fn=lambda a: baud_error(argparse.Namespace(**{**vars(a), "div": a.div or round(a.clock_hz / (16 * a.baud))})))

    s = sub.add_parser("battery-life")
    s.add_argument("--battery-mah", type=float, required=True)
    s.add_argument("--sleep-ua", type=float, required=True)
    s.add_argument("--sleep-pct", type=float, required=True)
    s.add_argument("--active-ma", type=float, required=True)
    s.add_argument("--active-pct", type=float)
    s.add_argument("--tx-ma", type=float)
    s.add_argument("--tx-pct", type=float)
    s.set_defaults(fn=battery_life)

    s = sub.add_parser("crc16")
    s.add_argument("--data", required=True)
    s.add_argument("--poly", type=lambda x: int(x, 0), default=0x1021)
    s.add_argument("--init", type=lambda x: int(x, 0), default=0xFFFF)
    s.add_argument("--refin", action="store_true")
    s.add_argument("--refout", action="store_true")
    s.add_argument("--xorout", type=lambda x: int(x, 0), default=0)
    s.set_defaults(fn=crc16)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
