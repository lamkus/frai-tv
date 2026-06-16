# -*- coding: utf-8 -*-
"""
AURUM HALO thumbnail concept (KEY=aurumhalo)
Borderless rounded still floating on YouTube white, lifted by a soft gold drop-glow
plus a dark grounding shadow, framed by a thin gold rim + dark keyline stack.
Native-style HQ / 8K dark pills with gold text.
"""
import io
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------- constants
W, H = 1280, 720
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_aurumhalo.png"

CANVAS   = (249, 249, 249)      # YouTube feed white #f9f9f9
GOLD     = (201, 169, 98)       # #c9a962
GOLD_LT  = (229, 199, 138)      # #e5c78a
GOLD_DK  = (168, 139, 74)       # #a88b4a
LIME     = (132, 204, 22)       # #84cc16
INK      = (18, 18, 20)

VIDEO_ID = "JzJrH43etPA"


# ---------------------------------------------------------------- helpers
def load_font(size, bold=True):
    for path in (r"C:\Windows\Fonts\impact.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fetch_test_frame():
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        url = "https://i.ytimg.com/vi/%s/%s.jpg" % (VIDEO_ID, q)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            print("fetched", q, img.size)
            return img
        except Exception as e:  # noqa
            print("miss", q, e)
    # fallback solid frame
    return Image.new("RGB", (1280, 720), (40, 40, 48))


def cover_resize(img, tw, th):
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return img.crop((x, y, x + tw, y + th))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def text_size(draw, txt, font):
    b = draw.textbbox((0, 0), txt, font=font)
    return b[2] - b[0], b[3] - b[1]


def make_pill(text, font, pad_x=18, pad_y=10, txt_col=GOLD_LT,
              bg=(16, 16, 18, 225), rim=GOLD):
    """Native-style dark rounded pill with gold text + subtle gold rim."""
    tmp = Image.new("RGBA", (10, 10))
    td = ImageDraw.Draw(tmp)
    tw, th = text_size(td, text, font)
    w = tw + pad_x * 2
    h = th + pad_y * 2
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    r = h // 2
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=bg)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, outline=rim + (235,), width=2)
    # text (slight ascender offset correction)
    d.text(((w - tw) // 2, (h - th) // 2 - 2), text, font=font, fill=txt_col + (255,))
    return pill


# ---------------------------------------------------------------- build
def main():
    base = Image.new("RGB", (W, H), CANVAS).convert("RGBA")

    # subtle vertical tint on the canvas so the card reads as "floating on feed"
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gp = grad.load()
    for y in range(H):
        t = y / (H - 1)
        # top a touch brighter, bottom a touch cooler/darker -> depth
        v = int(8 * t)
        gp_row = (0, 0, 0, v)
        for x in range(W):
            gp[x, y] = gp_row
    base = Image.alpha_composite(base, grad)

    # ---- card geometry (the floating still)
    margin_x = 150
    margin_top = 96
    card_w = W - margin_x * 2          # 980
    card_h = int(card_w * 9 / 16)      # 551
    card_x = (W - card_w) // 2         # 150
    card_y = margin_top                # 96
    radius = 30

    # ---- 1) DARK grounding shadow (below, blur 20, y+10)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [card_x + 6, card_y + 10, card_x + card_w - 6, card_y + card_h + 10],
        radius=radius, fill=(20, 16, 8, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base = Image.alpha_composite(base, shadow)

    # ---- 2) GOLD drop-GLOW (behind, blur 26, offset 0)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # slightly larger than card so the halo bleeds around all edges
    gpad = 10
    gd.rounded_rectangle(
        [card_x - gpad, card_y - gpad, card_x + card_w + gpad, card_y + card_h + gpad],
        radius=radius + gpad, fill=GOLD + (190,))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    base = Image.alpha_composite(base, glow)

    # second tighter, brighter glow pass for a premium core bloom
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g2 = ImageDraw.Draw(glow2)
    g2.rounded_rectangle(
        [card_x - 2, card_y - 2, card_x + card_w + 2, card_y + card_h + 2],
        radius=radius, fill=GOLD_LT + (140,))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(14))
    base = Image.alpha_composite(base, glow2)

    # ---- 3) the STILL (rounded, slightly darkened)
    frame = fetch_test_frame()
    still = cover_resize(frame, card_w, card_h)
    # darken slightly for the "premium dim" look
    dark = Image.new("RGB", (card_w, card_h), (0, 0, 0))
    still = Image.blend(still, dark, 0.16).convert("RGBA")
    # gentle top-light vignette so the rim reads
    vig = Image.new("L", (card_w, card_h), 0)
    vd = ImageDraw.Draw(vig)
    vd.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=radius, fill=0)
    # darken edges a hair
    edge = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=radius,
                         outline=(0, 0, 0, 90), width=14)
    edge = edge.filter(ImageFilter.GaussianBlur(10))
    still = Image.alpha_composite(still, edge)

    mask = rounded_mask((card_w, card_h), radius)
    base.paste(still, (card_x, card_y), mask)

    # ---- 4) thin gold rim + dark keyline stack around the still
    rim = ImageDraw.Draw(base)
    # outermost: dark keyline
    rim.rounded_rectangle(
        [card_x - 3, card_y - 3, card_x + card_w + 2, card_y + card_h + 2],
        radius=radius + 3, outline=(10, 8, 4, 255), width=2)
    # main gold rim
    rim.rounded_rectangle(
        [card_x - 1, card_y - 1, card_x + card_w, card_y + card_h],
        radius=radius + 1, outline=GOLD, width=3)
    # inner light-gold highlight keyline (top-left bias feel)
    rim.rounded_rectangle(
        [card_x + 2, card_y + 2, card_x + card_w - 3, card_y + card_h - 3],
        radius=radius - 1, outline=GOLD_LT + (180,), width=1)
    # inner dark keyline to seat it
    rim.rounded_rectangle(
        [card_x + 4, card_y + 4, card_x + card_w - 5, card_y + card_h - 5],
        radius=radius - 2, outline=(0, 0, 0, 120), width=1)

    # ---- 5) badges: native dark pills, gold text  (HQ top-left, 8K top-right)
    pill_font = load_font(34)
    hq = make_pill("HQ", pill_font, txt_col=GOLD_LT, rim=GOLD)
    k8 = make_pill("8K", pill_font, txt_col=GOLD_LT, rim=GOLD)
    pad = 18
    base.alpha_composite(hq, (card_x + pad, card_y + pad))
    base.alpha_composite(k8, (card_x + card_w - k8.width - pad, card_y + pad))

    # ---- 6) brand plaque "remAIke.IT" — small gold-rimmed pill under the card,
    #         left-aligned, kept clear of the bottom-right duration-pill zone.
    brand_font = load_font(40)
    brand = make_pill("remAIke.IT", brand_font, pad_x=22, pad_y=12,
                      txt_col=GOLD_LT, bg=(14, 14, 16, 235), rim=GOLD)
    by = card_y + card_h + 22
    base.alpha_composite(brand, (card_x + 2, by))

    # tiny lime accent dot to the right of the plaque (brand pop)
    bd = ImageDraw.Draw(base)
    dot_cx = card_x + 2 + brand.width + 26
    dot_cy = by + brand.height // 2
    bd.ellipse([dot_cx - 9, dot_cy - 9, dot_cx + 9, dot_cy + 9], fill=LIME)
    bd.ellipse([dot_cx - 9, dot_cy - 9, dot_cx + 9, dot_cy + 9],
               outline=(255, 255, 255, 230), width=2)

    # ---------------------------------------------------------------- save
    out = base.convert("RGB")
    out.save(OUT, "PNG")
    print("saved", OUT, out.size)


if __name__ == "__main__":
    main()
