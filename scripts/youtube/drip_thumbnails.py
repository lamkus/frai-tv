# -*- coding: utf-8 -*-
"""Thumbnail-Drip fuer den GANZEN Kanal: rendert CRT-Thumbnails + laedt taeglich bis N hoch.
- Prioritaet: PRIORITY_IDS zuerst, dann alle public Videos nach Views.
- Stoppt sauber bei YouTubes Tageslimit (429) -> am naechsten Tag automatisch weiter.
- Resume-sicher (config/thumb_progress.json). DRY default; --apply schreibt.
Usage: python drip_thumbnails.py [N] [--apply]
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
N = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 10
PRIORITY_IDS = ['0AEHKJTDLYI']  # Nr. 620 zuerst

# CRT-Renderer laden
src = open('scripts/youtube/thumb_crt_prototype.py', encoding='utf-8').read()
src = src.split('SAMPLES=')[0].replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", '')
exec(src)
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
def newtok():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = newtok(); print('[AUTH] OK')

up = json.loads(urllib.request.urlopen(urllib.request.Request(
    'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true',
    headers={'Authorization':f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[]; nx=None
while True:
    u=f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50'+(f'&pageToken={nx}' if nx else '')
    d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {tok}'})).read())
    ids+=[i['contentDetails']['videoId'] for i in d['items']]; nx=d.get('nextPageToken')
    if not nx: break
ids=list(dict.fromkeys(ids))
V=[]
for i in range(0,len(ids),50):
    V+=json.loads(urllib.request.urlopen(urllib.request.Request(
        f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,status&id={",".join(ids[i:i+50])}',
        headers={'Authorization':f'Bearer {tok}'})).read())['items']
pub=[v for v in V if v['status']['privacyStatus']=='public']

PROG='config/thumb_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
prio=[v for v in pub if v['id'] in PRIORITY_IDS and v['id'] not in done]
rest=sorted([v for v in pub if v['id'] not in PRIORITY_IDS and v['id'] not in done],
            key=lambda v:int(v['statistics'].get('viewCount',0)), reverse=True)
todo=(prio+rest)[:N]
print(f'[PLAN] {len(pub)} public, {len(done)} schon mit CRT, {len(pub)-len(done)} offen -> heute bis {len(todo)} (DRY={not APPLY})')

ok=err=0; stop=False
for v in todo:
    vid=v['id']; views=v['statistics'].get('viewCount','?'); t=v['snippet']['title'][:50]
    if not APPLY:
        print(f'  [DRY]  {vid} (views {views}) {t}'); ok+=1; continue
    p=make_crt(vid)
    if not p: err+=1; print(f'  [SKIP] {vid} kein Frame'); continue
    try:
        urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media',
            data=open(p,'rb').read(), headers={'Authorization':f'Bearer {tok}','Content-Type':'image/png'}, method='POST'))
        done.add(vid); ok+=1; print(f'  [OK]   {vid} CRT gesetzt (views {views}) {t}')
        json.dump(sorted(done),open(PROG,'w')); time.sleep(1.0)
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if e.code==429 or 'rateLimitExceeded' in b or 'uploadRateLimitExceeded' in b:
            print(f'  [LIMIT] YouTube-Tageslimit nach {ok} - morgen automatisch weiter.'); stop=True; break
        if 'quotaExceeded' in b: print(f'  [QUOTA] nach {ok}.'); stop=True; break
        err+=1; print(f'  [ERR]  {vid}: HTTP {e.code} {b[:80]}')
    except Exception as e:
        err+=1; print(f'  [ERR]  {vid}: {str(e)[:70]}')
json.dump(sorted(done),open(PROG,'w'))
remaining=len(pub)-len(done)
print(f'\n=== Thumbnails: {ok} {"gesetzt" if APPLY else "(dry)"}, {err} Fehler{" (LIMIT)" if stop else ""} | gesamt CRT: {len(done)}/{len(pub)} | offen: {remaining} (~{(remaining+9)//10} Tage)')
