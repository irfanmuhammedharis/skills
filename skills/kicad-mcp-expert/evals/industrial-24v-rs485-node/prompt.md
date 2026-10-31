---
tags: [skill-creator, kicad-mcp-expert]
max_turns: 120
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, ToolSearch, "mcp__kicad__*", "mcp__kicad-mixelpixx__*"]
---

We're building a field node for a factory cabinet: 24 V DC input (18-32 V, needs to survive IEC 61000-4-5 surge and reverse wiring), STM32G0 MCU, isolated RS-485 Modbus RTU port on a pluggable terminal block, 2 opto-isolated 24 V digital inputs, one high-side 24 V output up to 500 mA, -40 to +85 C. Production volume ~2k/yr, assembled at a CM. Set up the KiCad project in ./fieldnode, do the schematic and the board setup (stackup, netclasses, rules) and give me the placement plan. Don't route yet.
