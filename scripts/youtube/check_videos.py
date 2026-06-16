#!/usr/bin/env python3
"""Quick video check script"""
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    video_ids = sys.argv[1] if len(sys.argv) > 1 else '3UBF9ycZwJU,dpF2uQVgCsM'
    
    with open('config/youtube_oauth.json') as f:
        oauth = json.load(f)
    
    creds = Credentials(
        token=oauth['token'],
        refresh_token=oauth['refresh_token'],
        token_uri=oauth['token_uri'],
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret']
    )
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    response = youtube.videos().list(
        part='snippet,status,contentDetails,statistics',
        id=video_ids
    ).execute()
    
    for item in response.get('items', []):
        vid = item['id']
        snip = item['snippet']
        status = item['status']
        details = item['contentDetails']
        stats = item.get('statistics', {})
        
        print(f"=== {vid} ===")
        print(f"Title: {snip['title']}")
        print(f"Status: {status['privacyStatus']}")
        print(f"Category: {snip['categoryId']}")
        print(f"Duration: {details['duration']}")
        print(f"Views: {stats.get('viewCount', 'N/A')}")
        print(f"Likes: {stats.get('likeCount', 'N/A')}")
        print()
        desc = snip['description']
        print(f"Description ({len(desc)} chars):")
        print(desc[:800] if desc else '(empty)')
        print()
        print(f"Tags: {snip.get('tags', [])}")
        print()
        print("=" * 60)

if __name__ == '__main__':
    main()
