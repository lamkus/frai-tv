import os
import math
import random
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "filmtable"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_filmtable.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Brand colors
GOLD = (201, 169, 98)
LGOLD = (229, 199, 138)
DGOLD = (168, 139, 74)
LIME = (132, 204, 22)

random.seed(35)


# ---------- fonts ----------
def load_font(size, bold=True):
    for p in (r"C:\Windows\Fonts\impact.ttf",
              r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ---------- fetch test frame ----------
def fetch_frame():
    vid = "JzJrH43etPA"
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        url = f"https://i.ytimg.com/vi/{vid}/{q}.jpg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            with open(r"D:\remaike.TV\thumbnails_pilot\_tmp_frame.jpg", "wb") as f:
                f.write(data)
            im = Image.open(r"D:\remaike.TV\thumbnails_pilot\_tmp_frame.jpg").convert("RGB")
            if im.width >= 320:
                print("fetched", q, im.size)
                return im
        except Exception as e:
            print("fail", q, e)
    return None


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------- base canvas: warm dark light-table surface ----------
base = Image.new("RGB", (W, H), (18, 14, 10))
bd = ImageDraw.Draw(base)
# subtle vertical gradient on the central area (warm archival)
for y in range(H):
    t = y / H
    top = (40, 31, 20)
    mid = (28, 22, 14)
    if t < 0.5:
        c = lerp(top, mid, t / 0.5)
    else:
        c = lerp(mid, (22, 17, 11), (t - 0.5) / 0.5)
    bd.line([(0, y), (W, y)], fill=c)

# warm central glow (light-table luminance from the negative)
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
gd.ellipse([W * 0.18, H * 0.18, W * 0.82, H * 0.82], fill=130)
glow = glow.filter(ImageFilter.GaussianBlur(120))
warm = Image.new("RGB", (W, H), (90, 70, 38))
base = Image.composite(warm, base, glow.point(lambda v: int(v * 0.55)))


# ---------- film strip band ----------
def make_film_band(band_h):
    """Black 35mm strip with backlit warm-gold sprocket holes."""
    band = Image.new("RGB", (W, band_h), (8, 7, 6))
    bdr = ImageDraw.Draw(band)
    # subtle vertical sheen on the black celluloid
    for y in range(band_h):
        t = y / band_h
        c = lerp((6, 5, 4), (16, 13, 9), 1 - abs(t - 0.5) * 2)
        bdr.line([(0, y), (W, y)], fill=c)

    # backlit glow layer behind holes (gold gradient)
    glow_l = Image.new("L", (W, band_h), 0)
    gld = ImageDraw.Draw(glow_l)

    hole_w, hole_h = 34, 26
    gap = 64
    margin_y = (band_h - hole_h) // 2
    x = 26
    holes = []
    while x + hole_w < W - 10:
        holes.append((x, margin_y))
        # glow behind hole
        gld.rounded_rectangle([x - 8, margin_y - 8, x + hole_w + 8, margin_y + hole_h + 8],
                              radius=10, fill=200)
        x += hole_w + gap
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(14))
    goldlayer = Image.new("RGB", (W, band_h))
    gld = ImageDraw.Draw(goldlayer)
    for yy in range(band_h):
        t = yy / band_h
        gld.line([(0, yy), (W, yy)], fill=lerp(DGOLD, LGOLD, 1 - abs(t - 0.5) * 1.6))
    band = Image.composite(goldlayer, band, glow_l.point(lambda v: int(v * 0.85)))

    # punch the actual holes: bright warm backlit rectangles
    bdr = ImageDraw.Draw(band)
    for (hx, hy) in holes:
        # outer warm ring already from glow; draw bright hole
        for i, sh in enumerate(range(6, 0, -1)):
            t = i / 6
            col = lerp(DGOLD, (255, 244, 210), t)
            bdr.rounded_rectangle([hx + sh, hy + sh, hx + hole_w - sh, hy + hole_h - sh],
                                  radius=6, fill=col)
        bdr.rounded_rectangle([hx + 5, hy + 5, hx + hole_w - 5, hy + hole_h - 5],
                              radius=5, fill=(255, 248, 224))
    # thin gold edge lines top & bottom of band
    bdr.line([(0, 1), (W, 1)], fill=DGOLD)
    bdr.line([(0, band_h - 2), (W, band_h - 2)], fill=DGOLD)
    return band


BAND_H = 70
top_band = make_film_band(BAND_H)
bot_band = make_film_band(BAND_H)
base.paste(top_band, (0, 0))
base.paste(bot_band, (0, H - BAND_H))

# soft warm bloom spilling from bands onto the table
spill = Image.new("L", (W, H), 0)
sp = ImageDraw.Draw(spill)
sp.rectangle([0, BAND_H, W, BAND_H + 50], fill=120)
sp.rectangle([0, H - BAND_H - 50, W, H - BAND_H], fill=120)
spill = spill.filter(ImageFilter.GaussianBlur(40))
spillgold = Image.new("RGB", (W, H), (120, 92, 48))
base = Image.composite(spillgold, base, spill.point(lambda v: int(v * 0.5)))


# ---------- center image (the negative on the table) ----------
frame = fetch_frame()
img_x0, img_y0 = 300, 138
img_x1, img_y1 = 980, 582
iw, ih = img_x1 - img_x0, img_y1 - img_y0

if frame is not None:
    fr = frame.copy()
    # cover-fit
    fr_ratio = fr.width / fr.height
    box_ratio = iw / ih
    if fr_ratio > box_ratio:
        nh = ih
        nw = int(ih * fr_ratio)
    else:
        nw = iw
        nh = int(iw / fr_ratio)
    fr = fr.resize((nw, nh), Image.LANCZOS)
    left = (nw - iw) // 2
    top = (nh - ih) // 2
    fr = fr.crop((left, top, left + iw, top + ih))
    # warm archival grade: slight sepia tint
    sep = Image.new("RGB", (iw, ih), (60, 44, 22))
    fr = Image.blend(fr, sep, 0.14)
else:
    fr = Image.new("RGB", (iw, ih), (50, 40, 26))

# drop shadow under the negative
shadow = Image.new("L", (W, H), 0)
shd = ImageDraw.Draw(shadow)
shd.rounded_rectangle([img_x0 - 8, img_y0 - 8, img_x1 + 12, img_y1 + 16], radius=14, fill=200)
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
dark = Image.new("RGB", (W, H), (0, 0, 0))
base = Image.composite(dark, base, shadow.point(lambda v: int(v * 0.6)))

base.paste(fr, (img_x0, img_y0))

# thin gold keyline around the negative
kd = ImageDraw.Draw(base)
kd.rectangle([img_x0 - 2, img_y0 - 2, img_x1 + 1, img_y1 + 1], outline=GOLD, width=3)
kd.rectangle([img_x0 - 5, img_y0 - 5, img_x1 + 4, img_y1 + 4], outline=DGOLD, width=1)


# ---------- film grain over whole image ----------
grain = Image.effect_noise((W, H), 26).convert("L")
grain_rgb = Image.merge("RGB", (grain, grain, grain))
base = Image.blend(base, grain_rgb, 0.055)


# ---------- chips & plaque ----------
draw = ImageDraw.Draw(base)
font_chip = load_font(30)
font_plaque = load_font(30)


def chip(draw, x, y, text, font, pad=12):
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    w = tw + pad * 2
    h = th + pad * 2
    # dark rounded pill with gold keyline
    chip_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip_img)
    cd.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=(14, 11, 7, 235))
    cd.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, outline=GOLD, width=2)
    cd.text((pad, pad - tb[1]), text, font=font, fill=LGOLD)
    base.paste(chip_img, (x, y), chip_img)
    return w, h


# HQ top-left (below the top film band), 8K top-right
chip(draw, 22, BAND_H + 14, "HQ", font_chip)
w8, h8 = draw.textbbox((0, 0), "8K", font=font_chip)[2:]
cw, ch = chip(draw, 0, 0, "8K", font_chip)  # measure
# actually place 8K at right
chip_img_pad = 12
tb = draw.textbbox((0, 0), "8K", font=font_chip)
cw = (tb[2] - tb[0]) + chip_img_pad * 2
chip(draw, W - cw - 22, BAND_H + 14, "8K", font_chip)

# brand plaque bottom-left (keep bottom-right free for duration pill)
plaque_text = "remAIke.IT"
ptb = draw.textbbox((0, 0), plaque_text, font=font_plaque)
ptw, pth = ptb[2] - ptb[0], ptb[3] - ptb[1]
px0, py1 = 24, H - BAND_H - 16
pw, ph = ptw + 28, pth + 20
plaque = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
pld = ImageDraw.Draw(plaque)
# brushed gold plaque
for yy in range(ph):
    t = yy / ph
    pld.line([(0, yy), (pw, yy)], fill=lerp(LGOLD, DGOLD, t) + (255,))
pld.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=8, outline=(40, 30, 16), width=2)
pld.text((14, 10 - ptb[1]), plaque_text, font=font_plaque, fill=(28, 20, 10))
base.paste(plaque, (px0, py1 - ph), plaque)

# title-ish small archival caption near top of negative (optional thin gold label)
font_cap = load_font(26)
cap = "LICHTTISCH 35"
ctb = draw.textbbox((0, 0), cap, font=font_cap)
ctw = ctb[2] - ctb[0]
cap_x = img_x0 + (iw - ctw) // 2
# subtle shadow
draw.text((cap_x + 2, img_y1 + 10 + 2), cap, font=font_cap, fill=(0, 0, 0))
draw.text((cap_x, img_y1 + 10), cap, font=font_cap, fill=LGOLD)

# ---------- final vignette ----------
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], fill=0)
vd.ellipse([-200, -120, W + 200, H + 120], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(160))
darkv = Image.new("RGB", (W, H), (0, 0, 0))
base = Image.composite(base, darkv, vig)

base = base.convert("RGB")
base.save(OUT, "PNG")
print("saved", OUT, base.size)
