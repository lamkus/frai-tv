#!/usr/bin/env python3
"""Analysiere Soundies - Status, SEO, YouTube Music Optimierung."""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))

# Soundies finden
soundies = [v for v in data['videos'] if 'soundie' in v['snippet']['title'].lower()]

print("=" * 70)
print("🎵 SOUNDIES ANALYSE")
print("=" * 70)
print(f"\nGefunden: {len(soundies)} Soundies")

# Nach Status
public = [s for s in soundies if s['status']['privacyStatus'] == 'public']
private = [s for s in soundies if s['status']['privacyStatus'] == 'private']

print(f"✅ Public: {len(public)}")
print(f"🔒 Drafts: {len(private)}")

# Analyse der Public Soundies
print("\n" + "=" * 70)
print("📊 PUBLIC SOUNDIES (SEO Check):")
print("=" * 70)

total_views = 0
issues = []

for s in public[:15]:
    title = s['snippet']['title']
    desc = s['snippet'].get('description', '')
    tags = s['snippet'].get('tags', [])
    views = int(s['statistics'].get('viewCount', 0))
    total_views += views
    
    print(f"\n🎵 {title[:65]}")
    print(f"   Views: {views} | Tags: {len(tags)}")
    
    # SEO Checks
    problems = []
    if '8K' not in title and '8k' not in title:
        problems.append("❌ Kein 8K im Titel")
    if '@remAIke' not in title:
        problems.append("❌ Kein @remAIke_IT")
    if len(tags) < 5:
        problems.append(f"❌ Nur {len(tags)} Tags")
    if 'soundie' not in ' '.join(tags).lower():
        problems.append("❌ 'soundie' nicht in Tags")
    if 'jazz' not in ' '.join(tags).lower() and 'swing' not in ' '.join(tags).lower():
        problems.append("⚠️ Kein Genre-Tag (jazz/swing)")
    if len(desc) < 200:
        problems.append(f"⚠️ Kurze Description ({len(desc)} chars)")
    
    if problems:
        for p in problems:
            print(f"   {p}")
        issues.append({'id': s['id'], 'title': title, 'problems': problems})
    else:
        print("   ✅ SEO OK")

print("\n" + "=" * 70)
print("🔒 DRAFT SOUNDIES:")
print("=" * 70)

for s in private[:10]:
    title = s['snippet']['title']
    print(f"  📝 {title[:60]}")

# Zusammenfassung
print("\n" + "=" * 70)
print("📊 ZUSAMMENFASSUNG")
print("=" * 70)
print(f"Total Views (Public): {total_views}")
print(f"Avg Views: {total_views / len(public) if public else 0:.1f}")
print(f"Videos mit SEO-Problemen: {len(issues)}")

# Speichern
result = {
    'total': len(soundies),
    'public': len(public),
    'private': len(private),
    'total_views': total_views,
    'issues': issues,
    'public_videos': [{'id': s['id'], 'title': s['snippet']['title'], 'views': int(s['statistics'].get('viewCount', 0)), 'tags': s['snippet'].get('tags', [])} for s in public],
    'draft_videos': [{'id': s['id'], 'title': s['snippet']['title']} for s in private]
}
Path('config/soundies_analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n💾 Gespeichert: config/soundies_analysis.json")
