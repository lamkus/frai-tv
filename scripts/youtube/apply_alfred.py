# -*- coding: utf-8 -*-
"""Idempotenter Applier fuer Alfred J. Kwak. Matcht Live-Videos per E##.
DRY default; --apply schreibt. Nur EIN Live-Match pro Folge (Dubletten geflaggt). Quota-/resume-sicher.
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
CANON = json.load(open('config/alfred_canonical.json', encoding='utf-8'))

def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token(); print('[AUTH] OK')

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
        f'https://www.googleapis.com/youtube/v3/videos?part=snippet,status,recordingDetails&id={",".join(ids[i:i+50])}',
        headers={'Authorization':f'Bearer {tok}'})).read())['items']
pub=[v for v in V if v['status']['privacyStatus']=='public' and 'Kwak' in v['snippet']['title']]
print(f'[FETCH] {len(pub)} oeffentliche Alfred-Videos')

# INHALTSBASIERTES Matching: ueber den Folgentitel (Nummern des Kanals sind nachweislich falsch).
EPS = json.load(open('config/alfred_episodes.json', encoding='utf-8'))
def norm(s):
    s = (s or '').lower().replace('ß','ss').replace('ä','a').replace('ö','o').replace('ü','u')
    return re.sub(r'[^a-z0-9]', '', s)
def content_part(vt):
    s = re.sub(r'^.*?(?:\(E?\d{1,2}\)|E\d{1,2}:|Folge\s*\d+:?)\s*', '', vt, flags=re.I)  # bis zur Nummer weg
    s = re.sub(r'\s*[\|\[].*$', '', s)  # ab | oder [ weg
    return s.strip()
PUBN = [(v, norm(v['snippet']['title']), norm(content_part(v['snippet']['title']))) for v in pub]
byep = {}
used = {}  # video_id -> ep (Kollisionen verhindern)
for e in EPS:
    ep = e['ep']; tn = norm(e['title_de'])
    if len(tn) < 4: continue
    cands = [v for v, full, cp in PUBN if tn in full]  # strikt: exakter Folgentitel im Video-Titel
    if cands: byep[ep] = cands
# Kollisionen (ein Video matcht mehrere Folgen) flaggen statt falsch zuordnen
vid2eps = {}
for ep, vs in byep.items():
    for v in vs: vid2eps.setdefault(v['id'], []).append(ep)
collide = {vid: eps for vid, eps in vid2eps.items() if len(eps) > 1}
if collide:
    print('  [KOLLISION] Video -> mehrere Folgen:', {k: v for k, v in list(collide.items())[:5]})

PROG='config/alfred_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()

def needs(cur, c):
    s=cur['snippet']; diffs=[]
    if s.get('title','')!=c['title']: diffs.append('title')
    if s.get('description','')!=c['description']: diffs.append('desc')
    if sorted(s.get('tags',[]))!=sorted(c['tags']): diffs.append('tags')
    if s.get('defaultLanguage','')!=c['defaultLanguage']: diffs.append('lang')
    return diffs

ok=skip=miss=dup=err=0; quota=False
for c in CANON:
    ep=c['ep']
    if str(ep) in done: skip+=1; continue
    ms=byep.get(ep, [])
    if not ms: miss+=1; continue
    if len(ms)>1: dup+=1; print(f'  [DUP]  E{ep:02d} {len(ms)} Treffer -> manuell: '+' | '.join(v["id"] for v in ms)); continue
    v=ms[0]; vid=v['id']; diffs=needs(v, c)
    if not diffs: done.add(str(ep)); skip+=1; continue
    if not APPLY:
        print(f'  [DRY]  E{ep:02d} {vid}: {",".join(diffs)}  ->  {c["title"]}'); ok+=1; continue
    body={'id':vid,'snippet':{'title':c['title'],'description':c['description'],'tags':c['tags'],
        'categoryId':c['categoryId'],'defaultLanguage':c['defaultLanguage'],'defaultAudioLanguage':c['defaultAudioLanguage']}}
    try:
        urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        done.add(str(ep)); ok+=1; print(f'  [OK]   E{ep:02d} {vid}: {",".join(diffs)}')
        if ok%10==0: json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.4)
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] erreicht nach {ok} - morgen resume.'); quota=True; break
        err+=1; print(f'  [ERR]  E{ep:02d} {vid}: {b[:90]}')
    except Exception as e:
        err+=1; print(f'  [ERR]  E{ep:02d}: {str(e)[:80]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} {"geschrieben" if APPLY else "wuerden geaendert"}, {skip} ok/skip, {miss} ohne Match, {dup} Dubletten, {err} Fehler{" (QUOTA)" if quota else ""} ===')
