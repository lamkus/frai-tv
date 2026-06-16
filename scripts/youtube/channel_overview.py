"""Channel status overview from offline scan data"""
import json

with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data['videos']
print(f"Total Videos im Scan: {len(videos)}")

# Count by status
public = [v for v in videos if v.get('status', {}).get('privacyStatus', '') == 'public']
private = [v for v in videos if v.get('status', {}).get('privacyStatus', '') == 'private']
unlisted = [v for v in videos if v.get('status', {}).get('privacyStatus', '') == 'unlisted']
print(f"Public: {len(public)} | Private: {len(private)} | Unlisted: {len(unlisted)}")

# Check soundies
soundies = [v for v in videos if 'soundie' in v['snippet']['title'].lower()]
print(f"\nSoundies: {len(soundies)}")

# DUPEs check
dupe_ids = ['QRNAv0GKymk', 'R9dz4YGCy5E', 'SV7o2XaYZyc', 'LjGFowS8qHI',
            'LCa6Klpi8ts', 'ULzsDOb2x3U', 'sGZg6lIHFh8', 'iFSHNS7kVgQ']
found_dupes = [v for v in videos if v['id'] in dupe_ids]
print(f"\nDUPEs noch im Scan: {len(found_dupes)} von {len(dupe_ids)}")
for d in found_dupes:
    vid = d['id']
    title = d['snippet']['title'][:60]
    priv = d.get('status', {}).get('privacyStatus', '?')
    print(f"  - {vid}: {title} ({priv})")

# Categories check
cats = {}
for v in public:
    cat = v['snippet'].get('categoryId', '?')
    cats[cat] = cats.get(cat, 0) + 1
print(f"\nCategories: {dict(sorted(cats.items(), key=lambda x: -x[1]))}")

# Videos since last session (Feb 12)
from datetime import datetime
recent = []
for v in videos:
    pub = v['snippet'].get('publishedAt', '')
    if pub > '2026-02-12':
        recent.append(v)
if recent:
    print(f"\nNeue Videos seit 12.02.: {len(recent)}")
    for r in sorted(recent, key=lambda x: x['snippet']['publishedAt']):
        title = r['snippet']['title'][:60]
        pub = r['snippet']['publishedAt'][:10]
        print(f"  - [{pub}] {title}")
else:
    print("\nKeine neuen Videos seit 12.02. im Scan (Scan vom 05.02.)")
    
# Scan age
scan_date = data.get('scan_date', data.get('scanned_at', 'unknown'))
print(f"\nScan-Datum: {scan_date}")
print("ACHTUNG: Scan ist veraltet! Frischer Scan braucht API Key.")
