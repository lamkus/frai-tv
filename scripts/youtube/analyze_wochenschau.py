#!/usr/bin/env python3
"""Analyze all Wochenschau videos in detail."""
import json

data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))

# Find all Wochenschau videos
wochenschau = []
for v in data['videos']:
    title = v['snippet']['title'].lower()
    if 'wochenschau' in title:
        wochenschau.append(v)

print("=" * 80)
print("🎬 WOCHENSCHAU ANALYSE - STEP BY STEP")
print("=" * 80)
print(f"Gefunden: {len(wochenschau)} Videos\n")

# Analyze each one
for i, v in enumerate(wochenschau, 1):
    title = v['snippet']['title']
    vid = v['id']
    desc = v['snippet'].get('description', '')[:200]
    tags = v['snippet'].get('tags', [])
    status = v.get('status', {}).get('privacyStatus', 'unknown')
    
    print(f"{'='*80}")
    print(f"[{i}/{len(wochenschau)}] VIDEO ID: {vid}")
    print(f"{'='*80}")
    print(f"📺 TITEL: {title}")
    print(f"📏 Länge: {len(title)} Zeichen")
    print(f"🔒 Status: {status}")
    print()
    
    # Analyze format
    if title.startswith('Die Deutsche Wochenschau'):
        print("❌ FORMAT: LANG (Die Deutsche Wochenschau Nr. XXX)")
        print("   → Sollte sein: Wochenschau Nr. XXX (YYYY) | 8K HQ | @remAIke_IT")
    elif title.startswith('Wochenschau Nr.'):
        print("✅ FORMAT: KURZ (Wochenschau Nr. XXX)")
    else:
        print("⚠️ FORMAT: UNBEKANNT")
    
    print()
    print(f"📝 DESCRIPTION (erste 200 Zeichen):")
    print(f"   {desc}...")
    print()
    print(f"🏷️ TAGS ({len(tags)}): {', '.join(tags[:10])}{'...' if len(tags) > 10 else ''}")
    print()

# Summary
print("=" * 80)
print("📊 ZUSAMMENFASSUNG")
print("=" * 80)

lang_format = [v for v in wochenschau if v['snippet']['title'].startswith('Die Deutsche')]
kurz_format = [v for v in wochenschau if v['snippet']['title'].startswith('Wochenschau Nr.')]

print(f"❌ Langes Format: {len(lang_format)} Videos")
for v in lang_format:
    print(f"   - {v['id']}: {v['snippet']['title'][:50]}...")

print()
print(f"✅ Kurzes Format: {len(kurz_format)} Videos")
for v in kurz_format:
    print(f"   - {v['id']}: {v['snippet']['title'][:50]}...")
