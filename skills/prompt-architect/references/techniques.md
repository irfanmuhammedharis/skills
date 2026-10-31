# Prompting Techniques Catalog

A menu, not a checklist. Pick only the techniques that improve *this* task. Stacking every technique onto a simple prompt makes it worse — longer, noisier, and harder for the model to follow. Each entry says what it is and, more importantly, **when it earns its place**.

## Table of contents
- Foundational: role, context, constraints, output format
- Reasoning: chain-of-thought, auto-CoT, decomposition, plan-first, self-consistency, tree/graph/algorithm of thoughts
- Examples: zero-shot, few-shot
- Efficiency: chain of draft, chain of density, skeleton-of-thought, chain-of-symbol
- Quality control: self-reflection, output verification, constraint prompting
- Agentic: ReAct, tool guidance, multi-agent, stepwise execution
- Retrieval: grounding in provided sources

---

## Foundational techniques (almost always worth it)

**Role / persona prompting.** Tell the model who to be ("senior firmware engineer specializing in ESP32 low-power design"). Sharpens vocabulary, priorities, and default assumptions.
- *Use when:* almost always. A precise role is the highest-leverage line in most prompts.

**Rich context.** Supply background, environment, audience, and the quality bar. Models don't share your unspoken situation.
- *Use when:* the task depends on facts the model can't infer — which is most non-trivial tasks.

**Explicit constraints.** State the tech stack, length, tone, budget, and things to avoid as concrete rules, not hints.
- *Use when:* the output must fit real-world limits or a house style. Concrete beats vague ("under 200 words, no bullet points" > "keep it short").

**Defined output format.** Specify the exact shape: JSON schema, Markdown headings, a table, a report skeleton, code only.
- *Use when:* always. Undefined format is the top cause of "technically correct but unusable" output. Non-negotiable when the output is parsed by software.

---

## Reasoning techniques

**Chain-of-thought (CoT) guidance.** Ask the model to work through the problem in structured steps *in its answer* — not to expose hidden scratchpad reasoning (many models hide that, and demanding it backfires). Producing the steps sequentially gives the model a working scratchpad, which sharply improves math, logic, and analysis. Trigger it zero-shot with "work through this step by step," or few-shot by showing example reasoning chains.
- *Use when:* multi-step logic, math, analysis, or debugging where skipping steps causes errors.
- *Avoid when:* the task is a simple lookup or generation — it just adds verbosity.

**Auto-CoT (automatic exemplar generation).** Instead of hand-writing reasoning examples, have the model generate its own: run a zero-shot "step by step" pass over a sample of representative questions, then curate the diverse, correct chains as few-shot demonstrations for the real prompt.
- *Use when:* you're building a reusable prompt/pipeline and want strong few-shot CoT without authoring examples by hand. Overkill for a one-off prompt.

**Decomposition.** Break a big task into named sub-tasks the model handles in order.
- *Use when:* the request bundles several distinct jobs. Prevents the model from dropping half of them.

**Plan-first.** Have the model produce a plan/outline, (optionally) get approval, then execute.
- *Use when:* long or expensive outputs (a full document, a codebase, a migration) where a wrong direction is costly to redo.

**Self-consistency.** Sample several independent reasoning paths (multiple runs at a non-zero temperature) and take the majority/consensus answer rather than trusting one greedy pass.
- *Use when:* accuracy matters a lot and the problem has a checkable right answer. Costs more tokens/calls — reserve for high-stakes reasoning.

### Non-linear reasoning: Tree / Graph / Algorithm of Thoughts

When a single straight reasoning line isn't enough — the problem needs exploring alternatives, backtracking, or combining partial results — escalate to a search-style paradigm. These are progressively more powerful and more expensive; reach for the lightest one that fits.

**Tree of Thoughts (ToT).** Frame reasoning as a tree search. At each step the model generates *K* candidate "next thoughts," self-scores each (e.g., promising vs. dead-end), prunes weak branches, and backtracks when a path fails — deliberate problem-solving instead of one committed guess. Usually needs orchestrator code and multiple calls.
- *Use when:* puzzles, planning, proofs, or design problems with real branching and no obvious single path. Overkill for straightforward tasks.

**Graph of Thoughts (GoT).** Generalizes ToT from a tree to a directed graph: thoughts are nodes, dependencies are edges. Beyond branching, the model can *merge* several reasoning paths, split into parallel sub-tasks, and loop to refine a specific node.
- *Use when:* the work naturally recombines — e.g. explore several partial solutions then synthesize them, or aggregate parallel findings. More orchestration overhead than ToT.

**Algorithm of Thoughts (AoT).** Push the whole search *into a single inference pass*: give the model few-shot exemplars that demonstrate an algorithmic trace (branch, evaluate, backtrack, e.g. a DFS log) so it explores and prunes internally before boxing a final answer — capturing much of ToT's benefit without dozens of API round-trips.
- *Use when:* you want ToT-style exploration but need to control latency and cost. The trade-off is less external control over the search.

---

## Example-based techniques

**Zero-shot.** Just describe the task well, no examples.
- *Use when:* the task is common and well-specified, or examples would be hard to produce. Modern models are strong zero-shot.

**Few-shot.** Include 2–5 input→output examples that demonstrate the exact pattern, tone, or edge-case handling you want.
- *Use when:* the desired format or style is specific and easier to *show* than describe (classification labels, a particular writing voice, a niche output schema). The single most reliable way to lock in format. Make examples cover the tricky cases, not just the easy ones.

---

## Efficiency / density-optimized techniques

These cut token cost, latency, or verbosity while holding quality. Reach for them when output length, speed, or spend actually matter — not by default.

**Chain of Draft (CoD).** A minimalist cousin of CoT: instruct the model to reason in terse shorthand — roughly five words per step — then give the answer after a separator. Preserves the accuracy benefit of showing work while cutting reasoning tokens dramatically (often well over half), which also lowers latency.
- *Use when:* you want CoT-level correctness on math/logic but the full verbose reasoning is wasted tokens (high-volume or latency-sensitive calls).
- *Directive:* "Think step by step, but keep each step to five words or fewer. Give the final answer after `####`."

**Chain of Density (CoD, summarization).** Produce a summary that gets *denser*, not longer. Start sparse, then iterate ~5 times: each pass adds 1–3 important entities missing from the prior summary and rewrites at the *same length* via fusion and compression, never dropping earlier entities.
- *Use when:* you need maximally informative fixed-length summaries (abstracts, briefings) rather than a first-pass skim.

**Skeleton-of-Thought (SoT).** Split generation into two stages to parallelize: first produce a short skeleton (3–10 bullet points / section headers), then expand each point *concurrently* (parallel calls or batched decoding) and concatenate.
- *Use when:* the output is long and naturally decomposable, and generation latency is the bottleneck. Needs an orchestrator that can fan out the expansion calls.

**Chain-of-Symbol (CoS).** Replace verbose spatial/relational language ("the red block is on top of the blue block, to the left of…") with compact symbolic notation (`A→B`, `A⊂C`). Reduces ambiguity and token count for structured reasoning.
- *Use when:* spatial reasoning, navigation, block-world planning, or any task with lots of positional/relational description.

---

## Quality-control techniques

**Self-reflection / critique.** After drafting, have the model review its own output against the requirements and revise.
- *Use when:* correctness and completeness matter and one pass tends to miss things.

**Output verification.** End with an explicit checklist the model must confirm ("Verify: all N requirements addressed; no contradictions; assumptions listed; limitations noted").
- *Use when:* enterprise/production prompts, or anything with many discrete requirements that are easy to partially satisfy.

**Constraint prompting.** State negative constraints as firmly as positive ones ("Do NOT invent citations. Do NOT exceed 3 dependencies.").
- *Use when:* there are known failure modes to fence off. What to *avoid* is often as important as what to do.

---

## Agentic techniques

**ReAct (reason + act).** Interleave thinking with tool actions: reason about what's needed, call a tool, observe the result, reason again.
- *Use when:* the target is a tool-using agent that must gather information or affect the world before answering. See `agent-prompting.md`.

**Explicit tool guidance.** Tell the agent which tools exist, what each is for, and when to prefer one over another.
- *Use when:* the agent has more than one tool, or a tool is easy to misuse. Vague tool access leads to skipped or wasted calls.

**Stepwise / staged execution.** Force the agent to complete and confirm one stage before moving to the next.
- *Use when:* long autonomous workflows where a mistake early poisons everything downstream.

**Multi-agent / role split.** Assign distinct roles that hand off to each other (planner → implementer → reviewer), or ask one model to play these roles in sequence.
- *Use when:* complex tasks that genuinely benefit from separation of concerns. Adds coordination overhead — don't use it for simple work.

---

## Retrieval / grounding

**Retrieval guidance.** Instruct the model to answer *only* from provided sources, cite which source supports each claim, and say "not found" rather than guess.
- *Use when:* accuracy against a knowledge base matters and hallucination is unacceptable (docs Q&A, RAG systems, compliance). Pair with a "if the answer isn't in the sources, say so" rule.
