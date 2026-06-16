"""Find all NOT_EMBEDDABLE + DESC_LINE1_EQUALS_TITLE videos."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
yt = build('youtube', 'v3', credentials=creds)

# Get ALL video IDs
ids = []
page = None
while True:
    req = yt.playlistItems().list(part='contentDetails', playlistId='UUVFv6Egpl0LDvigpFbQXNeQ', maxResults=50, pageToken=page)
    data = req.execute()
    for item in data.get('items', []):
        ids.append(item['contentDetails']['videoId'])
    page = data.get('nextPageToken')
    if not page:
        break

print(f"Total videos: {len(ids)}")

# Get details in batches
not_embeddable = []
desc_eq_title = []
too_many_hashtags = []

for i in range(0, len(ids), 50):
    batch = ids[i:i+50]
    data = yt.videos().list(part='snippet,status', id=','.join(batch)).execute()
    for v in data.get('items', []):
        s = v['snippet']
        st = v.get('status', {})
        title = s['title']
        desc = s.get('description', '')
        first_line = desc.split('\n')[0].strip()
        
        if st.get('privacyStatus') != 'public':
            continue
        
        if not st.get('embeddable', True):
            not_embeddable.append((v['id'], title[:80]))
        
        if first_line == title.strip():
            desc_eq_title.append((v['id'], title[:80]))
        
        hashtags = [w for w in desc.split() if w.startswith('#')]
        if len(hashtags) > 5:
            too_many_hashtags.append((v['id'], title[:60], len(hashtags)))

print(f"\n=== NOT EMBEDDABLE ({len(not_embeddable)} videos) ===")
print("These videos CANNOT be embedded on external sites = LESS exposure!")
for vid_id, title in not_embeddable:
    print(f"  {vid_id} | {title}")

print(f"\n=== DESC LINE1 = TITLE ({len(desc_eq_title)} videos) ===")
print("YouTube shows line 1-2 in search results. If line 1 = title, it's WASTED.")
for vid_id, title in desc_eq_title[:20]:
    print(f"  {vid_id} | {title}")
if len(desc_eq_title) > 20:
    print(f"  ... and {len(desc_eq_title)-20} more")

print(f"\n=== TOO MANY HASHTAGS ({len(too_many_hashtags)} videos) ===")
print("Max 5 hashtags! More = YouTube may treat as spam.")
for vid_id, title, count in too_many_hashtags:
    print(f"  {vid_id} | {title} | {count} hashtags")

# Save for fix scripts
json.dump({
    'not_embeddable': [{'id': v[0], 'title': v[1]} for v in not_embeddable],
    'desc_eq_title': [{'id': v[0], 'title': v[1]} for v in desc_eq_title],
    'too_many_hashtags': [{'id': v[0], 'title': v[1], 'count': v[2]} for v in too_many_hashtags],
}, open('reports/seo_fix_targets.json', 'w'), indent=2)
print(f"\nSaved to reports/seo_fix_targets.json")
