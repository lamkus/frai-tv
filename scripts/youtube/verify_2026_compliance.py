#!/usr/bin/env python3
"""
VERIFY 2026 COMPLIANCE
Prüft ALLE Videos gegen die neuen technischen Standards (2025/2026).
"""

import json
import re

print("="*70)
print("🔬 TECHNICAL COMPLIANCE CHECK (2026 STANDARDS)")
print("="*70)

# Lade Channel Data
with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Lade Locations für detaillierten Kreuz-Check
with open('config/wochenschau_complete_locations.json', 'r', encoding='utf-8') as f:
    locations = json.load(f)

videos = data['videos']
public_videos = [v for v in videos if v['status']['privacyStatus'] == 'public']

print(f"📊 Analyzing {len(public_videos)} public videos...")

# === RULES ENGINE ===
rules = {
    'SAFETY_DISCLAIMER': {
        'name': 'EDSA Safety Disclaimer (Description)',
        'check': lambda v: 'HISTORICAL DOCUMENT' in v['snippet'].get('description', '').upper() or 'HISTORISCHES DOKUMENT' in v['snippet'].get('description', '').upper(),
        'target': ['wochenschau'] # Nur für sensitive content PFLICHT
    },
    'CATEGORY_EDUCATION': {
        'name': 'Category 27 (Education)',
        'check': lambda v: v['snippet'].get('categoryId') == '27',
        'target': ['wochenschau'] # Pflicht für History
    },
    'CATEGORY_MUSIC': {
        'name': 'Category 10 (Music)',
        'check': lambda v: v['snippet'].get('categoryId') == '10',
        'target': ['soundie'] # Pflicht für Musikvideos
    },
    'QUALITY_SIGNAL': {
        'name': '8K/4K Quality Signal',
        'check': lambda v: '8K' in v['snippet']['title'] or '4K' in v['snippet']['title'],
        'target': ['all']
    },
    'BRAND_SIGNAL': {
        'name': 'Brand Signal (@remAIke_IT)',
        'check': lambda v: '@remaike' in v['snippet']['description'].lower() or 'www.remaike.it' in v['snippet']['description'].lower(),
        'target': ['all']
    },
    'HASHTAG_OPTIMIZATION': {
        'name': 'Smart Hashtags (2-5 tags)',
        'check': lambda v: 2 <= v['snippet'].get('description', '').count('#') <= 5,
        'target': ['all']
    },
    'TAG_MINIMALISM': {
        'name': 'Minimal Tags (<= 15)',
        'check': lambda v: len(v['snippet'].get('tags', [])) <= 15,
        'target': ['all']
    },
    'LOCATION_CONTEXT': {
        'name': 'Location Metadata Injection',
        'check': lambda v: '📍 Location:' in v['snippet'].get('description', ''),
        'target': ['wochenschau']
    }
}

# === RUN CHECKS ===
results = {r: {'pass': 0, 'fail': 0, 'fails': []} for r in rules}

for v in public_videos:
    title = v['snippet']['title']
    vid = v['id']
    
    # Determine Type
    v_type = 'other'
    if 'wochenschau' in title.lower():
        v_type = 'wochenschau'
    elif 'soundie' in title.lower():
        v_type = 'soundie'
    
    for rule_key, rule in rules.items():
        # Check if rule applies to this video type
        if 'all' in rule['target'] or v_type in rule['target']:
            passed = rule['check'](v)
            if passed:
                results[rule_key]['pass'] += 1
            else:
                results[rule_key]['fail'] += 1
                results[rule_key]['fails'].append({
                    'id': vid,
                    'title': title[:50],
                    'type': v_type
                })

# === REPORT ===
print("\n" + "="*70)
print("📈 COMPLIANCE REPORT")
print("="*70)

overall_score = 0
total_checks = 0

for key, data in results.items():
    passed = data['pass']
    failed = data['fail']
    total = passed + failed
    
    if total == 0:
        continue
        
    rate = (passed / total) * 100
    icon = "✅" if rate >= 95 else ("⚠️" if rate >= 80 else "❌")
    
    overall_score += rate
    total_checks += 1
    
    print(f"{icon} {rules[key]['name']:<40} : {passed}/{total} ({rate:.1f}%)")
    
    if failed > 0 and failed < 10:
        for f in data['fails']:
            print(f"   ↳ FAIL: {f['title']}")
    elif failed >= 10:
        print(f"   ↳ {failed} videos failed (e.g. {data['fails'][0]['title']})")

print("-" * 70)
final_score = overall_score / total_checks if total_checks > 0 else 0
print(f"🏆 CHANNEL TECHNICAL SCORE: {final_score:.1f}/100")

if final_score < 100:
    print("\n💡 RECOMMENDATION: Run specific fix scripts for the failing categories.")
else:
    print("\n🎉 PERFECT TECHNICAL ALIGNMENT! Channel is ready for AI Indexing.")
