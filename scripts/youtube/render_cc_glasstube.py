import os
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "glasstube"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_glasstube.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---- Brand colors ----
GOLD = (201, 169, 98)
LGOLD = (229, 199, 138)
DGOLD = (168, 139, 74)
LIME = (132, 204, 22)

# ---- Fonts ----
def load_font(size, bold=True):
    for p in [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---- Fetch test frame ----
def fetch_frame():
    vid = "JzJrH43etPA"
    for q in ["maxresdefault", "sddefault", "hqdefault"]:
        url = f"https://i.ytimg.com/vi/{vid}/{q}.jpg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            tmp = os.path.join(os.path.dirname(OUT), f"_tmp_{q}.jpg")
            with open(tmp, "wb") as f:
                f.write(data)
            im = Image.open(tmp).convert("RGB")
            if im.width >= 480:
                print(f"Fetched {q}: {im.size}")
                return im
        except Exception as e:
            print(f"  {q} failed: {e}")
            continue
    # fallback gray
    return Image.new("RGB", (1280, 720), (40, 40, 44))

def cover_resize(im, tw, th):
    iw, ih = im.size
    s = max(tw / iw, th / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return m

# ============================================================
# Base canvas: charcoal gradient bezel
# ============================================================
base = Image.new("RGB", (W, H), (28, 28, 32))
px = base.load()
# vertical charcoal gradient #1c1c20 with subtle variation
for y in range(H):
    t = y / (H - 1)
    r = int(30 + 6 * (1 - t))
    g = int(30 + 6 * (1 - t))
    b = int(34 + 7 * (1 - t))
    for x in range(W):
        px[x, y] = (r, g, b)

draw = ImageDraw.Draw(base)

# ---- Outer bezel bevel: light top-left, dark bottom-right ----
# Draw a recessed dark bezel frame. The CRT glass sits inside.
BZ = 70  # bezel thickness
# bevel highlight (top-left)
for i in range(6):
    a = int(70 * (1 - i / 6))
    draw.line([(i, i), (W - 1 - i, i)], fill=(min(255, 60 + a), min(255, 60 + a), min(255, 66 + a)))
    draw.line([(i, i), (i, H - 1 - i)], fill=(min(255, 60 + a), min(255, 60 + a), min(255, 66 + a)))
# bevel shadow (bottom-right)
for i in range(6):
    a = int(60 * (1 - i / 6))
    c = max(0, 14 - a // 8)
    draw.line([(i, H - 1 - i), (W - 1 - i, H - 1 - i)], fill=(c, c, c + 2))
    draw.line([(W - 1 - i, i), (W - 1 - i, H - 1 - i)], fill=(c, c, c + 2))

# Inner recess shadow ring around the screen opening
screen_box = (BZ, BZ, W - BZ, H - BZ)
sx0, sy0, sx1, sy1 = screen_box
sw, sh = sx1 - sx0, sy1 - sy0

# soft inner shadow (recess) - draw a blurred dark rounded rect slightly larger
recess = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(recess)
rd.rounded_rectangle([sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14], radius=96, outline=(0, 0, 0, 200), width=18)
recess = recess.filter(ImageFilter.GaussianBlur(12))
base = Image.alpha_composite(base.convert("RGBA"), recess).convert("RGB")
draw = ImageDraw.Draw(base)

# bevel on screen opening: light top-left edge, dark bottom-right edge (3D recess => inverted: dark TL, light BR? )
# For a recessed screen, top-left edge is in shadow, bottom-right catches light. But brief says bezel bevel light TL / dark BR.
# We'll give the OPENING inner edge a recessed look: darker top-left lip, subtle light bottom-right lip.
op = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(op)
for i in range(5):
    aa = int(120 * (1 - i / 5))
    od.line([(sx0 + i, sy0 + i), (sx1 - i, sy0 + i)], fill=(0, 0, 0, aa))  # top dark
    od.line([(sx0 + i, sy0 + i), (sx0 + i, sy1 - i)], fill=(0, 0, 0, aa))  # left dark
for i in range(4):
    aa = int(50 * (1 - i / 4))
    od.line([(sx0 + i, sy1 - i), (sx1 - i, sy1 - i)], fill=(120, 120, 128, aa))  # bottom light
    od.line([(sx1 - i, sy0 + i), (sx1 - i, sy1 - i)], fill=(120, 120, 128, aa))  # right light
base = Image.alpha_composite(base.convert("RGBA"), op).convert("RGB")

# ============================================================
# CRT screen content
# ============================================================
GLASS_R = 80
frame = fetch_frame()
frame = cover_resize(frame, sw, sh)
frame = frame.convert("RGBA")

fd = ImageDraw.Draw(frame)

# --- scanlines (alpha ~30) ---
scan = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
sd = ImageDraw.Draw(scan)
for yy in range(0, sh, 3):
    sd.line([(0, yy), (sw, yy)], fill=(0, 0, 0, 30))
frame = Image.alpha_composite(frame, scan)

# --- vignette for CRT curvature ---
vig = Image.new("L", (sw, sh), 0)
vd = ImageDraw.Draw(vig)
vd.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=GLASS_R, fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(60))
# build vignette overlay: darken edges
vov = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
vovpx = vov.load()
vigpx = vig.load()
cx, cy = sw / 2, sh / 2
maxd = math.hypot(cx, cy)
for yy in range(sh):
    for xx in range(0, sw, 1):
        d = math.hypot(xx - cx, yy - cy) / maxd
        a = int(min(150, max(0, (d - 0.45) * 300)))
        if a > 0:
            vovpx[xx, yy] = (0, 0, 0, a)
frame = Image.alpha_composite(frame, vov)

# --- diagonal glass glare (soft) ---
glare = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
gd = ImageDraw.Draw(glare)
# a broad soft diagonal band top-left
gd.polygon([(-50, 0), (sw * 0.55, 0), (sw * 0.18, sh), (-50, sh)], fill=(255, 255, 255, 26))
gd.polygon([(sw * 0.05, 0), (sw * 0.22, 0), (-30, sh), (-120, sh)], fill=(255, 255, 255, 18))
glare = glare.filter(ImageFilter.GaussianBlur(28))
frame = Image.alpha_composite(frame, glare)

# --- top phosphor sheen highlight ---
sheen = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
shd = ImageDraw.Draw(sheen)
shd.ellipse([sw * 0.05, -sh * 0.5, sw * 0.95, sh * 0.32], fill=(255, 255, 255, 22))
sheen = sheen.filter(ImageFilter.GaussianBlur(40))
frame = Image.alpha_composite(frame, sheen)

# round the screen corners (glass tube)
gmask = rounded_mask((sw, sh), GLASS_R)
frame.putalpha(gmask)

# paste screen into bezel
base = base.convert("RGBA")
base.alpha_composite(frame, (sx0, sy0))

# --- thin gold inner keyline around glass ---
draw = ImageDraw.Draw(base)
draw.rounded_rectangle([sx0 - 2, sy0 - 2, sx1 + 1, sy1 + 1], radius=GLASS_R + 2, outline=GOLD, width=2)
draw.rounded_rectangle([sx0 - 4, sy0 - 4, sx1 + 3, sy1 + 3], radius=GLASS_R + 4, outline=DGOLD, width=1)

# ============================================================
# Badges: HQ (top-left), 8K (top-right) - phosphor green-on-dark pills
# ============================================================
def pill(img, xy, text, font, fg, bg=(12, 14, 12, 235), pad=(16, 8), border=None, glow=None):
    d = ImageDraw.Draw(img)
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    x, y = xy
    w = tw + pad[0] * 2
    h = th + pad[1] * 2
    rad = h // 2
    if glow:
        gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gld = ImageDraw.Draw(gl)
        gld.rounded_rectangle([x - 4, y - 4, x + w + 4, y + h + 4], radius=rad + 4, fill=glow)
        gl = gl.filter(ImageFilter.GaussianBlur(10))
        img.alpha_composite(gl)
        d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], radius=rad, fill=bg)
    if border:
        d.rounded_rectangle([x, y, x + w, y + h], radius=rad, outline=border, width=2)
    d.text((x + pad[0] - tb[0], y + pad[1] - tb[1]), text, font=font, fill=fg)
    return (x, y, x + w, y + h)

bfont = load_font(40)
# HQ phosphor green
pill(base, (sx0 + 22, sy0 + 22), "HQ", bfont, (150, 255, 150),
     bg=(10, 18, 10, 230), border=(60, 140, 60), glow=(80, 220, 80, 90))
# 8K phosphor green, top-right
tb = ImageDraw.Draw(base).textbbox((0, 0), "8K", font=bfont)
w8 = (tb[2] - tb[0]) + 32
pill(base, (sx1 - 22 - w8, sy0 + 22), "8K", bfont, (150, 255, 150),
     bg=(10, 18, 10, 230), border=(60, 140, 60), glow=(80, 220, 80, 90))

# ============================================================
# Brand plaque: remAIke.IT  (bottom-left, away from duration pill bottom-right)
# ============================================================
pfont = load_font(34)
ptxt = "remAIke.IT"
plaque = Image.new("RGBA", base.size, (0, 0, 0, 0))
pld = ImageDraw.Draw(plaque)
tb = pld.textbbox((0, 0), ptxt, font=pfont)
ptw, pth = tb[2] - tb[0], tb[3] - tb[1]
ppx = sx0 + 22
ppy = sy1 - 22 - (pth + 20)
pw = ptw + 36
ph = pth + 20
# dark glass plaque with gold keyline
pld.rounded_rectangle([ppx, ppy, ppx + pw, ppy + ph], radius=10, fill=(14, 14, 16, 225))
pld.rounded_rectangle([ppx, ppy, ppx + pw, ppy + ph], radius=10, outline=GOLD, width=2)
# gold text
pld.text((ppx + 18 - tb[0], ppy + 10 - tb[1]), ptxt, font=pfont, fill=LGOLD)
base.alpha_composite(plaque)

# ============================================================
# Round outer corners slightly (YouTube rounds ~12px) - keep crisp, just final
# ============================================================
final = base.convert("RGB")
final.save(OUT, "PNG")
print("SAVED", OUT, final.size)
