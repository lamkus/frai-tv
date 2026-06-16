# -*- coding: utf-8 -*-
"""Rollout: generiert Marken-Thumbnail (Frame + 3-Ton-Gold-Rand + 8K/HQ-Badges, KEIN Text) fuer alle Videos und laedt via thumbnails.set hoch. Resume- + quota-sicher. Dunkle Frames werden geflaggt (trotzdem hochgeladen, da nie schlechter als Auto-Frame)."""
import io, sys, json, os, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageStat

o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
def token():
    data = urllib.parse.urlencode({'client_id': o['client_id'], 'client_secret': o['client_secret'],
        'refresh_token': o['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())['access_token']
tok = token(); print('[AUTH] OK')

GOLD=(201,169,98); GOLD_LIGHT=(229,199,138); GOLD_DARK=(166,138,77)
def font(sz):
    for f in [r'C:\Windows\Fonts\impact.ttf', r'C:\Windows\Fonts\arialbd.ttf']:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, sz)
            except: pass
    return ImageFont.load_default()

def build(vid):
    img=None
    for q in ['maxresdefault','sddefault','hqdefault']:
        try:
            raw=urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{q}.jpg',timeout=15).read()
            img=Image.open(io.BytesIO(raw)).convert('RGB'); break
        except: continue
    if img is None: return None, None
    img=img.resize((1280,720),Image.LANCZOS)
    bright=ImageStat.Stat(img.convert('L')).mean[0]
    img=ImageEnhance.Contrast(img).enhance(1.12); img=ImageEnhance.Color(img).enhance(1.15)
    d=ImageDraw.Draw(img,'RGBA')
    pos=0
    for col,wd in [(GOLD_LIGHT,3),(GOLD,4),(GOLD_DARK,3)]:
        for k in range(wd): d.rectangle([pos+k,pos+k,1279-pos-k,719-pos-k],outline=col,width=1)
        pos+=wd
    d.rectangle([pos,pos,1279-pos,719-pos],outline=(18,18,22),width=2)
    bf=font(66); bh_=96
    tb=d.textbbox((0,0),'8K',font=bf); bw_=tb[2]-tb[0]+52; bx=1280-bw_-28
    d.rounded_rectangle([bx,26,bx+bw_,26+bh_],radius=14,fill=(8,8,10,220),outline=GOLD,width=3)
    d.text((bx+26,36),'8K',font=bf,fill=(255,255,255))
    ht=d.textbbox((0,0),'HQ',font=bf); hbw=ht[2]-ht[0]+52
    d.rounded_rectangle([28,26,28+hbw,26+bh_],radius=14,fill=(8,8,10,220),outline=GOLD,width=3)
    d.text((28+26,36),'HQ',font=bf,fill=(255,255,255))
    buf=io.BytesIO(); img.save(buf,'PNG'); return buf.getvalue(), bright

def upload(vid, png):
    req=urllib.request.Request(f'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media',
        data=png, headers={'Authorization':f'Bearer {tok}','Content-Type':'image/png'}, method='POST')
    urllib.request.urlopen(req)

# alle public videos
up=json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true',headers={'Authorization':f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];nx=None
while True:
    u=f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50'+(f'&pageToken={nx}' if nx else '')
    d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {tok}'})).read())
    ids+=[i['contentDetails']['videoId'] for i in d['items']];nx=d.get('nextPageToken')
    if not nx:break
ids=list(dict.fromkeys(ids))
stat={};
for i in range(0,len(ids),50):
    for v in json.loads(urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=status&id={",".join(ids[i:i+50])}',headers={'Authorization':f'Bearer {tok}'})).read())['items']:
        stat[v['id']]=v['status']['privacyStatus']
pub=[i for i in ids if stat.get(i)=='public']

PROG='config/thumb_rollout_progress.json'; DARK='config/thumb_dark_flagged.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
dark=set(json.load(open(DARK))) if os.path.exists(DARK) else set()
todo=[i for i in pub if i not in done]
print(f'[PLAN] {len(pub)} public, {len(done)} fertig, {len(todo)} offen')

ok=err=darkn=0; quota=False
for n,vid in enumerate(todo,1):
    try:
        png,bright=build(vid)
        if png is None: err+=1; continue
        if bright is not None and bright<60: dark.add(vid); darkn+=1
        upload(vid,png); done.add(vid); ok+=1
        if ok%20==0:
            print(f'  [{ok}/{len(todo)}] hochgeladen (dunkel geflaggt: {darkn})')
            json.dump(sorted(done),open(PROG,'w')); json.dump(sorted(dark),open(DARK,'w'))
        time.sleep(0.4)
    except urllib.error.HTTPError as e:
        body=e.read().decode()[:160]
        if 'quotaExceeded' in body or e.code==403 and 'quota' in body.lower():
            print(f'  [QUOTA] erreicht nach {ok} Uploads - morgen resume.'); quota=True; break
        err+=1; print(f'  ERR {vid}: {body[:90]}')
    except Exception as e:
        err+=1; print(f'  ERR {vid}: {str(e)[:90]}')

json.dump(sorted(done),open(PROG,'w')); json.dump(sorted(dark),open(DARK,'w'))
print(f'\n=== {ok} hochgeladen, {err} Fehler, {darkn} dunkle geflaggt, {len(todo)-ok-err} offen{" (QUOTA)" if quota else ""} ===')
print(f'Fortschritt: {PROG} ({len(done)}/{len(pub)}) | Dunkle (spaeter besseres Frame): {DARK} ({len(dark)})')
