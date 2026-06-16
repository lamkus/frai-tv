#!/usr/bin/env python3
"""
OPTIMAL PLAYLIST STRATEGY
=========================
Minimale Anzahl Playlists, maximale Abdeckung.
Jedes Video in 2-4 relevanten Playlists für maximale Discoverability.

📊 YOUTUBE BEST PRACTICES:
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Wenige, gut gefüllte Playlists > viele leere
2. Mehrfachzuordnung ist GEWOLLT (erhöht Discoverability)
3. Sortierung: Entweder chronologisch ODER beliebtheit
4. Playlist-Beschreibung mit Keywords für SEO
5. Custom Thumbnails für Featured Playlists

🎯 STRATEGIE: 8 HAUPT-PLAYLISTS + 4 SPRACH/THEMEN-PLAYLISTS = 12 MAX
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set

CONFIG_DIR = 'd:/remaike.TV/config'

# ═══════════════════════════════════════════════════════════════════════════
# OPTIMALE PLAYLIST-STRUKTUR
# ═══════════════════════════════════════════════════════════════════════════

OPTIMAL_PLAYLIST_STRUCTURE = {
    # ══════════════════════════════════════════════════════════════════════
    # TIER 1: HAUPTSERIEN (Jede Serie die 10+ Videos hat)
    # ══════════════════════════════════════════════════════════════════════
    'main_series': {
        'betty_boop': {
            'title': '💋 Betty Boop - Jazz Age Collection (1930s) | 8K Restored',
            'emoji': '💋',
            'min_videos': 10,
            'keywords': ['betty boop', 'boop'],
            'description': '''Boop-Oop-a-Doop! 💋

Die ikonische Jazz-Age Queen in atemberaubender 8K Qualität!

🎭 Pre-Code Animation at its finest
🎵 Jazz, Swing & Surrealismus  
👠 Mode-Ikone der 1930er
🎬 Fleischer Studios Meisterwerke

📺 Alle Episoden auf FRai.TV
✨ 8K AI Restored by @remAIke_IT

#BettyBoop #JazzAge #Animation #8K #Fleischer #Vintage''',
        },
        
        'alfred_jodokus_quack': {
            'title': '🦆 Alfred Jodokus Quack - German | Deutsch | 8K Restored',
            'emoji': '🦆',
            'min_videos': 10,
            'keywords': ['alfred', 'quack', 'kwak', 'jodokus'],
            'description': '''Alfred J. Kwak - Die komplette Serie! 🦆

Die beliebte niederländisch-deutsche Zeichentrickserie über eine mutige kleine Ente.

🎭 52 Episoden
🇩🇪 Deutsche Synchronfassung
✨ 8K AI Restored

Themen: Freundschaft, Umwelt, Politik, Toleranz

📺 Alle Folgen auf FRai.TV

#AlfredJKwak #Zeichentrick #80er #90er #Deutsch #Animation''',
        },
        
        'superman_fleischer': {
            'title': '🦸 Superman - Fleischer Studios (1941-1943) | 8K Restored',
            'emoji': '🦸',
            'min_videos': 5,
            'keywords': ['superman', 'fleischer'],
            'description': '''Die LEGENDÄREN Superman-Cartoons! 🦸

Die Fleischer Studios schufen 1941-1943 die wohl schönsten Superman-Animationen aller Zeiten.

✨ 17 Episoden in 8K restauriert
🎬 Oscar-nominierte Animation
💥 Ikonische Action-Sequenzen

Public Domain - Kostenlos genießen!

#Superman #Fleischer #Animation #8K #40s #DCComics''',
        },
        
        'felix_cat': {
            'title': '🐱 Felix the Cat - Silent Era Collection | 8K Restored',
            'emoji': '🐱',
            'min_videos': 5,
            'keywords': ['felix', 'cat'],
            'description': '''Felix the Cat - Der ERSTE Cartoon-Star! 🐱

Aus der Stummfilmära der 1920er Jahre.

✨ Historische Animationen in 8K
🎬 Pat Sullivan Studios
🎭 Pionier der Animation

#FelixTheCat #SilentEra #Animation #8K #Vintage''',
        },
        
        'casper': {
            'title': '👻 Casper the Friendly Ghost | 8K Restored',
            'emoji': '👻',
            'min_videos': 5,
            'keywords': ['casper', 'ghost', 'geist'],
            'description': '''Casper der freundliche Geist! 👻

Famous Studios Collection (1945-1959) in 8K restauriert.

✨ Herzerwärmende Geschichten
🎬 Classic Animation
👶 Perfekt für Kinder

#Casper #Animation #8K #Vintage #FamousStudios''',
        },
        
        'porky_pig': {
            'title': '🐷 Porky Pig - Looney Tunes Collection | 8K Restored',
            'emoji': '🐷',
            'min_videos': 5,
            'keywords': ['porky', 'pig'],
            'description': '''Th-th-that's Porky Pig! 🐷

Warner Bros Classic Cartoons in 8K!

🎭 Looney Tunes & Merrie Melodies
😂 Timeless Comedy
✨ 8K AI Restored

#PorkyPig #LooneyTunes #WB #Animation #8K''',
        },
        
        'popeye': {
            'title': '⚓ Popeye the Sailor | 8K Restored',
            'emoji': '⚓',
            'min_videos': 3,
            'keywords': ['popeye', 'spinach', 'sailor'],
            'description': '''I'm Popeye the Sailor Man! ⚓

Fleischer & Famous Studios Klassiker in 8K!

💪 Spinach-powered Action
🥊 Popeye vs Bluto
💕 Olive Oyl

#Popeye #Fleischer #Animation #8K #Sailor''',
        },
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # TIER 2: THEMEN-PLAYLISTS (Aggregation)
    # ══════════════════════════════════════════════════════════════════════
    'theme_playlists': {
        'classic_cartoons': {
            'title': '🎨 Classic Cartoons | Vintage Animation | 8K Collection',
            'emoji': '🎨',
            'include_all_cartoons': True,
            'description': '''Golden Age of Animation! 🎨

Die schönsten Cartoons aus den 1920er-1950er Jahren:
• Betty Boop
• Popeye  
• Superman
• Felix the Cat
• Casper
• Porky Pig
• Color Classics

Alle restauriert in 8K Qualität!

#Animation #Vintage #8K #Cartoons #GoldenAge''',
        },
        
        'silent_film_era': {
            'title': '🎭 Silent Film Era | 1900-1930 | 8K Restored',
            'emoji': '🎭',
            'keywords': ['silent', 'chaplin', 'keaton', 'stummfilm', '1920', '1910'],
            'description': '''Die Stummfilm-Ära! 🎭

Meisterwerke von:
• Charlie Chaplin
• Buster Keaton
• Georges Méliès
• Frühe Animationen

Ohne Worte - voller Emotionen.

#SilentFilm #Stummfilm #Chaplin #Keaton #8K''',
        },
        
        'horror_classics': {
            'title': '🧛 Horror Classics | Vintage Horror | 8K Restored',
            'emoji': '🧛',
            'keywords': ['nosferatu', 'frankenstein', 'horror', 'häxan', 'caligari'],
            'description': '''Klassischer Horror! 🧛

Die Ursprünge des Horror-Genres:
• Nosferatu (1922)
• Frankenstein (1910)
• Cabinet of Dr. Caligari (1920)
• Häxan (1922)

Grusel aus einer anderen Zeit.

#Horror #Vintage #SilentFilm #8K #Nosferatu''',
        },
        
        'feature_films': {
            'title': '🎬 Feature Films | Public Domain Movies | 8K Restored',
            'emoji': '🎬',
            'duration_min': 3600,  # 60+ minutes
            'description': '''Spielfilme in voller Länge! 🎬

Public Domain Klassiker restauriert in 8K:
• Film Noir
• Silent Cinema
• Sci-Fi Pioniere
• Drama Klassiker

Kostenlos & Legal!

#Movies #PublicDomain #ClassicFilms #8K #Cinema''',
        },
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # TIER 3: SPRACH-PLAYLISTS
    # ══════════════════════════════════════════════════════════════════════
    'language_playlists': {
        'german_classics': {
            'title': '🇩🇪 Deutsche Klassiker | German Animation & Films | 8K',
            'emoji': '🇩🇪',
            'languages': ['de'],
            'description': '''Deutsche Klassiker! 🇩🇪

Zeichentrickserien und Filme auf Deutsch:
• Alfred Jodokus Quack
• Astro Boy (Deutsch)
• Ferdy die Ameise
• Und mehr!

#Deutsch #German #Animation #8K #Kinderserien''',
        },
        
        'kids_friendly': {
            'title': '👶 For Kids | Für Kinder | 8K Cartoon Collection',
            'emoji': '👶',
            'kids_friendly': True,
            'description': '''Perfekt für Kinder! 👶

Altersgerechte Klassiker:
• Casper
• Felix the Cat
• Popeye
• Betty Boop (ausgewählte Episoden)
• Alfred J. Kwak

Sicher & familienfreundlich!

#ForKids #FürKinder #Animation #8K #Family''',
        },
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # TIER 4: SPECIAL COLLECTIONS
    # ══════════════════════════════════════════════════════════════════════
    'special_collections': {
        'best_of_all': {
            'title': '⭐ Best of @remAIke_IT | Top Picks | 8K Showreel',
            'emoji': '⭐',
            'criteria': 'top_viewed',
            'max_videos': 50,
            'description': '''Die BESTEN Videos! ⭐

Unsere beliebtesten Uploads:
• Meistgesehene Videos
• Höchste Bewertungen
• Fan-Favoriten

Das Beste vom Besten in 8K!

#BestOf #TopPicks #8K #Restored''',
        },
        
        'new_uploads': {
            'title': '🆕 New Uploads | Neueste Videos | Fresh 8K Content',
            'emoji': '🆕',
            'criteria': 'recent',
            'max_videos': 30,
            'auto_update': True,
            'description': '''Frisch hochgeladen! 🆕

Unsere neuesten 8K Restaurierungen.
Regelmäßig aktualisiert!

#NewUploads #Fresh #8K #Latest''',
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# ZUORDNUNGS-LOGIK
# ═══════════════════════════════════════════════════════════════════════════

def get_video_playlists(video: dict) -> List[str]:
    """
    Bestimme alle Playlists für ein Video.
    Ziel: 2-4 relevante Playlists pro Video
    """
    playlists = set()
    
    title = video.get('title', '').lower()
    series = video.get('detected_series') or {}
    series_id = series.get('series_id', '') if series else ''
    language = video.get('language', 'en')
    duration = video.get('durationSeconds', 0)
    content_type = video.get('content_type', '')
    
    # 1. HAUPTSERIE (wenn erkannt)
    if series_id:
        series_map = {
            'betty_boop': 'betty_boop',
            'alfred_jodokus_quack': 'alfred_jodokus_quack',
            'superman': 'superman_fleischer',
            'felix_cat': 'felix_cat',
            'casper': 'casper',
            'porky_pig': 'porky_pig',
            'popeye': 'popeye',
            'looney_tunes': 'porky_pig',  # Zusammenfassen
            'astro_boy': 'german_classics',
            'ferdy_die_ameise': 'german_classics',
        }
        if series_id in series_map:
            playlists.add(f"main:{series_map[series_id]}")
    
    # 2. THEMEN-PLAYLIST
    # Alle Cartoons → classic_cartoons
    cartoon_keywords = ['cartoon', 'animation', 'betty', 'popeye', 'felix', 
                       'casper', 'porky', 'looney', 'color classic', 'fleischer']
    if any(kw in title for kw in cartoon_keywords) or content_type == 'cartoon_series':
        playlists.add('theme:classic_cartoons')
    
    # Silent Films
    silent_keywords = ['silent', 'chaplin', 'keaton', 'méliès', '1920', '1910', 
                       'stummfilm', 'nemo', '1922', '1919']
    if any(kw in title for kw in silent_keywords) or duration > 600 and 'cartoon' not in title.lower():
        # Prüfe Jahr im Titel
        import re
        year_match = re.search(r'\(1[89]\d{2}\)', title)
        if year_match:
            year = int(year_match.group()[1:5])
            if year < 1930:
                playlists.add('theme:silent_film_era')
    
    # Horror
    horror_keywords = ['nosferatu', 'frankenstein', 'horror', 'häxan', 'caligari', 
                       'dracula', 'monster', 'witch']
    if any(kw in title for kw in horror_keywords):
        playlists.add('theme:horror_classics')
    
    # Feature Films (60+ min)
    if duration >= 3600:
        playlists.add('theme:feature_films')
    
    # 3. SPRACH-PLAYLISTS
    if language == 'de' or 'deutsch' in title or 'german' in title:
        playlists.add('lang:german_classics')
    
    # 4. KIDS-FRIENDLY
    kids_safe_series = ['casper', 'felix', 'popeye', 'color_classics', 
                        'alfred_jodokus_quack', 'astro_boy', 'ferdy_die_ameise']
    if series_id in kids_safe_series:
        playlists.add('special:kids_friendly')
    
    # Fallback: Mindestens classic_cartoons für kurze Animationen
    if len(playlists) == 0 and duration < 1200 and duration > 60:
        playlists.add('theme:classic_cartoons')
    
    return list(playlists)


def generate_playlist_assignments(analysis_path: str = None):
    """Generate optimal playlist assignments for all videos"""
    if analysis_path is None:
        analysis_path = os.path.join(CONFIG_DIR, 'complete_channel_analysis.json')
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    
    # Track assignments
    playlist_videos = defaultdict(list)
    video_playlist_count = {}
    
    for video in videos:
        video_id = video['id']
        title = video.get('title', '')
        
        assigned_playlists = get_video_playlists(video)
        video_playlist_count[video_id] = len(assigned_playlists)
        
        for playlist in assigned_playlists:
            playlist_videos[playlist].append({
                'id': video_id,
                'title': title[:60],
            })
    
    # Statistics
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_videos': len(videos),
        'playlist_summary': {},
        'assignments': dict(playlist_videos),
        'statistics': {
            'videos_in_0_playlists': sum(1 for c in video_playlist_count.values() if c == 0),
            'videos_in_1_playlist': sum(1 for c in video_playlist_count.values() if c == 1),
            'videos_in_2_playlists': sum(1 for c in video_playlist_count.values() if c == 2),
            'videos_in_3_playlists': sum(1 for c in video_playlist_count.values() if c == 3),
            'videos_in_4plus_playlists': sum(1 for c in video_playlist_count.values() if c >= 4),
        }
    }
    
    for playlist, vids in playlist_videos.items():
        results['playlist_summary'][playlist] = len(vids)
    
    # Save results
    output_path = os.path.join(CONFIG_DIR, 'optimal_playlist_assignments.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("OPTIMAL PLAYLIST STRATEGY - ANALYSIS")
    print("="*60)
    print(f"\nTotal Videos: {len(videos)}")
    print(f"\nPlaylist Coverage:")
    for playlist, count in sorted(results['playlist_summary'].items(), key=lambda x: -x[1]):
        print(f"  {playlist}: {count} videos")
    
    print(f"\nVideo Distribution:")
    print(f"  In 0 playlists: {results['statistics']['videos_in_0_playlists']} ⚠️")
    print(f"  In 1 playlist:  {results['statistics']['videos_in_1_playlist']}")
    print(f"  In 2 playlists: {results['statistics']['videos_in_2_playlists']} ✓")
    print(f"  In 3 playlists: {results['statistics']['videos_in_3_playlists']} ✓")
    print(f"  In 4+ playlists: {results['statistics']['videos_in_4plus_playlists']} ✓")
    
    print(f"\nOutput saved to: {output_path}")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# OPTIMALE PLAYLIST-EMPFEHLUNG (12 Playlists gesamt)
# ═══════════════════════════════════════════════════════════════════════════

RECOMMENDED_PLAYLISTS = """
╔══════════════════════════════════════════════════════════════════════════╗
║  EMPFOHLENE PLAYLIST-STRUKTUR FÜR remAIke_IT (12 Playlists)              ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  🏆 HAUPTSERIEN (7 Playlists)                                           ║
║  ─────────────────────────────────────────────────────────────────────   ║
║  1. 💋 Betty Boop Collection          ~60 videos                        ║
║  2. 🦆 Alfred J. Quack (Deutsch)      ~32 videos                        ║
║  3. 🦸 Superman Fleischer             ~15 videos                        ║
║  4. 🐱 Felix the Cat                  ~13 videos                        ║
║  5. 👻 Casper Collection               ~9 videos                        ║
║  6. 🐷 Porky Pig & Looney Tunes       ~20 videos                        ║
║  7. ⚓ Popeye Collection                ~4 videos                        ║
║                                                                          ║
║  🎨 THEMEN-SAMMLUNGEN (3 Playlists)                                     ║
║  ─────────────────────────────────────────────────────────────────────   ║
║  8. 🎭 Silent Film Era                ~20 videos                        ║
║  9. 🎬 Feature Films (60+ min)        ~15 videos                        ║
║  10. 🧛 Horror Classics                ~5 videos                        ║
║                                                                          ║
║  🌍 SPRACHE & ZIELGRUPPE (2 Playlists)                                  ║
║  ─────────────────────────────────────────────────────────────────────   ║
║  11. 🇩🇪 Deutsche Klassiker           ~40 videos                        ║
║  12. 👶 For Kids / Kinderfreundlich   ~80 videos                        ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  📊 ZIEL: Jedes Video in 2-4 Playlists für maximale Discoverability     ║
╚══════════════════════════════════════════════════════════════════════════╝
"""


if __name__ == '__main__':
    print(RECOMMENDED_PLAYLISTS)
    results = generate_playlist_assignments()
