import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

KEY = "nativechrome"
OUT_DIR = r"D:\remaike.TV\thumbnails_pilot"
OUT_PATH = os.path.join(OUT_DIR, f"CC_{KEY}.png")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1280, 720

# Brand colors
GOLD = (201, 169, 98)
LIGHT_GOLD = (229, 199, 138)
DARK_GOLD = (168, 139, 74)
LIME = (132, 204, 22)

# ---- Fetch test still ----
VID = "JzJrH43etPA"
still = None
for q in ("maxresdefault", "sddefault", "hqdefault"):
    try:
        url = f"https://i.ytimg.com/vi/{VID}/{q}.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        from io import BytesIO
        still = Image.open(BytesIO(data)).convert("RGB")
        print(f"Fetched {q}: {still.size}")
        break
    except Exception as e:
        print(f"  {q} failed: {e}")

if still is None:
    still = Image.new("RGB", (1280, 720), (40, 40, 48))

# Cover-fit the still to WxH
sw, sh = still.size
scale = max(W / sw, H / sh)
nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
still = still.resize((nw, nh), Image.LANCZOS)
left = (nw - W) // 2
top = (nh - H) // 2
still = still.crop((left, top, left + W, top + H))

# ---- Darken the still (Brightness 0.78) ----
still = ImageEnhance.Brightness(still).enhance(0.78)

base = still.convert("RGBA")

# ---- Subtle top/bottom vignette ----
vig = Image.new("L", (1, H), 0)
vd = vig.load()
for y in range(H):
    # darker near top and bottom edges
    ty = min(y, H - 1 - y)  # distance from nearest top/bottom edge
    band = 120  # px band depth
    if ty < band:
        a = int(110 * (1 - ty / band) ** 1.6)
    else:
        a = 0
    vd[0, y] = a
vig = vig.resize((W, H))
vlayer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vlayer.putalpha(vig)
black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
black.putalpha(vig)
base = Image.alpha_composite(base, black)

draw = ImageDraw.Draw(base)


def rr(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


# ---- Three concentric rounded keylines ----
# (1) dark inset rule (0,0,0,140) 3px r=8 inset 6px
i1 = 6
rr(draw, [i1, i1, W - 1 - i1, H - 1 - i1], r=8, outline=(0, 0, 0, 140), width=3)
# (2) GOLD stroke #c9a962 3px r=6 inset 9.5px
i2 = 9.5
rr(draw, [i2, i2, W - 1 - i2, H - 1 - i2], r=6, outline=GOLD + (255,), width=3)
# (3) light-gold hairline (229,199,138,128) 1px r=5 inset 12.5px
i3 = 12.5
rr(draw, [i3, i3, W - 1 - i3, H - 1 - i3], r=5, outline=LIGHT_GOLD + (128,), width=1)


# ---- Badge / pill helper ----
def load_font(size):
    for fp in (r"C:\Windows\Fonts\impact.ttf",
               r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


pill_font = load_font(30)
plaque_font = load_font(26)
WARM_WHITE = (245, 240, 230)


def text_size(font, txt):
    bb = font.getbbox(txt)
    return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]


def draw_pill(canvas, cx_anchor, top_y, txt, align="left", h=44):
    tw, th, ox, oy = text_size(pill_font, txt)
    pad_x = 18
    w = tw + pad_x * 2
    if align == "left":
        x0 = cx_anchor
    else:  # right
        x0 = cx_anchor - w
    x1 = x0 + w
    y0 = top_y
    y1 = y0 + h
    # pill layer for crisp alpha
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pl)
    rr(pd, [x0, y0, x1, y1], r=6, fill=(0, 0, 0, 214))
    # 1.5px gold inner border (inset ~2px)
    rr(pd, [x0 + 2, y0 + 2, x1 - 2, y1 - 2], r=5,
       outline=GOLD + (255,), width=2)
    # warm off-white text, centered
    tx = x0 + (w - tw) / 2 - ox
    ty = y0 + (h - th) / 2 - oy
    pd.text((tx, ty), txt, font=pill_font, fill=WARM_WHITE + (255,))
    canvas.alpha_composite(pl)


# HQ top-left, 8K top-right (inside keylines)
MARGIN = 24
draw_pill(base, MARGIN, MARGIN, "HQ", align="left")
draw_pill(base, W - MARGIN, MARGIN, "8K", align="right")

# ---- Brand plaque (bottom-left, dark gold pill) ----
plaque_txt = "remAIke.IT"
ptw, pth, pox, poy = text_size(plaque_font, plaque_txt)
ppad_x, ppad_y = 16, 10
pw = ptw + ppad_x * 2
ph = pth + ppad_y * 2
px0 = MARGIN
py1 = H - MARGIN
py0 = py1 - ph
px1 = px0 + pw
pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pl)
rr(pd, [px0, py0, px1, py1], r=6, fill=(0, 0, 0, 214))
rr(pd, [px0 + 2, py0 + 2, px1 - 2, py1 - 2], r=5, outline=GOLD + (255,), width=2)
# small gold square accent
pd.rectangle([px0 + 10, py0 + ph / 2 - 5, px0 + 20, py0 + ph / 2 + 5], fill=LIME + (255,))
pd.text((px0 + ppad_x + 16, py0 + (ph - pth) / 2 - poy), plaque_txt,
        font=plaque_font, fill=LIGHT_GOLD + (255,))
base.alpha_composite(pl)

# ---- Soft drop shadow for lift on white, then composite frame onto white canvas ----
frame = base.convert("RGBA")
shadow = Image.new("RGBA", (W + 80, H + 80), (0, 0, 0, 0))
sh_rect = Image.new("RGBA", (W, H), (0, 0, 0, 110))
shadow.paste(sh_rect, (40, 40 + 6))  # y+6 offset
shadow = shadow.filter(ImageFilter.GaussianBlur(18))

canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
# composite shadow (cropped to canvas) then frame
shadow_crop = shadow.crop((40, 40, 40 + W, 40 + H))
canvas = Image.alpha_composite(canvas, shadow_crop)
canvas = Image.alpha_composite(canvas, frame)

final = canvas.convert("RGB")
final.save(OUT_PATH, "PNG")
print(f"Saved {OUT_PATH} size={final.size}")
