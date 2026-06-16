
import os
import json
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# SCOPES
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'config/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

def main():
    if not os.path.exists('config/alfred_deep_fix.json'):
        print("❌ Config file 'config/alfred_deep_fix.json' not found. Run create_alfred_fix.py first.")
        return

    with open('config/alfred_deep_fix.json', 'r', encoding='utf-8') as f:
        updates = json.load(f)
        
    print(f"🔄 Loaded {len(updates)} planned updates for Alfred J. Kwak.")
    print("⚠️  COST: 50 Quota Units per update.")
    print(f"⚠️  TOTAL COST: {len(updates) * 50} Units.")
    
    confirm = input("Type 'APPLY' to proceed with LIVE updates: ")
    if confirm != "APPLY":
        print("❌ Aborted.")
        return

    youtube = get_authenticated_service()
    
    success_count = 0
    fail_count = 0
    
    for item in updates:
        vid_id = item['id']
        new_title = item['new_title']
        
        print(f"🎬 Updating: {vid_id} -> {new_title}")
        
        try:
            # 1. Get current snippet to preserve other fields if needed (though we overwrite mostly)
            # Actually, per instructions, we should READ with valid key or just overwrite snippet?
            # 'update' requires the full snippet object usually, or it might clear missing fields.
            # Safest is to fetch first (Cost: 1 unit).
            
            get_req = youtube.videos().list(
                part="snippet",
                id=vid_id
            )
            get_res = get_req.execute()
            
            if not get_res['items']:
                print(f"❌ Video {vid_id} not found.")
                fail_count += 1
                continue
                
            snippet = get_res['items'][0]['snippet']
            
            # 2. Modify Snippet
            snippet['title'] = item['new_title']
            snippet['description'] = item['new_description']
            snippet['tags'] = item['new_tags']
            snippet['categoryId'] = item['categoryId'] # 1 = Film & Animation
            
            # 3. Update (Cost: 50 units)
            update_req = youtube.videos().update(
                part="snippet",
                body={
                    "id": vid_id,
                    "snippet": snippet
                }
            )
            update_req.execute()
            
            print(f"✅ Success: {new_title}")
            success_count += 1
            time.sleep(1) # Rate limit politeness
            
        except Exception as e:
            print(f"❌ Failed to update {vid_id}: {str(e)}")
            fail_count += 1
            
    print(f"🏁 DONE. Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
