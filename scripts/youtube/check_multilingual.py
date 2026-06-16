"""
Check ALL public videos for multilingual descriptions
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Get ALL videos from uploads playlist
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
all_items = []
next_page = None

print("Fetching all videos...")
while True:
    response = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=next_page
    ).execute()
    all_items.extend(response.get('items', []))
    next_page = response.get('nextPageToken')
    if not next_page:
        break

video_ids = [item['contentDetails']['videoId'] for item in all_items]
public_videos = []

print(f"Checking {len(video_ids)} videos for details...")
for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    vids = youtube.videos().list(
        part='snippet,status',
        id=','.join(batch)
    ).execute()
    for v in vids.get('items', []):
        if v['status']['privacyStatus'] == 'public':
            public_videos.append(v)

print(f"\n=== {len(public_videos)} PUBLIC VIDEOS - MULTILINGUAL CHECK ===\n")

# Check for multilingual content markers
lang_markers = [
    'ENGLISH', 'DEUTSCH', 'ESPAÑOL', 'FRANÇAIS', 'PORTUGUÊS', 'ITALIANO', 
    'РУССКИЙ', '日本語', '中文', '한국어', 'TÜRKÇE', 'العربية', 'हिंदी',
    '🇺🇸', '🇬🇧', '🇩🇪', '🇪🇸', '🇫🇷', '🇵🇹', '🇮🇹', '🇷🇺', '🇯🇵', '🇨🇳', '🇰🇷',
    'NEDERLANDS', 'POLSKI', 'SVENSKA', 'TIẾNG VIỆT', 'BAHASA', 'ไทย'
]

no_multilingual = []
has_multilingual = []

for v in public_videos:
    desc = v['snippet']['description']
    
    # Count unique language markers
    lang_count = sum(1 for marker in lang_markers if marker in desc)
    
    video_info = {
        'id': v['id'],
        'title': v['snippet']['title'],
        'langs': lang_count,
        'desc_len': len(desc)
    }
    
    if lang_count >= 5:
        has_multilingual.append(video_info)
    else:
        no_multilingual.append(video_info)

print(f"✅ Mit Multilingual (5+ Sprachen): {len(has_multilingual)}")
print(f"❌ OHNE Multilingual: {len(no_multilingual)}")
print()
print("=== VIDEOS OHNE MULTILINGUAL ===")
for v in no_multilingual:
    print(f"{v['id']} | {v['langs']} langs | {v['desc_len']:4d} chars | {v['title'][:50]}")

# Save to JSON
result = {
    'total_public': len(public_videos),
    'with_multilingual': len(has_multilingual),
    'without_multilingual': len(no_multilingual),
    'videos_needing_update': no_multilingual
}

with open('config/multilingual_check.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n📁 Details saved to config/multilingual_check.json")
