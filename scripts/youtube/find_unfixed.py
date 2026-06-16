"""Find all unfixed new uploads in the latest channel scan"""
import json

with open('config/channel_scan_2026_02_13.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data.get('all', [])
raw_vids = data.get('raw', [])
print(f"Total videos: {data['total']}")
print(f"Raw flagged: {len(raw_vids)}")

# Check structure
if videos:
    v0 = videos[0]
    if isinstance(v0, dict):
        print(f"Video keys: {list(v0.keys())[:8]}")

# Find ALL unfixed videos (raw filenames, no SEO)
unfixed = []
for v in videos:
    if isinstance(v, dict):
        title = v.get('title', v.get('snippet', {}).get('title', ''))
        vid = v.get('id', v.get('video_id', '?'))
        priv = v.get('privacy', v.get('status', {}).get('privacyStatus', '?'))
        tags = v.get('tags', v.get('tags_count', '?'))
        desc = v.get('description', v.get('desc_length', '?'))
        cat = v.get('category', v.get('categoryId', '?'))
    else:
        continue
    
    # Detect raw filename titles
    raw_indicators = ['sls', 'archive protected', 'archive blurred', '_sls', 'aac sls',
                     'bvawxwvg', 'xvid', 'h264', 'x264', '.mp4', '.mov', '.mkv']
    is_raw = any(x in title.lower() for x in raw_indicators)
    
    # Also detect if missing SEO basics
    no_8k = '8K' not in title and '4K' not in title
    no_pipe = '|' not in title
    
    if is_raw or (no_8k and no_pipe and len(title) > 10):
        unfixed.append({
            'id': vid,
            'title': title,
            'privacy': priv,
            'is_raw': is_raw,
            'no_seo': no_8k and no_pipe,
            'tags': tags,
            'cat': cat
        })

# Sort: raw first, then no-SEO
unfixed.sort(key=lambda x: (not x['is_raw'], x['title']))

print(f"\n{'='*100}")
print(f"UNFIXED VIDEOS: {len(unfixed)}")
print(f"{'='*100}")
print(f"{'RAW':4} {'SEO':4} {'PRIV':8} {'CAT':4} {'ID':13} TITLE")
print(f"{'-'*100}")
for u in unfixed:
    raw_flag = 'RAW' if u['is_raw'] else '   '
    seo_flag = 'noSEO' if u['no_seo'] else '     '
    print(f"{raw_flag:4} {seo_flag:5} {str(u['privacy']):8} {str(u['cat']):4} {u['id']:13} {u['title'][:70]}")

# Also show the pre-flagged raw ones
if raw_vids:
    print(f"\n{'='*100}")
    print(f"PRE-FLAGGED RAW (from scan): {len(raw_vids)}")
    print(f"{'='*100}")
    for r in raw_vids:
        if isinstance(r, dict):
            vid = r.get('id', r.get('video_id', '?'))
            title = r.get('title', r.get('snippet', {}).get('title', '?'))
            print(f"  {vid}: {title[:80]}")
        elif isinstance(r, str):
            print(f"  {r}")
