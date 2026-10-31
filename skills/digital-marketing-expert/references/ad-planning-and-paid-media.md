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
