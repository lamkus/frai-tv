#!/usr/bin/env python3
"""
AUDIT: Was habe ich heute kaputt gemacht?
Verwendet PUBLIC API (nicht OAuth!) für READ-only Analyse.
"""
import os
import requests
import json

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    print("❌ YOUTUBE_API_KEY nicht gesetzt!")
    print("   Setze: $env:YOUTUBE_API_KEY = 'dein-key'")
    exit(1)

# Videos die ich heute geändert habe (aus meinen Scripts)
CHANGED_VIDEOS = {
    # BraveStarr - öffentlich
    'XU7yM4H5vrY': 'BraveStarr Musikfestival (sollte E01 sein)',
    
    # BraveStarr Drafts (private - werden nicht via Public API sichtbar sein)
    'EaOwzlJuQJU': 'BraveStarr E02 Draft (sollte "Das Ungetüm aus der Wüste" sein)',
    '5qhJxQk89vE': 'BraveStarr E04 Draft (sollte "Der Weltraumzoo" sein)',
    
    # Shorts die ich geändert habe
    'Y7YQf5F_xw4': 'Short 1',
    '_wWo_2l-zn8': 'Short 2', 
    'j2WQjj-b4F4': 'Short 3',
    '2QO4ZYLV4wk': 'Short 4',
    'xKjvTL1F6dM': 'Short 5',
}

def check_video(video_id, expected):
    """Prüft ein Video via Public API"""
    url = 'https://youtube.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet',
        'id': video_id,
        'key': API_KEY
    }
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if 'items' not in data or len(data['items']) == 0:
            return {'status': 'NOT_FOUND', 'reason': 'Private oder gelöscht', 'expected': expected}
        
        snippet = data['items'][0]['snippet']
        return {
            'status': 'FOUND',
            'title': snippet.get('title', ''),
            'description': snippet.get('description', '')[:200] + '...',
            'tags': snippet.get('tags', []),
            'expected': expected
        }
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e), 'expected': expected}

print("=" * 70)
print("🔍 AUDIT: Meine heutigen Änderungen (Public API)")
print("=" * 70)
print()

results = {}
for vid, expected in CHANGED_VIDEOS.items():
    print(f"Prüfe {vid}...")
    results[vid] = check_video(vid, expected)

print()
print("=" * 70)
print("📊 ERGEBNISSE")
print("=" * 70)

# Problematische Tags die NIEMALS bei Kinderfilmen sein sollten
BAD_TAGS = [
    'sex', 'sexy', 'nude', 'naked', 'porn', 'xxx', 'adult', 'erotic',
    'tits', 'boobs', 'ass', 'fuck', 'shit', 'damn', 'hell',
    'violence', 'gore', 'blood', 'kill', 'murder', 'death',
    'drug', 'cocaine', 'weed', 'marijuana', 'alcohol', 'beer', 'wine',
    'gun', 'weapon', 'shoot', 'war', 'terror',
    # German
    'nackt', 'sex', 'erotik', 'gewalt', 'blut', 'tod', 'drogen', 'waffe'
]

problems = []

for vid, data in results.items():
    print()
    print(f"📹 {vid}")
    print(f"   Erwartet: {data['expected']}")
    
    if data['status'] == 'NOT_FOUND':
        print(f"   Status: ⚠️ Nicht öffentlich sichtbar (Private/Draft)")
    elif data['status'] == 'ERROR':
        print(f"   Status: ❌ Fehler: {data['error']}")
    else:
        print(f"   Titel: {data['title']}")
        print(f"   Tags ({len(data['tags'])}): {data['tags'][:10]}...")
        
        # Prüfe auf problematische Tags
        bad_found = []
        for tag in data['tags']:
            tag_lower = tag.lower()
            for bad in BAD_TAGS:
                if bad in tag_lower:
                    bad_found.append(tag)
                    break
        
        if bad_found:
            print(f"   ⚠️ PROBLEMATISCHE TAGS: {bad_found}")
            problems.append((vid, data['title'], bad_found))
        else:
            print(f"   ✅ Keine offensichtlich problematischen Tags")

print()
print("=" * 70)
print("📋 ZUSAMMENFASSUNG")
print("=" * 70)

if problems:
    print()
    print("❌ PROBLEME GEFUNDEN:")
    for vid, title, bad_tags in problems:
        print(f"   - {vid}: {title}")
        print(f"     Problematische Tags: {bad_tags}")
else:
    print()
    print("✅ Keine offensichtlich problematischen Tags in öffentlichen Videos gefunden.")
    print("   (Private Drafts können nicht via Public API geprüft werden)")

# Speichere Report
report = {
    'audit_date': '2026-01-13',
    'method': 'Public API (READ-only)',
    'results': results,
    'problems': [{'id': p[0], 'title': p[1], 'bad_tags': p[2]} for p in problems]
}

with open('config/change_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print()
print("📄 Report gespeichert: config/change_audit_report.json")
