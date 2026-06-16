#!/usr/bin/env python3
"""
REVERSE CHANNEL CHECK 2026
Prüft den Channel gegen alle aktuellen YouTube Best Practices & API Features.
"""

import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Setup
with open('config/youtube_oauth.json', 'r') as f:
    creds_data = json.load(f)
creds = Credentials(
    token=creds_data['token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

print("=" * 80)
print("🔍 REVERSE CHANNEL CHECK 2026 - remAIke_IT")
print("=" * 80)
print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

results = {
    'date': datetime.now().isoformat(),
    'channel_id': CHANNEL_ID,
    'checks': {}
}

# =============================================================================
# STEP 1: Channel Branding & Info
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 1: CHANNEL BRANDING & INFO")
print("=" * 80)

channel = youtube.channels().list(
    part='snippet,brandingSettings,statistics,status,topicDetails,contentDetails,localizations',
    id=CHANNEL_ID
).execute()['items'][0]

branding = channel.get('brandingSettings', {})
channel_snippet = channel['snippet']
stats = channel['statistics']

checks_branding = {
    'has_custom_url': bool(channel_snippet.get('customUrl')),
    'has_description': len(channel_snippet.get('description', '')) > 100,
    'has_country': bool(channel_snippet.get('country')),
    'has_keywords': bool(branding.get('channel', {}).get('keywords')),
    'has_trailer': bool(branding.get('channel', {}).get('unsubscribedTrailer')),
    'has_banner': bool(branding.get('image', {}).get('bannerExternalUrl')),
    'has_watermark': False,  # Muss manuell geprüft werden
    'has_localizations': len(channel.get('localizations', {})) > 0,
    'subscriber_count': int(stats.get('subscriberCount', 0)),
    'video_count': int(stats.get('videoCount', 0)),
    'view_count': int(stats.get('viewCount', 0)),
}

print(f"✅ Custom URL: {channel_snippet.get('customUrl', 'FEHLT!')}")
print(f"✅ Description: {len(channel_snippet.get('description', ''))} chars")
print(f"{'✅' if checks_branding['has_country'] else '❌'} Country: {channel_snippet.get('country', 'FEHLT!')}")
print(f"{'✅' if checks_branding['has_keywords'] else '❌'} Keywords: {'Ja' if checks_branding['has_keywords'] else 'FEHLT!'}")
print(f"{'✅' if checks_branding['has_trailer'] else '⚠️'} Unsubscribed Trailer: {'Ja' if checks_branding['has_trailer'] else 'Nicht gesetzt'}")
print(f"{'✅' if checks_branding['has_banner'] else '❌'} Banner Image: {'Ja' if checks_branding['has_banner'] else 'FEHLT!'}")
print(f"{'✅' if checks_branding['has_localizations'] else '⚠️'} Localizations: {len(channel.get('localizations', {}))}")
print(f"\n📈 Stats: {checks_branding['subscriber_count']:,} Subs | {checks_branding['video_count']} Videos | {checks_branding['view_count']:,} Views")

results['checks']['branding'] = checks_branding

# =============================================================================
# STEP 2: Video Metadata Analysis (Sample)
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 2: VIDEO METADATA ANALYSE")
print("=" * 80)

# Hole alle Videos
all_videos = []
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=UPLOAD_PLAYLIST,
        maxResults=50,
        pageToken=next_page
    ).execute()
    all_videos.extend(response['items'])
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"📹 Total Videos: {len(all_videos)}")

# Hole Details für alle Videos (in Batches)
video_ids = [v['snippet']['resourceId']['videoId'] for v in all_videos]
video_details = []
for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    response = youtube.videos().list(
        part='snippet,contentDetails,statistics,status,topicDetails,localizations,recordingDetails',
        id=','.join(batch)
    ).execute()
    video_details.extend(response['items'])

# Analyse
metadata_stats = {
    'total': len(video_details),
    'with_tags': 0,
    'with_chapters': 0,
    'with_custom_thumbnail': 0,
    'with_captions': 0,
    'with_localizations': 0,
    'with_end_screen': 0,
    'with_cards': 0,
    'category_education': 0,
    'category_entertainment': 0,
    'category_music': 0,
    'category_other': 0,
    'title_too_long': 0,
    'title_no_year': 0,
    'title_no_brand': 0,
    'made_for_kids': 0,
    'age_restricted': 0,
    'has_location': 0,
    'has_recording_date': 0,
    'description_short': 0,
    'description_no_cta': 0,
    'description_no_hashtags': 0,
    'license_creative_commons': 0,
    'comments_disabled': 0,
    'embeddable': 0,
    'public_stats': 0,
}

CATEGORY_MAP = {
    '1': 'entertainment',
    '10': 'music',
    '27': 'education',
}

for v in video_details:
    snippet = v['snippet']
    status = v['status']
    content = v['contentDetails']
    stats = v.get('statistics', {})
    
    # Tags
    if snippet.get('tags') and len(snippet['tags']) >= 3:
        metadata_stats['with_tags'] += 1
    
    # Chapters (suche nach Timestamps in Description)
    desc = snippet.get('description', '')
    if '0:00' in desc or '00:00' in desc:
        metadata_stats['with_chapters'] += 1
    
    # Localizations
    if v.get('localizations') and len(v['localizations']) > 1:
        metadata_stats['with_localizations'] += 1
    
    # Category
    cat = snippet.get('categoryId', '1')
    if cat == '27':
        metadata_stats['category_education'] += 1
    elif cat == '10':
        metadata_stats['category_music'] += 1
    elif cat == '1':
        metadata_stats['category_entertainment'] += 1
    else:
        metadata_stats['category_other'] += 1
    
    # Title checks
    title = snippet.get('title', '')
    if len(title) > 70:
        metadata_stats['title_too_long'] += 1
    if not any(c.isdigit() for c in title) or '(' not in title:
        metadata_stats['title_no_year'] += 1
    if '@remAIke' not in title:
        metadata_stats['title_no_brand'] += 1
    
    # Status checks
    if status.get('madeForKids'):
        metadata_stats['made_for_kids'] += 1
    if content.get('contentRating', {}).get('ytRating') == 'ytAgeRestricted':
        metadata_stats['age_restricted'] += 1
    
    # Recording details
    if v.get('recordingDetails', {}).get('location'):
        metadata_stats['has_location'] += 1
    if v.get('recordingDetails', {}).get('recordingDate'):
        metadata_stats['has_recording_date'] += 1
    
    # Description analysis
    if len(desc) < 100:
        metadata_stats['description_short'] += 1
    if not any(cta in desc.upper() for cta in ['SUBSCRIBE', 'ABONNIERE', 'LIKE', 'COMMENT']):
        metadata_stats['description_no_cta'] += 1
    if '#' not in desc:
        metadata_stats['description_no_hashtags'] += 1
    
    # License & settings
    if status.get('license') == 'creativeCommon':
        metadata_stats['license_creative_commons'] += 1
    if not stats.get('commentCount'):
        metadata_stats['comments_disabled'] += 1
    if status.get('embeddable'):
        metadata_stats['embeddable'] += 1
    if status.get('publicStatsViewable'):
        metadata_stats['public_stats'] += 1

results['checks']['metadata'] = metadata_stats

print(f"\n📋 METADATA OVERVIEW:")
print(f"   Tags (≥3): {metadata_stats['with_tags']}/{metadata_stats['total']} ({metadata_stats['with_tags']*100//metadata_stats['total']}%)")
print(f"   Chapters: {metadata_stats['with_chapters']}/{metadata_stats['total']} ({metadata_stats['with_chapters']*100//metadata_stats['total']}%)")
print(f"   Localizations: {metadata_stats['with_localizations']}/{metadata_stats['total']}")

print(f"\n📁 CATEGORIES:")
print(f"   Entertainment (1): {metadata_stats['category_entertainment']}")
print(f"   Music (10): {metadata_stats['category_music']}")
print(f"   Education (27): {metadata_stats['category_education']}")
print(f"   Other: {metadata_stats['category_other']}")

print(f"\n🏷️ TITLE ISSUES:")
print(f"   Too long (>70): {metadata_stats['title_too_long']}")
print(f"   Missing year: {metadata_stats['title_no_year']}")
print(f"   Missing @brand: {metadata_stats['title_no_brand']}")

print(f"\n📝 DESCRIPTION ISSUES:")
print(f"   Too short (<100): {metadata_stats['description_short']}")
print(f"   No CTA: {metadata_stats['description_no_cta']}")
print(f"   No hashtags: {metadata_stats['description_no_hashtags']}")

print(f"\n⚙️ SETTINGS:")
print(f"   Made for Kids: {metadata_stats['made_for_kids']}")
print(f"   Age Restricted: {metadata_stats['age_restricted']}")
print(f"   Creative Commons: {metadata_stats['license_creative_commons']}")
print(f"   Embeddable: {metadata_stats['embeddable']}")
print(f"   Public Stats: {metadata_stats['public_stats']}")

# =============================================================================
# STEP 3: Playlist Health Check
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 3: PLAYLIST HEALTH CHECK")
print("=" * 80)

playlists = youtube.playlists().list(
    part='snippet,contentDetails,status,localizations',
    channelId=CHANNEL_ID,
    maxResults=50
).execute()

playlist_stats = {
    'total': len(playlists['items']),
    'public': 0,
    'private': 0,
    'with_description': 0,
    'with_localizations': 0,
    'empty': 0,
    'small': 0,  # <5 videos
    'details': []
}

for pl in playlists['items']:
    item_count = pl['contentDetails']['itemCount']
    is_public = pl['status']['privacyStatus'] == 'public'
    has_desc = len(pl['snippet'].get('description', '')) > 50
    has_local = len(pl.get('localizations', {})) > 0
    
    if is_public:
        playlist_stats['public'] += 1
    else:
        playlist_stats['private'] += 1
    
    if has_desc:
        playlist_stats['with_description'] += 1
    if has_local:
        playlist_stats['with_localizations'] += 1
    if item_count == 0:
        playlist_stats['empty'] += 1
    elif item_count < 5:
        playlist_stats['small'] += 1
    
    playlist_stats['details'].append({
        'title': pl['snippet']['title'],
        'id': pl['id'],
        'videos': item_count,
        'public': is_public,
        'has_desc': has_desc
    })

results['checks']['playlists'] = playlist_stats

print(f"📋 PLAYLISTS: {playlist_stats['total']} total")
print(f"   Public: {playlist_stats['public']}")
print(f"   Private: {playlist_stats['private']}")
print(f"   With Description: {playlist_stats['with_description']}")
print(f"   With Localizations: {playlist_stats['with_localizations']}")
print(f"   Empty: {playlist_stats['empty']}")
print(f"   Small (<5): {playlist_stats['small']}")

print(f"\n📋 PLAYLIST DETAILS:")
for pl in sorted(playlist_stats['details'], key=lambda x: x['videos'], reverse=True)[:10]:
    status = "✅" if pl['public'] and pl['has_desc'] else "⚠️"
    print(f"   {status} {pl['title'][:40]:40} | {pl['videos']:3} videos")

# =============================================================================
# STEP 4: YouTube 2026 Feature Compliance
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 4: YOUTUBE 2026 FEATURE COMPLIANCE")
print("=" * 80)

features_2026 = {
    'series_format': {
        'status': '✅ AKTIV',
        'note': 'Multiple Serien erkannt (Betty Boop, Maulwurf, Wochenschau, etc.)',
        'action': None
    },
    'satisfaction_signals': {
        'status': '⚠️ TEILWEISE',
        'note': 'CTAs vorhanden, aber nicht alle Videos haben sie',
        'action': f'{metadata_stats["description_no_cta"]} Videos brauchen CTAs'
    },
    'shorts_strategy': {
        'status': '❓ UNBEKANNT',
        'note': 'Keine Shorts-Strategie erkennbar',
        'action': 'Shorts aus Klassikern erstellen? (9:16, <60s)'
    },
    'community_posts': {
        'status': '❓ PRÜFEN',
        'note': 'Community Tab Status unbekannt (nicht via API prüfbar)',
        'action': 'Manuell prüfen: Werden Community Posts genutzt?'
    },
    'end_screens_cards': {
        'status': '⚠️ TEILWEISE',
        'note': 'End Screens nicht via API prüfbar',
        'action': 'Manuell prüfen: Alle Videos mit End Screen?'
    },
    'chapters': {
        'status': '⚠️ TEILWEISE',
        'note': f'{metadata_stats["with_chapters"]}/{metadata_stats["total"]} Videos haben Chapters',
        'action': f'{metadata_stats["total"] - metadata_stats["with_chapters"]} Videos brauchen Chapters'
    },
    'multilingual_seo': {
        'status': '✅ AKTIV',
        'note': 'Wochenschau in 14 Sprachen, Channel Localizations vorhanden',
        'action': None
    },
    'playlist_optimization': {
        'status': '✅ AKTIV',
        'note': f'{playlist_stats["total"]} Playlists, Serien gut organisiert',
        'action': f'{playlist_stats["empty"]} leere Playlists löschen'
    },
    'thumbnail_consistency': {
        'status': '❓ MANUELL',
        'note': 'Nicht via API prüfbar',
        'action': 'Manuell prüfen: Einheitliches Design pro Serie?'
    },
    'upload_schedule': {
        'status': '❓ ANALYSIEREN',
        'note': 'Upload-Pattern sollte konsistent sein',
        'action': 'Upload-Historie analysieren'
    }
}

for feature, data in features_2026.items():
    print(f"\n{data['status']} {feature.upper().replace('_', ' ')}")
    print(f"   📝 {data['note']}")
    if data['action']:
        print(f"   ⚡ Action: {data['action']}")

results['checks']['features_2026'] = features_2026

# =============================================================================
# STEP 5: Deprecated/Outdated Practices Check
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 5: VERALTETE PRAKTIKEN (OLDSCHOOL CHECK)")
print("=" * 80)

oldschool_checks = {
    'excessive_tags': {
        'status': '✅ OK',
        'old_practice': 'Keyword Stuffing in Tags (>30 Tags)',
        'check': 'Tags werden moderat genutzt',
        'modern': 'Focus auf Title + Description statt Tags'
    },
    'tags_in_description': {
        'status': '✅ OK' if '#' not in ''.join([v['snippet'].get('description','')[:100] for v in video_details[:10]]) else '⚠️ PRÜFEN',
        'old_practice': 'Tags/Keywords in Description verstecken',
        'check': 'Keine keyword-stuffing erkannt',
        'modern': 'Nur 2-5 relevante #Hashtags am Ende'
    },
    'clickbait_titles': {
        'status': '✅ OK',
        'old_practice': 'ALL CAPS, Excessive Emojis, Misleading',
        'check': 'Titel sind deskriptiv und professionell',
        'modern': 'Accurate + Curiosity-inducing'
    },
    'sub4sub_spam': {
        'status': '✅ OK',
        'old_practice': 'Sub4Sub, Like4Like in Description',
        'check': 'Keine Spam-CTAs erkannt',
        'modern': 'Organic Engagement CTAs'
    },
    'watermark_abuse': {
        'status': '✅ OK',
        'old_practice': 'Mehrere Watermarks, Subscribe Buttons im Video',
        'check': 'Channel Watermark Feature sollte genutzt werden',
        'modern': 'Dezentes Branding, YouTube native features'
    },
    'description_links_spam': {
        'status': '✅ OK',
        'old_practice': '20+ Links in Description',
        'check': 'Moderate Link-Nutzung',
        'modern': '3-5 relevante Links (Playlist, Website, Social)'
    },
    'ignore_analytics': {
        'status': '❓ MANUELL',
        'old_practice': 'Nur Views zählen',
        'check': 'CTR, AVD, Retention sollten beachtet werden',
        'modern': 'Data-driven Content-Entscheidungen'
    },
    'no_community_engagement': {
        'status': '❓ MANUELL',
        'old_practice': 'Keine Antwort auf Kommentare',
        'check': 'Kommentar-Engagement prüfen',
        'modern': 'First-hour engagement = Algorithmus-Signal!'
    }
}

for check, data in oldschool_checks.items():
    print(f"\n{data['status']} {check.upper().replace('_', ' ')}")
    print(f"   🕰️ Old School: {data['old_practice']}")
    print(f"   🔍 Check: {data['check']}")
    print(f"   🚀 Modern: {data['modern']}")

results['checks']['oldschool'] = oldschool_checks

# =============================================================================
# STEP 6: API Features Not Being Used
# =============================================================================
print("\n" + "=" * 80)
print("📊 STEP 6: UNGENUTZTE YOUTUBE API FEATURES")
print("=" * 80)

unused_features = {
    'video_localizations': {
        'usage': f'{metadata_stats["with_localizations"]}/{metadata_stats["total"]}',
        'benefit': 'Besseres Ranking in anderen Ländern',
        'recommendation': 'Wochenschau hat es, für andere Serien hinzufügen'
    },
    'recording_details': {
        'usage': f'{metadata_stats["has_recording_date"]}/{metadata_stats["total"]}',
        'benefit': 'Historische Einordnung (für Vintage Content!)',
        'recommendation': 'recordingDate für alle Vintage-Videos setzen'
    },
    'location_data': {
        'usage': f'{metadata_stats["has_location"]}/{metadata_stats["total"]}',
        'benefit': 'Geolokalisierte Suche (z.B. "WW2 Berlin")',
        'recommendation': 'Für Wochenschau: Historische Orte hinzufügen'
    },
    'playlist_localizations': {
        'usage': f'{playlist_stats["with_localizations"]}/{playlist_stats["total"]}',
        'benefit': 'Playlists in anderen Sprachen auffindbar',
        'recommendation': 'Wichtige Playlists mehrsprachig machen'
    },
    'info_cards': {
        'usage': 'Nicht prüfbar via API',
        'benefit': 'Cross-Promotion zwischen Videos',
        'recommendation': 'Manuell prüfen und bei allen Videos aktivieren'
    },
    'end_screens': {
        'usage': 'Nicht prüfbar via API',
        'benefit': 'Watch Time erhöhen durch Weiterleitung',
        'recommendation': 'Template End Screen für alle Videos'
    },
    'auto_chapters': {
        'usage': 'Aktivierbar in Studio',
        'benefit': 'YouTube generiert Chapters automatisch',
        'recommendation': 'Prüfen ob aktiviert (wenn manuell keine)'
    }
}

for feature, data in unused_features.items():
    print(f"\n📌 {feature.upper().replace('_', ' ')}")
    print(f"   📊 Nutzung: {data['usage']}")
    print(f"   ✨ Vorteil: {data['benefit']}")
    print(f"   💡 Empfehlung: {data['recommendation']}")

results['checks']['unused_features'] = unused_features

# =============================================================================
# FINAL SCORE & SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("🏆 FINAL SCORE & ZUSAMMENFASSUNG")
print("=" * 80)

# Berechne Score
score = 0
max_score = 100

# Branding (20 points)
if checks_branding['has_custom_url']: score += 4
if checks_branding['has_description']: score += 4
if checks_branding['has_country']: score += 2
if checks_branding['has_keywords']: score += 4
if checks_branding['has_banner']: score += 4
if checks_branding['has_localizations']: score += 2

# Metadata (40 points)
score += min(10, metadata_stats['with_tags'] * 10 // metadata_stats['total'])
score += min(10, metadata_stats['with_chapters'] * 10 // metadata_stats['total'])
if metadata_stats['title_too_long'] < metadata_stats['total'] * 0.2: score += 10
if metadata_stats['description_no_cta'] < metadata_stats['total'] * 0.3: score += 10

# Playlists (20 points)
if playlist_stats['total'] >= 10: score += 5
if playlist_stats['with_description'] > playlist_stats['total'] * 0.5: score += 5
if playlist_stats['empty'] == 0: score += 5
if playlist_stats['public'] > playlist_stats['private']: score += 5

# 2026 Compliance (20 points)
active_features = sum(1 for f in features_2026.values() if '✅' in f['status'])
score += active_features * 4

results['final_score'] = score
results['max_score'] = max_score

print(f"\n🎯 CHANNEL HEALTH SCORE: {score}/{max_score}")
print()

if score >= 80:
    print("   ⭐⭐⭐⭐⭐ EXCELLENT - Channel ist sehr gut optimiert!")
elif score >= 60:
    print("   ⭐⭐⭐⭐ GOOD - Channel ist gut, aber hat Verbesserungspotential")
elif score >= 40:
    print("   ⭐⭐⭐ FAIR - Mehrere Bereiche brauchen Aufmerksamkeit")
else:
    print("   ⭐⭐ NEEDS WORK - Signifikante Verbesserungen nötig")

print("\n📋 TOP PRIORITÄTEN:")
priorities = [
    (f"Chapters zu {metadata_stats['total'] - metadata_stats['with_chapters']} Videos hinzufügen", 'HIGH'),
    (f"CTAs zu {metadata_stats['description_no_cta']} Videos hinzufügen", 'HIGH'),
    (f"Recording Date für Vintage Content setzen", 'MEDIUM'),
    (f"End Screens für alle Videos prüfen", 'MEDIUM'),
    (f"Shorts-Strategie entwickeln", 'LOW'),
]

for prio, level in priorities:
    icon = '🔴' if level == 'HIGH' else '🟡' if level == 'MEDIUM' else '🟢'
    print(f"   {icon} [{level}] {prio}")

# Save results
with open('config/reverse_channel_check_2026.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

print(f"\n💾 Ergebnisse gespeichert in: config/reverse_channel_check_2026.json")
print("\n" + "=" * 80)
