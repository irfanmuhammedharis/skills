---
name: certificate-builder
description: >-
  Generate elegant, print-ready PDF completion/participation/achievement certificates — one polished file per recipient — from a list of names. Produces a warm ivory design with antique-gold and ink-navy accents, classic Cinzel display capitals, a Great Vibes script name, EB Garamond body text, ornamental corner flourishes, a vector gold seal, and a faint centered brand watermark. Use this skill WHENEVER the user wants certificates of ANY kind — "make certificates", "create a certificate", "completion certificate", "participation certificate", "award certificate", "training certificate", "internship certificate" — or wants to bulk-generate per-person certificates for a course, workshop, bootcamp, event, or training programme. Trigger even when the user only pastes a list of names plus an event, or asks to "issue certificates to these students". Defaults are tuned for HexCodePlus training programmes but every label, colour, logo, and signatory is configurable.
---

# Certificate Builder

Generates a beautiful certificate PDF for each recipient, plus a combined PDF
(all certificates in one file for bulk printing) and a ZIP of the individual
files. The visual design is fixed and refined — your job is to gather the event
details and recipient list, write a config JSON, and run the script.

## Workflow

1. **Gather inputs.** From the conversation collect: the recipient list (names,
   each with an optional subtitle like a department/roll/team), the programme or
   event name, the date range / location line, the certificate title, and the
   signatory names. If a logo file was provided, note its path; otherwise the
   bundled HexCodePlus logo is used automatically. Don't over-ask — sensible
   defaults exist for everything except the recipients.

2. **Write a config JSON** (see schema below). Put recipients and any overrides
   in it.

3. **Install deps and run:**
   ```bash
   pip install reportlab pypdf pillow pdf2image --break-system-packages -q
   python scripts/generate_certificates.py config.json
   ```
   Running the script with no argument writes a `sample_config.json` you can
   copy from.

4. **Visually verify before delivering.** Render one short name and one long
   name to PNG and inspect them — the script auto-scales the script-font name,
   but always eyeball it:
   ```bash
   python -c "from pdf2image import convert_from_path; convert_from_path('OUT/02_Name.pdf', dpi=100)[0].save('/tmp/check.png')"
   ```
   Check: name fits inside its gold rule, the seal doesn't collide with the date
   line above or the footer below, and the watermark shows only the logo symbol
   (not wordmark/tagline text).

5. **Deliver** the combined PDF and the ZIP via `present_files`.

## Config schema

All fields optional except `recipients`. Unspecified fields fall back to
HexCodePlus AI/ML training defaults.

```json
{
  "title": "CERTIFICATE",
  "subtitle": "OF COMPLETION",
  "presented_line": "This certificate is proudly presented to",
  "intro_line": "has successfully completed and demonstrated outstanding commitment throughout the",
  "programme_lead": "5-Day Intensive Hands-On Training Programme in",
  "programme_name": "Artificial Intelligence  &  Machine Learning",
  "body_lines": [
    "organised by HexCodePlus — covering AI fundamentals, machine-learning algorithms, data preprocessing,",
    "model training, evaluation techniques and real-world deployment — held over five days of guided practice."
  ],
  "duration_line": "8th June 2025  to  15th June 2025      •      Trivandrum, Kerala, India",
  "signatories": [
    { "name": "Programme Coordinator", "org": "HexCodePlus" },
    { "name": "Director", "org": "HexCodePlus" }
  ],
  "seal_text_top": "HEXCODE+",
  "seal_text_bottom": "CERTIFIED",
  "seal_monogram": "h+",
  "cert_prefix": "HCP-AIML-2025",
  "footer_extra": "hexcodeplus.com      |      Issued June 2025",
  "logo_path": "assets/hexcode_logo.png",
  "watermark": true,
  "watermark_crop": null,
  "palette": {},
  "output_dir": "certificates_out",
  "combined_name": "ALL_Certificates.pdf",
  "zip_name": "Individual_Certificates.zip",
  "recipients": [
    { "name": "Jishnu Raj", "subtitle": "CSE S2" },
    { "name": "Daya Elizabeth Biju", "subtitle": "CSE S4" }
  ]
}
```

### Field notes

- **recipients** — the only required field. Three accepted forms, mixable:
  `"Jishnu Raj"` (string), `["Jishnu Raj", "CSE S2"]` (pair), or
  `{"name": "...", "subtitle": "..."}` (dict). `subtitle` prints in small blue
  caps under the name (department, roll number, team — or omit it).
- **subtitle vs programme** — `subtitle` is per-recipient; `programme_name` is
  the big gold line shared by everyone.
- **signatories** — 1, 2, or 3 entries. Two flank the central seal (the common
  case); three add a centred lower signature. `org` is the small line beneath.
- **cert_prefix** — each certificate is numbered `PREFIX-001`, `PREFIX-002`, …
  in recipient order.
- **logo_path** — full brand lockup, centred at the top. Omit to use the bundled
  HexCodePlus logo. PNG with transparency looks best.
- **watermark / watermark_crop** — a faint centred copy of the logo *symbol*
  sits behind the text. By default the script crops a top-centre square of the
  logo so it grabs the icon, not the wordmark. If your symbol sits elsewhere,
  set `watermark_crop: [x0, y0, x1, y1]` as 0–1 fractions of the trimmed logo.
  Set `watermark: false` to disable.
- **palette** — override any of these hex colours:
  `navy, blue_mid, gold, gold_brt, gold_pale, ivory, ivory_deep, ink, grey_soft`.

## Design (fixed)

Landscape A4. Warm ivory paper with a navy + double-gold frame and hand-drawn
corner flourishes. Typographic hierarchy: **Cinzel** engraved capitals for the
title and programme name, **Great Vibes** script for the recipient's name (the
hero, auto-scaled by length), **EB Garamond** for body copy. A custom vector
gold rosette seal with ribbon tails anchors the signature row. Fonts are bundled
under `assets/fonts/` (all SIL Open Font License) — no system fonts required.

To restyle, edit `palette` (colours) or the copy fields. Structural layout
changes live in `scripts/generate_certificates.py` (`draw_cert`).

## Tips

- For large cohorts the combined PDF is best for a single print job; the ZIP is
  best for emailing individuals.
- Keep `programme_name` to one line (~40 chars) so it stays on one row in
  Cinzel. Put extra detail in `body_lines`.
- Each `body_lines` entry is one centred line — break long sentences yourself at
  natural points; the script does not wrap.
- Use straight typographic dashes (—, •) directly in the JSON for a refined look.

## Dependencies

`reportlab` (PDF), `pypdf` (combined PDF), `pillow` (logo/watermark),
`pdf2image` (preview rendering only). Install with `--break-system-packages` as
shown above.
