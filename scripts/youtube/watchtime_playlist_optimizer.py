#!/usr/bin/env python3
"""
WATCHTIME PLAYLIST OPTIMIZER
============================
Maximiere Watch Time durch intelligente Playlist-Struktur.

📊 YOUTUBE WATCHTIME FAKTOREN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. AUTOPLAY: Nächstes Video muss "passen" → Viewer bleibt
2. REIHENFOLGE: Chronologisch bei Serien (Episode 1→2→3)
3. LÄNGE: Ähnliche Längen gruppieren (7min + 7min, nicht 7min + 90min)
4. THEMA: Verwandte Inhalte halten Zuschauer im Binge-Modus
5. HOOK: Beste Videos am Anfang → Algorithmus pusht Playlist

🎯 STRATEGIE:
- Serien: Chronologisch sortiert
- Compilations: Nach Beliebtheit (Views) sortiert  
- Mixed: Nach Thema clustern, dann nach Länge

QUOTA: Nur READ via Public API
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

CONFIG_DIR = 'd:/remaike.TV/config'

# Public API key must come from environment (do not hardcode secrets)
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise RuntimeError('Missing env var: YOUTUBE_API_KEY')
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

# ═══════════════════════════════════════════════════════════════════════════
# WATCHTIME RULES
# ═══════════════════════════════════════════════════════════════════════════

WATCHTIME_RULES = {
    # Serien-Playlists: Chronologische Reihenfolge
    'series': {
        'sort': 'chronological',  # Nach Episode-Nummer
        'strategy': 'binge',       # Alle Folgen hintereinander
        'min_videos': 3,           # Mindestens 3 für Playlist-Effekt
    },
    
    # Themen-Playlists: Nach Engagement sortieren
    'theme': {
        'sort': 'engagement',      # Views + Likes
        'strategy': 'hook_first',  # Beste Videos zuerst
        'group_by_length': True,   # Ähnliche Längen zusammen
    },
    
    # Kids: Kürzere Videos zuerst, dann länger werden
    'kids': {
        'sort': 'duration_asc',    # Kurz → Lang (Aufbau)
        'max_duration': 1800,      # Max 30 min pro Video
        'strategy': 'gradual',     # Langsam steigern
    },
    
    # Feature Films: Nach Beliebtheit
    'features': {
        'sort': 'views_desc',
        'strategy': 'popular_first',
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# EPISODE NUMBER EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

def extract_episode_number(title: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract episode number and total from title like (15/52)"""
    # Pattern: (15/52) oder (1/17)
    match = re.search(r'\((\d+)/(\d+)\)', title)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Pattern: Episode 15 oder Ep. 15
    match = re.search(r'(?:Episode|Ep\.?|Folge)\s*(\d+)', title, re.IGNORECASE)
    if match:
        return int(match.group(1)), None
    
    # Pattern: S01E15
    match = re.search(r'S\d+E(\d+)', title, re.IGNORECASE)
    if match:
        return int(match.group(1)), None
    
    return None, None


def extract_year(title: str) -> Optional[int]:
    """Extract year from title like (1932) or (1941)"""
    match = re.search(r'\((\d{4})\)', title)
    if match:
        year = int(match.group(1))
        if 1890 <= year <= 2030:
            return year
    return None

# ═══════════════════════════════════════════════════════════════════════════
# SORTING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def sort_chronological(videos: List[dict]) -> List[dict]:
    """Sort by episode number (for series)"""
    def sort_key(v):
        ep_num, _ = extract_episode_number(v.get('title', ''))
        year = extract_year(v.get('title', ''))
        # Episode number first, then year, then title
        return (ep_num or 999, year or 9999, v.get('title', ''))
    
    return sorted(videos, key=sort_key)


def sort_by_engagement(videos: List[dict]) -> List[dict]:
    """Sort by views + likes (engagement score)"""
    def engagement_score(v):
        views = int(v.get('viewCount', 0) or 0)
        likes = int(v.get('likeCount', 0) or 0)
        # Views + Likes*10 (likes are more valuable)
        return views + (likes * 10)
    
    return sorted(videos, key=engagement_score, reverse=True)


def sort_by_duration(videos: List[dict], ascending: bool = True) -> List[dict]:
    """Sort by video duration"""
    def duration_key(v):
        return v.get('durationSeconds', 0) or 0
    
    return sorted(videos, key=duration_key, reverse=not ascending)


def sort_by_views(videos: List[dict], descending: bool = True) -> List[dict]:
    """Sort by view count"""
    def views_key(v):
        return int(v.get('viewCount', 0) or 0)
    
    return sorted(videos, key=views_key, reverse=descending)


def sort_by_year(videos: List[dict]) -> List[dict]:
    """Sort by release year (for vintage content)"""
    def year_key(v):
        year = extract_year(v.get('title', ''))
        return year or 9999
    
    return sorted(videos, key=year_key)

# ═══════════════════════════════════════════════════════════════════════════
# WATCHTIME PLAYLIST DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

WATCHTIME_PLAYLISTS = {
    # ══════════════════════════════════════════════════════════════════════
    # SERIEN-PLAYLISTS (Chronologisch für Binge-Watching)
    # ══════════════════════════════════════════════════════════════════════
    
    'betty_boop_chronological': {
        'title': '💋 Betty Boop - Complete Series (1930-1939) | 8K Restored',
        'description': '''Boop-Oop-a-Doop! 💋

Die KOMPLETTE Betty Boop Serie in chronologischer Reihenfolge!
Perfekt zum Durchschauen - von Episode 1 bis 110.

🎬 110 Episoden | 1930-1939
✨ 8K AI Restored
🎭 Fleischer Studios

▶️ Autoplay an - Binge Betty Boop!

#BettyBoop #BingeWatch #Animation #8K''',
        'filter': {'series_id': 'betty_boop'},
        'sort': 'chronological',
        'min_videos': 10,
    },
    
    'alfred_quack_chronological': {
        'title': '🦆 Alfred J. Quack - Alle Folgen (1/52 - 52/52) | Deutsch | 8K',
        'description': '''Alfred Jodokus Quack - Die KOMPLETTE Serie! 🦆

Alle 52 Folgen in der richtigen Reihenfolge.
Perfekt zum Durchschauen!

🎬 52 Episoden
🇩🇪 Deutsche Synchronfassung
✨ 8K Restored

▶️ Autoplay an und los geht's!

#AlfredJKwak #Zeichentrick #Deutsch #BingeWatch''',
        'filter': {'series_id': 'alfred_jodokus_quack'},
        'sort': 'chronological',
        'min_videos': 10,
    },
    
    'superman_chronological': {
        'title': '🦸 Superman Fleischer - All 17 Episodes (1941-1943) | 8K',
        'description': '''Die legendären Superman Cartoons! 🦸

Alle 17 Episoden in Produktionsreihenfolge.
Die schönste Superman-Animation aller Zeiten.

🎬 17 Episoden | 1941-1943  
✨ 8K Restored
🎭 Fleischer Studios

#Superman #Fleischer #Animation #8K''',
        'filter': {'series_id': 'superman'},
        'sort': 'chronological',
        'min_videos': 5,
    },
    
    'casper_chronological': {
        'title': '👻 Casper - Complete Collection | 8K Restored',
        'description': '''Casper der freundliche Geist! 👻

Alle Casper Cartoons chronologisch sortiert.
Famous Studios Collection (1945-1959).

✨ 8K Restored
🎬 Chronologische Reihenfolge

#Casper #Animation #8K #BingeWatch''',
        'filter': {'series_id': 'casper'},
        'sort': 'chronological',
        'min_videos': 5,
    },
    
    'felix_chronological': {
        'title': '🐱 Felix the Cat - Silent Era Collection | 8K Restored',
        'description': '''Felix the Cat - Chronologisch! 🐱

Die Stummfilm-Klassiker in Reihenfolge.
Von den 1920er Jahren.

✨ 8K Restored

#FelixTheCat #SilentFilm #Animation''',
        'filter': {'series_id': 'felix_cat'},
        'sort': 'chronological',
        'min_videos': 5,
    },
    
    'porky_looney': {
        'title': '🐷 Porky Pig & Looney Tunes | 8K Restored',
        'description': '''Th-th-that's all folks! 🐷

Porky Pig und Looney Tunes Klassiker.
Warner Bros Golden Age.

✨ 8K Restored
🎬 Chronologisch sortiert

#PorkyPig #LooneyTunes #WB #Animation''',
        'filter': {'series_id': ['porky_pig', 'looney_tunes']},
        'sort': 'chronological',
        'min_videos': 5,
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # THEMEN-PLAYLISTS (Nach Engagement sortiert)
    # ══════════════════════════════════════════════════════════════════════
    
    'best_cartoons': {
        'title': '⭐ Best Classic Cartoons | Most Popular | 8K Restored',
        'description': '''Die BELIEBTESTEN Cartoons! ⭐

Nach Views und Likes sortiert.
Die besten Golden Age Animationen.

✨ 8K Restored
📊 Sortiert nach Beliebtheit

#BestOf #Animation #8K #MostPopular''',
        'filter': {'content_type': 'cartoon'},
        'sort': 'engagement',
        'max_videos': 50,
    },
    
    'silent_era_classics': {
        'title': '🎭 Silent Film Era - Best First | 8K Restored',
        'description': '''Stummfilm-Klassiker! 🎭

Sortiert nach Beliebtheit - die besten zuerst.
Chaplin, Keaton, Méliès und mehr.

✨ 8K Restored

#SilentFilm #Stummfilm #ClassicCinema''',
        'filter': {'content_type': 'silent_film'},
        'sort': 'engagement',
        'max_videos': 30,
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # MARATHON-PLAYLISTS (Längste Watch Time)
    # ══════════════════════════════════════════════════════════════════════
    
    'cartoon_marathon': {
        'title': '🎬 Cartoon Marathon | 4+ Hours | 8K Restored',
        'description': '''CARTOON MARATHON! 🎬

Über 4 Stunden Cartoon-Spaß am Stück!
Perfekt für gemütliche Abende.

✨ 8K Restored
⏱️ 4+ Stunden Content

#Marathon #Cartoons #BingeWatch''',
        'filter': {'content_type': 'cartoon'},
        'sort': 'engagement',
        'target_duration': 14400,  # 4 hours in seconds
    },
    
    'feature_films_marathon': {
        'title': '🎬 Classic Films Marathon | Full Movies | 8K',
        'description': '''Spielfilm-Marathon! 🎬

Komplette Filme am Stück.
Public Domain Klassiker.

✨ 8K Restored

#Movies #Marathon #ClassicFilms''',
        'filter': {'min_duration': 3600},  # 60+ min
        'sort': 'engagement',
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # KIDS-PLAYLIST (Aufbauend: kurz → länger)
    # ══════════════════════════════════════════════════════════════════════
    
    'kids_watchtime': {
        'title': '👶 For Kids - Easy Start | 8K Cartoons',
        'description': '''Perfekt für Kinder! 👶

Beginnt mit kürzeren Cartoons, 
wird langsam länger.
Ideal für kleine Aufmerksamkeitsspannen.

✨ 8K Restored
🎬 Kinderfreundlich sortiert

#ForKids #FürKinder #Cartoons''',
        'filter': {'kids_friendly': True},
        'sort': 'duration_asc',
        'max_duration': 1800,  # Max 30 min videos
    },
    
    # ══════════════════════════════════════════════════════════════════════
    # DEUTSCHE KLASSIKER (Chronologisch)
    # ══════════════════════════════════════════════════════════════════════
    
    'german_series_complete': {
        'title': '🇩🇪 Deutsche Zeichentrickserien | Komplett | 8K',
        'description': '''Deutsche Klassiker zum Durchschauen! 🇩🇪

• Alfred J. Quack (52 Folgen)
• Astro Boy (Deutsch)
• Ferdy die Ameise

✨ 8K Restored
🎬 Chronologisch sortiert

#Deutsch #German #Zeichentrick''',
        'filter': {'language': 'de'},
        'sort': 'chronological',
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# OPTIMIZER LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def filter_videos(videos: List[dict], filter_config: dict) -> List[dict]:
    """Filter videos based on criteria"""
    result = videos
    
    # Series ID filter
    if 'series_id' in filter_config:
        series_ids = filter_config['series_id']
        if isinstance(series_ids, str):
            series_ids = [series_ids]
        result = [v for v in result if (v.get('detected_series') or {}).get('series_id') in series_ids]
    
    # Content type filter
    if 'content_type' in filter_config:
        ct = filter_config['content_type']
        result = [v for v in result if ct in (v.get('content_type', '') or '').lower()]
    
    # Language filter
    if 'language' in filter_config:
        lang = filter_config['language']
        result = [v for v in result if v.get('language') == lang]
    
    # Min duration filter
    if 'min_duration' in filter_config:
        min_dur = filter_config['min_duration']
        result = [v for v in result if (v.get('durationSeconds', 0) or 0) >= min_dur]
    
    # Max duration filter (for kids)
    if 'max_duration' in filter_config:
        max_dur = filter_config['max_duration']
        result = [v for v in result if (v.get('durationSeconds', 0) or 0) <= max_dur]
    
    # Kids friendly filter
    if filter_config.get('kids_friendly'):
        kids_series = ['casper', 'felix_cat', 'popeye', 'color_classics', 
                       'alfred_jodokus_quack', 'astro_boy', 'ferdy_die_ameise']
        result = [v for v in result if (v.get('detected_series') or {}).get('series_id') in kids_series]
    
    return result


def sort_videos(videos: List[dict], sort_type: str) -> List[dict]:
    """Sort videos based on strategy"""
    if sort_type == 'chronological':
        return sort_chronological(videos)
    elif sort_type == 'engagement':
        return sort_by_engagement(videos)
    elif sort_type == 'duration_asc':
        return sort_by_duration(videos, ascending=True)
    elif sort_type == 'duration_desc':
        return sort_by_duration(videos, ascending=False)
    elif sort_type == 'views_desc':
        return sort_by_views(videos, descending=True)
    elif sort_type == 'year':
        return sort_by_year(videos)
    else:
        return videos


def calculate_playlist_watchtime(videos: List[dict]) -> int:
    """Calculate total potential watch time in seconds"""
    return sum(v.get('durationSeconds', 0) or 0 for v in videos)


def optimize_for_target_duration(videos: List[dict], target_seconds: int) -> List[dict]:
    """Select videos to reach target duration"""
    result = []
    total = 0
    
    for v in videos:
        duration = v.get('durationSeconds', 0) or 0
        if total + duration <= target_seconds * 1.1:  # Allow 10% overflow
            result.append(v)
            total += duration
        if total >= target_seconds:
            break
    
    return result


def generate_watchtime_playlists(analysis_path: str = None):
    """Generate watchtime-optimized playlist configurations"""
    if analysis_path is None:
        analysis_path = os.path.join(CONFIG_DIR, 'complete_channel_analysis.json')
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_videos = data.get('videos', [])
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'playlists': {},
        'summary': {
            'total_videos': len(all_videos),
            'total_duration_hours': calculate_playlist_watchtime(all_videos) / 3600,
        }
    }
    
    print("\n" + "═"*65)
    print("  🎯 WATCHTIME PLAYLIST OPTIMIZER")
    print("═"*65)
    print(f"\n📊 Analysiere {len(all_videos)} Videos...\n")
    
    for playlist_id, config in WATCHTIME_PLAYLISTS.items():
        print(f"\n{'─'*60}")
        print(f"📋 {config['title'][:50]}...")
        
        # Filter
        filtered = filter_videos(all_videos, config.get('filter', {}))
        print(f"   Nach Filter: {len(filtered)} Videos")
        
        if len(filtered) < config.get('min_videos', 3):
            print(f"   ⚠️ Zu wenige Videos (min: {config.get('min_videos', 3)})")
            continue
        
        # Sort
        sorted_videos = sort_videos(filtered, config.get('sort', 'chronological'))
        
        # Target duration (for marathons)
        if 'target_duration' in config:
            sorted_videos = optimize_for_target_duration(
                sorted_videos, 
                config['target_duration']
            )
            print(f"   Target Duration: {config['target_duration']//3600}h")
        
        # Max videos limit
        if 'max_videos' in config:
            sorted_videos = sorted_videos[:config['max_videos']]
        
        # Calculate stats
        total_duration = calculate_playlist_watchtime(sorted_videos)
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        
        print(f"   ✅ {len(sorted_videos)} Videos")
        print(f"   ⏱️ Gesamtlänge: {hours}h {minutes}m")
        
        # Show first 5 videos in order
        print(f"   📺 Reihenfolge (erste 5):")
        for i, v in enumerate(sorted_videos[:5], 1):
            title = v.get('title', '')[:40]
            ep, _ = extract_episode_number(v.get('title', ''))
            ep_str = f"[Ep.{ep}]" if ep else ""
            dur = (v.get('durationSeconds', 0) or 0) // 60
            print(f"      {i}. {ep_str} {title}... ({dur}min)")
        
        if len(sorted_videos) > 5:
            print(f"      ... +{len(sorted_videos)-5} weitere")
        
        # Store result
        results['playlists'][playlist_id] = {
            'title': config['title'],
            'description': config['description'],
            'video_count': len(sorted_videos),
            'total_duration_seconds': total_duration,
            'total_duration_formatted': f"{hours}h {minutes}m",
            'sort_strategy': config.get('sort'),
            'video_ids': [v['id'] for v in sorted_videos],
            'video_order': [
                {
                    'position': i+1,
                    'id': v['id'],
                    'title': v.get('title', '')[:60],
                    'duration': v.get('durationSeconds', 0),
                }
                for i, v in enumerate(sorted_videos)
            ],
        }
    
    # Summary
    print("\n" + "═"*65)
    print("  📊 ZUSAMMENFASSUNG")
    print("═"*65)
    
    total_watchtime = sum(
        p['total_duration_seconds'] 
        for p in results['playlists'].values()
    )
    
    print(f"\n   Playlists erstellt: {len(results['playlists'])}")
    print(f"   Potenzielle Watch Time: {total_watchtime // 3600}h {(total_watchtime % 3600)//60}m")
    
    # Top Playlists by duration
    print(f"\n   🏆 Top Playlists nach Watch Time:")
    sorted_playlists = sorted(
        results['playlists'].items(),
        key=lambda x: x[1]['total_duration_seconds'],
        reverse=True
    )[:5]
    
    for pid, pdata in sorted_playlists:
        print(f"      {pdata['title'][:35]}... → {pdata['total_duration_formatted']}")
    
    # Save
    output_path = os.path.join(CONFIG_DIR, 'watchtime_playlists.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n   📄 Output: {output_path}")
    
    return results


if __name__ == '__main__':
    results = generate_watchtime_playlists()
