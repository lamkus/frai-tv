# -*- coding: utf-8 -*-
"""Generalisierter Cartoon-Pass (Betty Boop, Felix, Popeye, Casper, Soundies, Maulwurf).
Titel sind bereits korrekt -> behalten. Setzt defaultLanguage (Auto-Dub-Hebel!), SOTA-Beschreibung,
recordingDate (Jahr aus Titel), categoryId. Dedup per normalisiertem Titel (Keeper = erster).
DRY default; --apply schreibt. Resume-/quota-sicher (config/cartoon_progress.json).
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
ROWS = json.load(open('config/other_videos.json', encoding='utf-8'))
SUB = 'https://www.youtube.com/@remAIke_IT?sub_confirmation=1'

# keyword -> (lang, series_label, public_domain, studio/blurb)
CFG = [
    ('betty boop', ('en', 'Betty Boop', True,  'Fleischer Studios')),
    ('felix',      ('en', 'Felix the Cat', True, 'Pat Sullivan / Otto Messmer')),
    ('popeye',     ('en', 'Popeye', True,  'Fleischer / Famous Studios')),
    ('casper',     ('en', 'Casper the Friendly Ghost', True, 'Famous Studios')),
    ('soundie',    ('en', 'Soundies', True, 'Soundies Distributing Corp. (1940s musical jukebox films)')),
    ('krtek',      ('de', 'Der kleine Maulwurf (Krtek)', False, 'Zdeněk Miler')),
    ('maulwurf',   ('de', 'Der kleine Maulwurf (Krtek)', False, 'Zdeněk Miler')),
]
def series_of(t):
    tl = t.lower()
    for kw, cfg in CFG:
        if kw in tl: return cfg
    return None

def year_of(t):
    m = re.search(r'\((\d{4})\)', t)
    if m: return int(m.group(1))
    m = re.search(r'\((\d{4})s\)', t)
    if m: return int(m.group(1)) + 5  # "1940s" -> 1945
    m = re.search(r'\b(19\d{2}|20\d{2})\b', t)
    return int(m.group(1)) if m else None

def clean_name(t):  # Inhaltsteil vor " | " / " (Jahr)" / " [8K]"
    s = re.sub(r'\s*[\|\[].*$', '', t)
    s = re.sub(r'\s*\((?:19|20)\d{2}s?\).*$', '', s)
    return s.strip()

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def desc(title, lang, label, pd, blurb):
    name = clean_name(title); yr = year_of(title)
    head = f'{name}' + (f' ({yr})' if yr else '') + f' – {label}-Klassiker, in 8K (4K UHD) KI-restauriert von remAIke.TV.'
    pdl = 'Originalmaterial: Public Domain.' if pd else 'Klassiker-Restauration.'
    blocks = [head[:125] if len(head) > 125 else head,
              f'Aus der Reihe {label} ({blurb}). {pdl}',
              f'Alle Klassiker kostenlos auf frai.TV:\nhttps://frai.tv\n\nAbonnieren:\n{SUB}']
    if lang == 'en':
        blocks.append(f'[EN] {name} – classic {label} cartoon, 8K AI-restored.')
    tagw = label.split(' ')[0]
    blocks.append(f'#{re.sub(r"[^A-Za-z]","",label)} #Zeichentrick #Cartoon #8K #remAIke')
    return '\n\n'.join(blocks)[:4900]

def tags(title, label):
    name = clean_name(title)
    out = [label, name, 'Zeichentrick', 'Cartoon', 'Klassiker', 'remAIke.TV', '8K']
    seen=[]; [seen.append(x) for x in out if x and x not in seen]
    return seen[:8]

# Kandidaten + Dedup
cands = []
for r in ROWS:
    cfg = series_of(r['title'])
    if cfg: cands.append((r, cfg))
seen_title = {}
keepers = []; dupes = []
for r, cfg in cands:
    k = (cfg[1], norm(clean_name(r['title'])))
    if k in seen_title: dupes.append(r['id'])
    else: seen_title[k] = r['id']; keepers.append((r, cfg))
print(f'[PLAN] {len(cands)} Cartoon-Videos, {len(keepers)} Keeper, {len(dupes)} Dubletten')

def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token() if APPLY else None
PROG='config/cartoon_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()

ok=skip=err=0; quota=False
for r, cfg in keepers:
    vid=r['id']; lang,label,pd,blurb = cfg
    if vid in done: skip+=1; continue
    title=r['title']; yr=year_of(title)
    body={'id':vid,'snippet':{'title':title,'description':desc(title,lang,label,pd,blurb),'tags':tags(title,label),
        'categoryId':'1','defaultLanguage':lang,'defaultAudioLanguage':lang}}
    if yr: body['recordingDetails']={'recordingDate':f'{yr}-01-01T00:00:00Z'}
    if not APPLY:
        if ok<6: print(f'  [DRY] {label[:14]:14} {vid} lang={lang} {yr} | {clean_name(title)[:40]}')
        ok+=1; continue
    part='snippet,recordingDetails' if yr else 'snippet'
    try:
        urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part={part}',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        done.add(vid); ok+=1
        if ok%10==0: print(f'  [{ok}] geschrieben'); json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.35)
        if ok%100==0: tok=token()
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] nach {ok} - resume morgen'); quota=True; break
        err+=1; print(f'  [ERR] {vid}: {b[:80]}')
json.dump(sorted(done),open(PROG,'w'))
json.dump(dupes, open('config/cartoon_remove_list.json','w'), ensure_ascii=False, indent=1)
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} {"geschrieben" if APPLY else "(dry)"}, {skip} skip, {err} Fehler{" (QUOTA)" if quota else ""} | {len(dupes)} Dubletten -> cartoon_remove_list.json ===')
