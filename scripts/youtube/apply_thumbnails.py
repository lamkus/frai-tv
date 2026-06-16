# -*- coding: utf-8 -*-
"""Rendert CRT-Thumbnails (aus i.ytimg-Auto-Frame) + lädt sie hoch via thumbnails.set.
Wählt die N meistgesehenen Wochenschau-Videos (dort bringt CTR am meisten).
Rate-Limit-sicher (Stop bei 429/quota), resume-sicher (config/thumb_progress.json).
Usage: python apply_thumbnails.py [N]   (default N=10)
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
N = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 10

# CRT-Renderfunktionen aus dem Prototyp laden (ohne SAMPLES-Loop / ohne stdout-Reassign)
src = open('scripts/youtube/thumb_crt_prototype.py', encoding='utf-8').read()
src = src.split('SAMPLES=')[0].replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", '')
exec(src)  # definiert: token-Variable tok, make_crt, get_frame, OUT, o ...

o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
def newtok():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = newtok(); print('[AUTH] OK')

# Wochenschau-Videos + Views holen
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
woch=[v for v in V if v['status']['privacyStatus']=='public' and ('Wochenschau' in v['snippet']['title'] or 'Tonwoche' in v['snippet']['title'])]
woch.sort(key=lambda v:int(v['statistics'].get('viewCount',0)), reverse=True)

PROG='config/thumb_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
todo=[v for v in woch if v['id'] not in done][:N]
print(f'[PLAN] {len(woch)} Wochenschau public, {len(done)} schon mit CRT, nehme Top {len(todo)} nach Views')

def upload_thumb(vid, png):
    data=open(png,'rb').read()
    req=urllib.request.Request(f'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}&uploadType=media',
        data=data, headers={'Authorization':f'Bearer {tok}','Content-Type':'image/png'}, method='POST')
    urllib.request.urlopen(req)

ok=err=0; stop=False
for v in todo:
    vid=v['id']; views=v['statistics'].get('viewCount','?')
    p=make_crt(vid)
    if not p:
        err+=1; print(f'  [SKIP] {vid} kein Frame (views {views})'); continue
    try:
        upload_thumb(vid, p)
        done.add(vid); ok+=1; print(f'  [OK]   {vid} CRT gesetzt (views {views}) | {v["snippet"]["title"][:50]}')
        json.dump(sorted(done),open(PROG,'w')); time.sleep(1.0)
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if e.code==429 or 'rateLimitExceeded' in b or 'uploadRateLimitExceeded' in b:
            print(f'  [RATE] Thumbnail-Limit erreicht nach {ok} - morgen weiter.'); stop=True; break
        if 'quotaExceeded' in b:
            print(f'  [QUOTA] erreicht nach {ok}.'); stop=True; break
        err+=1; print(f'  [ERR]  {vid}: HTTP {e.code} {b[:90]}')
    except Exception as e:
        err+=1; print(f'  [ERR]  {vid}: {str(e)[:80]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== Thumbnails: {ok} gesetzt, {err} Fehler{" (LIMIT/QUOTA)" if stop else ""} | gesamt mit CRT: {len(done)} ===')
