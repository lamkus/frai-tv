import os
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
KEY = "viewfinder"
OUT_DIR = r"D:\remaike.TV\thumbnails_pilot"
OUT_PATH = os.path.join(OUT_DIR, f"CC_{KEY}.png")
os.makedirs(OUT_DIR, exist_ok=True)

# Brand colors
GOLD = (201, 169, 98)
LIGHT_GOLD = (229, 199, 138)
DARK_GOLD = (168, 139, 74)
LIME = (132, 204, 22)

# ---------- Fetch test frame ----------
VID = "JzJrH43etPA"
frame = None
for q in ("maxresdefault", "sddefault", "hqdefault"):
    try:
        url = f"https://i.ytimg.com/vi/{VID}/{q}.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        frame = Image.open(BytesIO(data)).convert("RGB")
        print(f"Fetched {q}: {frame.size}")
        break
    except Exception as e:
        print(f"Failed {q}: {e}")

if frame is None:
    frame = Image.new("RGB", (W, H), (28, 28, 32))
    print("Using fallback solid frame")

# Cover-fit frame to 1280x720
def cover_fit(img, tw, th):
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))

base = cover_fit(frame, W, H).convert("RGBA")

# ---------- Darken overlay 18% + bottom gradient to 45% ----------
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = overlay.load()
top_a = int(255 * 0.18)
bot_a = int(255 * 0.45)
for y in range(H):
    # gradient only in bottom ~45% region, blend from top_a to bot_a
    t = y / (H - 1)
    if t < 0.55:
        a = top_a
    else:
        f = (t - 0.55) / 0.45
        a = int(top_a + (bot_a - top_a) * f)
    for x in range(W):
        od[x, y] = (0, 0, 0, a)
base = Image.alpha_composite(base, overlay)

draw = ImageDraw.Draw(base)

# ---------- Thin dark keyline at the very edge ----------
draw.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0, 230), width=3)
draw.rectangle([3, 3, W - 4, H - 4], outline=(0, 0, 0, 120), width=1)

# ---------- Viewfinder brackets ----------
ARM = 120     # arm length
THK = 10      # thickness
INSET = 28    # inset from corners

# Build each bracket on its own RGBA layer so we can add shadow + bevel cleanly.
def make_bracket(corner):
    """corner in {'tl','tr','bl','br'}. Returns (layer, paste_xy)."""
    pad = 40  # room for shadow/glow
    size = ARM + pad * 2
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Geometry: an L made of horizontal + vertical bar meeting at the bracket's outer corner.
    # We'll draw for a 'tl' corner then rotate/flip for others.
    ox = pad
    oy = pad
    # horizontal arm (goes right from corner)
    h_rect = [ox, oy, ox + ARM, oy + THK]
    # vertical arm (goes down from corner)
    v_rect = [ox, oy, ox + THK, oy + ARM]

    return layer, ld, h_rect, v_rect, (ox, oy), size, pad

def rounded_l(ld, h_rect, v_rect, fill):
    ld.rectangle(h_rect, fill=fill)
    ld.rectangle(v_rect, fill=fill)
    # small rounded outer corner cap
    r = THK // 2
    ld.ellipse([h_rect[0], h_rect[1], h_rect[0] + THK, h_rect[1] + THK], fill=fill)

# Draw a generic top-left bracket layer with shadow + bevel
def render_tl_layer():
    layer, ld, h_rect, v_rect, (ox, oy), size, pad = make_bracket('tl')

    # --- Shadow layer (soft contact shadow, offset down-right) ---
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    off = 6
    sh_h = [h_rect[0] + off, h_rect[1] + off, h_rect[2] + off, h_rect[3] + off]
    sh_v = [v_rect[0] + off, v_rect[1] + off, v_rect[2] + off, v_rect[3] + off]
    rounded_l(shd, sh_h, sh_v, (0, 0, 0, 180))
    sh = sh.filter(ImageFilter.GaussianBlur(7))

    # --- Main gold L ---
    main = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mn = ImageDraw.Draw(main)
    rounded_l(mn, h_rect, v_rect, GOLD + (255,))

    # --- Bevel highlight (light gold) on top/left edges of each arm ---
    bev = 3
    # horizontal arm top edge
    mn.rectangle([h_rect[0], h_rect[1], h_rect[2], h_rect[1] + bev], fill=LIGHT_GOLD + (255,))
    # vertical arm left edge
    mn.rectangle([v_rect[0], v_rect[1], v_rect[0] + bev, v_rect[3]], fill=LIGHT_GOLD + (255,))
    # dark edge bottom/right for 3D
    mn.rectangle([h_rect[0], h_rect[3] - bev, h_rect[2], h_rect[3]], fill=DARK_GOLD + (255,))
    mn.rectangle([v_rect[2] - bev, v_rect[1], v_rect[2], v_rect[3]], fill=DARK_GOLD + (255,))

    composed = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    composed = Image.alpha_composite(composed, sh)
    composed = Image.alpha_composite(composed, main)
    return composed, pad

tl_layer, PAD = render_tl_layer()

# Place at four corners with transforms.
# top-left
base.alpha_composite(tl_layer, (INSET - PAD, INSET - PAD))
# top-right (mirror horizontally)
tr = tl_layer.transpose(Image.FLIP_LEFT_RIGHT)
base.alpha_composite(tr, (W - INSET - (tl_layer.width - PAD), INSET - PAD))
# bottom-left (mirror vertically)
bl = tl_layer.transpose(Image.FLIP_TOP_BOTTOM)
base.alpha_composite(bl, (INSET - PAD, H - INSET - (tl_layer.height - PAD)))
# bottom-right (rotate 180)
br = tl_layer.transpose(Image.ROTATE_180)
base.alpha_composite(br, (W - INSET - (tl_layer.width - PAD), H - INSET - (tl_layer.height - PAD)))

# ---------- Fonts ----------
def load_font(size):
    for p in (r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

pill_font = load_font(34)

# ---------- Pills (HQ top-left, 8K top-right) ----------
def draw_pill(d, xy_center_anchor, text, text_color, anchor="left"):
    pad_x, pad_y = 18, 9
    bbox = d.textbbox((0, 0), text, font=pill_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw = tw + pad_x * 2
    ph = th + pad_y * 2
    if anchor == "left":
        x0 = xy_center_anchor[0]
    else:  # right
        x0 = xy_center_anchor[0] - pw
    y0 = xy_center_anchor[1]
    x1, y1 = x0 + pw, y0 + ph

    # soft shadow
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sdr = ImageDraw.Draw(shadow)
    sdr.rounded_rectangle([x0, y0 + 3, x1, y1 + 3], radius=ph // 2, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    base.alpha_composite(shadow)

    d2 = ImageDraw.Draw(base)
    d2.rounded_rectangle([x0, y0, x1, y1], radius=ph // 2, fill=(18, 18, 20, 235))
    d2.rounded_rectangle([x0, y0, x1, y1], radius=ph // 2, outline=GOLD + (180,), width=2)
    d2.text((x0 + pad_x - bbox[0], y0 + pad_y - bbox[1]), text, font=pill_font, fill=text_color)
    return (x0, y0, x1, y1)

# place pills just inside the bracket corners
draw_pill(draw, (INSET + ARM + 24, INSET + 6), "HQ", (255, 255, 255, 255), anchor="left")
draw_pill(draw, (W - INSET - ARM - 24, INSET + 6), "8K", LIGHT_GOLD + (255,), anchor="right")

# ---------- Brand plaque ----------
plaque_font = load_font(28)
btext = "remAIke.IT"
bbox = draw.textbbox((0, 0), btext, font=plaque_font)
btw = bbox[2] - bbox[0]
bth = bbox[3] - bbox[1]
ppad = 14
px0 = INSET + ARM + 24
py0 = H - INSET - 6 - (bth + ppad * 2)
px1 = px0 + btw + ppad * 2
py1 = py0 + bth + ppad * 2

pl_shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
pls = ImageDraw.Draw(pl_shadow)
pls.rounded_rectangle([px0, py0 + 3, px1, py1 + 3], radius=10, fill=(0, 0, 0, 150))
pl_shadow = pl_shadow.filter(ImageFilter.GaussianBlur(5))
base.alpha_composite(pl_shadow)

draw = ImageDraw.Draw(base)
draw.rounded_rectangle([px0, py0, px1, py1], radius=10, fill=(18, 18, 20, 230))
draw.rounded_rectangle([px0, py0, px1, py1], radius=10, outline=GOLD + (200,), width=2)
# lime accent dot
draw.ellipse([px0 + ppad - 2, (py0 + py1) // 2 - 3, px0 + ppad + 4, (py0 + py1) // 2 + 3], fill=LIME + (255,))
draw.text((px0 + ppad - bbox[0], py0 + ppad - bbox[1]), btext, font=plaque_font, fill=LIGHT_GOLD + (255,))

# ---------- Save ----------
final = base.convert("RGB")
final.save(OUT_PATH, "PNG")
print(f"Saved: {OUT_PATH}  size={final.size}")
