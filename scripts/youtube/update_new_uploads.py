#!/usr/bin/env python3
"""Check and update new uploads one by one."""

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

# New uploads to process
NEW_UPLOADS = [
    {
        "id": "HGg-g6SwrrQ",
        "current": "reefer madness1938 sls 8K HQ",
        "new_title": "Reefer Madness (1938) | 8K HQ | Anti-Cannabis Propaganda | @remAIke_IT",
        "category": "1",  # Film & Animation
        "description": """🎬 Reefer Madness (1938)

The infamous anti-cannabis propaganda film! Originally financed by a church group, this cult classic has become a symbol of 1930s drug scare tactics and is now celebrated as an unintentional comedy.

📅 Year: 1938
🎞️ Genre: Exploitation / Propaganda
✨ Quality: 8K AI-Enhanced
📜 Status: Public Domain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you enjoyed this classic!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage films!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#ReeferMadness #CultClassic #Propaganda #1930s #PublicDomain #8K #VintageFilm #Exploitation #Cannabis #DrugScare""",
        "tags": ["Reefer Madness", "1938", "propaganda", "cult classic", "exploitation", "cannabis", "marijuana", "public domain", "8K", "vintage film", "anti-drug", "1930s"]
    },
    {
        "id": "YWru08pI9dA",
        "current": "popeye 1941 10 the mighty navy sls 8K HQ",
        "new_title": "Popeye: The Mighty Navy (1941) | 8K HQ | Fleischer Studios | @remAIke_IT",
        "category": "1",
        "description": """🎬 Popeye: The Mighty Navy (1941)

Classic Popeye cartoon from Fleischer Studios! Popeye joins the Navy and shows off his spinach-powered strength.

🎭 Characters: Popeye, Bluto, Olive Oyl
📅 Year: 1941
🎬 Studio: Fleischer Studios
✨ Quality: 8K AI-Enhanced
📜 Status: Public Domain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love Popeye!
💬 COMMENT your favorite episode!
🔔 SUBSCRIBE for more classic cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Popeye #FleischerStudios #ClassicCartoon #1941 #Animation #PublicDomain #8K #VintageAnimation #Navy""",
        "tags": ["Popeye", "Fleischer Studios", "1941", "classic cartoon", "animation", "public domain", "8K", "vintage", "Mighty Navy", "Bluto", "Olive Oyl"]
    },
    {
        "id": "kjoxZ7qkduk",
        "current": "beautifuldaytofall sls 8K HQ",
        "new_title": None,  # Need more info
        "skip": True
    },
    {
        "id": "PbIzH1DnEoc",
        "current": "theescortsbetty radiocommercials sls 8K HQ",
        "new_title": None,  # Need more info
        "skip": True
    },
    {
        "id": "7iq6jfc2BvY",
        "current": "soundie gotosleeplittlebaby sls 8K HQ",
        "new_title": "Soundie: Go to Sleep Little Baby | 8K HQ | Vintage Music | @remAIke_IT",
        "category": "10",  # Music
        "description": """🎬 Soundie: Go to Sleep Little Baby

A rare vintage Soundie from the golden age of jukebox music films! Soundies were 3-minute musical films produced between 1940-1947 for coin-operated film jukeboxes called Panorams.

🎼 Song: Go to Sleep Little Baby
📅 Era: 1940s
🎞️ Format: Soundie (Musical Short Film)
✨ Quality: 8K AI-Enhanced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love vintage music!
💬 COMMENT your favorite classic songs!
🔔 SUBSCRIBE for more rare musical gems!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Soundie #VintageMusic #1940s #Lullaby #ClassicMusic #JukeboxMusic #PublicDomain #8K #MusicalShort""",
        "tags": ["Soundie", "Go to Sleep Little Baby", "1940s", "vintage music", "lullaby", "jukebox", "panoram", "public domain", "8K", "musical short"]
    },
    {
        "id": "JzJrH43etPA",
        "current": "ken block gymkhana 3 topaz ready sls 8K HQ",
        "new_title": "Ken Block: Gymkhana 3 (2010) | 8K HQ | DC Shoes | @remAIke_IT",
        "category": "17",  # Sports
        "description": """🏎️ Ken Block: Gymkhana 3 - The Music Video Infomercial (2010)

The legendary Gymkhana 3 video featuring Ken Block's incredible stunt driving! Part of DC Shoes' groundbreaking Gymkhana series that revolutionized car videos.

🚗 Driver: Ken Block
🎬 Series: Gymkhana
📅 Year: 2010
🏢 Production: DC Shoes
✨ Quality: 8K AI-Enhanced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love motorsport!
💬 COMMENT your favorite Gymkhana!
🔔 SUBSCRIBE for more action!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT
🕊️ RIP Ken Block (1967-2023)

#KenBlock #Gymkhana #DCShoes #Motorsport #Drifting #Rally #8K #StuntDriving #FordFiesta #Hoonigan""",
        "tags": ["Ken Block", "Gymkhana", "Gymkhana 3", "DC Shoes", "drifting", "rally", "motorsport", "stunt driving", "8K", "Ford Fiesta", "Hoonigan"]
    },
    {
        "id": "2up3EWL61sU",
        "current": "popeye 1936 06 i wanna be a life guard sls 8K HQ",
        "new_title": "Popeye: I Wanna Be a Life Guard (1936) | 8K HQ | Fleischer Studios | @remAIke_IT",
        "category": "1",
        "description": """🎬 Popeye: I Wanna Be a Life Guard (1936)

Classic Popeye cartoon from Fleischer Studios! Popeye and Bluto compete to be lifeguards and impress Olive Oyl at the beach.

🎭 Characters: Popeye, Bluto, Olive Oyl
📅 Year: 1936
🎬 Studio: Fleischer Studios
✨ Quality: 8K AI-Enhanced
📜 Status: Public Domain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love Popeye!
💬 COMMENT your favorite episode!
🔔 SUBSCRIBE for more classic cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Popeye #FleischerStudios #ClassicCartoon #1936 #Animation #PublicDomain #8K #VintageAnimation #Lifeguard""",
        "tags": ["Popeye", "Fleischer Studios", "1936", "classic cartoon", "animation", "public domain", "8K", "vintage", "Life Guard", "Bluto", "Olive Oyl"]
    },
    {
        "id": "19FSrxzSx-M",
        "current": "popeye 1934 06 axe me another sls 8K HQ",
        "new_title": "Popeye: Axe Me Another (1934) | 8K HQ | Fleischer Studios | @remAIke_IT",
        "category": "1",
        "description": """🎬 Popeye: Axe Me Another (1934)

Classic Popeye cartoon from Fleischer Studios! An early Popeye adventure featuring his trademark spinach-powered heroics.

🎭 Characters: Popeye, Bluto, Olive Oyl
📅 Year: 1934
🎬 Studio: Fleischer Studios
✨ Quality: 8K AI-Enhanced
📜 Status: Public Domain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love Popeye!
💬 COMMENT your favorite episode!
🔔 SUBSCRIBE for more classic cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Popeye #FleischerStudios #ClassicCartoon #1934 #Animation #PublicDomain #8K #VintageAnimation""",
        "tags": ["Popeye", "Fleischer Studios", "1934", "classic cartoon", "animation", "public domain", "8K", "vintage", "Axe Me Another", "Bluto", "Olive Oyl"]
    },
    {
        "id": "1Z_LwK_ledI",
        "current": "1940 06 20 wochenschau nr 511  cpm unknown sls 8K HQ",
        "new_title": "Die Deutsche Wochenschau Nr. 511 (20.06.1940) | 8K HQ | @remAIke_IT",
        "category": "25",  # News & Politics
        "description": """🎬 Die Deutsche Wochenschau Nr. 511 (20.06.1940)

German newsreel from World War II era. Historical documentation preserved in 8K quality.

📅 Date: June 20, 1940
🎞️ Format: Deutsche Wochenschau (German Newsreel)
✨ Quality: 8K AI-Enhanced
📜 Status: Public Domain

⚠️ DISCLAIMER: This historical footage is presented for educational and documentary purposes only. It does not represent the views of this channel.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 For historical research and education
🔔 SUBSCRIBE for more historical footage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More: https://frai.tv | @remAIke_IT

#Wochenschau #1940 #WWII #History #Newsreel #PublicDomain #8K #Documentary #HistoricalFootage""",
        "tags": ["Wochenschau", "1940", "WWII", "World War 2", "history", "newsreel", "documentary", "public domain", "8K", "German", "historical"]
    }
]

def update_video(video_id, new_title, description, tags, category):
    """Update a single video."""
    try:
        response = youtube.videos().list(part="snippet,status", id=video_id).execute()
        if not response.get("items"):
            return False, "Video not found"
        
        snippet = response["items"][0]["snippet"]
        old_title = snippet["title"]
        
        snippet["title"] = new_title
        snippet["description"] = description
        snippet["tags"] = tags
        snippet["categoryId"] = category
        
        youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": snippet}
        ).execute()
        
        return True, old_title
    except Exception as e:
        return False, str(e)

# Process each video
print("🎬 NEUE UPLOADS STEP-BY-STEP AKTUALISIEREN")
print("=" * 70)

for i, upload in enumerate(NEW_UPLOADS, 1):
    print(f"\n[{i}/{len(NEW_UPLOADS)}] {upload['current']}")
    
    if upload.get("skip"):
        print("   ⏭️ ÜBERSPRUNGEN - braucht mehr Info")
        continue
    
    if upload.get("new_title"):
        success, result = update_video(
            upload["id"],
            upload["new_title"],
            upload["description"],
            upload["tags"],
            upload["category"]
        )
        
        if success:
            print(f"   ✅ → {upload['new_title'][:55]}...")
        else:
            print(f"   ❌ Fehler: {result[:50]}")

print("\n" + "=" * 70)
print("✅ FERTIG!")
