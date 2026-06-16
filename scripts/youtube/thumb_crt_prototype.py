# -*- coding: utf-8 -*-
"""CRT-Roehren-TV-Rahmen mit 3D-Tiefe: Holz-Gehaeuse, versenkter Glas-Bildschirm (Vignette/Scanlines/Glanz),
Bedienpanel mit Drehknoepfen + Marken-Plakette, OSD-Badges. Pillow-only."""
import io, sys, json, os, math, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

OUT='thumbnails_pilot'; os.makedirs(OUT, exist_ok=True)
o=json.load(open('config/youtube_oauth.json',encoding='utf-8'))
tok=json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
    urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
GOLD=(201,169,98)
def font(sz,bold=True):
    for f in ([r'C:\Windows\Fonts\impact.ttf'] if bold else [])+[r'C:\Windows\Fonts\arialbd.ttf',r'C:\Windows\Fonts\arial.ttf']:
        if os.path.exists(f):
            try: return ImageFont.truetype(f,sz)
            except: pass
    return ImageFont.load_default()
def vgrad(w,h,top,bot):
    g=Image.new('RGB',(1,h))
    for y in range(h):
        f=y/h; g.putpixel((0,y),tuple(int(top[i]+(bot[i]-top[i])*f) for i in range(3)))
    return g.resize((w,h))
def get_frame(vid):
    for q in ['maxresdefault','sddefault','hqdefault']:
        try: return Image.open(io.BytesIO(urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{q}.jpg',timeout=15).read())).convert('RGB')
        except: continue
    return None

def make_crt(vid):
    src=get_frame(vid)
    if src is None: return None
    W,H=1280,720
    # --- Gehaeuse: dunkles Walnuss-Holz mit Maserung + 3D-Form ---
    cab=vgrad(W,H,(74,52,34),(34,22,13))
    dc=ImageDraw.Draw(cab)
    for y in range(0,H,3):  # Holzmaserung (feine Streifen)
        shade=int(12*math.sin(y*0.07)+6*math.sin(y*0.31))
        dc.line([(0,y),(W,y)],fill=(max(0,52+shade),max(0,36+shade),max(0,22+shade)),width=1)
    # Aussen-Bevel (3D-Box): hell oben/links, dunkel unten/rechts
    dc.line([(0,0),(W,0)],fill=(120,92,64),width=4); dc.line([(0,0),(0,H)],fill=(104,78,52),width=4)
    dc.line([(0,H-1),(W,H-1)],fill=(14,9,5),width=5); dc.line([(W-1,0),(W-1,H)],fill=(18,12,7),width=5)
    img=cab; d=ImageDraw.Draw(img,'RGBA')
    # --- Bildschirm-Geometrie (versenkt) ---
    SX1,SY1,SX2,SY2=72,52,1208,604; R=66
    # versenkter Rahmen: Schatten oben/links, Glanz unten/rechts
    d.rounded_rectangle([SX1-10,SY1-10,SX2+10,SY2+10],radius=R+10,fill=(20,14,9))
    d.arc([SX1-10,SY1-10,SX2+10,SY2+10],90,270,fill=(10,7,4),width=8)      # Schatten oben-links
    d.arc([SX1-10,SY1-10,SX2+10,SY2+10],270,90,fill=(120,96,66),width=4)   # Glanz unten-rechts
    # --- Video ins Glas ---
    sw,sh=SX2-SX1,SY2-SY1
    fr=src.resize((sw,sh),Image.LANCZOS)
    fr=ImageEnhance.Contrast(fr).enhance(1.14); fr=ImageEnhance.Color(fr).enhance(1.2); fr=ImageEnhance.Brightness(fr).enhance(1.05)
    fd=ImageDraw.Draw(fr,'RGBA')
    # Scanlines
    for y in range(0,sh,3): fd.line([(0,y),(sw,y)],fill=(0,0,0,38),width=1)
    # Vignette (CRT dunkler am Rand)
    vig=Image.new('L',(sw,sh),0); ImageDraw.Draw(vig).ellipse([-sw*0.12,-sh*0.12,sw*1.12,sh*1.12],fill=255)
    vig=vig.filter(ImageFilter.GaussianBlur(70))
    fr=Image.composite(fr,Image.new('RGB',(sw,sh),(0,0,0)),vig)
    # Glas-Glanz (weicher Sweep oben-links)
    gl=Image.new('L',(sw,sh),0); ImageDraw.Draw(gl).ellipse([-sw*0.3,-sh*0.5,sw*0.7,sh*0.35],fill=70)
    gl=gl.filter(ImageFilter.GaussianBlur(60))
    fr=Image.composite(Image.new('RGB',(sw,sh),(255,255,255)),fr,gl)
    # runde Glas-Ecken
    gm=Image.new('L',(sw,sh),0); ImageDraw.Draw(gm).rounded_rectangle([0,0,sw-1,sh-1],radius=R,fill=255)
    img.paste(fr,(SX1,SY1),gm)
    d=ImageDraw.Draw(img,'RGBA')
    d.rounded_rectangle([SX1,SY1,SX2,SY2],radius=R,outline=(8,8,10),width=3)
    d.line([(SX1+40,SY1+3),(SX2-40,SY1+3)],fill=(255,255,255,90),width=2)  # Glas-Kante oben
    # --- Bedienpanel unten ---
    d.rectangle([0,SY2+16,W,H],fill=(46,32,20))
    # Lautsprecher-Grill links
    for gx in range(70,330,12): d.line([(gx,SY2+34),(gx,H-22)],fill=(26,18,11),width=4)
    # Marken-Plakette
    d.rounded_rectangle([360,SY2+34,720,H-26],radius=10,fill=(20,14,9),outline=GOLD,width=2)
    _brand='remAIke.IT'; _bf=font(44,bold=False)
    try: _bw=d.textlength(_brand,font=_bf)
    except: _bw=210
    d.text((360+(360-_bw)/2, SY2+40), _brand, font=_bf, fill=GOLD)
    # Drehknoepfe rechts (3D)
    for kx in (1010,1150):
        d.ellipse([kx-34,SY2+32,kx+34,H-22],fill=(28,20,12),outline=(12,8,5),width=2)
        d.ellipse([kx-30,SY2+36,kx+22,H-30],fill=(70,52,34))  # Glanz oben-links
        d.ellipse([kx-26,SY2+40,kx+18,H-34],fill=(40,28,17))
        d.line([(kx,SY2+44),(kx,SY2+60)],fill=(200,180,140),width=3)
    # Power-LED
    d.ellipse([900,SY2+58,918,SY2+76],fill=(120,255,120)); d.ellipse([903,SY2+61,915,SY2+73],fill=(200,255,200))
    # --- OSD-Badges (wie TV-Kanalanzeige) ---
    for txt,xx in [('HQ',SX1+22),('8K',SX2-118)]:
        d.rounded_rectangle([xx,SY1+22,xx+96,SY1+94],radius=12,fill=(8,10,8,180),outline=(120,255,120,180),width=2)
        d.text((xx+16,SY1+30),txt,font=font(50),fill=(180,255,180))
    p=os.path.join(OUT,f'CRT_{vid}.png'); img.save(p,'PNG'); return p

SAMPLES=[('Wochenschau','LpM0ybqqL90'),('KenBlock','JzJrH43etPA'),('SkeletonDance','ezYIk8bReaE'),('WhiteZombie','d8Ak1R_eOlY'),('Superman','cH5VPFJFKtI')]
for kw,vid in SAMPLES:
    print(f'{kw}: {make_crt(vid)}')
