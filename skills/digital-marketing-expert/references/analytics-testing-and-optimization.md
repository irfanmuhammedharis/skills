# Analytics, Testing & Optimization

Read this file for: KPI definitions and formulas, attribution modeling, rigorous A/B testing methodology, conversion rate optimization (CRO), and reporting/dashboard design. For creative-specific testing and frequency management, see `ad-planning-and-paid-media.md`.

## 1. KPI Hierarchy & Core Formulas

See SKILL.md Section 3.2 for the three-tier hierarchy (Lagging / Leading / Diagnostic). Core formulas worth having exact:
- **ROAS** = Revenue from ads ÷ Ad spend
- **CAC** (Customer Acquisition Cost) = Total acquisition spend ÷ Number of new customers acquired
- **LTV** (Lifetime Value) = Average order value × Purchase frequency × Average customer lifespan (or a cohort-based actual-revenue calculation where the data supports it — more reliable than the formulaic estimate once there's enough history)
- **LTV:CAC ratio**: a commonly cited healthy target is roughly 3:1 or higher — treat this as an industry rule of thumb to sanity-check against, not a universal target; capital-intensive or long-payback businesses can be healthy at a lower ratio if payback period and cash flow support it.
- **CPA** (Cost Per Acquisition/Action) = Spend ÷ Number of conversions (define "conversion" precisely — a lead and a closed sale are very different denominators)

## 2. Attribution Modeling

See `ad-planning-and-paid-media.md` Section 8 for the full comparison of last-click, multi-touch, media mix modeling, and incrementality testing. The short version for reporting purposes: know which model any dashboard number is using before comparing it across channels or time periods — comparing a last-click number from one period to an MMM-adjusted number from another produces a false trend.

## 3. A/B Testing — Full Protocol

1. **Hypothesis**: "Changing X will improve Y because Z" — written down before launch. A hypothesis with no stated mechanism ("let's just try a different color") is much harder to learn from even if it wins, because there's no reusable insight.
2. **Variable isolation**: test exactly one element (headline, image, CTA, layout, audience). Testing a full page redesign against the original tells you the redesign won or lost, not why — which limits how much the result generalizes to the next decision.
3. **Sample size / statistical power**: driven by baseline conversion rate and the minimum effect size worth detecting, not a fixed conversion count. A low-traffic page chasing a small lift needs a much longer runtime than "wait for 100 conversions" suggests — use a sample-size calculator against the actual baseline rate rather than a rule of thumb when the decision is high-stakes.
4. **No early stopping**: pre-commit to a duration or sample size before launch and hold to it — checking daily and calling a winner the first time it looks good inflates the false-positive rate significantly (this is one of the most common and least visible testing mistakes).
5. **Significance threshold**: 95% confidence is the common bar for a permanent, high-stakes decision; a lower, faster bar can be reasonable for a cheap, easily-reversible creative swap. Match the rigor to the cost of being wrong.
6. **Document in a test library**: hypothesis, result, and the takeaway — institutional memory of what's already been tried is where a testing program's compounding value actually comes from.

## 4. CRO (Conversion Rate Optimization) Framework

- **Diagnose before prescribing**: use session recordings, heatmaps, and funnel drop-off data to find where people actually get stuck before proposing a fix — redesigning a page based on a hunch skips the diagnostic step that makes CRO reliable rather than lucky.
- **Prioritize by a structured score, not gut feeling**: a simple, defensible model is Potential (how much room for improvement) × Importance (how much traffic/value passes through this page) × Ease (how quickly it can be tested) — this keeps the test backlog focused on high-leverage pages instead of whichever page someone happens to be looking at.
- **Common friction sources**: unclear value proposition, too many form fields, slow load time, unclear or buried CTA, lack of trust signals (reviews, guarantees, security badges) at the decision point, mismatched messaging between the ad/referral source and the landing page.

## 5. Reporting & Dashboard Design

- **Match the report to the audience**: an executive dashboard shows lagging-indicator business outcomes and trend direction; a practitioner dashboard shows leading and diagnostic metrics that are actually actionable day-to-day. The same raw data, organized differently for who's reading it.
- **Show trend, not just a snapshot**: a single-period number without a comparison (prior period, same period last year, or a goal line) is hard to interpret — is 3.2% CTR good? Depends entirely on what it's being compared to.
- **Flag data caveats directly in the report**: attribution model in use, any tracking gaps, any known data quality issues — a clean-looking number built on shaky data is worse than a rougher number with an honest caveat, because the clean one gets trusted more than it should.
