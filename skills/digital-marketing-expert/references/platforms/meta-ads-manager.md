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
