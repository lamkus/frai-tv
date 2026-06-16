# -*- coding: utf-8 -*-
"""
HOLOLAB SCAN thumbnail render for remAIke.IT
KEY=hololab  -> D:\remaike.TV\thumbnails_pilot\CC_hololab.png  (1280x720)
"""
import os
import io
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = r"D:\remaike.TV\thumbnails_pilot"
OUT_PATH = os.path.join(OUT_DIR, "CC_hololab.png")
W, H = 1280, 720

# Brand colors
GOLD = (201, 169, 98)
LIGHT_GOLD = (229, 199, 138)
DARK_GOLD = (168, 139, 74)
LIME = (132, 204, 22)
CYAN = (120, 230, 255)
CYAN_BRIGHT = (200, 250, 255)

VID = "JzJrH43etPA"


def fetch_test_frame():
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        url = f"https://i.ytimg.com/vi/{VID}/{q}.jpg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            print(f"[ok] fetched {q} ({img.size})")
            return img
        except Exception as e:
            print(f"[skip] {q}: {e}")
    raise RuntimeError("Could not fetch any test frame")


def load_font(size, bold=True):
    for path in (r"C:\Windows\Fonts\impact.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def cover_resize(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def tint_layer(base, color, alpha):
    overlay = Image.new("RGB", base.size, color)
    return Image.blend(base, overlay, alpha)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    frame = fetch_test_frame()
    base = cover_resize(frame, W, H).convert("RGB")

    # Cyan/gold tint: slightly desaturate then tint cyan, add gold warmth
    base = tint_layer(base, (30, 60, 80), 0.18)   # cyan cast
    base = tint_layer(base, GOLD, 0.07)           # subtle gold warmth

    # Slight darkening vignette for HUD legibility
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-W * 0.25, -H * 0.25, W * 1.25, H * 1.25), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), (4, 10, 16))
    base = Image.composite(base, dark, vig)

    img = base.convert("RGBA")

    # ---- Chromatic aberration at edges ----
    edge_mask = Image.new("L", (W, H), 0)
    em = ImageDraw.Draw(edge_mask)
    em.rectangle((0, 0, W, H), fill=255)
    em.rounded_rectangle((70, 70, W - 70, H - 70), radius=40, fill=0)
    edge_mask = edge_mask.filter(ImageFilter.GaussianBlur(40))
    r, g, b, a = img.split()
    r_sh = Image.merge("RGBA", (r, g, b, a)).transform(
        (W, H), Image.AFFINE, (1, 0, -4, 0, 1, 0), resample=Image.BILINEAR)
    b_sh = Image.merge("RGBA", (r, g, b, a)).transform(
        (W, H), Image.AFFINE, (1, 0, 4, 0, 1, 0), resample=Image.BILINEAR)
    rr = r_sh.split()[0]
    bb = b_sh.split()[2]
    chroma = Image.merge("RGBA", (rr, g, bb, a))
    img = Image.composite(chroma, img, edge_mask)

    # ---- Hologram horizontal scanlines (subtle, full frame) ----
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 3):
        sd.line((0, y, W, y), fill=(120, 200, 230, 16))
    img = Image.alpha_composite(img, scan)

    draw = ImageDraw.Draw(img)

    # ---- SCAN BEAM (bright cyan-white horizontal gradient line) ~1/3 down ----
    beam_y = int(H * 0.34)
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    glow_h = 60
    for dy in range(-glow_h, glow_h + 1):
        t = 1 - (abs(dy) / glow_h)
        t = max(0.0, t)
        inten = int(150 * (t ** 2.2))
        col = (
            int(120 + 80 * t),
            int(220 + 30 * t),
            255,
            inten,
        )
        bd.line((0, beam_y + dy, W, beam_y + dy), fill=col)
    beam = beam.filter(ImageFilter.GaussianBlur(2))
    bd2 = ImageDraw.Draw(beam)
    # bright core line
    bd2.line((0, beam_y, W, beam_y), fill=(*CYAN_BRIGHT, 240), width=2)
    bd2.line((0, beam_y - 1, W, beam_y - 1), fill=(255, 255, 255, 180), width=1)
    # leading bright dot sweeping
    dot_x = int(W * 0.78)
    bd2.ellipse((dot_x - 6, beam_y - 6, dot_x + 6, beam_y + 6),
                fill=(255, 255, 255, 230))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img)

    # ---- HUD corner brackets in GOLD ----
    def corner(cx, cy, dx, dy, length=64, t=4):
        col = LIGHT_GOLD
        draw.line((cx, cy, cx + dx * length, cy), fill=col, width=t)
        draw.line((cx, cy, cx, cy + dy * length), fill=col, width=t)
        # inner thin accent
        draw.line((cx + dx * 10, cy + dy * 10, cx + dx * (length - 6), cy + dy * 10),
                  fill=(*GOLD, 255), width=1)

    m = 40
    corner(m, m, 1, 1)
    corner(W - m, m, -1, 1)
    corner(m, H - m, 1, -1)
    corner(W - m, H - m, -1, -1)

    # Thin full HUD frame
    draw.rounded_rectangle((m, m, W - m, H - m), radius=10, outline=(*GOLD, 110), width=1)

    # ---- Tick marks along top and bottom edges ----
    for x in range(m + 90, W - m - 90, 36):
        long = (x // 36) % 4 == 0
        ln = 14 if long else 7
        draw.line((x, m + 2, x, m + 2 + ln), fill=(*GOLD, 150), width=1)
        draw.line((x, H - m - 2, x, H - m - 2 - ln), fill=(*GOLD, 150), width=1)
    # Tick marks along left/right
    for y in range(m + 90, H - m - 90, 36):
        long = (y // 36) % 4 == 0
        ln = 14 if long else 7
        draw.line((m + 2, y, m + 2 + ln, y), fill=(*GOLD, 150), width=1)
        draw.line((W - m - 2, y, W - m - 2 - ln, y), fill=(*GOLD, 150), width=1)

    # ---- Readout text ----
    f_read = load_font(26)
    f_small = load_font(20)
    readout = "8K • RESTORED • remAIke.IT"
    draw.text((m + 80, m + 18), readout, font=f_read, fill=LIGHT_GOLD)

    # small scan label near beam
    draw.text((m + 14, beam_y + 14), "SCAN ▸ ACTIVE", font=f_small, fill=CYAN_BRIGHT)
    draw.text((W - m - 200, beam_y - 36), "RES 7680×4320", font=f_small, fill=(*CYAN, 220))

    # Brand plaque bottom-left (keep bottom-right free for duration pill)
    plaque_w, plaque_h = 196, 50
    px, py = m + 6, H - m - plaque_h - 6
    plaque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plaque)
    pd.rounded_rectangle((px, py, px + plaque_w, py + plaque_h),
                         radius=10, fill=(10, 16, 22, 200), outline=(*GOLD, 255), width=2)
    img = Image.alpha_composite(img, plaque)
    draw = ImageDraw.Draw(img)
    f_brand = load_font(30)
    draw.text((px + 16, py + 10), "remAIke.IT", font=f_brand, fill=LIGHT_GOLD)

    # ---- HUD chips: HQ (top-left) and 8K (top-right) ----
    def hud_chip(text, anchor_x, anchor_y, align_right=False, accent=GOLD):
        f = load_font(34)
        tw = draw.textlength(text, font=f)
        cw = int(tw + 38)
        ch = 52
        if align_right:
            x0 = anchor_x - cw
        else:
            x0 = anchor_x
        y0 = anchor_y
        chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(chip)
        cd.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=8,
                             fill=(8, 14, 20, 215), outline=(*accent, 255), width=2)
        # corner notch detail
        cd.line((x0 + 6, y0 + 6, x0 + 18, y0 + 6), fill=(*CYAN, 220), width=2)
        cd.line((x0 + cw - 18, y0 + ch - 6, x0 + cw - 6, y0 + ch - 6),
                fill=(*CYAN, 220), width=2)
        return chip, f, text, x0, y0, cw, ch

    # HQ top-left (inside brackets)
    hq_chip, hqf, hqt, hx, hy, hcw, hch = hud_chip("HQ", m + 80, m + 60, accent=GOLD)
    img = Image.alpha_composite(img, hq_chip)
    draw = ImageDraw.Draw(img)
    draw.text((hx + 19, hy + 8), "HQ", font=hqf, fill=LIGHT_GOLD)

    # 8K top-right
    k_chip, kf, kt, kx, ky, kcw, kch = hud_chip("8K", W - m - 80, m + 60,
                                                align_right=True, accent=CYAN)
    img = Image.alpha_composite(img, k_chip)
    draw = ImageDraw.Draw(img)
    draw.text((kx + 19, ky + 8), "8K", font=kf, fill=CYAN_BRIGHT)

    # final subtle outer gold frame glow already; flatten
    final = img.convert("RGB")
    final.save(OUT_PATH, "PNG")
    print(f"[saved] {OUT_PATH}  size={final.size}")
    return OUT_PATH


if __name__ == "__main__":
    main()
