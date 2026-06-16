"""Quick scan: find newest uploads and check if they need fixing."""
import os, json, sys

# Use OAuth (works for both reads and writes)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = r"D:\remaike.TV\token.json"
CLIENT_SECRET = r"D:\remaike.TV\config\client_secret.json"
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

yt = get_youtube()

# Step 1: Get channel stats
ch = yt.channels().list(part='statistics', id=CHANNEL_ID).execute()
stats = ch['items'][0]['statistics']
print(f"Channel: {stats['subscriberCount']} subs, {stats['videoCount']} videos")

# Step 2: Fetch ALL videos from upload playlist (1 unit per page)
all_vids = []
page_token = None
pages = 0
while True:
    pages += 1
    req = yt.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=UPLOAD_PLAYLIST,
        maxResults=50,
        pageToken=page_token
    )
    resp = req.execute()
    for it in resp.get('items', []):
        vid_id = it['contentDetails']['videoId']
        pub = it['contentDetails'].get('videoPublishedAt', it['snippet'].get('publishedAt', ''))
        title = it['snippet'].get('title', '???')
        status = it['snippet'].get('status', {})
        all_vids.append({'id': vid_id, 'published': pub, 'title': title})
    page_token = resp.get('nextPageToken')
    if not page_token:
        break

print(f"\nFetched {len(all_vids)} videos ({pages} pages, ~{pages+1} quota)")

# Step 3: Load known IDs from our DB
import sqlite3
db_path = r'D:\remaike.TV\tools\channel_manager\channel_manager.db'
known_ids = set()
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id FROM videos").fetchall()
    known_ids = {r[0] for r in rows}
    conn.close()
print(f"Known video IDs in DB: {len(known_ids)}")

# Step 4: Find NEW videos
new_vids = [v for v in all_vids if v['id'] not in known_ids]
print(f"\n{'='*60}")
print(f"NEW videos (not in DB): {len(new_vids)}")
for v in sorted(new_vids, key=lambda x: x['published'], reverse=True):
    print(f"  NEW: {v['id']} | {v['published'][:10]} | {v['title'][:65]}")

# Step 5: Show newest 20 videos regardless
print(f"\n{'='*60}")
print(f"NEWEST 20 videos on channel:")
sorted_all = sorted(all_vids, key=lambda x: x['published'], reverse=True)
for v in sorted_all[:20]:
    is_new = " [NEW!]" if v['id'] not in known_ids else ""
    print(f"  {v['id']} | {v['published'][:10]} | {v['title'][:60]}{is_new}")
