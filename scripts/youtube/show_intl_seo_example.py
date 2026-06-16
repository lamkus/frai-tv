#!/usr/bin/env python3
"""Show international SEO example for Wochenschau"""

import sys
sys.path.insert(0, '.')
from scripts.youtube.wochenschau_complete_seo_update import build_description, build_tags, WOCHENSCHAU_DATA

# Battle of Britain (516) - most internationally searched
nr = 516
data = WOCHENSCHAU_DATA[nr]

print("=" * 70)
print(f"WOCHENSCHAU {nr}: {data['event_en']}")
print("=" * 70)
print()

print("📝 NEW TITLE:")
title = f"Wochenschau {nr}: {data['event_en']} ({data['date']}) | 8K | @remAIke_IT"
print(f"   {title}")
print(f"   Length: {len(title)} chars (max 70)")
print()

print("🏷️ TAGS (mit internationalen Keywords):")
tags = build_tags(nr, data)
for i, tag in enumerate(tags):
    lang = "EN" if i < 4 else ("INTL" if i >= 8 else "DE")
    print(f"   {i+1:2}. [{lang}] {tag}")
print()

print("📄 DESCRIPTION (erste 160 chars = in YouTube Search sichtbar!):")
print("-" * 70)
desc = build_description(nr, data)
lines = desc.split('\n')
for line in lines[:15]:
    print(line)
print("...")
print("-" * 70)

print()
print("🌍 INTERNATIONALE REICHWEITE:")
print("   🇪🇸 Spanisch: 'Segunda Guerra Mundial' im Text")
print("   🇯🇵 Japanisch: '第二次世界大戦' im Text")  
print("   🇧🇷 Portugiesisch: 'Segunda Guerra' im Text")
print("   🇷🇺 Russisch: Tags wie 'Битва за Британию'")
print("   🇮🇳 Hindi: Tags wie 'ब्रिटेन की लड़ाई'")
print()
print("→ Inder/Japaner/Brasilianer finden Videos über IHRE Suchbegriffe!")
