import json, re, sys, os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
youtube = build('youtube', 'v3', credentials=creds)

with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data.get('public_videos', []) + data.get('private_videos', []) + data.get('unlisted_videos', [])

to_update = []
for v in videos:
    vid = v['id']
    snippet = v.get('snippet', {})
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    
    # We only care about Wochenschau videos
    if 'Wochenschau' not in title:
        continue
    if title.startswith('DUPE'):
        continue
        
    # Standard format has already the number: "Wochenschau 713:"
    title_match = re.search(r'Wochenschau\s+(\d{3,4})', title)
    if title_match:
        continue # Already has number
        
    # Title has no number! E.g. "Wochenschau: Invasion Expected ..."
    # Let's extract from description: "Newsreel Nr. 711" or "Wochenschau Nr. 711" (often in first lines)
    desc_match = re.search(r'(?:Newsreel|Wochenschau)\s+Nr\.?\s*(\d{3,4})', desc, re.IGNORECASE)
    if not desc_match:
        print(f"Skipping {vid}, no number in desc: {title}")
        continue
        
    nr = desc_match.group(1)
    # Replace "Wochenschau:" with "Wochenschau 711:"
    new_title = title.replace("Wochenschau:", f"Wochenschau {nr}:", 1)
    if new_title == title:
        # fallback just in case
        new_title = title.replace("Wochenschau ", f"Wochenschau {nr} ", 1)
        
    to_update.append({"id": vid, "snippet": snippet, "old_title": title, "new_title": new_title})

print(f"Found {len(to_update)} videos needing number injection.")

for u in to_update:
    print(f"[{u['id']}] {u['old_title']} -> {u['new_title']}")
    snippet = u['snippet']
    snippet['title'] = u['new_title']
    snippet['defaultLanguage'] = "de" # important to set default language on update sometimes to avoid API error
    
    try:
        # Keep categoryId because YouTube api sometimes drops it 
        snippet.setdefault('categoryId', '27')

        youtube.videos().update(
            part="snippet",
            body={"id": u['id'], "snippet": snippet}
        ).execute()
        print("  ✅ Updated!")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
