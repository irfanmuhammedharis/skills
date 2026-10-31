# Programmatic Prompt Optimization

Hand-tuning prompt strings tops out fast. When a prompt must hit a *measurable* accuracy bar, run at scale, or stay reproducible across model changes, move from "string-tinkering" to **eval-driven, declarative optimization**. Consult this file when the user is building a production pipeline rather than a one-off prompt.

## The shift

```
Manual prompting:  tweak string → test → fail → re-tweak → hardcode in app
Programmatic:      define signature → build pipeline → compile against data + metric → auto-optimized prompt
```

The manual loop relies on a human's intuition and a handful of eyeballed examples. The programmatic loop replaces intuition with a dataset and a metric, and lets an optimizer search the prompt/example space for you.

## DSPy (Declarative Self-improving Python)

DSPy is the leading framework for this. It treats prompting as software: you declare *what* each step should do, and the framework figures out the wording.

- **Signatures** — a typed input→output spec for a step, written as a clean interface instead of a prose prompt. Example: a signature declaring `contract_text: str` in and `effective_date: str` (as `YYYY-MM-DD`) plus `liability_cap_usd: float` out. You describe the contract of the step; you don't write the prompt string.
- **Modules** — reusable strategies applied over a signature: `dspy.Predict` (direct), `dspy.ChainOfThought` (adds reasoning), `dspy.ReAct` (adds tool use), and so on. Swapping modules swaps the prompting strategy without rewriting anything.
- **Adapters** — translate a signature into the optimal model-specific format behind the scenes (e.g. render it as a JSON template for one model, XML for another), so the same program targets different models cleanly.

### Signature sketch

```python
import dspy

class ContractExtraction(dspy.Signature):
    """Extract key variables and risk values from a contract."""
    contract_text: str    = dspy.InputField()
    effective_date: str   = dspy.OutputField(desc="Date in YYYY-MM-DD format")
    liability_cap_usd: float = dspy.OutputField(desc="Maximum liability cap in USD")
```

## Optimizers / compilers

The payoff is the optimizer. Given a program, a small labeled dataset, and a validation metric, optimizers such as **MIPROv2** or **BootstrapFewShot** automatically improve the prompt:

- **Instruction generation** — a capable "teacher" model proposes and refines candidate instruction strings.
- **Demo bootstrapping** — the compiler runs the training data through the pipeline, keeps the steps that produced correct results, and synthesizes those into high-quality few-shot examples embedded in the prompt.
- **Evaluation loop** — it scores prompt-and-example combinations against the metric and compiles the best-performing configuration to a clean config (often JSON) you can version and ship.

## When to recommend this path

- The prompt is a component in a **product or pipeline**, not a chat one-off.
- There's an **objective metric** (accuracy, F1, exact-match, a rubric score) and at least a small labeled dataset.
- The prompt must survive **model swaps** without a full manual rewrite.
- Reliability and **reproducibility** matter more than a quick hand-tuned win.

When these hold, advise the user to define signatures + a metric + a small eval set and let an optimizer compile the prompt — and to keep the eval set in CI so quality is measured on every change, not assumed. For one-off or exploratory prompts, this is overkill; a well-structured manual prompt from the main workflow is the right tool.
