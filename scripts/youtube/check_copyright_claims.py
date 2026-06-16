import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube_service():
    token_path = os.path.join('token.json')
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/youtube.force-ssl'])
    return build('youtube', 'v3', credentials=creds)

def check_videos():
    youtube = get_youtube_service()
    
    # Load all videos to find Wochenschau IDs
    with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    all_videos = data.get('public_videos', []) + data.get('private_videos', []) + data.get('unlisted_videos', [])
    wochenschau_videos = [v for v in all_videos if 'Wochenschau' in v.get('snippet', {}).get('title', '')]
    
    print(f"Found {len(wochenschau_videos)} Wochenschau videos.")
    
    # Check a batch of 50
    video_ids = [v['id'] for v in wochenschau_videos[:50]]
    
    request = youtube.videos().list(
        part="snippet,contentDetails,status",
        id=','.join(video_ids)
    )
    response = request.execute()
    
    for item in response.get('items', []):
        title = item['snippet']['title']
        licensed = item['contentDetails'].get('licensedContent', False)
        status = item['status']
        print(f"Title: {title[:40]}... | Licensed: {licensed} | Status: {status.get('uploadStatus')} | Privacy: {status.get('privacyStatus')}")

if __name__ == '__main__':
    check_videos()
