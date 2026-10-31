#!/usr/bin/env bash
# Environment + project preflight for the two KiCad MCP servers.
# Usage: preflight.sh [project-dir]
# Exit 0 = ready, 1 = a blocker was found (details printed). Warnings don't fail.
set -u
PROJ="${1:-}"
fail=0
ok()   { printf '  [ok]   %s\n' "$*"; }
warn() { printf '  [warn] %s\n' "$*"; }
bad()  { printf '  [FAIL] %s\n' "$*"; fail=1; }

echo "== Toolchain"
if command -v kicad-cli >/dev/null; then ok "kicad-cli $(kicad-cli version 2>/dev/null)"; else bad "kicad-cli not on PATH (ERC/DRC/exports will not run)"; fi
if command -v java >/dev/null; then
  jv=$(java -version 2>&1 | head -1); ok "java: $jv"
else warn "java missing: Freerouting autoroute unavailable"; fi
FR="${FREEROUTING_JAR:-$HOME/kicad-claude-mcp/third_party/freerouting.jar}"
[ -f "$FR" ] && ok "freerouting jar: $FR" || warn "freerouting jar not found at $FR"
command -v ngspice >/dev/null && ok "ngspice: $(command -v ngspice)" || warn "ngspice missing: run_ngspice_simulation unavailable"
python3 -c "import pcbnew" 2>/dev/null && ok "pcbnew python module importable" || warn "system python cannot import pcbnew (mixelpixx uses its own env; usually fine)"

echo "== MCP server state"
IDX="${XDG_CACHE_HOME:-$HOME/.cache}/kicad-claude/index.json"
if [ -s "$IDX" ]; then ok "kicad library index: $(du -h "$IDX" | cut -f1), built $(date -r "$IDX" +%F)"; else warn "no library index: call mcp__kicad__index_libraries once (~60 s)"; fi
[ -f "$HOME/KiCAD-MCP-Server/dist/index.js" ] && ok "mixelpixx server build present" || warn "mixelpixx dist/index.js missing"
LOGDIR="$HOME/.kicad-mcp/logs"
[ -d "$LOGDIR" ] && ok "mixelpixx logs: $LOGDIR"
if pgrep -x kicad >/dev/null || pgrep -x pcbnew >/dev/null || pgrep -x eeschema >/dev/null; then
  warn "KiCad GUI is running: close it before file edits, or open the board there with IPC enabled and call open_project (IPC pin)"
  [ -S /tmp/kicad/api.sock ] && ok "IPC socket present (/tmp/kicad/api.sock)" || warn "no IPC socket: enable Preferences > Plugins > IPC API Server"
fi

if [ -n "$PROJ" ]; then
  echo "== Project: $PROJ"
  if [ -d "$PROJ" ]; then
    pro=$(find "$PROJ" -maxdepth 1 -name '*.kicad_pro' | head -1)
    [ -n "$pro" ] && ok "project file: $(basename "$pro")" || warn "no .kicad_pro yet (new project?)"
    locks=$(find "$PROJ" -maxdepth 1 -name '*.lck' 2>/dev/null)
    if [ -n "$locks" ]; then bad "KiCad lock files present: GUI has the project open and may overwrite MCP edits:"; echo "$locks" | sed 's/^/           /'; fi
    for f in "$PROJ"/*.kicad_sch "$PROJ"/*.kicad_pcb; do
      [ -f "$f" ] || continue
      ok "$(basename "$f"): $(wc -c <"$f") bytes, modified $(date -r "$f" '+%F %T')"
    done
    compgen -G "$PROJ/*.kicad_dru" >/dev/null && ok "custom rules (.kicad_dru) present" || warn "no .kicad_dru: board-specific rules not set yet"
    if command -v kicad-cli >/dev/null; then
      for s in "$PROJ"/*.kicad_sch; do
        [ -f "$s" ] || continue
        if kicad-cli sch export netlist --format kicadxml -o /dev/null "$s" >/dev/null 2>&1; then ok "kicad-cli parses $(basename "$s")"; else bad "kicad-cli cannot parse $(basename "$s")"; fi
      done
    fi
  else
    warn "project dir does not exist yet (will be created)"
  fi
fi

echo
[ $fail -eq 0 ] && echo "PREFLIGHT: ready" || echo "PREFLIGHT: blockers found (see FAIL lines)"
exit $fail
