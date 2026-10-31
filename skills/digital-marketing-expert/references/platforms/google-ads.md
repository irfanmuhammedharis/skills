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
