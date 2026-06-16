# -*- coding: utf-8 -*-
"""Idempotenter Applier: schreibt kanonische Metadaten (config/wochenschau_canonical.json) auf die Live-Videos.
- matcht Folgen-Nr -> Live-Video-ID anhand des aktuellen Titels
- schreibt NUR Abweichungen (idempotent), ueberspringt bereits korrekte
- quota-sicher (Stop bei quotaExceeded), resume-sicher (config/apply_progress.json)
- DRY-RUN default; --apply schreibt. Nur EIN Live-Match pro Nr (Duplikate werden geflaggt, nicht angefasst).
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
CANON = json.load(open('config/wochenschau_canonical.json', encoding='utf-8'))

def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token(); print('[AUTH] OK')

# --- alle Uploads holen ---
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
pub=[v for v in V if v['status']['privacyStatus']=='public']
print(f'[FETCH] {len(pub)} oeffentliche Videos')

def num_of(title):
    m=re.search(r'Nr\.?\s*(\d+)', title) or re.search(r'(?:Wochenschau|Tonwoche)\s+(\d+)', title)
    return m.group(1) if m else None

# Nr -> [Videos]
bynum={}
for v in pub:
    if 'Wochenschau' in v['snippet']['title'] or 'Tonwoche' in v['snippet']['title']:
        n=num_of(v['snippet']['title'])
        if n: bynum.setdefault(n, []).append(v)

PROG='config/apply_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()

def needs_update(cur, c):
    s=cur['snippet']; rd=cur.get('recordingDetails',{})
    diffs=[]
    if s.get('title','')!=c['title']: diffs.append('title')
    if s.get('description','')!=c['description']: diffs.append('desc')
    if sorted(s.get('tags',[]))!=sorted(c['tags']): diffs.append('tags')
    if (rd.get('recordingDate') or '')[:10]!=(c['recordingDate'] or '')[:10]: diffs.append('recDate')
    if s.get('defaultLanguage','')!=c['defaultLanguage']: diffs.append('lang')
    return diffs

ok=skip=miss=dup=err=0; quota=False
for c in CANON:
    n=c['nr']
    if n in done: skip+=1; continue
    matches=bynum.get(n, [])
    if not matches: miss+=1; print(f'  [MISS] Nr.{n} kein Live-Video'); continue
    if len(matches)>1: dup+=1; print(f'  [DUP]  Nr.{n} {len(matches)} Treffer -> manuell, uebersprungen'); continue
    v=matches[0]; vid=v['id']; diffs=needs_update(v, c)
    if not diffs:
        done.add(n); skip+=1; continue
    if not APPLY:
        print(f'  [DRY]  Nr.{n} {vid} -> aendert: {",".join(diffs)}')
        ok+=1; continue
    body={'id':vid,'snippet':{'title':c['title'],'description':c['description'],'tags':c['tags'],
        'categoryId':c['categoryId'],'defaultLanguage':c['defaultLanguage'],'defaultAudioLanguage':c['defaultAudioLanguage']},
        'recordingDetails':{'recordingDate':c['recordingDate']}}
    try:
        urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet,recordingDetails',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        done.add(n); ok+=1; print(f'  [OK]   Nr.{n} {vid}: {",".join(diffs)}')
        if ok%10==0: json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.4)
        if ok%100==0: tok=token()
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] erreicht nach {ok} - morgen resume.'); quota=True; break
        err+=1; print(f'  [ERR]  Nr.{n} {vid}: {b[:90]}')
    except Exception as e:
        err+=1; print(f'  [ERR]  Nr.{n}: {str(e)[:80]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} {"geschrieben" if APPLY else "wuerden geaendert"}, {skip} ok/skip, {miss} ohne Match, {dup} Duplikate, {err} Fehler{" (QUOTA)" if quota else ""} ===')
