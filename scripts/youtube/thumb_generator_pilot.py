# -*- coding: utf-8 -*-
"""Thumbnail-Generator-Pilot: echtes Frame + Marken-Rand + 8K-Badge + fetter Text. Erzeugt 3 Beispiele (Superman/Wochenschau/Alfred)."""
import io, sys, json, re, os, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT = 'thumbnails_pilot'
os.makedirs(OUT, exist_ok=True)
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
data = urllib.parse.urlencode({'client_id': o['client_id'], 'client_secret': o['client_secret'],
    'refresh_token': o['refresh_token'], 'grant_type': 'refresh_token'}).encode()
tok = json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())['access_token']
up = json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true', headers={'Authorization': f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids = []; nx = None
while True:
    u = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50' + (f'&pageToken={nx}' if nx else '')
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': f'Bearer {tok}'})).read())
    ids += [i['contentDetails']['videoId'] for i in d['items']]; nx = d.get('nextPageToken')
    if not nx: break
ids = list(dict.fromkeys(ids))
V = []
for i in range(0, len(ids), 50):
    V += json.loads(urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={",".join(ids[i:i+50])}', headers={'Authorization': f'Bearer {tok}'})).read())['items']

def pick(kw):
    # waehle ein Video mit guter (heller) Vorschau: bevorzugt mit maxres, ueberspringt Drafts
    cands = [v for v in V if kw.lower() in v['snippet']['title'].lower()]
    return cands[len(cands)//2] if cands else None  # mittiges statt erstes (oft besseres Frame)
SERIES = [
    ('Superman','Superman','SUPERMAN'), ('Wochenschau','Deutsche Wochenschau Nr.','WOCHENSCHAU'),
    ('Alfred','Alfred J. Kwak','ALFRED J. KWAK'), ('BettyBoop','Betty Boop','BETTY BOOP'),
    ('Felix','Felix','FELIX THE CAT'), ('Popeye','Popeye','POPEYE'), ('Casper','Casper','CASPER'),
    ('Soundies','Soundie','SOUNDIES'), ('Looney','Looney','LOONEY TUNES'), ('Maulwurf','Maulwurf','DER MAULWURF'),
]
samples = [(lbl, pick(kw), ov) for lbl, kw, ov in SERIES]

# Fonts (Windows)
def font(sz, bold=True):
    for f in ([r'C:\Windows\Fonts\impact.ttf'] if bold else []) + [r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\arial.ttf']:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, sz)
            except: pass
    return ImageFont.load_default()

GOLD = (201, 169, 98)        # #c9a962 remaike.IT Gold (Kern)
GOLD_LIGHT = (229, 199, 138) # #e5c78a Hell-Gold
GOLD_DARK = (166, 138, 77)   # #a68a4d Dunkel-Gold
def make_thumb(vid, label, overlay_text):
    # hole bestes verfuegbares Standbild
    img = None
    for q in ['maxresdefault', 'sddefault', 'hqdefault']:
        try:
            raw = urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{q}.jpg', timeout=15).read()
            img = Image.open(io.BytesIO(raw)).convert('RGB'); break
        except: continue
    if img is None: return None
    M, RAD = 16, 28  # Bezel + Eck-Radius (rund/eingebettet)
    iw, ih = 1280-2*M, 720-2*M
    frame = img.resize((iw, ih), Image.LANCZOS)
    frame = ImageEnhance.Contrast(frame).enhance(1.12)
    frame = ImageEnhance.Color(frame).enhance(1.15)
    fmask = Image.new('L', (iw, ih), 0)
    ImageDraw.Draw(fmask).rounded_rectangle([0, 0, iw-1, ih-1], radius=RAD, fill=255)
    canvas = Image.new('RGB', (1280, 720), (13, 13, 15))  # YouTube-Dark Bezel (verschmilzt)
    canvas.paste(frame, (M, M), fmask)
    img = canvas
    d = ImageDraw.Draw(img, 'RGBA')
    # 3-Ton-Gold runder Marken-Rahmen entlang der Frame-Kante
    d.rounded_rectangle([M-2, M-2, 1280-M+1, 720-M+1], radius=RAD+2, outline=GOLD_DARK, width=2)
    d.rounded_rectangle([M, M, 1280-M-1, 720-M-1], radius=RAD, outline=GOLD, width=4)
    d.rounded_rectangle([M+4, M+4, 1280-M-5, 720-M-5], radius=RAD-4, outline=GOLD_LIGHT, width=1)
    # Badges innerhalb der runden Ecken (werden nie abgeschnitten)
    bf = font(58); bh_ = 84; by = M+16
    tb = d.textbbox((0, 0), '8K', font=bf); bw_ = tb[2]-tb[0]+44; bx = 1280-M-bw_-16
    d.rounded_rectangle([bx, by, bx+bw_, by+bh_], radius=16, fill=(8, 8, 10, 230), outline=GOLD, width=3)
    d.text((bx+22, by+8), '8K', font=bf, fill=(255, 255, 255))
    ht = d.textbbox((0, 0), 'HQ', font=bf); hbw = ht[2]-ht[0]+44; hbx = M+16
    d.rounded_rectangle([hbx, by, hbx+hbw, by+bh_], radius=16, fill=(8, 8, 10, 230), outline=GOLD, width=3)
    d.text((hbx+22, by+8), 'HQ', font=bf, fill=(255, 255, 255))
    path = os.path.join(OUT, f'{label}_{vid}.png')
    img.save(path, 'PNG')
    return path

for label, v, ov in samples:
    if not v: print(f'{label}: kein Video gefunden'); continue
    t = v['snippet']['title']
    if label == 'Wochenschau':
        m = re.search(r'Nr\.?\s*(\d+)', t); ov = f"WOCHENSCHAU {m.group(1) if m else ''}".strip()
    p = make_thumb(v['id'], label, ov)
    print(f'{label}: {p}  <- "{t[:50]}"')
print(f'\\nFertig. PNGs in {OUT}/ (1280x720, upload-ready via thumbnails.set API)')
