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
