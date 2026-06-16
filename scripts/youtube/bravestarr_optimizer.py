#!/usr/bin/env python3
"""BraveStarr Series Optimizer - Playlist, Beschreibung, Tags

Diese Script:
1. Erstellt eine chronologische Playlist für alle BraveStarr Folgen
2. Optimiert Titel im Format: BraveStarr (X/65): [Originaltitel] ([Jahr]) | 8K HQ | Deutsch | @remAIke_IT
3. Fügt recherchierte Tags hinzu
4. Aktualisiert Beschreibungen mit Serieninfos

BraveStarr Facts (Wikipedia):
- Serie: 1987-1988, Filmation
- 65 Episoden
- Space Western, 23. Jahrhundert, Planet New Texas
- Hauptcharakter: Marshal BraveStarr (Native American)
- Sidekick: Thirty/Thirty (Equestroid)
- Antagonist: Tex Hex, Stampede
- Regisseure: Lou Kachivas, Tom Tataranowicz, Ernie Schmidt, Bill Reed, etc.
- Stimmen: Pat Fraley, Charlie Adler, Ed Gilbert, Susan Blu, Alan Oppenheimer
"""

from __future__ import annotations
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
OAUTH_FILE = CONFIG / "youtube_oauth.json"
VIDEOS_CACHE = CONFIG / "videos.json"
REPORT_FILE = CONFIG / "bravestarr_report.json"

# ═══════════════════════════════════════════════════════════════════════════
# BRAVESTARR KNOWLEDGE BASE - Recherchiert von Wikipedia
# ═══════════════════════════════════════════════════════════════════════════

BRAVESTARR_INFO = {
    "series_name": "BraveStarr",
    "total_episodes": 65,
    "year_start": 1987,
    "year_end": 1988,
    "studio": "Filmation",
    "genre": "Space Western",
    "setting": "New Texas, 23. Jahrhundert",
    
    "main_characters": [
        "Marshal BraveStarr", "Thirty/Thirty", "Deputy Fuzz", 
        "Judge J.B. McBride", "Shaman", "Tex Hex", "Stampede"
    ],
    
    "voice_actors": {
        "Pat Fraley": "Marshal BraveStarr",
        "Ed Gilbert": "Thirty/Thirty, Shaman",
        "Charlie Adler": "Deputy Fuzz, Tex Hex",
        "Susan Blu": "Judge J.B. McBride",
        "Alan Oppenheimer": "Stampede",
        "Lou Scheimer": "Doc Clayton",
    },
    
    "bravestarr_powers": [
        "Eyes of the Hawk", "Ears of the Wolf", 
        "Strength of the Bear", "Speed of the Puma"
    ],
    
    "base_tags": [
        "BraveStarr", "Bravestarr", "Brave Starr",
        "Filmation", "1987", "1988", "80s cartoon",
        "Space Western", "sci-fi western", "New Texas",
        "Marshal BraveStarr", "Thirty Thirty",
        "Tex Hex", "Stampede", "Shaman",
        "Mattel", "action cartoon", "80er Zeichentrick",
        "Deutsch", "German", "HD", "8K", "4K UHD",
        "remastered", "AI upscaled", "remAIke",
        "Pat Fraley", "Charlie Adler", "Ed Gilbert",
        "Eyes of the Hawk", "Strength of the Bear",
        "classic cartoon", "nostalgia", "retro",
        "He-Man era", "Masters of the Universe era"
    ]
}

# Chronologische Episodenliste (Broadcast Order)
EPISODE_LIST = [
    (1, "The Disappearance of Thirty-Thirty", "September 14, 1987"),
    (2, "Fallen Idol", "September 15, 1987"),
    (3, "The Taking of Thistledown 123", "September 16, 1987"),
    (4, "Skuzz and Fuzz", "September 17, 1987"),
    (5, "A Day in the Life of a New Texas Judge", "September 18, 1987"),
    (6, "Rampage", "September 21, 1987"),
    (7, "To Walk a Mile", "September 22, 1987"),
    (8, "Big Thirty and Little Wimble", "September 23, 1987"),
    (9, "BraveStarr and the Law", "September 24, 1987"),
    (10, "Kerium Fever", "September 25, 1987"),
    (11, "Memories", "September 28, 1987"),
    (12, "Eyewitness", "September 29, 1987"),
    (13, "The Vigilantes", "September 30, 1987"),
    (14, "Wild Child", "October 1, 1987"),
    (15, "Hail, Hail, the Gang's All Here", "October 2, 1987"),
    (16, "Eye of the Beholder", "October 5, 1987"),
    (17, "The Wrong Hands", "October 6, 1987"),
    (18, "An Older Hand", "October 7, 1987"),
    (19, "Showdown at Sawtooth", "October 8, 1987"),
    (20, "Unsung Hero", "October 12, 1987"),
    (21, "Lost Mountain", "October 13, 1987"),
    (22, "Trouble Wears a Badge", "October 15, 1987"),
    (23, "Who Am I?", "October 16, 1987"),
    (24, "BraveStarr and the Treaty", "October 20, 1987"),
    (25, "Thoren the Slavemaster", "October 21, 1987"),
    (26, "The Price", "October 22, 1987"),
    (27, "Revolt of the Prairie People", "October 23, 1987"),
    (28, "Hostage", "October 26, 1987"),
    (29, "Tunnel of Terror", "October 27, 1987"),
    (30, "The Good, the Bad, and the Clumsy", "October 28, 1987"),
    (31, "Balance of Power", "October 29, 1987"),
    (32, "Call to Arms", "October 30, 1987"),
    (33, "BraveStarr and the Three Suns", "November 2, 1987"),
    (34, "The Witnesses", "November 3, 1987"),
    (35, "Handlebar and Rampage", "November 4, 1987"),
    (36, "Runaway Planet", "November 5, 1987"),
    (37, "The Bounty Hunter", "November 6, 1987"),
    (38, "Buddy", "November 9, 1987"),
    (39, "The Day the Town Was Taken", "November 10, 1987"),
    (40, "BraveStarr and the Medallion", "November 11, 1987"),
    (41, "Legend of a Pretty Lady", "November 12, 1987"),
    (42, "Sunrise, Sunset", "November 13, 1987"),
    (43, "Call of the Wild", "November 16, 1987"),
    (44, "Tex But No Hex", "November 17, 1987"),
    (45, "Space Zoo", "November 18, 1987"),
    (46, "Tex's Terrible Night", "December 14, 1987"),  # Christmas Episode
    (47, "Running Wild", "January 29, 1988"),
    (48, "Thirty-Thirty Goes Camping", "February 1, 1988"),
    (49, "The Haunted Shield", "February 2, 1988"),
    (50, "Ship of No Return", "February 3, 1988"),
    (51, "The Little Lie That Grew", "February 4, 1988"),
    (52, "Brothers in Crime", "February 5, 1988"),
    (53, "Sherlock Holmes in the 23rd Century: Part 1", "February 8, 1988"),
    (54, "Sherlock Holmes in the 23rd Century: Part 2", "February 9, 1988"),
    (55, "New Texas Blues", "February 10, 1988"),
    (56, "Jeremiah and the Prairie People", "February 11, 1988"),
    (57, "The Ballad of Sara Jane", "February 12, 1988"),
    (58, "Brother's Keeper", "February 15, 1988"),
    (59, "BraveStarr and the Empress", "February 16, 1988"),
    (60, "Night of the Bronco-Tank", "February 17, 1988"),
    (61, "Nomad Is an Island", "February 18, 1988"),
    (62, "The Blockade", "February 19, 1988"),
    (63, "No Drums, No Trumpets", "February 22, 1988"),
    (64, "Shake Hands with Long Arm John", "February 23, 1988"),
    (65, "Strength of the Bear", "February 24, 1988"),
]

SERIES_DESCRIPTION = """🤠 BraveStarr - Komplette Serie in 8K | Folge {ep_num} von 65

📺 "{ep_title}" - Original ausgestrahlt am {air_date}

═══════════════════════════════════════════════
🌟 ÜBER BRAVESTARR
═══════════════════════════════════════════════

BraveStarr ist eine amerikanische Space-Western-Zeichentrickserie von Filmation (1987-1988). Die Serie spielt im 23. Jahrhundert auf dem Wüstenplaneten New Texas.

👤 HAUPTCHARAKTERE:
• Marshal BraveStarr - Galaktischer Marshal mit Tierkräften
• Thirty/Thirty - Sein Equestroid-Partner (Pferd-Cyborg)  
• Deputy Fuzz - Kleiner pelziger Hilfsdeputy
• Judge J.B. McBride - Richterin und BraveStarrs Verbündete
• Shaman - BraveStarrs mystischer Mentor
• Tex Hex - Hauptantagonist mit magischen Kräften
• Stampede - Uralter Broncosaur, Anführer der Schurken

⚡ BRAVESTARRS KRÄFTE:
• 👁️ Eyes of the Hawk (Adleraugen)
• 👂 Ears of the Wolf (Wolfsohren)
• 💪 Strength of the Bear (Bärenstärke)
• 🏃 Speed of the Puma (Pumaschnelligkeit)

═══════════════════════════════════════════════
📋 EPISODENLISTE - KOMPLETTE SERIE
═══════════════════════════════════════════════
▶️ Playlist: https://www.youtube.com/playlist?list=BRAVESTARR_PLAYLIST_ID

═══════════════════════════════════════════════
🎬 ÜBER DIESE VERSION
═══════════════════════════════════════════════
• 8K AI-Upscaling (4K UHD verfügbar)
• Deutsche Synchronfassung
• Restauriert & Remastered
• Best Quality Online

📌 ABONNIEREN für mehr klassische Zeichentrickserien!

#BraveStarr #Filmation #80sCartoon #SpaceWestern #Deutsch #8K #Retro #Nostalgie #Zeichentrick #remAIke
"""


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_youtube_client():
    if not OAUTH_FILE.exists():
        raise SystemExit(f"Missing: {OAUTH_FILE}")
    
    creds_data = load_json(OAUTH_FILE)
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes"),
    )
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        creds_data["token"] = creds.token
        save_json(OAUTH_FILE, creds_data)
    
    return build("youtube", "v3", credentials=creds)


def match_episode(title: str) -> Optional[tuple]:
    """Findet passende Episode basierend auf Titel"""
    title_lower = title.lower()
    
    for ep_num, ep_title, air_date in EPISODE_LIST:
        # Exakter Match auf Episodentitel
        ep_lower = ep_title.lower()
        if ep_lower in title_lower:
            return (ep_num, ep_title, air_date)
        
        # Keyword-Match
        keywords = ep_lower.split()
        matches = sum(1 for kw in keywords if len(kw) > 3 and kw in title_lower)
        if matches >= 2:
            return (ep_num, ep_title, air_date)
    
    # Spezielle Matches
    if "musik" in title_lower or "festival" in title_lower:
        return (55, "New Texas Blues", "February 10, 1988")
    if "intro" in title_lower:
        return (0, "Intro/Opening", "1987")
    
    return None


def generate_episode_title(ep_num: int, ep_title: str) -> str:
    """Generiert optimierten Titel"""
    if ep_num == 0:
        return "BraveStarr Intro | 8K HQ (4K UHD) | Deutsch | @remAIke_IT"
    return f"BraveStarr ({ep_num}/65): {ep_title} (1987) | 8K HQ | Deutsch | @remAIke_IT"


def generate_episode_description(ep_num: int, ep_title: str, air_date: str) -> str:
    """Generiert Beschreibung für Episode"""
    return SERIES_DESCRIPTION.format(
        ep_num=ep_num if ep_num > 0 else "Intro",
        ep_title=ep_title,
        air_date=air_date
    )


def generate_tags(ep_num: int, ep_title: str) -> List[str]:
    """Generiert Tags für Episode"""
    tags = list(BRAVESTARR_INFO["base_tags"])
    
    # Episode-spezifische Tags
    if ep_num > 0:
        tags.append(f"Episode {ep_num}")
        tags.append(f"Folge {ep_num}")
    
    # Titel-Keywords (nur alphanumerische, keine Sonderzeichen)
    for word in ep_title.split():
        # Entferne Sonderzeichen, behalte nur Buchstaben
        clean_word = re.sub(r'[^a-zA-Z0-9äöüÄÖÜß]', '', word)
        if len(clean_word) > 3:
            tags.append(clean_word)
    
    # Spezielle Episodes
    ep_lower = ep_title.lower()
    if "sherlock" in ep_lower:
        tags.extend(["Sherlock Holmes", "time travel", "detective"])
    if "thirty" in ep_lower:
        tags.extend(["Thirty Thirty", "horse"])
    if "tex" in ep_lower:
        tags.extend(["Tex Hex", "villain", "Schurke"])
    if "shaman" in ep_lower or "bear" in ep_lower:
        tags.extend(["Shaman", "mystical", "powers"])
    
    # Deduplizieren und validieren
    seen = set()
    result = []
    for tag in tags:
        # Tag säubern: keine Sonderzeichen außer Leerzeichen, Bindestrich
        clean_tag = re.sub(r'[<>]', '', str(tag)).strip()
        if not clean_tag or len(clean_tag) < 2:
            continue
        key = clean_tag.lower()
        if key not in seen:
            seen.add(key)
            result.append(clean_tag)
    
    # Auf 500 Zeichen begrenzen
    kept = []
    for tag in result:
        if len(",".join(kept + [tag])) <= 500:
            kept.append(tag)
    
    return kept


def create_playlist(youtube, title: str, description: str) -> str:
    """Erstellt eine neue Playlist"""
    body = {
        "snippet": {
            "title": title,
            "description": description,
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    
    response = youtube.playlists().insert(
        part="snippet,status",
        body=body
    ).execute()
    
    return response["id"]


def add_to_playlist(youtube, playlist_id: str, video_id: str, position: int = None):
    """Fügt Video zur Playlist hinzu"""
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
    
    if position is not None:
        body["snippet"]["position"] = position
    
    youtube.playlistItems().insert(
        part="snippet",
        body=body
    ).execute()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BraveStarr Series Optimizer")
    parser.add_argument("--analyze", action="store_true", help="Nur analysieren")
    parser.add_argument("--create-playlist", action="store_true", help="Playlist erstellen")
    parser.add_argument("--update-videos", action="store_true", help="Videos optimieren")
    parser.add_argument("--apply", action="store_true", help="Änderungen anwenden")
    args = parser.parse_args()
    
    print("=" * 60)
    print("BRAVESTARR SERIES OPTIMIZER")
    print("Space Western · Filmation · 1987-1988 · 65 Episodes")
    print("=" * 60)
    
    youtube = get_youtube_client()
    
    # Videos laden
    cache = load_json(VIDEOS_CACHE)
    videos = cache.get("videos", [])
    
    # BraveStarr Videos finden
    bravestarr_videos = []
    for v in videos:
        title = v.get("title", "").lower()
        if "bravestar" in title or "brave star" in title:
            ep_match = match_episode(v.get("title", ""))
            bravestarr_videos.append({
                "video": v,
                "episode": ep_match
            })
    
    print(f"\n[Gefunden] {len(bravestarr_videos)} BraveStarr Videos")
    
    for item in bravestarr_videos:
        v = item["video"]
        ep = item["episode"]
        if ep:
            ep_num, ep_title, air_date = ep
            print(f"  • {v['title'][:50]}...")
            print(f"    → Episode {ep_num}: {ep_title}")
        else:
            print(f"  • {v['title'][:50]}... (Keine Episode erkannt)")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "videos_found": len(bravestarr_videos),
        "actions": []
    }
    
    if args.create_playlist and args.apply:
        print("\n[Playlist] Erstelle BraveStarr Playlist...")
        
        playlist_desc = """🤠 BraveStarr - Die komplette Serie in chronologischer Reihenfolge!

Alle 65 Episoden der legendären Space-Western-Serie von Filmation (1987-1988).

Erlebe Marshal BraveStarr und seinen treuen Partner Thirty/Thirty auf dem Planeten New Texas im 23. Jahrhundert!

⭐ 8K AI-Remastered
⭐ Deutsche Synchronfassung  
⭐ Chronologische Episodenreihenfolge

#BraveStarr #Filmation #80sCartoon #SpaceWestern #Retro"""
        
        playlist_id = create_playlist(
            youtube,
            "BraveStarr - Komplette Serie (1987-1988) | 8K Deutsch",
            playlist_desc
        )
        print(f"[OK] Playlist erstellt: {playlist_id}")
        results["playlist_id"] = playlist_id
        
        # Videos zur Playlist hinzufügen (sortiert nach Episode)
        sorted_videos = sorted(
            [item for item in bravestarr_videos if item["episode"]],
            key=lambda x: x["episode"][0]
        )
        
        for i, item in enumerate(sorted_videos):
            vid = item["video"]["id"]
            ep_num = item["episode"][0]
            try:
                add_to_playlist(youtube, playlist_id, vid, position=i)
                print(f"  [+] Episode {ep_num} hinzugefügt")
                time.sleep(0.5)
            except HttpError as e:
                print(f"  [!] Fehler bei Episode {ep_num}: {e}")
    
    if args.update_videos:
        print("\n[Update] Optimiere BraveStarr Videos...")
        
        for item in bravestarr_videos:
            v = item["video"]
            ep = item["episode"]
            
            if not ep:
                print(f"  [SKIP] {v['title'][:40]}... (keine Episode)")
                continue
            
            ep_num, ep_title, air_date = ep
            
            new_title = generate_episode_title(ep_num, ep_title)
            new_desc = generate_episode_description(ep_num, ep_title, air_date)
            new_tags = generate_tags(ep_num, ep_title)
            
            print(f"\n  [{ep_num}/65] {ep_title}")
            print(f"    Alt: {v['title'][:50]}...")
            print(f"    Neu: {new_title[:50]}...")
            print(f"    Tags: {len(new_tags)}")
            
            action = {
                "video_id": v["id"],
                "episode": ep_num,
                "old_title": v["title"],
                "new_title": new_title,
                "new_tags_count": len(new_tags),
                "status": "pending"
            }
            
            if args.apply:
                try:
                    # Aktuelles Snippet holen
                    resp = youtube.videos().list(part="snippet", id=v["id"]).execute()
                    if resp.get("items"):
                        snippet = resp["items"][0]["snippet"]
                        snippet["title"] = new_title
                        snippet["description"] = new_desc
                        snippet["tags"] = new_tags
                        
                        youtube.videos().update(
                            part="snippet",
                            body={"id": v["id"], "snippet": snippet}
                        ).execute()
                        
                        action["status"] = "OK"
                        print(f"    [OK] Aktualisiert!")
                    else:
                        action["status"] = "NOT_FOUND"
                except HttpError as e:
                    if "quotaExceeded" in str(e):
                        action["status"] = "QUOTA_EXCEEDED"
                        print(f"    [STOP] Quota überschritten!")
                        results["actions"].append(action)
                        break
                    action["status"] = f"ERROR: {e}"
                    print(f"    [ERROR] {e}")
                
                time.sleep(0.5)
            else:
                action["status"] = "DRY-RUN"
            
            results["actions"].append(action)
    
    # Report speichern
    save_json(REPORT_FILE, results)
    print(f"\n[Report] Gespeichert: {REPORT_FILE}")
    
    if not args.apply:
        print("\n[DRY-RUN] Keine Änderungen. Mit --apply ausführen.")


if __name__ == "__main__":
    main()
