# Instagram Playbook

*Specs and platform mechanics below are last-verified as of mid-2026 — confirm against Meta's current Ads Manager and Help Center before finalizing production assets (see SKILL.md Section 6).*

## Organic Content by Surface

- **Reels**: The primary discovery surface. 7–15 second hooks, trending audio (native audio still generally outperforms muted/no-audio for reach), text-on-screen for sound-off viewers, loop-worthy endings that reward rewatching.
- **Stories**: Polls, quizzes, and the **Link sticker** for click-throughs — this replaced the old "swipe-up" gesture in 2021 and has **no follower minimum**; every account, regardless of size, can add a tappable link to a Story. Good for behind-the-scenes, real-time, lower-production content.
- **Feed**: High-res imagery, carousels for educational/step-by-step content, a consistent aesthetic across the grid still matters for profile-visit conversion even though most discovery now happens via Reels/Explore rather than the grid itself.
- **Shopping**: Product tags on posts/Reels, collection showcases, native checkout where available by market — increasingly central to how commerce brands use the platform rather than a bolt-on feature.

## Ad Formats & Specs

*For campaign objectives, budget structure (CBO/ABO), audience-building, Pixel/CAPI setup, and ad policy — all shared across Facebook/Instagram/Threads — see `platforms/meta-ads-manager.md`.*

- **Dimensions**: 1:1 or 4:5 for feed (4:5 takes up more mobile screen space and frequently outperforms 1:1 on engagement); 9:16 for Stories/Reels placements.
- **Text overlay**: Meta retired its hard 20% text cap in 2020 — text-heavy images are no longer rejected outright — but the delivery algorithm still soft-penalizes text-heavy creative with lower predicted CTR and higher effective CPMs. Treat "keep it light" as a performance best practice, not a compliance rule.
- **Placements run through Meta Ads Manager** alongside Facebook — most advertisers build once and let Advantage+ placements decide the mix across Instagram feed/Stories/Reels/Explore rather than manually picking each surface (see `ad-planning-and-paid-media.md` Section 3).

## Algorithm & Ranking Notes

- Watch time and rewatches are strong signals for Reels distribution specifically — a short, loopable format frequently outperforms a longer one with a weaker ending.
- Saves and shares are read as stronger intent signals than likes for broader distribution — content designed to be saved (reference-style, list-style) or shared (relatable, surprising) tends to earn more reach than content designed only to be liked.
- Consistency of posting matters less than consistency of *quality relative to the account's own baseline* — a sudden low-effort post can suppress an account's subsequent reach more than an irregular posting schedule does.

## Practical Notes

- Auto-cross-posted content from other platforms (especially TikTok watermarked video) is measurably deprioritized — re-export or re-edit native Reels rather than reposting as-is when Instagram is a real priority surface, not an afterthought.
- Carousel posts remain a strong, underused format for educational/how-to content — they reward a swipe-through completion signal similarly to how video rewards watch-through.
