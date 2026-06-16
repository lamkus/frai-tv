# -*- coding: utf-8 -*-
"""Deterministischer Builder fuer Alfred J. Kwak (urheberrechtlich -> KEIN Public-Domain-Claim).
Input: config/alfred_episodes.json (52 autoritative Titel) + series_enrichment (Alfred).
Output: config/alfred_canonical.json. --dry zeigt ALT->NEU + Dubletten.
Titel: Entity vorn -> "Alfred J. Kwak (E##) <Titel> | 8K HQ (4K UHD)".
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EPS = json.load(open('config/alfred_episodes.json', encoding='utf-8'))
try:
    SER = json.load(open('config/series_enrichment.json', encoding='utf-8'))
    AL = next((s for s in SER if 'kwak' in json.dumps(s, ensure_ascii=False).lower() or 'alfred' in json.dumps(s, ensure_ascii=False).lower()), None)
except Exception:
    AL = None
HIST = (AL or {}).get('history', '').strip() if AL else ''

HUB = 'https://frai.tv/series/kwak/'
SUB = 'https://www.youtube.com/@remAIke_IT?sub_confirmation=1'
RESTAGE = '8K HQ (4K UHD)'

def e2(n): return f'E{int(n):02d}'

def build_title(ep):
    n = ep['ep']; t = ep['title_de']
    for v in [f'Alfred J. Kwak ({e2(n)}) {t} | {RESTAGE}', f'Alfred J. Kwak ({e2(n)}) {t} | 8K', f'Alfred J. Kwak ({e2(n)}) {t}']:
        if len(v) <= 100: return v
    return f'Alfred J. Kwak ({e2(n)}) {t}'[:100]

def build_description(ep, video_id=None):
    n = ep['ep']; t = ep['title_de']
    watch = f'https://frai.tv/watch/{video_id}/' if video_id else HUB
    hook = f'Alfred J. Kwak – Folge {n}: {t}. Der Zeichentrick-Klassiker (1989) in 8K (4K UHD), KI-restauriert von remAIke.TV.'
    blocks = [hook[:125] if len(hook) > 125 else hook]
    series = HIST or ('Alfred J. Kwak ist eine deutsch-niederlaendisch-japanische Zeichentrickserie von 1989, basierend auf einer Figur von Herman van Veen. '
                      'Die 52 Folgen erzaehlen die Geschichte der Ente Alfred Jodocus Kwak und behandeln Themen wie Freundschaft, Toleranz, Umwelt und Demokratie.')
    blocks.append(series)
    blocks.append(f'Alle Folgen von Alfred J. Kwak:\n{HUB}\n\nMehr Klassiker auf frai.TV:\n{watch}\n\nAbonnieren:\n{SUB}')
    blocks.append(f'[EN] Alfred J. Kwak (1989) Episode {n}: {t} – classic animated series in 8K AI-restored.')
    blocks.append('#AlfredJKwak #Zeichentrick #Kinderserie #8K #remAIke')
    return '\n\n'.join(blocks)[:4900]

def build_tags(ep):
    n = ep['ep']
    out = ['Alfred J. Kwak', 'Alfred Jodocus Kwak', f'Alfred J. Kwak Folge {n}', 'Zeichentrick', 'Kinderserie', 'remAIke.TV', '@remAIke_IT']
    seen = []
    for t in out:
        if t and t not in seen: seen.append(t)
    return seen[:8]

def build(ep, video_id=None):
    return {
        'ep': ep['ep'], 'video_id': video_id,
        'title': build_title(ep), 'description': build_description(ep, video_id),
        'tags': build_tags(ep), 'recordingDate': None,  # Cartoon: keine sinnvolle Aufnahme-Datierung
        'defaultLanguage': 'de', 'defaultAudioLanguage': 'de', 'categoryId': '1',  # Film & Animation
    }

if __name__ == '__main__':
    canon = [build(e) for e in EPS]
    json.dump(canon, open('config/alfred_canonical.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'Builder: {len(canon)} Folgen -> config/alfred_canonical.json | Alfred-Enrichment gefunden: {bool(HIST)}')
    # ALT-Titel aus Cache + E##-Match (Dubletten zeigen)
    try:
        cache = json.load(open('config/all_videos_raw.json', encoding='utf-8'))
    except Exception:
        cache = []
    bye = {}
    for v in cache:
        t = v.get('title', '')
        if 'Kwak' not in t: continue
        m = re.search(r'E0?(\d{1,2})', t)
        if m: bye.setdefault(int(m.group(1)), []).append((v.get('id', ''), t))
    print('\n=== DRY-RUN Stichproben (ALT -> NEU) ===')
    for n in [6, 14, 15, 43, 47, 52]:
        c = next((x for x in canon if x['ep'] == n), None)
        if not c: continue
        olds = bye.get(n, [])
        print(f"\n--- E{n:02d} ({len(olds)} Video(s){' DUBLETTE!' if len(olds) > 1 else ''}) ---")
        for vid, ot in olds[:3]: print('  ALT:', ot[:70])
        print('  NEU:', c['title'], f"({len(c['title'])}z)")
    dups = {n: len(v) for n, v in bye.items() if len(v) > 1}
    print('\nDubletten (E## mit >1 Video):', dups)
    print('Episoden im Cache gefunden:', sorted(bye.keys()))
