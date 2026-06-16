
import os
import json
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from tqdm import tqdm

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'config/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

def main():
    if not os.path.exists('config/channel_master_fix_prioritized.json'):
         print("❌ No plan found.")
         return

    with open('config/channel_master_fix_prioritized.json', 'r', encoding='utf-8') as f:
        updates = json.load(f)
        
    print(f"🔄 Loaded {len(updates)} tasks.")
    
    # Batching to safeguard quota?
    # 345 * 50 units = 17,250 units.
    # Daily Limit is usually 10,000.
    # WE MUST STOP at 180 videos today.
    # UPDATE: We now skip already-updated videos to maximize efficiency.
    
    # LIMIT = 180
    # print(f"⚠️ QUOTA SAFETY: Limiting to first {LIMIT} videos today.")
    
    # confirm = input("Type 'GO' to start processing: ")
    # if confirm != "GO":
    #    return
    print("🚀 Starting auto-execution.")

    youtube = get_authenticated_service()
    
    count = 0
    skipped_count = 0
    
    for item in tqdm(updates): # Process ALL, skip if done
        vid_id = item['id']
        try:
            # OPTIMIZATION: We can skip the 'get' if we trust our description.
            # But 'update' needs a complete snippet.
            # Minimizing 'get' calls saves 1 unit/video. Negligible vs 50 write.
            # Safety first: Read, Modify, Write.
            
            get_req = youtube.videos().list(part="snippet", id=vid_id)
            get_res = get_req.execute()
            
            if not get_res['items']:
                continue
                
            snippet = get_res['items'][0]['snippet']
            
            # IDEMPOTENCY CHECK (Save 50 Units)
            if snippet['title'] == item['new_title']:
                # Assume if title matches, tags are likely done too or not worth the 50 unit cost today
                skipped_count += 1
                continue

            # Apply Changes
            snippet['title'] = item['new_title']
            snippet['tags'] = item['new_tags']
            
            # Only update description if we have a NEW one (we preserved Wochenschau)
            if item['new_description'] != snippet['description']:
                snippet['description'] = item['new_description']
            
            update_req = youtube.videos().update(
                part="snippet",
                body={"id": vid_id, "snippet": snippet}
            )
            update_req.execute()
            
            count += 1
            print(f"✅ Updated: {item['new_title'][:40]}...")
            time.sleep(1) # Rate limiting
            
        except Exception as e:
            if "quotaExceeded" in str(e):
                print("🛑 FATAL: QUOTA EXCEEDED. Stopping immediately.")
                break
            print(f"Error on {vid_id}: {e}")
            
    print(f"Done. Updated: {count}, Skipped (Already Done): {skipped_count}")

if __name__ == "__main__":
    main()
