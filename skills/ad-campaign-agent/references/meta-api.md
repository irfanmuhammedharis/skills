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
