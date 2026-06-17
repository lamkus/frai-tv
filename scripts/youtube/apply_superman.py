# -*- coding: utf-8 -*-
"""Superman (Fleischer/Famous 1941-43, Public Domain): Titel sind bereits korrekt -> behalten.
Setzt defaultLanguage/Audio='en' (Auto-Dub-Hebel!), SOTA-Beschreibung, recordingDate (Jahr), categoryId.
Dubletten werden geflaggt (nur Keeper geschrieben). DRY default; --apply schreibt. Quota-/resume-sicher.
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))

# (videoId, cartoon_title, year) ; Keeper pro Cartoon-Nr. Duplikate -> DUPES
EPISODES = [
    ('6A2_RKWP2X4', 'Superman', 1941, 1),
    ('guleycwwXeQ', 'Billion Dollar Limited', 1942, 3),
    ('Aq1OfWdwV-Q', 'Electric Earthquake', 1942, 7),
    ('cH5VPFJFKtI', 'Terror on the Midway', 1942, 9),
    ('bShrsrrzOYQ', 'Japoteurs', 1942, 10),
    ('MGDT-j7K32s', 'The Mummy Strikes', 1943, 14),
    ('5H3WyI_TG-I', 'Jungle Drums', 1943, 15),
    ('D4Rphx3UDzQ', 'The Underground World', 1943, 16),
]
DUPES = ['e0Tagj2Z5SU', 'unzHtnrKeOU']  # #1 + #10 Doppel-Uploads -> löschen (deine Aktion)
SUB = 'https://www.youtube.com/@remAIke_IT?sub_confirmation=1'

def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token(); print('[AUTH] OK')

def desc(ct, yr, n):
    return (f'{ct} ({yr}) – der klassische Superman-Zeichentrick (Folge {n}/17) von Fleischer/Famous Studios, '
            f'in 8K (4K UHD) KI-restauriert von remAIke.TV.\n\n'
            f'Einer der 17 legendären Superman-Cartoons (1941–1943), produziert von Fleischer Studios und Famous '
            f'Studios für Paramount – wegweisende Animation, die den Superhelden auf der Leinwand definierte. '
            f'Originalmaterial: Public Domain.\n\n'
            f'Alle Klassiker kostenlos auf frai.TV:\nhttps://frai.tv\n\nAbonnieren:\n{SUB}\n\n'
            f'[EN] Superman ({yr}): {ct} – the classic Fleischer/Famous Studios theatrical cartoon, 8K AI-restored.\n\n'
            f'#Superman #FleischerStudios #Zeichentrick #Cartoon #8K #remAIke')

def tags(ct):
    out = ['Superman', 'Fleischer Studios', 'Famous Studios', ct, 'Zeichentrick', 'Cartoon', 'remAIke.TV', '8K']
    seen=[]; [seen.append(t) for t in out if t and t not in seen]
    return seen[:8]

ok=err=0; quota=False
for vid, ct, yr, n in EPISODES:
    title = f'Superman ({n}/17): {ct} ({yr}) | 8K HQ (4K UHD)'
    body = {'id':vid,'snippet':{'title':title,'description':desc(ct,yr,n),'tags':tags(ct),
        'categoryId':'1','defaultLanguage':'en','defaultAudioLanguage':'en'},
        'recordingDetails':{'recordingDate':f'{yr}-01-01T00:00:00Z'}}
    if not APPLY:
        print(f'  [DRY] {vid} -> {title} (en, {yr})'); ok+=1; continue
    try:
        urllib.request.urlopen(urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet,recordingDetails',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        ok+=1; print(f'  [OK]  {vid}: {ct} ({yr}) | lang=en'); time.sleep(0.4)
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] nach {ok}'); quota=True; break
        err+=1; print(f'  [ERR] {vid}: {b[:90]}')
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} {"geschrieben" if APPLY else "(dry)"}, {err} Fehler{" (QUOTA)" if quota else ""} | Dubletten zum Löschen: {", ".join(DUPES)} ===')
