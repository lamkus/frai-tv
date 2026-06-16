#!/usr/bin/env python3
"""
REVERSE CHECK: Prüft Channel gegen ALLE SEO-Regeln aus Research
Basierend auf:
- docs/youtube/YOUTUBE_ALGORITHM_2026.md
- docs/WOCHENSCHAU_SEO_KONZEPT.md
- docs/templates/SOUNDIES_SEO_TEMPLATE.md
- docs/templates/WOCHENSCHAU_MULTILINGUAL_SEO.md
- .github/copilot-instructions.md
"""

import json
import re

print("="*70)
print("🔍 REVERSE CHECK: CHANNEL vs SEO REGELN 2026")
print("="*70)

with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n📅 Scan: {data['fetched_at']}")
print(f"📺 Videos: {data['public']} public\n")

# === REGELN AUS RESEARCH ===
checks = {
    # TITEL-REGELN
    'title_max_70': {'pass': 0, 'fail': [], 'rule': 'Titel max 70 Zeichen'},
    'title_keyword_first': {'pass': 0, 'fail': [], 'rule': 'Keyword am ANFANG des Titels'},
    'title_8k': {'pass': 0, 'fail': [], 'rule': '8K oder 8K HQ im Titel'},
    'title_brand': {'pass': 0, 'fail': [], 'rule': '@remAIke_IT im Titel'},
    'title_year': {'pass': 0, 'fail': [], 'rule': 'Jahr in Klammern (YYYY)'},
    
    # DESCRIPTION-REGELN  
    'desc_cta': {'pass': 0, 'fail': [], 'rule': 'CTA (LIKE/SUBSCRIBE) in Description'},
    'desc_hashtags': {'pass': 0, 'fail': [], 'rule': 'Hashtags vorhanden (2-5)'},
    'desc_not_excessive_hashtags': {'pass': 0, 'fail': [], 'rule': 'Max 5 Hashtags (nicht mehr!)'},
    'desc_playlist_link': {'pass': 0, 'fail': [], 'rule': 'Playlist-Link in Description'},
    
    # TAGS-REGELN
    'tags_max_15': {'pass': 0, 'fail': [], 'rule': 'Max 15 Tags (YouTube sagt MINIMAL!)'},
    'tags_not_empty': {'pass': 0, 'fail': [], 'rule': 'Min 5 Tags vorhanden'},
    
    # KATEGORIE-SPEZIFISCH
    'soundie_music_category': {'pass': 0, 'fail': [], 'rule': 'Soundies = Category Music (10)'},
    'wochenschau_format': {'pass': 0, 'fail': [], 'rule': 'Wochenschau: Keyword + Nr + Event'},
}

# Zähler für Kategorien
categories = {'soundie': 0, 'wochenschau': 0, 'betty': 0, 'alfred': 0, 'other': 0}

for v in data['videos']:
    if v['status']['privacyStatus'] != 'public':
        continue
        
    vid = v['id']
    title = v['snippet']['title']
    desc = v['snippet'].get('description', '')
    tags = v['snippet'].get('tags', [])
    category = v['snippet'].get('categoryId', '0')
    title_lower = title.lower()
    
    # Kategorisieren
    if 'soundie' in title_lower:
        categories['soundie'] += 1
        cat = 'soundie'
    elif 'wochenschau' in title_lower:
        categories['wochenschau'] += 1
        cat = 'wochenschau'
    elif 'betty boop' in title_lower:
        categories['betty'] += 1
        cat = 'betty'
    elif 'alfred' in title_lower:
        categories['alfred'] += 1
        cat = 'alfred'
    else:
        categories['other'] += 1
        cat = 'other'
    
    # === TITEL CHECKS ===
    
    # 1. Max 70 chars
    if len(title) <= 70:
        checks['title_max_70']['pass'] += 1
    else:
        checks['title_max_70']['fail'].append((vid, f"[{len(title)}] {title[:50]}"))
    
    # 2. Keyword am Anfang
    good_starts = ['betty boop', 'wochenschau', 'alfred', 'felix', 'soundie', 
                   'superman', 'porky', 'looney', 'popeye', 'casper', 'die deutsche']
    has_keyword_first = any(title_lower.startswith(kw) for kw in good_starts)
    # Auch OK: Song-Titel für Soundies
    if cat == 'soundie' and '|' in title:  # Song | Soundie format
        has_keyword_first = True
    if has_keyword_first:
        checks['title_keyword_first']['pass'] += 1
    else:
        checks['title_keyword_first']['fail'].append((vid, title[:50]))
    
    # 3. 8K im Titel
    if '8k' in title_lower or '8K' in title:
        checks['title_8k']['pass'] += 1
    else:
        checks['title_8k']['fail'].append((vid, title[:50]))
    
    # 4. @remAIke_IT im Titel
    if '@remaike' in title_lower:
        checks['title_brand']['pass'] += 1
    else:
        checks['title_brand']['fail'].append((vid, title[:50]))
    
    # 5. Jahr in Klammern
    year_match = re.search(r'\(1[89]\d{2}\)', title) or re.search(r'\(20\d{2}\)', title)
    if year_match:
        checks['title_year']['pass'] += 1
    else:
        checks['title_year']['fail'].append((vid, title[:50]))
    
    # === DESCRIPTION CHECKS ===
    
    # 6. CTA vorhanden
    cta_keywords = ['subscribe', 'like', 'comment', 'abonnier', '👆', '💬', '🔔', 'LIKE', 'SUBSCRIBE']
    has_cta = any(kw in desc for kw in cta_keywords)
    if has_cta:
        checks['desc_cta']['pass'] += 1
    else:
        checks['desc_cta']['fail'].append((vid, title[:40]))
    
    # 7. Hashtags vorhanden
    hashtag_count = desc.count('#')
    if hashtag_count >= 2:
        checks['desc_hashtags']['pass'] += 1
    else:
        checks['desc_hashtags']['fail'].append((vid, f"[{hashtag_count}] {title[:40]}"))
    
    # 8. Nicht zu viele Hashtags (max 5 laut Research!)
    if hashtag_count <= 5:
        checks['desc_not_excessive_hashtags']['pass'] += 1
    else:
        checks['desc_not_excessive_hashtags']['fail'].append((vid, f"[{hashtag_count}] {title[:40]}"))
    
    # 9. Playlist-Link
    if 'playlist' in desc.lower() or 'youtube.com/playlist' in desc:
        checks['desc_playlist_link']['pass'] += 1
    else:
        checks['desc_playlist_link']['fail'].append((vid, title[:40]))
    
    # === TAGS CHECKS ===
    
    # 10. Max 15 Tags
    if len(tags) <= 15:
        checks['tags_max_15']['pass'] += 1
    else:
        checks['tags_max_15']['fail'].append((vid, f"[{len(tags)}] {title[:40]}"))
    
    # 11. Min 5 Tags
    if len(tags) >= 5:
        checks['tags_not_empty']['pass'] += 1
    else:
        checks['tags_not_empty']['fail'].append((vid, f"[{len(tags)}] {title[:40]}"))
    
    # === KATEGORIE-SPEZIFISCH ===
    
    # 12. Soundies = Music Category
    if cat == 'soundie':
        if category == '10':  # Music
            checks['soundie_music_category']['pass'] += 1
        else:
            checks['soundie_music_category']['fail'].append((vid, f"[cat={category}] {title[:40]}"))
    
    # 13. Wochenschau Format
    if cat == 'wochenschau':
        # Sollte haben: Wochenschau + Nr/Nummer + Event/Datum
        has_nr = 'nr' in title_lower or re.search(r'\d{3}', title)
        if has_nr:
            checks['wochenschau_format']['pass'] += 1
        else:
            checks['wochenschau_format']['fail'].append((vid, title[:50]))

# === REPORT ===
print("="*70)
print("📊 REGEL-COMPLIANCE REPORT")
print("="*70)

total = data['public']
overall_score = 0
max_score = 0

for key, check in checks.items():
    passed = check['pass']
    failed = len(check['fail'])
    total_check = passed + failed
    
    if total_check == 0:
        continue
        
    pct = passed * 100 // total_check if total_check > 0 else 0
    
    # Score berechnen
    if key.startswith('title_'):
        weight = 40 / 5  # 40 Punkte für Titel, 5 Checks
    elif key.startswith('desc_'):
        weight = 30 / 4  # 30 Punkte für Desc, 4 Checks
    else:
        weight = 30 / 4  # Rest
    
    score = (pct / 100) * weight
    overall_score += score
    max_score += weight
    
    # Status-Icon
    if pct >= 95:
        icon = "✅"
    elif pct >= 80:
        icon = "🟡"
    else:
        icon = "❌"
    
    print(f"{icon} {check['rule']}: {passed}/{total_check} ({pct}%)")
    
    # Bei Fehlern: Beispiele zeigen
    if failed > 0 and pct < 95:
        for vid, info in check['fail'][:3]:
            print(f"   ⚠️ {info}")
        if failed > 3:
            print(f"   ... und {failed-3} weitere")
    print()

# === ZUSAMMENFASSUNG ===
print("="*70)
print("🎯 ZUSAMMENFASSUNG")
print("="*70)

print(f"\nKategorien:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

final_score = (overall_score / max_score * 100) if max_score > 0 else 0
print(f"\n📊 OVERALL SEO COMPLIANCE: {final_score:.1f}/100")

if final_score >= 90:
    print("✅ EXCELLENT - Channel ist sehr gut optimiert!")
elif final_score >= 75:
    print("🟡 GOOD - Noch einige Verbesserungen möglich")
else:
    print("❌ NEEDS WORK - Signifikante SEO-Lücken!")

# Kritische Issues
print("\n🚨 KRITISCHE ISSUES:")
critical = []
for key, check in checks.items():
    if len(check['fail']) > 0:
        pct = check['pass'] * 100 // (check['pass'] + len(check['fail']))
        if pct < 80:
            critical.append((check['rule'], pct, len(check['fail'])))

if critical:
    for rule, pct, count in sorted(critical, key=lambda x: x[1]):
        print(f"  ❌ {rule}: nur {pct}% ({count} Fails)")
else:
    print("  ✅ Keine kritischen Issues!")

print("\n" + "="*70)
