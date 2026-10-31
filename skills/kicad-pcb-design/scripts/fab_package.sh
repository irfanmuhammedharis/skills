#!/usr/bin/env bash
# fab_package.sh - build a complete, gated fabrication package from a KiCad project.
#
#   bash fab_package.sh <project.kicad_pro|project-dir> [options]
#
# Options:
#   --out DIR          output directory            (default: fab/<rev or date>)
#   --profile NAME     generic | jlcpcb | pcbway   (default: generic)
#   --layers LIST      override the gerber layer list
#   --variant NAME     KiCad 10 design variant to build
#   --rev TEXT         revision string used in the output folder and README
#   --no-gate          produce outputs even if ERC/DRC report violations (NOT for release)
#   --skip-3d          skip the STEP export (slow on big boards)
#
# Gates on `sch erc` and `pcb drc --schematic-parity`; exit code 5 from either means
# violations were found. Requires kicad-cli (KiCad 9 or 10) on PATH.

set -uo pipefail

PROJECT=""; OUT=""; PROFILE="generic"; LAYERS=""; VARIANT=""; REV=""
GATE=1; DO_3D=1

die() { echo "error: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

[[ $# -ge 1 ]] || { sed -n '2,20p' "$0"; exit 1; }
PROJECT="$1"; shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2;;
    --profile) PROFILE="$2"; shift 2;;
    --layers) LAYERS="$2"; shift 2;;
    --variant) VARIANT="$2"; shift 2;;
    --rev) REV="$2"; shift 2;;
    --no-gate) GATE=0; shift;;
    --skip-3d) DO_3D=0; shift;;
    *) die "unknown option: $1";;
  esac
done

have kicad-cli || die "kicad-cli not found on PATH (macOS: /Applications/KiCad/KiCad.app/Contents/MacOS/)"

# ------------------------------------------------------------------ locate files
if [[ -d "$PROJECT" ]]; then
  PRO=$(find "$PROJECT" -maxdepth 2 -name '*.kicad_pro' | head -1)
else
  PRO="$PROJECT"
fi
[[ -n "${PRO:-}" && -f "$PRO" ]] || die "no .kicad_pro found at '$PROJECT'"
DIR=$(cd "$(dirname "$PRO")" && pwd)
BASE=$(basename "$PRO" .kicad_pro)
SCH="$DIR/$BASE.kicad_sch"
PCB="$DIR/$BASE.kicad_pcb"
[[ -f "$SCH" ]] || die "missing schematic: $SCH"
[[ -f "$PCB" ]] || die "missing board: $PCB"

REV="${REV:-$(date +%Y%m%d)}"
OUT="${OUT:-$DIR/fab/$BASE-$REV}"
mkdir -p "$OUT"/{gerbers,reports,docs}

VARG=(); [[ -n "$VARIANT" ]] && VARG=(--variant "$VARIANT")

echo "project : $BASE"
echo "revision: $REV"
echo "profile : $PROFILE"
echo "output  : $OUT"
kicad-cli version | sed 's/^/kicad   : /'

# ------------------------------------------------------------------ gates
echo; echo "== ERC =="
kicad-cli sch erc --severity-error --exit-code-violations --units mm \
  --format json -o "$OUT/reports/erc.json" "$SCH"
ERC=$?
echo "== DRC (with schematic parity) =="
kicad-cli pcb drc --schematic-parity --severity-error --exit-code-violations \
  --refill-zones --units mm --format json -o "$OUT/reports/drc.json" "$PCB"
DRC=$?
echo "erc exit=$ERC  drc exit=$DRC   (0 = clean, 5 = violations)"
if [[ $GATE -eq 1 && ( $ERC -eq 5 || $DRC -eq 5 ) ]]; then
  die "violations found - see $OUT/reports/. Fix them, or re-run with --no-gate for a non-release build."
fi

# ------------------------------------------------------------------ layer list
if [[ -z "$LAYERS" ]]; then
  CU=$(grep -o '"In[0-9]*\.Cu"' "$PCB" | tr -d '"' | sort -u -V | paste -sd, -)
  LAYERS="F.Cu${CU:+,$CU},B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
fi
echo; echo "gerber layers: $LAYERS"

# ------------------------------------------------------------------ fabrication
echo "== gerbers =="
kicad-cli pcb export gerbers --output "$OUT/gerbers/" --layers "$LAYERS" \
  --subtract-soldermask --check-zones --no-protel-ext "${VARG[@]}" "$PCB" || die "gerber export failed"

echo "== drill =="
kicad-cli pcb export drill --output "$OUT/gerbers/" --format excellon \
  --drill-origin absolute --excellon-units mm --excellon-separate-th \
  --generate-map --map-format gerberx2 --generate-report \
  --report-path "$OUT/reports/drill.rpt" "$PCB" || die "drill export failed"

# ------------------------------------------------------------------ assembly
echo "== BOM =="
case "$PROFILE" in
  jlcpcb)
    FIELDS='Reference,Value,Footprint,${QUANTITY},LCSC,MPN,Manufacturer'
    LABELS='Designator,Comment,Footprint,Quantity,LCSC Part #,MPN,Manufacturer' ;;
  *)
    FIELDS='Reference,Value,Footprint,${QUANTITY},MPN,Manufacturer,Datasheet'
    LABELS='Designator,Value,Footprint,Qty,MPN,Manufacturer,Datasheet' ;;
esac
kicad-cli sch export bom --output "$OUT/bom.csv" \
  --fields "$FIELDS" --labels "$LABELS" \
  --group-by 'Value,Footprint' --sort-field Reference --exclude-dnp "${VARG[@]}" "$SCH" \
  || echo "warn: BOM export failed (check field names exist in the schematic)"

echo "== position / CPL =="
kicad-cli pcb export pos --output "$OUT/cpl.csv" --format csv --units mm --side both \
  --use-drill-file-origin --exclude-dnp --smd-only "${VARG[@]}" "$PCB" \
  || echo "warn: position export failed"

# ------------------------------------------------------------------ documentation
echo "== documentation =="
kicad-cli sch export pdf --output "$OUT/docs/$BASE-schematic.pdf" "${VARG[@]}" "$SCH" \
  || echo "warn: schematic PDF failed"
kicad-cli pcb export pdf --output "$OUT/docs/$BASE-assembly.pdf" --mode-multipage \
  --layers "F.SilkS,F.Fab,F.Cu,Edge.Cuts,B.SilkS,B.Fab,B.Cu" --include-border-title \
  --crossout-DNP-footprints-on-fab-layers --check-zones "${VARG[@]}" "$PCB" \
  || echo "warn: assembly PDF failed"
kicad-cli pcb export ipcd356 --output "$OUT/reports/$BASE-netlist.d356" "$PCB" \
  || echo "warn: IPC-D-356 export failed"
kicad-cli pcb export statistics --output "$OUT/reports/statistics.txt" "$PCB" 2>/dev/null \
  || true

if [[ $DO_3D -eq 1 ]]; then
  echo "== 3D (STEP) =="
  kicad-cli pcb export step --output "$OUT/docs/$BASE.step" --subst-models --no-dnp \
    --force "${VARG[@]}" "$PCB" || echo "warn: STEP export failed"
fi

# ------------------------------------------------------------------ archive
echo "== archive =="
( cd "$OUT/gerbers" && zip -q -j "../$BASE-$REV-gerbers.zip" ./* ) \
  || echo "warn: zip not available - send the gerbers/ directory contents (flat)"

cat > "$OUT/README.md" <<EOF
# $BASE - fabrication package $REV

Generated $(date -u '+%Y-%m-%d %H:%M UTC') by fab_package.sh (profile: $PROFILE${VARIANT:+, variant: $VARIANT})
Source: $(git -C "$DIR" describe --always --dirty 2>/dev/null || echo "not under git")

| File | Purpose |
|---|---|
| $BASE-$REV-gerbers.zip | send this to the fab (gerbers + drill, flat archive) |
| bom.csv | purchasing / assembly BOM (DNP excluded) |
| cpl.csv | placement file, drill-file origin, SMD only |
| docs/ | schematic PDF, assembly PDF, STEP model |
| reports/ | ERC and DRC JSON, drill report, IPC-D-356 netlist, statistics |

ERC exit code: $ERC   DRC exit code: $DRC   (0 = clean, 5 = violations)

Before ordering: open the gerbers in GerbView and check every layer, confirm the drill
table, verify CPL rotations against the assembler's convention, and send fab notes
(stackup, finish, impedance, tenting, special processes) with the order.
EOF

echo
echo "done -> $OUT"
ls -1 "$OUT"
