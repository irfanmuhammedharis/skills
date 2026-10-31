# Testing & Verification Guide

Write `07-testing-strategy.md` from this file, adapting specifics (frameworks, commands, thresholds)
to the project's stack. The goal is not "tests exist" — it's that the agent can **prove the software
works** and knows exactly when a task is finished. Underspecified testing docs are the number-one
reason AI-built software looks done but isn't.

---

## Philosophy

- **A task is not done until its tests pass and the change is verified end to end.** State this in
  the docs and enforce it in every task's Definition of Done. It is the load-bearing rule.
- **Test behavior, not implementation.** Tests assert observable outcomes (return values, state
  changes, responses), so they survive refactors.
- **Every requirement traces to a test.** If a functional requirement has no test, it is not
  actually delivered. Keep the traceability table in `01-requirements.md` current.
- **Cover the unhappy path.** Invalid input, auth failures, empty/limit/boundary conditions, and
  concurrency where relevant — not just the happy path.

## The test pyramid

Specify the mix for this project. A typical shape:

- **Unit (most):** pure functions and single units in isolation. Fast, no I/O.
- **Integration (some):** units wired together with real adjacent dependencies (DB, in-process API).
- **End-to-end (few):** the whole system exercised as a user would, through its real entry points.
- **Contract (as needed):** verify API request/response shapes match `04-api-spec.md`; guards against
  drift between producer and consumer.

State roughly how many of each and why, given the product's risk profile.

## Coverage gates

Give concrete numbers so "done" is objective, e.g.:

- Overall line coverage ≥ 80%; core domain logic ≥ 90%.
- 0 known-failing tests on the main branch.
- Every new build-plan task adds tests for its new behavior (no untested code merged).

Coverage is a floor, not a goal — a green bar with meaningless assertions is worse than honest gaps.
Tell the agent to assert real outcomes, not just execute lines.

## Test types — when to use each

| Type | Use it to verify | Speed |
|------|------------------|-------|
| Unit | A single function/class behaves per spec, incl. edge cases | Fast |
| Integration | Components work together (e.g. API → service → DB) | Medium |
| E2E | A full user flow works through real entry points | Slow |
| Contract | API shapes match the spec exactly | Fast |
| Regression | A previously fixed bug stays fixed (add one per bug) | Varies |

## How to write a good test

- **Name states the behavior:** `create_task_rejects_empty_title`, not `test_task_1`.
- **Arrange → Act → Assert**, one behavior per test.
- **Deterministic:** no reliance on wall clock, network, or random unless seeded/mocked.
- **Independent:** any order, no shared mutable state; each test sets up and tears down its own data.
- **Meaningful assertions:** check the actual result and side effects, not just "no exception."

## How to run tests (fill in exact commands)

Give the literal commands for this stack so the agent runs them verbatim, e.g.:

```
# unit + integration
<test runner command>            # e.g. pytest -q   |   npm test   |   go test ./...   |   cargo test
# coverage
<coverage command>               # e.g. pytest --cov   |   npm run test:coverage
# e2e
<e2e command>
# lint / typecheck / build (also gates)
<lint> && <typecheck> && <build>
```

## The verify loop (the agent runs this to confirm real working)

This is the concrete loop the agent executes for every build-plan task before marking it done. Put
it verbatim in `07-testing-strategy.md` and reference it from `AGENTS.md`:

1. **Implement** the task per its spec.
2. **Write tests** for the new behavior (happy + unhappy paths) per this guide.
3. **Run the focused tests** for the change. Red → fix and repeat. Never edit a test just to make it
   pass unless the test itself is genuinely wrong.
4. **Run the full suite** to catch regressions. All green required.
5. **Run lint, typecheck, and build** — these are gates too.
6. **Verify end to end at the real boundary.** Don't trust green unit tests alone: actually exercise
   the feature the way a user/client would — call the running endpoint, drive the UI flow, run the
   CLI, or execute the script against realistic data — and confirm the observable outcome matches the
   acceptance criteria. For anything with a runnable surface, boot it and hit it.
7. **Check the Definition of Done** for the task; update `CHANGELOG.md`.
8. Only now move to the next task.

If a step can't be completed (missing dependency, ambiguous spec), stop and record a `[TODO]` /
blocker per `AGENTS.md` rather than faking a pass.

## Test data & fixtures

Point the agent at the seed/fixture data in `03-data-model.md`. Tests must create and clean up their
own data. Prefer factories/builders over copy-pasted literals so tests stay readable and maintainable.

## CI gate

Define the single gate that blocks a bad merge — typically: full test suite green **and** coverage
threshold met **and** lint/typecheck/build pass. If CI exists, wire these in `09-deployment-ops.md`.
