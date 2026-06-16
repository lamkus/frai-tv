#!/usr/bin/env python3
"""Get ALL Wochenschau videos and analyze descriptions."""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth laden
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Bekannte Wochenschau IDs + Suche nach mehr
known_ids = [
    'T-EsdXGhqog',  # Nr. 516 - 86 Views - TOP PERFORMER
    '6K-MuUu6L44',  # Nr. 720
    'jGz1kC1Z69A',  # Nr. 746
    'W-UcQleew8Y',  # Nr. 721
    'w2UvksMOs3c',  # Nr. 750
    'dYBzf5V1TjI',  # Nr. 654
    'H_n_mS-eKps',  # Nr. 754
    '6YLPpJLgVXk',  # Nr. 751
    'iEEvt-s1XhQ',  # Nr. 753
    'bZkUPQHqyfg',  # Nr. 722
    '0sO7jVL43yQ',  # Nr. 652
    '3rB80OGKzrg',  # Nr. 511 (evtl)
]

print("=" * 80)
print("🎬 VOLLSTÄNDIGE WOCHENSCHAU ANALYSE")
print("=" * 80)

# Hole alle Videos
all_videos = []
for vid in known_ids:
    try:
        response = youtube.videos().list(
            part='snippet,statistics,status',
            id=vid
        ).execute()
        
        if response.get('items'):
            all_videos.append(response['items'][0])
    except Exception as e:
        print(f"Error for {vid}: {e}")

# Sortiere nach Views
all_videos.sort(key=lambda x: int(x['statistics'].get('viewCount', 0)), reverse=True)

print(f"\n📊 {len(all_videos)} Wochenschau-Videos gefunden\n")
print("=" * 80)
print("SORTIERT NACH VIEWS:")
print("=" * 80)

for i, v in enumerate(all_videos, 1):
    vid = v['id']
    title = v['snippet']['title']
    views = int(v['statistics'].get('viewCount', 0))
    likes = int(v['statistics'].get('likeCount', 0))
    status = v['status'].get('privacyStatus', '?')
    
    # Determine format
    if title.startswith('Wochenschau Nr.'):
        fmt = "✅ KURZ"
    elif title.startswith('Die Deutsche Wochenschau'):
        fmt = "❌ LANG"
    else:
        fmt = "⚠️ OTHER"
    
    print(f"\n#{i} | {views} Views | {likes} Likes | {fmt} | {status}")
    print(f"   ID: {vid}")
    print(f"   Title: {title}")

# Detailed analysis of TOP performer (Nr. 516)
print("\n" + "=" * 80)
print("🏆 TOP PERFORMER ANALYSE: Nr. 516 (86 Views)")
print("=" * 80)

top = next((v for v in all_videos if v['id'] == 'T-EsdXGhqog'), None)
if top:
    print(f"\n📺 TITEL: {top['snippet']['title']}")
    print(f"📏 Länge: {len(top['snippet']['title'])} Zeichen")
    print(f"\n📝 VOLLSTÄNDIGE DESCRIPTION:\n")
    print("-" * 80)
    print(top['snippet'].get('description', ''))
    print("-" * 80)
    print(f"\n🏷️ TAGS: {top['snippet'].get('tags', [])}")

# Compare with worst performer
print("\n" + "=" * 80)
print("📉 WORST PERFORMER ANALYSE")
print("=" * 80)

worst = all_videos[-1] if all_videos else None
if worst and worst['id'] != 'T-EsdXGhqog':
    print(f"\n📺 TITEL: {worst['snippet']['title']}")
    print(f"📏 Länge: {len(worst['snippet']['title'])} Zeichen")
    print(f"👁️ Views: {worst['statistics'].get('viewCount', 0)}")
    print(f"\n📝 VOLLSTÄNDIGE DESCRIPTION:\n")
    print("-" * 80)
    print(worst['snippet'].get('description', '')[:1500])
    print("-" * 80)

# Save for later
output = {
    'videos': [{
        'id': v['id'],
        'title': v['snippet']['title'],
        'views': int(v['statistics'].get('viewCount', 0)),
        'likes': int(v['statistics'].get('likeCount', 0)),
        'status': v['status'].get('privacyStatus', '?'),
        'description': v['snippet'].get('description', ''),
        'tags': v['snippet'].get('tags', [])
    } for v in all_videos]
}

Path('config/wochenschau_full_analysis.json').write_text(
    json.dumps(output, indent=2, ensure_ascii=False),
    encoding='utf-8'
)
print("\n💾 Gespeichert: config/wochenschau_full_analysis.json")
