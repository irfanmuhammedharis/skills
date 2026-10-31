# skills

Agent skills for Claude Code, Codex, Cursor, OpenCode and other agents that read `SKILL.md`.

## Install

```
npx skills add irfanmuhammedharis/skills -g
```

One skill only:

```
npx skills add irfanmuhammedharis/skills -g --skill kicad-mcp-expert
```

## Skills

| Skill | What it does |
| --- | --- |
| [`hk32f103`](skills/hk32f103/SKILL.md) | Build, flash and debug HK32F103 (Hangshun / 航顺) Cortex-M3 boards — HK32F103C8T6, C8T6A, CBT6A, VET6 — in PlatformIO. Use when a project targets an HK32F103... |
| [`kicad-mcp-expert`](skills/kicad-mcp-expert/SKILL.md) | Drive KiCad 10 through the KiCad MCP servers (`mcp__kicad__*` and `mcp__kicad-mixelpixx__*`) the way a senior circuit and PCB designer would, from a rough... |
| [`pi-zero-2w`](skills/pi-zero-2w/SKILL.md) | Build and run Rust, Python and C on a Raspberry Pi Zero 2 W (and Zero W v1). Use when targeting a Pi Zero, cross-compiling for ARM, choosing armhf vs arm64,... |
| [`skill-orchestrator`](skills/skill-orchestrator/SKILL.md) | Runs first on any non-trivial task: turns the request into a metaprompt via prompt-architect, picks skills from a once-per-project cached registry, and... |

## Licence

MIT. See [LICENSE](LICENSE).
