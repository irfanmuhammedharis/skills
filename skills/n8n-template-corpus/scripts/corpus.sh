#!/usr/bin/env bash
# Mine a local n8n workflow corpus and validate workflow JSON.
# Usage:
#   corpus.sh node <node-type>            templates using that node type
#   corpus.sh grep <keyword>              templates matching a keyword
#   corpus.sh versions <node-type>        typeVersion frequency for a node type
#   corpus.sh common [n]                  top n most-used node types (default 30)
#   corpus.sh nodes <file.json>           node inventory of one workflow
#   corpus.sh schema <file.json> <type>   dump full node objects of that type
#   corpus.sh check <file.json>           validate structure before import
# Corpus path defaults to the AdNexus template folder; override with $N8N_CORPUS.
set -euo pipefail

CORPUS="${N8N_CORPUS:-/home/irfan/Documents/software/n8n ads/adnexus/template}"

need_corpus() {
  [ -d "$CORPUS" ] || { echo "corpus not found: $CORPUS (set \$N8N_CORPUS)" >&2; exit 1; }
}

# Walks the corpus, ignoring .git and unparseable files. $1 = per-workflow JS body,
# with `w` (workflow), `f` (path) in scope; $2 = summary JS body, with `acc` in scope.
scan() {
  node -e '
    const fs = require("fs"), path = require("path");
    const root = process.argv[1], perFile = process.argv[2], summary = process.argv[3];
    const arg = process.argv[4] || "";
    const files = [];
    (function walk(d) {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        if (e.name === ".git" || e.name === "node_modules") continue;
        const p = path.join(d, e.name);
        e.isDirectory() ? walk(p) : e.name.endsWith(".json") && files.push(p);
      }
    })(root);
    const acc = {};
    const fn = new Function("w", "f", "acc", "arg", "root", perFile);
    for (const f of files) {
      let w;
      try { w = JSON.parse(fs.readFileSync(f, "utf8")); } catch { continue; }
      if (!Array.isArray(w.nodes)) continue;
      fn(w, f, acc, arg, root);
    }
    new Function("acc", "arg", summary)(acc, arg);
  ' "$CORPUS" "$2" "$3" "${4:-}"
}

case "${1:-}" in
  node)
    need_corpus
    scan _ '
      if (w.nodes.some((n) => n.type === arg)) console.log(f.slice(root.length + 1));
    ' '' "$2" | sort
    ;;

  grep)
    need_corpus
    grep -ril --include=*.json --exclude-dir=.git -- "$2" "$CORPUS" \
      | sed "s|^$CORPUS/||" | sort
    ;;

  versions)
    need_corpus
    scan _ '
      for (const n of w.nodes) if (n.type === arg) {
        const v = String(n.typeVersion);
        acc[v] = (acc[v] || 0) + 1;
      }
    ' '
      const rows = Object.entries(acc).sort((a, b) => b[1] - a[1]);
      if (!rows.length) { console.error("no nodes of type " + arg + " in corpus"); process.exit(1); }
      const total = rows.reduce((s, [, c]) => s + c, 0);
      console.log(arg + "  (" + total + " instances)");
      for (const [v, c] of rows)
        console.log("  v" + v.padEnd(6) + String(c).padStart(4) +
                    "  " + Math.round((c / total) * 100) + "%");
    ' "$2"
    ;;

  common)
    need_corpus
    scan _ '
      for (const n of w.nodes) acc[n.type] = (acc[n.type] || 0) + 1;
    ' '
      const limit = Number(arg) || 30;
      for (const [t, c] of Object.entries(acc).sort((a, b) => b[1] - a[1]).slice(0, limit))
        console.log(String(c).padStart(5), t);
    ' "${2:-30}"
    ;;

  nodes)
    node -e '
      const w = require(process.argv[1]), c = {};
      for (const n of w.nodes || []) {
        const k = n.type + " (v" + (n.typeVersion ?? "?") + ")";
        c[k] = (c[k] || 0) + 1;
      }
      for (const [k, v] of Object.entries(c).sort()) console.log(String(v).padStart(3), k);
    ' "$(realpath "$2")"
    ;;

  schema)
    node -e '
      const w = require(process.argv[1]);
      const hits = (w.nodes || []).filter((n) => n.type === process.argv[2]);
      if (!hits.length) { console.error("no nodes of type " + process.argv[2]); process.exit(1); }
      console.log(JSON.stringify(hits, null, 2));
    ' "$(realpath "$2")" "$3"
    ;;

  check)
    node -e '
      const w = require(process.argv[1]);
      const errs = [], warns = [];
      if (!Array.isArray(w.nodes)) errs.push("nodes is not an array");
      if (!w.connections || typeof w.connections !== "object") errs.push("missing connections");

      const names = new Set(), dupes = new Set();
      for (const n of w.nodes || []) {
        if (names.has(n.name)) dupes.add(n.name);
        names.add(n.name);
        if (!n.type) errs.push(`node "${n.name}" has no type`);
        if (n.typeVersion === undefined) errs.push(`node "${n.name}" has no typeVersion`);
        if (n.continueOnFail) warns.push(`node "${n.name}" uses deprecated continueOnFail`);
      }
      for (const d of dupes) errs.push(`duplicate node name "${d}" — breaks connections`);

      const targeted = new Set(), attached = new Set();
      for (const [src, outs] of Object.entries(w.connections || {})) {
        if (!names.has(src)) errs.push(`connection source "${src}" is not a node`);
        for (const [kind, branches] of Object.entries(outs)) {
          // AI sub-nodes (model, tool, memory, parser...) attach by being the SOURCE
          // of an ai_* connection into their parent — they have no inbound edge.
          if (kind.startsWith("ai_")) attached.add(src);
          for (const branch of branches || []) {
            for (const link of branch || []) {
              if (!names.has(link.node)) errs.push(`"${src}" -> unknown node "${link.node}"`);
              targeted.add(link.node);
            }
          }
        }
      }

      for (const n of w.nodes || []) {
        if (n.type === "n8n-nodes-base.stickyNote") continue;
        // legacy start/interval are triggers too, despite not being named *Trigger
        const isTrigger = /trigger|webhook|cron|schedule|interval|emailReadImap/i.test(n.type)
          || n.type === "n8n-nodes-base.start";
        if (!isTrigger && !targeted.has(n.name) && !attached.has(n.name))
          warns.push(`node "${n.name}" is unreachable`);
      }

      if (w.pinData && Object.keys(w.pinData).length)
        warns.push(`pinData present (${Object.keys(w.pinData).length} nodes) — strip before production`);
      if ((w.settings || {}).executionOrder !== "v1")
        warns.push(`settings.executionOrder is not "v1"`);
      if (!(w.settings || {}).errorWorkflow)
        warns.push("no settings.errorWorkflow — failures will be invisible");

      const risky = (w.nodes || []).filter(
        (n) => /httpRequest|postgres|mysql|mongoDb|redis/i.test(n.type) && !n.retryOnFail
      );
      if (risky.length)
        warns.push(`${risky.length} network/DB node(s) without retryOnFail: ` +
                   risky.map((n) => n.name).join(", "));

      for (const s of JSON.stringify(w).match(/"(sk-|ghp_|xox[baprs]-)[A-Za-z0-9_-]{8,}"/g) || [])
        errs.push("possible hardcoded credential: " + s.slice(0, 18) + "...");

      if (warns.length) console.log(warns.map((x) => "  ! " + x).join("\n"));
      if (errs.length) { console.error(errs.map((e) => "  x " + e).join("\n")); process.exit(1); }
      console.log(`  ok ${(w.nodes || []).length} nodes, connections resolve`);
    ' "$(realpath "$2")"
    ;;

  *)
    sed -n '2,10p' "${BASH_SOURCE[0]}"
    exit 1
    ;;
esac
