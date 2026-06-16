"""
fix_bad_titles.py – Apply SEO titles/descriptions to all badly-named videos
============================================================================
Fixes 7 videos:
  - 2x Raw Wochenschau uploads (Nr.697, Nr.700) → Full SEO
  - 4x Old livestream recordings → Proper archive titles
  - 1x "Livestream von remAIke_IT" → Proper archive title

Quota: 7x videos.update = 350 units

Usage:
    python fix_bad_titles.py --dry-run   # Preview changes (no API calls)
    python fix_bad_titles.py --apply     # Apply changes via API
"""
import sys, json, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = r'D:\remaike.TV\token.json'

# ══════════════════════════════════════════════════════════════════════════════
# VIDEO FIX DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

def build_wochenschau_description(nr, date_de, date_en, event_de, event_en, note, location):
    """Build full SEO description per WOCHENSCHAU_SEO_TEMPLATE.md"""
    return f"""WE HAVE THE BEST VERSION FOR YOU!
SHARE AND PUSH US TO GET THE WHOLE INTERNET UPGRADED :)

@remAIke_IT | www.remAIke.IT
www.FRai.TV - All videos organized....

DE:
Die Deutsche Wochenschau Nr. {nr} vom {date_de}.
Originale Kino-Wochenschau aus Deutschland mit zeitgenössischem Bild- und Tonmaterial.
Diese Ausgabe zeigt: {event_de} — {note}
Schauplatz: {location}

⚠️ Historisches Archivmaterial - dient der Dokumentation und Bildung.

EN:
German Weekly Newsreel No. {nr}, dated {date_en}.
Original theatrical newsreel footage with contemporary image and sound material.
This edition documents: {event_en}
Location: {location}

⚠️ Historical archive material - for documentation and educational purposes.

ES:
Noticiero Semanal Alemán Nr. {nr}, fechado {date_en}.
Material de archivo cinematográfico original con imágenes y sonido de la época.

⚠️ Material de archivo histórico - con fines documentales y educativos.

8K HQ Edition:
• stabilized archival source
• enhanced clarity for modern displays
• original visual and audio character preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #GermanNewsreel #WWIIHistory #1944 #ArchiveFootage #HistoricalFilm
#Zeitgeschichte #WorldHistory #8K #remAIke"""


WOCHENSCHAU_TAGS = [
    "wochenschau", "german newsreel", "wwii history", "1944",
    "archive footage", "historical film", "zeitgeschichte",
    "world history", "8k", "remAIke", "documentary",
    "kino wochenschau", "remastered", "restored", "public domain"
]

FIXES = [
    # ── Nr.700: Korsun Pocket ────────────────────────────────────────────────
    {
        'id': 'WyDmmQuHV5Y',
        'type': 'WOCHENSCHAU_UPLOAD',
        'new_title': 'Wochenschau 700: Korsun Pocket (02.02.1944) | 8K HQ (4K UHD)',
        'new_description': build_wochenschau_description(
            nr=700,
            date_de='02. Februar 1944',
            date_en='February 2, 1944',
            event_de='Tscherkassy Kessel',
            event_en='Korsun Pocket',
            note='Kesselschlacht bei Tscherkassy',
            location='Korsun, Ukraine',
        ),
        'tags': WOCHENSCHAU_TAGS + ["korsun pocket", "tscherkassy"],
        'category': '27',
    },
    # ── Nr.697: Leningrad Relief ─────────────────────────────────────────────
    {
        'id': 'UJRbjGwCptI',
        'type': 'WOCHENSCHAU_UPLOAD',
        'new_title': 'Wochenschau 697: Leningrad Relief (12.01.1944) | 8K HQ (4K UHD)',
        'new_description': build_wochenschau_description(
            nr=697,
            date_de='12. Januar 1944',
            date_en='January 12, 1944',
            event_de='Leningrad Entsetzen',
            event_en='Leningrad Relief',
            note='Offensive zur Befreiung Leningrads',
            location='Leningrad (St. Petersburg), Russia',
        ),
        'tags': WOCHENSCHAU_TAGS + ["leningrad", "siege of leningrad"],
        'category': '27',
    },
    # ── Old livestream recordings → Archive titles ───────────────────────────
    {
        'id': 'EBysKraqDYU',
        'type': 'STREAM_ARCHIVE',
        'new_title': 'WochenschauTV Stream Archive (23.02.2026) | Private Recording',
        'new_description': None,  # Keep existing
        'tags': None,
        'category': None,
    },
    {
        'id': 'HuyWJlD8R28',
        'type': 'STREAM_ARCHIVE',
        'new_title': 'WochenschauTV Stream Archive (23.02.2026) | Test Recording',
        'new_description': None,
        'tags': None,
        'category': None,
    },
    {
        'id': 'A4XcS4mOvaU',
        'type': 'STREAM_ARCHIVE',
        'new_title': 'WochenschauTV Stream Archive (21.02.2026) | Private Recording',
        'new_description': None,
        'tags': None,
        'category': None,
    },
    {
        'id': 'Bf04muRRRh4',
        'type': 'STREAM_ARCHIVE',
        'new_title': 'WochenschauTV Stream Archive (21.02.2026) | 3h Recording',
        'new_description': None,
        'tags': None,
        'category': None,
    },
    {
        'id': '-cygkIsaWXQ',
        'type': 'STREAM_ARCHIVE',
        'new_title': 'WochenschauTV Stream Archive (21.02.2026) | Test Recording',
        'new_description': None,
        'tags': None,
        'category': None,
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--apply', action='store_true', help='Apply changes via API')
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Usage: --dry-run or --apply")
        return

    print(f"{'DRY RUN' if args.dry_run else 'APPLYING'} — {len(FIXES)} videos to fix\n")

    if args.apply:
        creds = Credentials.from_authorized_user_file(TOKEN)
        yt = build('youtube', 'v3', credentials=creds)

    success = 0
    failed = 0
    quota_used = 0

    for fix in FIXES:
        vid_id = fix['id']
        print(f"[{vid_id}] {fix['type']}")
        print(f"  NEW TITLE: {fix['new_title']}")
        if fix.get('new_description'):
            print(f"  NEW DESC:  {fix['new_description'][:80]}...")
        if fix.get('tags'):
            print(f"  TAGS:      {len(fix['tags'])} tags")
        print()

        if args.apply:
            try:
                # First get current video data
                current = yt.videos().list(
                    part='snippet,status',
                    id=vid_id
                ).execute()
                
                if not current.get('items'):
                    print(f"  ERROR: Video not found!")
                    failed += 1
                    continue
                
                video = current['items'][0]
                snippet = video['snippet']
                
                # Update snippet
                snippet['title'] = fix['new_title']
                if fix.get('new_description'):
                    snippet['description'] = fix['new_description']
                if fix.get('tags'):
                    snippet['tags'] = fix['tags']
                if fix.get('category'):
                    snippet['categoryId'] = fix['category']
                
                # Remove problematic fields
                snippet.pop('publishedAt', None)
                snippet.pop('channelId', None)
                snippet.pop('thumbnails', None)
                snippet.pop('channelTitle', None)
                snippet.pop('localized', None)
                snippet.pop('liveBroadcastContent', None)
                
                # Apply update
                body = {
                    'id': vid_id,
                    'snippet': snippet,
                }
                
                yt.videos().update(
                    part='snippet',
                    body=body
                ).execute()
                
                quota_used += 50  # videos.update = 50 units
                success += 1
                print(f"  ✅ UPDATED! (50 units)")
                
            except Exception as e:
                failed += 1
                print(f"  ❌ FAILED: {e}")
        else:
            success += 1

    print(f"\n{'='*60}")
    print(f"Results: {success} success, {failed} failed")
    if args.apply:
        print(f"Quota used: {quota_used} units")


if __name__ == '__main__':
    main()
