# -*- coding: utf-8 -*-
"""
CC_oled: Sleek modern 8K OLED monitor bezel ("old film, new glass").
Light studio bg, brushed-metal rim, gold hairline, glass glare.
Output 1280x720 -> D:/remaike.TV/thumbnails_pilot/CC_oled.png
"""
import io
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_oled.png"

# Brand colors
GOLD = (201, 169, 98)
GOLD_LT = (229, 199, 138)
GOLD_DK = (168, 139, 74)
LIME = (132, 204, 22)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        c = lerp(top, bottom, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c
    return img


def load_font(size, bold=True):
    for path in (r"C:\Windows\Fonts\impact.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def fetch_test_frame():
    vid = "JzJrH43etPA"
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        url = "https://i.ytimg.com/vi/%s/%s.jpg" % (vid, q)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width >= 200:
                print("Fetched test frame:", q, im.size)
                return im
        except Exception as e:
            print("  miss", q, e)
    print("  no frame, using fallback")
    return None


# ---------- Build background (light studio) ----------
bg = vgrad((W, H), (238, 240, 243), (205, 209, 215)).convert("RGBA")

# Subtle radial floor vignette / studio sweep behind device
sweep = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sweep)
sd.ellipse([W * 0.12, H * 0.55, W * 0.88, H * 1.25], fill=70)
sweep = sweep.filter(ImageFilter.GaussianBlur(80))
bright = Image.new("RGBA", (W, H), (255, 255, 255, 255))
bg = Image.composite(bright, bg, sweep)

# ---------- Device geometry ----------
DX0, DY0, DX1, DY1 = 150, 90, 1130, 630
DR = 34
RIM = 20

# Drop shadow under device (blur 22, y+6)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.rounded_rectangle([DX0, DY0 + 6, DX1, DY1 + 6], radius=DR, fill=(0, 0, 0, 130))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
bg = Image.alpha_composite(bg, shadow)

# ---------- Brushed-metal rim (device body) ----------
# Vertical gradient (70,72,78) -> (120,124,132)
metal = vgrad((DX1 - DX0, DY1 - DY0), (70, 72, 78), (120, 124, 132)).convert("RGBA")
mw, mh = metal.size
mpx = metal.load()
# brushed texture: faint horizontal striations via per-row jitter
import random
random.seed(7)
row_jit = [random.randint(-7, 7) for _ in range(mh)]
for y in range(mh):
    j = row_jit[y]
    if j == 0:
        continue
    for x in range(mw):
        r, g, b, a = mpx[x, y]
        mpx[x, y] = (max(0, min(255, r + j)),
                     max(0, min(255, g + j)),
                     max(0, min(255, b + j)), a)

# additive horizontal sheen band for 3D metal (a bright vertical-position band)
sheen = Image.new("L", (mw, mh), 0)
sdr = ImageDraw.Draw(sheen)
band_y = int(mh * 0.30)
sdr.rectangle([0, band_y - 26, mw, band_y + 26], fill=90)
band_y2 = int(mh * 0.78)
sdr.rectangle([0, band_y2 - 14, mw, band_y2 + 14], fill=45)
sheen = sheen.filter(ImageFilter.GaussianBlur(20))
sheen_rgba = Image.merge("RGBA", (Image.new("L", (mw, mh), 255),
                                  Image.new("L", (mw, mh), 255),
                                  Image.new("L", (mw, mh), 255), sheen))
metal = Image.alpha_composite(metal, sheen_rgba)

# Mask metal to rounded device shape
dev_mask = Image.new("L", (mw, mh), 0)
ImageDraw.Draw(dev_mask).rounded_rectangle([0, 0, mw - 1, mh - 1], radius=DR, fill=255)
bg.paste(metal, (DX0, DY0), dev_mask)

# Bevel on rim: light top-left edge, dark bottom-right edge
bevel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bevel)
bd.rounded_rectangle([DX0, DY0, DX1, DY1], radius=DR, outline=(180, 184, 192, 200), width=2)
bg = Image.alpha_composite(bg, bevel)
bevel2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd2 = ImageDraw.Draw(bevel2)
# dark inner edge bottom-right feel: draw an offset dark arc-ish outline
bd2.rounded_rectangle([DX0 + 1, DY0 + 3, DX1 + 1, DY1 + 1], radius=DR, outline=(40, 41, 46, 150), width=2)
b2mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(b2mask).rectangle([DX0 + (DX1 - DX0) // 2, DY0 + (DY1 - DY0) // 2, W, H], fill=255)
bg = Image.composite(Image.alpha_composite(bg, bevel2), bg, b2mask)

# ---------- Screen inset ----------
SX0, SY0 = DX0 + RIM, DY0 + RIM
SX1, SY1 = DX1 - RIM, DY1 - RIM
SR = 14

# Screen base (deep OLED black)
screen_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sl = ImageDraw.Draw(screen_layer)
sl.rounded_rectangle([SX0, SY0, SX1, SY1], radius=SR, fill=(8, 9, 11, 255))
bg = Image.alpha_composite(bg, screen_layer)

# ---------- Place the test frame INSIDE the screen ----------
frame = fetch_test_frame()
sw, sh = SX1 - SX0, SY1 - SY0
if frame is None:
    # fallback gradient "content"
    frame = vgrad((sw, sh), (28, 24, 20), (60, 50, 38)).convert("RGB")
# cover-fit (fill, crop center)
fr = frame.convert("RGB")
scale = max(sw / fr.width, sh / fr.height)
nw, nh = int(fr.width * scale), int(fr.height * scale)
fr = fr.resize((nw, nh), Image.LANCZOS)
ox = (nw - sw) // 2
oy = (nh - sh) // 2
fr = fr.crop((ox, oy, ox + sw, oy + sh)).convert("RGBA")

# Slightly deepen blacks / OLED contrast: multiply toward dark a touch at edges (vignette)
vig = Image.new("L", (sw, sh), 0)
ImageDraw.Draw(vig).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=SR, fill=255)
vig_inner = Image.new("L", (sw, sh), 0)
ImageDraw.Draw(vig_inner).rounded_rectangle([18, 18, sw - 19, sh - 19], radius=SR, fill=255)
vig_inner = vig_inner.filter(ImageFilter.GaussianBlur(22))
# darken outside inner region
dark = Image.new("RGBA", (sw, sh), (0, 0, 0, 110))
fr = Image.composite(fr, Image.alpha_composite(fr, dark), vig_inner)

# Mask frame to rounded screen
fmask = Image.new("L", (sw, sh), 0)
ImageDraw.Draw(fmask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=SR, fill=255)
bg.paste(fr, (SX0, SY0), fmask)

# ---------- 2px GOLD hairline around the screen ----------
hair = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(hair)
hd.rounded_rectangle([SX0, SY0, SX1, SY1], radius=SR, outline=GOLD + (255,), width=2)
bg = Image.alpha_composite(bg, hair)

# ---------- Soft diagonal white glass-glare (blur 30, low alpha) ----------
glare = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glare)
# diagonal band across upper-left of screen
gd.polygon([(SX0, SY0), (SX0 + 360, SY0), (SX0 + 120, SY1), (SX0, SY1 - 120)],
           fill=(255, 255, 255, 60))
gd.polygon([(SX0 + 80, SY0), (SX0 + 200, SY0), (SX0 + 40, SY0 + 260), (SX0, SY0 + 200)],
           fill=(255, 255, 255, 40))
glare = glare.filter(ImageFilter.GaussianBlur(30))
# clip glare to screen
gmask = Image.new("L", (W, H), 0)
ImageDraw.Draw(gmask).rounded_rectangle([SX0, SY0, SX1, SY1], radius=SR, fill=255)
glare.putalpha(Image.composite(glare.getchannel("A"), Image.new("L", (W, H), 0), gmask))
bg = Image.alpha_composite(bg, glare)

draw = ImageDraw.Draw(bg)

# ---------- HQ / 8K chips: dark rounded, gold outline, at bottom of screen ----------
def chip(d, x, y, text, font):
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    padx, pady = 16, 9
    w = tw + padx * 2
    h = th + pady * 2
    rect = [x, y, x + w, y + h]
    d.rounded_rectangle(rect, radius=h // 2, fill=(12, 13, 16, 235), outline=GOLD + (255,), width=2)
    d.text((x + padx - tb[0], y + pady - tb[1]), text, font=font, fill=GOLD_LT)
    return w, h


chip_font = load_font(30)
chip_y = SY1 - 60
# HQ bottom-left of screen
chip(draw, SX0 + 24, chip_y, "HQ", chip_font)
# 8K bottom area, kept LEFT of the reserved bottom-right pill zone
w8, h8 = draw.textbbox((0, 0), "8K", font=chip_font)[2:]
# place 8K a bit right of HQ (premium pair, away from BR corner)
chip(draw, SX0 + 24 + 90, chip_y, "8K", chip_font)

# ---------- Brand plaque on the metal chin (bottom rim) ----------
plaque_font = load_font(26)
ptxt = "remAIke.IT"
ptb = draw.textbbox((0, 0), ptxt, font=plaque_font)
ptw = ptb[2] - ptb[0]
pcx = (DX0 + DX1) // 2
chin_cy = (SY1 + DY1) // 2 + 1
# tiny gold separator dots flanking the wordmark, etched look
draw.text((pcx - ptw // 2 + 1, chin_cy - (ptb[3] - ptb[1]) // 2 - ptb[1] + 1),
          ptxt, font=plaque_font, fill=(30, 31, 35))  # engrave shadow
draw.text((pcx - ptw // 2, chin_cy - (ptb[3] - ptb[1]) // 2 - ptb[1]),
          ptxt, font=plaque_font, fill=GOLD_LT)
# lime accent power dot on chin (left)
draw.ellipse([DX0 + 30, chin_cy - 5, DX0 + 40, chin_cy + 5], fill=LIME)

# ---------- Top-left "HQ" and top-right "8K" badges (brief requirement) ----------
# Small dark rounded pills with gold outline near the device top corners.
badge_font = load_font(26)
# HQ top-left, on the metal rim
chip(draw, DX0 + 10, DY0 - 6, "HQ", badge_font)
# 8K top-right: measure first (no draw), then place flush to right rim corner
b8b = draw.textbbox((0, 0), "8K", font=badge_font)
b8w = (b8b[2] - b8b[0]) + 32  # padx*2 = 32
chip(draw, DX1 - 10 - b8w, DY0 - 6, "8K", badge_font)

# Save
bg_rgb = bg.convert("RGB")
bg_rgb.save(OUT, "PNG")
print("Saved", OUT, bg_rgb.size)
