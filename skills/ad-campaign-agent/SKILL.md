---
name: ad-campaign-agent
description: >
  AI-driven agent for creating, configuring, and launching advertising campaigns on Meta (Facebook/Instagram) and Google Ads.
  Use this skill whenever a user wants to build, plan, or automate ad campaigns — even if they phrase it as "create ads", "set up a campaign", "run Facebook ads",
  "advertise on Google", "generate ad copy", "build a Meta campaign", "set up Google Search ads", or anything about paid social/search advertising.
  Also trigger for requests about ad targeting, bidding strategies, campaign structure, ad creative specs, UTM tagging, pixel setup, A/B ad testing,
  or integrating with the Meta Marketing API or Google Ads API. This skill covers the full pipeline: input collection → LLM copy generation →
  API-ready campaign configuration → code snippets for execution.
---

# Ad Campaign Agent

An AI agent that automates ad campaign creation across Meta (Facebook/Instagram) and Google Ads. It handles input collection, generates ad copy with LLM prompts, produces API-ready configurations, and outputs working code snippets.

## When to read reference files

| Need | File |
|------|------|
| Meta API endpoints, auth, SDK details | `references/meta-api.md` |
| Google Ads API endpoints, auth, SDK details | `references/google-api.md` |
| Ad format specs (dimensions, file sizes) | `references/ad-formats.md` |
| LLM prompt templates for copy generation | `references/prompt-templates.md` |

Read reference files on demand — only load the ones relevant to the current request.

---

## Step 1 — Collect Inputs

Gather these before generating anything. If any are missing, ask. Use sensible defaults where noted.

### Required
- **Business goal** — traffic / conversions / leads / app installs / brand awareness / sales
- **Platform(s)** — Meta (FB/IG), Google Ads, or both
- **Budget** — daily or total spend (e.g. ₹5,000/day or $500 total)
- **Target audience** — demographics (age, gender, location), interests, keywords (Google), or upload type (custom audience, lookalike)
- **Product/service description** — what is being advertised; key benefits; unique value prop
- **Landing page URL(s)** — where clicks go; also needed for UTM tagging
- **Creative assets** — images/videos available (dimensions known?), or copy-only request

### Optional (use defaults if absent)
- Ad format preference (default: responsive/auto-placement)
- Campaign schedule (default: no end date, start immediately)
- Bid strategy (default: platform-recommended for the goal)
- Tracking: Pixel ID (Meta), Google tag/conversion ID, UTM convention
- Competitor or style reference for tone
- Compliance constraints (restricted categories, required disclaimers)

### Input validation checklist
- [ ] Landing page URL is provided and reachable
- [ ] At least one creative asset or product description is available
- [ ] Budget is within a reasonable range for the goal
- [ ] Geo-targeting is specified (at minimum, country)
- [ ] Ad account ID is available (for API calls)

---

## Step 2 — Select Ad Formats

Use the platform + goal to recommend the right format. Quick reference:

| Goal | Meta Format | Google Format |
|------|-------------|---------------|
| Traffic / clicks | Single Image or Carousel | Responsive Search Ad |
| Conversions | Single Image + retargeting | Responsive Search + RSLA |
| App installs | App Install Objective | App Campaign |
| Brand awareness | Video / Reach campaign | Display (Responsive Display Ad) |
| E-commerce / sales | Carousel or Collection | Performance Max |
| Lead generation | Lead Ads (native form) | Lead Form Extensions |
| Stories / vertical | Instagram Stories (9:16) | N/A (use Discovery/Demand Gen) |

For format specs (dimensions, file limits, character counts), read `references/ad-formats.md`.

---

## Step 3 — Generate Ad Copy

Use the prompt templates in `references/prompt-templates.md`. Core structure:

1. Fill the prompt with: product info, audience description, goal, platform, character limits
2. Request 3–5 headline variations and 2–3 descriptions per format
3. Post-process output into platform-specific fields:
   - **Meta**: `headline`, `body` (primary text), `description`, `call_to_action`
   - **Google RSA**: `headlines[]` (max 30 chars each, up to 15), `descriptions[]` (max 90 chars each, up to 4)
   - **Google Display**: `short_headline` (≤25 chars), `long_headline` (≤90 chars), `description` (≤90 chars)

Always generate at least 3 headline variants for A/B testing.

---

## Step 4 — Build Campaign Configuration

### Meta Campaign Hierarchy
```
Ad Account
└── Campaign (objective, budget type)
    └── Ad Set (audience, placement, bid, schedule)
        └── Ad (creative: image/video + copy)
```

### Google Ads Hierarchy
```
Customer Account
└── Campaign (channel type, bid strategy, budget)
    └── Ad Group (keywords or audience, CPC bid)
        └── Ad (text/image/responsive assets)
```

Produce a structured config block for each level. Example output format:

```yaml
campaign:
  name: "SpringSale_Traffic_2026"
  platform: meta
  objective: LINK_CLICKS
  status: PAUSED          # always start paused for review
  daily_budget: 500       # in account currency (smallest unit: paise/cents)
  start_time: "2026-07-01T00:00:00+0530"

ad_set:
  name: "SpringSale_Women25-44_Mumbai"
  optimization_goal: LINK_CLICKS
  billing_event: IMPRESSIONS
  targeting:
    age_min: 25
    age_max: 44
    genders: [2]          # 1=male, 2=female
    geo_locations:
      cities: [{ key: "2295424", name: "Mumbai" }]
    interests: [{ id: "6003107902433", name: "Online shopping" }]
  placements: auto

ad:
  name: "SpringSale_ImageAd_V1"
  creative:
    image: "1080x1080_product.jpg"
    headline: "Grab the Deal Before It's Gone"
    body: "Shop our Spring collection — up to 40% off. Free delivery on orders above ₹999."
    call_to_action: SHOP_NOW
    link: "https://example.com/spring?utm_source=facebook&utm_medium=paid&utm_campaign=springsale"
```

---

## Step 5 — Output Code Snippets

Always output working Python code for both platforms. Read the relevant reference file for exact API parameters:
- Meta snippets → `references/meta-api.md`
- Google snippets → `references/google-api.md`

The `scripts/` directory contains reusable base scripts:
- `scripts/create_meta_campaign.py` — full Meta campaign creation flow
- `scripts/create_google_campaign.py` — full Google Ads campaign creation flow

Run or adapt these for the user's specific campaign config.

---

## Step 6 — Tracking & UTM Tags

Always output a UTM template:

```
?utm_source={platform}&utm_medium={medium}&utm_campaign={campaign_name}&utm_content={ad_name}&utm_term={keyword_or_audience}
```

| Platform | utm_source | utm_medium |
|----------|-----------|------------|
| Meta (Facebook) | facebook | paid-social |
| Meta (Instagram) | instagram | paid-social |
| Google Search | google | cpc |
| Google Display | google | display |

For Meta: append UTM to the `link` field in the ad creative.
For Google: use ValueTrack parameters (`{keyword}`, `{matchtype}`) plus static UTMs in the Final URL.

---

## Step 7 — Compliance Check

Before finalizing any campaign, verify:

### Meta Policy Checks
- [ ] No prohibited content: weapons, drugs, tobacco, adult content, hate speech, misleading claims
- [ ] No discriminatory targeting by race, religion, health, sexual orientation
- [ ] Restricted categories (credit, housing, employment) require special ad category flag
- [ ] Images: no excessive text (keep text under ~20% of image area)
- [ ] Landing page matches ad offer; no bait-and-switch

### Google Policy Checks
- [ ] No prohibited content: counterfeit goods, dangerous products, dishonest practices
- [ ] Restricted: alcohol, gambling, healthcare — requires certification/targeting
- [ ] Editorial: no excessive caps, correct grammar, no generic CTAs ("Click Here" alone)
- [ ] Destination requirements: landing page must be functional and match ad content

### Privacy / GDPR
- [ ] Custom audience emails must be hashed (SHA-256) before upload
- [ ] Remarketing requires cookie consent from users
- [ ] Do not store raw PII; use encrypted storage for any user data
- [ ] Document legal basis for any data usage

---

## Error Handling Reference

| Error | Platform | Cause | Fix |
|-------|----------|-------|-----|
| HTTP 429 | Both | Rate limit exceeded | Exponential backoff; batch operations |
| `RESOURCE_TEMPORARILY_EXHAUSTED` | Google | Daily quota hit | Wait until quota resets; use batch mutate |
| `Invalid OAuth token` | Both | Token expired | Refresh token; re-authenticate |
| `AdCreative validation` | Meta | Image wrong size or > 30MB | Resize/compress; check specs in ad-formats.md |
| Ad disapproved | Both | Policy violation | Review compliance checklist; edit copy/creative |
| `CAMPAIGN_NOT_FOUND` | Google | Wrong customer ID | Verify customer_id in google-ads.yaml |

For rate limits: Meta allows 9,000 points/5 min (Standard Access). Google: ~15,000 ops/day (Basic token). Always implement retry with jitter.

---

## A/B Testing Setup

Create 2–4 ad variants per campaign by varying:
- Headlines (different value props)
- Images (product vs lifestyle vs offer-focused)
- CTAs (Shop Now vs Learn More vs Get Offer)
- Audiences (broad vs interest-based vs retargeting)

**Meta**: Use Campaign Budget Optimization (CBO) — Meta auto-allocates to best-performing ad set.
**Google**: Use Ad Rotation: "Optimize" for machine-led, or "Do not optimize" for manual A/B.

Track per-variant: CTR, CVR, CPA, ROAS. Declare a winner after statistical significance (minimum 100 conversions per variant or 95% confidence).

---

## Output Summary Checklist

When handing off a campaign configuration, always include:
- [ ] Campaign YAML config (all levels)
- [ ] Ad copy variations (3+ headlines, 2+ descriptions)
- [ ] Creative spec list (dimensions, formats, max file sizes)
- [ ] UTM-tagged final URLs
- [ ] Python code snippets (campaign + ad set + ad creation)
- [ ] Compliance check results
- [ ] Recommended bid strategy and why
- [ ] A/B test plan (variants defined)
- [ ] Monitoring KPIs (CTR target, CPA goal, ROAS floor)
