#!/usr/bin/env python3
"""Check specific video details"""
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    video_id = sys.argv[1] if len(sys.argv) > 1 else 'T-EsdXGhqog'
    
    with open('config/youtube_oauth.json', 'r') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret']
    )

    youtube = build('youtube', 'v3', credentials=creds)

    # Get video details
    response = youtube.videos().list(
        part='snippet,status,statistics',
        id=video_id
    ).execute()

    if response['items']:
        item = response['items'][0]
        snippet = item['snippet']
        status = item['status']
        stats = item.get('statistics', {})
        
        print('=' * 60)
        print('VIDEO DETAILS')
        print('=' * 60)
        print(f"Video ID: {video_id}")
        print(f"Title: {snippet['title']}")
        print(f"Channel: {snippet['channelTitle']}")
        print(f"Published: {snippet['publishedAt']}")
        print(f"Privacy: {status['privacyStatus']}")
        print(f"Category: {snippet.get('categoryId', 'N/A')}")
        print(f"Views: {stats.get('viewCount', 'N/A')}")
        print(f"Likes: {stats.get('likeCount', 'N/A')}")
        print()
        print('DESCRIPTION:')
        print('-' * 40)
        desc = snippet.get('description', '')
        print(desc[:800] if desc else '(empty)')
        print()
        print('TAGS:')
        print('-' * 40)
        tags = snippet.get('tags', [])
        print(tags if tags else '(no tags)')
    else:
        print('Video not found or not accessible')

if __name__ == '__main__':
    main()
