import os, math, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "proscenium"
OUT = r"D:\remaike.TV\thumbnails_pilot\CC_" + KEY + ".png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---------------- Colors ----------------
GOLD = (201, 169, 98)
LGOLD = (229, 199, 138)
DGOLD = (168, 139, 74)
LIME = (132, 204, 22)
VELVET_DARK = (60, 8, 12)
VELVET = (120, 16, 22)
VELVET_LIGHT = (175, 34, 40)
STAGE_BG = (18, 10, 14)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ---------------- Fonts ----------------
def font(path_list, size):
    for p in path_list:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

IMPACT = [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
ARIALBD = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"]

f_title = font(IMPACT, 132)
f_sub = font(ARIALBD, 40)
f_marquee = font(IMPACT, 46)
f_badge = font(ARIALBD, 34)
f_now = font(IMPACT, 38)

# ---------------- Base canvas ----------------
img = Image.new("RGB", (W, H), STAGE_BG)
draw = ImageDraw.Draw(img)

# Stage background: dark radial-ish vignette with a warm center glow (the "screen")
for y in range(H):
    t = y / H
    # vertical gradient: slightly lighter middle
    base = lerp((28, 16, 20), (10, 6, 9), abs(t - 0.42) * 1.6)
    draw.line([(0, y), (W, y)], fill=base)

# Warm center glow (screen light)
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
gd.ellipse([W*0.18, H*0.10, W*0.82, H*0.92], fill=120)
glow = glow.filter(ImageFilter.GaussianBlur(140))
glow_col = Image.new("RGB", (W, H), (70, 55, 30))
img = Image.composite(glow_col, img, glow)
draw = ImageDraw.Draw(img)

# ---------------- Theater curtains (left + right) ----------------
def draw_curtain(target, x0, x1, side):
    """Draw velvet folds. Curtains slightly wider at the bottom (stage perspective)."""
    d = ImageDraw.Draw(target)
    top_w = x1 - x0
    bot_w = int(top_w * 1.18)  # wider at bottom
    n_folds = 7
    for y in range(H):
        ty = y / H
        # current width at this row
        cur_w = int(top_w + (bot_w - top_w) * ty)
        if side == "left":
            rx0 = x0
            rx1 = x0 + cur_w
        else:
            rx1 = x1
            rx0 = x1 - cur_w
        fold_w = cur_w / n_folds
        for fi in range(n_folds + 1):
            fx0 = rx0 + fi * fold_w
            fx1 = fx0 + fold_w
            # fold shading: cosine across each fold => rounded velvet look
            for px in range(int(fx0), int(fx1) + 1):
                if px < 0 or px >= W:
                    continue
                local = (px - fx0) / max(1.0, fold_w)
                shade = (math.cos(local * 2 * math.pi - math.pi) + 1) / 2  # 0..1
                # darken toward bottom slightly + vertical drape highlight
                vdark = 1.0 - ty * 0.18
                col = lerp(VELVET_DARK, VELVET_LIGHT, shade)
                col = tuple(int(c * vdark) for c in col)
                d.line([(px, y), (px, y)], fill=col)

curtain_w = 300
draw_curtain(img, 0, curtain_w, "left")
draw_curtain(img, W - curtain_w, W, "right")
draw = ImageDraw.Draw(img)

# Inner shadow edge of curtains onto the stage for depth
shadow = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(shadow)
sd.rectangle([curtain_w, 0, curtain_w + 60, H], fill=160)
sd.rectangle([W - curtain_w - 60, 0, W - curtain_w, H], fill=160)
shadow = shadow.filter(ImageFilter.GaussianBlur(40))
dark = Image.new("RGB", (W, H), (0, 0, 0))
img = Image.composite(dark, img, shadow)
draw = ImageDraw.Draw(img)

# ---------------- Gold valance / arch at top ----------------
arch_h = 150
# Scalloped valance: draw a gold band then scallop the bottom edge
for y in range(arch_h):
    t = y / arch_h
    col = lerp(LGOLD, DGOLD, t)
    draw.line([(0, y), (W, y)], fill=col)

# Scallop bottom edge of valance (cut into stage color via dark arcs)
scallops = 9
scal_w = W / scallops
for i in range(scallops):
    cx = i * scal_w + scal_w / 2
    r = scal_w * 0.62
    # arc going downward
    draw.pieslice([cx - r, arch_h - r, cx + r, arch_h + r], 0, 180, fill=STAGE_BG)
# Re-blend: the scallop fill should match the glowy stage; approximate with dark warm
# Add a thin gold bead line along scallop tops
for i in range(scallops + 1):
    cx = i * scal_w
    draw.ellipse([cx - 8, arch_h - 8, cx + 8, arch_h + 8], fill=GOLD, outline=DGOLD)

# Arch corners: small gold curved fillets hugging the curtain tops (kept tight so
# they don't bleed into the dark stage as stray half-circles)
draw.pieslice([curtain_w - 48, arch_h - 48, curtain_w + 8, arch_h + 8], 0, 90, fill=GOLD)
draw.pieslice([W - curtain_w - 8, arch_h - 48, W - curtain_w + 48, arch_h + 8], 90, 180, fill=GOLD)

# ---------------- Marquee bulbs along the arch ----------------
def glow_dot(cx, cy, r, col):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(g)
    gd2.ellipse([cx - r*2.4, cy - r*2.4, cx + r*2.4, cy + r*2.4], fill=col + (110,))
    g = g.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(g) if img.mode == "RGBA" else None
    return g

# Work in RGBA for glows
img = img.convert("RGBA")
draw = ImageDraw.Draw(img)

n_bulbs = 22
for i in range(n_bulbs):
    cx = int(40 + (W - 80) * i / (n_bulbs - 1))
    cy = 30
    # glow
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(g)
    gd2.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(255, 225, 150, 130))
    g = g.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(g)
    draw = ImageDraw.Draw(img)
    # bulb
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 240, 190, 255), outline=(180, 140, 60, 255))
    draw.ellipse([cx - 4, cy - 5, cx + 1, cy, ], fill=(255, 255, 255, 255))

# ---------------- "NOW SHOWING" small banner top-center ----------------
ns_text = "NOW SHOWING"
bbox = draw.textbbox((0, 0), ns_text, font=f_now)
ns_w = bbox[2] - bbox[0]
ns_x = (W - ns_w) // 2
ns_y = 60
# ribbon plate
draw.rounded_rectangle([ns_x - 24, ns_y - 8, ns_x + ns_w + 24, ns_y + 50], radius=10,
                       fill=(40, 8, 12, 255), outline=GOLD + (255,), width=3)
draw.text((ns_x, ns_y), ns_text, font=f_now, fill=LGOLD + (255,))

# ---------------- Title block (the feature presentation) ----------------
def text_center(d, cx, cy, txt, fnt, fill, shadow_col=(0,0,0), shadow_off=4):
    b = d.textbbox((0, 0), txt, font=fnt)
    tw, th = b[2] - b[0], b[3] - b[1]
    x = cx - tw / 2 - b[0]
    y = cy - th / 2 - b[1]
    d.text((x + shadow_off, y + shadow_off), txt, font=fnt, fill=shadow_col + (200,))
    d.text((x, y), txt, font=fnt, fill=fill + (255,))
    return tw, th

cx = W // 2
# Glow behind title
tg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
tgd = ImageDraw.Draw(tg)
text_center(tgd, cx, 360, "remAIke", f_title, (255, 220, 150))
tg = tg.filter(ImageFilter.GaussianBlur(22))
img.alpha_composite(tg)
draw = ImageDraw.Draw(img)

text_center(draw, cx, 358, "remAIke", f_title, LGOLD, (50, 8, 10), 5)
# subtitle
draw.rounded_rectangle([cx - 240, 440, cx + 240, 500], radius=12, fill=(20, 10, 14, 230),
                       outline=GOLD + (255,), width=2)
text_center(draw, cx, 470, "THE FEATURE PRESENTATION", f_sub, LIME, (0,0,0), 2)

# ---------------- Gold marquee plate "remAIke.IT" bottom-center ----------------
plate_text = "remAIke.IT"
b = draw.textbbox((0, 0), plate_text, font=f_marquee)
pw = b[2] - b[0]
px0 = cx - pw // 2 - 40
px1 = cx + pw // 2 + 40
py0, py1 = 560, 640
# plate gradient
plate = Image.new("RGBA", (px1 - px0, py1 - py0), (0, 0, 0, 0))
pd = ImageDraw.Draw(plate)
for y in range(py1 - py0):
    t = y / (py1 - py0)
    col = lerp(LGOLD, DGOLD, t)
    pd.line([(0, y), (px1 - px0, y)], fill=col + (255,))
mask = Image.new("L", (px1 - px0, py1 - py0), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, px1 - px0 - 1, py1 - py0 - 1], radius=14, fill=255)
img.paste(plate, (px0, py0), mask)
draw = ImageDraw.Draw(img)
# bevel
draw.rounded_rectangle([px0, py0, px1, py1], radius=14, outline=(255, 240, 200, 255), width=2)
draw.rounded_rectangle([px0+3, py0+3, px1-3, py1-3], radius=12, outline=(120, 90, 40, 200), width=2)
# bulbs around plate
for i in range(int((px1 - px0) / 34) + 1):
    bx = px0 + 14 + i * 34
    for by in (py0 + 8, py1 - 8):
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 245, 200, 255))
text_center(draw, cx, (py0 + py1) // 2, plate_text, f_marquee, (60, 30, 8), (255, 240, 200), -2)

# ---------------- Theater-style gold badges HQ / 8K ----------------
def theater_badge(d, x, y, txt, w=92, h=58):
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=(30, 8, 12, 235),
                        outline=GOLD + (255,), width=3)
    # inner gold line
    d.rounded_rectangle([x + 5, y + 5, x + w - 5, y + h - 5], radius=9,
                        outline=DGOLD + (255,), width=1)
    bb = d.textbbox((0, 0), txt, font=f_badge)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x + (w - tw) / 2 - bb[0], y + (h - th) / 2 - bb[1]), txt, font=f_badge, fill=LGOLD + (255,))

theater_badge(draw, 26, 170, "HQ")
theater_badge(draw, W - 26 - 92, 170, "8K")

# ---------------- Final corner vignette ----------------
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], fill=0)
vd.ellipse([-200, -200, W + 200, H + 200], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(120))
black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
img = Image.composite(img, black, vig)

img = img.convert("RGB")
img.save(OUT, "PNG")
print("SAVED", OUT, img.size)
