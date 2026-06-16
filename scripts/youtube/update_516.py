#!/usr/bin/env python3
"""Update Nr. 516 to new title format"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'
VIDEO_ID = 'T-EsdXGhqog'

# Load event data
with open('config/wochenschau_events.json', 'r', encoding='utf-8') as f:
    events_data = json.load(f)
    events = events_data.get('events', {})

event_516 = events.get('516', {})
print("Event data for Nr. 516:")
print(json.dumps(event_516, indent=2, ensure_ascii=False))

# New title - OPTION A: Keyword First
new_title = f"Wochenschau Nr. 516: Battle of Britain (1940) | 8K | @remAIke_IT"

# Build new description with locations
event_de = event_516.get('event_de', 'Luftschlacht England')
event_en = event_516.get('event_en', 'Battle of Britain')
note = event_516.get('note', '')
date = event_516.get('date', '1940-07-24')

# Locations for this episode
locations = "🗺️ LOCATIONS: England, London, Dover, RAF Bases, Luftwaffe, English Channel"

new_description = f"""🎬 Die Deutsche Wochenschau Nr. 516 ({date}) | {event_en} | 8K

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🇩🇪 {event_de}: {note}
Wochenschau Nr. 516 zeigt NS-Propaganda zur Luftschlacht um England. Original Bundesarchiv-Material in 8K restauriert.

🇺🇸 {event_en}: German newsreel coverage of the aerial campaign against Britain. 
Nazi propaganda footage from German Federal Archives, restored in stunning 8K quality.

{locations}

📅 Historical Context:
The Battle of Britain (July-October 1940) was the first major military campaign fought entirely by air forces. 
The German Luftwaffe attempted to gain air superiority over the RAF as a prelude to Operation Sea Lion (invasion of Britain).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you found this historically valuable!
💬 COMMENT: What do you know about the Battle of Britain?
🔔 SUBSCRIBE @remAIke_IT for more WWII archives!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at https://frai.tv | @remAIke_IT

#Wochenschau #BattleOfBritain #Luftschlacht #WWII #WW2 #1940 #RAF #Luftwaffe #8K"""

# Tags with "Wochenschau" FIRST
new_tags = [
    "Wochenschau",
    "Deutsche Wochenschau",
    "Battle of Britain",
    "Luftschlacht um England",
    "WWII",
    "World War 2",
    "1940",
    "Nazi Germany",
    "RAF",
    "Luftwaffe",
    "8K",
    "Historical Documentary",
    "German Newsreel",
    "Bundesarchiv",
    "London Blitz",
    "English Channel"
]

print()
print("=" * 60)
print("PROPOSED UPDATE FOR Nr. 516")
print("=" * 60)
print(f"Video ID: {VIDEO_ID}")
print()
print("NEW TITLE:")
print(f"  {new_title}")
print()
print("NEW DESCRIPTION (first 500 chars):")
print(new_description[:500])
print()
print("NEW TAGS:")
print(new_tags)
print()
print("=" * 60)

import sys
if '--apply' not in sys.argv:
    print("DRY RUN - run with --apply to update")
    sys.exit(0)

# Apply update
print("Applying update...")

with open(OAUTH_FILE, 'r') as f:
    td = json.load(f)

creds = Credentials(
    token=td['token'],
    refresh_token=td['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=td['client_id'],
    client_secret=td['client_secret']
)

yt = build('youtube', 'v3', credentials=creds)

# Get current snippet
current = yt.videos().list(part='snippet', id=VIDEO_ID).execute()
if not current['items']:
    print("ERROR: Video not found!")
    sys.exit(1)

snippet = current['items'][0]['snippet']
category_id = snippet['categoryId']

# Update
response = yt.videos().update(
    part='snippet',
    body={
        'id': VIDEO_ID,
        'snippet': {
            'title': new_title,
            'description': new_description,
            'tags': new_tags,
            'categoryId': category_id
        }
    }
).execute()

print("✅ SUCCESS! Video updated.")
print(f"New title: {response['snippet']['title']}")
