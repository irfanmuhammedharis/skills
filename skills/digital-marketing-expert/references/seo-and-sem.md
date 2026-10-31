# SEO, SEM & AI-Search Optimization

Read this file for: on-page and technical SEO, keyword research, topic clusters, SEM/PPC search campaign structure, and optimizing for AI-generated answers (AEO/GEO). For editorial calendar mechanics, see `content-planning-and-calendars.md`.

## 1. On-Page SEO Fundamentals

- **Title tags**: front-load the primary keyword/intent, keep it distinct from every other page's title on the site — duplicate or near-duplicate titles confuse both search engines and users deciding which result to click.
- **Meta descriptions**: written to earn the click (they're a pitch, not a ranking factor directly) — specific and benefit-forward beats generic.
- **Header structure**: one H1 per page reflecting the core topic, H2s/H3s structuring genuine subtopics (not just formatting for formatting's sake) — a clean header hierarchy is also exactly what both classic search snippets and AI answer engines lean on to extract structure (see Section 4).
- **Internal linking**: link to and from related content using descriptive anchor text (not "click here") — this is how both crawlers and readers understand topical relationships across the site.
- **Schema markup**: structured data (FAQ, HowTo, Product, Article, etc.) that explicitly tells search engines and AI crawlers what a page contains — increasingly important as more of the answer surface is machine-extracted rather than click-through (see Section 4).

## 2. Technical SEO Basics

- **Crawlability**: confirm nothing important is accidentally blocked in robots.txt or noindexed; a clean XML sitemap submitted to Search Console.
- **Site speed / Core Web Vitals**: page-load and interactivity metrics that affect both ranking and, more directly, conversion rate — slow pages lose people regardless of rank.
- **Mobile-first**: the mobile version of a page is what search engines primarily evaluate — a desktop-polished, mobile-broken page underperforms regardless of desktop quality.

## 3. Keyword Research Process

1. **Classify by search intent**: informational ("how does X work"), navigational ("brand name login"), commercial investigation ("best X for Y," "X vs Y"), transactional ("buy X," "X pricing"). The content format should match the intent — a transactional query landing on a pure educational blog post underperforms even if the keyword volume looked attractive.
2. **Build topic clusters**: a pillar page covering a broad topic comprehensively, linked to and from a cluster of narrower supporting pages on subtopics. This structure signals topical authority more effectively than isolated, unlinked pages targeting the same general subject.
3. **Content gap analysis**: identify what real customer questions and competitor-ranking topics have no corresponding page yet — the gap between "what people are asking" and "what we currently answer" is usually the highest-leverage content backlog.

## 4. AI-Search Optimization (AEO / GEO)

Traditional SEO gets a page ranked; a meaningful and growing share of search behavior now resolves through AI-generated summaries (Google AI Overviews, ChatGPT, Perplexity, and similar) that answer the question directly, sometimes without a click at all. This doesn't replace SEO — it adds a layer on top of it, and the fundamentals (crawlable, well-structured, genuinely authoritative content) are still the foundation either way.

- **AEO (Answer Engine Optimization)**: structuring specific content so it's easily extracted as a direct answer — concise, self-contained answer paragraphs near the top of a section, clear question-formatted subheadings, and content formatted to match how the topic is typically surfaced (paragraph, list, or table — check what format currently shows for the target query and match it).
- **GEO (Generative Engine Optimization)**: the broader practice of building brand presence and authority such that generative AI systems cite or recommend the brand when synthesizing an answer — this leans more on earned authority, consistent entity presence across the web, and third-party mentions than on any single on-page trick.
- **Entity clarity**: make sure the brand, product, and key concepts are unambiguously and consistently described across the site and in structured data — AI systems (like classic search) rely heavily on being able to confidently resolve "what/who is this" before citing it.
- **This is a fast-moving, heavily-covered area with a lot of unverified statistics circulating** — treat specific percentage claims about AI-search traffic share or citation-rate lift with real skepticism, verify against current reporting before repeating a number, and lean on the durable structural advice (clear direct answers, schema, entity consistency, earned third-party citations) over any single "hack."

## 5. SEM / PPC Search Campaigns

*For the full Google Ads campaign-type taxonomy (Search, Display, Shopping, Demand Gen, Performance Max, App), Smart Bidding strategy names, conversion tracking, ad Assets, and Google ad policy, see `platforms/google-ads.md`. This section covers Search campaign structure specifically.*

- **Structure**: Campaign (budget + goal) → Ad Group (tightly themed keyword cluster) → Keywords + Ads. A tightly themed ad group (a handful of closely related keywords) lets the ad copy actually match the query — a loosely grouped ad group forces generic copy that matches nothing well.
- **Match types**: broad, phrase, and exact match trade reach for precision — broad match now leans heavily on the platform's own AI matching rather than literal keyword matching, so it needs closer monitoring (and negative keywords) than it used to.
- **Quality Score factors**: expected CTR, ad relevance, and landing page experience — a low Quality Score raises effective cost per click even at the same bid, so landing page relevance is a cost lever, not just a conversion lever.
- **Responsive Search Ads (RSAs)**: supply multiple headline/description variations and let the platform test combinations — provide genuinely distinct messaging angles across the variations (not just minor rewordings) so the system has real options to test, not near-duplicates.
- **Negative keywords**: actively maintained, not a one-time setup — review search term reports regularly to catch irrelevant queries burning budget, especially under broad match.
