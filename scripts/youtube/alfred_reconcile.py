# -*- coding: utf-8 -*-
"""Alfred J. Kwak: konsolidierte Zuordnung + Dedup.
- Ordnet jedes Live-Video per FOLGENTITEL einer Episode zu (Kanal-Nummern sind unzuverlaessig).
- Dubletten: Keeper = meiste Views -> bekommt kanonischen Titel; ueberzaehlige -> Loesch-Liste (config/alfred_remove_list.json).
- 2-Stufen-Match (strikt + gekuerzte Titel). DRY default; --apply schreibt. Quota-/resume-sicher.
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
EPS = json.load(open('config/alfred_episodes.json', encoding='utf-8'))
CANON = {c['ep']: c for c in json.load(open('config/alfred_canonical.json', encoding='utf-8'))}

def norm(s):
    s = (s or '').lower().replace('ß','ss').replace('ä','a').replace('ö','o').replace('ü','u')
    return re.sub(r'[^a-z0-9]', '', s)
def content_part(vt):
    s = re.sub(r'^.*?(?:\(E?\d{1,2}\)|E\d{1,2}:|Folge\s*\d+:?)\s*', '', vt, flags=re.I)
    return re.sub(r'\s*[\|\[].*$', '', s).strip()

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
        f'https://www.googleapis.com/youtube/v3/videos?part=snippet,status,statistics&id={",".join(ids[i:i+50])}',
        headers={'Authorization':f'Bearer {tok}'})).read())['items']
vids=[v for v in V if v['status']['privacyStatus']=='public' and 'Kwak' in v['snippet']['title']]
print(f'[FETCH] {len(vids)} oeffentliche Alfred-Videos')

# Stufe 1: jedes Video -> Folge mit laengstem passenden Titel (strikt: title_de in Video-Titel)
for v in vids:
    full = norm(v['snippet']['title']); best=None; bl=0
    for e in EPS:
        tn = norm(e['title_de'])
        if len(tn) >= 4 and tn in full and len(tn) > bl: best=e['ep']; bl=len(tn)
    v['_ep'] = best
# Stufe 2: Videos ohne Zuordnung -> gekuerzte Titel gegen noch freie Folgen
assigned = set(v['_ep'] for v in vids if v['_ep'])
for v in vids:
    if v['_ep']: continue
    cp = norm(content_part(v['snippet']['title']))
    if len(cp) < 6: continue
    cands=[e for e in EPS if e['ep'] not in assigned and (cp in norm(e['title_de']) or norm(e['title_de']) in cp)]
    if len(cands)==1: v['_ep']=cands[0]['ep']; assigned.add(cands[0]['ep']); print(f'  [match2] E{cands[0]["ep"]:02d} <- {v["id"]} ({content_part(v["snippet"]["title"])[:30]})')

byep={}
for v in vids:
    if v['_ep']: byep.setdefault(v['_ep'], []).append(v)

PROG='config/alfred_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
def views(v): return int(v['statistics'].get('viewCount',0))
def needs(cur, c):
    s=cur['snippet']; d=[]
    if s.get('title','')!=c['title']: d.append('title')
    if s.get('description','')!=c['description']: d.append('desc')
    if sorted(s.get('tags',[]))!=sorted(c['tags']): d.append('tags')
    if s.get('defaultLanguage','')!=c['defaultLanguage']: d.append('lang')
    return d

remove_list=[]; ok=skip=err=0; quota=False
matched_eps=sorted(byep.keys())
missing=[e['ep'] for e in EPS if e['ep'] not in byep]
for ep in matched_eps:
    vs=sorted(byep[ep], key=views, reverse=True)
    keeper=vs[0]; extras=vs[1:]; c=CANON[ep]
    for x in extras:
        remove_list.append({'ep':ep,'id':x['id'],'views':views(x),'title':x['snippet']['title']})
    diffs=needs(keeper, c)
    tag=' (KEEPER von %d)'%len(vs) if len(vs)>1 else ''
    if not diffs:
        skip+=1; print(f'  [SKIP] E{ep:02d} {keeper["id"]} schon korrekt{tag}'); continue
    if not APPLY:
        print(f'  [DRY]  E{ep:02d} {keeper["id"]} ({views(keeper)} views){tag}: {",".join(diffs)} -> {c["title"]}'); ok+=1; continue
    body={'id':keeper['id'],'snippet':{'title':c['title'],'description':c['description'],'tags':c['tags'],
        'categoryId':c['categoryId'],'defaultLanguage':c['defaultLanguage'],'defaultAudioLanguage':c['defaultAudioLanguage']}}
    try:
        urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        ok+=1; print(f'  [OK]   E{ep:02d} {keeper["id"]}{tag}: {",".join(diffs)}'); time.sleep(0.4)
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] nach {ok}'); quota=True; break
        err+=1; print(f'  [ERR]  E{ep:02d}: {b[:80]}')

json.dump(remove_list, open('config/alfred_remove_list.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} Keeper {"geschrieben" if APPLY else "wuerden"}, {skip} schon ok, {len(remove_list)} Dubletten zum Entfernen, {err} Fehler{" (QUOTA)" if quota else ""} ===')
print(f'Folgen zugeordnet: {len(matched_eps)}/52 | noch fehlend: {missing}')
print('Loesch-Liste -> config/alfred_remove_list.json')
