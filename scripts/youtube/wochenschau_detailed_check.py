#!/usr/bin/env python3
"""
WOCHENSCHAU DETAILED CHECK
Prüft ob die individuellen Orte/Events aus wochenschau_complete_locations.json
tatsächlich in den Videos verwendet werden.

Workspace-Daten:
- config/wochenschau_complete_locations.json (3026 Zeilen!)
- config/wochenschau_events.json (1527 Zeilen!)
- docs/templates/WOCHENSCHAU_MULTILINGUAL_SEO.md (342 Zeilen)
"""

import json
import re

print("="*70)
print("🎬 WOCHENSCHAU DETAILED CHECK")
print("="*70)

# Lade Location/Event Daten
with open('config/wochenschau_complete_locations.json', 'r', encoding='utf-8') as f:
    locations_data = json.load(f)

with open('config/wochenschau_events.json', 'r', encoding='utf-8') as f:
    events_data = json.load(f)

# Lade Channel Scan
with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    channel_data = json.load(f)

print(f"\n📊 WORKSPACE-DATEN:")
print(f"   Locations definiert: {len(locations_data)} Episoden")
print(f"   Events definiert: {len(events_data.get('events', {}))} Episoden")

# Extrahiere Wochenschau-Videos aus Channel
wochenschau_videos = []
for v in channel_data['videos']:
    title = v['snippet']['title'].lower()
    if 'wochenschau' in title:
        # Extrahiere Nummer aus Titel
        nr_match = re.search(r'(\d{3})', v['snippet']['title'])
        nr = nr_match.group(1) if nr_match else None
        wochenschau_videos.append({
            'id': v['id'],
            'title': v['snippet']['title'],
            'desc': v['snippet'].get('description', ''),
            'tags': v['snippet'].get('tags', []),
            'nr': nr,
            'status': v['status']['privacyStatus']
        })

print(f"   Videos auf Channel: {len(wochenschau_videos)}")
print(f"     - Public: {sum(1 for v in wochenschau_videos if v['status'] == 'public')}")
print(f"     - Private/Draft: {sum(1 for v in wochenschau_videos if v['status'] != 'public')}")

# Analysiere jedes Video
print("\n" + "="*70)
print("📋 INDIVIDUAL VIDEO ANALYSIS")
print("="*70)

checks = {
    'has_location_in_desc': {'pass': 0, 'fail': []},
    'has_event_in_title': {'pass': 0, 'fail': []},
    'has_date_format': {'pass': 0, 'fail': []},
    'has_multilingual_desc': {'pass': 0, 'fail': []},
    'has_remaike_brand': {'pass': 0, 'fail': []},
    'has_8k': {'pass': 0, 'fail': []},
    'hashtags_2_5': {'pass': 0, 'fail': []},
    'tags_max_15': {'pass': 0, 'fail': []},
}

for v in wochenschau_videos:
    if v['status'] != 'public':
        continue
    
    nr = v['nr']
    title = v['title']
    desc = v['desc']
    tags = v['tags']
    
    # 1. Location in Description?
    location_info = locations_data.get(nr, {})
    expected_location = location_info.get('location', {}).get('desc', '')
    if expected_location and expected_location.lower() in desc.lower():
        checks['has_location_in_desc']['pass'] += 1
    else:
        checks['has_location_in_desc']['fail'].append({
            'nr': nr,
            'title': title[:50],
            'expected': expected_location,
            'found': 'MISSING'
        })
    
    # 2. Event in Title?
    events = events_data.get('events', {})
    event_info = events.get(nr, {})
    expected_event = event_info.get('event_en', '')
    if expected_event and expected_event.lower() in title.lower():
        checks['has_event_in_title']['pass'] += 1
    else:
        checks['has_event_in_title']['fail'].append({
            'nr': nr,
            'title': title[:50],
            'expected': expected_event,
            'found': 'MISSING'
        })
    
    # 3. Datum-Format (DD.MM.YYYY)?
    if re.search(r'\d{2}\.\d{2}\.\d{4}', title):
        checks['has_date_format']['pass'] += 1
    else:
        checks['has_date_format']['fail'].append({
            'nr': nr,
            'title': title[:50]
        })
    
    # 4. Multilingual Keywords in Desc?
    multilingual_markers = ['🇩🇪', '🇬🇧', '🇪🇸', '🇫🇷', 'Zweiter Weltkrieg', 'World War', 'Segunda Guerra']
    has_multilingual = any(m in desc for m in multilingual_markers)
    if has_multilingual:
        checks['has_multilingual_desc']['pass'] += 1
    else:
        checks['has_multilingual_desc']['fail'].append({
            'nr': nr,
            'title': title[:50]
        })
    
    # 5. @remAIke_IT Brand?
    if '@remaike' in title.lower():
        checks['has_remaike_brand']['pass'] += 1
    else:
        checks['has_remaike_brand']['fail'].append({
            'nr': nr,
            'title': title[:50]
        })
    
    # 6. 8K in Title?
    if '8k' in title.lower():
        checks['has_8k']['pass'] += 1
    else:
        checks['has_8k']['fail'].append({
            'nr': nr,
            'title': title[:50]
        })
    
    # 7. Hashtags 2-5?
    hashtag_count = desc.count('#')
    if 2 <= hashtag_count <= 5:
        checks['hashtags_2_5']['pass'] += 1
    else:
        checks['hashtags_2_5']['fail'].append({
            'nr': nr,
            'title': title[:40],
            'count': hashtag_count
        })
    
    # 8. Tags max 15?
    if len(tags) <= 15:
        checks['tags_max_15']['pass'] += 1
    else:
        checks['tags_max_15']['fail'].append({
            'nr': nr,
            'title': title[:40],
            'count': len(tags)
        })

# Report
print("\n" + "="*70)
print("📊 WOCHENSCHAU COMPLIANCE REPORT")
print("="*70)

total_public = sum(1 for v in wochenschau_videos if v['status'] == 'public')

report = []
for check_name, data in checks.items():
    passed = data['pass']
    failed = len(data['fail'])
    total = passed + failed
    if total == 0:
        continue
    pct = passed * 100 // total
    
    icon = "✅" if pct >= 90 else ("🟡" if pct >= 70 else "❌")
    label = check_name.replace('_', ' ').title()
    
    report.append({
        'check': label,
        'passed': passed,
        'total': total,
        'pct': pct,
        'icon': icon,
        'fails': data['fail'][:5]  # Max 5 Beispiele
    })
    
    print(f"{icon} {label}: {passed}/{total} ({pct}%)")

# Detaillierte Fails
print("\n" + "="*70)
print("❌ FEHLENDE INDIVIDUELLE DATEN")
print("="*70)

# Location Fails
location_fails = checks['has_location_in_desc']['fail']
if location_fails:
    print(f"\n📍 ORTE FEHLEN ({len(location_fails)} Videos):")
    for f in location_fails[:10]:
        print(f"   Nr.{f['nr']}: Erwartet '{f['expected']}' → FEHLT")

# Event Fails
event_fails = checks['has_event_in_title']['fail']
if event_fails:
    print(f"\n📅 EVENTS FEHLEN IM TITEL ({len(event_fails)} Videos):")
    for f in event_fails[:10]:
        print(f"   Nr.{f['nr']}: Erwartet '{f['expected']}' → FEHLT")

# Brand Fails
brand_fails = checks['has_remaike_brand']['fail']
if brand_fails:
    print(f"\n🏷️ @remAIke_IT FEHLT ({len(brand_fails)} Videos):")
    for f in brand_fails[:5]:
        print(f"   Nr.{f['nr']}: {f['title']}")

# Multilingual Fails
multilingual_fails = checks['has_multilingual_desc']['fail']
if multilingual_fails:
    print(f"\n🌍 MULTILINGUAL DESC FEHLT ({len(multilingual_fails)} Videos):")
    for f in multilingual_fails[:5]:
        print(f"   Nr.{f['nr']}: {f['title']}")

# Hashtag Issues
hashtag_fails = checks['hashtags_2_5']['fail']
if hashtag_fails:
    print(f"\n#️⃣ HASHTAGS NICHT 2-5 ({len(hashtag_fails)} Videos):")
    for f in hashtag_fails[:5]:
        print(f"   Nr.{f['nr']}: {f['count']} Hashtags → {f['title']}")

# Save Report
result = {
    'total_wochenschau': len(wochenschau_videos),
    'public': total_public,
    'checks': {k: {'passed': v['pass'], 'failed': len(v['fail'])} for k, v in checks.items()},
    'location_fails': location_fails,
    'event_fails': event_fails,
    'brand_fails': brand_fails,
    'multilingual_fails': multilingual_fails,
    'hashtag_fails': hashtag_fails
}

with open('config/wochenschau_detailed_check.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n✅ Report gespeichert: config/wochenschau_detailed_check.json")
