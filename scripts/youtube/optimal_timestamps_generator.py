#!/usr/bin/env python3
"""
OPTIMAL TIMESTAMPS GENERATOR
============================
Basierend auf Best Practices der erfolgreichsten YouTube-Kanäle für Public Domain Content.

📊 RESEARCH: Top-Performer Timestamp-Strukturen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Die erfolgreichsten Kanäle (100k+ Subs) nutzen:
- Erstes Kapitel IMMER bei 0:00 (Pflicht für YouTube Chapters!)
- Mindestens 3 Timestamps für Chapter-Aktivierung
- Jedes Kapitel mind. 10 Sekunden lang
- Emotionale Labels mit Emojis für höhere CTR
- Beschreibende Titel (nicht nur "Scene 1, Scene 2")

🎯 CTR-OPTIMIERTE TIMESTAMP-PATTERNS
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

CONFIG_DIR = 'd:/remaike.TV/config'

# ═══════════════════════════════════════════════════════════════════════════
# OPTIMALE TIMESTAMP-TEMPLATES (basierend auf Top-Performer-Analyse)
# ═══════════════════════════════════════════════════════════════════════════

OPTIMAL_TEMPLATES = {
    # ──────────────────────────────────────────────────────────────────────
    # DEUTSCHE SERIEN (21-24 Min Episoden)
    # ──────────────────────────────────────────────────────────────────────
    'alfred_jodokus_quack': {
        'duration_range': (1200, 1500),  # 20-25 min
        'description': 'Alfred J. Kwak Episode',
        'timestamps': [
            ('0:00', '🦆 Episode Start'),
            ('0:25', '🎵 Intro Theme'),
            ('1:30', '📖 Story Begins'),
            ('5:00', '🎭 Act I: Setup'),
            ('10:00', '⚡ Act II: Conflict'),
            ('15:00', '🔥 Act III: Climax'),
            ('19:30', '✨ Resolution'),
            ('21:00', '🎵 End Credits'),
        ],
        'dynamic': True,  # Timestamps werden auf tatsächliche Länge skaliert
    },
    
    'astro_boy': {
        'duration_range': (1300, 1500),  # ~23 min
        'description': 'Astro Boy Episode',
        'timestamps': [
            ('0:00', '🤖 Episode Start'),
            ('0:30', '🎵 Opening Theme'),
            ('1:30', '📖 Story Begins'),
            ('6:00', '⚡ Action Sequence'),
            ('12:00', '💥 Main Battle'),
            ('18:00', '🌟 Resolution'),
            ('21:30', '🎵 Ending Theme'),
        ],
        'dynamic': True,
    },
    
    'ferdy_die_ameise': {
        'duration_range': (1400, 1600),  # ~25 min
        'description': 'Ferdy Episode',
        'timestamps': [
            ('0:00', '🐜 Episode Start'),
            ('0:30', '🎵 Intro'),
            ('2:00', '🌿 Adventure Begins'),
            ('8:00', '🎭 Main Plot'),
            ('15:00', '⚡ Climax'),
            ('22:00', '✨ Happy End'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # BETTY BOOP (5-9 Min Cartoons)
    # ──────────────────────────────────────────────────────────────────────
    'betty_boop': {
        'duration_range': (280, 540),  # 4.6-9 min
        'description': 'Betty Boop Cartoon',
        'timestamps': [
            ('0:00', '💋 Cartoon Start'),
            ('0:12', '🎬 Title Card'),
            ('0:30', '🎭 Story Begins'),
            ('2:00', '🎵 Musical Number'),
            ('4:00', '😄 Finale'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # SUPERMAN FLEISCHER (8-10 Min)
    # ──────────────────────────────────────────────────────────────────────
    'superman': {
        'duration_range': (480, 660),  # 8-11 min
        'description': 'Superman Fleischer',
        'timestamps': [
            ('0:00', '🦸 Episode Start'),
            ('0:15', '🎬 Title Card'),
            ('0:45', '📰 Daily Planet Scene'),
            ('2:30', '⚡ Crisis Begins'),
            ('5:00', '💥 Superman in Action'),
            ('7:30', '🏆 Victory'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # FELIX THE CAT (4-8 Min Silent Cartoons)
    # ──────────────────────────────────────────────────────────────────────
    'felix_cat': {
        'duration_range': (200, 540),  # 3.3-9 min
        'description': 'Felix the Cat',
        'timestamps': [
            ('0:00', '🐱 Cartoon Start'),
            ('0:10', '🎬 Title Card'),
            ('0:30', '😺 Felix Appears'),
            ('2:00', '🎭 Adventure'),
            ('4:00', '😸 Happy End'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # CASPER (6-8 Min)
    # ──────────────────────────────────────────────────────────────────────
    'casper': {
        'duration_range': (330, 480),  # 5.5-8 min
        'description': 'Casper Cartoon',
        'timestamps': [
            ('0:00', '👻 Cartoon Start'),
            ('0:15', '🎬 Title Card'),
            ('0:35', '😊 Casper Appears'),
            ('2:00', '🎭 Making Friends'),
            ('4:30', '💕 Happy Ending'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # PORKY PIG / LOONEY TUNES (7-8 Min)
    # ──────────────────────────────────────────────────────────────────────
    'porky_pig': {
        'duration_range': (380, 500),  # 6.3-8.3 min
        'description': 'Porky Pig Cartoon',
        'timestamps': [
            ('0:00', '🐷 Cartoon Start'),
            ('0:12', '🎬 Title Card'),
            ('0:35', '🎭 Th-th-that\'s the Start!'),
            ('2:30', '😂 Comedy Peak'),
            ('5:00', '🎉 Th-th-that\'s All Folks!'),
        ],
        'dynamic': True,
    },
    
    'looney_tunes': {
        'duration_range': (380, 500),
        'description': 'Looney Tunes / Merrie Melodies',
        'timestamps': [
            ('0:00', '🎭 Cartoon Start'),
            ('0:12', '🎬 Title Card'),
            ('0:35', '🎵 Opening Gag'),
            ('2:30', '😂 Comedy Peak'),
            ('5:30', '🎉 That\'s All Folks!'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # POPEYE (7-8 Min)
    # ──────────────────────────────────────────────────────────────────────
    'popeye': {
        'duration_range': (380, 500),
        'description': 'Popeye Cartoon',
        'timestamps': [
            ('0:00', '⚓ Cartoon Start'),
            ('0:12', '🎬 Title Card'),
            ('0:35', '💪 Popeye Theme'),
            ('2:00', '😈 Bluto Appears'),
            ('4:00', '🥬 Spinach Time!'),
            ('5:30', '🏆 Popeye Wins'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # SILENT FILMS / CHAPLIN / KEATON
    # ──────────────────────────────────────────────────────────────────────
    'silent_short': {
        'duration_range': (600, 1800),  # 10-30 min
        'description': 'Silent Comedy Short',
        'timestamps': [
            ('0:00', '🎬 Film Start'),
            ('0:30', '📜 Title Cards'),
            ('2:00', '🎭 Act I'),
            ('8:00', '⚡ Act II'),
            ('15:00', '🎉 Finale'),
        ],
        'dynamic': True,
    },
    
    'chaplin': {
        'duration_range': (600, 5400),  # 10-90 min
        'description': 'Charlie Chaplin',
        'timestamps': [
            ('0:00', '🎩 Film Start'),
            ('0:30', '📜 Opening Credits'),
            ('2:00', '🚶 The Tramp Appears'),
            ('10:00', '😂 Comedy Sequence'),
            ('20:00', '💕 Romantic Scene'),
            ('35:00', '🎭 Dramatic Climax'),
        ],
        'dynamic': True,
    },
    
    'keaton': {
        'duration_range': (600, 5400),
        'description': 'Buster Keaton',
        'timestamps': [
            ('0:00', '😐 Film Start'),
            ('0:30', '📜 Title Cards'),
            ('2:00', '🤸 First Stunt'),
            ('10:00', '💥 Major Stunt Sequence'),
            ('20:00', '🏃 Chase Scene'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # FEATURE FILMS (60-120 Min)
    # ──────────────────────────────────────────────────────────────────────
    'feature_film': {
        'duration_range': (3600, 9000),  # 60-150 min
        'description': 'Feature Film',
        'timestamps': [
            ('0:00', '🎬 Film Start'),
            ('2:00', '📜 Opening Credits'),
            ('10:00', '🎭 Act I: Setup'),
            ('30:00', '⚡ Act II: Rising Action'),
            ('50:00', '🔥 Midpoint'),
            ('70:00', '💥 Act III: Climax'),
            ('85:00', '✨ Resolution'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # HORROR CLASSICS
    # ──────────────────────────────────────────────────────────────────────
    'horror': {
        'duration_range': (3000, 7200),  # 50-120 min
        'description': 'Horror Classic',
        'timestamps': [
            ('0:00', '🎬 Film Start'),
            ('2:00', '📜 Opening'),
            ('10:00', '😰 First Scare'),
            ('25:00', '👻 Monster Reveal'),
            ('45:00', '😱 Terror Peaks'),
            ('60:00', '⚡ Final Confrontation'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # COLOR CLASSICS (FLEISCHER)
    # ──────────────────────────────────────────────────────────────────────
    'color_classics': {
        'duration_range': (400, 600),  # 6.6-10 min
        'description': 'Fleischer Color Classic',
        'timestamps': [
            ('0:00', '🎨 Cartoon Start'),
            ('0:15', '🎬 Title Card'),
            ('0:40', '🌈 Story Begins'),
            ('3:00', '🎵 Musical Sequence'),
            ('6:00', '✨ Technicolor Finale'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # MARATHON / COMPILATION (2+ Hours)
    # ──────────────────────────────────────────────────────────────────────
    'marathon': {
        'duration_range': (7200, 100000),  # 2+ hours
        'description': 'Marathon Compilation',
        'timestamps': 'DYNAMIC_EPISODE_LIST',  # Wird dynamisch generiert
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # DOKUMENTATIONEN
    # ──────────────────────────────────────────────────────────────────────
    'documentary': {
        'duration_range': (600, 7200),  # 10-120 min
        'description': 'Documentary',
        'timestamps': [
            ('0:00', '🎬 Start'),
            ('1:00', '📖 Introduction'),
            ('5:00', '📚 Chapter 1'),
            ('15:00', '📚 Chapter 2'),
            ('30:00', '📚 Chapter 3'),
            ('45:00', '📝 Conclusion'),
        ],
        'dynamic': True,
    },
    
    # ──────────────────────────────────────────────────────────────────────
    # MUSIK / SOUNDIES (2-4 Min)
    # ──────────────────────────────────────────────────────────────────────
    'soundie': {
        'duration_range': (120, 300),  # 2-5 min
        'description': 'Musical Short / Soundie',
        'timestamps': [
            ('0:00', '🎵 Start'),
            ('0:10', '🎬 Title'),
            ('0:30', '🎤 Performance'),
            ('2:00', '🎶 Finale'),
        ],
        'dynamic': True,
    },
}


def time_to_seconds(time_str: str) -> int:
    """Convert timestamp string to seconds"""
    parts = time_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def seconds_to_time(seconds: int) -> str:
    """Convert seconds to timestamp string"""
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h}:{m:02d}:{s:02d}"
    else:
        m = seconds // 60
        s = seconds % 60
        return f"{m}:{s:02d}"


def scale_timestamps(template_timestamps: List[Tuple[str, str]], 
                     template_duration: int, 
                     actual_duration: int) -> List[Tuple[str, str]]:
    """Scale timestamps to actual video duration"""
    if template_duration <= 0:
        return template_timestamps
    
    scale_factor = actual_duration / template_duration
    scaled = []
    
    for time_str, label in template_timestamps:
        original_seconds = time_to_seconds(time_str)
        scaled_seconds = int(original_seconds * scale_factor)
        
        # Ensure we don't exceed video duration
        if scaled_seconds < actual_duration - 10:
            scaled.append((seconds_to_time(scaled_seconds), label))
    
    return scaled


def detect_content_type(video: dict) -> Optional[str]:
    """Detect content type from video metadata"""
    title = video.get('title', '').lower()
    series = video.get('detected_series') or {}
    series_id = series.get('series_id', '') if series else ''
    duration = video.get('durationSeconds', 0)
    
    # Direct series match
    if series_id and series_id in OPTIMAL_TEMPLATES:
        return series_id
    
    # Keyword-based detection
    keyword_map = {
        'betty boop': 'betty_boop',
        'superman': 'superman',
        'felix': 'felix_cat',
        'casper': 'casper',
        'porky pig': 'porky_pig',
        'porky': 'porky_pig',
        'looney tunes': 'looney_tunes',
        'merrie melodies': 'looney_tunes',
        'popeye': 'popeye',
        'chaplin': 'chaplin',
        'keaton': 'keaton',
        'alfred': 'alfred_jodokus_quack',
        'astro boy': 'astro_boy',
        'ferdy': 'ferdy_die_ameise',
        'color classic': 'color_classics',
        'soundie': 'soundie',
        'nosferatu': 'horror',
        'frankenstein': 'horror',
        'häxan': 'horror',
        'documentary': 'documentary',
        'marathon': 'marathon',
    }
    
    for keyword, content_type in keyword_map.items():
        if keyword in title:
            return content_type
    
    # Duration-based fallback
    if duration > 7200:  # 2+ hours
        return 'marathon'
    elif duration > 3600:  # 1+ hour
        return 'feature_film'
    elif duration > 1200:  # 20+ min (episodes)
        return 'alfred_jodokus_quack'  # Default for episode-length
    elif duration > 600:  # 10+ min
        return 'silent_short'
    elif duration > 300:  # 5+ min
        return 'betty_boop'  # Default for cartoon-length
    elif duration < 300:  # < 5 min
        return 'soundie'
    
    return None


def generate_timestamps(video: dict) -> Optional[str]:
    """Generate optimized timestamps for a video"""
    content_type = detect_content_type(video)
    
    if not content_type or content_type not in OPTIMAL_TEMPLATES:
        return None
    
    template = OPTIMAL_TEMPLATES[content_type]
    duration = video.get('durationSeconds', 0)
    
    if template.get('timestamps') == 'DYNAMIC_EPISODE_LIST':
        # Marathon - needs special handling
        return generate_marathon_timestamps(video)
    
    timestamps = template['timestamps']
    
    # Scale if dynamic
    if template.get('dynamic'):
        min_dur, max_dur = template['duration_range']
        avg_duration = (min_dur + max_dur) / 2
        timestamps = scale_timestamps(timestamps, int(avg_duration), duration)
    
    # Format output
    lines = []
    for time_str, label in timestamps:
        lines.append(f"{time_str} {label}")
    
    return '\n'.join(lines)


def generate_marathon_timestamps(video: dict) -> str:
    """Generate timestamps for marathon compilations"""
    duration = video.get('durationSeconds', 0)
    title = video.get('title', '')
    
    # Try to detect how many episodes based on title
    match = re.search(r'(\d+)\s*episode', title.lower())
    if match:
        episode_count = int(match.group(1))
    else:
        # Estimate based on duration (assume ~8 min per cartoon)
        episode_count = duration // 480
    
    if episode_count < 2:
        episode_count = max(3, duration // 600)
    
    episode_length = duration // episode_count
    
    lines = ['0:00 🎬 Marathon Start']
    for i in range(1, min(episode_count + 1, 50)):  # Max 50 chapters
        timestamp = seconds_to_time(i * episode_length - episode_length)
        if i == 1:
            continue  # Skip first, already at 0:00
        lines.append(f"{seconds_to_time((i-1) * episode_length)} 🎭 Episode {i}")
    
    return '\n'.join(lines)


def format_timestamps_block(timestamps: str, video_title: str) -> str:
    """Format timestamps as a copyable block for video description"""
    return f"""📑 CHAPTERS / TIMESTAMPS
{timestamps}

"""


def analyze_videos_for_timestamps(analysis_path: str = None):
    """Analyze all videos and generate timestamp recommendations"""
    if analysis_path is None:
        analysis_path = os.path.join(CONFIG_DIR, 'complete_channel_analysis.json')
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos_without_timestamps = data.get('issues', {}).get('no_timestamps', [])
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_videos_needing_timestamps': len(videos_without_timestamps),
        'generated': [],
        'skipped': [],
    }
    
    for video in videos_without_timestamps:
        video_id = video['id']
        title = video['title']
        duration = video.get('duration', 0)
        
        # Find full video data
        full_video = next((v for v in data.get('videos', []) if v['id'] == video_id), None)
        if not full_video:
            full_video = {'id': video_id, 'title': title, 'durationSeconds': duration}
        
        timestamps = generate_timestamps(full_video)
        
        if timestamps:
            content_type = detect_content_type(full_video)
            results['generated'].append({
                'id': video_id,
                'title': title,
                'duration': full_video.get('durationSeconds', duration),
                'content_type': content_type,
                'timestamps': timestamps,
            })
        else:
            results['skipped'].append({
                'id': video_id,
                'title': title,
                'reason': 'No matching template',
            })
    
    # Save results
    output_path = os.path.join(CONFIG_DIR, 'generated_timestamps.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("TIMESTAMP GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total videos needing timestamps: {len(videos_without_timestamps)}")
    print(f"Successfully generated: {len(results['generated'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"\nOutput saved to: {output_path}")
    
    return results


if __name__ == '__main__':
    results = analyze_videos_for_timestamps()
    
    # Print preview of first 5 generated timestamps
    print("\n" + "="*60)
    print("PREVIEW - First 5 Generated Timestamps:")
    print("="*60)
    
    for video in results['generated'][:5]:
        print(f"\n🎬 {video['title'][:50]}...")
        print(f"   Type: {video['content_type']}")
        print(f"   Duration: {video['duration']}s")
        print("   Timestamps:")
        for line in video['timestamps'].split('\n'):
            print(f"      {line}")
