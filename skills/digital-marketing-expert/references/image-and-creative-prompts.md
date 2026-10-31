# Image & Creative Generation Prompts

Read this file for: writing image-generation prompts for marketing assets, ad creative, social graphics, and brand visuals — including matching generation output to a target size/resolution and choosing quality descriptors that actually do something. For platform-specific *dimension requirements* (the actual aspect ratios a placement needs), cross-check the relevant `platforms/*.md` — those numbers drift and are deliberately not hardcoded here (see SKILL.md Section 6). This file covers the generation *mechanics and craft* of hitting those dimensions well, which is a different, more durable layer. For the underlying creative strategy, see `strategy-and-positioning.md` and `content-planning-and-calendars.md`.

## 1. Prompt Anatomy

A strong marketing image prompt states, in order: **subject → setting → lighting → composition/framing → style/mood → technical specs → brand cues**. Vague prompts get generic results; the fix is almost always more specificity in setting and lighting, not a longer list of adjectives (see Section 2.3 on why adjective-stacking underperforms specificity).

```
A [mood] [style] photograph of [specific subject] in [specific setting],
[lighting description], [color palette], [composition/framing],
[emotion/atmosphere]. Shot on [camera/lens style, if photographic look wanted].
[Brand element: logo placement / color accent / product detail]. [Technical specs:
aspect ratio, resolution, quality descriptors].
```

## 2. Resolution, Output Size & Quality Descriptors

### 2.1 Matching Generation Output to a Target Size

State the target aspect ratio explicitly in the prompt itself — don't leave it to be resized after generation. Generating natively at the target ratio preserves the composition (negative space, focal point placement) that was actually composed for that shape; cropping a differently-composed image down to a new ratio after the fact frequently cuts off the intended focal point or the space reserved for a text overlay (see Section 6).

- **Get the target ratio from the actual destination**, not a guess — `platforms/*.md` is the source of truth for what a given placement needs.
- **Generation tool syntax for size/ratio varies by tool**: some accept an explicit aspect-ratio parameter, some accept exact pixel dimensions, some only offer a fixed preset list. Confirm current syntax for whichever tool is actually generating the image rather than assuming one universal format works everywhere.
- **Upscaling is sometimes unavoidable** when native output resolution is too low for the intended use. It can introduce its own artifacts (over-smoothed texture, fine-detail loss, occasional new artifacts at edges) — an upscaled asset needs the same final visual QA pass as any other output (Section 8), not less scrutiny just because it's "only a resize."

### 2.2 Resolution Needs by End-Use Tier

Resolution requirements scale with how the asset will actually be viewed. Treating every asset like it needs the same technical bar either wastes effort or under-delivers:
- **Small/digital-only** (social feed, email): lowest resolution tolerance — the platform typically re-compresses on upload anyway, and viewing size is small. Don't over-invest in resolution here at the expense of getting more generation attempts at the composition itself.
- **Mid-tier** (website hero, display ad, presentation slide): needs to hold up at a larger on-screen size without visible softness or compression artifact — a genuine, moderate resolution floor.
- **Large-format/print** (OOH, billboards, posters, printed collateral): the highest bar. Physical print and long viewing distance reveal detail loss that a small screen simply hides. This tier needs meaningfully higher native resolution (or a careful, artifact-checked upscale) *and* usually a simpler, bolder composition — fine detail reads poorly at billboard viewing distance regardless of source resolution. See the Print/Large-Format template in Section 3.

### 2.3 Quality Descriptors — What Actually Earns Its Place

Not every "quality" word in a prompt is doing real work. Two different things get called quality descriptors, and only one reliably changes output:
- **Specific, learnable technical/photographic terms** genuinely steer generation: "sharp focus," "shallow depth of field," "studio lighting," "color-accurate," "professional retouching," "35mm lens." These correspond to real visual concepts the model has actually learned from photography.
- **Vague quality boilerplate stacked at the end of a prompt** ("ultra-detailed, 8k, masterpiece, high quality, stunning, award-winning") is inconsistent across models and tools, and rarely does much once a reasonable baseline is already met — five overlapping quality buzzwords is a weaker use of prompt space than one or two well-chosen technical terms plus more specificity earlier in the prompt.
- **The real lever for perceived quality is specificity in subject/setting/lighting** (Section 1), not adjective density at the end — a precisely-described scene with minimal quality language consistently outperforms a vague scene buried in quality buzzwords.
- Always visually confirm the actual output meets the bar (Section 8) — a prompt with the "right" quality words is not a substitute for reviewing what actually got generated.

## 3. Template Library by Asset Type

**Social Media Ad (feed/reel)**
```
A [mood] [style] photograph of [subject] in [setting], [lighting description],
[color palette], [composition], [emotion/atmosphere]. Shot on [camera/lens].
[Brand element: subtle logo placement/color accent]. Clean background,
high contrast, mobile-optimized, [aspect ratio per platform — see platforms/*.md].
```

**Hero Banner / Website Header**
```
A [wide-angle/hero shot] of [subject/scene], [dramatic lighting],
[brand colors as accent], [depth and layers], [professional retouching].
[16:9 or per-placement ratio], generous negative space on [left/right] for
text overlay, corporate yet approachable.
```

**Product Photography**
```
Studio product shot of [product] on [surface/material], [lighting setup],
[shadow style], [contextual props], [angle]. Sharp focus, commercial
photography, color-accurate, reflection control, e-commerce ready, 1:1
aspect ratio.
```

**Influencer / Lifestyle / UGC-style**
```
Candid lifestyle photo of [demographic] [activity] in [location],
natural [time of day] lighting, authentic emotion, [brand product] naturally
integrated, relatable and aspirational, social-media-native, warm tones,
shallow depth of field, slightly imperfect framing (not studio-polished).
```

**Testimonial / Social-Proof Graphic**
```
Clean, minimal graphic layout with generous negative space for a quote
overlay, [brand color palette], subtle [texture/pattern] background,
professional but warm, room in [top/bottom/side] third for text, no
competing visual elements near the quote zone.
```

**Before / After**
```
Split-composition image, [left/right or top/bottom] divide, consistent
lighting and camera angle across both halves so the only variable is the
change itself, [subject/context], clear visual contrast between the two
states, clean dividing line, no distracting background elements.
```

**Infographic-Style Visual**
```
Flat, modern infographic illustration of [concept/process], [brand color
palette], simple iconography, clear visual hierarchy guiding the eye from
[start point] to [end point], generous white space, minimal text baked into
the image (add real text as an overlay layer instead — see Section 6).
```

**App/Product UI Mockup**
```
Clean device mockup ([phone/laptop/tablet] frame) displaying [app/product
screen], realistic screen glare/reflection at low intensity, neutral or
brand-colored background, soft shadow beneath device, professional product
marketing style.
```

**Email Header Graphic**
```
Wide, short-aspect banner image of [subject/scene], [brand color palette],
[lighting], designed with a clear focal point that survives being cropped
narrow on mobile email clients, minimal fine detail (email images render
small — see Section 2.2), [600px-width-safe composition].
```

**Carousel — Multi-Panel Consistency**
```
[Base prompt describing subject/setting/lighting/style], panel [N] of [total]:
[what's different in this specific panel]. Keep camera angle, lighting
direction, color grade, and subject styling identical across all panels
in the set — only the panel-specific element listed above should change.
```
Generate carousels as a named series and explicitly re-state the shared constants in every panel's prompt — image generation models don't retain a "style memory" between separate generations, so consistency has to be engineered into each prompt, not assumed.

**Seasonal/Promotional Overlay Base**
```
[Base product/lifestyle scene], composition leaves clear open space in
[quadrant] for a promotional graphic/badge to be added in post, avoid
generating text or numbers in the image itself (see Section 6), [seasonal
color palette/motifs] worked into props/background rather than overlaid text.
```

**Print / Large-Format / OOH**
```
[Subject/scene] composed boldly and simply for distant viewing — one large,
unmistakable focal point, minimal fine detail that would be lost at viewing
distance, high contrast for readability from far away. [Lighting], [brand
colors]. Generate at the highest native resolution the tool supports for
this composition, and plan a dedicated, artifact-checked upscale pass if
the final physical size requires it (see Section 2.1–2.2).
```
The composition brief here is genuinely different from every other template in this list, not just the resolution: billboard and large-poster viewing happens from a distance and often at speed (a passing car, a walked-past poster), so the design has to work as one glanceable idea — a busy, detail-rich composition that reads well on a phone screen usually fails at this scale.

## 4. Visual Style Directives

- **Luxury/Premium**: Soft lighting, muted palettes, minimal props, generous negative space, serif-adjacent visual cues
- **Tech/SaaS**: Clean lines, gradient accents, isometric or abstract-geometric elements, blue/cyan/purple palettes, modern sans-serif visual language
- **Wellness/Lifestyle**: Earth tones, natural light, organic textures, candid unposed moments, warm filters
- **Edgy/Youth**: High contrast, bold saturated colors, dynamic angles, street aesthetic, visible grain/texture
- **Corporate/B2B**: Professional settings, confident poses, structured/grid-based layouts, trustworthy blues and grays
- **Minimalist/Scandinavian**: Neutral palette, abundant negative space, one clear focal object, natural materials, soft diffused light
- **Maximalist/Retro-Revival**: Saturated clashing colors, pattern-on-pattern, playful composition, nostalgic references worn lightly rather than literally
- **Editorial/Fashion**: Dramatic directional lighting, strong single focal point, sophisticated color grading, intentional negative space as a compositional element
- **Playful/Gen-Z**: Bright flat colors, exaggerated proportions or props, irreverent composition, deliberately imperfect/handmade feel over polish
- **Heritage/Craft**: Warm, slightly desaturated tones, tactile/textured materials in frame, natural imperfection, storytelling props over sterile staging

## 5. Negative Prompt Guidance

State explicitly what to avoid — it does as much work as the positive prompt:
- **Avoid the generic "stock photo" look**: exclude "posed," "staged," "obviously stock," "corporate stock photography" when authenticity is the goal.
- **Avoid AI-image tells**: excessive symmetry, waxy/over-smoothed skin, malformed hands/text, uncanny-valley expressions — flag these as things to avoid, and always visually review output rather than trusting the prompt alone to prevent them.
- **Avoid heavy in-image text** where the platform's delivery algorithm penalizes it (see the Meta text-overlay note in `platforms/instagram.md`) — generate clean visuals and add text as a separate overlay layer instead (see Section 6).
- **Avoid competitor or real-brand visual cues** unintentionally — don't let "premium tech aesthetic" drift into replicating a specific real competitor's actual visual identity.

## 6. Text-in-Image: Generate Clean, Overlay Separately

Image generation models are unreliable at rendering legible, correctly-spelled text directly into an image, and several platforms' delivery algorithms still soft-penalize heavy in-image text even where it's not against a hard policy (see `platforms/instagram.md`). The reliable workflow: generate the visual completely clean, with composition that leaves clear negative space where text will go, then add real, crisp text as a separate design layer. Say so explicitly in the prompt ("leave clear open space in [location] for a text overlay to be added separately") rather than asking the model to render the words.

## 7. Brand Consistency Across a Set

- **Inject exact brand colors** as hex-adjacent descriptions ("a specific warm coral, not generic orange/red") rather than vague color names — vague color words drift generation to generation.
- **Anchor a consistent subject/style description** and reuse it verbatim across every prompt in a campaign set, changing only the scene-specific elements — the same discipline as the carousel guidance in Section 3.
- **Keep a running "style sheet"** of the exact phrases that produced on-brand results in past generations for a given brand, and reuse them — this is the fastest way to get repeatable output across a long campaign without redoing style discovery every time.

## 8. Iteration & Refinement Workflow

1. Generate against the brief, then critique the output against the brief specifically — not against a vague "does this look good" — did it hit subject, setting, lighting, composition, and brand cues as specified?
2. Isolate what's wrong and change only that element in the next prompt (composition, lighting, subject pose) — regenerating from scratch with a totally different prompt loses whatever was already working.
3. For anything going to production (paid media, a public-facing asset, anything upscaled per Section 2.1), do a final human visual QA pass specifically for AI-generation artifacts (Section 5) before it ships — these are easy to miss when reviewing quickly at thumbnail size.

## 9. AI-Generated Content Disclosure

Platform and regulatory disclosure requirements for AI-generated or AI-assisted marketing imagery are evolving and vary by platform, region, and use case — this is a compliance question, not a creative one, so confirm current requirements for the specific platform and market before publishing rather than assuming last year's rule still applies (see SKILL.md Section 6). This is general awareness, not legal advice.
