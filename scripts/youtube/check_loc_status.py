import json

data = json.load(open('D:/remaike.TV/config/localization_status_2026_02_06.json', 'r', encoding='utf-8'))
vids = data.get('videos_with_localizations', [])

# Sample 5
for v in vids[:5]:
    vid = v.get('id', '?')
    langs = v.get('languages', [])
    print(f"  {vid} | langs: {langs}")

# Count language frequency
from collections import Counter
lang_counts = Counter()
for v in vids:
    for l in v.get('languages', []):
        lang_counts[l] += 1

print(f"\nLanguage frequency across {len(vids)} videos:")
for lang, count in lang_counts.most_common(20):
    print(f"  {lang}: {count}")
