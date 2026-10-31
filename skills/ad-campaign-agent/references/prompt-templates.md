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
