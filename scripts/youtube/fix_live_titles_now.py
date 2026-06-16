# -*- coding: utf-8 -*-
"""Repariert verstuemmelte Live-Titel + Tonwoche-Wochenschau-Keyword. Dry-Run default; --apply schreibt."""
import io, sys, json, re, time, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout.reconfigure(line_buffering=True)

APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))

def token():
    data = urllib.parse.urlencode({'client_id': o['client_id'], 'client_secret': o['client_secret'],
        'refresh_token': o['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())['access_token']

tok = token()
print('[AUTH] Token OK')

r = urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true', headers={'Authorization': f'Bearer {tok}'})
uploads = json.loads(urllib.request.urlopen(r).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids = []; nxt = None
while True:
    u = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads}&maxResults=50'
    if nxt: u += f'&pageToken={nxt}'
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': f'Bearer {tok}'})).read())
    ids += [i['contentDetails']['videoId'] for i in d['items']]
    nxt = d.get('nextPageToken')
    if not nxt: break
vids = []
for i in range(0, len(ids), 50):
    rr = urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id={",".join(ids[i:i+50])}', headers={'Authorization': f'Bearer {tok}'})
    vids += json.loads(urllib.request.urlopen(rr).read())['items']
pub = [v for v in vids if v['status']['privacyStatus'] == 'public']
print(f'[FETCH] {len(pub)} public videos')

QUAL = '| 8K HQ (4K UHD)'

def clean_title(t):
    # Segment-based: drop empty / handle-fragment / truncated-'...' segments
    kept = []
    for s in [x.strip() for x in t.split('|')]:
        if not s: continue
        if '@' in s: continue
        if s.endswith('...') or s in ('...', '..'): continue
        kept.append(s)
    t2 = re.sub(r'\s{2,}', ' ', ' | '.join(kept)).strip()
    # strip canonical suffix to a clean core, then re-normalize quality
    core = re.sub(r'\s*\|\s*8K HQ \(4K UHD\)\s*$', '', t2).strip()
    has8 = bool(re.search(r'\b8K\b', core))
    has4 = bool(re.search(r'\b4K\b', core))
    if has8 and has4:
        t2 = core                       # both already inline, no suffix needed
    elif has8:
        t2 = core + ' (4K UHD)'         # keep 8K hook, ensure 4K present
    elif has4:
        t2 = core + ' (8K)'
    else:
        t2 = core + ' | 8K HQ (4K UHD)' # standard canonical suffix
    return re.sub(r'\s{2,}', ' ', t2).strip()

def is_malformed(t):
    return ('@' in t) or bool(re.search(r'\|\s*\|', t)) or ('  ' in t) or (len(re.findall(r'8K', t)) >= 2) or ('...' in t)

title_fixes = []
tonwoche_fixes = []
for v in pub:
    s = v['snippet']; t = s['title']; tags = s.get('tags', [])
    if is_malformed(t):
        nt = clean_title(t)
        if nt and nt != t:
            title_fixes.append((v['id'], t, nt, s))
    elif '8K' in t and '4K' not in t and t.strip() != '#1':
        # has 8K but missing 4K -> normalize quality suffix
        if t.rstrip().endswith('8K HQ'):
            nt = t.rstrip() + ' (4K UHD)'
        else:
            nt = t.rstrip() + ' (4K UHD)'
        title_fixes.append((v['id'], t, nt, s))
    if 'Tonwoche' in t and 'Wochenschau' not in t:
        m = re.match(r'(UFA-Tonwoche Nr\.\s*\d+)\s*\(\d{2}\.\d{2}\.(\d{4})', t)
        if m:
            nt = f'{m.group(1)} ({m.group(2)}) | Deutsche Wochenschau {QUAL}'
        else:
            nt = re.sub(r'\s*\| 8K HQ \(4K UHD\)\s*$', '', t).strip() + f' | Deutsche Wochenschau {QUAL}'
        new_tags = list(tags)
        for kw in ['Wochenschau', 'Deutsche Wochenschau', 'UFA-Tonwoche', 'Newsreel', 'WWII']:
            if kw not in new_tags and len(new_tags) < 15: new_tags.append(kw)
        tonwoche_fixes.append((v['id'], t, nt, new_tags, s))

print(f'\n=== FIX-PLAN ({"APPLY" if APPLY else "DRY-RUN"}) ===')
print(f'\n1) VERSTUEMMELTE TITEL: {len(title_fixes)}')
for vid, old, new, _ in title_fixes[:50]:
    print(f'  ALT: {old}\n  NEU: {new}')
print(f'\n2) TONWOCHE +Wochenschau: {len(tonwoche_fixes)}')
for vid, old, new, _, _ in tonwoche_fixes[:12]:
    print(f'  ALT: {old}\n  NEU: {new}')
no4k = [v['snippet']['title'] for v in pub if '4K' not in v['snippet']['title']]
print(f'\n3) OHNE 4K: {len(no4k)}')
for t in no4k[:12]: print(f'  - {t}')

if not APPLY:
    print(f'\n[DRY-RUN] Geplant: {len(title_fixes)} Titel-Fixes + {len(tonwoche_fixes)} Tonwoche. Nichts geschrieben.')
    sys.exit(0)

def put(vid, snip_updates, base):
    body = {'id': vid, 'snippet': {
        'title': snip_updates.get('title', base['title']),
        'description': base.get('description', ''),
        'tags': snip_updates.get('tags', base.get('tags', []))[:15],
        'categoryId': base.get('categoryId', '1'),
        'defaultLanguage': base.get('defaultLanguage', 'de'),
        'defaultAudioLanguage': base.get('defaultAudioLanguage', 'de')}}
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet',
        data=json.dumps(body).encode('utf-8'),
        headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

ok = err = 0
for vid, old, new, snip in title_fixes:
    try: put(vid, {'title': new}, snip); ok += 1; time.sleep(0.4)
    except Exception as e: err += 1; print(f'  ERR {vid}: {str(e)[:80]}')
for vid, old, new, new_tags, snip in tonwoche_fixes:
    try: put(vid, {'title': new, 'tags': new_tags}, snip); ok += 1; time.sleep(0.4)
    except Exception as e: err += 1; print(f'  ERR {vid}: {str(e)[:80]}')
print(f'\n=== ANGEWENDET: {ok} ok, {err} Fehler ===')
json.dump({'title_fixes': len(title_fixes), 'tonwoche': len(tonwoche_fixes), 'ok': ok, 'err': err}, open('config/live_title_fix_report.json', 'w'), indent=2)
