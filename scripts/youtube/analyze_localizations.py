#!/usr/bin/env python3
"""Analyze localization status results to identify issues and plan next steps."""

import json
from collections import Counter

with open('config/localization_status_2026_02_06.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data['videos_with_localizations']

# Deduplicate by ID (script may have output dupes)
seen = set()
unique_videos = []
for v in videos:
    if v['id'] not in seen:
        seen.add(v['id'])
        unique_videos.append(v)

print(f"=== LOCALIZATION ANALYSIS ===")
print(f"Total entries: {len(videos)}, Unique videos: {len(unique_videos)}")

# Count videos with ONLY self-language (= no REAL multi-language localizations)
only_self = 0
multi = 0
mismatched_single = []

for v in unique_videos:
    langs = v['localization_langs']
    dl = v['defaultLanguage']
    
    if len(langs) == 1 and langs[0] == dl:
        only_self += 1
    elif len(langs) == 1 and langs[0] != dl:
        mismatched_single.append(v)
    else:
        multi += 1

print(f"\nOnly self-language (NO real localizations): {only_self}")
print(f"Has multilingual localizations (>1 lang):   {multi}")
print(f"Mismatched single lang:                     {len(mismatched_single)}")

# defaultLanguage distribution
lang_counts = Counter(v['defaultLanguage'] for v in unique_videos)
print(f"\ndefaultLanguage distribution:")
for lang, count in lang_counts.most_common():
    print(f"  {lang}: {count}")

# Identify potentially WRONG defaultLanguage
wrong_default = []
for v in unique_videos:
    title = v.get('title', '')
    dl = v['defaultLanguage']
    
    # Soundies should be EN (English music videos)
    if 'Soundie' in title and dl != 'en':
        wrong_default.append(('Soundie→should be en', dl, v['id'], title[:70]))
    
    # English-titled content in DE  
    elif dl == 'de' and all(c.isascii() or c in '–—|:()' for c in title):
        # Check if title looks English
        english_markers = ['the ', 'of ', ' a ', ' an ', ' in ', ' on ', 'and ']
        title_lower = title.lower()
        if any(m in title_lower for m in english_markers) and 'Wochenschau' not in title and 'Alfred' not in title and 'Maulwurf' not in title and 'Betty Boop' not in title and 'Astro Boy' not in title:
            wrong_default.append(('EN content in DE?', dl, v['id'], title[:70]))
    
    # Vietnamese/Korean - likely wrong
    elif dl == 'vi':
        wrong_default.append(('Vietnamese?!', dl, v['id'], title[:70]))
    elif dl == 'ko':
        wrong_default.append(('Korean?!', dl, v['id'], title[:70]))

print(f"\n=== POTENTIALLY WRONG defaultLanguage: {len(wrong_default)} ===")
for cat, dl, vid, title in wrong_default:
    print(f"  [{dl}] {cat}: {vid} | {title}")

# Summary for next steps
print(f"\n=== SUMMARY ===")
print(f"✅ defaultLanguage is SET on ALL {len(unique_videos)} videos (was the main blocker before)")
print(f"❌ Only {multi} videos have real multilingual localizations")
print(f"❌ {only_self} videos have ONLY self-language (=useless)")
print(f"⚠️  {len(wrong_default)} videos may have WRONG defaultLanguage")
print(f"\n💡 NEXT STEP: Add localizations (EN, ES, FR, PT, HI) to all {len(unique_videos)} videos")
print(f"   Cost: ~50 quota per video × {len(unique_videos)} = {50 * len(unique_videos)} quota units")
print(f"   = {50 * len(unique_videos) / 10000:.1f} days at 10K quota/day")
