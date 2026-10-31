---
name: hermes-bizdev-editor
description: "Edit, extend, and debug the custom Hermes bizdev agent (Python CLI + n8n email integration) safely and correctly. Use when modifying src/, adding tools or adapters, touching the n8n email pipeline, rebuilding the Docker image, or diagnosing why inbound/outbound mail is broken."
version: 1.0.0
author: operator
license: MIT
metadata:
  project: hermesagent (custom bizdev agent, NOT NousResearch Hermes)
---

# Hermes Bizdev Agent — Editor's Skill

Operating manual for modifying this repository. It encodes the architecture,
the invariants that must never be broken, and the failure modes already paid
for in debugging time. Read the routing table and load what matches; do not
freestyle edits against this codebase.

**Disambiguation:** this is NOT the NousResearch `hermes-agent` product. This
is a bespoke Python agent (`src/`, Click CLI, SQLite CRM, YAML knowledge
base) that integrates with a dockerized n8n for email. Different codebase,
different rules. For n8n-side operations load the repo's `N8N.md`.

## Repository map

```
src/cli.py            Click CLI: run, chat, crm, email (serve/send/test-inbound), config
src/engine.py         WorkflowEngine — system-prompt build + agentic tool loop
src/providers.py      OpenAI/Anthropic provider factory (keys from env only)
src/personas.py       Role prompts with [[COMPANY_KB]] sentinel
src/kb.py             kb/*.yaml loader — fail-soft, filters placeholder: true
src/tools.py          Agent tools: crm_*, web_search, fetch_url, email_send_followup
src/crm.py            SQLite CRM — system of record
src/email_adapter.py  Inbound triage + outbound send (n8n-backed, dry-run gated)
src/webhook.py        Inbound HTTP receiver (shared-secret auth)
config/hermes.yaml    Defaults; real values come from HERMES_* env vars
tests/                pytest, one file per module — run before/after ANY change
N8N.md                n8n operations: published-version gotcha, payload contract
HERMES.md             Architecture & phase roadmap — update at phase boundaries
```

## Commands that must stay green

```bash
.venv/bin/python -m pytest -q                       # full suite
.venv/bin/python -m pytest tests/test_email.py -q   # after touching mail code
docker compose up -d --build hermes                 # code is baked into the image —
                                                    # container sees edits only after rebuild
```

Known pre-existing failure: `tests/test_email.py::test_analyze_excludes_email_send_followup_from_the_engine`
fails without a live `OPENAI_API_KEY` in the environment. It is not a
regression signal — check with `git stash` + rerun if unsure.

## Invariants (violating these breaks trust or security)

1. **Fail-soft everywhere.** A broken adapter, KB file, or payload returns
   `{"ok": False, "error": ...}` or renders a warning — it never raises into
   the caller, never crashes the webhook receiver, never silently drops a
   message. Match this pattern in new code.
2. **Secrets live in env / `.env`, never in `config/hermes.yaml` or code.**
   Providers read `*_API_KEY` env vars; the webhook reads
   `HERMES_EMAIL_INBOUND_SECRET`; nothing else may hold credentials.
3. **Dry-run is the default for every external side-effect.**
   `HERMES_EMAIL_DRY_RUN` defaults true; a dry-run "send" is a CRM log entry,
   never a network call. New outbound adapters must replicate this gate.
4. **`email_send_followup` stays out of the inbound-analysis engine.**
   `_analyze` feeds attacker-controlled email bodies into a tool-enabled
   model; `exclude_tools=frozenset({"email_send_followup"})` must remain, and
   no new send-capable tool may be reachable from that path.
5. **CRM writes are deterministic where correctness matters.** Triage → CRM
   sync runs in `_sync_crm_classification` with no LLM in the path, and
   `tag_company`/`set_status` are idempotent. Never route state changes
   solely through model tool calls.
6. **Never downgrade pipeline state.** `potential_client` sets `lead` only
   from `None`/`lead`/`disqualified`; `important` touches tags only. Preserve
   this asymmetry.
7. **Classification fallback is `important`** — never `junk` (would
   disqualify real mail) and never `potential_client` (would inflate the
   pipeline). Unparseable model output must surface for human review.
8. **Hermes never holds mail credentials.** All mail I/O goes through n8n
   webhooks; Hermes exchanges JSON only. Do not add IMAP/SMTP client code.

## How to make common changes

**Add an agent tool** (`src/tools.py`): define the function + schema,
register in the tool dispatch, add tests in `tests/test_tools.py`. If it has
external side-effects, dry-run gate it (invariant 3) and decide explicitly
whether `_analyze`'s `exclude_tools` must list it (invariant 4).

**Add an inbound field / new n8n payload shape** (`src/email_adapter.py`):
extend `InboundEmail.from_payload` — it already normalizes three shapes
(Gmail capitalised, IMAP string, IMAP object) via `_first`/`_address_value`.
Add a `test_inbound_email_accepts_*` regression test. The n8n contract is
`jsonBody: ={{ $json }}` — keep normalization on the Hermes side, never
per-field expressions in n8n.

**Change the webhook contract** (`src/webhook.py`): keep the 503-when-
unconfigured and 401-on-wrong-secret behaviour; keep `MAX_BODY_BYTES`.
Tests: `test_webhook_*` in `tests/test_email.py`.

**Touch the container**: after editing `src/`, rebuild —
`docker compose up -d --build hermes` — then re-run the E2E ritual from
`N8N.md` (send `--live` to `info@hexcodeplus.com`, wait ~90 s, expect a
`success` trigger execution, check `hermes crm show hexcodeplus.com`).

**Touch n8n itself**: load `N8N.md` first. The published-version gotcha
(active workflows run `workflow_history` via `activeVersionId`, NOT
`workflow_entity.nodes`) has already burned one debugging session.

## Debugging playbook (mail path)

Symptom → first check:

- "Hermes can't fetch n8n mail" → n8n workflow is broken, not Hermes.
  Hermes receives; n8n pushes. Query `execution_entity` for the latest
  `trigger`-mode rows (commands in `N8N.md`).
- 422 "missing or invalid 'from' address" in an execution → the n8n HTTP
  node isn't forwarding `={{ $json }}`, OR you're looking at the published
  version that still has the old mapping (gotcha).
- 503 from the webhook → `HERMES_EMAIL_INBOUND_SECRET` unset in `.env`.
- 401 → header value mismatch between n8n node and `.env`.
- `EAI_AGAIN` / `ENETUNREACH` / `ECONNRESET` on the IMAP trigger → host
  network blip, not config; probe with
  `docker exec hermes-n8n node -e "require('net').connect(993,'imap.hostinger.com',...)"`.
- Nothing arrives at all → `docker logs hermes-n8n | grep -i activat` —
  the workflow must show "Activated ... successful".

## Style conventions

- Match the surrounding comment density — this codebase documents *why*,
  at length, in module/function docstrings. New code without a "why"
  comment will be sent back.
- Docstrings name the invariant they enforce and cross-reference related
  files (e.g. "see tools.py's docstring").
- Minimal diffs; no opportunistic refactors. Phases live in `HERMES.md`'s
  roadmap — don't build Phase 4 autonomy while fixing Phase 2 mail.
- After behavior changes, sweep docstrings/comments for stale descriptions
  and update `HERMES.md` / `N8N.md` if architecture or runbooks changed.
