# -*- coding: utf-8 -*-
"""Deterministischer Metadaten-Builder (0 LLM-Token, idempotent).
Input: verifizierte Fakten (config/wochenschau_verified.json) + Serien-Enrichment + SOTA-Schema-Regeln.
Output: kanonische {title, description, tags, recordingDate, defaultLanguage, defaultAudioLanguage} pro Folge.
Gleicher Input -> gleicher Output. Wird vom Applier benutzt; --dry zeigt Vorschau.
"""
import io, sys, json, os, re

SUB = 'https://www.youtube.com/@remAIke_IT?sub_confirmation=1'
PLAYLIST = 'https://www.youtube.com/playlist?list=PL3d2Tsr13ihNgiDVAlRAi7wlwxxb-tzHI'
RESTAGE = '8K HQ (4K UHD)'
DISCLAIMER = ('WICHTIGER HINWEIS: Diese Aufnahmen dienen ausschliesslich der historischen Bildung und '
              'Dokumentation. Sie verherrlichen in keiner Weise totalitaere Regime oder deren Ideologien.')

def de_date(iso):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', iso or '')
    return f'{m.group(3)}.{m.group(2)}.{m.group(1)}' if m else ''

def year_of(iso):
    return (iso or '')[:4]

def series_label(nr):
    # "Deutsche Wochenschau" ist der reichweitenstarke Suchbegriff -> IMMER prominent.
    # Frühe Folgen (Nr. < 510, vor Juni 1940) sind historisch UfA-Tonwoche -> als korrekter Zusatz.
    try: n = int(nr)
    except: n = 9999
    if n < 510:
        return ('Deutsche Wochenschau (UfA-Tonwoche)', 'Deutsche Wochenschau / UfA-Tonwoche')
    return ('Deutsche Wochenschau', 'Die Deutsche Wochenschau')

def build_title(ep):
    """Ereignis VORN (SOTA): {Event} - {Serie} Nr. {N} ({Datum}) | {RESTAGE}. Hard-cap 100, Laengen-Guard."""
    nr = str(ep['nr']); ev = (ep.get('event_keyword_de') or '').strip()
    short, _full = series_label(nr)
    d = de_date(ep.get('verified_date'))
    y = year_of(ep.get('verified_date'))
    if not ev:  # kein verifiziertes Ereignis -> neutraler Titel
        base = f'{short} Nr. {nr}' + (f' ({d})' if d else '')
        return (base + f' | {RESTAGE}')[:100]
    variants = [
        f'{ev} – {short} Nr. {nr} ({d}) | {RESTAGE}',
        f'{ev} – {short} Nr. {nr} ({d}) | 8K',
        f'{ev} – {short} Nr. {nr} ({y}) | 8K',
        f'{ev} – {short} Nr. {nr} | 8K',
        f'{ev} – {short} Nr. {nr}',
    ]
    for v in variants:
        if len(v) <= 100: return v
    return variants[-1][:100]

def build_description(ep, video_id=None):
    nr = str(ep['nr']); ev = (ep.get('event_keyword_de') or '').strip()
    _short, full = series_label(nr)
    d = de_date(ep.get('verified_date')); y = year_of(ep.get('verified_date'))
    ev_en = (ep.get('event_keyword_en') or ev).strip()
    summary = (ep.get('content_summary_de') or '').strip()
    srcs = ep.get('source_urls') or []
    src = next((s for s in srcs if 'archive.org' in s), (srcs[0] if srcs else ''))
    watch = f'https://frai.tv/watch/{video_id}/' if video_id else 'https://frai.tv'
    # SOTA-5-Block, hook-Zeile <=125 mit Entitaet+Jahr+Marke
    hook = f'{ev} – {full} Nr. {nr} ({d}). In 8K (4K UHD) KI-restauriert von remAIke.TV.'
    blocks = [hook[:125] if len(hook) > 125 else hook]
    if summary: blocks.append('Inhalt dieser Ausgabe: ' + summary + '.')
    blocks.append(DISCLAIMER)
    cite = []
    if src: cite.append(f'Quelle / Source: {src}')
    cite.append('Originalmaterial: Public Domain.')
    blocks.append('\n'.join(cite))
    blocks.append(f'Mehr {full}-Episoden:\n{PLAYLIST}\n\nAlle Klassiker kostenlos auf frai.TV:\n{watch}\n\nAbonnieren:\n{SUB}')
    if ev_en:
        blocks.append(f'[EN] {full} No. {nr} ({y}): {ev_en} – 8K AI-restored historical WWII newsreel.')
    tag_words = ['Wochenschau', 'WWII', 'Zweiter Weltkrieg', '8K', 'remAIke']
    blocks.append(' '.join('#' + w for w in tag_words))
    return '\n\n'.join(blocks)[:4900]

def build_tags(ep):
    """SOTA: 5-8 Tags, nur Entitaet + Marke + Schreibvarianten. KEIN Stuffing."""
    nr = str(ep['nr'])
    try: is_ton = int(nr) < 510
    except: is_ton = False
    out = ['Deutsche Wochenschau', 'Wochenschau', f'Wochenschau {nr}', 'remAIke.TV', '@remAIke_IT']
    if is_ton: out.insert(1, 'UfA-Tonwoche')
    ev = (ep.get('event_keyword_de') or '')
    for w in re.split(r'[&–/]', ev):
        w = w.strip()
        if w and len(out) < 8 and w not in out: out.append(w)
    seen = []
    for t in out:
        if t and t not in seen: seen.append(t)
    return seen[:8]

def build(ep, video_id=None):
    return {
        'nr': str(ep['nr']),
        'video_id': video_id,
        'title': build_title(ep),
        'description': build_description(ep, video_id),
        'tags': build_tags(ep),
        'recordingDate': (ep.get('verified_date') + 'T00:00:00Z') if ep.get('verified_date') else None,
        'defaultLanguage': 'de',
        'defaultAudioLanguage': 'de',
        'categoryId': '27',  # Education
        'confidence': ep.get('confidence'),
    }

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    eps = json.load(open('config/wochenschau_verified.json', encoding='utf-8'))
    canon = [build(e) for e in eps]
    json.dump(canon, open('config/wochenschau_canonical.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'Builder: {len(canon)} Folgen -> config/wochenschau_canonical.json')
    # alte Titel (falsch) zum Vergleich laden
    try:
        old = {}
        for v in json.load(open('config/all_videos_raw.json', encoding='utf-8')):
            t = v.get('title', ''); m = re.search(r'Wochenschau (\d+)', t)
            if m: old[m.group(1)] = t
    except: old = {}
    print('\n=== DRY-RUN Stichproben (ALT -> NEU) ===')
    for nr in ['459', '511', '620', '652', '698', '713', '752']:
        c = next((x for x in canon if x['nr'] == nr), None)
        if not c: continue
        print(f"\n--- Nr. {nr} ({c['confidence']}) ---")
        if old.get(nr): print('ALT:', old[nr])
        print('NEU:', c['title'], f"({len(c['title'])} Zeichen)")
        print('REC:', c['recordingDate'], '| TAGS:', ', '.join(c['tags']))
        print('DESC[:240]:', c['description'][:240].replace('\n', ' / '))
