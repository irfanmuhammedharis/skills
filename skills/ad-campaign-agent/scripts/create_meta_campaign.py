#!/usr/bin/env python3
"""
Meta (Facebook/Instagram) Campaign Creation Script
HexCodePlus / Marinode AI — Ad Campaign Agent

Usage:
    python create_meta_campaign.py

Set environment variables before running:
    META_ACCESS_TOKEN   — Long-lived user or system user token
    META_AD_ACCOUNT_ID  — Format: act_123456789
    META_PAGE_ID        — Your Facebook Page ID

This script creates a complete campaign: Campaign → Ad Set → Creative → Ad (all PAUSED).
"""

import os
import json
import time
import random
import hashlib
import requests
from typing import Optional

# ── Config ─────────────────────────────────────────────────────────────────
ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "act_YOUR_ACCOUNT_ID")
PAGE_ID = os.environ.get("META_PAGE_ID", "YOUR_PAGE_ID")
API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


# ── Helpers ─────────────────────────────────────────────────────────────────

def api_post(endpoint: str, payload: dict, max_retries: int = 5) -> dict:
    """POST to Meta Graph API with exponential backoff on rate limits."""
    url = f"{BASE_URL}/{endpoint}"
    payload["access_token"] = ACCESS_TOKEN

    for attempt in range(max_retries):
        resp = requests.post(url, data=payload)
        if resp.status_code == 429:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {wait:.1f}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise ValueError(f"API error: {data['error']}")
        return data

    raise Exception("Max retries exceeded on Meta API call")


def api_get(endpoint: str, params: dict = None) -> dict:
    """GET from Meta Graph API."""
    url = f"{BASE_URL}/{endpoint}"
    params = params or {}
    params["access_token"] = ACCESS_TOKEN
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


# ── Campaign ─────────────────────────────────────────────────────────────────

def create_campaign(
    name: str,
    objective: str = "LINK_CLICKS",
    daily_budget: int = 50000,          # in paise/cents (50000 = ₹500 / $5)
    special_ad_categories: list = None,
) -> str:
    """
    Create a Meta campaign.

    Args:
        name: Campaign name
        objective: LINK_CLICKS | CONVERSIONS | APP_INSTALLS | LEAD_GENERATION |
                   BRAND_AWARENESS | REACH | VIDEO_VIEWS | MESSAGES
        daily_budget: Daily budget in smallest currency unit (paise for INR)
        special_ad_categories: ["HOUSING"] | ["CREDIT"] | ["EMPLOYMENT"] | [] for none

    Returns:
        campaign_id (string)
    """
    payload = {
        "name": name,
        "objective": objective,
        "status": "PAUSED",
        "daily_budget": str(daily_budget),
        "special_ad_categories": json.dumps(special_ad_categories or []),
    }
    result = api_post(f"{AD_ACCOUNT_ID}/campaigns", payload)
    campaign_id = result["id"]
    print(f"✅ Campaign created: {campaign_id}")
    return campaign_id


# ── Ad Set ─────────────────────────────────────────────────────────────────

def create_ad_set(
    campaign_id: str,
    name: str,
    optimization_goal: str = "LINK_CLICKS",
    billing_event: str = "IMPRESSIONS",
    daily_budget: Optional[int] = None,
    bid_amount: Optional[int] = None,
    targeting: Optional[dict] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> str:
    """
    Create an Ad Set inside a campaign.

    Args:
        optimization_goal: LINK_CLICKS | CONVERSIONS | APP_INSTALLS | REACH |
                           IMPRESSIONS | LANDING_PAGE_VIEWS
        billing_event: IMPRESSIONS | LINK_CLICKS
        daily_budget: If using ad-set-level budgets (int, in paise/cents)
        bid_amount: Manual bid in paise/cents. Omit for auto-bid.
        targeting: Dict with age_min, age_max, genders, geo_locations, interests, etc.
        start_time: ISO 8601 string, e.g. "2026-07-01T00:00:00+0530"

    Returns:
        adset_id (string)
    """
    default_targeting = {
        "age_min": 18,
        "age_max": 65,
        "geo_locations": {"countries": ["IN"]},
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["feed"],
        "instagram_positions": ["stream"],
    }

    payload = {
        "campaign_id": campaign_id,
        "name": name,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "targeting": json.dumps(targeting or default_targeting),
        "status": "PAUSED",
    }

    if daily_budget:
        payload["daily_budget"] = str(daily_budget)
    if bid_amount:
        payload["bid_amount"] = str(bid_amount)
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    result = api_post(f"{AD_ACCOUNT_ID}/adsets", payload)
    adset_id = result["id"]
    print(f"✅ Ad Set created: {adset_id}")
    return adset_id


# ── Creative ─────────────────────────────────────────────────────────────────

def upload_image(image_path: str) -> str:
    """
    Upload a local image to the ad account and return its image hash.
    image_path: local file path (JPG/PNG)
    """
    url = f"{BASE_URL}/{AD_ACCOUNT_ID}/adimages"
    with open(image_path, "rb") as f:
        files = {"filename": (os.path.basename(image_path), f, "image/jpeg")}
        data = {"access_token": ACCESS_TOKEN}
        resp = requests.post(url, files=files, data=data)
        resp.raise_for_status()
        result = resp.json()
        images = result.get("images", {})
        image_hash = list(images.values())[0]["hash"]
        print(f"✅ Image uploaded. Hash: {image_hash}")
        return image_hash


def create_image_creative(
    name: str,
    image_hash: str,
    headline: str,
    primary_text: str,
    link_url: str,
    cta_type: str = "SHOP_NOW",
    description: str = "",
) -> str:
    """
    Create an ad creative with a single image.

    cta_type options: SHOP_NOW | LEARN_MORE | SIGN_UP | DOWNLOAD | GET_QUOTE |
                      SUBSCRIBE | BOOK_TRAVEL | CONTACT_US | APPLY_NOW | INSTALL_APP
    """
    story_spec = {
        "page_id": PAGE_ID,
        "link_data": {
            "image_hash": image_hash,
            "link": link_url,
            "message": primary_text,
            "name": headline,
            "description": description,
            "call_to_action": {
                "type": cta_type,
                "value": {"link": link_url},
            },
        },
    }

    payload = {
        "name": name,
        "object_story_spec": json.dumps(story_spec),
    }
    result = api_post(f"{AD_ACCOUNT_ID}/adcreatives", payload)
    creative_id = result["id"]
    print(f"✅ Creative created: {creative_id}")
    return creative_id


def create_carousel_creative(
    name: str,
    primary_text: str,
    cards: list,
) -> str:
    """
    Create a carousel ad creative.

    cards: list of dicts with keys: image_hash, link, headline, description, cta_type
    Example card:
        {
            "image_hash": "abc123",
            "link": "https://example.com/product-1",
            "headline": "Product 1 — ₹999",
            "description": "Buy Now",
            "cta_type": "SHOP_NOW"
        }
    """
    child_attachments = []
    for card in cards:
        child_attachments.append({
            "link": card["link"],
            "image_hash": card["image_hash"],
            "name": card["headline"],
            "description": card.get("description", ""),
            "call_to_action": {"type": card.get("cta_type", "SHOP_NOW")},
        })

    story_spec = {
        "page_id": PAGE_ID,
        "link_data": {
            "link": cards[0]["link"],
            "message": primary_text,
            "child_attachments": child_attachments,
            "multi_share_optimized": True,
            "call_to_action": {"type": "SHOP_NOW"},
        },
    }

    payload = {
        "name": name,
        "object_story_spec": json.dumps(story_spec),
    }
    result = api_post(f"{AD_ACCOUNT_ID}/adcreatives", payload)
    creative_id = result["id"]
    print(f"✅ Carousel creative created: {creative_id}")
    return creative_id


# ── Ad ─────────────────────────────────────────────────────────────────────

def create_ad(adset_id: str, creative_id: str, name: str) -> str:
    """Create an ad linking an ad set to a creative."""
    payload = {
        "name": name,
        "adset_id": adset_id,
        "creative": json.dumps({"creative_id": creative_id}),
        "status": "PAUSED",
    }
    result = api_post(f"{AD_ACCOUNT_ID}/ads", payload)
    ad_id = result["id"]
    print(f"✅ Ad created: {ad_id}")
    return ad_id


# ── Reporting ─────────────────────────────────────────────────────────────────

def get_insights(entity_id: str, date_preset: str = "last_7d") -> dict:
    """Fetch performance insights for a campaign, ad set, or ad."""
    params = {
        "fields": "impressions,clicks,spend,ctr,cpc,cpm,actions,cost_per_action_type",
        "date_preset": date_preset,
    }
    return api_get(f"{entity_id}/insights", params)


# ── Custom Audiences ──────────────────────────────────────────────────────────

def hash_email(email: str) -> str:
    """SHA-256 hash an email address (lowercase, stripped) for Meta custom audiences."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


# ── UTM Builder ───────────────────────────────────────────────────────────────

def build_utm_url(
    base_url: str,
    campaign_name: str,
    ad_name: str = "",
    utm_source: str = "facebook",
    utm_medium: str = "paid-social",
) -> str:
    """Append UTM parameters to a URL."""
    separator = "&" if "?" in base_url else "?"
    params = (
        f"utm_source={utm_source}"
        f"&utm_medium={utm_medium}"
        f"&utm_campaign={campaign_name.replace(' ', '_').lower()}"
    )
    if ad_name:
        params += f"&utm_content={ad_name.replace(' ', '_').lower()}"
    return f"{base_url}{separator}{params}"


# ── Full Example ──────────────────────────────────────────────────────────────

def run_example():
    """
    End-to-end example: creates a single-image traffic campaign.
    Replace values with real ones.
    """
    # Campaign config
    campaign_name = "SpringSale_Traffic_2026"
    daily_budget = 50000  # ₹500 in paise

    targeting = {
        "age_min": 25,
        "age_max": 44,
        "genders": [2],  # 2 = female
        "geo_locations": {"countries": ["IN"]},
        "interests": [{"id": "6003107902433", "name": "Online shopping"}],
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["feed"],
        "instagram_positions": ["stream"],
    }

    landing_page = build_utm_url(
        "https://example.com/spring-sale",
        campaign_name=campaign_name,
        ad_name="ImageAd_V1",
    )

    # Create campaign
    campaign_id = create_campaign(
        name=campaign_name,
        objective="LINK_CLICKS",
        daily_budget=daily_budget,
    )

    # Create ad set
    adset_id = create_ad_set(
        campaign_id=campaign_id,
        name="Women25-44_India_Feed",
        optimization_goal="LINK_CLICKS",
        billing_event="IMPRESSIONS",
        targeting=targeting,
    )

    # Upload image and create creative
    # image_hash = upload_image("assets/spring_sale_1080x1080.jpg")
    # For demo purposes, use a placeholder hash:
    image_hash = "PLACEHOLDER_HASH_REPLACE_WITH_REAL"

    creative_id = create_image_creative(
        name="SpringSale_ImageCreative_V1",
        image_hash=image_hash,
        headline="Grab the Deal Before It's Gone",
        primary_text="Shop our Spring collection — up to 40% off. Free delivery above ₹999.",
        link_url=landing_page,
        cta_type="SHOP_NOW",
        description="Limited time offer",
    )

    # Create ad
    ad_id = create_ad(
        adset_id=adset_id,
        creative_id=creative_id,
        name="SpringSale_ImageAd_V1",
    )

    print("\n── Campaign Summary ──")
    print(f"Campaign ID:  {campaign_id}")
    print(f"Ad Set ID:    {adset_id}")
    print(f"Creative ID:  {creative_id}")
    print(f"Ad ID:        {ad_id}")
    print(f"Landing page: {landing_page}")
    print("\nAll entities created in PAUSED status. Review in Ads Manager before activating.")


if __name__ == "__main__":
    run_example()
