#!/usr/bin/env python3
"""
Quick scan: Check ALL videos (public + private/draft) for naming issues.
Uses OAuth to see private/draft videos too.
Quota: ~4-8 units (videos.list paginiert)
"""
import json, sys, io, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth (sees private + drafts)
creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Fetch ALL videos from uploads playlist
all_videos = []
next_token = None
while True:
    req = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=next_token
    )
    resp = req.execute()
    for item in resp.get('items', []):
        all_videos.append(item['contentDetails']['videoId'])
    next_token = resp.get('nextPageToken')
    if not next_token:
        break

print(f"Total videos in uploads playlist: {len(all_videos)}")

# Now get details for all videos (50 per batch)
detailed = []
for i in range(0, len(all_videos), 50):
    batch = all_videos[i:i+50]
    resp = youtube.videos().list(
        part='snippet,status',
        id=','.join(batch)
    ).execute()
    for v in resp.get('items', []):
        detailed.append({
            'id': v['id'],
            'title': v['snippet']['title'],
            'privacy': v['status']['privacyStatus'],
            'description': v['snippet'].get('description', ''),
            'tags': v['snippet'].get('tags', []),
            'categoryId': v['snippet'].get('categoryId', '?'),
            'publishedAt': v['snippet'].get('publishedAt', ''),
        })

print(f"Detailed info fetched: {len(detailed)} videos\n")

# Sort by publish date descending
detailed.sort(key=lambda x: x['publishedAt'], reverse=True)

# === ANALYSIS ===

# 1. Raw/unformatted titles (artifacts from filename)
RAW_MARKERS = ['sls', 'xvid', 'aac', '_8k_', '_hq', '.mp4', 'archive', 'cinema_']
unnamed = []
for v in detailed:
    t = v['title'].lower()
    if any(m in t for m in RAW_MARKERS):
        unnamed.append(v)

# 2. Very short titles
short_titles = [v for v in detailed if len(v['title']) < 25]

# 3. Missing 8K/4K in title  
no_quality = [v for v in detailed if '8K' not in v['title'] and '8k' not in v['title'] and '4K' not in v['title'] and '4k' not in v['title']]

# 4. Private/Draft videos
drafts = [v for v in detailed if v['privacy'] == 'private']

# 5. Unlisted
unlisted = [v for v in detailed if v['privacy'] == 'unlisted']

# 6. No description or very short
no_desc = [v for v in detailed if len(v['description']) < 50]

# 7. No tags
no_tags = [v for v in detailed if len(v['tags']) < 3]

# 8. Recent uploads (last 30 days) - check if properly named
from datetime import datetime, timedelta, timezone
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
recent = []
for v in detailed:
    try:
        pub = datetime.fromisoformat(v['publishedAt'].replace('Z', '+00:00'))
        if pub >= cutoff:
            recent.append(v)
    except:
        pass

# === PRINT RESULTS ===

print("=" * 80)
print("🔍 VOLLSTÄNDIGER VIDEO-CHECK (AKTUELL)")
print("=" * 80)

print(f"\n📊 ÜBERSICHT:")
print(f"   Total: {len(detailed)}")
print(f"   Public: {len([v for v in detailed if v['privacy'] == 'public'])}")  
print(f"   Private/Draft: {len(drafts)}")
print(f"   Unlisted: {len(unlisted)}")
print(f"   Letzte 30 Tage: {len(recent)}")

if unnamed:
    print(f"\n{'='*80}")
    print(f"🚨 ROHNAMEN / UNFORMATIERTE TITEL ({len(unnamed)} Videos)")
    print(f"{'='*80}")
    for v in unnamed:
        print(f"  [{v['privacy']:8s}] {v['id']}: {v['title']}")
        print(f"             Published: {v['publishedAt'][:10]}")

if short_titles:
    print(f"\n{'='*80}")
    print(f"⚠️ SEHR KURZE TITEL < 25 Zeichen ({len(short_titles)} Videos)")
    print(f"{'='*80}")
    for v in short_titles:
        print(f"  [{v['privacy']:8s}] {v['id']}: {v['title']} ({len(v['title'])} chars)")

if drafts:
    print(f"\n{'='*80}")
    print(f"📝 PRIVATE / DRAFT VIDEOS ({len(drafts)} Videos)")
    print(f"{'='*80}")
    for v in drafts:
        t = v['title']
        issues = []
        if any(m in t.lower() for m in RAW_MARKERS):
            issues.append("ROHNAMEN!")
        if len(t) < 25:
            issues.append("zu kurz")
        if '8K' not in t and '4K' not in t:
            issues.append("kein 8K/4K")
        if len(v['description']) < 50:
            issues.append("keine Beschreibung")
        if len(v['tags']) < 3:
            issues.append("wenige Tags")
        
        status = "✅" if not issues else "❌ " + ", ".join(issues)
        print(f"  {v['id']}: {t}")
        print(f"    {status}")
        print(f"    https://studio.youtube.com/video/{v['id']}/edit")

if recent:
    print(f"\n{'='*80}")
    print(f"🆕 LETZTE 30 TAGE - NEUE UPLOADS ({len(recent)} Videos)")
    print(f"{'='*80}")
    for v in recent:
        t = v['title']
        issues = []
        if any(m in t.lower() for m in RAW_MARKERS):
            issues.append("ROHNAMEN!")
        if len(t) < 25:
            issues.append("zu kurz")
        if '8K' not in t and '4K' not in t:
            issues.append("kein 8K/4K")
        if len(v['description']) < 100:
            issues.append("Desc zu kurz")
        if len(v['tags']) < 5:
            issues.append(f"nur {len(v['tags'])} Tags")
        if 'www.remaike.IT' not in v['description'] and 'remaike.IT' not in v['description']:
            issues.append("kein remaike.IT Link")
        
        status = "✅ OK" if not issues else "❌ " + ", ".join(issues)
        print(f"  [{v['privacy']:8s}] {v['publishedAt'][:10]} | {v['id']}: {t}")
        print(f"    {status}")

if no_quality:
    print(f"\n{'='*80}")
    print(f"⚠️ KEIN 8K/4K IM TITEL ({len(no_quality)} Videos)")
    print(f"{'='*80}")
    for v in no_quality[:20]:
        print(f"  [{v['privacy']:8s}] {v['id']}: {v['title']}")
    if len(no_quality) > 20:
        print(f"  ... und {len(no_quality)-20} weitere")

# Save results
results = {
    'scan_date': datetime.now(timezone.utc).isoformat(),
    'total': len(detailed),
    'public': len([v for v in detailed if v['privacy'] == 'public']),
    'private': len(drafts),
    'unlisted': len(unlisted),
    'raw_names': len(unnamed),
    'short_titles': len(short_titles),
    'no_quality_tag': len(no_quality),
    'recent_30d': len(recent),
    'all_videos': detailed
}
with open('config/video_check_2026_03_02.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n💾 Ergebnisse gespeichert: config/video_check_2026_03_02.json")
print(f"\n📊 Quota-Verbrauch: ~{(len(all_videos)//50 + 1) + (len(all_videos)//50 + 1)} Units (playlistItems.list + videos.list)")
