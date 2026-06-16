"""
audit_all_broadcasts.py – Show ALL broadcasts, find zombies, identify thumbnail
"""
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

print("=" * 80)
print("  COMPLETE BROADCAST AUDIT")
print("=" * 80)

# Get ALL broadcasts (active, upcoming, completed)
all_broadcasts = []
for status in ['active', 'upcoming', 'completed', 'all']:
    r = yt.liveBroadcasts().list(
        part='id,snippet,status,contentDetails',
        broadcastStatus=status,
        maxResults=50
    ).execute()
    for item in r.get('items', []):
        item['_query_status'] = status
        all_broadcasts.append(item)

print(f"\nFound {len(all_broadcasts)} total broadcasts\n")

for i, bc in enumerate(all_broadcasts):
    bid = bc['id']
    sn = bc['snippet']
    st = bc['status']
    title = sn.get('title', 'NO TITLE')[:70]
    privacy = st.get('privacyStatus', '?')
    lifecycle = st.get('lifeCycleStatus', '?')
    recording = st.get('recordingStatus', '?')
    scheduled = sn.get('scheduledStartTime', '?')[:19]
    actual_start = sn.get('actualStartTime', 'never')[:19]
    actual_end = sn.get('actualEndTime', 'never')[:19]
    thumb = sn.get('thumbnails', {})
    has_custom_thumb = 'maxres' in thumb or 'high' in thumb
    thumb_url = thumb.get('maxres', thumb.get('high', thumb.get('default', {}))).get('url', 'none') if thumb else 'none'
    
    # Check stream binding
    cd = bc.get('contentDetails', {})
    bound_stream = cd.get('boundStreamId', 'NONE')
    
    is_live = lifecycle == 'live'
    is_zombie = lifecycle in ['complete', 'revoked'] or (lifecycle != 'live' and privacy != 'public')
    
    status_icon = '🟢 LIVE' if is_live else '💀 ZOMBIE' if is_zombie else '⏸️ IDLE'
    
    print(f"{'─' * 80}")
    print(f"  {status_icon} #{i+1}: {bid}")
    print(f"  Title:     {title}")
    print(f"  Privacy:   {privacy}")
    print(f"  Lifecycle: {lifecycle}")
    print(f"  Recording: {recording}")
    print(f"  Started:   {actual_start}")
    print(f"  Ended:     {actual_end}")
    print(f"  Stream:    {bound_stream[:40]}...")
    print(f"  Thumbnail: {'CUSTOM' if has_custom_thumb else 'DEFAULT/AUTO'}")
    if 'custom' in thumb_url.lower() or 'maxres' in thumb:
        print(f"  Thumb URL: {thumb_url[:80]}")

# Also check what thumbnails exist as files
import os
print(f"\n{'=' * 80}")
print("  LOCAL THUMBNAIL FILES")
print(f"{'=' * 80}")
thumb_dirs = ['assets', 'assets/wochenschau', 'config', '.']
for d in thumb_dirs:
    full = os.path.join('D:\\remaike.TV', d)
    if os.path.isdir(full):
        for f in os.listdir(full):
            if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                fpath = os.path.join(full, f)
                size = os.path.getsize(fpath)
                print(f"  {d}/{f}  ({size:,} bytes)")
