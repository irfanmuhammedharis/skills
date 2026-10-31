---
name: software-docs-suite
description: >-
  Generate a complete, high-quality software documentation suite in Markdown that an AI coding
  agent can follow to build (or rebuild) a product end to end. Produces a folder of linked .md
  files covering product brief, requirements, architecture, data model, API, UI/UX, security,
  testing strategy, an ordered AI-agent build plan, deployment/ops, and an agent operating manual
  (which skills to invoke per task, coding standards, and how to write and verify tests so the
  software actually works). Use this skill whenever the user wants to "document a product/app/system,"
  write specs or a build blueprint, produce docs for AI-driven development, spec out something so
  Claude Code or another agent can build it, or document an existing codebase — even if they don't
  say the word "documentation." Handles both a fresh product idea and an existing repo.
---

# Software Documentation Suite

Produce a documentation suite that is detailed enough to serve as the **single source of truth for
building software with AI coding agents**. The output is not marketing docs or a wiki — it is an
executable blueprint. A capable agent (Claude Code, a terminal agent, an IDE agent like Cursor, or
a tool-agnostic one) should be able to open the suite and build the product to completion, with
tests, without needing to ask the user to re-explain the vision.

Quality bar: every document must be specific, decision-complete, and verifiable. Vague docs produce
broken software. Prefer concrete schemas, exact endpoint contracts, explicit acceptance criteria,
and named verification gates over prose that "describes the general idea."

---

## Step 0 — Detect the mode

Two entry modes. Detect which one you're in before doing anything else.

- **Greenfield (idea → docs).** The user has a product idea, brief, or feature request and no code
  yet (or a near-empty repo). You will *design* the system and write the docs that specify it.
- **Brownfield (codebase → docs).** A repository already exists. Inspect it and write docs that
  accurately describe what's there, then layer on the forward-looking plan for what's left to build.

If you can see files, list the project root and check for source directories, a manifest
(`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.), and existing docs. Real code
present → brownfield. Only a README or nothing → greenfield. When unsure, ask the user once.

In brownfield mode, **read before you write**: sample the manifest, entry points, route/handler
files, data models/migrations, config, and existing tests. Docs must reflect reality, not
assumptions. Mark anything you infer (vs. confirmed from code) so it can be checked.

---

## Step 1 — Gather just enough to be decision-complete

You cannot write decision-complete docs from a one-line prompt. Collect the essentials, but don't
interrogate — infer sensible defaults from the brief or codebase and mark them `[ASSUMPTION]` so the
user can correct them. Cover at minimum:

- **Product**: problem, target users, the core jobs-to-be-done, and 3–5 measurable success metrics.
- **Scope**: what's in the MVP vs. explicitly out (an out-of-scope list prevents agent scope-creep).
- **Constraints**: required stack/hosting/budget, compliance, deadlines, existing systems to integrate.
- **Non-functionals**: expected scale, latency, availability, security/privacy sensitivity.

Ask the user only for the few answers that would meaningfully change the architecture (e.g. "must
this be offline-first?", "is there a hard stack constraint?"). Everything else: default and mark it.

---

## Step 2 — Scaffold the suite

Create the folder structure. Use the helper for a clean, consistent skeleton:

```bash
python3 scripts/scaffold_docs.py <output-dir> --name "<Product Name>"
```

The suite layout (adapt — drop UI docs for a headless service, add docs for extra subsystems):

```
docs/
├── README.md                     # Index + how an agent should use this suite. Read first.
├── 00-product-brief.md           # Vision, users, jobs-to-be-done, success metrics, scope/out-of-scope
├── 01-requirements.md            # Functional + non-functional reqs, user stories, acceptance criteria
├── 02-architecture.md            # System design, components, tech stack + rationale, diagrams-as-text
├── 03-data-model.md              # Entities, schemas, relationships, migrations, seed/fixture data
├── 04-api-spec.md                # Endpoints/contracts, request+response, error model, auth, examples
├── 05-ui-ux.md                   # Screens, flows, states, components (omit for headless/back-end-only)
├── 06-security.md                # AuthN/Z, secrets, threat model, data handling, compliance
├── 07-testing-strategy.md        # Test pyramid, coverage gates, how to write + run + verify tests
├── 08-build-plan.md              # ORDERED agent task list: deps, per-task skill, Definition of Done
├── 09-deployment-ops.md          # Environments, CI/CD, infra, config, monitoring, rollback, runbooks
├── AGENTS.md                     # Operating manual for the AI dev agent (see Step 4). Agent reads this + README first.
├── glossary.md                   # Domain terms + acronyms, so the agent uses names consistently
├── decisions/                    # Architecture Decision Records (ADRs), one file per decision
│   └── 0001-example.md
└── CHANGELOG.md                  # Kept current as the agent builds
```

Numbered prefixes give the agent a natural reading order. `README.md` and `AGENTS.md` are the two
entry points every agent must read before touching code.

---

## Step 3 — Write each document to the template

Fill in each document using the templates in **`references/document-templates.md`**. Read that file
now — it contains the exact structure, required sections, and worked mini-examples for every doc in
the suite. Follow it rather than improvising structure, so the suite is consistent and predictable
for the consuming agent.

Non-negotiables while writing:

- **Requirements carry acceptance criteria.** Every user story ends in testable criteria
  (Given/When/Then or an explicit checklist). If it can't be tested, it isn't done — rewrite it.
- **Contracts are exact.** Data schemas specify types, nullability, constraints, and keys. API
  endpoints specify method, path, auth, full request/response shapes, status codes, and error bodies.
  An agent must be able to implement straight from the spec with zero guessing.
- **Every significant choice becomes an ADR.** Stack, database, auth approach, sync vs. async, etc.
  go in `decisions/` with context, the options considered, the decision, and consequences. This stops
  the agent from silently re-litigating settled choices.
- **Cross-link.** Use relative links between docs so the agent can navigate (`see [data model](03-data-model.md)`).
- **Mark uncertainty.** `[ASSUMPTION]` for defaults you chose, `[TODO]` for genuine open questions,
  `[INFERRED]` for brownfield facts read from code but not confirmed. Never present a guess as settled.

---

## Step 4 — Write the agent instructions (the part that makes it buildable)

This is the differentiator: the suite doesn't just describe the product, it **instructs the AI agent
how to build it**. Two documents do the heavy lifting.

### `08-build-plan.md` — the ordered execution plan

Decompose the product into a dependency-ordered sequence of build tasks (foundation → data layer →
core logic → API → UI → integration → hardening). Each task specifies:

- **Goal** — one sentence, outcome-focused.
- **Depends on** — task IDs that must be complete first.
- **Which skill(s) to use** — name the concrete tool/skill the agent should reach for (e.g. use the
  relevant framework/document skill for spreadsheet, docx, pdf output; project scaffolding commands;
  a testing framework). If the agent has a skill for the task, say so explicitly.
- **Steps** — the concrete work.
- **Tests to write** — the specific tests that prove this task works (see `07-testing-strategy.md`).
- **Definition of Done** — a checklist the agent must satisfy *and verify* before moving on, always
  including "tests written and passing" and "no regressions."

### `AGENTS.md` — the operating manual

The standing rules the agent follows throughout. Use the template in
**`references/agent-instructions.md`** (read it). It covers: how to read the suite, coding standards
and conventions, the build loop (implement → test → verify → commit), which skills to invoke for
which kinds of work, how to handle blockers/ambiguity, and the hard rule that **a task is not done
until its tests pass and the change is verified end to end**.

For the testing philosophy, coverage gates, test-type definitions, and the concrete verify loop the
agent must run to confirm the software actually works, read and adapt
**`references/testing-and-verification.md`** into `07-testing-strategy.md`.

---

## Step 5 — Self-review against the completeness checklist

Before handing the suite over, verify it against the checklist in
**`references/document-templates.md` → "Completeness checklist"**. The core test: *could a competent
agent that has never spoken to the user build the product to a passing test suite using only these
files?* If any answer requires knowledge that's only in your head or the chat, it belongs in the docs.

Common gaps to catch: missing error/edge-case behavior, unspecified auth, no seed data, acceptance
criteria that aren't actually testable, a build plan with hidden dependencies, and testing docs that
describe *what* to test but not *how to run and verify* it.

---

## Output & delivery

Write the suite to a real directory (default `./docs/` or a path the user gives). Because these are
many linked files that the user (and their agent) will keep and edit, write actual files — don't dump
the whole suite inline in chat. When done, tell the user where the suite is and give a short tour of
what each top-level doc contains and the recommended reading order for their agent
(`README.md` → `AGENTS.md` → `00` … → `08-build-plan.md`).

If the user only wants one or two documents rather than the full suite, generate just those using the
same templates — the templates stand alone.

---

## Reference files

- `references/document-templates.md` — exact template + mini-example for every document, plus the
  completeness checklist. Read before Step 3.
- `references/agent-instructions.md` — the `AGENTS.md` operating-manual template and skill-assignment
  guidance. Read before Step 4.
- `references/testing-and-verification.md` — testing strategy, coverage gates, test-type definitions,
  and the agent verify loop. Read before writing `07-testing-strategy.md`.
- `scripts/scaffold_docs.py` — creates the empty suite skeleton with numbered files and front-matter.
- `assets/adr-template.md` — copy into `decisions/` for each architecture decision.
