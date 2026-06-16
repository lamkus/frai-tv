# -*- coding: utf-8 -*-
"""Setzt recordingDate fuer alle public Videos: Wochenschau = exaktes Sendedatum (Event-Daten), sonst = Produktionsjahr aus Titel. Resume- + quota-sicher."""
import io, sys, json, re, os, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
EV = json.load(open('config/wochenschau_complete_locations.json', encoding='utf-8'))
def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token(); print('[AUTH] OK')

up = json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true', headers={'Authorization':f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];nx=None
while True:
    u=f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50'+(f'&pageToken={nx}' if nx else '')
    d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {tok}'})).read())
    ids+=[i['contentDetails']['videoId'] for i in d['items']];nx=d.get('nextPageToken')
    if not nx:break
ids=list(dict.fromkeys(ids))
V=[]
for i in range(0,len(ids),50):
    V+=json.loads(urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=snippet,recordingDetails,status&id={",".join(ids[i:i+50])}',headers={'Authorization':f'Bearer {tok}'})).read())['items']
pub=[v for v in V if v['status']['privacyStatus']=='public']

def derive_date(v):
    t=v['snippet']['title']
    # Wochenschau/Tonwoche: exaktes Datum aus Event-Daten
    m=re.search(r'Nr\.?\s*(\d+)',t)
    if ('Wochenschau' in t or 'Tonwoche' in t) and m and m.group(1) in EV:
        return EV[m.group(1)]['date']+'T00:00:00Z'
    # Datum direkt im Titel (DD.MM.YYYY)
    m2=re.search(r'\((\d{2})\.(\d{2})\.(\d{4})',t)
    if m2: return f'{m2.group(3)}-{m2.group(2)}-{m2.group(1)}T00:00:00Z'
    # sonst Jahr aus Titel -> 1. Januar
    m3=re.search(r'\((\d{4})\)',t) or re.search(r'\b(19\d{2}|20\d{2})\b',t)
    if m3: return f'{m3.group(1)}-01-01T00:00:00Z'
    return None

PROG='config/recdate_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
todo=[v for v in pub if v['id'] not in done and not v.get('recordingDetails',{}).get('recordingDate')]
print(f'[PLAN] {len(pub)} public, {len(todo)} ohne recordingDate offen')

ok=skip=err=0; quota=False
for v in todo:
    dt=derive_date(v)
    if not dt: skip+=1; continue
    body=json.dumps({'id':v['id'],'recordingDetails':{'recordingDate':dt}}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=recordingDetails',
            data=body, headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'}, method='PUT'))
        done.add(v['id']); ok+=1
        if ok%25==0: print(f'  [{ok}] gesetzt (zuletzt {dt[:10]})'); json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.35)
        if ok%100==0: tok=token()
    except urllib.error.HTTPError as e:
        b=e.read().decode()[:140]
        if 'quotaExceeded' in b: print(f'[QUOTA] erreicht nach {ok} - morgen resume.'); quota=True; break
        err+=1; print(f'  ERR {v["id"]}: {b[:80]}')
    except Exception as e:
        err+=1; print(f'  ERR {v["id"]}: {str(e)[:70]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== recordingDate: {ok} gesetzt, {skip} kein Datum ableitbar, {err} Fehler{" (QUOTA)" if quota else ""} ===')
