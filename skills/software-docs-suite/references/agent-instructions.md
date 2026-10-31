# Agent Instructions Guide

Use this to write the `AGENTS.md` file that ships inside the suite. `AGENTS.md` is the operating
manual the AI coding agent reads first and obeys throughout the build. It is what turns a pile of
specs into something an agent can execute reliably.

Copy the template below into the suite's `AGENTS.md`, then tailor the bracketed parts to the
project's stack, conventions, and the specific skills/tools the consuming agent has available.

---

## Skill-selection guidance (how to fill the "which skill to use" parts)

Throughout `AGENTS.md` and `08-build-plan.md`, tell the agent *which concrete capability to reach for*
rather than leaving it to guess. Map task kinds to tools:

- **Producing office files** (Word/Excel/PowerPoint/PDF output as a product feature or deliverable) →
  the corresponding document skill (docx, xlsx, pptx, pdf).
- **Front-end / UI work** → the project's chosen framework, plus any design skill or design-tool
  connector (e.g. Figma) named in `05-ui-ux.md` so layout comes from real specs.
- **Scaffolding / running code** → the stack's standard CLI (package manager, project generator,
  migration tool, test runner) — name the exact commands.
- **Testing** → the project's test framework and the commands in `07-testing-strategy.md`.
- **External services / data** → the relevant connector or API client, with auth handled per
  `06-security.md`.

If the consuming agent has a skill registry, instruct it to consult the skill list when a task
matches a known skill's trigger, and to prefer a purpose-built skill over ad-hoc code. If you don't
know what skills the agent has, phrase it capability-first ("use your spreadsheet-generation
capability") so it maps regardless of the toolset — this keeps the suite portable across Claude Code,
IDE agents, and tool-agnostic agents.

---

## AGENTS.md template

```markdown
# AGENTS.md — Operating Manual for the AI Development Agent

You are building <Product Name>. This file is your standing instruction set. Follow it for every
task. When this file and a specific doc disagree, the specific doc wins for that detail; when in
doubt about process, this file wins.

## 1. Before you write any code
- Read `README.md`, then this file, then `00`–`07`, then `08-build-plan.md`.
- Build strictly from `08-build-plan.md`, in order. Do not skip ahead of unmet dependencies.
- If anything is ambiguous or missing, do NOT invent product behavior. Record it as a `[TODO]` in the
  relevant doc and either ask or proceed with a clearly-marked `[ASSUMPTION]` — never a silent guess.

## 2. Coding standards
- Language/style: <formatter, linter, style guide, naming conventions>.
- Structure: follow the repository layout in `02-architecture.md`. Put things where the docs say.
- Cross-cutting conventions (config, logging, error handling) per `02-architecture.md`. Reuse them;
  don't reinvent per file.
- Commits: small and scoped; one logical change per commit; message says what and why.
- Never commit secrets. Config via env vars per `06-security.md`.

## 3. The build loop (run for EVERY task)
1. Read the task in `08-build-plan.md` and its referenced spec sections.
2. Implement the smallest correct version that satisfies the acceptance criteria.
3. Write tests for the new behavior — happy path AND unhappy path — per `07-testing-strategy.md`.
4. Run the focused tests → fix until green. Don't weaken a test to pass it.
5. Run the full suite + lint + typecheck + build. All must pass (no regressions).
6. Verify end to end at the real boundary (call the endpoint / drive the UI / run the script against
   realistic data) and confirm the observable result matches the acceptance criteria.
7. Tick the task's Definition of Done; update `CHANGELOG.md`.
8. Only then start the next task.

A task is DONE only when steps 3–7 are all satisfied. Green unit tests alone are not "done."

## 4. Which skill/tool to use
<Fill from the skill-selection guidance: map the project's task kinds to concrete skills/tools/
commands. Tell the agent to prefer a purpose-built skill over ad-hoc code, and to consult its skill
list when a task matches a skill's trigger.>

## 5. Decisions
Any non-trivial technical choice → add an ADR in `decisions/` (use `assets/adr-template.md`) before
implementing. Don't silently re-decide something an existing ADR already settled.

## 6. When you're blocked
- Missing dependency/tool: stop, note it, surface it — don't fake around it.
- Ambiguous requirement: mark `[TODO]`, pick the lowest-risk interpretation, flag it for the user.
- A test reveals the spec is wrong: fix the spec (and its ADR) first, then the code, then the test.
- Never delete or skip a failing test to make the build green.

## 7. Definition of Done (global)
The product is done when: all build-plan tasks are complete; every functional requirement traces to a
passing test; coverage gates in `07-testing-strategy.md` are met; lint/typecheck/build/CI are green;
and the system has been verified end to end against the acceptance criteria in `01-requirements.md`.
```

---

## Notes for tailoring

- Keep `AGENTS.md` short and imperative — it's read every task; bloat gets skimmed.
- Make the standing rules match the project's real tooling. A rule the agent can't follow (a command
  that doesn't exist, a skill it doesn't have) erodes trust in the whole file.
- The two rules that matter most, stated plainly: **build in order from the plan**, and **not done
  until tested and verified end to end**. Everything else supports those.
