"""Fetch REAL view counts for all public videos using statistics part."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from mega_fix import get_youtube_service

yt = get_youtube_service()

# Load scan for video IDs
with open('config/live_scan_2026_02_18.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

public = [v for v in scan['all_videos'] if v.get('privacy') in ('public', 'unlisted')]
all_ids = list(set(v['id'] for v in public))

print(f"Fetching statistics for {len(all_ids)} public videos...\n")

stats = {}
for batch_start in range(0, len(all_ids), 50):
    batch = all_ids[batch_start:batch_start+50]
    resp = yt.videos().list(
        part='statistics,snippet',
        id=','.join(batch)
    ).execute()
    for item in resp.get('items', []):
        vid = item['id']
        s = item.get('statistics', {})
        stats[vid] = {
            'title': item['snippet']['title'],
            'views': int(s.get('viewCount', 0)),
            'likes': int(s.get('likeCount', 0)),
            'comments': int(s.get('commentCount', 0)),
            'published': item['snippet']['publishedAt'][:10],
        }

# Show ALL videos sorted by views
by_views = sorted(stats.items(), key=lambda x: -x[1]['views'])

print("=== TOP 30 BY VIEWS ===")
for vid, s in by_views[:30]:
    print(f"  [{s['views']:>6}v {s['likes']:>3}L] [{s['published']}] {s['title'][:65]}")

print(f"\n=== BOTTOM 30 BY VIEWS ===")
for vid, s in by_views[-30:]:
    print(f"  [{s['views']:>6}v {s['likes']:>3}L] [{s['published']}] {s['title'][:65]}")

# Wochenschau specific
print(f"\n=== WOCHENSCHAU VIDEOS ===")
wochenschau = [(vid, s) for vid, s in stats.items() 
               if 'wochenschau' in s['title'].lower() or 'newsreel' in s['title'].lower()]
wochenschau.sort(key=lambda x: -x[1]['views'])

total_ws_views = sum(s['views'] for _, s in wochenschau)
total_ws_likes = sum(s['likes'] for _, s in wochenschau)
zero_ws = sum(1 for _, s in wochenschau if s['views'] == 0)

print(f"Total: {len(wochenschau)} videos")
print(f"Total views: {total_ws_views}")
print(f"Total likes: {total_ws_likes}")
print(f"0-view videos: {zero_ws}/{len(wochenschau)}")
print()

for vid, s in wochenschau:
    print(f"  [{s['views']:>6}v {s['likes']:>3}L] [{s['published']}] {s['title'][:65]}")

# Category comparison
print(f"\n=== VIEWS BY CATEGORY ===")
categories = {}
for vid, s in stats.items():
    t = s['title'].lower()
    if 'wochenschau' in t or 'newsreel' in t:
        cat = 'Wochenschau'
    elif 'betty boop' in t:
        cat = 'Betty Boop'
    elif 'alfred' in t and 'kwak' in t:
        cat = 'Alfred J. Kwak'
    elif 'soundie' in t:
        cat = 'Soundies'
    elif 'superman' in t or 'fleischer' in t:
        cat = 'Superman/Fleischer'
    elif 'felix' in t:
        cat = 'Felix the Cat'
    elif 'ken block' in t or 'gymkhana' in t:
        cat = 'Ken Block'
    elif 'casper' in t:
        cat = 'Casper'
    elif 'looney' in t or 'warner' in t:
        cat = 'Looney Tunes'
    elif 'bravestarr' in t:
        cat = 'BraveStarr'
    elif 'krtek' in t or 'maulwurf' in t:
        cat = 'Krtek'
    elif '7. sinn' in t or 'siebte sinn' in t:
        cat = 'Der 7. Sinn'
    else:
        cat = 'Other'
    
    if cat not in categories:
        categories[cat] = {'count': 0, 'views': 0, 'likes': 0}
    categories[cat]['count'] += 1
    categories[cat]['views'] += s['views']
    categories[cat]['likes'] += s['likes']

for cat in sorted(categories.keys(), key=lambda x: -categories[x]['views']):
    c = categories[cat]
    avg = c['views'] / c['count'] if c['count'] > 0 else 0
    print(f"  {cat:20s}: {c['count']:>3} vids, {c['views']:>7} views (avg {avg:>6.0f})")

# Save stats
out = {'date': '2026-02-18', 'total_videos': len(stats), 'stats': stats}
with open('config/video_stats_2026_02_18.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\nSaved to config/video_stats_2026_02_18.json")
