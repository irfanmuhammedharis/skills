#!/usr/bin/env python3
"""
Google Ads Campaign Creation Script
HexCodePlus / Marinode AI — Ad Campaign Agent

Usage:
    python create_google_campaign.py

Prerequisites:
    pip install google-ads google-auth-oauthlib

Configure google-ads.yaml in the working directory (or set GOOGLE_ADS_YAML env var):
    developer_token: "YOUR_DEVELOPER_TOKEN"
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    refresh_token: "YOUR_REFRESH_TOKEN"
    # login_customer_id: "YOUR_MCC_ID"  # Uncomment if using MCC

This script creates: Budget → Campaign → Ad Group → Keywords → Responsive Search Ad
All entities created in PAUSED status.
"""

import os
import sys
import time
import random
from typing import Optional

# ── Dependency check ────────────────────────────────────────────────────────
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    sys.exit(
        "google-ads package not found. Install with:\n"
        "  pip install google-ads\n"
        "  pip install google-auth-oauthlib"
    )

# ── Config ─────────────────────────────────────────────────────────────────
CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "1234567890")
CONFIG_PATH = os.environ.get("GOOGLE_ADS_YAML", "google-ads.yaml")

# Google Ads uses micros (1,000,000 micros = 1 currency unit)
# For INR: 500 * 1_000_000 = 500,000,000 micros = ₹500
INR_TO_MICROS = 1_000_000


def micros(amount_in_currency: float) -> int:
    """Convert currency amount to Google Ads micros."""
    return int(amount_in_currency * INR_TO_MICROS)


# ── Client ─────────────────────────────────────────────────────────────────

def get_client() -> GoogleAdsClient:
    """Load Google Ads client from yaml config."""
    return GoogleAdsClient.load_from_storage(path=CONFIG_PATH)


# ── Retry helper ────────────────────────────────────────────────────────────

def with_backoff(func, max_retries: int = 5):
    """Execute a function with exponential backoff on quota errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except ResourceExhausted:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"  Quota hit. Waiting {wait:.1f}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait)
        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                print(f"  Google Ads error: {error.message}")
            raise
    raise Exception("Max retries exceeded on Google Ads API call")


# ── Budget ─────────────────────────────────────────────────────────────────

def create_campaign_budget(
    client: GoogleAdsClient,
    customer_id: str,
    name: str,
    daily_budget_inr: float = 500.0,
    delivery_method: str = "STANDARD",
) -> str:
    """
    Create a campaign budget.

    Args:
        daily_budget_inr: Daily budget in INR (or your account currency)
        delivery_method: STANDARD (spread evenly) or ACCELERATED (spend as fast as possible)

    Returns:
        budget resource name (e.g. "customers/1234/campaignBudgets/5678")
    """
    budget_service = client.get_service("CampaignBudgetService")
    budget_op = client.get_type("CampaignBudgetOperation")
    budget = budget_op.create

    budget.name = name
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum[delivery_method]
    budget.amount_micros = micros(daily_budget_inr)
    budget.explicitly_shared = False  # Dedicated to one campaign

    def create():
        return budget_service.mutate_campaign_budgets(
            customer_id=customer_id,
            operations=[budget_op],
        )

    response = with_backoff(create)
    resource_name = response.results[0].resource_name
    print(f"✅ Budget created: {resource_name}")
    return resource_name


# ── Campaign ─────────────────────────────────────────────────────────────────

def create_campaign(
    client: GoogleAdsClient,
    customer_id: str,
    name: str,
    budget_resource: str,
    channel_type: str = "SEARCH",
    bid_strategy: str = "MANUAL_CPC",
    target_cpa_inr: Optional[float] = None,
    target_roas: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    Create a Google Ads campaign.

    Args:
        channel_type: SEARCH | DISPLAY | PERFORMANCE_MAX | APP | SHOPPING | DEMAND_GEN
        bid_strategy: MANUAL_CPC | MAXIMIZE_CLICKS | MAXIMIZE_CONVERSIONS |
                      TARGET_CPA | TARGET_ROAS | MAXIMIZE_CONVERSION_VALUE
        target_cpa_inr: Required if bid_strategy == TARGET_CPA
        target_roas: Required if bid_strategy == TARGET_ROAS (e.g. 3.5 = 350%)
        start_date: YYYYMMDD format, e.g. "20260701"
        end_date: YYYYMMDD format (optional)

    Returns:
        campaign resource name
    """
    campaign_service = client.get_service("CampaignService")
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.create

    campaign.name = name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.campaign_budget = budget_resource
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum[channel_type]
    )

    # Bid strategy
    if bid_strategy == "MANUAL_CPC":
        campaign.manual_cpc.enhanced_cpc_enabled = False
    elif bid_strategy == "TARGET_CPA":
        campaign.target_cpa.target_cpa_micros = micros(target_cpa_inr or 100)
    elif bid_strategy == "TARGET_ROAS":
        campaign.target_roas.target_roas = target_roas or 3.5
    elif bid_strategy == "MAXIMIZE_CONVERSIONS":
        campaign.maximize_conversions.target_cpa_micros = 0
    elif bid_strategy == "MAXIMIZE_CLICKS":
        campaign.maximize_clicks.target_spend_micros = 0
    elif bid_strategy == "MAXIMIZE_CONVERSION_VALUE":
        campaign.maximize_conversion_value.target_roas = target_roas or 0

    # Network settings (Search campaigns)
    if channel_type == "SEARCH":
        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = True
        campaign.network_settings.target_content_network = False
        campaign.network_settings.target_partner_search_network = False

    # Schedule
    if start_date:
        campaign.start_date = start_date
    if end_date:
        campaign.end_date = end_date

    def create():
        return campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_op],
        )

    response = with_backoff(create)
    resource_name = response.results[0].resource_name
    print(f"✅ Campaign created: {resource_name}")
    return resource_name


# ── Ad Group ─────────────────────────────────────────────────────────────────

def create_ad_group(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_resource: str,
    name: str,
    ad_group_type: str = "SEARCH_STANDARD",
    cpc_bid_inr: float = 5.0,
) -> str:
    """
    Create an ad group within a campaign.

    Args:
        ad_group_type: SEARCH_STANDARD | DISPLAY_STANDARD | SHOPPING_PRODUCT_ADS
        cpc_bid_inr: Default max CPC bid in INR

    Returns:
        ad group resource name
    """
    ad_group_service = client.get_service("AdGroupService")
    ad_group_op = client.get_type("AdGroupOperation")
    ad_group = ad_group_op.create

    ad_group.name = name
    ad_group.campaign = campaign_resource
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum[ad_group_type]
    ad_group.cpc_bid_micros = micros(cpc_bid_inr)

    def create():
        return ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_op],
        )

    response = with_backoff(create)
    resource_name = response.results[0].resource_name
    print(f"✅ Ad Group created: {resource_name}")
    return resource_name


# ── Keywords ─────────────────────────────────────────────────────────────────

def add_keywords(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_resource: str,
    keywords: list,
) -> list:
    """
    Add keywords to an ad group.

    Args:
        keywords: list of dicts:
            {"text": "buy running shoes", "match_type": "PHRASE", "bid_inr": 8.0}
            match_type: EXACT | PHRASE | BROAD

    Returns:
        list of criterion resource names
    """
    service = client.get_service("AdGroupCriterionService")
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
        if "bid_inr" in kw:
            criterion.cpc_bid_micros = micros(kw["bid_inr"])
        operations.append(op)

    def create():
        return service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=operations,
        )

    response = with_backoff(create)
    results = [r.resource_name for r in response.results]
    print(f"✅ {len(results)} keyword(s) added")
    return results


# ── Responsive Search Ad ──────────────────────────────────────────────────────

def create_responsive_search_ad(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_resource: str,
    headlines: list,
    descriptions: list,
    final_url: str,
    path1: str = "",
    path2: str = "",
    pinned_headlines: Optional[dict] = None,
) -> str:
    """
    Create a Responsive Search Ad.

    Args:
        headlines: list of strings, 3–15 items, each ≤30 chars
        descriptions: list of strings, 2–4 items, each ≤90 chars
        pinned_headlines: dict mapping headline text to pin position
            e.g. {"Buy Shoes Online": "HEADLINE_1"} — use sparingly
        path1, path2: Display path fields (each ≤15 chars)

    Returns:
        ad resource name
    """
    service = client.get_service("AdGroupAdService")
    ad_group_ad_op = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_op.create
    ad_group_ad.ad_group = ad_group_resource
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED

    ad = ad_group_ad.ad
    ad.final_urls.append(final_url)

    rsa = ad.responsive_search_ad
    if path1:
        rsa.path1 = path1
    if path2:
        rsa.path2 = path2

    for headline_text in headlines:
        hl = client.get_type("AdTextAsset")
        hl.text = headline_text
        if pinned_headlines and headline_text in pinned_headlines:
            pin_field = pinned_headlines[headline_text]
            hl.pinned_field = client.enums.ServedAssetFieldTypeEnum[pin_field]
        rsa.headlines.append(hl)

    for desc_text in descriptions:
        desc = client.get_type("AdTextAsset")
        desc.text = desc_text
        rsa.descriptions.append(desc)

    def create():
        return service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[ad_group_ad_op],
        )

    response = with_backoff(create)
    resource_name = response.results[0].resource_name
    print(f"✅ Responsive Search Ad created: {resource_name}")
    return resource_name


# ── Reporting ─────────────────────────────────────────────────────────────────

def get_campaign_performance(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_resource: Optional[str] = None,
    date_range: str = "LAST_7_DAYS",
):
    """
    Fetch campaign performance via GAQL.
    date_range: LAST_7_DAYS | LAST_30_DAYS | LAST_MONTH | THIS_MONTH | ALL_TIME
    """
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
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
        WHERE segments.date DURING {date_range}
          AND campaign.status != 'REMOVED'
    """
    if campaign_resource:
        query += f"\n  AND campaign.resource_name = '{campaign_resource}'"

    response = ga_service.search_stream(customer_id=customer_id, query=query)
    results = []
    for batch in response:
        for row in batch.results:
            results.append({
                "campaign": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "ctr": f"{row.metrics.ctr:.2%}",
                "avg_cpc": f"₹{row.metrics.average_cpc / INR_TO_MICROS:.2f}",
                "cost": f"₹{row.metrics.cost_micros / INR_TO_MICROS:.2f}",
                "conversions": row.metrics.conversions,
                "cpa": f"₹{row.metrics.cost_per_conversion / INR_TO_MICROS:.2f}",
            })
    return results


# ── UTM Builder ───────────────────────────────────────────────────────────────

def build_utm_url(
    base_url: str,
    campaign_name: str,
    ad_name: str = "",
    keyword_param: str = "{keyword}",
    matchtype_param: str = "{matchtype}",
) -> str:
    """Build a Google Ads final URL with UTM + ValueTrack parameters."""
    separator = "&" if "?" in base_url else "?"
    utm = (
        f"utm_source=google"
        f"&utm_medium=cpc"
        f"&utm_campaign={campaign_name.replace(' ', '_').lower()}"
        f"&utm_term={keyword_param}"
        f"&utm_matchtype={matchtype_param}"
    )
    if ad_name:
        utm += f"&utm_content={ad_name.replace(' ', '_').lower()}"
    return f"{base_url}{separator}{utm}"


# ── Full Example ──────────────────────────────────────────────────────────────

def run_example():
    """
    End-to-end example: creates a Google Search campaign with RSA and keywords.
    Replace placeholder values with real data.
    """
    client = get_client()
    customer_id = CUSTOMER_ID

    campaign_name = "SpringSale_Search_2026"
    landing_page = build_utm_url(
        "https://example.com/spring-sale",
        campaign_name=campaign_name,
        ad_name="RSA_V1",
    )

    # 1. Budget
    budget_resource = create_campaign_budget(
        client, customer_id,
        name=f"Budget_{campaign_name}",
        daily_budget_inr=500.0,
    )

    # 2. Campaign
    campaign_resource = create_campaign(
        client, customer_id,
        name=campaign_name,
        budget_resource=budget_resource,
        channel_type="SEARCH",
        bid_strategy="MANUAL_CPC",
        start_date="20260701",
    )

    # 3. Ad Group
    ad_group_resource = create_ad_group(
        client, customer_id,
        campaign_resource=campaign_resource,
        name="SpringSale_Keywords_AdGroup",
        cpc_bid_inr=5.0,
    )

    # 4. Keywords
    keywords = [
        {"text": "spring sale shoes", "match_type": "PHRASE"},
        {"text": "buy running shoes online india", "match_type": "BROAD"},
        {"text": "running shoes sale", "match_type": "EXACT", "bid_inr": 8.0},
    ]
    add_keywords(client, customer_id, ad_group_resource, keywords)

    # 5. Responsive Search Ad
    headlines = [
        "Spring Sale — Up to 40% Off",        # 29 chars ✓
        "Shop Running Shoes Online",            # 27 chars ✓
        "Free Delivery on All Orders",          # 28 chars ✓
        "Official Store — Best Prices",         # 29 chars ✓
        "30-Day Easy Returns",                  # 20 chars ✓
        "Buy Shoes — Save Big Today",           # 27 chars ✓
        "Top Running Brands at Low Price",      # 31 chars — trim to 30: "Top Running Brands — Low Price"
        "Order Today, Ship Tomorrow",           # 27 chars ✓
        "Exclusive Deals on Footwear",          # 28 chars ✓
        "India's Favourite Shoe Store",         # 29 chars ✓
    ]
    descriptions = [
        "Discover the best running shoes in India. Free delivery above ₹999. Shop now.",   # 78 chars ✓
        "Spring Sale with up to 40% off on top brands. 30-day returns. Order today.",       # 74 chars ✓
        "Premium quality footwear at unbeatable prices. Free shipping. 30-day returns.",   # 76 chars ✓
        "Shop our Spring collection with exclusive deals. Fast delivery across India.",     # 74 chars ✓
    ]

    create_responsive_search_ad(
        client, customer_id,
        ad_group_resource=ad_group_resource,
        headlines=headlines,
        descriptions=descriptions,
        final_url=landing_page,
        path1="sale",
        path2="shoes",
    )

    print("\n── Campaign Summary ──")
    print(f"Campaign:   {campaign_resource}")
    print(f"Ad Group:   {ad_group_resource}")
    print(f"Keywords:   {len(keywords)} added")
    print(f"Final URL:  {landing_page}")
    print("\nAll entities created in PAUSED status. Review in Google Ads before activating.")


if __name__ == "__main__":
    run_example()
