"""Analyze new public uploads that need SEO fixing."""
import json

with open('config/live_scan_2026_02_18.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('config/live_scan_2026_02_17.json', 'r', encoding='utf-8') as f:
    old = json.load(f)

old_ids = {v['id'] for v in old['all_videos']}

# New public uploads that need fixing
print("=== NEW PUBLIC UPLOADS NEEDING SEO ===\n")
for v in data['all_videos']:
    if v['id'] not in old_ids and v['privacy'] == 'public':
        print(f"ID: {v['id']}")
        print(f"Title: {v['title']}")
        print(f"Cat: {v.get('categoryId','?')}")
        print(f"Tags ({len(v.get('tags',[]))}): {v.get('tags',[])}") 
        desc = v.get('description','')
        print(f"Desc ({len(desc)} chars):")
        for line in desc.split('\n')[:8]:
            print(f"  {line}")
        print(f"  ... ({len(desc)} total chars)")
        issues = v.get('issues', [])
        if issues:
            print(f"Issues: {issues}")
        print()

# Also show existing public videos with issues
print("=== EXISTING PUBLIC VIDEOS WITH ISSUES ===\n")
for v in data['all_videos']:
    if v['id'] in old_ids and v.get('issues') and v['privacy'] == 'public':
        issues = [i for i in v['issues'] if 'R12' not in i]
        if issues:
            print(f"ID: {v['id']}")
            print(f"Title: {v['title']}")
            for i in issues:
                print(f"  -> {i}")
            print()

# Check for @rem... in titles (broken titles)
print("=== BROKEN TITLES (contains @rem...) ===\n")
for v in data['all_videos']:
    if '@rem' in v.get('title','').lower():
        print(f"  {v['id']}: {v['title']}")

# Check for raw artifacts in titles
print("\n=== RAW ARTIFACTS IN TITLES ===\n")
for v in data['all_videos']:
    title = v.get('title','')
    if any(x in title.lower() for x in ['sls', 'archive', 'cinema', 'xvid', 'aac', '  |']):
        print(f"  [{v['privacy']}] {v['id']}: {v['title']}")
