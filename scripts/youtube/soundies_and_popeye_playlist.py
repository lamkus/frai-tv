#!/usr/bin/env python3
"""Update remaining Soundies + Create Popeye Playlist."""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open("D:/remaike.TV/config/youtube_oauth.json", "r") as f:
    token_data = json.load(f)

credentials = Credentials(
    token=token_data["token"],
    refresh_token=token_data["refresh_token"],
    token_uri=token_data["token_uri"],
    client_id=token_data["client_id"],
    client_secret=token_data["client_secret"],
)

youtube = build("youtube", "v3", credentials=credentials)

# ============================================================
# PART 1: Update remaining Soundies
# ============================================================

REMAINING_SOUNDIES = [
    {
        "id": "kjoxZ7qkduk",
        "current": "beautifuldaytofall sls 8K HQ",
        "song": "Beautiful Day to Fall",
        "new_title": "Soundie: Beautiful Day to Fall | 8K HQ | Vintage Music | @remAIke_IT",
    },
    {
        "id": "PbIzH1DnEoc",
        "current": "theescortsbetty radiocommercials sls 8K HQ",
        "song": "The Escorts / Betty - Radio Commercials",
        "new_title": "Soundie: The Escorts & Betty - Radio Commercials | 8K HQ | @remAIke_IT",
    }
]

def generate_soundie_description(song):
    return f"""🎬 Soundie: {song}

A rare vintage Soundie from the golden age of jukebox music films! Soundies were 3-minute musical films produced between 1940-1947 for coin-operated film jukeboxes called Panorams.

🎼 Song: {song}
📅 Era: 1940s
🎞️ Format: Soundie (Musical Short Film)
✨ Quality: 8K AI-Enhanced
📜 Source: Archive.org

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love vintage music!
💬 COMMENT your favorite classic songs!
🔔 SUBSCRIBE for more rare musical gems!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More vintage music: https://frai.tv
🎬 Channel: @remAIke_IT

#Soundie #VintageMusic #1940s #Jazz #Swing #ClassicMusic #JukeboxMusic #BigBand #PublicDomain #8K #Retro #GoldenAge #MusicalShort #Panoram
"""

print("=" * 70)
print("🎵 PART 1: REMAINING SOUNDIES AKTUALISIEREN")
print("=" * 70)

for soundie in REMAINING_SOUNDIES:
    print(f"\n📽️ {soundie['current']}")
    try:
        response = youtube.videos().list(part="snippet", id=soundie["id"]).execute()
        if response.get("items"):
            snippet = response["items"][0]["snippet"]
            snippet["title"] = soundie["new_title"]
            snippet["description"] = generate_soundie_description(soundie["song"])
            snippet["categoryId"] = "10"  # Music
            snippet["tags"] = [
                "Soundie", "Soundies", "vintage music", "1940s", "jazz", "swing",
                "big band", "classic music", "jukebox", "panoram", "musical short",
                "public domain", "8K", soundie["song"]
            ]
            
            youtube.videos().update(
                part="snippet",
                body={"id": soundie["id"], "snippet": snippet}
            ).execute()
            print(f"   ✅ → {soundie['new_title'][:55]}...")
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)[:50]}")

# ============================================================
# PART 2: Create Popeye Playlist
# ============================================================

print("\n" + "=" * 70)
print("🍿 PART 2: POPEYE PLAYLIST ERSTELLEN")
print("=" * 70)

# First, find all Popeye videos
channel_response = youtube.channels().list(part="contentDetails", mine=True).execute()
uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

popeye_videos = []
next_page = None
while True:
    playlist_response = youtube.playlistItems().list(
        part="snippet,status",
        playlistId=uploads_playlist,
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in playlist_response.get("items", []):
        title = item["snippet"]["title"].lower()
        status = item["status"].get("privacyStatus", "unknown")
        if "popeye" in title and status == "public":
            video_id = item["snippet"]["resourceId"]["videoId"]
            popeye_videos.append({
                "id": video_id,
                "title": item["snippet"]["title"]
            })
    
    next_page = playlist_response.get("nextPageToken")
    if not next_page:
        break

print(f"\n🔍 Gefundene Popeye Videos: {len(popeye_videos)}")

# Check if playlist already exists
playlists_response = youtube.playlists().list(part="snippet", mine=True, maxResults=50).execute()
popeye_playlist_id = None
for pl in playlists_response.get("items", []):
    if "popeye" in pl["snippet"]["title"].lower():
        popeye_playlist_id = pl["id"]
        print(f"   📋 Existierende Playlist gefunden: {pl['snippet']['title']}")
        break

# Create playlist if not exists
if not popeye_playlist_id:
    print("\n🆕 Erstelle neue Popeye Playlist...")
    
    playlist_description = """🎬 POPEYE THE SAILOR - Complete Classic Cartoons Collection | 8K HQ

The complete collection of classic Popeye cartoons from Fleischer Studios and Famous Studios, all restored in stunning 8K quality!

🍿 WHAT YOU'LL FIND:
• Original Fleischer Studios shorts (1933-1942)
• Famous Studios era (1942-1957)
• All your favorite characters: Popeye, Olive Oyl, Bluto, Wimpy, Swee'Pea

⭐ WHY WATCH:
✨ 8K AI-Enhanced quality
📜 Public Domain classics
🎭 Golden Age of Animation
🎵 Original soundtracks preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE this playlist!
🔔 SUBSCRIBE for more classic cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Popeye #FleischerStudios #ClassicCartoons #Animation #PublicDomain #8K #VintageAnimation #OliveOyl #Bluto #Spinach #GoldenAge"""

    playlist_response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Popeye the Sailor | Classic Cartoons | 8K HQ | @remAIke_IT",
                "description": playlist_description,
                "tags": ["Popeye", "Fleischer Studios", "classic cartoons", "animation", "public domain", "8K", "vintage", "Olive Oyl", "Bluto"]
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    ).execute()
    
    popeye_playlist_id = playlist_response["id"]
    print(f"   ✅ Playlist erstellt: {playlist_response['snippet']['title']}")
    print(f"   🔗 ID: {popeye_playlist_id}")

# Add videos to playlist
print(f"\n📥 Füge {len(popeye_videos)} Videos zur Playlist hinzu...")

# Sort by title (chronological by year)
popeye_videos.sort(key=lambda x: x["title"])

added = 0
for video in popeye_videos:
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": popeye_playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video["id"]
                    }
                }
            }
        ).execute()
        added += 1
        print(f"   ✅ {video['title'][:50]}...")
    except Exception as e:
        if "already contains" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"   ⏭️ Bereits in Playlist: {video['title'][:40]}...")
        else:
            print(f"   ❌ Fehler: {str(e)[:40]}")

print("\n" + "=" * 70)
print(f"📊 ERGEBNIS:")
print(f"   🎵 Soundies aktualisiert: 2")
print(f"   🍿 Popeye Playlist: {popeye_playlist_id}")
print(f"   📺 Videos in Playlist: {added} neu hinzugefügt")
print("=" * 70)
