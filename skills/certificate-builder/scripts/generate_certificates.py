#!/usr/bin/env python3
"""
Certificate Builder — generates elegant per-recipient PDF certificates.

Design: warm ivory paper, antique-gold + ink-navy palette, Cinzel display caps,
Great Vibes script recipient name, EB Garamond body, ornamental corner flourishes,
a vector gold seal, and an optional faint centered logo watermark.

Usage:
    python generate_certificates.py config.json

The config JSON drives everything (event details + recipient list). See the
"CONFIG SCHEMA" section in SKILL.md for all fields and defaults. Run with no
argument to emit a sample config to ./sample_config.json.
"""
import sys, os, io, json, math, zipfile

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR   = os.path.join(SCRIPT_DIR, "..", "assets", "fonts")

# ── Default palette (override any via config["palette"]) ──────────────────
DEFAULT_PALETTE = {
    "navy":      "#16213E",
    "blue_mid":  "#2C5282",
    "gold":      "#B08D2F",
    "gold_brt":  "#C9A648",
    "gold_pale": "#E7D7A8",
    "ivory":     "#FBF8F1",
    "ivory_deep":"#F4EEE0",
    "ink":       "#2A2A33",
    "grey_soft": "#6B6B70",
}

# ── Default event copy (override via config) ──────────────────────────────
DEFAULTS = {
    "title":            "CERTIFICATE",
    "subtitle":         "OF COMPLETION",
    "presented_line":   "This certificate is proudly presented to",
    "intro_line":       "has successfully completed and demonstrated outstanding commitment throughout the",
    "programme_lead":   "5-Day Intensive Hands-On Training Programme in",
    "programme_name":   "Artificial Intelligence  &  Machine Learning",
    "body_lines": [
        "organised by HexCodePlus \u2014 covering AI fundamentals, machine-learning algorithms, data preprocessing,",
        "model training, evaluation techniques and real-world deployment \u2014 held over five days of guided practice.",
    ],
    "duration_line":    "8th June 2025  to  15th June 2025      \u2022      Trivandrum, Kerala, India",
    "signatories": [
        {"name": "Programme Coordinator", "org": "HexCodePlus"},
        {"name": "Director",              "org": "HexCodePlus"},
    ],
    "seal_text_top":    "HEXCODE+",
    "seal_text_bottom": "CERTIFIED",
    "seal_monogram":    "h+",
    "cert_prefix":      "HCP-AIML-2025",
    "footer_extra":     "hexcodeplus.com      |      Issued June 2025",
    "logo_path":        None,        # full brand lockup, centered top
    "watermark":        True,        # faint centered logo behind text
    "output_dir":       "certificates_out",
    "combined_name":    "ALL_Certificates.pdf",
    "zip_name":         "Individual_Certificates.zip",
}


def register_fonts():
    pdfmetrics.registerFont(TTFont("Cinzel",      os.path.join(FONT_DIR, "Cinzel-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Cinzel-Bold", os.path.join(FONT_DIR, "Cinzel-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Script",      os.path.join(FONT_DIR, "GreatVibes-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Garamond",    os.path.join(FONT_DIR, "EBGaramond-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Garamond-SB", os.path.join(FONT_DIR, "EBGaramond-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Garamond-It", os.path.join(FONT_DIR, "EBGaramond-Italic-Static.ttf")))


def make_watermark(logo_path, crop_frac=None):
    """Return (ImageReader, size) of a faint version of the logo's symbol mark.

    The symbol mark is assumed to sit top-centre (the most common lockup), so by
    default we crop a top-centre square — this avoids picking up wordmark/tagline
    text. Override with config["watermark_crop"] = [x0,y0,x1,y1] as 0..1 fractions
    of the trimmed logo if your mark sits elsewhere.
    """
    if not (HAVE_PIL and logo_path and os.path.exists(logo_path)):
        return None
    base = Image.open(logo_path).convert("RGBA")
    base = base.crop(base.getbbox())
    w, h = base.size
    if crop_frac and len(crop_frac) == 4:
        x0, y0, x1, y1 = crop_frac
        mark = base.crop((int(w*x0), int(h*y0), int(w*x1), int(h*y1)))
    else:
        side = min(w, int(h * 0.60))            # top-centre square
        x0 = max(0, (w - side) // 2)
        mark = base.crop((x0, 0, x0 + side, side))
    bb = mark.getbbox()
    if bb: mark = mark.crop(bb)
    r, g, b, a = mark.split()
    a = a.point(lambda x: int(x * 0.06))
    faint = Image.merge("RGBA", (r, g, b, a))
    buf = io.BytesIO(); faint.save(buf, format="PNG"); buf.seek(0)
    return ImageReader(buf), faint.size


def trimmed_logo(logo_path):
    if not (logo_path and os.path.exists(logo_path)):
        return None, None
    if HAVE_PIL:
        img = Image.open(logo_path).convert("RGBA")
        img = img.crop(img.getbbox())
        buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        return ImageReader(buf), img.size
    return ImageReader(logo_path), None


# ── Ornaments ─────────────────────────────────────────────────────────────
def corner_flourish(c, P, x, y, flip_x, flip_y, size=20*mm):
    c.saveState(); c.translate(x, y); c.scale(flip_x, flip_y)
    c.setStrokeColor(P["gold"]); c.setLineWidth(1.4)
    p = c.beginPath(); p.moveTo(size, 1.5*mm)
    p.curveTo(size*0.45, 1.5*mm, 1.5*mm, size*0.45, 1.5*mm, size)
    c.drawPath(p, stroke=1, fill=0)
    c.setLineWidth(0.6)
    p2 = c.beginPath(); p2.moveTo(size, 4.0*mm)
    p2.curveTo(size*0.5, 4.0*mm, 4.0*mm, size*0.5, 4.0*mm, size)
    c.drawPath(p2, stroke=1, fill=0)
    c.setFillColor(P["gold_brt"]); c.circle(3.2*mm, 3.2*mm, 1.0*mm, fill=1, stroke=0)
    c.setStrokeColor(P["gold_brt"]); c.setLineWidth(0.8)
    for t in (0.30, 0.55, 0.80):
        ang = t * math.pi/2
        lx = 1.5*mm + (size-1.5*mm)*math.cos(ang)
        ly = 1.5*mm + (size-1.5*mm)*math.sin(ang)
        c.line(lx, ly, lx-2.0*mm*math.cos(ang-0.5), ly-2.0*mm*math.sin(ang-0.5))
    c.restoreState()


def gold_seal(c, P, cx, cy, r, mono, t_top, t_bot):
    c.saveState()
    teeth = 28
    c.setFillColor(P["gold"]); p = c.beginPath()
    for i in range(teeth*2+1):
        ang = (i/(teeth*2)) * 2*math.pi
        rr = r if i % 2 == 0 else r*0.93
        x = cx + rr*math.cos(ang); y = cy + rr*math.sin(ang)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(P["navy"]); c.circle(cx, cy, r*0.82, fill=1, stroke=0)
    c.setStrokeColor(P["gold_brt"]); c.setLineWidth(1.2); c.circle(cx, cy, r*0.74, fill=0, stroke=1)
    c.setLineWidth(0.5); c.circle(cx, cy, r*0.66, fill=0, stroke=1)
    c.setFillColor(P["gold_brt"]); hp = c.beginPath(); hr = r*0.34
    for i in range(7):
        ang = math.pi/6 + i*(2*math.pi/6)
        x = cx + hr*math.cos(ang); y = cy + hr*math.sin(ang)
        (hp.moveTo if i == 0 else hp.lineTo)(x, y)
    hp.close(); c.drawPath(hp, fill=1, stroke=0)
    c.setFillColor(P["navy"]); c.setFont("Cinzel-Bold", 13)
    c.drawCentredString(cx, cy - 4.6, mono)
    c.setFillColor(P["gold_pale"]); c.setFont("Cinzel", 5.2)
    c.drawCentredString(cx, cy - r*0.55, t_bot)
    c.drawCentredString(cx, cy + r*0.46, t_top)
    c.setFillColor(P["gold"])
    for dx in (-1, 1):
        rp = c.beginPath()
        rp.moveTo(cx + dx*r*0.45, cy - r*0.72)
        rp.lineTo(cx + dx*r*0.70, cy - r*1.28)
        rp.lineTo(cx + dx*r*0.38, cy - r*1.16)
        rp.lineTo(cx + dx*r*0.16, cy - r*0.78)
        rp.close(); c.drawPath(rp, fill=1, stroke=0)
    c.restoreState()


def draw_cert(c, cfg, P, logo_ir, logo_size, wm_ir, wm_size, name, subtitle, cert_num):
    W, H = landscape(A4)
    cx = W/2

    # Background layers
    c.setFillColor(P["ivory"]);      c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(P["ivory_deep"]); c.rect(7*mm, 7*mm, W-14*mm, H-14*mm, fill=1, stroke=0)
    c.setFillColor(P["ivory"]);      c.rect(9*mm, 9*mm, W-18*mm, H-18*mm, fill=1, stroke=0)

    # Watermark
    if wm_ir is not None:
        ww = float(cfg.get("watermark_size_mm", 70))*mm; iw, ih = wm_size; wh = ww*ih/iw
        c.drawImage(wm_ir, cx-ww/2, H/2-wh/2-6*mm, width=ww, height=wh, mask='auto')

    # Borders
    c.setStrokeColor(P["navy"]); c.setLineWidth(3)
    c.rect(9*mm, 9*mm, W-18*mm, H-18*mm, fill=0, stroke=1)
    c.setStrokeColor(P["gold"]); c.setLineWidth(1.4)
    c.rect(12*mm, 12*mm, W-24*mm, H-24*mm, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.rect(13.2*mm, 13.2*mm, W-26.4*mm, H-26.4*mm, fill=0, stroke=1)

    # Corner flourishes
    m = 14*mm
    corner_flourish(c, P, m,   m,   +1, +1)
    corner_flourish(c, P, W-m, m,   -1, +1)
    corner_flourish(c, P, m,   H-m, +1, -1)
    corner_flourish(c, P, W-m, H-m, -1, -1)

    # Brand lockup (logo) or text fallback
    if logo_ir is not None:
        lw = 58*mm; iw, ih = logo_size; lh = lw*ih/iw
        logo_top_y = H - 20*mm - lh
        c.drawImage(logo_ir, cx-lw/2, logo_top_y, width=lw, height=lh,
                    preserveAspectRatio=True, mask='auto')
        fl_y = logo_top_y - 3*mm
    else:
        c.setFillColor(P["navy"]); c.setFont("Cinzel-Bold", 30)
        c.drawCentredString(cx, H - 28*mm, cfg.get("brand_text", "HEXCODE+"))
        fl_y = H - 36*mm

    # Gold flourish divider under brand
    c.setStrokeColor(P["gold"]); c.setLineWidth(0.8)
    c.line(cx-40*mm, fl_y, cx-6*mm, fl_y)
    c.line(cx+6*mm,  fl_y, cx+40*mm, fl_y)
    c.setFillColor(P["gold"]);     c.circle(cx, fl_y, 1.3*mm, fill=1, stroke=0)
    c.setFillColor(P["gold_brt"]); c.circle(cx-6*mm, fl_y, 0.7*mm, fill=1, stroke=0)
    c.circle(cx+6*mm, fl_y, 0.7*mm, fill=1, stroke=0)

    # Title
    title_y = fl_y - 11*mm
    c.setFillColor(P["navy"]); c.setFont("Cinzel-Bold", 25)
    c.drawCentredString(cx, title_y, cfg["title"])
    c.setFillColor(P["gold"]); c.setFont("Cinzel", 11)
    c.drawCentredString(cx, title_y - 7.5*mm, "  ".join(list(cfg["subtitle"])))

    # Presented line
    pres_y = title_y - 17*mm
    c.setFillColor(P["grey_soft"]); c.setFont("Garamond-It", 13)
    c.drawCentredString(cx, pres_y, cfg["presented_line"])

    # Name (script hero, auto-scaled)
    name_fs = 46
    if len(name) > 18: name_fs = 40
    if len(name) > 26: name_fs = 33
    if len(name) > 34: name_fs = 27
    name_y = pres_y - 16*mm
    c.setFillColor(P["navy"]); c.setFont("Script", name_fs)
    c.drawCentredString(cx, name_y, name)

    nw = pdfmetrics.stringWidth(name, "Script", name_fs)
    rule_w = max(nw*0.62, 55*mm); ry = name_y - 4.5*mm
    c.setStrokeColor(P["gold"]); c.setLineWidth(0.8)
    c.line(cx-rule_w/2, ry, cx-3*mm, ry); c.line(cx+3*mm, ry, cx+rule_w/2, ry)
    c.setFillColor(P["gold"]); c.saveState(); c.translate(cx, ry); c.rotate(45)
    c.rect(-1.1*mm, -1.1*mm, 2.2*mm, 2.2*mm, fill=1, stroke=0); c.restoreState()

    if subtitle:
        c.setFillColor(P["blue_mid"]); c.setFont("Garamond-SB", 11.5)
        c.drawCentredString(cx, name_y - 11*mm, subtitle)

    # Body
    y = name_y - 21*mm
    c.setFillColor(P["ink"]); c.setFont("Garamond", 12.5)
    c.drawCentredString(cx, y, cfg["intro_line"]); y -= 7*mm
    c.setFillColor(P["navy"]); c.setFont("Garamond-SB", 14)
    c.drawCentredString(cx, y, cfg["programme_lead"]); y -= 7*mm
    c.setFillColor(P["gold"]); c.setFont("Cinzel-Bold", 14.5)
    c.drawCentredString(cx, y, cfg["programme_name"]); y -= 7.5*mm
    c.setFillColor(P["ink"]); c.setFont("Garamond", 12)
    for line in cfg["body_lines"]:
        c.drawCentredString(cx, y, line); y -= 6.2*mm
    c.setFillColor(P["grey_soft"]); c.setFont("Garamond-It", 11.5)
    c.drawCentredString(cx, y, cfg["duration_line"])

    # Seal
    gold_seal(c, P, cx, 33*mm, 10.5*mm,
              cfg["seal_monogram"], cfg["seal_text_top"], cfg["seal_text_bottom"])

    # Signatures (1-3 supported; positioned to flank the seal)
    sigs = cfg["signatories"][:3]
    sig_line_y = 34*mm
    if len(sigs) == 1:
        xs = [cx]
    elif len(sigs) == 2:
        xs = [14*mm + (cx-14*mm)*0.40, cx + (W-14*mm-cx)*0.60]
    else:
        xs = [14*mm + (cx-14*mm)*0.32, cx, cx + (W-14*mm-cx)*0.68]
        sig_line_y = 30*mm  # drop the middle so it clears the seal
    for sx, sig in zip(xs, sigs):
        ly = sig_line_y
        if len(sigs) == 3 and abs(sx-cx) < 1:  # middle one lower
            continue_line = True
        c.setStrokeColor(P["navy"]); c.setLineWidth(0.8)
        c.line(sx-28*mm, ly, sx+28*mm, ly)
        c.setFillColor(P["navy"]); c.setFont("Garamond-SB", 10.5)
        c.drawCentredString(sx, ly-5*mm, sig.get("name", ""))
        if sig.get("org"):
            c.setFillColor(P["grey_soft"]); c.setFont("Garamond", 8.5)
            c.drawCentredString(sx, ly-9.5*mm, sig["org"])

    # Footer
    c.setFillColor(P["grey_soft"]); c.setFont("Garamond", 8.5)
    cert_no = f"Certificate No.  {cfg['cert_prefix']}-{cert_num:03d}"
    extra = cfg.get("footer_extra", "")
    footer = cert_no + (f"      |      {extra}" if extra else "")
    c.drawCentredString(cx, 15.5*mm, footer)


def load_config(path):
    with open(path) as f:
        user = json.load(f)
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in user.items() if k != "recipients"})
    cfg["recipients"] = user.get("recipients", [])
    # Palette merge
    pal = dict(DEFAULT_PALETTE)
    pal.update(user.get("palette", {}))
    cfg["_palette"] = {k: HexColor(v) for k, v in pal.items()}
    return cfg


def normalise_recipients(recips):
    """Accept list of strings, [name, subtitle] pairs, or {name, subtitle} dicts."""
    out = []
    for r in recips:
        if isinstance(r, str):
            out.append((r, ""))
        elif isinstance(r, (list, tuple)):
            out.append((r[0], r[1] if len(r) > 1 else ""))
        elif isinstance(r, dict):
            out.append((r.get("name", ""), r.get("subtitle", r.get("dept", ""))))
    return out


def main():
    if len(sys.argv) < 2:
        sample = {
            "title": "CERTIFICATE", "subtitle": "OF COMPLETION",
            "programme_lead": "5-Day Intensive Hands-On Training Programme in",
            "programme_name": "Artificial Intelligence  &  Machine Learning",
            "body_lines": DEFAULTS["body_lines"],
            "duration_line": DEFAULTS["duration_line"],
            "signatories": DEFAULTS["signatories"],
            "cert_prefix": "HCP-AIML-2025",
            "logo_path": "logo.png", "watermark": True,
            "output_dir": "certificates_out",
            "recipients": [
                {"name": "Jishnu Raj", "subtitle": "CSE S2"},
                {"name": "Daya Elizabeth Biju", "subtitle": "CSE S4"},
            ],
        }
        with open("sample_config.json", "w") as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)
        print("No config supplied. Wrote sample_config.json — edit it and rerun:")
        print("    python generate_certificates.py sample_config.json")
        return

    cfg = load_config(sys.argv[1])
    P = cfg["_palette"]
    register_fonts()

    logo_path = cfg.get("logo_path")
    if not logo_path:
        # Fall back to the bundled default brand logo
        bundled = os.path.join(SCRIPT_DIR, "..", "assets", "hexcode_logo.png")
        if os.path.exists(bundled):
            logo_path = bundled
            cfg["logo_path"] = bundled
    logo_ir, logo_size = trimmed_logo(logo_path)
    wm_ir, wm_size = (None, None)
    if cfg.get("watermark") and cfg.get("logo_path"):
        res = make_watermark(cfg["logo_path"], cfg.get("watermark_crop"))
        if res: wm_ir, wm_size = res

    recipients = normalise_recipients(cfg["recipients"])
    if not recipients:
        print("ERROR: config has no recipients."); sys.exit(1)

    out_dir = cfg["output_dir"]; os.makedirs(out_dir, exist_ok=True)
    pdf_paths = []
    for i, (name, subtitle) in enumerate(recipients, start=1):
        safe = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in name).strip().replace(" ", "_")
        path = os.path.join(out_dir, f"{i:02d}_{safe}.pdf")
        c = rl_canvas.Canvas(path, pagesize=landscape(A4))
        draw_cert(c, cfg, P, logo_ir, logo_size, wm_ir, wm_size, name, subtitle, i)
        c.save(); pdf_paths.append(path)
        print(f"  [{i:02d}] {name}")

    # Combined PDF
    try:
        from pypdf import PdfWriter, PdfReader
        w = PdfWriter()
        for p in pdf_paths: w.add_page(PdfReader(p).pages[0])
        combined = os.path.join(out_dir, cfg["combined_name"])
        with open(combined, "wb") as f: w.write(f)
        print(f"\nCombined : {combined}")
    except ImportError:
        print("\n(pypdf not installed — skipped combined PDF)")

    # ZIP
    zip_path = os.path.join(out_dir, cfg["zip_name"])
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in pdf_paths: zf.write(p, os.path.basename(p))
    print(f"ZIP      : {zip_path}\nDone — {len(recipients)} certificates.")


if __name__ == "__main__":
    main()
