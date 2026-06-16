#!/usr/bin/env python3
"""Update private/draft Soundies with SEO-optimized content."""

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

# Get uploads playlist
channel_response = youtube.channels().list(part="contentDetails", mine=True).execute()
uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Find private soundies
private_soundies = []
next_page = None
while True:
    playlist_response = youtube.playlistItems().list(
        part="snippet,status",
        playlistId=uploads_playlist,
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in playlist_response.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        status = item["status"].get("privacyStatus", "unknown")
        
        if "soundie" in title.lower() and status == "private":
            private_soundies.append({
                "id": video_id, 
                "title": title,
                "description": item["snippet"].get("description", "")
            })
    
    next_page = playlist_response.get("nextPageToken")
    if not next_page:
        break

print(f"🔒 GEFUNDENE PRIVATE SOUNDIES: {len(private_soundies)}")
print("=" * 70)

# Mapping based on filename patterns
SOUNDIE_MAPPING = {
    "icantgiveyouanything": {
        "artist": "Unknown Artist",
        "song": "I Can't Give You Anything But Love",
        "year": "1940s"
    },
    "johnnylong": {
        "artist": "Johnny Long Orchestra",
        "song": "My Girl Loves a Sailor",
        "year": "1940s"
    },
    "larryclinton": {
        "artist": "Larry Clinton Orchestra",
        "song": "Whatcha Know Joe",
        "year": "1940s"
    },
    "polkasong": {
        "artist": "Unknown Artist",
        "song": "Polka Song",
        "year": "1940s"
    },
    "louis armstrong": {
        "artist": "Louis Armstrong",
        "song": "Musical Review",
        "year": "1940s"
    },
    "yvonne marthay": {
        "artist": "Yvonne Marthay",
        "song": "Performance",
        "year": "1940s"
    },
    "black music": {
        "artist": "Various Artists",
        "song": "Black Music Compilation",
        "year": "1940s"
    },
    "scarlett knight": {
        "artist": "Scarlett Knight",
        "song": "Performance",
        "year": "1940s"
    }
}

def generate_seo_description(artist, song, year):
    return f"""🎬 {artist}: {song} ({year})

A rare vintage Soundie from the golden age of jukebox music films! Soundies were 3-minute musical films produced between 1940-1947 for coin-operated film jukeboxes called Panorams.

🎵 Artist: {artist}
🎼 Song: {song}
📅 Era: {year}
🎞️ Format: Soundie (Musical Short Film)
✨ Quality: 8K AI-Enhanced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love vintage music!
💬 COMMENT your favorite classic songs!
🔔 SUBSCRIBE for more rare musical gems!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More vintage music: https://frai.tv
🎬 Channel: @remAIke_IT

#Soundie #VintageMusic #1940s #Jazz #Swing #ClassicMusic #JukeboxMusic #BigBand #PublicDomain #8K #Retro #GoldenAge #MusicalShort #Panoram
"""

def get_mapping(title):
    title_lower = title.lower()
    for key, value in SOUNDIE_MAPPING.items():
        if key in title_lower:
            return value
    return None

# Update each private soundie
success = 0
for soundie in private_soundies:
    video_id = soundie["id"]
    old_title = soundie["title"]
    
    print(f"\n📽️ {old_title}")
    
    mapping = get_mapping(old_title)
    if mapping:
        artist = mapping["artist"]
        song = mapping["song"]
        year = mapping["year"]
        
        new_title = f"{artist}: {song} | Soundie ({year}) | 8K HQ | @remAIke_IT"
        new_description = generate_seo_description(artist, song, year)
        
        print(f"   → {artist}: {song}")
        
        try:
            # Get current snippet
            video_response = youtube.videos().list(part="snippet", id=video_id).execute()
            if video_response.get("items"):
                snippet = video_response["items"][0]["snippet"]
                snippet["title"] = new_title
                snippet["description"] = new_description
                snippet["tags"] = [
                    "Soundie", "Soundies", "vintage music", "1940s", "jazz", "swing",
                    "big band", "classic music", "jukebox", "panoram", "musical short",
                    "public domain", "8K", artist, song
                ]
                
                youtube.videos().update(
                    part="snippet",
                    body={"id": video_id, "snippet": snippet}
                ).execute()
                
                print(f"   ✅ Updated!")
                success += 1
            else:
                print(f"   ❌ Video not found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")
    else:
        print(f"   ⚠️ No mapping found - skipped")

print("\n" + "=" * 70)
print(f"📊 ERGEBNIS: {success}/{len(private_soundies)} Drafts aktualisiert")
print("=" * 70)
