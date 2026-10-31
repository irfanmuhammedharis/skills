# digital-marketing-expert — Reference Bundle

This file bundles several reference documents into one, separated by clear headers, so they fit ChatGPT's knowledge file-count limit per Custom GPT / Project.

---



## FILE: references/ad-planning-and-paid-media.md

# Ad Planning & Paid Media

Read this file for: media planning, campaign architecture, budget allocation, bid strategy, audience research, AI-driven campaign automation, creative testing, frequency management, and attribution/measurement. For platform-specific specs and formats, also read the relevant `platforms/*.md` file. For copy inside the ads, see `copywriting-and-messaging.md`.

## 1. Campaign Architecture

### 1.1 Structure & Naming
Standard hierarchy: **Campaign** (objective + budget) → **Ad Set/Group** (audience + placement + schedule) → **Ad** (creative + copy). Keep naming conventions consistent and machine-sortable from day one — e.g. `[Objective]_[Audience]_[Date]_[Creative Version]` — because a media plan that can't be filtered and pivoted in a spreadsheet six months in is a media plan nobody is actually learning from.

### 1.2 Structuring for Signal, Not Just Organization
Modern ad platforms (see 3) learn from conversion signal inside each ad set — splitting budget across too many small ad sets starves each one of the volume it needs to exit the learning phase. As a rule of thumb, consolidate rather than fragment: fewer, better-funded ad sets outperform many thin ones on platforms with algorithmic delivery.

## 2. Audience Research & Targeting

- **First-party data**: Owned customer/lead lists — the highest-signal, most privacy-resilient targeting input available (see `email-crm-lifecycle.md` and the Privacy-First section of `emerging-trends-and-ai-marketing.md`).
- **Lookalike/similar audiences**: Modeled from a first-party seed list. Quality depends entirely on the seed — a seed list of "everyone who ever visited the site" produces a worse lookalike than a seed of "customers with LTV in the top quartile."
- **Interest/behavioral targeting**: Platform-inferred categories. Useful for cold prospecting but increasingly less precise as platforms lean on broad/AI-driven delivery (see Section 3) — treat as a loose steer, not a scalpel.
- **Contextual targeting**: Targeting based on the content/page a user is currently viewing rather than who they are. Regaining relevance as identity-based tracking erodes (see privacy trends).
- **Retargeting**: Segment by funnel depth (site visitors vs. cart abandoners vs. past purchasers) — a single undifferentiated retargeting pool wastes budget showing a cold message to a hot audience and vice versa.

## 3. AI-Driven Campaign Automation

Paid social and search now default to broad, AI-driven optimization over granular manual targeting — this is one of the largest structural shifts in performance marketing in the last few years, and any "elite" plan has to account for it rather than defaulting to 2019-style manual audience-stacking.

- **Meta Advantage+**: Broad or no manual targeting; the system finds buyers from the pixel/conversion signal and creative performance. Manual audience building is now mainly a testing/learning tool, not the default production approach.
- **Google Performance Max**: Single-campaign automation spanning Search, Display, YouTube, and Shopping inventory from one asset group. Feed quality (for Shopping) and creative-asset variety matter more than manual bid/placement control, since the system assembles combinations itself.
- **What this changes practically**: the marketer's highest-leverage job shifts from granular targeting to (a) feeding the system clean, high-quality conversion signal, and (b) supplying enough creative variety for the system to find a winning combination. Starve either input and the automation underperforms regardless of budget.
- **Minimum data before trusting automation**: these systems need a real volume of conversion events to learn — running Advantage+ or PMax on a brand-new pixel with near-zero conversion history usually underperforms a manual campaign until enough signal accumulates. Don't force automation before there's data for it to learn from.

## 4. Bid Strategy Selection

| Strategy | Use When | Trade-off |
|---|---|---|
| Maximize Conversions / Volume | Early learning phase, building signal | Spends the full budget; less cost control |
| Cost Cap / Cost Per Result Goal | Stable performance, protecting unit economics | Can limit delivery/volume if the cap is too aggressive |
| Target ROAS | E-commerce with reliable revenue tracking | Needs enough conversion volume and revenue variance to model well; unstable on low volume |
| Bid Cap | Full manual control, direct-response specialists | High effort, easy to under-deliver if set wrong; rare as a default in 2026 |

Start broader/automated to gather signal, then tighten toward cost or ROAS targets once there's enough conversion volume to model against — moving to a tight ROAS target before the account has data is a common way to strangle delivery.

## 5. Budget Allocation

The often-cited 70/20/10 split (70% proven performers, 20% testing variations on what's working, 10% experimental/new channels) is a reasonable default *starting point* for an account with some maturity — the rationale is protecting what's already working while still funding the discovery of what's next. Adjust the ratio for stage: a pre-product-market-fit budget should skew far more toward testing (closer to 50/50) since there isn't yet a "proven 70%" to protect.

## 6. Creative Testing Methodology

1. **Hypothesis first**: "Changing X will improve Y because Z" — write it down before launching, not after seeing results (post-hoc storytelling isn't a test).
2. **One variable per test**: headline, image, CTA, or audience — isolate one, or the result can't be attributed to anything specific.
3. **Sample size is about statistical power, not a fixed number**: "100 conversions" is a rough floor cited industry-wide, but the real requirement depends on baseline conversion rate and the minimum effect size worth detecting — a low-traffic account chasing a small lift needs much longer than that floor suggests. When in doubt, run longer rather than call a winner early.
4. **Don't peek and stop early**: checking results daily and killing a test the first time it dips is how noise gets mistaken for signal. Pre-commit to a duration or sample size before launch.
5. **95% confidence** is the common bar before declaring a winner — useful for high-stakes/permanent decisions; a lower bar can be acceptable for reversible, low-cost creative swaps.
6. **Document everything in a test library** — the compounding value of a testing program comes from institutional memory of what's already been tried, not any single test result.

## 7. Creative Fatigue Management

- Refresh creative every 7–14 days for high-frequency campaigns; slower-frequency campaigns can run creative longer before fatigue sets in.
- Rotate 3–5 ad variants simultaneously so the algorithm has room to find the best performer without over-relying on one asset.
- Watch frequency (impressions per user) as a leading indicator of fatigue — rising frequency alongside falling CTR on the *same* creative is the classic fatigue signature.
- Use dynamic/AI-assembled creative (multiple image/video/text components auto-combined per platform) where available — it naturally extends creative lifespan by serving more permutations from the same asset pool.

## 8. Attribution & Measurement

- **Last-click**: Simplest, most overstates the bottom-of-funnel channel, understates awareness channels. Still common because it's easy, rarely the most honest picture.
- **Multi-touch/data-driven attribution**: Distributes credit across the path based on modeled influence. More honest than last-click, still limited by what's trackable — which keeps shrinking (see privacy trends).
- **Media mix modeling (MMM)**: Statistical, top-down modeling of spend vs. outcomes across channels and time, independent of individual user-level tracking. Growing in importance specifically *because* user-level tracking keeps eroding — it doesn't need a pixel to work.
- **Incrementality/holdout testing**: The gold standard for "did this spend actually cause this outcome" — geo or audience holdouts that isolate a true causal lift rather than inferring it from correlated signal. More operationally heavy, but it's the only method that directly answers the causality question the others only approximate.
- **Practical stance**: no single method is complete on its own in a privacy-constrained, multi-platform world. A mature measurement stack triangulates platform-reported numbers, MMM, and periodic incrementality tests rather than trusting any one source as ground truth.


---


## FILE: references/analytics-testing-and-optimization.md

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


---


## FILE: references/content-planning-and-calendars.md

# Content Planning & Calendars

Read this file for: editorial calendar structure, content pillar strategy, content-to-funnel mapping, repurposing/atomization, content briefs, and approval workflows. For SEO content strategy specifically (topic clusters, keyword-to-content mapping), see `seo-and-sem.md`. For platform posting cadence/format specifics, see the relevant `platforms/*.md`.

## 1. Deriving Content Pillars

Pillars should come from the intersection of two things, not from a brainstorm in isolation:
1. **What the ICP actually searches, asks, and struggles with** (from `strategy-and-positioning.md`'s persona work, sales call notes, support tickets, community questions)
2. **What the brand is credibly positioned to own** (from the differentiationework in `strategy-and-positioning.md`)

3–5 pillars is a workable range for most brands — fewer and the content feels thin/repetitive fast; more and the content strategy loses focus and dilutes authority on any one topic. Each pillar should be specific enough to generate a year of distinct content ideas, not so broad it's really the whole category ("productivity tips" is too broad; "async communication for distributed teams" is a pillar).

## 2. Content-to-Funnel Mapping

| Funnel Stage | Content Types |
|---|---|
| TOFU (Awareness) | Educational how-tos, trend commentary, original data/research, brand storytelling, entertaining/shareable content |
| MOFU (Consideration) | Case studies, comparison/alternatives pages, webinars, buyer's guides, lead magnets (templates, checklists, calculators) |
| BOFU (Conversion) | Product demos, free trial/consultation offers, customer testimonials, pricing/ROI pages, limited-time offers |
| Retention | Onboarding content, community programming, advanced/power-user guides, loyalty and referral content, re-engagement campaigns |

A healthy content calendar has representation across all four — a calendar that's 90% TOFU generates awareness that never converts; one that's mostly BOFU runs out of warm audience because nothing upstream is building it.

## 3. Editorial Calendar Structure

- **Cadence should match capacity, not ambition.** A realistic, sustained 2 posts/week beats an ambitious 5 posts/week that collapses after a month. Set cadence based on actual production capacity (writing, design, review, approval) — not the cadence a competitor appears to run.
- **Plan in themed blocks** (monthly or campaign-length), not post-by-post improvisation — this is what makes pillar coverage and funnel-stage balance actually trackable instead of accidental.
- **Build in buffer for reactive content** (trend participation, timely commentary) — a calendar planned to 100% capacity with no slack can't take advantage of a moment when one shows up.
- **Track pillar and funnel-stage tags per piece** so a monthly audit can actually show whether coverage is balanced, rather than relying on a gut feeling.

## 4. Content Repurposing / Atomization

One well-made pillar asset (a long-form guide, an original research report, a webinar) should generate a deliberate set of derivatives, not an afterthought social post:
- Long-form article → 3–5 social posts (native to each platform's format, not identical copy-paste), 1 email, 1 short-form video script, a handful of pull-quote graphics
- Webinar → full recording + 5–10 clipped highlight videos + a written recap post + a slide-deck carousel
- Original data/research → a hero report + a press/PR angle + a series of individual-stat social posts (one stat, one visual, one post) that can run for weeks after the original publish

The efficiency case for repurposing is real, but native reformatting matters — auto-cross-posted, unedited content reads as lazy on every platform it wasn't built for (see platform files for specifics).

## 5. Content Brief Template

A brief that's missing any of these fields is a brief that will come back for revision:
- **Objective & funnel stage**: what this piece is supposed to do and where it sits
- **Target keyword/topic** (if SEO-relevant — see `seo-and-sem.md`)
- **Audience & the specific question/pain point this answers**
- **Key points to cover** (not a full outline — leave room for the writer's structure)
- **Proof points/data to include**, with sources
- **CTA**: what happens after someone reads/watches this
- **Format & length constraints**, platform if applicable
- **Brand voice notes** relevant to this specific piece (see `copywriting-and-messaging.md` for the full framework)

## 6. Content Governance

- **Approval workflow**: define who reviews for brand voice, who reviews for legal/compliance claims, and in what order — a piece that goes to legal after design is finished wastes design time when legal flags a claim.
- **Style guide enforcement**: a living document (not a one-time PDF) covering approved terminology, forbidden claims/jargon, formatting conventions, and accessibility basics (alt text, caption requirements).
- **Versioning**: especially for evergreen content (pillar pages, guides) — schedule periodic re-review, since content that was accurate at publish can go stale (broken claims, outdated screenshots, superseded stats) without anyone noticing until a customer does.


---


## FILE: references/copywriting-and-messaging.md

# Copywriting & Messaging

Read this file for: copywriting formulas, headline writing, brand voice/tone frameworks, ad copy by objective and platform, and CTA language. For the underlying positioning these formulas should express, see `strategy-and-positioning.md`.

## 1. Copywriting Formulas

Only formulas with genuine, widespread pedigree are listed here — a copy formula with no real teaching lineage behind it is a liability, not an asset, in front of a client.

- **AIDA** — Attention → Interest → Desire → Action. The original, still the most broadly applicable structure for a single piece of persuasive copy.
- **PAS** — Problem → Agitate → Solution. Best when the audience already half-recognizes the problem; agitation makes the cost of inaction concrete before the solution arrives.
- **FAB** — Features → Advantages → Benefits. Forces the copy to translate a spec sheet into "what this actually means for you" — the most common failure in technical/B2B copy is stopping at Features.
- **BAB** — Before → After → Bridge. Paints the current-state pain, the desired future state, then positions the product as the bridge between them. Strong for transformation-oriented offers (fitness, education, productivity tools).
- **4 Ps / PPP** — Promise → Picture → Proof → Push. Open with the core promise, help the reader picture achieving it, back it with proof, then push for action.

## 2. The 4 Cs — A Copy Quality Checklist (not a structural formula)
Run any draft against: **Clear** (would a stranger understand this in one read?), **Concise** (is every word earning its place?), **Compelling** (is there an actual reason to care, not just a description?), **Credible** (is every claim backed by something, or does it read like marketing puffery?).

## 3. Headline Template Bank

Organized by the psychological trigger each relies on — pick based on what the audience actually needs (curiosity for cold/TOFU audiences, specificity and proof for warmer/BOFU audiences):

**Curiosity**
- "The [surprising thing] nobody tells you about [topic]"
- "Why [common belief] is wrong (and what to do instead)"

**Specificity / Proof**
- "[Number] Minutes to [Result] — Here's Exactly How"
- "How [specific customer/company] achieved [specific result] in [timeframe]"

**Benefit-Forward**
- "How to [Achieve Result] Without [Common Pain Point]"
- "[Achieve outcome] — without [the thing people assume is required]"

**List / Structure**
- "The [Number] [Adjective] Ways to [Desired Outcome]"
- "[Number] [Category] mistakes that are costing you [specific cost]"

**Contrarian**
- "Why [counterintuitive statement] (and what to do instead)"
- "[Common practice] is dead. Here's what's replacing it."

**Narrative / Personal Proof**
- "I [action] for [timeframe]. Here's what happened."
- "What [number] [customers/users] taught us about [topic]"

**Question**
- "Still doing [outdated approach]?"
- "What if [reframe of the problem]?"

## 4. Ad Copy by Objective & Format

- **Cold/prospecting (short-form social)**: Lead with the hook, not the brand name — nobody scrolling has decided to care about the brand yet. One idea per ad; a cold ad trying to communicate three benefits communicates none.
- **Retargeting (short-form social)**: Can assume prior awareness — lean into specificity, proof, and urgency rather than re-explaining what the product is.
- **Search ads**: Match the copy tightly to searcher intent at that specific keyword — a search ad is answering a question the person just asked, not introducing a brand cold. Headlines should mirror the language of the query itself where possible.
- **Long-form (landing page, email body)**: Can build a full argument — problem, agitation, proof, objection-handling, offer — because the reader has already opted into more attention than a feed scroll allows.
- **B2B vs. B2C tone**: B2B copy still needs emotional stakes (career risk, team frustration, being the one who championed the wrong tool) — "B2B just means boring and rational" is a common and costly misread. The buyer is still a person with something personally on the line.

## 5. Brand Voice & Tone Framework

Define these explicitly for any brand before writing at scale — an unwritten voice drifts piece to piece and writer to writer:
- **Voice (personality, stable)**: Is the brand a mentor, a rebel, a friend, or an authority? This shouldn't change based on the channel or the day.
- **Tone (mood, situational)**: The same voice flexes — celebratory for a launch, empathetic for a support issue, urgent for a deadline, educational for a how-to. Tone shifts; voice doesn't.
- **Vocabulary**: A living list of approved words/phrases, forbidden jargon, and any signature phrases that are actually part of the brand's recognizable voice.
- **Sentence structure**: Short and punchy vs. long-form narrative — pick a default and name the exceptions (e.g. "punchy everywhere except long-form educational content, where a more narrative register is fine").
- **Emoji policy**: Which emojis (if any) fit the brand, frequency limits, and where they're appropriate vs. not (an emoji in a playful social caption and the same emoji in a B2B outreach email land very differently).

## 6. CTA Language Bank

Match the CTA's commitment level to the funnel stage — asking for a purchase-level commitment at a TOFU touchpoint is a common conversion killer:
- **Low-commitment (TOFU)**: "Learn more," "See how it works," "Read the guide"
- **Medium-commitment (MOFU)**: "Get the template," "Book a demo," "Start your free trial"
- **High-commitment (BOFU)**: "Buy now," "Get started today," "Claim your [specific offer]"
- **Urgency variants** (use only when the urgency is real — a fake countdown timer is a fast way to burn trust): "Only [N] left," "Offer ends [specific date]," "Limited spots for [cohort/date]"


---


## FILE: references/email-crm-lifecycle.md

# Email, CRM & Lifecycle Marketing

Read this file for: lifecycle stage mapping, segmentation strategy, automation flow design, email design/copy conventions, and deliverability. For subject line psychology and general copy formulas, also see `copywriting-and-messaging.md`.

## 1. Lifecycle Stages

Map the email/CRM program to the same funnel used everywhere else in this skill (see SKILL.md Section 3.1), with lifecycle-specific detail:
- **Lead/Subscriber** (pre-purchase, TOFU/MOFU): nurture toward first purchase or conversion event
- **New Customer** (first 0–90 days): onboarding, activation, first-value delivery
- **Active Customer** (Retention): engagement, cross-sell/upsell, loyalty
- **At-Risk/Lapsing**: declining engagement or usage signals, needs a distinct win-back motion before full churn
- **Churned/Lapsed**: sunset or long-cycle win-back, different cadence and offer than an active win-back attempt

## 2. Segmentation Strategies

- **Behavioral**: based on actions taken (or not taken) — page visits, feature usage, purchase category. Usually the highest-signal segmentation available.
- **RFM (Recency, Frequency, Monetary)**: classic e-commerce/retail segmentation scoring customers on how recently, how often, and how much they buy — cheap to compute, still genuinely effective for prioritizing who gets which offer.
- **Demographic/firmographic**: useful as a targeting layer but weaker as a primary segmentation than behavior — two people with identical demographics can have completely different intent.
- **Engagement-based**: active vs. dormant subscribers, segmented specifically so a re-engagement flow doesn't get sent to already-engaged users (annoying) and an active-nurture flow doesn't get sent to the dormant (wasted, and it hurts sender reputation — see Section 5).

## 3. Automation Flow Blueprints

- **Welcome series** (3–5 emails): set expectations, deliver early value, introduce the brand story, first soft offer by the final email. Highest-engagement flow in most programs — worth disproportionate creative investment.
- **Abandoned cart** (typically 2–3 emails): reminder → light incentive/urgency → final nudge. Timing matters more than content — the first email close to abandonment, escalating urgency if no action.
- **Browse abandonment**: lighter-touch than cart abandonment (lower intent signal) — usually 1–2 emails, softer CTA.
- **Post-purchase**: order confirmation → delivery/usage tips → review request → related-product suggestion, spaced to match the actual product's usage timeline (a review request the day after delivery for a product that takes weeks to "prove itself" is premature).
- **Win-back / re-engagement / sunset**: escalating specificity — start with genuine value or a "we miss you," end with an explicit "should we stop emailing you" sunset message. A sunset flow protects sender reputation (see Section 5) by proactively pruning dead addresses instead of letting them silently rot the list.
- **Replenishment** (consumable products): timed to the product's actual usage cycle, not a generic interval.
- **VIP/loyalty**: recognition and exclusive access for top-tier customers, distinct cadence and tone from general lifecycle email.

## 4. Subject Line & Preview Text

- **Subject lines**: 6–10 words is a reasonable working target; personalization and genuine curiosity gaps outperform generic promotional language; use emojis sparingly and only where they fit brand voice (see `copywriting-and-messaging.md`).
- **Preview text**: Treat as a second headline — it should complement the subject line, not repeat it. A preview text that just restates the subject wastes real estate that could be doing more persuasive work.

## 5. Deliverability Fundamentals

Deliverability isn't a "set it and forget it" technical checkbox — it's an active reputation to maintain, and the rules tightened materially in the last two years.

- **Authentication (SPF, DKIM, DMARC)**: SPF authorizes which servers can send on the domain's behalf; DKIM cryptographically signs outgoing mail; DMARC enforces alignment between the two and sets a policy for failures (none/quarantine/reject). All three are baseline requirements now, not best-practice extras.
- **Bulk sender rules are real and enforced, not just guidance**: Google and Yahoo both classify a domain as a "bulk sender" once it crosses roughly 5,000 emails/day to personal Gmail/Yahoo addresses — and that classification does not expire if volume later drops. Bulk senders must have DMARC published, support one-click unsubscribe on marketing (not transactional) email, and keep spam complaint rates low — the commonly cited threshold is under roughly 0.3%, with under ~0.1% treated as the safer target. As of late 2025, enforcement moved from soft deferrals to outright rejection at the server level for non-compliant senders — this is a hard operational risk, not a theoretical one, so confirm current enforcement status before assuming yesterday's setup still clears the bar (see SKILL.md Section 6).
- **One-click unsubscribe** is required on marketing/promotional email under these rules; transactional email (password resets, order confirmations) is exempt.
- **List hygiene**: regularly suppress or sunset genuinely dead addresses (see win-back/sunset flow above) — a list padded with unengaged addresses drags down engagement rate and spam-complaint ratio, which then hurts deliverability for the *entire* list, including the good addresses.
- **Sender reputation is domain- and IP-level, not campaign-level** — one bad campaign (bought list, poor targeting, spammy content) can suppress inbox placement for unrelated future campaigns from the same domain.

## 6. Email Design Principles

- Single-column layout, roughly 600px max width — the safest default across the wide range of email clients still in use.
- Keep sections tight (roughly 50–125 words) with one clear CTA per email — an email asking for three different actions usually gets none of them.
- Design mobile-first: most email opens happen on mobile, and a desktop-first design that breaks on mobile loses the majority of the audience.


---


## FILE: references/emerging-trends-and-ai-marketing.md

# Emerging Trends & AI in Marketing

Read this file for: the current shape of AI's impact across marketing, and a rubric for deciding whether a new trend or platform is actually worth testing rather than chasing on hype alone. This is the fastest-moving file in the skill — apply SKILL.md Section 6 (currency caveats) especially strictly here, and verify anything time-sensitive before presenting it as current fact.

## 1. AI-Generated Content & Disclosure

Hybrid human-AI creative workflows (AI-assisted drafting/generation, human strategy/editing/final judgment) are now mainstream rather than novel. Disclosure requirements for AI-generated or AI-assisted marketing content vary by platform, region, and content type, and are actively evolving — confirm current requirements for the specific platform and market before publishing rather than assuming a prior rule still holds (see `image-and-creative-prompts.md` Section 9). This is general awareness, not legal advice.

## 2. AI-Driven Media Buying

Broad, AI-optimized targeting (Meta Advantage+, Google Performance Max) is now the default mode for paid social and search rather than an experimental option — see `ad-planning-and-paid-media.md` Section 3 for the full operational detail. The strategic implication worth internalizing: competitive advantage has shifted from targeting precision (increasingly commoditized by the platforms themselves) toward creative variety and first-party signal quality, which the algorithms can't manufacture on a brand's behalf.

## 3. AI Search / Answer Engines (AEO / GEO)

A meaningful and growing share of search behavior now resolves through AI-generated answers rather than a traditional results page — see `seo-and-sem.md` Section 4 for the full operational playbook. Treat any specific traffic-share or citation-rate statistic in this space with real skepticism (it's a heavily content-marketed topic with a lot of unverified numbers circulating) and verify before repeating one.

## 4. Social Commerce

Live shopping, in-app checkout, and creator storefronts continue to mature across platforms — Pinterest, TikTok, and Instagram all have meaningfully built-out native commerce surfaces (see the respective `platforms/*.md` files for current specifics). The strategic shift worth noting: commerce is increasingly happening natively inside the content platform rather than requiring an off-platform site visit, which changes both the creative approach (product needs to be discoverable and purchasable inside the scroll, not just advertised) and the measurement approach (on-platform conversion data vs. site analytics).

## 5. Privacy-First Infrastructure

Third-party cookie deprecation and mobile tracking restrictions (iOS App Tracking Transparency and equivalents) have permanently changed measurement and targeting — see `ad-planning-and-paid-media.md` Section 8 (Attribution) for the practical measurement response. On the marketing-ops side, the operational response is: invest in owned first-party data (see `email-crm-lifecycle.md`), implement server-side tracking (Meta Conversions API, Google Enhanced Conversions, or platform equivalents) to recover signal lost to client-side blocking, and treat contextual targeting as a legitimate primary tactic again rather than a fallback.

## 6. Community-Led Growth

Owned community spaces (Discord, Slack communities, dedicated forums) and structured brand-ambassador/UGC programs are an increasingly deliberate growth lever rather than an incidental side effect of having engaged customers — see `influencer-and-creator-partnerships.md` Section 6 for the UGC-program detail. The distinguishing trait of a genuine community-led strategy vs. a broadcast channel with a community label: two-way engagement and member-to-member value, not just brand-to-audience announcements.

## 7. Interactive & Immersive Content

Polls, quizzes, AR try-on, and shoppable video are moving from novelty to standard toolkit across major platforms (see `platforms/pinterest.md` and `platforms/instagram.md` for current native support). Evaluate these the same way as any other format — against the rubric in Section 8 — rather than adopting them by default just because they're available.

## 8. Rubric: Is This New Trend/Platform Worth Testing?

Chasing every new format or platform spreads a team thin without building expertise anywhere; ignoring all of them risks missing the next channel while it's still cheap. A structured filter beats both extremes:
1. **Audience presence**: is the actual ICP meaningfully there, or is this early-adopter noise that doesn't overlap with the real buyer?
2. **Cost of testing**: what's the real cost (money + team time + opportunity cost of attention) to run a genuine test, not just to "be present"?
3. **Signal timeline**: how long until a test would produce a real read on performance — a channel that takes six months to show signal needs a different commitment calculus than one that shows signal in two weeks.
4. **Differentiation potential**: is competition for attention on this channel/format still low enough that quality work stands out, or has it already saturated?
5. **Reversibility**: how easily can the team pull back if it doesn't work — a channel requiring a large upfront production or platform-specific skill investment is a bigger bet than one that's cheap to abandon.

A trend that scores well on audience presence and differentiation but poorly on cost/reversibility deserves a small, deliberately-scoped test — not a full program commitment on day one.


---


## FILE: references/image-and-creative-prompts.md

# Image & Creative Generation Prompts

Read this file for: writing image-generation prompts for marketing assets, ad creative, social graphics, and brand visuals — including matching generation output to a target size/resolution and choosing quality descriptors that actually do something. For platform-specific *dimension requirements* (the actual aspect ratios a placement needs), cross-check the relevant `platforms/*.md` — those numbers drift and are deliberately not hardcoded here (see SKILL.md Section 6). This file covers the generation *mechanics and craft* of hitting those dimensions well, which is a different, more durable layer. For the underlying creative strategy, see `strategy-and-positioning.md` and `content-planning-and-calendars.md`.

## 1. Prompt Anatomy

A strong marketing image prompt states, in order: **subject → setting → lighting → composition/framing → style/mood → technical specs → brand cues**. Vague prompts get generic results; the fix is almost always more specificity in setting and lighting, not a longer list of adjectives (see Section 2.3 on why adjective-stacking underperforms specificity).

```
A [mood] [style] photograph of [specific subject] in [specific setting],
[lighting description], [color palette], [composition/framing],
[emotion/atmosphere]. Shot on [camera/lens style, if photographic look wanted].
[Brand element: logo placement / color accent / product detail]. [Technical specs:
aspect ratio, resolution, quality descriptors].
```

## 2. Resolution, Output Size & Quality Descriptors

### 2.1 Matching Generation Output to a Target Size

State the target aspect ratio explicitly in the prompt itself — don't leave it to be resized after generation. Generating natively at the target ratio preserves the composition (negative space, focal point placement) that was actually composed for that shape; cropping a differently-composed image down to a new ratio after the fact frequently cuts off the intended focal point or the space reserved for a text overlay (see Section 6).

- **Get the target ratio from the actual destination**, not a guess — `platforms/*.md` is the source of truth for what a given placement needs.
- **Generation tool syntax for size/ratio varies by tool**: some accept an explicit aspect-ratio parameter, some accept exact pixel dimensions, some only offer a fixed preset list. Confirm current syntax for whichever tool is actually generating the image rather than assuming one universal format works everywhere.
- **Upscaling is sometimes unavoidable** when native output resolution is too low for the intended use. It can introduce its own artifacts (over-smoothed texture, fine-detail loss, occasional new artifacts at edges) — an upscaled asset needs the same final visual QA pass as any other output (Section 8), not less scrutiny just because it's "only a resize."

### 2.2 Resolution Needs by End-Use Tier

Resolution requirements scale with how the asset will actually be viewed. Treating every asset like it needs the same technical bar either wastes effort or under-delivers:
- **Small/digital-only** (social feed, email): lowest resolution tolerance — the platform typically re-compresses on upload anyway, and viewing size is small. Don't over-invest in resolution here at the expense of getting more generation attempts at the composition itself.
- **Mid-tier** (website hero, display ad, presentation slide): needs to hold up at a larger on-screen size without visible softness or compression artifact — a genuine, moderate resolution floor.
- **Large-format/print** (OOH, billboards, posters, printed collateral): the highest bar. Physical print and long viewing distance reveal detail loss that a small screen simply hides. This tier needs meaningfully higher native resolution (or a careful, artifact-checked upscale) *and* usually a simpler, bolder composition — fine detail reads poorly at billboard viewing distance regardless of source resolution. See the Print/Large-Format template in Section 3.

### 2.3 Quality Descriptors — What Actually Earns Its Place

Not every "quality" word in a prompt is doing real work. Two different things get called quality descriptors, and only one reliably changes output:
- **Specific, learnable technical/photographic terms** genuinely steer generation: "sharp focus," "shallow depth of field," "studio lighting," "color-accurate," "professional retouching," "35mm lens." These correspond to real visual concepts the model has actually learned from photography.
- **Vague quality boilerplate stacked at the end of a prompt** ("ultra-detailed, 8k, masterpiece, high quality, stunning, award-winning") is inconsistent across models and tools, and rarely does much once a reasonable baseline is already met — five overlapping quality buzzwords is a weaker use of prompt space than one or two well-chosen technical terms plus more specificity earlier in the prompt.
- **The real lever for perceived quality is specificity in subject/setting/lighting** (Section 1), not adjective density at the end — a precisely-described scene with minimal quality language consistently outperforms a vague scene buried in quality buzzwords.
- Always visually confirm the actual output meets the bar (Section 8) — a prompt with the "right" quality words is not a substitute for reviewing what actually got generated.

## 3. Template Library by Asset Type

**Social Media Ad (feed/reel)**
```
A [mood] [style] photograph of [subject] in [setting], [lighting description],
[color palette], [composition], [emotion/atmosphere]. Shot on [camera/lens].
[Brand element: subtle logo placement/color accent]. Clean background,
high contrast, mobile-optimized, [aspect ratio per platform — see platforms/*.md].
```

**Hero Banner / Website Header**
```
A [wide-angle/hero shot] of [subject/scene], [dramatic lighting],
[brand colors as accent], [depth and layers], [professional retouching].
[16:9 or per-placement ratio], generous negative space on [left/right] for
text overlay, corporate yet approachable.
```

**Product Photography**
```
Studio product shot of [product] on [surface/material], [lighting setup],
[shadow style], [contextual props], [angle]. Sharp focus, commercial
photography, color-accurate, reflection control, e-commerce ready, 1:1
aspect ratio.
```

**Influencer / Lifestyle / UGC-style**
```
Candid lifestyle photo of [demographic] [activity] in [location],
natural [time of day] lighting, authentic emotion, [brand product] naturally
integrated, relatable and aspirational, social-media-native, warm tones,
shallow depth of field, slightly imperfect framing (not studio-polished).
```

**Testimonial / Social-Proof Graphic**
```
Clean, minimal graphic layout with generous negative space for a quote
overlay, [brand color palette], subtle [texture/pattern] background,
professional but warm, room in [top/bottom/side] third for text, no
competing visual elements near the quote zone.
```

**Before / After**
```
Split-composition image, [left/right or top/bottom] divide, consistent
lighting and camera angle across both halves so the only variable is the
change itself, [subject/context], clear visual contrast between the two
states, clean dividing line, no distracting background elements.
```

**Infographic-Style Visual**
```
Flat, modern infographic illustration of [concept/process], [brand color
palette], simple iconography, clear visual hierarchy guiding the eye from
[start point] to [end point], generous white space, minimal text baked into
the image (add real text as an overlay layer instead — see Section 6).
```

**App/Product UI Mockup**
```
Clean device mockup ([phone/laptop/tablet] frame) displaying [app/product
screen], realistic screen glare/reflection at low intensity, neutral or
brand-colored background, soft shadow beneath device, professional product
marketing style.
```

**Email Header Graphic**
```
Wide, short-aspect banner image of [subject/scene], [brand color palette],
[lighting], designed with a clear focal point that survives being cropped
narrow on mobile email clients, minimal fine detail (email images render
small — see Section 2.2), [600px-width-safe composition].
```

**Carousel — Multi-Panel Consistency**
```
[Base prompt describing subject/setting/lighting/style], panel [N] of [total]:
[what's different in this specific panel]. Keep camera angle, lighting
direction, color grade, and subject styling identical across all panels
in the set — only the panel-specific element listed above should change.
```
Generate carousels as a named series and explicitly re-state the shared constants in every panel's prompt — image generation models don't retain a "style memory" between separate generations, so consistency has to be engineered into each prompt, not assumed.

**Seasonal/Promotional Overlay Base**
```
[Base product/lifestyle scene], composition leaves clear open space in
[quadrant] for a promotional graphic/badge to be added in post, avoid
generating text or numbers in the image itself (see Section 6), [seasonal
color palette/motifs] worked into props/background rather than overlaid text.
```

**Print / Large-Format / OOH**
```
[Subject/scene] composed boldly and simply for distant viewing — one large,
unmistakable focal point, minimal fine detail that would be lost at viewing
distance, high contrast for readability from far away. [Lighting], [brand
colors]. Generate at the highest native resolution the tool supports for
this composition, and plan a dedicated, artifact-checked upscale pass if
the final physical size requires it (see Section 2.1–2.2).
```
The composition brief here is genuinely different from every other template in this list, not just the resolution: billboard and large-poster viewing happens from a distance and often at speed (a passing car, a walked-past poster), so the design has to work as one glanceable idea — a busy, detail-rich composition that reads well on a phone screen usually fails at this scale.

## 4. Visual Style Directives

- **Luxury/Premium**: Soft lighting, muted palettes, minimal props, generous negative space, serif-adjacent visual cues
- **Tech/SaaS**: Clean lines, gradient accents, isometric or abstract-geometric elements, blue/cyan/purple palettes, modern sans-serif visual language
- **Wellness/Lifestyle**: Earth tones, natural light, organic textures, candid unposed moments, warm filters
- **Edgy/Youth**: High contrast, bold saturated colors, dynamic angles, street aesthetic, visible grain/texture
- **Corporate/B2B**: Professional settings, confident poses, structured/grid-based layouts, trustworthy blues and grays
- **Minimalist/Scandinavian**: Neutral palette, abundant negative space, one clear focal object, natural materials, soft diffused light
- **Maximalist/Retro-Revival**: Saturated clashing colors, pattern-on-pattern, playful composition, nostalgic references worn lightly rather than literally
- **Editorial/Fashion**: Dramatic directional lighting, strong single focal point, sophisticated color grading, intentional negative space as a compositional element
- **Playful/Gen-Z**: Bright flat colors, exaggerated proportions or props, irreverent composition, deliberately imperfect/handmade feel over polish
- **Heritage/Craft**: Warm, slightly desaturated tones, tactile/textured materials in frame, natural imperfection, storytelling props over sterile staging

## 5. Negative Prompt Guidance

State explicitly what to avoid — it does as much work as the positive prompt:
- **Avoid the generic "stock photo" look**: exclude "posed," "staged," "obviously stock," "corporate stock photography" when authenticity is the goal.
- **Avoid AI-image tells**: excessive symmetry, waxy/over-smoothed skin, malformed hands/text, uncanny-valley expressions — flag these as things to avoid, and always visually review output rather than trusting the prompt alone to prevent them.
- **Avoid heavy in-image text** where the platform's delivery algorithm penalizes it (see the Meta text-overlay note in `platforms/instagram.md`) — generate clean visuals and add text as a separate overlay layer instead (see Section 6).
- **Avoid competitor or real-brand visual cues** unintentionally — don't let "premium tech aesthetic" drift into replicating a specific real competitor's actual visual identity.

## 6. Text-in-Image: Generate Clean, Overlay Separately

Image generation models are unreliable at rendering legible, correctly-spelled text directly into an image, and several platforms' delivery algorithms still soft-penalize heavy in-image text even where it's not against a hard policy (see `platforms/instagram.md`). The reliable workflow: generate the visual completely clean, with composition that leaves clear negative space where text will go, then add real, crisp text as a separate design layer. Say so explicitly in the prompt ("leave clear open space in [location] for a text overlay to be added separately") rather than asking the model to render the words.

## 7. Brand Consistency Across a Set

- **Inject exact brand colors** as hex-adjacent descriptions ("a specific warm coral, not generic orange/red") rather than vague color names — vague color words drift generation to generation.
- **Anchor a consistent subject/style description** and reuse it verbatim across every prompt in a campaign set, changing only the scene-specific elements — the same discipline as the carousel guidance in Section 3.
- **Keep a running "style sheet"** of the exact phrases that produced on-brand results in past generations for a given brand, and reuse them — this is the fastest way to get repeatable output across a long campaign without redoing style discovery every time.

## 8. Iteration & Refinement Workflow

1. Generate against the brief, then critique the output against the brief specifically — not against a vague "does this look good" — did it hit subject, setting, lighting, composition, and brand cues as specified?
2. Isolate what's wrong and change only that element in the next prompt (composition, lighting, subject pose) — regenerating from scratch with a totally different prompt loses whatever was already working.
3. For anything going to production (paid media, a public-facing asset, anything upscaled per Section 2.1), do a final human visual QA pass specifically for AI-generation artifacts (Section 5) before it ships — these are easy to miss when reviewing quickly at thumbnail size.

## 9. AI-Generated Content Disclosure

Platform and regulatory disclosure requirements for AI-generated or AI-assisted marketing imagery are evolving and vary by platform, region, and use case — this is a compliance question, not a creative one, so confirm current requirements for the specific platform and market before publishing rather than assuming last year's rule still applies (see SKILL.md Section 6). This is general awareness, not legal advice.


---


## FILE: references/influencer-and-creator-partnerships.md

# Influencer & Creator Partnerships

Read this file for: creator tiers, sourcing and vetting, contract/usage-rights essentials, rate benchmarking approach, campaign structuring, and UGC programs as a distinct lever from paid influencer work.

## 1. Creator Tiers

Rough, commonly-used follower bands (exact cutoffs vary by source and platform — treat as directional, not official):
- **Nano** (roughly 1K–10K): highest trust/engagement rate per follower, lowest reach, often the best cost-per-engagement, best for hyper-relevant niche fit and authentic UGC-style content.
- **Micro** (roughly 10K–100K): still strong engagement, more production consistency than nano, the workhorse tier for most mid-sized brand programs.
- **Mid-tier** (roughly 100K–500K): meaningful reach with still-reasonable engagement, more professional/agency-managed than smaller tiers.
- **Macro** (roughly 500K–1M): significant reach, engagement rate typically declines relative to smaller tiers, closer to a media buy than a genuine endorsement in how the audience perceives it.
- **Mega/Celebrity** (1M+): broad awareness and brand halo, weakest relative engagement rate, priced and negotiated closer to traditional celebrity endorsement than typical creator partnership.

## 2. Sourcing & Vetting

- **Audience quality check**: look past follower count to engagement rate, comment quality (genuine responses vs. bot/generic spam), and audience overlap with the actual target demographic — a large but disengaged or misaligned audience is a poor buy regardless of the headline follower number.
- **Engagement rate benchmarks vary sharply by tier and platform**: nano/micro creators typically post noticeably higher engagement rates than macro/mega — don't compare a nano creator's rate against a mega creator's rate as if they should be similar; compare within tier.
- **Brand fit assessment**: review the creator's actual content history and past brand partnerships (frequency, categories, apparent authenticity of past endorsements) — a creator who promotes a new brand every other post has trained their audience to tune out the promotion.

## 3. Contract & Usage Rights Essentials

- **Content usage rights**: define exactly where the brand can reuse the content — organic repost only, or also paid amplification (see whitelisting below), and for how long. "Usage rights" without a specified duration and channel scope is an underspecified contract term that causes disputes later.
- **Whitelisting / creator-authorized ads**: running paid ads through the creator's own handle (rather than the brand's) using their granted ad permissions — typically commands a separate, additional fee beyond the base content fee, since it's a materially different and more valuable usage than an organic post.
- **Exclusivity**: category exclusivity (the creator won't promote a direct competitor for a defined window) is a common and reasonable ask, but it should be priced into the fee — exclusivity has real opportunity cost for the creator.
- **FTC/regulatory disclosure**: sponsored content disclosure requirements (clear #ad/#sponsored/paid-partnership labeling) are well-established baseline requirements in most major markets — this isn't optional or a nice-to-have, and it's the brand's risk as much as the creator's if it's skipped.

## 4. Rate Benchmarking Approach

Rather than quoting fixed dollar figures (which vary enormously by niche, platform, and market, and go stale immediately), benchmark using a repeatable method:
- **Cost-per-engagement or cost-per-mille comparison**: normalize a proposed rate against the creator's typical engagement/reach to see how it compares to other media buys with a similar expected outcome.
- **Compare against a basket of similar-tier creators**, not a single anchor — a single comparison point is easy to game (by either side) in a negotiation.
- **Factor in usage rights and exclusivity separately** from the base content fee (see Section 3) — bundling everything into one number makes it hard to negotiate any single term independently.

## 5. Campaign Structuring

- **Seeding vs. paid partnership**: sending product for organic, unpaid consideration (seeding) is a legitimate lower-cost/lower-certainty lever, distinct from a paid guaranteed-deliverable partnership — be explicit internally about which motion a given creator relationship is, since the expectations (and disclosure obligations, if content results) differ.
- **Brief for authenticity, not a script**: the strongest-performing creator content usually comes from giving the creator the key message and letting them execute in their own voice/format, rather than a word-for-word script — audiences are good at detecting when a creator is reading brand copy verbatim.
- **Usage rights negotiation is part of campaign structuring, not an afterthought** — decide before the campaign whether the content is meant to be repurposed as paid media, and negotiate accordingly (see Section 3).

## 6. UGC Programs (Distinct from Influencer Marketing)

User-generated content programs — soliciting content from customers/fans rather than paid creators — is a distinct lever with different economics: typically lower cost per asset, higher perceived authenticity, but less production consistency and less guaranteed reach than a paid creator partnership. Many brands run both simultaneously: UGC for a steady stream of authentic, low-cost creative testing material (see the creative testing methodology in `ad-planning-and-paid-media.md`), paid creator partnerships for guaranteed reach and production quality on flagship campaigns.


---


## FILE: references/seo-and-sem.md

# SEO, SEM & AI-Search Optimization

Read this file for: on-page and technical SEO, keyword research, topic clusters, SEM/PPC search campaign structure, and optimizing for AI-generated answers (AEO/GEO). For editorial calendar mechanics, see `content-planning-and-calendars.md`.

## 1. On-Page SEO Fundamentals

- **Title tags**: front-load the primary keyword/intent, keep it distinct from every other page's title on the site — duplicate or near-duplicate titles confuse both search engines and users deciding which result to click.
- **Meta descriptions**: written to earn the click (they're a pitch, not a ranking factor directly) — specific and benefit-forward beats generic.
- **Header structure**: one H1 per page reflecting the core topic, H2s/H3s structuring genuine subtopics (not just formatting for formatting's sake) — a clean header hierarchy is also exactly what both classic search snippets and AI answer engines lean on to extract structure (see Section 4).
- **Internal linking**: link to and from related content using descriptive anchor text (not "click here") — this is how both crawlers and readers understand topical relationships across the site.
- **Schema markup**: structured data (FAQ, HowTo, Product, Article, etc.) that explicitly tells search engines and AI crawlers what a page contains — increasingly important as more of the answer surface is machine-extracted rather than click-through (see Section 4).

## 2. Technical SEO Basics

- **Crawlability**: confirm nothing important is accidentally blocked in robots.txt or noindexed; a clean XML sitemap submitted to Search Console.
- **Site speed / Core Web Vitals**: page-load and interactivity metrics that affect both ranking and, more directly, conversion rate — slow pages lose people regardless of rank.
- **Mobile-first**: the mobile version of a page is what search engines primarily evaluate — a desktop-polished, mobile-broken page underperforms regardless of desktop quality.

## 3. Keyword Research Process

1. **Classify by search intent**: informational ("how does X work"), navigational ("brand name login"), commercial investigation ("best X for Y," "X vs Y"), transactional ("buy X," "X pricing"). The content format should match the intent — a transactional query landing on a pure educational blog post underperforms even if the keyword volume looked attractive.
2. **Build topic clusters**: a pillar page covering a broad topic comprehensively, linked to and from a cluster of narrower supporting pages on subtopics. This structure signals topical authority more effectively than isolated, unlinked pages targeting the same general subject.
3. **Content gap analysis**: identify what real customer questions and competitor-ranking topics have no corresponding page yet — the gap between "what people are asking" and "what we currently answer" is usually the highest-leverage content backlog.

## 4. AI-Search Optimization (AEO / GEO)

Traditional SEO gets a page ranked; a meaningful and growing share of search behavior now resolves through AI-generated summaries (Google AI Overviews, ChatGPT, Perplexity, and similar) that answer the question directly, sometimes without a click at all. This doesn't replace SEO — it adds a layer on top of it, and the fundamentals (crawlable, well-structured, genuinely authoritative content) are still the foundation either way.

- **AEO (Answer Engine Optimization)**: structuring specific content so it's easily extracted as a direct answer — concise, self-contained answer paragraphs near the top of a section, clear question-formatted subheadings, and content formatted to match how the topic is typically surfaced (paragraph, list, or table — check what format currently shows for the target query and match it).
- **GEO (Generative Engine Optimization)**: the broader practice of building brand presence and authority such that generative AI systems cite or recommend the brand when synthesizing an answer — this leans more on earned authority, consistent entity presence across the web, and third-party mentions than on any single on-page trick.
- **Entity clarity**: make sure the brand, product, and key concepts are unambiguously and consistently described across the site and in structured data — AI systems (like classic search) rely heavily on being able to confidently resolve "what/who is this" before citing it.
- **This is a fast-moving, heavily-covered area with a lot of unverified statistics circulating** — treat specific percentage claims about AI-search traffic share or citation-rate lift with real skepticism, verify against current reporting before repeating a number, and lean on the durable structural advice (clear direct answers, schema, entity consistency, earned third-party citations) over any single "hack."

## 5. SEM / PPC Search Campaigns

*For the full Google Ads campaign-type taxonomy (Search, Display, Shopping, Demand Gen, Performance Max, App), Smart Bidding strategy names, conversion tracking, ad Assets, and Google ad policy, see `platforms/google-ads.md`. This section covers Search campaign structure specifically.*

- **Structure**: Campaign (budget + goal) → Ad Group (tightly themed keyword cluster) → Keywords + Ads. A tightly themed ad group (a handful of closely related keywords) lets the ad copy actually match the query — a loosely grouped ad group forces generic copy that matches nothing well.
- **Match types**: broad, phrase, and exact match trade reach for precision — broad match now leans heavily on the platform's own AI matching rather than literal keyword matching, so it needs closer monitoring (and negative keywords) than it used to.
- **Quality Score factors**: expected CTR, ad relevance, and landing page experience — a low Quality Score raises effective cost per click even at the same bid, so landing page relevance is a cost lever, not just a conversion lever.
- **Responsive Search Ads (RSAs)**: supply multiple headline/description variations and let the platform test combinations — provide genuinely distinct messaging angles across the variations (not just minor rewordings) so the system has real options to test, not near-duplicates.
- **Negative keywords**: actively maintained, not a one-time setup — review search term reports regularly to catch irrelevant queries burning budget, especially under broad match.


---


## FILE: references/strategy-and-positioning.md

# Strategy & Positioning

Read this file for: brand strategy, campaign strategy, go-to-market planning, ideal customer profile (ICP) and persona work, competitive positioning, and channel/budget planning at the strategic level.

## 1. Brand Strategy & Positioning

### 1.1 Differentiation Framework
Before any campaign work, establish:
- **Category**: What frame of reference does the buyer already have for this? (Fighting the category is expensive; using it is cheap.)
- **Point of difference**: The one or two things that are true of this brand and not true of the main alternatives.
- **Reason to believe**: Proof the difference is real — data, mechanism, guarantee, credential. A claim without a reason to believe is just an adjective.
- **Who it's not for**: A positioning that tries to fit everyone fits no one memorably. Naming the non-audience sharpens the message for the real one.

### 1.2 Value Proposition Design
Structure every value prop as: **[Target customer]** who **[has this problem/job-to-be-done]** gets **[this outcome]** because of **[this mechanism]**, unlike **[the main alternative]**, which **[falls short in this specific way]**.
This format forces specificity — "we're better" and "we're the leading provider of X" both fail this test because they don't name a mechanism or a real alternative.

### 1.3 Brand Architecture
- **Branded house**: One master brand across all products (Google, FedEx). Efficient equity-building, but a failure in one product can bleed into all.
- **House of brands**: Independent brands under a parent (P&G, most conglomerates). Isolates risk, allows sharp positioning per brand, costs more to build each one from zero.
- **Endorsed brands**: Sub-brands carry the parent's name as a credibility stamp (Marriott Courtyard). A middle path — most startups and scale-ups default here without deciding to, which is worth flagging if it's happening by accident.

### 1.4 ICP & Persona Development
A usable persona has, at minimum: the job/role, the specific trigger event that starts their buying process, the outcome they're personally measured on (not just the company's outcome), their real objections (not the sanitized ones), and where they actually go to research a decision like this. A persona built from internal assumptions instead of real customer interviews is a guess wearing a name tag — validate with actual interviews before treating it as fact.

### 1.5 Competitive Positioning
Map competitors on the two axes that actually matter to the buyer (rarely "price" and "quality" — usually something more specific like "self-serve vs. white-glove" or "breadth vs. depth"). The goal isn't to prove superiority on every axis; it's to find where there's open, defensible ground.

## 2. Campaign Strategy

### 2.1 The AIDA+ Method
Map every campaign's content to the classic AIDA arc, extended with a growth stage. (This is a content-mapping framework, not a go-to-market plan — don't call it "GTM," that term means something different and more specific; see 2.2.)
- **Attention**: Hook creative, thumb-stopping visuals, provocative headlines
- **Interest**: Problem agitation, curiosity gaps, social proof teasers
- **Desire**: Transformation stories, benefit stacking, scarcity/urgency
- **Action**: Clear CTA, friction reduction, incentive alignment
- **Growth**: Referral loops, retention hooks, loyalty amplification

### 2.2 Go-To-Market Planning
A real GTM plan answers five questions in order — skipping ahead (especially straight to "channel") is the most common GTM failure mode:
1. **Market**: Who exactly, and how big is the addressable slice worth pursuing first?
2. **Product**: What's the wedge — the specific use case this is best-in-world at, not everything it can theoretically do?
3. **Positioning & pricing**: How is it framed against alternatives, and does the price signal match the position (a premium claim at a discount price undercuts itself)?
4. **Channel**: Where does this ICP actually make buying decisions — not where the team likes to post.
5. **Launch motion & timeline**: Sequenced rollout (beta/waitlist → soft launch → full launch) with clear go/no-go criteria between stages, not a single big-bang date.

### 2.3 Objective Setting
Every campaign objective should be a SMART goal that maps to one tier of the KPI Hierarchy (see main SKILL.md, Section 3.2) — e.g. "reduce CPA to $X within Y weeks while holding lead quality above Z" is a leading+lagging pair, not just a lagging number in isolation. An objective with no leading-indicator target attached is unfalsifiable until it's too late to course-correct.

### 2.4 Funnel Architecture
See main SKILL.md, Section 3.1 — TOFU/MOFU/BOFU/Retention. Use it to sanity-check a campaign brief: if 90% of planned content sits in one funnel stage, the plan is probably lopsided (all-TOFU campaigns build awareness that never converts; all-BOFU campaigns run out of warm audience fast).

### 2.5 Channel Selection Matrix
| Goal | Primary | Secondary | Creative Type |
|------|---------|-----------|---------------|
| Brand Awareness | TikTok / YouTube | Instagram / Display | Video, UGC |
| Lead Generation | LinkedIn / Meta | Google / Programmatic | Carousel, Lead Forms |
| E-commerce Sales | Meta / TikTok | Google Shopping / Pinterest | Dynamic Product, Video |
| B2B Authority | LinkedIn / Email | X / YouTube | Whitepapers, Case Studies |
| App Installs | TikTok / Instagram | Google UAC | Short Video, Playables |
| High-Intent Discovery/Commerce | Pinterest / Google Search | Instagram Shopping | Product Pins, Search Ads |

This is a default starting matrix, not a rule — a genuinely differentiated channel choice (e.g. B2B on TikTok, done well) can outperform the "safe" default precisely because there's less competition for attention there. Use the matrix to start the conversation, not to end it.

### 2.6 Budget Planning at the Strategy Level
Two common methods, use whichever fits the maturity stage:
- **Objective-based (build up)**: Define the objective (e.g. X qualified leads), work backward through expected conversion rates at each funnel stage to the required spend. More defensible, harder to do without existing funnel data.
- **Percentage-of-revenue (top down)**: Common ranges cited industry-wide run roughly 5–15% of revenue for established brands and higher for aggressive growth-stage companies — treat any specific benchmark like this as a rough anchor to sanity-check against, not a target to hit exactly; the right number depends entirely on margin structure, growth stage, and LTV:CAC economics (see `analytics-testing-and-optimization.md`).

### 2.7 Market & Competitive Research Process
1. Identify the real competitive set (including the "do nothing" / status quo alternative — often the actual biggest competitor for a new category).
2. Audit their positioning, pricing, and channel mix — not just their product features.
3. Identify the gap: where is a real customer need underserved by every current option?
4. Pressure-test the gap with actual prospects before building a campaign around it — a gap the team is excited about and a gap customers will pay to close are not always the same gap.


---


## FILE: references/platforms/facebook.md

# Facebook Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against Meta's current Ads Manager before finalizing production assets (see SKILL.md Section 6).*

## Organic Content

- **Audience skews older** than Instagram/TikTok on average, and organic reach for brand-page posts has been structurally low for years — Facebook's organic value today is concentrated more in **Groups and community** than in brand-page broadcast posting. A brand-run or brand-adjacent Group with genuine member value typically outperforms brand-page posting for organic engagement.
- **Marketplace**: a meaningfully large, often-overlooked commerce/discovery surface, particularly for local and secondhand-adjacent categories.
- **Long-form organic content** (event posts, community updates, longer captions) still has real viability here in a way it doesn't on more short-form-dominant platforms — the audience and format expectations are different from Instagram even though both run through the same Meta backend.

## Ad Formats & Specs

Facebook ads run through the same Meta Ads Manager as Instagram and Threads, and share the same underlying creative specs and text-overlay guidance — see `platforms/instagram.md` for the shared Meta-wide creative detail (dimensions, the retired 20% text rule) and `platforms/meta-ads-manager.md` for account mechanics: objectives, CBO/ABO budget structure, audience-building, Pixel/CAPI, and ad policy. Facebook-specific placement notes:

- **Additional placements unique to Facebook** beyond feed/Stories/Reels: right-column ads (desktop only, lower cost, lower engagement — a cheap supplementary placement rather than a primary one), Marketplace ads, and in-stream video ads.
- **Lead Ads** (native lead-gen forms that pre-fill with the user's Facebook profile data) remain a strong lower-friction format specifically on this platform, converting at a higher rate than sending the same audience to an external landing page, at some cost to lead quality — pair with fast follow-up and lead-quality tracking.

## Practical Notes

- Because Facebook, Instagram, and Threads now share one Ads Manager and one AI-driven delivery system, most campaigns should be planned as **one Meta campaign with Advantage+ placements**, not as three separate platform-specific buys — see `ad-planning-and-paid-media.md` Section 3. Reserve a Facebook-only buy for the specific cases above (Groups strategy, Marketplace, right-column) where the platform's distinct audience or format genuinely calls for separate treatment.


---


## FILE: references/platforms/google-ads.md

# Google Ads — Campaign Types & Account Mechanics

*Covers Search, Display, Shopping, Video, Demand Gen, Performance Max, and App campaigns as account-setup mechanics. For keyword research, match types, Quality Score, and RSA copy specific to Search, see `seo-and-sem.md` Section 5 (not duplicated here). Google Ads campaign types are actively consolidating right now — confirm current availability directly in Google Ads before finalizing a media plan (see SKILL.md Section 6).*

## 1. Campaign Type Taxonomy

Google has been folding older, more granular campaign types into broader AI-driven ones, and this consolidation is still in progress. Current core types:

- **Search**: text ads on Google's own results for active queries. Highest-intent, most keyword-controllable format — see `seo-and-sem.md` Section 5 for full structure.
- **Performance Max (PMax)**: single campaign, AI-driven, spans nearly all Google inventory (Search, Display, YouTube, Discover, Gmail, Maps, Shopping) from one asset group and one budget. See `ad-planning-and-paid-media.md` Section 3 for strategic framing; Section 3 below for mechanics.
- **Shopping**: product-listing ads driven by a Merchant Center feed. Increasingly run through Performance Max rather than standalone, though standalone Shopping still exists for advertisers who want direct product-level bid control PMax abstracts away.
- **Demand Gen**: visual, feed-native ads across YouTube (including Shorts), Discover, Gmail, and Maps — built to create interest before a searcher has expressed explicit intent, positioned upper-to-mid-funnel. This absorbed the older **Discovery** campaign type and, more recently, **Video Action Campaigns** — if older material treats either as a separate campaign type, they now live inside Demand Gen.
- **Display**: Responsive Display Ads across the Google Display Network. **Standalone Display campaigns are actively being phased out and migrated into Demand Gen** — confirm current availability before planning a new standalone Display buy; this consolidation was still actively rolling out as of mid-2026 and may no longer be offered for new campaigns by the time this is read.
- **Video**: YouTube-specific placements, increasingly overlapping with Demand Gen's YouTube inventory — see `platforms/youtube.md`.
- **App**: automated campaigns built to drive installs and in-app actions from a small set of creative assets across Google's full inventory.
- **AI Max for Search**: a newer AI layer sitting on top of Search campaigns that broadens keyword matching and asset combination automatically — distinct from Performance Max (which spans campaign types); this stays within Search inventory specifically.
- **Local**: increasingly handled through Performance Max's local-inventory capability rather than a dedicated standalone Local campaign type.

## 2. Choosing a Campaign Type

The decisive question is intent, not channel preference:
- **Demand already exists** (people actively search for this) → Search first — closest to purchase, fastest clean read on whether the underlying economics work.
- **Demand needs creating** (the audience doesn't know to search for this yet) → Demand Gen or Video/YouTube.
- **Selling physical products with a feed** → Shopping or Performance Max, depending on how much manual product-level bid control is wanted.
- **Driving app installs** → App campaigns.
- **A commonly recommended combined structure** pairs Performance Max for full-funnel automated reach, Search (with or without the AI Max layer) for captured high-intent demand, and Demand Gen for upper-funnel consideration — treat these as complementary, not mutually exclusive. The usual rationale for keeping Search running alongside PMax specifically: it preserves branded-query control and the competitive impression-share visibility that PMax's more automated, less transparent reporting doesn't fully surface.

## 3. Smart Bidding Strategies

| Strategy | Optimizes For | Use When |
|---|---|---|
| Maximize Conversions | Conversion volume within budget | Early learning phase, building conversion signal |
| Maximize Conversion Value | Total conversion value within budget | E-commerce with varied order values, once there's enough volume to model value reliably |
| Target CPA | A specific cost-per-conversion goal | Stable conversion volume, protecting unit economics on cost per lead/sale |
| Target ROAS | A specific return-on-ad-spend goal | E-commerce with reliable revenue tracking and enough conversion volume to model against |
| Manual CPC / Enhanced CPC | Direct bid control, with optional automated adjustment | Full manual control, or a transitional step before full Smart Bidding |

Maps directly to the platform-agnostic bid guidance in `ad-planning-and-paid-media.md` Section 4 — same logic (start broad/volume-focused to build signal, tighten toward a cost or value target once there's enough data), just under Google's naming.

## 4. Shopping & Merchant Center

Shopping ads (standalone or via Performance Max) run entirely off a product feed configured in **Google Merchant Center** — accurate, complete product data (title, price, availability, product identifiers, quality imagery) is the actual creative lever here, not manually written ad copy. A feed with missing identifiers, stale pricing, or poor imagery undermines performance regardless of bid strategy or budget — directly analogous to Meta's Advantage+ Shopping depending on Commerce Manager catalog quality (see `meta-ads-manager.md` Section 7).

## 5. Conversion Tracking

- **Google tag (gtag.js) or Google Tag Manager**: the client-side foundation for conversion tracking across Search, Display, Shopping, and Video.
- **GA4 linking**: connecting Google Analytics 4 to Google Ads for shared conversion/audience data and richer post-click behavioral reporting than Ads' own interface provides alone.
- **Enhanced Conversions**: server-side-assisted matching that sends hashed first-party customer data (email, phone, address) alongside a conversion event to improve match accuracy as cookie-based tracking degrades — the direct Google-side equivalent of Meta's Pixel + CAPI pairing (Section 4 of `meta-ads-manager.md`), and increasingly a baseline setup step rather than an optional add-on.

## 6. Ad Extensions / Assets

Google renamed "ad extensions" to **"Assets"** — sitelinks, callouts, structured snippets, call, location, and price information are managed as Assets at the account, campaign, or ad-group level rather than a separate extensions tab. Not optional polish: Assets materially increase an ad's real estate on the results page and are a real factor in Ad Rank (which also drives cost-per-click) — a Search ad running with no Assets attached is leaving both visibility and cost-efficiency on the table.

## 7. Ad Policy Essentials

- **Restricted categories requiring certification/special approval**: healthcare and pharmaceuticals, financial services, alcohol, gambling, and political/election advertising — broadly parallel to Meta's restricted-category list (see `meta-ads-manager.md` Section 5), though the certification process is Google's own and shouldn't be assumed identical.
- **Common disapproval triggers**: misleading or unsubstantiated claims, destination mismatches (the ad promises something the landing page doesn't deliver), trademark misuse in ad copy, and "unacceptable business practices" — a broad catch-all Google applies to anything that reads as deceptive even without a narrower policy technically being violated.
- **Landing page requirements**: functional, genuinely relevant to the ad's claim, and transparent about the business — a mismatch here factors into Quality Score (see `seo-and-sem.md` Section 5) as well as being a standalone policy risk.


---


## FILE: references/platforms/instagram.md

# Instagram Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against Meta's current Ads Manager and Help Center before finalizing production assets (see SKILL.md Section 6).*

## Organic Content by Surface

- **Reels**: The primary discovery surface. 7–15 second hooks, trending audio (native audio still generally outperforms muted/no-audio for reach), text-on-screen for sound-off viewers, loop-worthy endings that reward rewatching.
- **Stories**: Polls, quizzes, and the **Link sticker** for click-throughs — this replaced the old "swipe-up" gesture in 2021 and has **no follower minimum**; every account, regardless of size, can add a tappable link to a Story. Good for behind-the-scenes, real-time, lower-production content.
- **Feed**: High-res imagery, carousels for educational/step-by-step content, a consistent aesthetic across the grid still matters for profile-visit conversion even though most discovery now happens via Reels/Explore rather than the grid itself.
- **Shopping**: Product tags on posts/Reels, collection showcases, native checkout where available by market — increasingly central to how commerce brands use the platform rather than a bolt-on feature.

## Ad Formats & Specs

*For campaign objectives, budget structure (CBO/ABO), audience-building, Pixel/CAPI setup, and ad policy — all shared across Facebook/Instagram/Threads — see `platforms/meta-ads-manager.md`.*

- **Dimensions**: 1:1 or 4:5 for feed (4:5 takes up more mobile screen space and frequently outperforms 1:1 on engagement); 9:16 for Stories/Reels placements.
- **Text overlay**: Meta retired its hard 20% text cap in 2020 — text-heavy images are no longer rejected outright — but the delivery algorithm still soft-penalizes text-heavy creative with lower predicted CTR and higher effective CPMs. Treat "keep it light" as a performance best practice, not a compliance rule.
- **Placements run through Meta Ads Manager** alongside Facebook — most advertisers build once and let Advantage+ placements decide the mix across Instagram feed/Stories/Reels/Explore rather than manually picking each surface (see `ad-planning-and-paid-media.md` Section 3).

## Algorithm & Ranking Notes

- Watch time and rewatches are strong signals for Reels distribution specifically — a short, loopable format frequently outperforms a longer one with a weaker ending.
- Saves and shares are read as stronger intent signals than likes for broader distribution — content designed to be saved (reference-style, list-style) or shared (relatable, surprising) tends to earn more reach than content designed only to be liked.
- Consistency of posting matters less than consistency of *quality relative to the account's own baseline* — a sudden low-effort post can suppress an account's subsequent reach more than an irregular posting schedule does.

## Practical Notes

- Auto-cross-posted content from other platforms (especially TikTok watermarked video) is measurably deprioritized — re-export or re-edit native Reels rather than reposting as-is when Instagram is a real priority surface, not an afterthought.
- Carousel posts remain a strong, underused format for educational/how-to content — they reward a swipe-through completion signal similarly to how video rewards watch-through.


---


## FILE: references/platforms/linkedin.md

# LinkedIn Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against LinkedIn's current Campaign Manager before finalizing production assets (see SKILL.md Section 6).*

## Organic Content

- **Thought leadership**: Personal profile posts (from founders/executives/subject-matter experts) frequently outreach company-page posts on this platform specifically — LinkedIn's algorithm and audience both favor a named person's voice over a corporate account's. A personal-plus-company-page combined strategy generally outperforms either alone.
- **Native document posts** (PDF carousels/slide-style posts uploaded directly): consistently strong organic reach format for structured, educational content.
- **B2B creative**: Clean, professional, data-driven visuals; client logos and concrete proof points read as more credible here than the more aspirational/lifestyle creative style that works on consumer platforms.
- **Strategic commenting**: Thoughtful, substantive comments on target accounts' posts is a genuine, effective way to build visibility with prospects — do this organically, one account at a time. This is a **different tactic from "engagement pods"** (closed groups that reciprocally like/comment to game the algorithm), which carry real risk of account restriction and violate platform guidelines. Don't conflate the two — one is normal relationship-building, the other is manipulation with downside risk.

## Ad Formats & Specs

LinkedIn runs a wide format set: single image, carousel, video, document ads, event ads, article/newsletter ads, thought leader ads (boosting an individual's organic post rather than a company-page asset), sponsored messaging (Message and Conversation ads), dynamic ads, text ads, and connected TV.

- **Single image**: 1.91:1 landscape (roughly 1200×627) is the classic default and mirrors LinkedIn's own link-preview format, reading as "editorial" to a desktop-heavy B2B audience; 1:1 square takes more mobile feed space and often stop-scrolls better there.
- **Video**: keep to roughly 15–30 seconds for feed placements, include captions (a large share of viewing happens sound-off in a professional context), upload at 720p or higher.
- **Carousel**: 2–10 cards, roughly a 45-character practical limit per card headline — the headline constraint is the most common reason a carousel's design looks fine but the copy fails in review; write card headlines short from the start rather than trying to trim later.
- **Document ads**: PDF/DOC/PPT uploads that let members preview and download without leaving LinkedIn — a strong-performing lead-gen format for whitepapers/case studies specifically because of the in-platform preview.
- **Thought leader ads**: boost an individual employee's existing organic post (requires their permission) rather than a company-page asset — inherits that post's specs and, often, its existing engagement/credibility.
- **Cost context**: LinkedIn CPCs and CPMs run structurally higher than consumer platforms — this reflects the value of the professional targeting data (job title, seniority, company size, industry) available here, not necessarily inefficiency; judge LinkedIn paid performance against lead *quality*, not against Meta/TikTok cost benchmarks directly.

## Practical Notes

- Front-load intro text — most of it gets cut behind a "see more" fold well before the stated character maximum, especially on mobile.
- Treat the first page of any document ad as a standalone creative — LinkedIn generates the ad's thumbnail from it, so a weak first page undersells strong content behind it.


---


## FILE: references/platforms/meta-ads-manager.md

# Meta Ads Manager — Setup & Account Mechanics

*Shared mechanics for Facebook, Instagram, and Threads — all three run through one Meta Ads Manager account. For platform-specific organic tactics and creative specs, see `instagram.md`, `facebook.md`, and `threads.md`. Specs and policy detail below are last-verified as of mid-2026 and this is an actively-tightening area — confirm against Meta's current Ads Manager and Business Help Center before finalizing anything production-critical (see SKILL.md Section 6).*

## 1. Campaign Objectives (ODAX)

Meta consolidated its objective list to six under the Outcome-Driven Ad Experiences (ODAX) framework, the exclusive campaign-creation path since 2023 — if older material references "Conversions," "Catalog Sales," "Brand Awareness," or "Video Views" as separate top-level objectives, that's the retired pre-ODAX taxonomy.

- **Awareness** — reach, ad recall, or video views. Best for cold audiences or a pixel with too little conversion history to optimize toward yet.
- **Traffic** — link clicks or landing page views.
- **Engagement** — post interactions, messaging conversations (click-to-Messenger/WhatsApp), or video views.
- **Leads** — Instant Form submissions, website leads, or calls.
- **App Promotion** — installs and in-app events.
- **Sales** — purchases/conversions; unlocks catalog-based dynamic ads (this absorbed the old standalone "Catalog Sales" objective — the capability moved a level down, it didn't disappear).

The objective is set once at the campaign level and can't change after launch, and it gates which ad-set features are even available (Instant Forms only appear under Leads) — getting it right up front matters more than it looks.

## 2. Budget Structure: CBO vs. ABO

- **Campaign Budget Optimization (CBO)** — officially rebranded "Advantage+ campaign budget" in the interface, though "CBO" remains the common shorthand industry-wide. One budget at the campaign level; Meta shifts spend across ad sets in real time toward whatever's converting most efficiently. The default recommendation for most accounts in 2026.
- **Ad Set Budget Optimization (ABO)** — a fixed, manually-set budget per ad set (industry shorthand, not a distinct named Meta product). Narrower role now: controlled tests needing guaranteed equal spend per variant so a result isn't confounded by the algorithm favoring one ad set early, or protecting a segment (e.g. retargeting) that CBO might under-fund relative to a larger prospecting pool.
- **Practical default**: test in ABO with equal spend to find a winner, scale in CBO once there's a confirmed one.

## 3. Audience Building

- **Advantage+ Audience**: broad, AI-driven targeting — Meta finds buyers from creative performance and conversion signal rather than manual interest/demo selection. The increasingly standard starting point (see `ad-planning-and-paid-media.md` Section 3).
- **Custom Audiences**: built from owned signal — website visitors (Pixel/Conversions API), an uploaded customer list, content engagement, or app activity. The highest-signal input available, and the required seed for Lookalikes.
- **Lookalike Audiences**: modeled from a Custom Audience seed at a chosen similarity percentage (tighter = closer match/smaller reach; looser = broader/less precise). Quality depends entirely on the seed — a high-LTV-customer seed outperforms an "everyone who ever visited" seed by a wide margin.
- **Meta has been shifting emphasis toward Advantage+ Audience and away from manually-built interest targeting and Lookalikes** over the past couple of years — treat granular manual audience-building as increasingly a testing/diagnostic tool rather than the default production approach. Confirm current tool availability before assuming an older workflow still applies exactly as it used to.
- **Controls vs. suggestions**: location, language, minimum age, exclusions, and any Special Ad Category restriction (Section 5) are hard guardrails Meta won't violate; detailed-targeting/Custom/Lookalike inputs increasingly function as soft signals the algorithm weighs rather than strict filters. Don't assume a targeting selection is a hard exclusion without verifying current behavior.

## 4. Conversion Tracking

- **Meta Pixel**: client-side website tracking firing standard events (Purchase, Lead, AddToCart, etc.) that power both optimization and Custom Audience building.
- **Conversions API (CAPI)**: server-side event tracking sent directly from the business's own server, bypassing browser-level loss from ad blockers, iOS App Tracking Transparency, and cookie restrictions. Pairing Pixel + CAPI (deduplicated) is the current standard, not an either/or — Pixel alone misses a growing share of events to blocking; CAPI alone misses some browser-side context.
- **Domain verification and event prioritization**: required in Business Manager for iOS-driven and aggregated measurement, including a prioritized, limited set of conversion events per domain — confirm the current event-count limit directly in Events Manager rather than assuming a remembered number, since it has changed before.

## 5. Ad Policy Essentials

Review and enforcement got meaningfully stricter and more automated through 2026 — treat this as real operational risk to plan around, not a formality.

- **Special Ad Categories (Housing, Employment, Credit — HEC)**: mandatory targeting restrictions (no zip-level exclusions, no age/gender/detailed-targeting narrowing), originating from anti-discrimination settlements. As of 2026, detection reportedly runs on ad **images and video**, not just text — classifiers flag real-estate imagery, hiring/office imagery, or credit-card/loan-calculator visuals and can auto-apply HEC restrictions even when the advertiser never manually selected the category. Don't assume vague language or skipping the category selector avoids classification — this is an active, tightening enforcement area; confirm current detection scope before relying on any workaround.
- **Restricted categories requiring special authorization**: financial services and credit (increasingly including buy-now-pay-later and crypto-adjacent products), healthcare and pharmaceuticals, alcohol, gambling, and social issues/elections/politics.
- **Prohibited outright, no authorization path**: illegal products, weapons (beyond narrow licensed exceptions), tobacco, discriminatory content.
- **Common disapproval triggers worth briefing creative teams on directly**: implied personal attributes ("you" language assuming a protected characteristic, health condition, or financial situation about the viewer), unverified or exaggerated health/outcome claims, before/after imagery implying a health or body transformation, non-functional or mismatched landing pages, and increasingly a lack of disclosure where AI-generated-content rules apply (see `image-and-creative-prompts.md` Section 9).
- **Review and appeals**: most ads clear automated review within roughly 24 hours; Meta can re-review an already-running ad at any time, and any creative edit sends it back through review (budget/schedule changes generally don't). If restricted, start in Ads Manager's Account Quality section to see exactly what triggered it before appealing — appeal with a specific, corrected explanation rather than a generic resubmission, and expect roughly a week for a response.

## 6. Testing & Scaling Tools

- **Meta Experiments**: the built-in, statistically-structured A/B testing tool (audience, creative, or placement splits with proper holdout methodology) — preferred over manually duplicating ad sets and eyeballing the difference, since it controls for overlap and timing that manual duplication doesn't.
- **Post-ID duplication**: when scaling a winning ad from a test into a new campaign, duplicate by post ID to preserve existing social proof (likes/comments/shares) instead of relaunching the same creative from zero engagement.

## 7. Advantage+ Shopping & Catalog Setup

E-commerce Advantage+ Shopping campaigns run off a product catalog configured in Commerce Manager (accurate pricing, availability, imagery) rather than one-off ad creative — feed quality is the primary lever, directly analogous to Google Merchant Center's role in Google Shopping/PMax (see `google-ads.md` Section 4). A stale or incomplete feed undermines the campaign regardless of how good the surrounding creative is.


---


## FILE: references/platforms/pinterest.md

# Pinterest Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against Pinterest's current ad specs page before finalizing production assets; Pinterest revises these frequently (see SKILL.md Section 6).*

## Why Pinterest Belongs in the Plan

Pinterest is a visual **search and discovery** engine with unusually high purchase intent for a "social" platform — users are there to plan and research a decision (often well before they've picked a specific brand), not primarily to socialize. For commerce, home, fashion, food, and planning-heavy categories, it frequently delivers lower-competition, higher-intent traffic than the more crowded social feeds, and often at a lower CPM. It's also one of the most commonly overlooked channels in a media plan — worth actively considering rather than defaulting out of.

## Terminology Note

Two older terms are now retired and worth knowing so a plan doesn't reference dead vocabulary:
- **"Promoted Pins"** is a legacy label — Pinterest now just calls paid placements **"ads."** The format choice (standard, video, carousel, etc.) is a separate decision from the fact that it's paid.
- **"Idea Pins"** was retired as an organic format in 2023 — Pinterest merged it into the general "Pins" format. The paid, storytelling-oriented version lives on as **"Idea ads."**

## Organic Content ("Pins")

- **Standard aspect ratio**: 2:3 vertical (commonly cited as 1000×1500px) is the safe default across the platform — taller ratios risk being cropped in feed.
- **Video**: autoplays without sound by default, so the message has to read visually without audio; 6–15 seconds is the commonly cited sweet spot for engagement even though the platform supports much longer runtimes.
- **Titles and descriptions matter for discovery, not just display**: titles get roughly the first 40 characters shown in feed (of a longer allowed limit), and descriptions — while not displayed prominently in feed — are read by Pinterest's algorithm to determine who sees the Pin. Treat description fields as genuine SEO copy, not an afterthought.

## Ad Formats

- **Standard (image) and Video Pins**: the baseline formats for traffic and awareness.
- **Idea ads**: storytelling/tutorial-style multi-page format, including a paid-partnership variant for creator collaborations.
- **Carousel**: multiple images/products in one ad unit for comparison or sequential storytelling.
- **Shopping/Catalog ads**: product-feed-driven, generated automatically from a product catalog rather than built as one-off creative — central to Pinterest's commerce positioning.
- **Collection ads**: a hero image/video plus secondary product images, well suited to brands with a rich catalog.
- **AR Try-On ads**: category-specific (beauty, home) augmented-reality try-before-you-buy format, a genuine differentiator versus most other ad platforms.

## Practical Notes

- Because this is a *search-and-discovery* surface rather than a pure social feed, apply keyword-research thinking (see `seo-and-sem.md` Section 3) to Pin titles and descriptions — treat it more like optimizing a product listing or a blog post for search than like writing a social caption.
- Vertical (2:3) creative built specifically for Pinterest consistently outperforms a resized asset built for another platform's aspect ratio — it's worth a dedicated crop/edit rather than reusing an Instagram or TikTok export as-is.


---


## FILE: references/platforms/threads.md

# Threads Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against Meta's current Ads Manager before finalizing production assets (see SKILL.md Section 6). Threads is one of the newest ad surfaces covered in this skill and is still evolving quickly.*

## Organic Content

- **Format**: Text-first — a genuinely conversational, unpolished tone consistently outperforms a polished, brand-speak post here, similar to X but with its own distinct culture and audience.
- **Cadence**: Rewards real-time, reactive posting more than a pre-built content calendar — treat it closer to a live conversation than a scheduled channel.
- **Cross-posting**: Auto-cross-posted Instagram captions read as lazy on Threads — native, platform-specific copy performs meaningfully better than a copy-pasted caption.

## Ads

Threads now runs paid advertising — this rolled out to select advertisers in 2025 and reached full global availability to all users in **January 2026**, so treat "Threads doesn't have ads" as outdated information if it comes up. *For objectives, budget structure, audience-building, and ad policy, see `platforms/meta-ads-manager.md` — all shared with Facebook and Instagram.*

- **Runs through Meta Ads Manager**, using the same underlying AI-powered ad system as Facebook and Instagram — no separate Threads-specific ad account or profile is required to run ads there.
- **Formats**: image, video, carousel, Advantage+ catalog ads, and app-install ads.
- **Threads is included in Meta Advantage+ placements by default** (see `ad-planning-and-paid-media.md` Section 3) — advertisers running Advantage+ campaigns across Meta's apps are likely already delivering on Threads unless they've manually opted the placement out.
- **Creative specs**: 4:5 aspect ratio is the primary supported ratio; primary text in the roughly 80–160 character range is the current recommendation.
- **CPMs have generally run below equivalent Instagram placements** during this early-adoption window — typical of a newly-monetized surface with more inventory than competing demand; expect that gap to narrow as more advertisers adopt the placement over time.

## Practical Notes

- Because Threads sits inside the same Ads Manager and Advantage+ system as Facebook/Instagram, the fastest way to start testing it is simply confirming the placement isn't manually excluded from an existing Advantage+ campaign, rather than building a dedicated Threads-only campaign from scratch.
- Given how recently ads launched here, verify current formats and specs directly in Ads Manager before finalizing creative — this file will go stale on Threads specifics faster than on more mature platforms.


---


## FILE: references/platforms/tiktok.md

# TikTok Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against TikTok's current Ads Manager before finalizing production assets (see SKILL.md Section 6). TikTok updates specs and formats especially frequently.*

## Organic Content

- **Hook rate**: The first 1–3 seconds are what determine whether the video gets watched at all — a strong opening beats a strong ending for reach, because a weak opening means most of the audience never sees the ending.
- **Native feel**: Vertical, handheld, authentic — content that reads as "produced by a brand" rather than "made by a person" consistently underperforms native-feeling content, even from the same account.
- **Trend participation**: Jump on trending sounds/formats within roughly 24–48 hours of them trending — trend relevance decays fast, and a late, technically-correct trend post reads as out of touch rather than current.
- **CTA**: Both verbal (said in the video) and on-screen text, with a clear end-frame — TikTok audiences respond to direct, spoken calls to action more than a purely visual/text-only CTA.
- **Posting frequency**: 1–3 posts/day supports faster growth for accounts building an audience; for conversion-focused accounts, quality and relevance to the specific offer matter more than raw frequency.

## Ad Formats & Specs

- **Primary format — In-Feed ads**: 9:16 vertical is strongly preferred (horizontal underperforms significantly on this platform); TikTok now supports much longer in-feed video (up to several minutes) but the 9–15 second range still wins on completion rate and engagement for most direct-response use cases — longer runtime is an option, not a mandate.
- **Spark Ads**: boosts an *existing organic post* (the creator's or the brand's own) rather than uploading separate ad creative — these carry an authorization window (commonly 7 or 30 days) after which the ad stops delivering unless renewed. Often outperforms a from-scratch ad upload because it inherits the organic post's existing engagement and native feel.
- **TopView**: premium, full-screen placement shown immediately on app open — high-impact awareness format, priced and bought differently from standard in-feed auction inventory.
- **Safe zones**: keep critical text/logo away from the top and bottom edges of the frame, where TikTok's own UI (captions, engagement buttons, username) overlays the video.
- **Sound-on**: the large majority of TikTok viewing happens with sound on (unlike Instagram/Facebook feed) — a silent-first edit is a real competitive disadvantage on this platform specifically.

## Commerce

- **TikTok Shop**: native in-app shopping with product tags, live shopping, and affiliate/creator commission structures — a materially different motion from running ads to an external site, with its own content style (unpolished, demo-heavy, creator-led) that tends to outperform traditional ad creative for conversion inside the app.

## Practical Notes

- Verify current in-feed duration limits and file-size caps directly in Ads Manager before finalizing an edit — this platform's technical specs move faster than most others covered in this skill.
- Brief creators for a native, unscripted feel rather than handing over brand-produced footage to repurpose — the platform's own audience can tell the difference, and it affects both organic reach and paid performance.


---


## FILE: references/platforms/x-twitter.md

# X (Twitter) Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against X's current Ads Manager before finalizing production assets (see SKILL.md Section 6).*

## Organic Content

- **Tweet threads**: 8–12 posts, a strong opening line (it has to work as a standalone hook since it's what appears before anyone expands the thread), visual breaks between dense sections, and concrete, actionable takeaways rather than a purely narrative structure.
- **Media mix**: X is genuinely more copy-first than most other major platforms — plain, well-written text posts routinely outperform image or video posts here, unlike almost anywhere else covered in this skill. Don't force visual creative onto every post out of habit carried over from other platforms.
- **Replies over likes**: the platform's ranking weighs genuine conversation (replies) far more heavily than likes — content engineered to start a real back-and-forth consistently outreaches content engineered only to be liked or agreed with.
- **Hashtags are largely obsolete for reach**: the platform's content understanding now runs on semantic/contextual analysis rather than keyword/hashtag matching — use zero or at most one genuinely relevant hashtag (a branded or event tag); stacking multiple hashtags provides no benefit and can actively suppress reach.
- **Links in the body of a post measurably reduce initial reach.** The common workaround is posting the core content as a standalone post, then adding the link as the first reply — this preserves most of the organic reach that a same-post link would cost.
- **Video is currently getting a meaningful algorithmic boost** as the platform competes directly with TikTok/Shorts for watch time — even simple, low-production talking-head video tends to outperform an equivalent text-only post right now.

## Ad Formats & Specs

- **Core self-serve formats**: Promoted Ads (image, video, carousel, and plain text), running through auction-based bidding targetable by keyword, conversation, interest, and follower lookalike.
- **Premium/managed formats**: Takeovers (top-of-timeline placements) and Amplify (pre-roll video alongside publisher content) — reservation-based, priced and bought differently from self-serve auction inventory, typically reserved for large awareness moments (launches, events) rather than always-on campaigns.
- **Video specs**: broadly 16:9, 1:1, or 9:16 depending on placement; keep to roughly 15–30 seconds for most feed placements even where longer runtime is technically supported.
- **The "Follower" objective (growing followers directly via ads) has been deprecated** — don't build a campaign plan assuming that objective still exists; reach/engagement/conversion objectives are the current toolkit.

## Practical Notes

- Because copy-first content genuinely wins here, invest proportionally more in the actual writing (the hook line, the thread structure) relative to production value compared to a visual-first platform like Instagram or TikTok.
- Treat X as a real-time, conversational surface rather than a scheduled broadcast channel — reactive, timely posting tends to outperform content that reads as pre-planned days in advance.


---


## FILE: references/platforms/youtube.md

# YouTube Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against YouTube's current Ads guidance before finalizing production assets (see SKILL.md Section 6).*

## Organic Content

- **Thumbnails**: High-contrast faces, bold short text (3–4 words max — anything longer becomes unreadable at thumbnail size), a genuine curiosity gap. The thumbnail and title work as a pair, not independently — a strong thumbnail with a mismatched or vague title still underperforms.
- **Titles**: Front-load the keyword/topic, use numbers and brackets where genuinely relevant (e.g. a year or a format cue), and lead with the emotional or curiosity hook rather than burying it at the end where it may get cut off.
- **Retention**: Pattern interrupts roughly every 30 seconds (a new visual, a re-frame, a callback), a clear storytelling arc rather than a flat information dump, and open loops/cliffhangers that carry the viewer to the next section. Average view duration and audience retention curve are the dominant signals YouTube's own recommendation system weighs — a video that's technically informative but loses retention early will be suppressed regardless of information quality.
- **SEO within YouTube**: description with front-loaded keywords and timestamps, relevant tags, end screens and cards linking to related content, and organizing content into playlists — all of this feeds both YouTube's own search/recommendation system and its visibility in general web search.

## Shorts

- Distinct discovery surface from long-form, competing directly with TikTok/Reels-style short vertical video — hook-first, 9:16, same short-form disciplines as `platforms/tiktok.md` apply, but cross-promotion into the channel's long-form catalog (via comments, end-screens, or explicit call-outs) is a genuine advantage unique to YouTube that a standalone TikTok/Reels account doesn't have.

## Ad Formats & Specs

- **In-stream skippable/non-skippable, bumper ads, and in-feed (discovery) ads** are the core formats — skippable in-stream needs to earn attention in the first 5 seconds before the skip option appears, which functions similarly to the "hook immediately" rule across every other short-form format in this skill.
- **YouTube inventory is a core placement inside Google Performance Max** (see `ad-planning-and-paid-media.md` Section 3) rather than only bought as a standalone YouTube campaign — many advertisers now reach YouTube inventory through PMax's cross-inventory automation rather than a dedicated YouTube-only buy.

## Practical Notes

- Always add captions — a large share of viewing happens sound-off or with accessibility needs, and captions also feed YouTube's content-understanding/search system.
- A strong channel trailer and consistent upload cadence still matter for subscriber conversion even though individual-video discovery increasingly happens outside the subscription feed (via Shorts and recommendation).


---
