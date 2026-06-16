#!/usr/bin/env python3
"""Check drafts and livestream title."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json')
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def main():
    youtube = get_youtube()
    
    # 1) Get uploads playlist
    ch = youtube.channels().list(part='contentDetails', mine=True).execute()
    uploads_pl = ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"Uploads playlist: {uploads_pl}")
    
    # 2) List ALL videos from uploads
    all_vids = []
    next_token = None
    page = 0
    while True:
        resp = youtube.playlistItems().list(
            part='contentDetails,status',
            playlistId=uploads_pl,
            maxResults=50,
            pageToken=next_token
        ).execute()
        for item in resp.get('items', []):
            vid_id = item['contentDetails']['videoId']
            status = item.get('status', {}).get('privacyStatus', '?')
            all_vids.append({'id': vid_id, 'status': status})
        next_token = resp.get('nextPageToken')
        page += 1
        if not next_token or page > 12:
            break
    
    print(f"Total videos: {len(all_vids)}")
    
    # 3) Filter private (drafts are private)
    private_vids = [v for v in all_vids if v['status'] == 'private']
    print(f"Private videos: {len(private_vids)}")
    
    # 4) Get details for private videos
    drafts = []
    if private_vids:
        for i in range(0, len(private_vids), 50):
            batch = private_vids[i:i+50]
            ids = ','.join(v['id'] for v in batch)
            det = youtube.videos().list(part='snippet,status', id=ids).execute()
            for item in det.get('items', []):
                vid_id = item['id']
                title = item['snippet']['title']
                status = item['status']['privacyStatus']
                upload = item['status'].get('uploadStatus', '?')
                cat = item['snippet'].get('categoryId', '?')
                drafts.append({
                    'id': vid_id,
                    'title': title,
                    'status': status,
                    'upload': upload,
                    'category': cat
                })
                print(f"  [{status}/{upload}] cat={cat} {vid_id}: {title}")
    
    # 5) Check livestream
    print("\n=== LIVESTREAM CHECK ===")
    live = youtube.videos().list(
        part='snippet,status,liveStreamingDetails',
        id='lm4EcKHQ45o'
    ).execute()
    
    if live.get('items'):
        ls = live['items'][0]
        snippet = ls['snippet']
        status = ls['status']
        print(f"Title: {snippet['title']}")
        print(f"Status: {status['privacyStatus']}")
        print(f"Category: {snippet.get('categoryId', '?')}")
        desc = snippet.get('description', '')
        desc_lines = desc.split('\n')[:8]
        print("Desc (first 8 lines):")
        for l in desc_lines:
            print(f"  {l}")
        tags = snippet.get('tags', [])
        print(f"Tags ({len(tags)}): {tags}")
    else:
        print("Livestream not found!")
    
    # Save results
    result = {
        'drafts': drafts,
        'total_videos': len(all_vids),
        'private_count': len(private_vids)
    }
    with open('config/draft_check_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to config/draft_check_result.json")
    
    # Quota used: channels.list(1) + playlistItems.list(pages*1) + videos.list(batches*1) + videos.list(1)
    quota = 1 + page + (len(private_vids)//50 + 1) + 1
    print(f"Estimated quota used: ~{quota} Units (all reads)")

if __name__ == '__main__':
    main()
