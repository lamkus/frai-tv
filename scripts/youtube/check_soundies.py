#!/usr/bin/env python3
"""Check current Soundie titles."""
import json

data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))
soundies = [v for v in data['videos'] if 'soundie' in v['snippet']['title'].lower()]

print(f"🎵 Soundies gefunden: {len(soundies)}")
print("=" * 70)

# Count formats
old_format = 0  # "Soundie:" at start
new_format = 0  # Song title first

for v in soundies:
    title = v['snippet']['title']
    video_id = v['id']
    if title.lower().startswith('soundie:') or title.lower().startswith('soundie -'):
        old_format += 1
        print(f"❌ OLD: {title[:65]}")
    else:
        new_format += 1
        print(f"✅ NEW: {title[:65]}")

print()
print("=" * 70)
print(f"❌ Altes Format (Soundie: am Anfang): {old_format}")
print(f"✅ Neues Format (Song zuerst): {new_format}")
