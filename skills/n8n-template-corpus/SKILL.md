---
name: n8n-template-corpus
description: Build production-grade n8n workflow JSON by mining a local corpus of 319 real, working workflows for exact node schemas, typeVersions, and wiring. Use when writing, editing, reviewing, or debugging any n8n workflow JSON, adapting a downloaded n8n template, or when a workflow fails to import or a node's parameters are uncertain. Complements n8n-workflow-patterns (architecture) with verified concrete schemas, plus the production hardening the templates themselves lack. Prefers self-hosted and free-tier services.
---

# n8n Template Corpus

Ground every workflow you write in a real one that already runs. n8n silently ignores
parameters it does not recognize and rejects imports on bad `typeVersion`, so guessing
node schemas from memory is the single most common way a generated workflow fails.

**Corpus location:** `/home/irfan/Documents/software/n8n ads/adnexus/template`
(319 parseable workflows across 19 categories). Check it exists; if it has moved, set
`N8N_CORPUS` to the new path — every command below honors that override.

## Rule 1 — Copy schemas, never invent them

Before writing any node, pull a real one:

```bash
scripts/corpus.sh node n8n-nodes-base.httpRequest    # which templates use it
scripts/corpus.sh schema <file.json> <node-type>     # exact parameter object
scripts/corpus.sh grep "qdrant"                      # find by keyword
scripts/corpus.sh nodes <file.json>                  # node inventory of one workflow
scripts/corpus.sh check <file.json>                  # validate before import
```

Copy the node's `type`, `typeVersion`, and parameter *keys*; rewrite only the values.
Always strip `credentials` blocks, `webhookId`s, and `pinData` from anything you adapt —
they reference the original author's instance.

## Rule 2 — Use the typeVersions the corpus actually uses

An invented `typeVersion` fails the import outright. Verified majority versions:

| Node | typeVersion | Node | typeVersion |
|---|---|---|---|
| `set` | **3.4** | `httpRequest` | **4.2** |
| `code` | **2** | `if` | **2.2** |
| `switch` | **3.2** | `filter` | **2.2** |
| `merge` | **3** | `splitInBatches` | **3** |
| `splitOut` / `aggregate` | **1** | `webhook` | **2** |
| `respondToWebhook` | **1.1** | `scheduleTrigger` | **1.2** |
| `wait` | **1.1** | `formTrigger` | **2.2** |
| `googleSheets` | **4.5** | `gmail` | **2.1** |
| `googleDrive` | **3** | `airtable` | **2.1** |
| `telegram` | **1.2** | `telegramTrigger` | **1.1** |
| `slack` | **2.1–2.3** | `html` | **1.2** |
| `executeWorkflowTrigger` | **1** | `extractFromFile` | **1** |
| `stickyNote` / `noOp` / `manualTrigger` | **1** | `markdown` | **1** |

LangChain nodes (`@n8n/n8n-nodes-langchain.*`): `agent` **1.7**, `chainLlm` **1.4**,
`lmChatOpenAi` **1**, `chatTrigger` **1.1**, `outputParserStructured` **1.2**,
`memoryBufferWindow` **1.3**, `toolWorkflow` **1.2**, `vectorStoreQdrant` **1**,
`documentDefaultDataLoader` **1**, `informationExtractor` **1**.

When unsure, re-derive rather than trust this table:
`scripts/corpus.sh versions <node-type>`.

## Rule 3 — Get the connection graph right

`connections` is keyed by **source node name**, and node names must be unique — duplicate
names silently break wiring. Standard data flow uses the `main` kind:

```json
"connections": {
  "Webhook": { "main": [[{ "node": "Validate", "type": "main", "index": 0 }]] }
}
```

Multi-output nodes use the outer array as the branch index: `if` is
`[[true-branch],[false-branch]]`; `switch` has one inner array per rule;
`splitInBatches` is `[[done],[loop]]` — output 0 is the *done* branch, not the loop.

**AI sub-nodes connect backwards.** The model/tool/memory node is the connection
*source*, and the agent is the target — not the other way round. This trips up most
hand-written LangChain workflows:

```json
"OpenAI Chat Model":      { "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]] },
"Structured Output Parser":{ "ai_outputParser":  [[{ "node": "AI Agent", "type": "ai_outputParser",  "index": 0 }]] }
```

Kinds in use: `ai_languageModel`, `ai_tool`, `ai_memory`, `ai_embedding`,
`ai_outputParser`, `ai_textSplitter`, `ai_document`, `ai_vectorStore`, `ai_retriever`.

Set `settings.executionOrder: "v1"` on every workflow (the corpus majority) — v0 ordering
is legacy and makes multi-branch execution order unpredictable.

## Rule 4 — The corpus does NOT teach production hygiene

Measured across the corpus: of ~5,000 nodes only **65** set `retryOnFail`, **90** set
`onError`, and **not one** workflow sets an error workflow. These are demos. Take the
schemas; add the hardening yourself:

- **Retries** — `retryOnFail: true`, `maxTries: 3`, `waitBetweenTries: 2000` on every
  HTTP, DB, and third-party node.
- **Error routing** — `onError: "continueErrorOutput"` on nodes whose failure you can
  handle, wired to a real recovery path. `continueOnFail` is deprecated; don't copy it
  from older templates.
- **Error workflow** — set `settings.errorWorkflow` to a workflow that persists the
  failed payload and alerts. Without it, a failed execution is invisible.
- **Idempotency** — webhooks and provider callbacks fire twice. Derive a deterministic
  key and dedupe (Redis `SET key NX EX 86400`, or a unique DB constraint) before any
  side effect.
- **Validate at the boundary** — first node after a trigger checks the payload shape and
  rejects bad input explicitly; never let it reach a Code node that assumes fields.
- **Authenticate webhooks** — n8n webhooks are unauthenticated by default. Require an
  HMAC signature or a shared secret header and verify it in constant time.
- **Batch and throttle** — `splitInBatches` (`batchSize` 50–100) for lists over ~100,
  plus a `wait` node between batches for rate-limited APIs. Per-item HTTP calls are the
  usual reason a workflow passes in test and times out in production.
- **Strip `pinData` before shipping.** 285 of 319 templates carry it; it silently
  overrides live input and will make a production workflow replay stale test data.

## Rule 5 — No secrets, no paid services

Workflow JSON gets committed and shared — treat it as public. Use n8n credentials or
`{{ $env.VAR }}`; never a literal key. Verify before handing off:

```bash
grep -nEi '(api[_-]?key|secret|password|token|bearer [A-Za-z0-9])"[[:space:]]*:[[:space:]]*"[^{]' workflow.json
```

Prefer free/self-hosted; when a template pulls in a paid service, substitute:

| Template uses | Free substitute |
|---|---|
| Pinecone / Weaviate | Qdrant (`vectorStoreQdrant`, already used in 26 templates) |
| Airtable / Sheets as datastore | Postgres |
| S3 | MinIO (S3-compatible, same HTTP node) |
| SendGrid / Mailgun | `emailSend` over your own SMTP |
| Paid LLM tiers | Ollama locally, or a free-tier key via `httpRequest` |
| Paid schedulers / queues | `scheduleTrigger` + Redis |

If nothing free exists, say what the paid dependency is and what it costs — don't add it
silently.

## Before handing off

1. `scripts/corpus.sh check <file.json>` — structure, duplicate names, dangling
   connections, unreachable nodes.
2. Import into n8n and execute once with a realistic payload.
3. Report what you actually ran versus what you only wrote. An unimported workflow is
   untested; describe it that way.
