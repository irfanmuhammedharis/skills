# ad-campaign-agent — Reference Bundle

This file bundles several reference documents into one, separated by clear headers, so they fit ChatGPT's knowledge file-count limit per Custom GPT / Project.

---



## FILE: references/ad-formats.md

# Ad Format Specifications

## Meta (Facebook / Instagram) Ad Formats

### Single Image Ad
| Spec | Requirement |
|------|-------------|
| Recommended dimensions | 1080×1080 px (1:1) — Feed; 1080×1920 px (9:16) — Stories |
| Minimum dimensions | 600×315 px |
| Aspect ratio | 1:1 (square) or 1.91:1 (landscape) or 4:5 (portrait) |
| File types | JPG, PNG |
| Max file size | 30 MB |
| Max image text | ~20% of image (keep text minimal; excessive text reduces delivery) |
| Headline | ≤ 40 characters (best practice), max 255 |
| Primary text | ≤ 125 characters visible above "See More"; max 500 |
| Description | ≤ 30 characters |
| Link description | ≤ 30 characters |

**Best placements:** Facebook Feed, Instagram Feed, Facebook Right Column, Marketplace, Audience Network

---

### Carousel Ad
| Spec | Requirement |
|------|-------------|
| Cards | 2–10 cards per carousel |
| Image per card | 1080×1080 px recommended (1:1); or 1200×628 (landscape) |
| Video per card | 1080×1080 px, max 240 min, 4GB |
| Headline per card | ≤ 40 characters |
| Description per card | ≤ 20 characters |
| CTA | One CTA per carousel (shared across cards) |
| Primary text | Same as Single Image |

**Best placements:** Facebook Feed, Instagram Feed

---

### Stories / Reels Ad (Vertical)
| Spec | Requirement |
|------|-------------|
| Dimensions | 1080×1920 px (9:16 vertical) |
| Minimum | 500×889 px |
| File type | JPG/PNG (image); MP4/MOV (video) |
| Max image file size | 30 MB |
| Max video file size | 4 GB |
| Video duration (Stories) | 1–15 seconds |
| Video duration (Reels) | 1–90 seconds |
| Safe zone | Keep text/logos in center 1080×1420 px (avoid top 250px and bottom 250px) |
| Primary text | Not shown in Stories/Reels; embed text in creative |

**Best placements:** Instagram Stories, Instagram Reels, Facebook Stories

---

### Video Ad (Feed)
| Spec | Requirement |
|------|-------------|
| Recommended ratio | 4:5 (portrait) — takes more feed space; or 1:1 (square) |
| Resolution | 1080×1350 px (4:5) or 1080×1080 px (1:1) |
| File type | MP4, MOV, GIF |
| Max file size | 4 GB |
| Duration | 1 second – 241 minutes (feed); keep to ≤15s for best engagement |
| Thumbnail | Auto-generated; can supply custom 1080×1080 JPG/PNG |
| Primary text | ≤ 125 characters |
| Captions | Strongly recommended (85% of videos watched without sound) |

---

### Lead Ad
- Uses all the same image/video specs as Single Image or Video ad
- Includes an Instant Form attached to the ad creative
- Form fields: email, phone, name (or custom questions)
- No landing page required (form opens natively in Facebook/Instagram)

---

### App Install Ad
- Uses same creative specs as Single Image or Video
- Campaign objective must be `APP_INSTALLS`
- Deep link to App Store / Play Store required
- Install tracking: Facebook SDK or MMP (AppsFlyer, Adjust, Branch)

---

## Google Ads Formats

### Responsive Search Ad (RSA)
| Spec | Requirement |
|------|-------------|
| Headlines | Up to 15; ≤ 30 characters each; minimum 3 required |
| Descriptions | Up to 4; ≤ 90 characters each; minimum 2 required |
| Final URL | Valid URL; must match display domain |
| Display path | Up to 2 path fields; ≤ 15 characters each |
| Business name | ≤ 25 characters |

Google dynamically assembles up to 3 headlines + 2 descriptions per impression.

---

### Expanded Text Ad (Legacy — no longer creatable, but still running)
| Spec | Requirement |
|------|-------------|
| Headline 1/2/3 | ≤ 30 characters each |
| Description 1/2 | ≤ 90 characters each |
| Path 1/2 | ≤ 15 characters each |

---

### Responsive Display Ad (RDA)
| Spec | Requirement |
|------|-------------|
| Short headline | ≤ 30 characters; up to 5 required |
| Long headline | ≤ 90 characters; 1 required |
| Description | ≤ 90 characters; up to 5 required |
| Business name | ≤ 25 characters |
| Landscape image | 1200×628 px (1.91:1); min 600×314; ≤ 5 MB; JPG or PNG |
| Square image | 1200×1200 px (1:1); min 300×300; ≤ 5 MB; JPG or PNG |
| Portrait image | 900×1600 px (9:16); optional |
| Logo (square) | 1200×1200 px; min 128×128; ≤ 5 MB |
| Logo (landscape) | 1200×300 px; optional |
| Video | Optional; YouTube URL |

---

### Performance Max Assets
PMax uses a single **asset group** with all asset types pooled:
- Same image + logo specs as RDA above
- Headlines: up to 5, ≤30 chars
- Long headlines: up to 5, ≤90 chars
- Descriptions: up to 5, ≤90 chars
- Videos: YouTube links (optional; Google auto-generates if absent)
- Final URL, business name

---

### App Campaign
- Assets: text, images, videos, HTML5 (optional)
- Google automatically mixes and matches across Search, Play Store, YouTube, Display
- Required: app package name, at least one text asset
- Image specs: 320×50, 320×480, 300×250, 336×280 (banner sizes) + 1200×628 for native

---

### Shopping / Performance Max (Retail)
- No ad creative required; pulled from Merchant Center product feed
- Required: Merchant Center account linked to Google Ads
- Product image specs (for feed): 100×100 px minimum; 800×800 recommended; JPG/PNG/GIF

---

## Character Limit Quick Reference

| Platform | Element | Limit |
|----------|---------|-------|
| Meta | Primary text (visible) | 125 chars |
| Meta | Headline | 40 chars (best practice) |
| Meta | Description / Link desc | 30 chars |
| Meta | Stories text overlay | Embed in image; no limit field |
| Google RSA | Headline | 30 chars |
| Google RSA | Description | 90 chars |
| Google RDA | Short headline | 30 chars |
| Google RDA | Long headline | 90 chars |
| Google RDA | Description | 90 chars |
| Google | Display path | 15 chars per field |
| Google | Business name | 25 chars |

---

## File Format Summary

| Asset Type | Meta | Google |
|-----------|------|--------|
| Image | JPG, PNG | JPG, PNG |
| Video | MP4, MOV, GIF | MP4, MOV, AVI, WMV, MPEG (via YouTube for video ads) |
| Max image size | 30 MB | 5 MB (RDA) |
| Max video size | 4 GB | Per YouTube limits |

---

## Creative Best Practices

### Meta
1. Use square (1:1) or portrait (4:5) for mobile — takes more vertical space
2. Keep image text minimal — heavy text reduces reach
3. First 3 seconds of video must hook attention (feed auto-plays, muted)
4. Add captions to all videos (most watch without sound)
5. Test static vs video: video usually beats static for awareness; static wins for conversion
6. Carousel works best for e-commerce (one product per card) or storytelling

### Google
1. Use at least 5 distinct headlines (not just variations of the same phrase)
2. Include keyword in at least one headline (improves Ad Strength)
3. Pin headlines/descriptions only when legally required — reduces machine learning efficiency
4. Use all 4 descriptions when possible
5. For RSA: Ad Strength "Excellent" = 15 headlines + 4 descriptions with high variety
6. RDA: always provide both landscape (1200×628) and square (1200×1200) images


---


## FILE: references/google-api.md

# Google Ads API Reference

## Authentication

### Prerequisites
1. Google Cloud project with **Google Ads API** enabled
2. OAuth 2.0 credentials (Desktop App or Service Account)
3. **Developer Token** from Google Ads → Tools → API Center (apply for access)
4. Manager Account (MCC) if managing multiple client accounts

### google-ads.yaml Config
```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_MCC_CUSTOMER_ID"   # optional, for MCC
```

### OAuth2 Refresh Token (one-time setup)
```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/adwords"]
)
creds = flow.run_local_server(port=0)
print("Refresh token:", creds.refresh_token)
```

### Client Initialization
```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage("google-ads.yaml")
# Or from dict:
client = GoogleAdsClient.load_from_dict({
    "developer_token": DEVELOPER_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
})
```

---

## Rate Limits & Quotas

| Access Level | Ops/day | QPS | Notes |
|---|---|---|---|
| Basic | 15,000 | Limited | Default for new developers |
| Standard | 250,000 | Higher | After application review |
| Basic (Reporting) | Unlimited | — | GAQL queries |

**Batch operations**: Pack up to 10,000 operations in a single `mutate_campaigns()` call. Far more efficient than 1 call per entity.

**Handling RESOURCE_TEMPORARILY_EXHAUSTED:**
```python
from google.api_core.exceptions import ResourceExhausted
import time, random

def google_api_call_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except ResourceExhausted:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Quota hit. Waiting {wait:.1f}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

---

## Campaign Types

| Type | API Enum | Use Case |
|------|----------|----------|
| Search | `SEARCH` | Text ads on Google Search |
| Display | `DISPLAY` | Image/responsive ads on GDN |
| Shopping | `SHOPPING` | Product listing ads (requires Merchant Center) |
| App | `MULTI_CHANNEL` | App installs across all Google properties |
| Performance Max | `PERFORMANCE_MAX` | Automated across all Google channels |
| Demand Gen | `DEMAND_GEN` | YouTube, Discover, Gmail placements |
| Video | `VIDEO` | (Use PMax or Demand Gen instead via API) |

---

## Campaign Creation

```python
def create_google_campaign(client, customer_id, name, channel_type="SEARCH",
                            daily_budget_micros=500000000):  # 500000000 = ₹500
    campaign_service = client.get_service("CampaignService")
    budget_service = client.get_service("CampaignBudgetService")

    # Step 1: Create budget
    budget_op = client.get_type("CampaignBudgetOperation")
    budget = budget_op.create
    budget.name = f"Budget for {name}"
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.amount_micros = daily_budget_micros  # 1 unit = 1,000,000 micros

    budget_response = budget_service.mutate_campaign_budgets(
        customer_id=customer_id,
        operations=[budget_op]
    )
    budget_resource = budget_response.results[0].resource_name

    # Step 2: Create campaign
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.create
    campaign.name = name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum[channel_type]
    )
    campaign.campaign_budget = budget_resource

    # Bid strategy (manual CPC example)
    campaign.manual_cpc.enhanced_cpc_enabled = False

    # Network settings (for Search)
    if channel_type == "SEARCH":
        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = True
        campaign.network_settings.target_content_network = False

    response = campaign_service.mutate_campaigns(
        customer_id=customer_id,
        operations=[campaign_op]
    )
    campaign_resource = response.results[0].resource_name
    print(f"Campaign created: {campaign_resource}")
    return campaign_resource
```

---

## Ad Group Creation

```python
def create_google_ad_group(client, customer_id, campaign_resource, name,
                            cpc_bid_micros=1000000):  # 1000000 = ₹1
    ad_group_service = client.get_service("AdGroupService")

    ad_group_op = client.get_type("AdGroupOperation")
    ad_group = ad_group_op.create
    ad_group.name = name
    ad_group.campaign = campaign_resource
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = cpc_bid_micros

    response = ad_group_service.mutate_ad_groups(
        customer_id=customer_id,
        operations=[ad_group_op]
    )
    return response.results[0].resource_name
```

---

## Keyword Creation

```python
def add_keywords(client, customer_id, ad_group_resource, keywords):
    """
    keywords: list of dicts like {"text": "buy running shoes", "match_type": "PHRASE"}
    match_type options: EXACT, PHRASE, BROAD
    """
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    operations = []

    for kw in keywords:
        op = client.get_type("AdGroupCriterionOperation")
        criterion = op.create
        criterion.ad_group = ad_group_resource
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = kw["text"]
        criterion.keyword.match_type = (
            client.enums.KeywordMatchTypeEnum[kw["match_type"]]
        )
        operations.append(op)

    response = ad_group_criterion_service.mutate_ad_group_criteria(
        customer_id=customer_id,
        operations=operations
    )
    return [r.resource_name for r in response.results]
```

---

## Responsive Search Ad Creation

```python
def create_responsive_search_ad(client, customer_id, ad_group_resource,
                                 headlines, descriptions, final_url):
    """
    headlines: list of up to 15 strings (≤30 chars each)
    descriptions: list of up to 4 strings (≤90 chars each)
    """
    ad_service = client.get_service("AdGroupAdService")

    ad_group_ad_op = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_op.create
    ad_group_ad.ad_group = ad_group_resource
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED

    # Build the RSA
    ad = ad_group_ad.ad
    ad.final_urls.append(final_url)
    ad.responsive_search_ad.path1 = "sale"
    ad.responsive_search_ad.path2 = "shop"

    for headline_text in headlines:
        headline = client.get_type("AdTextAsset")
        headline.text = headline_text
        ad.responsive_search_ad.headlines.append(headline)

    for desc_text in descriptions:
        description = client.get_type("AdTextAsset")
        description.text = desc_text
        ad.responsive_search_ad.descriptions.append(description)

    response = ad_service.mutate_ad_group_ads(
        customer_id=customer_id,
        operations=[ad_group_ad_op]
    )
    return response.results[0].resource_name
```

---

## Responsive Display Ad (for Display campaigns)

Key assets:
- `marketing_images`: 1200×628 (1.91:1) — required
- `square_marketing_images`: 1200×1200 (1:1) — required
- `headlines`: up to 5, ≤30 chars
- `long_headline`: 1, ≤90 chars
- `descriptions`: up to 5, ≤90 chars
- `business_name`: ≤25 chars

Upload assets first via `AssetService`, then reference asset resource names in `ResponsiveDisplayAdInfo`.

---

## Performance Max Campaign

Performance Max runs across Search, Display, YouTube, Discover, Gmail, Maps automatically.

```python
# PMax requires asset groups instead of ad groups
# Set advertising_channel_type = PERFORMANCE_MAX
# Then create asset groups via AssetGroupService

pmax_campaign_op = client.get_type("CampaignOperation")
pmax = pmax_campaign_op.create
pmax.name = "SpringSale_PMax"
pmax.advertising_channel_type = (
    client.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX
)
pmax.status = client.enums.CampaignStatusEnum.PAUSED
# PMax uses Target ROAS or Maximize Conversion Value
pmax.maximize_conversion_value.target_roas = 3.5  # 350% ROAS target
pmax.campaign_budget = budget_resource
```

---

## Bid Strategies Reference

| Strategy | API Setting | Best For |
|----------|------------|----------|
| Manual CPC | `manual_cpc` | Full control, new campaigns |
| Enhanced CPC | `manual_cpc.enhanced_cpc_enabled = True` | Semi-automated |
| Maximize Clicks | `maximize_clicks` | Traffic campaigns |
| Target CPA | `target_cpa.target_cpa_micros` | Conversion optimization |
| Target ROAS | `target_roas.target_roas` | E-commerce |
| Maximize Conversions | `maximize_conversions` | Get most conversions in budget |
| Maximize Conv. Value | `maximize_conversion_value` | Revenue optimization |

---

## Reporting (GAQL)

```python
def get_campaign_performance(client, customer_id, campaign_resource=None):
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_per_conversion
        FROM campaign
        WHERE segments.date DURING LAST_7_DAYS
          AND campaign.status != 'REMOVED'
    """
    if campaign_resource:
        query += f" AND campaign.resource_name = '{campaign_resource}'"

    response = ga_service.search_stream(customer_id=customer_id, query=query)
    for batch in response:
        for row in batch.results:
            print(f"""
Campaign: {row.campaign.name}
Impressions: {row.metrics.impressions}
Clicks: {row.metrics.clicks}
CTR: {row.metrics.ctr:.2%}
Avg CPC: ₹{row.metrics.average_cpc / 1_000_000:.2f}
Cost: ₹{row.metrics.cost_micros / 1_000_000:.2f}
Conversions: {row.metrics.conversions}
CPA: ₹{row.metrics.cost_per_conversion / 1_000_000:.2f}
            """)
```

---

## Install Dependencies

```bash
pip install google-ads
pip install google-auth-oauthlib
```

Google Ads Python library docs: https://developers.google.com/google-ads/api/docs/client-libs/python


---


## FILE: references/meta-api.md

# Meta Marketing API Reference

## Authentication

### OAuth 2.0 Flow
1. Create a Facebook App at developers.facebook.com
2. Add **Marketing API** product to the app
3. Required permissions: `ads_management`, `ads_read`, `business_management`
4. Exchange short-lived token for long-lived token (valid 60 days):

```python
import requests

def get_long_lived_token(app_id, app_secret, short_lived_token):
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token,
    }
    return requests.get(url, params=params).json()["access_token"]
```

For production: use a **System User** token (never expires) via Business Manager → System Users.

### Environment Setup
```python
import os
ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"]   # format: act_123456789
PAGE_ID = os.environ["META_PAGE_ID"]
API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
```

---

## Rate Limits

| Access Level | Points per 300s | Notes |
|---|---|---|
| Development | 60 | Default for new apps |
| Standard | 9,000 | After app review |
| Advanced | Higher (negotiated) | Large advertisers |

Each API call costs 1 point by default. Batch requests cost 1 point for the batch, not per sub-request.

**Handling 429:**
```python
import time, random

def api_call_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## Campaign Endpoints

### Create Campaign
```
POST https://graph.facebook.com/v18.0/act_{account_id}/campaigns
```

**Parameters:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✓ | Campaign name |
| `objective` | enum | ✓ | See objectives table below |
| `status` | enum | ✓ | `PAUSED` recommended for new campaigns |
| `special_ad_categories` | array | conditional | Required for credit/housing/employment/political |
| `daily_budget` | int | conditional | Cents/paise. Either this or lifetime_budget |
| `lifetime_budget` | int | conditional | Total budget in cents |
| `bid_strategy` | enum | optional | `LOWEST_COST_WITHOUT_CAP`, `COST_CAP`, `BID_CAP` |

**Campaign Objectives:**

| Objective | API Value | Use Case |
|-----------|-----------|----------|
| Traffic | `LINK_CLICKS` | Drive website visits |
| Conversions | `CONVERSIONS` | Purchase/signup optimization |
| App Installs | `APP_INSTALLS` | Mobile app promotion |
| Lead Generation | `LEAD_GENERATION` | Native lead form |
| Brand Awareness | `BRAND_AWARENESS` | Reach and frequency |
| Reach | `REACH` | Maximum audience coverage |
| Video Views | `VIDEO_VIEWS` | Video engagement |
| Messages | `MESSAGES` | WhatsApp/Messenger flow |

**Python Example:**
```python
import requests

def create_meta_campaign(name, objective, daily_budget_paise, access_token, account_id):
    url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns"
    payload = {
        "name": name,
        "objective": objective,
        "status": "PAUSED",
        "daily_budget": str(daily_budget_paise),  # e.g., 50000 = ₹500
        "access_token": access_token,
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()["id"]
```

---

## Ad Set Endpoints

### Create Ad Set
```
POST https://graph.facebook.com/v18.0/act_{account_id}/adsets
```

**Key Parameters:**

| Field | Type | Notes |
|-------|------|-------|
| `campaign_id` | string | Parent campaign ID |
| `name` | string | Ad set name |
| `optimization_goal` | enum | `LINK_CLICKS`, `CONVERSIONS`, `APP_INSTALLS`, `REACH`, `IMPRESSIONS` |
| `billing_event` | enum | `IMPRESSIONS`, `LINK_CLICKS` |
| `bid_amount` | int | Manual bid in cents (optional for auto-bid) |
| `daily_budget` | int | If campaign uses ad-set-level budget |
| `targeting` | object | See targeting spec below |
| `start_time` | datetime | ISO 8601 |
| `end_time` | datetime | ISO 8601 (optional) |
| `status` | enum | `PAUSED` or `ACTIVE` |

**Targeting Spec (JSON Object):**
```python
targeting = {
    "age_min": 25,
    "age_max": 44,
    "genders": [1],  # 1=male, 2=female, omit for all
    "geo_locations": {
        "countries": ["IN"],  # ISO 2-letter country codes
        # OR cities:
        # "cities": [{"key": "2295424", "name": "Mumbai", "radius": 10, "distance_unit": "kilometer"}]
    },
    "interests": [
        {"id": "6003107902433", "name": "Online shopping"}
    ],
    "behaviors": [
        {"id": "6071631541183", "name": "Online buyers"}
    ],
    "custom_audiences": [
        {"id": "12345678"}  # Custom audience ID from uploaded list
    ],
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed", "right_hand_column"],
    "instagram_positions": ["stream", "story", "reels"],
    "device_platforms": ["mobile"],  # or "desktop"
}
```

**Python Example:**
```python
def create_meta_adset(campaign_id, name, targeting, optimization_goal,
                      daily_budget_paise, access_token, account_id):
    url = f"https://graph.facebook.com/v18.0/{account_id}/adsets"
    payload = {
        "campaign_id": campaign_id,
        "name": name,
        "optimization_goal": optimization_goal,
        "billing_event": "IMPRESSIONS",
        "daily_budget": str(daily_budget_paise),
        "targeting": str(targeting).replace("'", '"'),  # JSON stringify
        "status": "PAUSED",
        "access_token": access_token,
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()["id"]
```

---

## Ad Creative & Ad Endpoints

### Upload Image
```
POST https://graph.facebook.com/v18.0/act_{account_id}/adimages
```
Returns `image_hash` — used in creative spec.

### Create Ad Creative
```
POST https://graph.facebook.com/v18.0/act_{account_id}/adcreatives
```

**Single Image Creative:**
```python
creative_spec = {
    "name": "Spring Sale Creative V1",
    "object_story_spec": {
        "page_id": PAGE_ID,
        "link_data": {
            "image_hash": "a1b2c3d4e5f6...",  # From image upload
            "link": "https://example.com/sale?utm_source=facebook&utm_medium=paid-social",
            "message": "Shop our Spring Sale — up to 40% off. Free delivery above ₹999.",
            "name": "Grab the Deal Before It's Gone",  # headline
            "description": "Limited time offer. Shop now.",
            "call_to_action": {
                "type": "SHOP_NOW",
                "value": {"link": "https://example.com/sale"}
            }
        }
    }
}
```

**Carousel Creative:**
```python
carousel_spec = {
    "name": "Spring Carousel V1",
    "object_story_spec": {
        "page_id": PAGE_ID,
        "link_data": {
            "link": "https://example.com",
            "child_attachments": [
                {
                    "link": "https://example.com/product-1",
                    "image_hash": "hash1",
                    "name": "Product 1 — ₹999",
                    "description": "Buy Now",
                    "call_to_action": {"type": "SHOP_NOW"}
                },
                {
                    "link": "https://example.com/product-2",
                    "image_hash": "hash2",
                    "name": "Product 2 — ₹1,499",
                    "description": "Buy Now",
                    "call_to_action": {"type": "SHOP_NOW"}
                }
            ],
            "multi_share_optimized": True,
        }
    }
}
```

### Create Ad
```
POST https://graph.facebook.com/v18.0/act_{account_id}/ads
```
```python
def create_meta_ad(adset_id, creative_id, name, access_token, account_id):
    url = f"https://graph.facebook.com/v18.0/{account_id}/ads"
    payload = {
        "name": name,
        "adset_id": adset_id,
        "creative": f'{{"creative_id": "{creative_id}"}}',
        "status": "PAUSED",
        "access_token": access_token,
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()["id"]
```

---

## Reporting — Insights API

```
GET https://graph.facebook.com/v18.0/act_{account_id}/insights
```

Key fields: `impressions`, `clicks`, `spend`, `ctr`, `cpc`, `cpm`, `actions` (includes conversions), `cost_per_action_type`

```python
def get_campaign_insights(campaign_id, access_token, date_preset="last_7d"):
    url = f"https://graph.facebook.com/v18.0/{campaign_id}/insights"
    params = {
        "fields": "impressions,clicks,spend,ctr,cpc,actions,cost_per_action_type",
        "date_preset": date_preset,
        "access_token": access_token,
    }
    return requests.get(url, params=params).json()
```

---

## Custom Audiences

### Upload Hashed Email List
```
POST https://graph.facebook.com/v18.0/act_{account_id}/customaudiences
```
Then: `POST /{audience_id}/users` with SHA-256 hashed emails (lowercase before hashing).

```python
import hashlib

def hash_email(email):
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()

hashed_emails = [hash_email(e) for e in email_list]
```

---

## Facebook Business SDK (Alternative)

Install: `pip install facebook-business`

```python
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

FacebookAdsApi.init(app_id, app_secret, ACCESS_TOKEN)
account = AdAccount(f"act_{ACCOUNT_ID}")

# Create campaign
campaign = account.create_campaign(fields=[], params={
    Campaign.Field.name: "Spring Sale Campaign",
    Campaign.Field.objective: Campaign.Objective.link_clicks,
    Campaign.Field.status: Campaign.Status.paused,
    Campaign.Field.daily_budget: 50000,  # in paise
})
print("Campaign ID:", campaign.get_id())
```


---


## FILE: references/prompt-templates.md

# Prompt Templates for Ad Copy Generation

These templates are designed to be filled with campaign-specific data and sent to an LLM (Claude, GPT-4, etc.) to generate ad copy. Fill every `[PLACEHOLDER]` before sending.

---

## Template 1 — Meta Feed Ad (Single Image)

```
You are an expert digital marketing copywriter specialising in Facebook and Instagram ads.

CAMPAIGN BRIEF:
- Product/Service: [PRODUCT_OR_SERVICE_NAME]
- Key benefit or offer: [PRIMARY_VALUE_PROP — e.g., "40% off Spring collection"]
- Target audience: [AUDIENCE_DESCRIPTION — e.g., "women aged 25–40 in Mumbai who enjoy fashion and online shopping"]
- Campaign goal: [GOAL — e.g., "drive clicks to the sale landing page"]
- Tone: [TONE — e.g., "upbeat and urgent" / "professional and trustworthy" / "friendly and conversational"]
- Brand voice: [BRAND_VOICE — optional, e.g., "Bold. Modern. Accessible."]

TASK:
Generate 5 headline variations and 3 primary text variations for a Facebook/Instagram single-image feed ad.

FORMAT RULES:
- Headlines: ≤ 40 characters each (shorter is better; aim for 25–35)
- Primary text: ≤ 125 characters for the visible portion (first line); can continue after a break
- Each primary text must begin with a strong hook
- Include ONE clear call-to-action phrase in each primary text (e.g., "Shop now", "Grab yours", "Learn more")
- Do NOT use emojis unless the brand tone is casual/playful
- Avoid superlatives like "best" or "world-class" without evidence

OUTPUT FORMAT (JSON):
{
  "headlines": [
    "Headline 1",
    "Headline 2",
    "Headline 3",
    "Headline 4",
    "Headline 5"
  ],
  "primary_texts": [
    "Primary text variation 1.",
    "Primary text variation 2.",
    "Primary text variation 3."
  ],
  "descriptions": [
    "Short description 1 (≤30 chars)",
    "Short description 2 (≤30 chars)"
  ]
}
```

---

## Template 2 — Google Responsive Search Ad (RSA)

```
You are an expert Google Ads copywriter.

CAMPAIGN BRIEF:
- Product/Service: [PRODUCT_OR_SERVICE_NAME]
- Primary keywords to include: [KEYWORDS — e.g., "buy running shoes", "running shoes online India"]
- Unique selling points: [USP_LIST — e.g., "Free shipping", "30-day returns", "Official store"]
- Target audience: [AUDIENCE_DESCRIPTION]
- Final URL: [LANDING_PAGE_URL]
- Campaign goal: [GOAL — e.g., "generate product page visits and purchases"]

TASK:
Generate 15 headline variations and 4 description variations for a Google Responsive Search Ad.

FORMAT RULES:
- Headlines: EXACTLY ≤ 30 characters each (count spaces and punctuation)
- Descriptions: EXACTLY ≤ 90 characters each
- Include at least 2 headlines that contain the primary keyword verbatim
- Include at least 1 headline with a strong CTA (e.g., "Shop Now", "Order Today")
- Include at least 1 headline with a number or offer (e.g., "Up to 40% Off")
- Descriptions must be complete sentences; no truncation
- No punctuation at the end of headlines
- No excessive capitalisation (only proper nouns and first word)

VERIFICATION: After generating, count the exact character length of each headline and flag any that exceed 30 characters.

OUTPUT FORMAT (JSON):
{
  "headlines": [
    {"text": "Headline 1", "char_count": 12},
    ...
  ],
  "descriptions": [
    {"text": "Description 1", "char_count": 85},
    ...
  ]
}
```

---

## Template 3 — Instagram Stories / Reels Ad

```
You are a creative advertising copywriter specialising in short-form vertical video and Instagram Stories ads.

CAMPAIGN BRIEF:
- Product/Service: [PRODUCT_OR_SERVICE_NAME]
- Key message: [KEY_MESSAGE — e.g., "Our app helps you track fitness goals in under 2 minutes a day"]
- Target audience: [AUDIENCE_DESCRIPTION — e.g., "fitness-conscious adults aged 18–35"]
- Campaign goal: [GOAL — e.g., "app installs"]
- Tone: [TONE — e.g., "energetic and motivational"]

TASK:
Generate 3 script variations for a 6–15 second Instagram Stories ad. Each variation should include:
1. A text overlay hook (appears in first 2 seconds)
2. A voiceover/on-screen text script (complete 6–15 sec)
3. A CTA overlay text (appears in last 2 seconds)

FORMAT RULES:
- Hook text overlay: ≤ 20 characters (must be immediately attention-grabbing)
- Script: written for spoken word; conversational; max 50 words
- CTA: ≤ 20 characters — e.g., "Swipe Up", "Download Now", "Shop the Sale"
- No jargon; direct and punchy
- Assume visuals will show the product/app in use

OUTPUT FORMAT (JSON):
{
  "variations": [
    {
      "hook_overlay": "...",
      "script": "...",
      "cta_overlay": "..."
    }
  ]
}
```

---

## Template 4 — App Install Ad (Meta or Google)

```
You are a mobile app marketing specialist.

CAMPAIGN BRIEF:
- App name: [APP_NAME]
- App category: [CATEGORY — e.g., "fitness tracker", "food delivery", "fintech"]
- Core value proposition: [CORE_VALUE — e.g., "track your budget automatically with AI"]
- Key features (pick top 3): [FEATURE_1], [FEATURE_2], [FEATURE_3]
- Target user: [TARGET_USER — e.g., "young professionals aged 22–35 who want to save money"]
- Platform: [META / GOOGLE / BOTH]
- Goal: App installs

TASK:
Generate 3 ad copy sets for an app install campaign. Each set includes headline, body copy, and CTA.

FORMAT RULES:
- Headlines: ≤ 40 characters (Meta) / ≤ 30 characters (Google)
- Body: ≤ 90 characters (keep punchy; lead with the benefit, not the feature)
- CTA: Use "Install Now", "Get the App", "Download Free", or "Try Free"
- Avoid listing features; instead lead with the outcome the user gets
- Personalise to the target user's pain point

OUTPUT FORMAT (JSON):
{
  "ad_sets": [
    {
      "headline": "...",
      "body": "...",
      "cta": "..."
    }
  ]
}
```

---

## Template 5 — E-commerce Carousel Ad (Meta)

```
You are an e-commerce advertising copywriter.

CAMPAIGN BRIEF:
- Brand name: [BRAND_NAME]
- Products to feature: [LIST_OF_PRODUCTS — e.g., "Running Shoes (₹2,499)", "Yoga Pants (₹1,299)", "Gym Bag (₹999)"]
- Overall offer: [OFFER — e.g., "Up to 40% off during the Spring Sale"]
- Target audience: [AUDIENCE]
- Goal: Online sales / conversions

TASK:
Write carousel ad copy for up to 5 cards. Card 1 should be an intro/offer card; remaining cards feature individual products.

FORMAT RULES:
- Card headline: ≤ 40 characters (shown under each carousel card)
- Card description: ≤ 20 characters (shown below headline)
- Intro primary text (shown once above carousel): ≤ 125 characters
- Each card should have a unique angle (price, feature, use case)
- CTA: SHOP_NOW for all cards

OUTPUT FORMAT (JSON):
{
  "primary_text": "...",
  "cards": [
    {
      "headline": "...",
      "description": "...",
      "product_link": "[PRODUCT_URL]"
    }
  ]
}
```

---

## Template 6 — Retargeting Ad (Warm Audience)

```
You are a performance marketing specialist.

CAMPAIGN BRIEF:
- Product/Service: [PRODUCT_OR_SERVICE_NAME]
- Audience type: [RETARGETING_SEGMENT — e.g., "website visitors who viewed product pages but didn't purchase in the last 14 days"]
- Objection to overcome: [OBJECTION — e.g., "price concern", "didn't trust the brand yet", "got distracted"]
- Incentive (if any): [INCENTIVE — e.g., "extra 10% off for returning visitors"]
- Platform: [META / GOOGLE]

TASK:
Generate 3 retargeting ad copy variations. Each should acknowledge the user's prior interest without being creepy, overcome the stated objection, and include the incentive if provided.

FORMAT RULES:
- Tone: Helpful and inviting, not pushy
- Headline: ≤ 40 chars (Meta) / ≤ 30 chars (Google)
- Body/Description: ≤ 90 characters
- Do NOT say "We noticed you visited our site" — too explicit; imply familiarity instead
- Include social proof element if possible (e.g., "Join 10,000+ happy customers")

OUTPUT FORMAT (JSON):
{
  "variations": [
    {
      "headline": "...",
      "body": "...",
      "cta": "..."
    }
  ]
}
```

---

## Post-Processing Checklist

After receiving LLM output, verify:
- [ ] All character counts are within limits (count manually for final versions)
- [ ] No trademark/copyright issues (competitor brand names, protected terms)
- [ ] No policy-violating claims: "guaranteed", "cure", "best in the world" without evidence
- [ ] No prices in Google headlines (can change and cause disapproval)
- [ ] No excessive punctuation (!!!, ???)
- [ ] No ALL CAPS words (violates both platform policies)
- [ ] CTA is appropriate for the platform's allowed CTA buttons
- [ ] Localise pricing, currency, and cultural references for target market

---

## LLM API Call (Python)

```python
import anthropic

def generate_ad_copy(template: str) -> dict:
    """Send a filled prompt template to Claude and return structured JSON."""
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": template
            }
        ]
    )
    
    import json
    raw_text = message.content[0].text
    
    # Strip markdown code fences if present
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
    
    return json.loads(raw_text)
```


---
