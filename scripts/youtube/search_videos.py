#!/usr/bin/env python3
"""Search for videos by keyword"""
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    queries = sys.argv[1:] if len(sys.argv) > 1 else ['ganja', 'cannabis', 'weed', 'marijuana', 'hemp', 'reefer']
    
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

    found = set()
    for query in queries:
        response = youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            maxResults=10,
            q=query
        ).execute()
        
        if response.get('items'):
            print(f'=== Search: {query} ===')
            for item in response['items']:
                vid = item['id']['videoId']
                if vid not in found:
                    found.add(vid)
                    print(f"[{vid}] {item['snippet']['title']}")
            print()

if __name__ == '__main__':
    main()
