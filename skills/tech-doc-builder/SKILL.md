---
name: tech-doc-builder
description: Generate exhaustive, AI-implementable technical product documentation from a project brief or requirements description. Produces a complete spec covering architecture, per-feature UI specs, API contracts, backend logic, database schemas (DDL), data pipelines (Mermaid), testing plans (Given/When/Then), error handling, logging, security, and performance — detailed enough that an AI coding agent can implement the entire product without guessing. Use this skill WHENEVER the user asks to "create product documentation", "generate technical documentation", "write a tech spec", "create a PRD/SRS/technical design doc", "document this project/feature", "prepare docs for an AI agent to build", or pastes/uploads a project brief and asks for documentation, specs, or a build plan — even if they don't say the word "documentation" explicitly.
---

# Tech Doc Builder

Generates a single, self-contained technical documentation file from a project brief. The output is designed for **AI agent consumption**: an AI coding agent reading the finished document must be able to implement the entire product without guessing.

## Workflow

1. **Ingest the brief.** Accept the project brief as pasted text or an uploaded file (read it from `/mnt/user-data/uploads/` if uploaded). Do not ask clarifying questions about missing details — fill gaps with reasonable architectural assumptions and mark each one inline with `[ASSUMPTION]`.
2. **Identify features.** Extract the distinct features from the brief. Each feature gets its own full 3.X section. If the brief contains **8 or more features**, list them and ask the user which to document (default: all). Under 8, proceed without asking.
3. **Choose the stack.** If the brief specifies a tech stack, use it exactly and match its naming conventions (camelCase vs snake_case, etc.). If not, assume a sensible modern default and mark it `[ASSUMPTION]` — e.g., Next.js 14 + TypeScript frontend, NestJS (or FastAPI if Python signals present) backend, PostgreSQL, Redis, Docker.
4. **Read the template.** Load `references/template.md` and follow its structure **exactly** — every numbered section, every sub-section, in order. Do not skip sections; if a section genuinely does not apply (e.g., no background jobs), state "Not applicable — <one-line reason>" rather than omitting it.
5. **Write the document** to `/home/claude/` first, then copy the final version to `/mnt/user-data/outputs/<project-slug>-technical-documentation.md` and share with `present_files`.
6. **Offer DOCX export.** After delivering the Markdown, offer: "I can also export this as a branded HexCodePlus Word document if you need a client-facing version." Only build the DOCX if accepted (use the docx skill; HexCodePlus brand: navy #0B2C4D, teal #1B8A8A, Calibri labels, EB Garamond body, A4, 0.75in side margins).

## Writing Rules (critical — apply to every section)

- **Exhaustive, not verbose.** When in doubt, provide the schema or code snippet instead of prose.
- **Consistent naming** exactly matching the codebase/stack conventions chosen in step 3. Never mix camelCase and snake_case for the same layer.
- **API contracts** must be machine-parseable: OpenAPI 3.1 YAML snippets or JSON Schema for every endpoint (method, path, auth, request body, response bodies per status code, error envelope).
- **Database schemas** as DDL (`CREATE TABLE ...`) or ORM model definitions, plus the summary table format from the template. Include constraints, indexes, and FK relationships.
- **State machines and flows** in Mermaid (preferred) — sequence diagrams for request lifecycles, `stateDiagram-v2` for status transitions, `erDiagram` for relationships. Validate that Mermaid syntax is well-formed.
- **Testing** in strict `Given / When / Then` format referencing exact function/component names defined earlier in the doc.
- **No placeholder text.** Every section filled with concrete details. `[INSERT X]`, `TBD`, and `...` are forbidden. Missing info → invent a reasonable concrete answer and tag `[ASSUMPTION]`.
- **Self-contained.** No references to external documents that don't exist. Define all domain terms in the Glossary (section 6).
- **Error handling** must enumerate every failure state with detection mechanism and the exact HTTP status + response body.

## Quality checklist (run before delivering)

- [ ] All template sections present (1, 2, 3.X.1–3.X.11 per feature, 4, 5, 6)
- [ ] Zero placeholders/TBDs; all gaps tagged `[ASSUMPTION]`
- [ ] Every endpoint has an OpenAPI/JSON Schema contract
- [ ] Every table has DDL + summary table
- [ ] At least one Mermaid sequence diagram per feature
- [ ] All test cases in Given/When/Then referencing real names from the doc
- [ ] Naming consistent throughout
- [ ] Glossary covers every domain term used

## Resources

- `references/template.md` — the full document template. **Always read this before writing.**
