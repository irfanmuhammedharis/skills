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
