# -*- coding: utf-8 -*-
"""Light-Mode-Prototyp: schwebende Karte (runde Ecken + weicher Schatten + nativer Pill-Badge-Stil),
gerendert + auf hellem YouTube-Hintergrund als Vorschau (Embedding-Effekt sichtbar)."""
import io, sys, json, os, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

OUT = 'thumbnails_pilot'; os.makedirs(OUT, exist_ok=True)
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
data = urllib.parse.urlencode({'client_id': o['client_id'], 'client_secret': o['client_secret'],
    'refresh_token': o['refresh_token'], 'grant_type': 'refresh_token'}).encode()
tok = json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())['access_token']

GOLD=(201,169,98); GOLD_L=(229,199,138); GOLD_D=(166,138,77)
PAGE_LIGHT=(249,249,249)  # YouTube Light-Mode bg
def font(sz):
    for f in [r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\impact.ttf']:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, sz)
            except: pass
    return ImageFont.load_default()

def get_frame(vid):
    for q in ['maxresdefault','sddefault','hqdefault']:
        try: return Image.open(io.BytesIO(urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{q}.jpg',timeout=15).read())).convert('RGB')
        except: continue
    return None

def native_pill(d, x, y, text, fnt):
    tb = d.textbbox((0,0), text, font=fnt); tw = tb[2]-tb[0]; th = tb[3]-tb[1]
    pad = 16; w = tw+pad*2; h = th+18
    d.rounded_rectangle([x, y, x+w, y+h], radius=h//2, fill=(15,15,15,200))  # YT-natives dunkles Pill
    d.text((x+pad, y+7), text, font=fnt, fill=(255,255,255))
    return w

def make_lightcard(vid):
    src = get_frame(vid)
    if src is None: return None
    M, RAD = 22, 30
    iw, ih = 1280-2*M, 720-2*M
    frame = src.resize((iw, ih), Image.LANCZOS)
    frame = ImageEnhance.Contrast(frame).enhance(1.1); frame = ImageEnhance.Color(frame).enhance(1.12)
    rmask = Image.new('L',(iw,ih),0); ImageDraw.Draw(rmask).rounded_rectangle([0,0,iw-1,ih-1],radius=RAD,fill=255)
    # Canvas = Light-Page-Farbe (verschmilzt auf heller YT-Seite)
    canvas = Image.new('RGB',(1280,720),PAGE_LIGHT)
    # weicher Schatten unter der Karte (Lift-Effekt)
    sh = Image.new('RGBA',(1280,720),(0,0,0,0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([M+6, M+14, 1280-M+6, 720-M+14], radius=RAD, fill=(60,55,45,120))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); canvas.paste(sh,(0,0),sh)
    canvas.paste(frame,(M,M),rmask)
    d = ImageDraw.Draw(canvas,'RGBA')
    # feiner Gold-Rahmen (duenn, premium)
    d.rounded_rectangle([M,M,1280-M-1,720-M-1],radius=RAD,outline=GOLD,width=3)
    d.rounded_rectangle([M+3,M+3,1280-M-4,720-M-4],radius=RAD-3,outline=(255,245,215,110),width=1)
    # native Pills: HQ links, 8K rechts
    pf = font(46)
    native_pill(d, M+18, M+18, 'HQ', pf)
    w8 = d.textbbox((0,0),'8K',font=pf); pad=16; w=(w8[2]-w8[0])+pad*2
    native_pill(d, 1280-M-18-w, M+18, '8K', pf)
    canvas.save(os.path.join(OUT,f'LIGHT_{vid}.png'),'PNG')
    # Vorschau: Karte auf heller YT-Seite (Embedding sichtbar)
    prev = Image.new('RGB',(1480,920),PAGE_LIGHT); prev.paste(canvas,(100,100))
    pd = ImageDraw.Draw(prev)
    pd.text((100,40),'  Vorschau: so sitzt es im YouTube Light-Mode-Feed', font=font(30), fill=(40,40,40))
    pp = os.path.join(OUT,f'LIGHT_PREVIEW_{vid}.png'); prev.save(pp,'PNG')
    return pp

# alle public videos holen, 2 helle Beispiele
up=json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true',headers={'Authorization':f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];nx=None
while True:
    u=f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,snippet&playlistId={up}&maxResults=50'+(f'&pageToken={nx}' if nx else '')
    dd=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {tok}'})).read())
    ids+=[(i['contentDetails']['videoId'], i['snippet']['title']) for i in dd['items']]; nx=dd.get('nextPageToken')
    if not nx:break
def pick(kw):
    for vid,t in ids:
        if kw.lower() in t.lower(): return vid
    return None
for kw in ['Popeye','Betty Boop']:
    vid=pick(kw)
    if vid: print(f'{kw}: {make_lightcard(vid)}')
