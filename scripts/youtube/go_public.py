#!/usr/bin/env python3
"""
Switch from private test broadcast to PUBLIC broadcast.

Steps:
1. End old broadcast 57TykeHQYwU (transition → complete)
2. Update stream endpoint resolution: 2160p → 1080p (matches v9 output)
3. Set F4SwdhCvHAo privacy to PUBLIC  
4. F4SwdhCvHAo auto-starts on the active permastream

Quota cost: ~153 units (3 transitions + 1 stream update + 1 broadcast update)
"""
import os, sys, time, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE = r'D:\remaike.TV'
TOKEN = os.path.join(BASE, 'token.json')

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN, 'w') as f:
                f.write(creds.to_json())
        else:
            print("ERROR: No valid token!")
            sys.exit(1)
    return build('youtube', 'v3', credentials=creds)

yt = get_youtube()

OLD_BROADCAST = '57TykeHQYwU'
NEW_BROADCAST = 'F4SwdhCvHAo'
PERMASTREAM = 'VFv6Egpl0LDvigpFbQXNeQ1771887015419315'

# ═══════════════════════════════════════════════════════════════
# STEP 1: End old broadcast (transition live → complete)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("STEP 1: End old broadcast 57TykeHQYwU")
print("=" * 60)

try:
    # First check current status
    resp = yt.liveBroadcasts().list(id=OLD_BROADCAST, part='status').execute()
    old_status = resp['items'][0]['status']['lifeCycleStatus'] if resp.get('items') else 'not_found'
    print(f"  Current status: {old_status}")
    
    if old_status == 'live':
        print("  Transitioning live → complete...")
        yt.liveBroadcasts().transition(
            broadcastStatus='complete',
            id=OLD_BROADCAST,
            part='status'
        ).execute()
        print("  ✅ 57TykeHQYwU → complete")
        time.sleep(3)  # Wait for YouTube to process
    elif old_status == 'complete':
        print("  Already complete, skipping.")
    elif old_status == 'ready':
        print("  Not live, skipping transition.")
    else:
        print(f"  Unexpected status: {old_status}")
except Exception as e:
    print(f"  ⚠️ Error ending old broadcast: {e}")
    print("  Continuing anyway...")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Update stream endpoint resolution: 2160p → 1080p
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("STEP 2: Update permastream resolution to 1080p")
print("=" * 60)

try:
    # Get current stream config
    resp = yt.liveStreams().list(id=PERMASTREAM, part='snippet,cdn,status').execute()
    if resp.get('items'):
        stream = resp['items'][0]
        current_res = stream.get('cdn', {}).get('resolution', '?')
        current_fps = stream.get('cdn', {}).get('frameRate', '?')
        print(f"  Current: {current_res} @ {current_fps}")
        
        if current_res != '1080p':
            # Update to 1080p
            stream['cdn']['resolution'] = '1080p'
            stream['cdn']['frameRate'] = '30fps'
            updated = yt.liveStreams().update(
                part='snippet,cdn',
                body=stream
            ).execute()
            new_res = updated.get('cdn', {}).get('resolution', '?')
            print(f"  ✅ Updated to: {new_res} @ 30fps")
        else:
            print("  Already 1080p, skipping.")
    else:
        print("  ⚠️ Stream not found!")
except Exception as e:
    print(f"  ⚠️ Error updating stream: {e}")
    print("  (Bitrate warning is cosmetic - stream still works)")

# Wait for old broadcast to fully release the stream
print("\n  Waiting 5s for stream release...")
time.sleep(5)

# ═══════════════════════════════════════════════════════════════
# STEP 3: Set F4SwdhCvHAo to PUBLIC
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("STEP 3: Set F4SwdhCvHAo to PUBLIC")
print("=" * 60)

try:
    # Get current broadcast config (need full snippet for update)
    resp = yt.liveBroadcasts().list(id=NEW_BROADCAST, part='snippet,status,contentDetails').execute()
    if resp.get('items'):
        broadcast = resp['items'][0]
        current_privacy = broadcast['status']['privacyStatus']
        print(f"  Current privacy: {current_privacy}")
        
        if current_privacy != 'public':
            # Update to public
            broadcast['status']['privacyStatus'] = 'public'
            updated = yt.liveBroadcasts().update(
                part='status',
                body={
                    'id': NEW_BROADCAST,
                    'status': {
                        'privacyStatus': 'public'
                    }
                }
            ).execute()
            new_privacy = updated['status']['privacyStatus']
            print(f"  ✅ Privacy updated to: {new_privacy}")
        else:
            print("  Already public, skipping.")
    else:
        print("  ⚠️ Broadcast not found!")
except Exception as e:
    print(f"  ⚠️ Error setting public: {e}")

# ═══════════════════════════════════════════════════════════════
# STEP 4: Check if F4SwdhCvHAo auto-started
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("STEP 4: Verify F4SwdhCvHAo status (auto-start check)")
print("=" * 60)

# Wait for auto-start to trigger
for attempt in range(6):
    time.sleep(5)
    resp = yt.liveBroadcasts().list(id=NEW_BROADCAST, part='status,contentDetails').execute()
    if resp.get('items'):
        item = resp['items'][0]
        lifecycle = item['status']['lifeCycleStatus']
        privacy = item['status']['privacyStatus']
        recording = item['status']['recordingStatus']
        print(f"  [{attempt+1}/6] LifeCycle: {lifecycle} | Privacy: {privacy} | Recording: {recording}")
        
        if lifecycle == 'live':
            print(f"\n  🎉 F4SwdhCvHAo is LIVE and {privacy.upper()}!")
            print(f"  URL: https://www.youtube.com/watch?v={NEW_BROADCAST}")
            break
        elif lifecycle == 'testing':
            print("  Stream in testing phase, waiting for live...")
    else:
        print(f"  [{attempt+1}/6] Broadcast not found!")
else:
    # After 30 seconds, still not live
    print("\n  ⚠️ Auto-start hasn't triggered yet.")
    print("  The stream may need manual transition.")
    
    # Try manual transition: ready → testing → live
    try:
        resp = yt.liveBroadcasts().list(id=NEW_BROADCAST, part='status').execute()
        current = resp['items'][0]['status']['lifeCycleStatus']
        
        if current == 'ready':
            print("  Attempting manual transition: ready → testing...")
            yt.liveBroadcasts().transition(
                broadcastStatus='testing',
                id=NEW_BROADCAST,
                part='status'
            ).execute()
            time.sleep(10)
            
            print("  Attempting manual transition: testing → live...")
            yt.liveBroadcasts().transition(
                broadcastStatus='live',
                id=NEW_BROADCAST,
                part='status'
            ).execute()
            time.sleep(5)
            
            # Final check
            resp = yt.liveBroadcasts().list(id=NEW_BROADCAST, part='status').execute()
            lifecycle = resp['items'][0]['status']['lifeCycleStatus']
            privacy = resp['items'][0]['status']['privacyStatus']
            print(f"  Final: LifeCycle={lifecycle}, Privacy={privacy}")
            if lifecycle == 'live':
                print(f"\n  🎉 F4SwdhCvHAo is LIVE and {privacy.upper()}!")
                print(f"  URL: https://www.youtube.com/watch?v={NEW_BROADCAST}")
    except Exception as e:
        print(f"  ⚠️ Manual transition error: {e}")

# ═══════════════════════════════════════════════════════════════
# Final summary
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("SUMMARY")
print("=" * 60)

# Quick final check on both
for bid, label in [(OLD_BROADCAST, 'OLD'), (NEW_BROADCAST, 'NEW')]:
    try:
        resp = yt.liveBroadcasts().list(id=bid, part='status').execute()
        if resp.get('items'):
            s = resp['items'][0]['status']
            print(f"  {label} ({bid}): {s['lifeCycleStatus']} | {s['privacyStatus']}")
    except:
        pass

# Check stream
try:
    resp = yt.liveStreams().list(id=PERMASTREAM, part='status,cdn').execute()
    if resp.get('items'):
        s = resp['items'][0]
        print(f"  STREAM: {s['status']['streamStatus']} | {s['cdn'].get('resolution')} | Health: {s['status'].get('healthStatus', {}).get('status', '?')}")
except:
    pass

print(f"\n  🔗 https://www.youtube.com/watch?v={NEW_BROADCAST}")
print(f"  📊 https://studio.youtube.com/video/{NEW_BROADCAST}/livestreaming")
