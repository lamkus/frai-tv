import json, sys

data = json.load(open('D:/remaike.TV/config/comprehensive_audit_2026_02_06.json', 'r', encoding='utf-8'))

# Navigate structure
videos = data.get('videos', data.get('results', []))
if not videos and isinstance(data, dict):
    # Try nested
    for k, v in data.items():
        if isinstance(v, list) and len(v) > 10:
            videos = v
            break

print(f"Total videos in audit: {len(videos)}")
print(f"Keys in first entry: {list(videos[0].keys()) if videos else 'N/A'}")
print()

long_titles = []
for v in videos:
    title = v.get('title', '')
    vid = v.get('video_id', v.get('id', ''))
    if len(title) > 70:
        long_titles.append({'id': vid, 'title': title, 'len': len(title)})

print(f"Found {len(long_titles)} titles > 70 chars:")
for t in long_titles:
    print(f"  [{t['len']}] {t['id']}")
    print(f"         {t['title']}")
