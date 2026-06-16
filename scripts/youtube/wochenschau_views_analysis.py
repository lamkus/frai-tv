#!/usr/bin/env python3
"""Analyze Wochenschau videos by views to find winning format."""
import json

data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))

# Find all Wochenschau videos with stats
wochenschau = []
for v in data['videos']:
    title = v['snippet']['title'].lower()
    if 'wochenschau' in title:
        stats = v.get('statistics', {})
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        wochenschau.append({
            'id': v['id'],
            'title': v['snippet']['title'],
            'views': views,
            'likes': likes,
            'status': v.get('status', {}).get('privacyStatus', 'unknown'),
            'description': v['snippet'].get('description', '')
        })

# Sort by views
wochenschau.sort(key=lambda x: x['views'], reverse=True)

print("=" * 80)
print("🎬 WOCHENSCHAU - SORTIERT NACH VIEWS")
print("=" * 80)
print()

for i, v in enumerate(wochenschau, 1):
    title = v['title']
    views = v['views']
    likes = v['likes']
    
    # Determine format
    if title.startswith('Die Deutsche Wochenschau'):
        fmt = "❌ LANG"
    elif title.startswith('Wochenschau Nr.'):
        fmt = "✅ KURZ"
    else:
        fmt = "⚠️ OTHER"
    
    print(f"#{i} | {views:,} Views | {likes} Likes | {fmt}")
    print(f"   {title}")
    print()

# Analysis
print("=" * 80)
print("📊 FORMAT-ANALYSE")
print("=" * 80)

lang = [v for v in wochenschau if v['title'].startswith('Die Deutsche')]
kurz = [v for v in wochenschau if v['title'].startswith('Wochenschau Nr.')]

lang_views = sum(v['views'] for v in lang)
kurz_views = sum(v['views'] for v in kurz)

lang_avg = lang_views / len(lang) if lang else 0
kurz_avg = kurz_views / len(kurz) if kurz else 0

print(f"\n❌ LANGES FORMAT ({len(lang)} Videos):")
print(f"   Total Views: {lang_views:,}")
print(f"   Durchschnitt: {lang_avg:,.0f} Views/Video")

print(f"\n✅ KURZES FORMAT ({len(kurz)} Videos):")
print(f"   Total Views: {kurz_views:,}")
print(f"   Durchschnitt: {kurz_avg:,.0f} Views/Video")

print()
if kurz_avg > lang_avg:
    print(f"🏆 GEWINNER: KURZES FORMAT (+{kurz_avg - lang_avg:,.0f} Views/Video)")
else:
    print(f"🏆 GEWINNER: LANGES FORMAT (+{lang_avg - kurz_avg:,.0f} Views/Video)")

# Show best performer structure
print()
print("=" * 80)
print("🏆 TOP PERFORMER - VOLLE STRUKTUR")
print("=" * 80)
best = wochenschau[0]
print(f"\nTITEL: {best['title']}")
print(f"VIEWS: {best['views']:,}")
print(f"\nDESCRIPTION:")
print("-" * 40)
print(best['description'][:2000])
