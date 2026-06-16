import os
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "archiveseal"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_" + KEY + ".png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Brand colors
GOLD = (201, 169, 98)
LGOLD = (229, 199, 138)
DGOLD = (168, 139, 74)
LIME = (132, 204, 22)

# ---------- helpers ----------

def load_font(size, bold=True):
    paths = [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def load_font_arialbd(size):
    p = r"C:\Windows\Fonts\arialbd.ttf"
    if os.path.exists(p):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp(top, bottom, t)
        for x in range(w):
            px[x, y] = c
    return img

def radial_grad(size, inner, outer, cx, cy, radius):
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / radius
            t = min(1.0, d)
            px[x, y] = lerp(inner, outer, t)
    return img

# ---------- fetch test frame ----------

def fetch_frame():
    vid = "JzJrH43etPA"
    for q in ["maxresdefault", "sddefault", "hqdefault"]:
        url = "https://i.ytimg.com/vi/%s/%s.jpg" % (vid, q)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            tmp = os.path.join(os.path.dirname(OUT), "_tmp_frame.jpg")
            with open(tmp, "wb") as f:
                f.write(data)
            im = Image.open(tmp).convert("RGB")
            print("Fetched frame:", q, im.size)
            return im
        except Exception as e:
            print("fail", q, e)
    return None

frame = fetch_frame()
if frame is None:
    frame = vgrad((640, 360), (40, 50, 70), (10, 12, 20))

# ============================================================
# BUILD CANVAS
# ============================================================
base = Image.new("RGB", (W, H), (0, 0, 0))

# --- Outer dark mat / passe-partout: deep neutral textured board ---
mat = vgrad((W, H), (38, 34, 28), (20, 18, 14))
base.paste(mat, (0, 0))

# subtle vignette on the mat
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-260, -200, W + 260, H + 200], fill=80)
vig = vig.filter(ImageFilter.GaussianBlur(160))
dark = Image.new("RGB", (W, H), (8, 7, 5))
base = Image.composite(base, dark, vig)

# faint paper grain on mat
import random
random.seed(7)
grain = Image.new("L", (W, H), 0)
gp = grain.load()
for i in range(140000):
    x = random.randint(0, W - 1)
    y = random.randint(0, H - 1)
    gp[x, y] = random.randint(0, 26)
# add grain via composite lighten
base = Image.composite(Image.new("RGB", (W, H), (60, 54, 44)), base, grain)

draw = ImageDraw.Draw(base, "RGBA")

# ============================================================
# RECESSED FRAME WINDOW with beveled inner edge
# ============================================================
# Mat window geometry (the beveled recess)
mx0, my0, mx1, my1 = 150, 96, 1130, 624   # outer edge of bevel
bevel = 30                                  # bevel thickness
ix0, iy0, ix1, iy1 = mx0 + bevel, my0 + bevel, mx1 - bevel, my1 - bevel  # inner window

# Draw bevel as 4 trapezoids: top/left lighter (light source top-left), bottom/right darker
def fill_poly(pts, color):
    draw.polygon(pts, fill=color)

# bevel colors
bev_tl = (108, 96, 74)   # lighter gold-brown (catching light)
bev_tl2 = (150, 134, 100)
bev_br = (18, 16, 12)    # deep shadow
bev_br2 = (40, 36, 27)

# top bevel (light)
fill_poly([(mx0, my0), (mx1, my0), (ix1, iy0), (ix0, iy0)], bev_tl2)
# left bevel (light-mid)
fill_poly([(mx0, my0), (ix0, iy0), (ix0, iy1), (mx0, my1)], bev_tl)
# bottom bevel (dark)
fill_poly([(mx0, my1), (ix0, iy1), (ix1, iy1), (mx1, my1)], bev_br)
# right bevel (dark-mid)
fill_poly([(mx1, my0), (mx1, my1), (ix1, iy1), (ix0, iy0) if False else (ix1, iy0)], bev_br2)

# thin gold liner line just inside the bevel (gallery fillet)
draw.rectangle([ix0 - 3, iy0 - 3, ix1 + 3, iy1 + 3], outline=DGOLD, width=3)
draw.rectangle([ix0 - 1, iy0 - 1, ix1 + 1, iy1 + 1], outline=LGOLD, width=1)

# ============================================================
# INNER IMAGE (the restored frame) inside the window
# ============================================================
iw, ih = ix1 - ix0, iy1 - iy0
fr = frame.copy()
# cover-fit
fr_ratio = fr.width / fr.height
win_ratio = iw / ih
if fr_ratio > win_ratio:
    nh = ih
    nw = int(nh * fr_ratio)
else:
    nw = iw
    nh = int(nw / fr_ratio)
fr = fr.resize((nw, nh), Image.LANCZOS)
ox = (nw - iw) // 2
oy = (nh - ih) // 2
fr = fr.crop((ox, oy, ox + iw, oy + ih))

# gentle archival warm tone + slight contrast
fr = Image.eval(fr, lambda v: min(255, int(v * 1.02)))
warm = Image.new("RGB", (iw, ih), (255, 244, 220))
fr = Image.blend(fr, warm, 0.06)
base.paste(fr, (ix0, iy0))

# inner shadow on the image edges (recess depth) - top & left darker rim
rim = Image.new("L", (iw, ih), 0)
rd = ImageDraw.Draw(rim)
rd.rectangle([0, 0, iw - 1, ih - 1], outline=255, width=1)
for i in range(18):
    a = int(150 * (1 - i / 18))
    rd.rectangle([i, i, iw - 1 - i, ih - 1 - i], outline=a)
rim = rim.filter(ImageFilter.GaussianBlur(6))
shadow_layer = Image.new("RGB", (iw, ih), (0, 0, 0))
img_region = base.crop((ix0, iy0, ix1, iy1))
img_region = Image.composite(shadow_layer, img_region, rim.point(lambda v: int(v * 0.5)))
base.paste(img_region, (ix0, iy0))

draw = ImageDraw.Draw(base, "RGBA")

# ============================================================
# TITLE PLAQUE on top mat (engraved brand)
# ============================================================
plq_w, plq_h = 360, 56
plq_x = W // 2 - plq_w // 2
plq_y = 22
# engraved recess
draw.rounded_rectangle([plq_x, plq_y, plq_x + plq_w, plq_y + plq_h], radius=10, fill=(26, 23, 18))
draw.rounded_rectangle([plq_x, plq_y, plq_x + plq_w, plq_y + plq_h], radius=10, outline=DGOLD, width=2)
draw.rounded_rectangle([plq_x + 1, plq_y + 1, plq_x + plq_w - 1, plq_y + 1], radius=10, outline=(70, 62, 48))
fbrand = load_font_arialbd(30)
btxt = "remAIke.IT"
bb = draw.textbbox((0, 0), btxt, font=fbrand)
bw, bh = bb[2] - bb[0], bb[3] - bb[1]
btx = plq_x + (plq_w - bw) // 2 - bb[0]
bty = plq_y + (plq_h - bh) // 2 - bb[1]
# engraved: dark shadow up-left, gold fill
draw.text((btx - 1, bty - 1), btxt, font=fbrand, fill=(12, 10, 7))
draw.text((btx + 1, bty + 1), btxt, font=fbrand, fill=(120, 102, 70))
draw.text((btx, bty), btxt, font=fbrand, fill=LGOLD)
# subtitle small
fsub = load_font_arialbd(13)
stxt = "ARCHIVE MASTER"
sbb = draw.textbbox((0, 0), stxt, font=fsub)
sw = sbb[2] - sbb[0]
# (place inside? plaque small - skip if no room) -> put below plaque on mat
draw.text((W // 2 - sw // 2, plq_y + plq_h + 4), stxt, font=fsub, fill=(150, 134, 100))

# ============================================================
# WAX SEAL EMBLEM bottom-left (dimensional gold)
# ============================================================
SEAL = 230
sd = SEAL
seal = Image.new("RGBA", (sd, sd), (0, 0, 0, 0))
sdr = ImageDraw.Draw(seal)
cx = cy = sd // 2
R = sd // 2 - 6

# drop shadow (rendered onto base first, below)
# Build seal disc with radial gold gradient (lit top-left)
disc = radial_grad((sd, sd), LGOLD, DGOLD, cx - R * 0.35, cy - R * 0.35, R * 1.6).convert("RGBA")
mask = Image.new("L", (sd, sd), 0)
ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
seal.paste(disc, (0, 0), mask)
sdr = ImageDraw.Draw(seal)

# scalloped/serrated wax edge (small bumps)
bumps = 48
for i in range(bumps):
    ang = 2 * math.pi * i / bumps
    bx = cx + math.cos(ang) * (R + 4)
    by = cy + math.sin(ang) * (R + 4)
    # light or dark depending on angle relative to top-left light
    lit = (math.cos(ang - math.radians(225)) + 1) / 2
    bc = lerp(DGOLD, LGOLD, lit)
    sdr.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=bc + (255,))
# re-overlay disc top so bumps sit behind
seal2 = Image.new("RGBA", (sd, sd), (0, 0, 0, 0))
seal2.paste(seal, (0, 0))
# paste main disc again on top
md = disc.copy()
seal2.paste(md, (0, 0), mask)
seal = seal2
sdr = ImageDraw.Draw(seal)

# bevel rim: light arc top-left, dark arc bottom-right
sdr.arc([cx - R, cy - R, cx + R, cy + R], start=135, end=315, fill=LGOLD + (255,), width=5)
sdr.arc([cx - R, cy - R, cx + R, cy + R], start=-45, end=135, fill=(120, 98, 60, 255), width=5)

# concentric rings
sdr.ellipse([cx - R + 12, cy - R + 12, cx + R - 12, cy + R - 12], outline=DGOLD + (255,), width=3)
sdr.ellipse([cx - R + 16, cy - R + 16, cx + R - 16, cy + R - 16], outline=LGOLD + (200,), width=1)
innerR = R - 46
sdr.ellipse([cx - innerR, cy - innerR, cx + innerR, cy + innerR], outline=DGOLD + (255,), width=3)
sdr.ellipse([cx - innerR + 3, cy - innerR + 3, cx + innerR - 3, cy + innerR - 3], outline=(120, 98, 60, 220), width=1)

# circular text around (top: remAIke.IT, bottom: 8K RESTORED)
def draw_arc_text(target, text, radius, center, start_deg, end_deg, font, color, flip=False):
    n = len(text)
    if n == 0:
        return
    span = end_deg - start_deg
    for i, ch in enumerate(text):
        t = i / max(1, n - 1)
        ang = math.radians(start_deg + span * t)
        # create char image rotated tangentially
        chimg = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        cd = ImageDraw.Draw(chimg)
        cb = cd.textbbox((0, 0), ch, font=font)
        cw = cb[2] - cb[0]
        chh = cb[3] - cb[1]
        cd.text((20 - cw // 2 - cb[0], 20 - chh // 2 - cb[1]), ch, font=font, fill=color)
        rot = -math.degrees(ang) - 90
        if flip:
            rot += 180
        chimg = chimg.rotate(rot, resample=Image.BICUBIC, center=(20, 20))
        px = center[0] + math.cos(ang) * radius - 20
        py = center[1] + math.sin(ang) * radius - 20
        target.alpha_composite(chimg, (int(px), int(py)))

farc = load_font_arialbd(20)
# top text (remAIke.IT) spanning upper arc, baseline outward
draw_arc_text(seal, "remAIke.IT", R - 30, (cx, cy), 200, 340, farc, LGOLD + (255,))
# bottom text (8K RESTORED) lower arc, flipped to read upright
draw_arc_text(seal, "8K RESTORED", R - 30, (cx, cy), 160, 20, farc, LGOLD + (255,), flip=True)

sdr = ImageDraw.Draw(seal)
# center emblem: stylized "AI" monogram + star
fcen = load_font(46)
mono = "AI"
mb = sdr.textbbox((0, 0), mono, font=fcen)
mw = mb[2] - mb[0]
mh = mb[3] - mb[1]
mtx = cx - mw // 2 - mb[0]
mty = cy - mh // 2 - mb[1] - 4
sdr.text((mtx - 2, mty - 2), mono, font=fcen, fill=(120, 98, 60, 255))
sdr.text((mtx + 1, mty + 1), mono, font=fcen, fill=(255, 246, 220, 230))
sdr.text((mtx, mty), mono, font=fcen, fill=LGOLD + (255,))
# small stars flanking
fst = load_font_arialbd(18)
for sx in (cx - 70, cx + 70):
    sdr.text((sx - 5, cy + 30), "*", font=fst, fill=LGOLD + (255,))
# small ribbon text under monogram
frib = load_font_arialbd(15)
rib = "8K"
rbb = sdr.textbbox((0, 0), rib, font=frib)
rw = rbb[2] - rbb[0]
sdr.text((cx - rw // 2 - rbb[0], cy + 26), rib, font=frib, fill=(60, 48, 28, 255))

# place seal on base with drop shadow (bottom-left)
seal_x, seal_y = 70, H - sd - 40
# shadow
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shm = Image.new("L", (sd, sd), 0)
ImageDraw.Draw(shm).ellipse([6, 10, sd - 2, sd + 2], fill=170)
shm = shm.filter(ImageFilter.GaussianBlur(14))
sh.paste((0, 0, 0, 170), (seal_x + 8, seal_y + 14), shm)
base_rgba = base.convert("RGBA")
base_rgba.alpha_composite(sh)
base_rgba.alpha_composite(seal, (seal_x, seal_y))
base = base_rgba.convert("RGB")

draw = ImageDraw.Draw(base, "RGBA")

# ============================================================
# HQ / 8K engraved-gold badges (corners of mat)
# ============================================================
def engraved_badge(x, y, text, w=84, h=46):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=9, fill=(24, 21, 16, 255))
    draw.rounded_rectangle([x, y, x + w, y + h], radius=9, outline=DGOLD, width=2)
    draw.rounded_rectangle([x + 1, y + 1, x + w - 1, y + 2], radius=9, outline=(78, 68, 50))
    f = load_font_arialbd(26)
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    tx = x + (w - tw) // 2 - bb[0]
    ty = y + (h - th) // 2 - bb[1]
    draw.text((tx - 1, ty - 1), text, font=f, fill=(10, 8, 5))
    draw.text((tx, ty), text, font=f, fill=LGOLD)

engraved_badge(40, 30, "HQ")
engraved_badge(W - 40 - 84, 30, "8K")

# ============================================================
# keep bottom-right ~210x52 clear (YouTube duration pill) - it's mat, fine
# ============================================================

# final subtle global vignette for premium feel
fv = Image.new("L", (W, H), 0)
ImageDraw.Draw(fv).rectangle([0, 0, W, H], fill=0)
fvd = ImageDraw.Draw(fv)
fvd.ellipse([-200, -160, W + 200, H + 160], fill=255)
fv = fv.filter(ImageFilter.GaussianBlur(120))
darkv = Image.new("RGB", (W, H), (6, 5, 4))
base = Image.composite(base, darkv, fv)

base.save(OUT, "PNG")
print("SAVED", OUT, base.size)
