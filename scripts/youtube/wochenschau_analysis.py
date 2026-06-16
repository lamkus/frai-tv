"""Wochenschau Deep Analysis: Why do ALL 47 public videos have 0 views?"""
import json, os, sys

# Load latest scan
with open('config/live_scan_2026_02_18.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

# Get all Wochenschau videos
wochenschau = []
for v in scan['all_videos']:
    title = v.get('title', '')
    if 'wochenschau' in title.lower() or 'newsreel' in title.lower():
        wochenschau.append(v)
    elif v.get('categoryId') == '27':
        # Check if it's in the Wochenschau category
        desc = v.get('description', '')
        if 'wochenschau' in desc.lower() or 'newsreel' in desc.lower():
            wochenschau.append(v)

print(f"=== WOCHENSCHAU DEEP ANALYSIS ===")
print(f"Total Wochenschau videos: {len(wochenschau)}")
print()

# Separate by status
public = [v for v in wochenschau if v.get('privacy') == 'public']
private = [v for v in wochenschau if v.get('privacy') == 'private']
unlisted = [v for v in wochenschau if v.get('privacy') == 'unlisted']

print(f"Public: {len(public)} | Private: {len(private)} | Unlisted: {len(unlisted)}")
print()

# Analyze views
views = [int(v.get('views', 0)) for v in public]
zero_views = sum(1 for x in views if x == 0)
print(f"Views distribution:")
print(f"  0 views: {zero_views}/{len(public)}")
print(f"  >0 views: {len(public) - zero_views}/{len(public)}")
if views:
    print(f"  Total views: {sum(views)}")
    print(f"  Max views: {max(views)}")
    print(f"  Average: {sum(views)/len(views):.1f}")
print()

# Analyze titles
print("=== TITLE ANALYSIS ===")
for v in sorted(public, key=lambda x: x.get('title', '')):
    t = v['title']
    views_count = v.get('views', 0)
    pub_date = v.get('publishedAt', '')[:10]
    print(f"  [{views_count:>5} views] [{pub_date}] {t[:80]}")
print()

# Analyze title patterns
print("=== TITLE PATTERN ISSUES ===")
issues = {
    'no_8k_hq': 0,
    'no_4k_uhd': 0,
    'too_long': 0,
    'has_handle': 0,
    'no_year_date': 0,
    'has_nr': 0,
    'generic_event': 0,
}
for v in public:
    t = v['title']
    if '8K HQ' not in t:
        issues['no_8k_hq'] += 1
    if '4K UHD' not in t:
        issues['no_4k_uhd'] += 1
    if len(t) > 70:
        issues['too_long'] += 1
    if '@rem' in t:
        issues['has_handle'] += 1
    if not any(c.isdigit() for c in t.split('|')[0] if c != '/'):
        issues['no_year_date'] += 1
    if 'Nr.' in t or 'Nr ' in t:
        issues['has_nr'] += 1

for k, cnt in issues.items():
    if cnt > 0:
        print(f"  {k}: {cnt}/{len(public)}")
print()

# Tag analysis
print("=== TAG ANALYSIS ===")
all_tags = {}
for v in public:
    for tag in v.get('tags', []):
        tl = tag.lower()
        all_tags[tl] = all_tags.get(tl, 0) + 1

print(f"  Total unique tags: {len(all_tags)}")
print(f"  Top 20 tags:")
for tag, cnt in sorted(all_tags.items(), key=lambda x: -x[1])[:20]:
    print(f"    {cnt:>3}x {tag}")
print()

# Description analysis
print("=== DESCRIPTION ANALYSIS ===")
desc_issues = {
    'no_cta': 0,
    'no_remaike_link': 0,
    'no_youtube_link': 0,
    'no_chapters': 0,
    'too_short': 0,
    'has_disclaimer': 0,
    'has_hashtags': 0,
    'has_multilingual': 0,
}
for v in public:
    d = v.get('description', '')
    if 'SUBSCRIBE' not in d.upper() and 'LIKE' not in d.upper():
        desc_issues['no_cta'] += 1
    if 'remaike.it' not in d.lower() and 'remaike.IT' not in d:
        desc_issues['no_remaike_link'] += 1
    if '@remAIke_IT' not in d and 'youtube.com/@remAIke' not in d:
        desc_issues['no_youtube_link'] += 1
    if '0:00' not in d:
        desc_issues['no_chapters'] += 1
    if len(d) < 200:
        desc_issues['too_short'] += 1
    if 'disclaimer' in d.lower() or 'historisches dokument' in d.lower() or 'historical document' in d.lower():
        desc_issues['has_disclaimer'] += 1
    if '#' in d:
        desc_issues['has_hashtags'] += 1
    if any(x in d.lower() for x in ['segunda guerra', 'perang dunia', 'world war']):
        desc_issues['has_multilingual'] += 1

for k, cnt in desc_issues.items():
    print(f"  {k}: {cnt}/{len(public)}")
print()

# Upload date analysis
print("=== UPLOAD DATE ANALYSIS ===")
dates = {}
for v in public:
    d = v.get('publishedAt', '')[:10]
    dates[d] = dates.get(d, 0) + 1
for d in sorted(dates.keys()):
    print(f"  {d}: {dates[d]} videos")
print()

# Category check
print("=== CATEGORY CHECK ===")
cats = {}
for v in public:
    c = v.get('categoryId', '?')
    cats[c] = cats.get(c, 0) + 1
for c, cnt in cats.items():
    cat_name = {'27': 'Education', '1': 'Film', '10': 'Music', '25': 'News'}.get(c, c)
    print(f"  Category {c} ({cat_name}): {cnt}")
print()

# Sample full description
print("=== SAMPLE DESCRIPTION (first public) ===")
if public:
    sample = public[0]
    print(f"Title: {sample['title']}")
    print(f"Desc ({len(sample.get('description',''))} chars):")
    print(sample.get('description', '')[:1000])
    print()
    print(f"Tags: {sample.get('tags', [])}")

# Compare with best performing content
print("\n=== TOP 10 PERFORMING VIDEOS (Channel-wide) ===")
all_pub = [v for v in scan['all_videos'] if v.get('privacy') == 'public']
by_views = sorted(all_pub, key=lambda x: int(x.get('views', 0)), reverse=True)
for v in by_views[:10]:
    print(f"  [{int(v.get('views', 0)):>6} views] {v['title'][:70]}")
