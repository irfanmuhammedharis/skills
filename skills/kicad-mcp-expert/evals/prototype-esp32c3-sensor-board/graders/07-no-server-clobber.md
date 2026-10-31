---
type: llm
focus: trace
weight: 1
---

The trace never calls mixelpixx save_project with force or forceExternalChanges set to true, and after any kicad (kicad-claude-mcp) tool wrote the board file while mixelpixx had it loaded, mixelpixx reload_board or open_project was called before further mixelpixx edits.
