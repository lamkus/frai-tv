# -*- coding: utf-8 -*-
"""Reichert alle public Videos an: Description (echte Historie+Ort aus Recherche) + recherchierte Tags + recordingDate
in EINEM Update (50 Units/Video). Dry-Run default; --apply schreibt. Resume- + quota-sicher."""
import io, sys, json, re, os, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY='--apply' in sys.argv
o=json.load(open('config/youtube_oauth.json',encoding='utf-8'))
EV=json.load(open('config/wochenschau_complete_locations.json',encoding='utf-8'))
SER=json.load(open('config/series_enrichment.json',encoding='utf-8'))
def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok=token(); print('[AUTH] OK')

# Serie nach Titel zuordnen -> Index in SER
def series_for(t):
    tl=t.lower()
    if 'wochenschau' in tl or 'tonwoche' in tl: return 0
    if 'betty boop' in tl: return 1
    if 'superman' in tl: return 2
    if 'felix' in tl: return 3
    if 'popeye' in tl: return 4
    if 'casper' in tl: return 5
    if 'soundie' in tl: return 6
    if 'alfred' in tl: return 7
    if 'maulwurf' in tl or 'krtek' in tl: return 9
    return 8  # Classic Films / sonstiges

def year_of(t):
    m=re.search(r'\((\d{4})',t) or re.search(r'\b(19\d{2}|20\d{2})\b',t)
    return m.group(1) if m else ''

def rec_date(t):
    m=re.search(r'Nr\.?\s*(\d+)',t)
    if ('Wochenschau' in t or 'Tonwoche' in t) and m and m.group(1) in EV:
        return EV[m.group(1)]['date']+'T00:00:00Z'
    m2=re.search(r'\((\d{2})\.(\d{2})\.(\d{4})',t)
    if m2: return f'{m2.group(3)}-{m2.group(2)}-{m2.group(1)}T00:00:00Z'
    y=year_of(t)
    return f'{y}-01-01T00:00:00Z' if y else None

def build_tags(s):
    out=[]
    for k in (s.get('keywords_en',[])[:8]+s.get('keywords_de',[])[:3]+s.get('keywords_es',[])[:1]+s.get('keywords_ja',[])[:1]+s.get('keywords_pt',[])[:1]):
        if k and k not in out: out.append(k)
    for must in ['8K','4K UHD','Remastered','Public Domain','AI Restoration']:
        if len(out)<15 and must not in out: out.append(must)
    return out[:15]

def build_desc(s, title, year):
    hist=s.get('history','').strip()
    loc=s.get('production_location','').strip()
    clean=re.sub(r'\s*\|\s*8K HQ \(4K UHD\).*$','',title).strip()
    parts=[f'{clean}' + (f' ({year})' if year and year not in clean else '')]
    mnr=re.search(r'Nr\.?\s*(\d+)',title)
    if ('Wochenschau' in title or 'Tonwoche' in title) and mnr and mnr.group(1) in EV:
        e=EV[mnr.group(1)]
        parts.append(f"📍 Ereignis / Event: {e['event_en']} ({e['event_de']}) — Ort / Location: {e['location']['desc']} · {e['date']}." + (f" {e.get('historical_note','')}" if e.get('historical_note') else ''))
    if hist: parts.append(hist)
    if loc: parts.append(f'Produktion / Production: {loc}')
    parts.append('KI-restauriert in 8K (4K UHD) von remAIke.IT. AI-restored in 8K.')
    parts.append('🔔 https://www.youtube.com/@remAIke_IT?sub_confirmation=1\n🌐 https://frai.tv')
    tags=build_tags(s)
    parts.append(' '.join('#'+re.sub(r'[^A-Za-z0-9]','',k) for k in tags[:5] if re.sub(r'[^A-Za-z0-9]','',k)))
    d='\n\n'.join(parts)
    return d[:4900]

# fetch
up=json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true',headers={'Authorization':f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];nx=None
while True:
    u=f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50'+(f'&pageToken={nx}' if nx else '')
    d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {tok}'})).read())
    ids+=[i['contentDetails']['videoId'] for i in d['items']];nx=d.get('nextPageToken')
    if not nx:break
ids=list(dict.fromkeys(ids))
V=[]
for i in range(0,len(ids),50):
    V+=json.loads(urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id={",".join(ids[i:i+50])}',headers={'Authorization':f'Bearer {tok}'})).read())['items']
pub=[v for v in V if v['status']['privacyStatus']=='public']

PROG='config/enrich_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()
todo=[v for v in pub if v['id'] not in done]
print(f'[PLAN] {len(pub)} public, {len(done)} fertig, {len(todo)} offen ({"APPLY" if APPLY else "DRY-RUN"})')

if not APPLY:
    from collections import Counter
    c=Counter(SER[series_for(v['snippet']['title'])]['series'][:22] for v in pub)
    print('\nSerien-Verteilung:')
    for k,n in c.most_common(): print(f'  {n:>3}  {k}')
    print('\n=== 3 Beispiel-Descriptions ===')
    for v in pub[:3]:
        s=SER[series_for(v['snippet']['title'])]; y=year_of(v['snippet']['title'])
        print(f"\n--- {v['snippet']['title'][:50]} ---")
        print(build_desc(s,v['snippet']['title'],y)[:500])
        print('TAGS:',build_tags(s))
        print('recDate:',rec_date(v['snippet']['title']))
    sys.exit()

ok=err=0; quota=False
for v in todo:
    s=SER[series_for(v['snippet']['title'])]; snip=v['snippet']; t=snip['title']; y=year_of(t)
    body={'id':v['id'],'snippet':{'title':t,'description':build_desc(s,t,y),'tags':build_tags(s),
        'categoryId':snip.get('categoryId','1'),'defaultLanguage':snip.get('defaultLanguage','de'),'defaultAudioLanguage':snip.get('defaultAudioLanguage','de')}}
    rd=rec_date(t)
    part='snippet,recordingDetails' if rd else 'snippet'
    if rd: body['recordingDetails']={'recordingDate':rd}
    try:
        urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part={part}',data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        done.add(v['id']); ok+=1
        if ok%20==0: print(f'  [{ok}/{len(todo)}] angereichert'); json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.4)
        if ok%100==0: tok=token()
    except urllib.error.HTTPError as e:
        b=e.read().decode()[:150]
        if 'quotaExceeded' in b: print(f'[QUOTA] erreicht nach {ok} - morgen resume.'); quota=True; break
        err+=1; print(f'  ERR {v["id"]}: {b[:80]}')
    except Exception as e:
        err+=1; print(f'  ERR {v["id"]}: {str(e)[:70]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== {ok} angereichert, {err} Fehler, {len(todo)-ok} offen{" (QUOTA)" if quota else ""} ===')
