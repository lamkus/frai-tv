# -*- coding: utf-8 -*-
"""Pilot: lokalisiert N Wochenschau-Videos in 9 Sprachen (Titel+Beschreibung). Dry-Run default; --apply schreibt. --n=3 Anzahl."""
import io, sys, json, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout.reconfigure(line_buffering=True)

APPLY = '--apply' in sys.argv
N = next((int(a.split('=')[1]) for a in sys.argv if a.startswith('--n=')), 3)
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
EV = json.load(open('config/wochenschau_complete_locations.json', encoding='utf-8'))

def token():
    data = urllib.parse.urlencode({'client_id': o['client_id'], 'client_secret': o['client_secret'],
        'refresh_token': o['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())['access_token']
tok = token(); print('[AUTH] OK')

up = json.loads(urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true', headers={'Authorization': f'Bearer {tok}'})).read())['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids = []; nx = None
while True:
    u = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={up}&maxResults=50' + (f'&pageToken={nx}' if nx else '')
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': f'Bearer {tok}'})).read())
    ids += [i['contentDetails']['videoId'] for i in d['items']]; nx = d.get('nextPageToken')
    if not nx: break
ids = list(dict.fromkeys(ids))
V = []
for i in range(0, len(ids), 50):
    V += json.loads(urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part=snippet,localizations,status&id={",".join(ids[i:i+50])}', headers={'Authorization': f'Bearer {tok}'})).read())['items']
woch = [v for v in V if v['status']['privacyStatus'] == 'public' and 'Wochenschau' in v['snippet']['title']]

QUAL = '8K HQ (4K UHD)'
# Newsreel-Begriff je Sprache
NR = {'de':'Deutsche Wochenschau Nr.','en':'German Newsreel No.','es':'Noticiero Alemán Nº','es-419':'Noticiero Alemán Nº',
      'pt-BR':'Cinejornal Alemão Nº','fr':'Actualités Allemandes Nº','ja':'ドイツ週間ニュース 第','ko':'독일 주간뉴스 제','hi':'जर्मन न्यूज़रील नं.'}
SUF = {'ja':'号','ko':'호'}  # Zähl-Suffix
# Kurzbeschreibung je Sprache (neutral-dokumentarisch)
def desc(lang, nr, ev, year):
    e = ev['event_en']; loc = ev['location']['desc']
    L = {
      'de': f"Deutsche Wochenschau Nr. {nr} ({ev['date']}) — {e}, {loc}. Historisches WWII-Newsreel, KI-restauriert in 8K (4K UHD). Historisches Dokument zur wissenschaftlich-historischen Aufklärung.",
      'en': f"German WWII newsreel No. {nr} ({ev['date']}) — {e}, {loc}. AI-restored in 8K (4K UHD). Historical document for educational purposes only.",
      'es': f"Noticiero alemán de la 2ª Guerra Mundial Nº {nr} ({ev['date']}) — {e}, {loc}. Restaurado con IA en 8K (4K UHD). Documento histórico con fines educativos.",
      'es-419': f"Noticiero alemán de la Segunda Guerra Mundial Nº {nr} ({ev['date']}) — {e}, {loc}. Restaurado con IA en 8K (4K UHD). Documento histórico con fines educativos.",
      'pt-BR': f"Cinejornal alemão da 2ª Guerra Mundial Nº {nr} ({ev['date']}) — {e}, {loc}. Restaurado com IA em 8K (4K UHD). Documento histórico para fins educativos.",
      'fr': f"Actualités allemandes de la 2e Guerre mondiale Nº {nr} ({ev['date']}) — {e}, {loc}. Restauré par IA en 8K (4K UHD). Document historique à but éducatif.",
      'ja': f"第二次世界大戦のドイツ週間ニュース 第{nr}号（{ev['date']}）— {e}、{loc}。AIにより8K（4K UHD）で復元。教育目的の歴史的資料。",
      'ko': f"제2차 세계대전 독일 주간뉴스 제{nr}호 ({ev['date']}) — {e}, {loc}. AI로 8K(4K UHD) 복원. 교육 목적의 역사적 자료.",
      'hi': f"द्वितीय विश्व युद्ध का जर्मन न्यूज़रील नं. {nr} ({ev['date']}) — {e}, {loc}। AI द्वारा 8K (4K UHD) में पुनर्स्थापित। केवल शैक्षिक उद्देश्य हेतु ऐतिहासिक दस्तावेज़।",
    }
    return L.get(lang, L['en']) + "\n\n🌐 frai.tv · ▶ youtube.com/@remAIke_IT"

def title(lang, nr, ev, year):
    e = ev['event_en']; ede = ev['event_de']
    if lang == 'de':
        return f"Deutsche Wochenschau Nr. {nr} ({year}) | {ede} | {QUAL}"
    if lang in ('ja','ko'):
        return f"{NR[lang]}{nr}{SUF[lang]} ({year}) | {e} | {QUAL}"
    return f"{NR[lang]} {nr} ({year}) | {e} | {QUAL}"

LANGS = ['de','en','es','es-419','pt-BR','fr','ja','ko','hi']

def put_loc(v, localizations):
    s = v['snippet']
    body = {'id': v['id'], 'snippet': {
        'title': s['title'], 'description': s.get('description',''), 'tags': s.get('tags',[])[:15],
        'categoryId': s.get('categoryId','27'), 'defaultLanguage': 'de', 'defaultAudioLanguage': 'de'},
        'localizations': localizations}
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet,localizations',
        data=json.dumps(body).encode('utf-8'),
        headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

import os
EXCLUDE = {'LJ4Dz-aeD0o'}  # geflaggtes Duplikat (Wochenschau 593) - nicht anfassen
PROG = 'config/wochenschau_loc_progress.json'
done = set(json.load(open(PROG)) ) if os.path.exists(PROG) else set()

picked = []
for v in woch:
    if v['id'] in EXCLUDE or v['id'] in done: continue
    m = re.search(r'Nr\.?\s*(\d+)', v['snippet']['title'])
    if not m: continue
    nr = m.group(1)
    if nr not in EV: continue
    picked.append((v, nr, EV[nr]))

print(f'\n=== LOKALISIERUNG: {len(picked)} Wochenschau offen (bereits fertig: {len(done)}, ausgeschlossen: {len(EXCLUDE)}) ===')
ok = err = 0; quota_hit = False
for v, nr, ev in picked:
    year = ev['date'][:4]
    locs = {lg: {'title': title(lg, nr, ev, year), 'description': desc(lg, nr, ev, year)} for lg in LANGS}
    if not APPLY:
        print(f"  Nr. {nr} ({ev['event_en']}) -> 9 Sprachen")
        continue
    try:
        put_loc(v, locs); ok += 1; done.add(v['id'])
        if ok % 10 == 0:
            print(f'  [{ok}] localized (zuletzt Nr. {nr})')
            json.dump(sorted(done), open(PROG,'w'))
        time.sleep(0.45)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:150]
        if 'quotaExceeded' in body:
            print(f'  [QUOTA] erreicht bei Nr. {nr} - Stopp, morgen resume.'); quota_hit = True; break
        err += 1; print(f'  ✗ Nr. {nr}: {body[:90]}')
    except Exception as e:
        err += 1; print(f'  ✗ Nr. {nr}: {str(e)[:90]}')

if APPLY:
    json.dump(sorted(done), open(PROG,'w'))
    print(f"\n=== {ok} lokalisiert, {err} Fehler, {len(picked)-ok-err} offen{' (QUOTA - morgen weiter)' if quota_hit else ''} ===")
    print(f'Fortschritt gespeichert: {PROG} ({len(done)} fertig)')
else:
    print(f'\n[DRY-RUN] {len(picked)} offen. Mit --apply schreiben.')
