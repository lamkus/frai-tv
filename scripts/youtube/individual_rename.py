#!/usr/bin/env python3
"""
Individueller Rename-Plan - Manuell kuratierte Titel-Korrekturen

Jeder Titel wird EINZELN geprüft und korrekt formatiert.
Format-Ziel: [Content] ([Jahr]) | 8K HQ | @remAIke_IT
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import sys

# Manuell kuratierte Fixes - jeder Titel individuell geprüft
RENAME_PLAN = [
    # === Format: (video_id, neuer_titel) ===
    
    # Marihuana - Titel kürzen wegen Multilingual
    ("CSLfwklQq9s", "Marihuana (1936) | 8K HQ | @remAIke_IT"),
    
    # Livestream
    ("wAkUnHRxwT8", "Livestream von remAIke_IT | 8K HQ | @remAIke_IT"),
    
    # Alfred J. Kwak - Deutsch/Englisch Trailer
    ("w5Yyyp0H6vo", "Alfred J. Kwak / Quack – Deutsche Zeichentrickserie Trailer | 8K HQ | @remAIke_IT"),
    
    # BraveStarr - 4K HQ entfernen, nur 8K HQ
    ("XU7yM4H5vrY", "BraveStarr: Das Musikfestival (1/65) | Deutsch | 8K HQ | @remAIke_IT"),
    
    # Teaserama Short
    ("YHlhhiAfxEA", "Teaserama (1955): Tempest Storm + Betty Page | 8K HQ | @remAIke_IT"),
    
    # Teaserama Full + Branding fix
    ("Fjb-aAUetX0", "Teaserama (1955) | Burlesque: Betty Page, Tempest Storm | 8K HQ | @remAIke_IT"),
    
    # Betty Boop for President - Titel korrigieren
    ("nqynuh9a79c", "Betty Boop for President (1932) | 8K HQ | @remAIke_IT"),
    
    # Looney Tunes - einfache Fixes
    ("hOZQjNBV5R0", "Pagan Moon (1932) | 8K HQ | @remAIke_IT"),
    ("MKSFnveRc7c", "Battling Bosko (1932) | 8K HQ | @remAIke_IT"),
    ("1qMv827zxW0", "Ain't Nature Grand (1931) | 8K HQ | @remAIke_IT"),
    ("EZxg1D958mo", "A Corny Concerto (1943) | 8K HQ | @remAIke_IT"),
    ("2nT_DjkOWn8", "Pigs In A Polka (1943) | 8K HQ | @remAIke_IT"),
    
    # Popeye Marathon
    ("3gzbxznJ_PM", "Popeye Marathon (4h 41m) | Fleischer Studios | 8K HQ | @remAIke_IT"),
    
    # Pearl Harbor Documentary
    ("EasEhYlorqQ", "Pearl Harbor Documentary (1942) | 8K HQ | @remAIke_IT"),
    
    # Experiments in Revival
    ("D1WD7sS637k", "Experiments in the Revival of Organisms (1940) | 8K HQ | @remAIke_IT"),
    
    # Kirby Abridged
    ("Qm3K0-XL46Q", "Kirby Abridged Collection | Funny Anime Parody | 8K HQ | @remAIke_IT"),
    
    # Lucy Show
    ("AyjJbgijx68", "Lucy Meets John Wayne (1966) | The Lucy Show S5E10 | 8K HQ | @remAIke_IT"),
    
    # Silent Films
    ("gMpONbJ3-9U", "The Bee and the Rose (1908) | Segundo de Chomón | 8K HQ | @remAIke_IT"),
    ("Nzi6aRKDoEs", "Nosferatu (1922) | Silent Horror Classic | 8K HQ | @remAIke_IT"),
    ("_3Z1GTYFUAM", "Buster Keaton: Convict 13 (1920) | Silent Comedy | 8K HQ | @remAIke_IT"),
    ("T8AnrW3H5i8", "Little Nemo (1911) | Winsor McCay Animation | 8K HQ | @remAIke_IT"),
    ("mybF4jPjl64", "Buster Keaton: My Wife's Relations (1922) | 8K HQ | @remAIke_IT"),
    ("hPQN992PMUY", "Frankenstein (1910) | Edison Studios | 8K HQ | @remAIke_IT"),
    
    # Archive.org Videos
    ("j4r3bPPQza0", "Commodore 64 Vintage Computer Documentary | 8K HQ | @remAIke_IT"),
    ("EhZdQ74_sCM", "Prelinger: Children Make Movies | 8K HQ | @remAIke_IT"),
    ("EMnokZOLpzU", "The Grim Game (1919) | Houdini Silent Thriller | 8K HQ | @remAIke_IT"),
    
    # Cartoons
    ("ExbniPRgH70", "The Candid Candidate (1937) | Cartoon Classic | 8K HQ | @remAIke_IT"),
    ("PSdJJaxI4gM", "Charade (1953) | Vintage Mystery | 8K HQ | @remAIke_IT"),
    ("5WVJHELSD7A", "The Cabinet of Dr. Caligari (1920) | Silent Horror | 8K HQ | @remAIke_IT"),
    ("9_rhugQFh8w", "The Big Game Hunter | Classic Animation | 8K HQ | @remAIke_IT"),
    ("tk3DHvp9CFs", "The Astronomer's Dream (1898) | Georges Méliès | 8K HQ | @remAIke_IT"),
    
    # Alte @reAImastered Branding - komplett neu
    ("WWdC0Rq4cQQ", "Krazy Kat: Keeping Up (1916) | 8K HQ | @remAIke_IT"),
    ("3NagSoFaAwI", "Airship Destroyed (1909) | Early Sci-Fi | 8K HQ | @remAIke_IT"),
    ("-623U3tgryM", "Mel-O-Toons: Peter and the Wolf (1960) | 8K HQ | @remAIke_IT"),
    ("qZU5lVJMkoM", "Felix Minds the Kid (1922) | Felix the Cat | 8K HQ | @remAIke_IT"),
    ("d8Ak1R_eOlY", "White Zombie (1932) | Horror Classic | 8K HQ | @remAIke_IT"),
    ("0pBFESQ-FmA", "Little Nemo in Slumberland (1911) | Winsor McCay | 8K HQ | @remAIke_IT"),
    
    # Tokyo Jokio fix
    ("M0-tJK4H3lo", "Tokyo Jokio (1943) | Merrie Melodies WWII | 8K HQ | @remAIke_IT"),
]

def main():
    with open('config/youtube_oauth.json', encoding='utf-8') as f:
        oauth = json.load(f)
    
    creds = Credentials(
        token=oauth['token'],
        refresh_token=oauth['refresh_token'],
        token_uri=oauth['token_uri'],
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret'],
    )
    youtube = build('youtube', 'v3', credentials=creds)
    
    print("🔧 INDIVIDUELLER RENAME-PLAN")
    print("=" * 70)
    print(f"Videos zu fixen: {len(RENAME_PLAN)}")
    print()
    
    # Zeige Plan
    for vid, new_title in RENAME_PLAN:
        print(f"📺 {vid}")
        print(f"   → {new_title}")
        print(f"   ({len(new_title)} Zeichen)")
        print()
    
    if '--apply' not in sys.argv:
        print("=" * 70)
        print("⚠️  DRY RUN - Keine Änderungen!")
        print("    Starte mit --apply um anzuwenden")
        return
    
    print("=" * 70)
    print("🚀 WENDE ÄNDERUNGEN AN...")
    print()
    
    success = 0
    failed = []
    
    for vid, new_title in RENAME_PLAN:
        try:
            # Hole aktuelle Video-Daten
            result = youtube.videos().list(part='snippet', id=vid).execute()
            if not result['items']:
                print(f"❌ {vid}: Nicht gefunden")
                failed.append(vid)
                continue
            
            snippet = result['items'][0]['snippet']
            old_title = snippet['title']
            
            # Update
            youtube.videos().update(
                part='snippet',
                body={
                    'id': vid,
                    'snippet': {
                        'title': new_title,
                        'description': snippet['description'],
                        'tags': snippet.get('tags', []),
                        'categoryId': snippet['categoryId']
                    }
                }
            ).execute()
            
            print(f"✅ {vid}")
            print(f"   ALT: {old_title[:60]}...")
            print(f"   NEU: {new_title}")
            success += 1
            
        except Exception as e:
            print(f"❌ {vid}: {str(e)[:60]}")
            failed.append(vid)
    
    print()
    print("=" * 70)
    print(f"✅ Erfolgreich: {success}")
    print(f"❌ Fehlgeschlagen: {len(failed)}")
    
    # Speichere Ergebnis
    result_data = {
        'date': datetime.now().isoformat(),
        'success': success,
        'failed': failed,
        'total': len(RENAME_PLAN)
    }
    
    with open('config/individual_rename_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\n💾 Ergebnis: config/individual_rename_result.json")

if __name__ == '__main__':
    main()
