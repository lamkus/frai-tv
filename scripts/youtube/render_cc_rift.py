import os, urllib.request, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops

random.seed(42)
W, H = 1280, 720
KEY = "rift"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_rift.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---------- colors ----------
GOLD = (201, 169, 98)
LGOLD = (229, 199, 138)
DGOLD = (168, 139, 74)
LIME = (132, 204, 22)
NEARWHITE = (255, 250, 235)

# ---------- fetch test frame ----------
VID = "JzJrH43etPA"
frame = None
for q in ["maxresdefault", "sddefault", "hqdefault"]:
    try:
        url = f"https://i.ytimg.com/vi/{VID}/{q}.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        tmp = os.path.join(os.path.dirname(OUT), f"_frame_{KEY}.jpg")
        with open(tmp, "wb") as f:
            f.write(data)
        frame = Image.open(tmp).convert("RGB")
        print("got frame", q, frame.size)
        break
    except Exception as e:
        print("fail", q, e)
if frame is None:
    frame = Image.new("RGB", (W, H), (40, 40, 50))

def cover(img, tw, th):
    iw, ih = img.size
    s = max(tw / iw, th / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return img.crop((x, y, x + tw, y + th))

base_frame = cover(frame, W, H)

# ---------- fonts ----------
def load_font(size):
    for p in [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

f_chip = load_font(30)

# ---------- canvas: dark bezel vertical gradient (43,43,48)->(26,26,30) ----------
canvas = Image.new("RGB", (W, H))
top = (43, 43, 48)
bot = (26, 26, 30)
px = canvas.load()
for y in range(H):
    t = y / (H - 1)
    r = int(top[0] + (bot[0] - top[0]) * t)
    g = int(top[1] + (bot[1] - top[1]) * t)
    b = int(top[2] + (bot[2] - top[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

# ---------- geometry ----------
# Inner opening inset 70px, rounded r=18
INSET = 70
RAD = 18
ox0, oy0, ox1, oy1 = INSET, INSET, W - INSET, H - INSET

# ---------- DECAYED outer-ring frame (full frame, decayed) ----------
decayed = base_frame.copy()
decayed = ImageEnhance.Color(decayed).enhance(0.35)  # desaturate
# sepia tint
gray = ImageOps.grayscale(decayed)
sepia = ImageOps.colorize(gray, black=(28, 20, 10), white=(228, 205, 165), mid=(150, 120, 78))
decayed = Image.blend(decayed, sepia, 0.55)
# film grain
noise = Image.effect_noise((W, H), 38).convert("L")
noise_rgb = Image.merge("RGB", (noise, noise, noise))
decayed = ImageChops.overlay(decayed, noise_rgb)
# scanlines
sl = ImageDraw.Draw(decayed)
for y in range(0, H, 3):
    sl.line([(0, y), (W, y)], fill=(0, 0, 0), width=1)
decayed = Image.blend(base_frame, decayed, 0.92)
# vignette on decayed
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.3, -H * 0.3, W * 1.3, H * 1.3], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(160))
dark = Image.new("RGB", (W, H), (0, 0, 0))
decayed = Image.composite(decayed, dark, vig)

# ---------- CLEAN inner 8K frame ----------
clean = base_frame.copy()
clean = ImageEnhance.Color(clean).enhance(1.18)
clean = ImageEnhance.Sharpness(clean).enhance(1.4)
clean = ImageEnhance.Contrast(clean).enhance(1.05)

# ---------- paste decayed ring (everything between bezel and inner opening) ----------
# Outer ring ~60px between bezel and inner opening => the decayed area starts ~10px and inner opening at 70.
RING_OUT = 10
# decayed region mask: rounded rect from RING_OUT to (W-RING_OUT) minus the inner opening
ring_mask = Image.new("L", (W, H), 0)
rd = ImageDraw.Draw(ring_mask)
rd.rounded_rectangle([RING_OUT, RING_OUT, W - RING_OUT, H - RING_OUT], radius=RAD + 8, fill=255)
canvas.paste(decayed, (0, 0), ring_mask)

# ---------- paste clean inner opening ----------
inner_mask = Image.new("L", (W, H), 0)
imd = ImageDraw.Draw(inner_mask)
imd.rounded_rectangle([ox0, oy0, ox1, oy1], radius=RAD, fill=255)
canvas.paste(clean, (0, 0), inner_mask)

# ---------- THE RIFT: irregular gold crack along the opening edge ----------
# Build jittered point path tracing the rounded-rect opening perimeter.
def rounded_rect_perimeter(x0, y0, x1, y1, r, n=260):
    pts = []
    # corners centers
    corners = [
        (x1 - r, y0 + r, -90, 0),   # top-right arc
        (x1 - r, y1 - r, 0, 90),    # bottom-right
        (x0 + r, y1 - r, 90, 180),  # bottom-left
        (x0 + r, y0 + r, 180, 270), # top-left
    ]
    # We'll sample sequentially: top edge, TR arc, right edge, BR arc, bottom, BL arc, left, TL arc
    seq = []
    steps_edge = n // 8
    steps_arc = n // 12
    # top edge L->R
    for i in range(steps_edge):
        t = i / steps_edge
        seq.append((x0 + r + (x1 - r - (x0 + r)) * t, y0))
    # TR arc
    for i in range(steps_arc):
        a = math.radians(-90 + 90 * i / steps_arc)
        seq.append((x1 - r + r * math.cos(a), y0 + r + r * math.sin(a)))
    # right edge
    for i in range(steps_edge):
        t = i / steps_edge
        seq.append((x1, y0 + r + (y1 - r - (y0 + r)) * t))
    # BR arc
    for i in range(steps_arc):
        a = math.radians(0 + 90 * i / steps_arc)
        seq.append((x1 - r + r * math.cos(a), y1 - r + r * math.sin(a)))
    # bottom edge R->L
    for i in range(steps_edge):
        t = i / steps_edge
        seq.append((x1 - r - (x1 - r - (x0 + r)) * t, y1))
    # BL arc
    for i in range(steps_arc):
        a = math.radians(90 + 90 * i / steps_arc)
        seq.append((x0 + r + r * math.cos(a), y1 - r + r * math.sin(a)))
    # left edge B->T
    for i in range(steps_edge):
        t = i / steps_edge
        seq.append((x0, y1 - r - (y1 - r - (y0 + r)) * t))
    # TL arc
    for i in range(steps_arc):
        a = math.radians(180 + 90 * i / steps_arc)
        seq.append((x0 + r + r * math.cos(a), y0 + r + r * math.sin(a)))
    return seq

perim = rounded_rect_perimeter(ox0, oy0, ox1, oy1, RAD, n=320)
# jitter outward/inward to make an irregular crack
crack = []
for (x, y) in perim:
    j = random.uniform(-7, 7)
    # rough normal direction approx from center
    cx, cy = W / 2, H / 2
    dx, dy = x - cx, y - cy
    d = math.hypot(dx, dy) or 1
    nx, ny = dx / d, dy / d
    crack.append((x + nx * j + random.uniform(-3, 3), y + ny * j + random.uniform(-3, 3)))

# layer images for screen blend
core_layer = Image.new("RGB", (W, H), (0, 0, 0))
bloom_layer = Image.new("RGB", (W, H), (0, 0, 0))
cdraw = ImageDraw.Draw(core_layer)
bdraw = ImageDraw.Draw(bloom_layer)

# wide bloom (gold), then hot core (near-white)
bdraw.line(crack, fill=GOLD, width=5, joint="curve")
bdraw.line(crack, fill=LGOLD, width=3, joint="curve")
cdraw.line(crack, fill=NEARWHITE, width=4, joint="curve")
cdraw.line(crack, fill=(255, 255, 255), width=2, joint="curve")

bloom_layer = bloom_layer.filter(ImageFilter.GaussianBlur(14))
core_layer = core_layer.filter(ImageFilter.GaussianBlur(2))

# screen blend onto canvas so light spills both sides
canvas = ImageChops.screen(canvas, bloom_layer)
canvas = ImageChops.screen(canvas, core_layer)
# add a touch more bloom for spill
canvas = ImageChops.screen(canvas, bloom_layer.filter(ImageFilter.GaussianBlur(22)))

# ---------- bright gold embers near torn corners ----------
ember_layer = Image.new("RGB", (W, H), (0, 0, 0))
ed = ImageDraw.Draw(ember_layer)
ember_anchors = [(ox0, oy0), (ox1, oy0), (ox0, oy1), (ox1, oy1)]
for (ax, ay) in ember_anchors:
    for _ in range(7):
        ex = ax + random.uniform(-40, 40)
        ey = ay + random.uniform(-40, 40)
        rr = random.uniform(2, 5)
        col = random.choice([LGOLD, GOLD, NEARWHITE])
        ed.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=col)
glow = ember_layer.filter(ImageFilter.GaussianBlur(6))
canvas = ImageChops.screen(canvas, glow)
canvas = ImageChops.screen(canvas, ember_layer)

# ---------- bezel inner bevel: light top-left, dark bottom-right around opening ----------
bevel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bv = ImageDraw.Draw(bevel)
bv.rounded_rectangle([ox0 - 2, oy0 - 2, ox1 + 2, oy1 + 2], radius=RAD + 2, outline=(255, 240, 210, 70), width=2)
bv.rounded_rectangle([ox0, oy0, ox1, oy1], radius=RAD, outline=(0, 0, 0, 120), width=2)
canvas = Image.alpha_composite(canvas.convert("RGBA"), bevel).convert("RGB")

# ---------- HQ / 8K gold-outline dark chips top corners ----------
def chip(cnv, x, y, text):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bbox = d.textbbox((0, 0), text, font=f_chip)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    padx, pady = 16, 9
    w = tw + padx * 2
    h = th + pady * 2
    # shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=12, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    cnv = Image.alpha_composite(cnv.convert("RGBA"), sh)
    d2 = ImageDraw.Draw(cnv)
    d2.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=(22, 22, 26, 235), outline=GOLD + (255,), width=2)
    d2.text((x + padx - bbox[0], y + pady - bbox[1]), text, font=f_chip, fill=LGOLD)
    return cnv.convert("RGB")

canvas = chip(canvas, 24, 24, "HQ")
bb = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), "8K", font=f_chip)
w8 = (bb[2] - bb[0]) + 32
canvas = chip(canvas, W - 24 - w8, 24, "8K")

# ---------- brand plaque "remAIke.IT" ----------
f_brand = load_font(26)
plaque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(plaque)
btext = "remAIke.IT"
bbb = pd.textbbox((0, 0), btext, font=f_brand)
btw = bbb[2] - bbb[0]
bth = bbb[3] - bbb[1]
ppadx, ppady = 18, 10
pw = btw + ppadx * 2
ph = bth + ppady * 2
plx = (W - pw) // 2
ply = H - INSET + 18
if ply + ph > H - 10:
    ply = H - ph - 12
pd.rounded_rectangle([plx, ply, plx + pw, ply + ph], radius=12, fill=(20, 20, 24, 230), outline=GOLD + (255,), width=2)
pd.text((plx + ppadx - bbb[0], ply + ppady - bbb[1]), btext, font=f_brand, fill=LGOLD)
canvas = Image.alpha_composite(canvas.convert("RGBA"), plaque).convert("RGB")

# ---------- save ----------
canvas.save(OUT, "PNG")
print("saved", OUT, canvas.size)
