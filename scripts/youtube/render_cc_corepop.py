"""COREPOP thumbnail render — duotone accent edge.
Concept: still with GOLD->LIME diagonal gradient accent bar on left edge,
matching thin top edge, dark vignette on right, dark keyline frame, rounded r=16.
Energetic, modern, signature color-pop. Chunky dark HQ/8K pills.
"""
import io
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "corepop"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_corepop.png"

# Brand colors
GOLD = (201, 169, 98)
LIGHT_GOLD = (229, 199, 138)
DARK_GOLD = (168, 139, 74)
LIME = (132, 204, 22)

VID = "JzJrH43etPA"


def fetch_still():
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        url = f"https://i.ytimg.com/vi/{VID}/{q}.jpg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=20).read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            if img.width >= 320:
                print(f"fetched {q} ({img.width}x{img.height})")
                return img
        except Exception as e:
            print(f"failed {q}: {e}")
    raise RuntimeError("no still")


def cover_resize(img, w, h):
    """Resize to cover w x h, center-crop."""
    src_r = img.width / img.height
    dst_r = w / h
    if src_r > dst_r:
        nh = h
        nw = int(h * src_r)
    else:
        nw = w
        nh = int(w / src_r)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def load_font(size, bold=True):
    paths = [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def diagonal_gradient(w, h, c0, c1):
    """Gradient along the main diagonal (top-left -> bottom-right)."""
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    maxd = (w - 1) + (h - 1) if (w > 1 and h > 1) else 1
    for y in range(h):
        for x in range(w):
            t = (x + y) / maxd
            px[x, y] = lerp(c0, c1, t)
    return grad


def main():
    still = fetch_still()
    base = cover_resize(still, W, H).convert("RGBA")

    # --- Right-side dark vignette for contrast ---
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    for x in range(W):
        # only ramp up on the right ~45%
        t = max(0.0, (x - W * 0.55) / (W * 0.45))
        a = int((t ** 1.6) * 150)
        vd.line([(x, 0), (x, H)], fill=a)
    dark = Image.new("RGBA", (W, H), (10, 8, 4, 0))
    dark.putalpha(vig)
    base = Image.alpha_composite(base, dark)

    # subtle global contrast/saturation pop via dark overlay on edges top/bottom
    edge = Image.new("L", (W, H), 0)
    ed = ImageDraw.Draw(edge)
    for y in range(H):
        t_top = max(0.0, (60 - y) / 60) if y < 60 else 0.0
        t_bot = max(0.0, (y - (H - 80)) / 80) if y > H - 80 else 0.0
        a = int(max(t_top, t_bot) * 90)
        ed.line([(0, y), (W, y)], fill=a)
    edl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    edl.putalpha(edge)
    base = Image.alpha_composite(base, edl)

    draw = ImageDraw.Draw(base)

    # --- LEFT accent bar (~24px) with GOLD->LIME diagonal gradient ---
    BAR_W = 24
    left_grad = diagonal_gradient(BAR_W, H, GOLD, LIME)
    base.paste(left_grad, (0, 0))
    # glow to the right of the bar
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([0, 0, BAR_W + 10, H], fill=(*LIME, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    base = Image.alpha_composite(base, glow)
    base.paste(left_grad, (0, 0))  # repaint crisp bar on top of glow

    # --- TOP thin accent edge (~10px), same gradient direction ---
    TOP_H = 10
    top_grad = diagonal_gradient(W, TOP_H, GOLD, LIME)
    base.paste(top_grad, (0, 0))
    # re-establish the top-left corner of the left bar overlapping cleanly
    base.paste(diagonal_gradient(BAR_W, TOP_H + 4, GOLD, lerp(GOLD, LIME, 0.15)), (0, 0))

    draw = ImageDraw.Draw(base)

    # --- Dark keyline frame, rounded r=16 ---
    KL = 3
    draw.rounded_rectangle([KL // 2, KL // 2, W - 1 - KL // 2, H - 1 - KL // 2],
                           radius=16, outline=(18, 16, 12, 255), width=KL)
    # inner subtle gold hairline
    draw.rounded_rectangle([KL + 2, KL + 2, W - 3 - KL, H - 3 - KL],
                           radius=13, outline=(*DARK_GOLD, 110), width=1)

    # --- Helper: chunky dark pill badge ---
    def pill(cx_left, cy_top, text, txt_color, accent):
        f = load_font(46)
        bb = draw.textbbox((0, 0), text, font=f)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        pad_x, pad_y = 26, 14
        pw = tw + pad_x * 2
        ph = th + pad_y * 2
        x0, y0 = cx_left, cy_top
        x1, y1 = x0 + pw, y0 + ph
        # drop shadow
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdr = ImageDraw.Draw(sh)
        sdr.rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6], radius=ph // 2,
                              fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        base.alpha_composite(sh)
        d2 = ImageDraw.Draw(base)
        # pill body (chunky dark)
        d2.rounded_rectangle([x0, y0, x1, y1], radius=ph // 2, fill=(22, 20, 16, 235))
        # accent ring
        d2.rounded_rectangle([x0, y0, x1, y1], radius=ph // 2, outline=(*accent, 255), width=3)
        # top bevel highlight
        d2.arc([x0 + 3, y0 + 3, x1 - 3, y1 - 3], 180, 360, fill=(255, 255, 255, 40), width=2)
        tx = x0 + (pw - tw) // 2 - bb[0]
        ty = y0 + (ph - th) // 2 - bb[1]
        d2.text((tx, ty), text, font=f, fill=txt_color)
        return x1, y1

    # HQ top-left (gold accent), 8K top-right (lime text)
    pill(BAR_W + 22, 22, "HQ", (*LIGHT_GOLD, 255), GOLD)
    # measure 8K width to right-align
    f8 = load_font(46)
    bb8 = draw.textbbox((0, 0), "8K", font=f8)
    w8 = (bb8[2] - bb8[0]) + 52
    pill(W - 24 - w8, 22, "8K", (*LIME, 255), LIME)

    # --- Brand plaque bottom-left: remAIke.IT ---
    bf = load_font(34)
    btxt = "remAIke.IT"
    bbb = draw.textbbox((0, 0), btxt, font=bf)
    btw = bbb[2] - bbb[0]
    bth = bbb[3] - bbb[1]
    bpx, bpy = 22, 12
    bx0 = BAR_W + 22
    by1 = H - 24
    by0 = by1 - (bth + bpy * 2)
    bx1 = bx0 + btw + bpx * 2
    # shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdr = ImageDraw.Draw(sh)
    sdr.rounded_rectangle([bx0 + 3, by0 + 5, bx1 + 3, by1 + 5], radius=14, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    base.alpha_composite(sh)
    d3 = ImageDraw.Draw(base)
    d3.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(20, 18, 14, 230))
    # gradient accent left edge of plaque
    pg = diagonal_gradient(6, by1 - by0, GOLD, LIME)
    base.paste(pg, (bx0 + 2, by0))
    d3.rounded_rectangle([bx0, by0, bx1, by1], radius=14, outline=(*DARK_GOLD, 200), width=2)
    tx = bx0 + bpx + 4 - bbb[0]
    ty = by0 + bpy - bbb[1]
    # text: "remAIke" gold, ".IT" lime
    d3.text((tx, ty), "remAIke", font=bf, fill=(*LIGHT_GOLD, 255))
    wpre = draw.textbbox((0, 0), "remAIke", font=bf)[2]
    d3.text((tx + wpre, ty), ".IT", font=bf, fill=(*LIME, 255))

    out = base.convert("RGB")
    out.save(OUT, "PNG")
    print(f"saved {OUT} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
