#!/usr/bin/env python3
"""Self-test for the circuit-diagram skill.

Proves verify_diagram.py PASSES correct diagrams and FAILS broken ones.
Run:  python3 tests/test_checker.py   (from the skill root)
Exit 0 = all tests pass.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERIFY = ROOT / "scripts" / "verify_diagram.py"
GOOD_SVG = ROOT / "examples" / "led-blink-breadboard.svg"
GOOD_SPEC = ROOT / "examples" / "led-blink-wiring.json"
GOOD_CODE = ROOT / "examples" / "led-blink.ino"

PASSED, FAILED = [], []


def run_checker(svg, spec=None, code=None):
    cmd = [sys.executable, str(VERIFY), "--svg", str(svg)]
    if spec:
        cmd += ["--spec", str(spec)]
    if code:
        cmd += ["--code", str(code)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}  {detail}")


def make_broken(tmp):
    """Break the good example in 3 ways: wrong pin wire, missing label, dangling wire."""
    text = pathlib.Path(GOOD_SVG).read_text()
    # 1) wire the signal to D9 (446,348) instead of D13 (446,436)
    text = text.replace('d="M446 436 Q 520 300 590 270"', 'd="M446 348 Q 520 300 590 270"')
    # 2) drop the LED1 label
    text = re.sub(r'<text x="662" y="256"[^>]*>LED1</text>\n', "", text)
    # 3) add a dangling wire from a hole to empty space
    text = text.replace('<g id="wires">',
        '<g id="wires">\n    <path class="wire" d="M734 270 L880 170" stroke="#1e88e5" stroke-width="4" fill="none"/>')
    broken = tmp / "broken.svg"
    broken.write_text(text)
    return broken


def main():
    print("== test 1: correct example must PASS ==")
    rc, out = run_checker(GOOD_SVG, GOOD_SPEC, GOOD_CODE)
    check("good example passes (exit 0)", rc == 0, f"rc={rc}\n{out}")

    print("== test 2: broken diagram must FAIL with specific errors ==")
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        broken = make_broken(tmp)
        rc, out = run_checker(broken, GOOD_SPEC)
        check("broken diagram fails (exit 1)", rc == 1, f"rc={rc}")
        check("catches wrong-pin wire (missing D13->e1)", "missing wire: D13 -> e1" in out, out)
        check("catches dangling wire", "dangles" in out, out)
        check("catches missing label", 'missing component label "LED1"' in out, out)

    print("== test 3: code/spec pin mismatch must FAIL ==")
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        code = tmp / "bad.ino"
        code.write_text(GOOD_CODE.read_text().replace("int ledPin = 13;", "int ledPin = 9;"))
        rc, out = run_checker(GOOD_SVG, GOOD_SPEC, code)
        check("code mismatch fails (exit 1)", rc == 1, f"rc={rc}")
        check("reports 'code uses pin 9'", "code uses pin 9" in out, out)

    print("-" * 40)
    if FAILED:
        print(f"RESULT: {len(FAILED)} failed, {len(PASSED)} passed")
        return 1
    print(f"RESULT: all {len(PASSED)} tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
