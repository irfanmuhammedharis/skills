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
