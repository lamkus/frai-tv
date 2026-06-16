import json
d = json.load(open('config/vintage_commercials_catalog.json', 'r', encoding='utf-8'))
cats = d['categories']
print(f"Categories: {len(cats)}")
total = 0
for k, v in cats.items():
    n = len(v.get('items', []))
    total += n
    print(f"  {k}: {n} items")
print(f"\nTotal items: {total}")
print(f"\nDownload tiers: {list(d['download_priority'].keys())}")
for tk, tv in d['download_priority'].items():
    if isinstance(tv, dict) and 'items' in tv:
        print(f"  {tk}: {len(tv['items'])} items — {tv.get('note','')[:60]}")
if 'stats' in d:
    print(f"\nStats: {json.dumps(d['stats'], indent=2)}")
