#!/usr/bin/env python3
"""LIVE SEO OPTIMIZER - KI-gestützte Tag-Optimierung

Dieses Script analysiert jedes Video einzeln und generiert
perfekte, recherchierte Tags basierend auf:
- Titel-Analyse
- Historische Daten (Jahr, Regisseur, Darsteller)
- Genre-spezifische Keywords
- SEO Best Practices

KEINE generischen Batch-Tags - jedes Video bekommt individuelle Behandlung!
"""

from __future__ import annotations
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
OAUTH_FILE = CONFIG / "youtube_oauth.json"
VIDEOS_CACHE = CONFIG / "videos.json"
SEO_KNOWLEDGE = CONFIG / "seo_knowledge_base.json"
OUT_REPORT = CONFIG / "live_seo_report.json"

# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE - Recherchiertes Wissen
# ═══════════════════════════════════════════════════════════════════════════

SOUNDIE_KNOWLEDGE = {
    "base_tags": [
        "Soundie", "Soundies", "1940s", "Panoram", "jukebox film",
        "Mills Novelty Company", "music video", "short film",
        "vintage music", "swing era", "big band"
    ],
    # YouTube Music Discovery Tags - für Mobile App Auffindbarkeit
    "youtube_music_tags": [
        "Official Audio", "music", "song", "official video",
        "vintage music video", "classic music", "retro music",
        "jazz music", "swing music", "1940s music", "big band music",
        "boogie woogie music", "rhythm and blues", "R&B",
        "jazz standard", "American Songbook", "golden age music",
        "Topic", "auto-generated"  # YouTube Music erkennt diese
    ],
    "famous_performers": {
        "duke ellington": ["Duke Ellington", "jazz", "orchestra", "swing", "Harlem"],
        "count basie": ["Count Basie", "jazz", "orchestra", "Kansas City jazz"],
        "louis jordan": ["Louis Jordan", "Tympany Five", "jump blues", "R&B"],
        "fats waller": ["Fats Waller", "stride piano", "Honeysuckle Rose"],
        "cab calloway": ["Cab Calloway", "Hi-De-Ho", "Minnie the Moocher", "scat"],
        "dorothy dandridge": ["Dorothy Dandridge", "actress", "singer"],
        "nat king cole": ["Nat King Cole", "King Cole Trio", "jazz piano"],
        "sister rosetta tharpe": ["Sister Rosetta Tharpe", "gospel", "guitar"],
        "ink spots": ["The Ink Spots", "vocal group", "doo-wop"],
        "mills brothers": ["Mills Brothers", "vocal harmony", "barbershop"],
    },
    "songs": {
        "i can't give you anything but love": {
            "composers": ["Jimmy McHugh", "Dorothy Fields"],
            "year": 1928,
            "tags": ["jazz standard", "Blackbirds of 1928", "Adelaide Hall"]
        },
        "hollywood boogie": {
            "performer": "Hadda Brooks",
            "tags": ["Hadda Brooks", "Queen of Boogie", "boogie woogie", "piano"]
        },
        "beyond the blue horizon": {
            "composers": ["Leo Robin", "Richard A. Whiting", "W. Franke Harling"],
            "year": 1930,
            "tags": ["Jeanette MacDonald", "Monte Carlo", "Great American Songbook"]
        }
    }
}

BETTY_BOOP_KNOWLEDGE = {
    "base_tags": [
        "Betty Boop", "Fleischer Studios", "Max Fleischer", "Dave Fleischer",
        "Pre-Code", "1930s cartoon", "animation", "classic cartoon",
        "jazz age", "flapper", "Mae Questel", "Bimbo", "Koko the Clown"
    ],
    "special_episodes": {
        "minnie the moocher": ["Cab Calloway", "rotoscope", "jazz"],
        "snow white": ["Pre-Code", "Cab Calloway", "St. James Infirmary Blues"],
        "bimbo's initiation": ["surreal", "avant-garde"],
        "dizzy dishes": ["first appearance", "debut"],
    }
}

LOONEY_TUNES_KNOWLEDGE = {
    "base_tags": [
        "Looney Tunes", "Warner Bros", "Merrie Melodies", "animation",
        "classic cartoon", "golden age animation"
    ],
    "directors": {
        "tex avery": ["Tex Avery", "slapstick", "wild takes"],
        "chuck jones": ["Chuck Jones", "character animation"],
        "friz freleng": ["Friz Freleng", "musical timing"],
        "bob clampett": ["Bob Clampett", "surreal", "rubber hose"],
        "robert mckimson": ["Robert McKimson"],
    },
    "characters": {
        "porky pig": ["Porky Pig", "Mel Blanc", "stuttering"],
        "bugs bunny": ["Bugs Bunny", "Mel Blanc", "What's up Doc"],
        "daffy duck": ["Daffy Duck", "Mel Blanc"],
        "tweety": ["Tweety Bird", "Sylvester"],
    }
}

CLASSIC_FILM_KNOWLEDGE = {
    "directors": {
        "fritz lang": {
            "tags": ["Fritz Lang", "German Expressionism", "film noir", "auteur"],
            "films": {
                "metropolis": ["sci-fi", "dystopia", "silent film", "1927", "UFA"],
                "scarlet street": ["film noir", "Edward G. Robinson", "Joan Bennett"]
            }
        },
        "alfred hitchcock": {
            "tags": ["Alfred Hitchcock", "Master of Suspense", "thriller", "British"],
            "films": {
                "blackmail": ["first British talkie", "1929", "Anny Ondra"]
            }
        },
        "charlie chaplin": {
            "tags": ["Charlie Chaplin", "silent film", "The Tramp", "slapstick", "comedy"],
        },
        "buster keaton": {
            "tags": ["Buster Keaton", "silent film", "physical comedy", "deadpan"],
        }
    },
    "genres": {
        "horror": ["horror", "classic horror", "Universal Monsters", "gothic"],
        "film noir": ["film noir", "crime", "femme fatale", "shadow", "1940s"],
        "silent": ["silent film", "silent era", "intertitles", "1920s"],
        "musical": ["musical", "song and dance", "Hollywood musical"],
    }
}


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


def extract_year(title: str) -> Optional[int]:
    """Extrahiert Jahr aus Titel wie (1933) oder (1940s)"""
    match = re.search(r'\((\d{4})\)', title)
    if match:
        return int(match.group(1))
    return None


def extract_episode_info(title: str) -> Tuple[Optional[int], Optional[int]]:
    """Extrahiert Episodennummer wie (43/105)"""
    match = re.search(r'\((\d+)/(\d+)\)', title)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def analyze_soundie(title: str) -> List[str]:
    """Generiert spezifische Tags für Soundie-Videos - YouTube Music optimiert!"""
    tags = list(SOUNDIE_KNOWLEDGE["base_tags"])
    
    # YOUTUBE MUSIC TAGS ZUERST - für App-Auffindbarkeit!
    tags.extend(SOUNDIE_KNOWLEDGE["youtube_music_tags"])
    
    title_lower = title.lower().replace("'", "").replace("'", "")  # Handle apostrophes
    
    # Prüfe auf bekannte Performer
    for performer, performer_tags in SOUNDIE_KNOWLEDGE["famous_performers"].items():
        if performer in title_lower:
            tags.extend(performer_tags)
    
    # Prüfe auf bekannte Songs (mit fuzzy matching)
    for song, song_data in SOUNDIE_KNOWLEDGE["songs"].items():
        # Normalize song name for matching
        song_normalized = song.replace("'", "").replace("'", "")
        if song_normalized in title_lower or song in title_lower:
            tags.extend(song_data.get("tags", []))
            if "composers" in song_data:
                tags.extend(song_data["composers"])
            if "performer" in song_data:
                tags.append(song_data["performer"])
    
    # Spezifische Song-Detection basierend auf Titel-Keywords
    if "love" in title_lower and "anything" in title_lower:
        tags.extend(["I Cant Give You Anything But Love", "jazz standard", 
                     "Jimmy McHugh", "Dorothy Fields", "Adelaide Hall"])
    
    if "hollywood" in title_lower and "boogie" in title_lower:
        tags.extend(["Hadda Brooks", "Queen of Boogie", "boogie woogie", 
                     "piano", "R&B", "Modern Records"])
    
    if "beyond" in title_lower and "horizon" in title_lower:
        tags.extend(["Beyond the Blue Horizon", "Jeanette MacDonald", 
                     "Leo Robin", "Great American Songbook"])
    
    if "hawaiian" in title_lower or "hawaii" in title_lower:
        tags.extend(["Hawaiian music", "ukulele", "tropical", "island"])
    
    if "boogie" in title_lower:
        tags.extend(["boogie woogie", "piano boogie", "rhythm"])
    
    # Extrahiere Jahr
    year = extract_year(title)
    if year:
        tags.append(str(year))
        decade = f"{year // 10 * 10}s"
        tags.append(decade)
    
    return tags


def analyze_betty_boop(title: str) -> List[str]:
    """Generiert spezifische Tags für Betty Boop"""
    tags = list(BETTY_BOOP_KNOWLEDGE["base_tags"])
    title_lower = title.lower()
    
    # Episode-Info
    ep_num, total = extract_episode_info(title)
    if ep_num:
        tags.append(f"Episode {ep_num}")
    
    # Jahr
    year = extract_year(title)
    if year:
        tags.append(str(year))
        if year < 1934:
            tags.append("Pre-Code Hollywood")
    
    # Spezielle Episoden
    for episode, special_tags in BETTY_BOOP_KNOWLEDGE["special_episodes"].items():
        if episode in title_lower:
            tags.extend(special_tags)
    
    # Episoden-spezifische Tags aus Titel
    episode_title = re.sub(r'Betty Boop \(\d+/\d+\):\s*', '', title)
    episode_title = re.sub(r'\s*\|.*$', '', episode_title)
    words = episode_title.split()
    for word in words:
        if len(word) > 3 and word.isalpha():
            tags.append(word)
    
    return tags


def analyze_looney_tunes(title: str) -> List[str]:
    """Generiert Tags für Looney Tunes/Porky Pig"""
    tags = list(LOONEY_TUNES_KNOWLEDGE["base_tags"])
    title_lower = title.lower()
    
    # Character detection
    for char, char_tags in LOONEY_TUNES_KNOWLEDGE["characters"].items():
        if char in title_lower:
            tags.extend(char_tags)
    
    # Jahr
    year = extract_year(title)
    if year:
        tags.append(str(year))
        decade = f"{year // 10 * 10}s"
        tags.append(decade)
        if year < 1943:
            tags.append("Golden Age")
    
    return tags


def analyze_classic_film(title: str) -> List[str]:
    """Analysiert klassische Filme"""
    tags = []
    title_lower = title.lower()
    
    # Regisseur-Detection
    for director, data in CLASSIC_FILM_KNOWLEDGE["directors"].items():
        if director in title_lower:
            tags.extend(data["tags"])
            # Prüfe spezifische Filme
            if "films" in data:
                for film, film_tags in data["films"].items():
                    if film in title_lower:
                        tags.extend(film_tags)
    
    # Genre-Detection
    if any(x in title_lower for x in ["zombie", "dracula", "frankenstein", "horror", "phantom"]):
        tags.extend(CLASSIC_FILM_KNOWLEDGE["genres"]["horror"])
    
    if "noir" in title_lower or any(x in title_lower for x in ["murder", "crime", "detective"]):
        tags.extend(CLASSIC_FILM_KNOWLEDGE["genres"]["film noir"])
    
    # Jahr
    year = extract_year(title)
    if year:
        tags.append(str(year))
        if year < 1930:
            tags.extend(CLASSIC_FILM_KNOWLEDGE["genres"]["silent"])
    
    return tags


def generate_smart_tags(video_id: str, title: str, description: str, current_tags: List[str]) -> List[str]:
    """Hauptfunktion: Generiert intelligente, recherchierte Tags"""
    all_tags = []
    title_lower = title.lower()
    
    # 1. Kategorie erkennen und spezifische Tags generieren
    if "soundie" in title_lower:
        all_tags.extend(analyze_soundie(title))
    
    elif "betty boop" in title_lower:
        all_tags.extend(analyze_betty_boop(title))
    
    elif any(x in title_lower for x in ["porky", "looney", "merrie melod"]):
        all_tags.extend(analyze_looney_tunes(title))
    
    elif any(x in title_lower for x in ["chaplin", "keaton", "hitchcock", "fritz lang", "metropolis"]):
        all_tags.extend(analyze_classic_film(title))
    
    # 2. Allgemeine Tags basierend auf Titel
    year = extract_year(title)
    if year:
        all_tags.append(str(year))
        decade = f"{year // 10 * 10}s"
        all_tags.append(decade)
    
    # 3. Technische Tags (immer hinzufügen)
    tech_tags = ["8K", "4K UHD", "restored", "remastered", "AI upscaled", 
                 "best online version", "remAIke", "@remAIke_IT"]
    all_tags.extend(tech_tags)
    
    # 4. Bestehende gute Tags behalten
    all_tags.extend(current_tags)
    
    # 5. Deduplizieren und limitieren
    return limit_tags_500_chars(all_tags)


def limit_tags_500_chars(tags: List[str], min_tags: int = 20, max_tags: int = 30) -> List[str]:
    """Dedupliziert und limitiert auf 500 Zeichen"""
    seen = set()
    result = []
    
    for tag in tags:
        tag = str(tag or "").strip().lstrip("#")
        if not tag or len(tag) < 2:
            continue
        key = tag.casefold()
        if key not in seen:
            seen.add(key)
            result.append(tag)
    
    # Auf 500 Zeichen begrenzen
    kept = []
    for tag in result:
        candidate = kept + [tag]
        if len(",".join(candidate)) <= 500:
            kept = candidate
        if len(kept) >= max_tags:
            break
    
    return kept


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LIVE SEO Optimizer")
    parser.add_argument("--video-id", help="Einzelnes Video optimieren")
    parser.add_argument("--category", choices=["soundie", "betty_boop", "porky", "all"], default="all")
    parser.add_argument("--apply", action="store_true", help="Änderungen anwenden")
    parser.add_argument("--limit", type=int, default=10, help="Max Videos")
    parser.add_argument("--youtube-music", action="store_true", help="YouTube Music optimierte Tags für Soundies")
    parser.add_argument("--all-remaining", action="store_true", help="Alle Videos mit <15 Tags optimieren")
    args = parser.parse_args()
    
    print("=" * 60)
    print("LIVE SEO OPTIMIZER - KI-gestutzte Tag-Optimierung")
    print("=" * 60)
    
    youtube = get_youtube_client()
    
    # Videos laden
    cache = load_json(VIDEOS_CACHE)
    videos = cache.get("videos", [])
    
    # Filtern nach Kategorie
    if args.category == "soundie":
        videos = [v for v in videos if "soundie" in v.get("title", "").lower()]
    elif args.category == "betty_boop":
        videos = [v for v in videos if "betty boop" in v.get("title", "").lower()]
    elif args.category == "porky":
        videos = [v for v in videos if "porky" in v.get("title", "").lower()]
    
    # YouTube Music Modus: NUR Soundies, auch wenn sie schon Tags haben
    if args.youtube_music:
        videos = [v for v in cache.get("videos", []) if "soundie" in v.get("title", "").lower()]
        print(f"[YouTube Music Mode] Alle {len(videos)} Soundies werden für Music App optimiert!")
    # Nur Videos mit wenigen Tags (normal mode)
    elif not args.all_remaining:
        videos = [v for v in videos if len(v.get("tags", [])) < 15]
    else:
        # --all-remaining: alle mit <15 Tags
        videos = [v for v in videos if len(v.get("tags", [])) < 15]
    
    if args.limit:
        videos = videos[:args.limit]
    
    print(f"\n[Analyse] {len(videos)} Videos zu optimieren")
    
    results = []
    
    for i, video in enumerate(videos, 1):
        vid = video.get("id", "")
        title = video.get("title", "")
        desc = video.get("description", "")
        current_tags = video.get("tags", [])
        
        print(f"\n[{i}/{len(videos)}] {title[:50]}...")
        print(f"   Aktuelle Tags: {len(current_tags)}")
        
        # Smart Tags generieren
        new_tags = generate_smart_tags(vid, title, desc, current_tags)
        
        print(f"   Neue Tags: {len(new_tags)}")
        print(f"   Beispiele: {new_tags[:5]}")
        
        result = {
            "id": vid,
            "title": title,
            "old_tags": len(current_tags),
            "new_tags": new_tags,
            "new_count": len(new_tags)
        }
        
        if args.apply:
            try:
                # Video-Snippet holen
                resp = youtube.videos().list(part="snippet", id=vid).execute()
                if resp.get("items"):
                    snippet = resp["items"][0]["snippet"]
                    snippet["tags"] = new_tags
                    
                    youtube.videos().update(
                        part="snippet",
                        body={"id": vid, "snippet": snippet}
                    ).execute()
                    
                    result["status"] = "OK"
                    print(f"   [OK] Tags aktualisiert!")
                else:
                    result["status"] = "NOT_FOUND"
            except HttpError as e:
                if "quotaExceeded" in str(e):
                    print(f"   [STOP] Quota exceeded!")
                    result["status"] = "QUOTA_EXCEEDED"
                    results.append(result)
                    break
                result["status"] = f"ERROR: {e}"
            
            time.sleep(0.5)
        else:
            result["status"] = "DRY-RUN"
        
        results.append(result)
    
    # Report speichern
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "category": args.category,
        "total": len(results),
        "results": results
    }
    save_json(OUT_REPORT, report)
    
    print(f"\n[Report] Gespeichert: {OUT_REPORT}")
    
    if not args.apply:
        print("\n[DRY-RUN] Keine Aenderungen. Mit --apply ausfuehren.")


if __name__ == "__main__":
    main()
