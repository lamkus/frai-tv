#!/usr/bin/env python3
"""
fix_soundies_playlist.py — Add 3 missing Soundies to main playlist

Only 3 Soundies are missing from the main Soundies playlist.
The original estimate of "19 missing" was wrong (duplicated scan data).

Playlist: PL3d2Tsr13ihMFH1EDv8To7SBS04OW5tBL (30 videos → 33 after fix)
Quota: 3 × 50 = 150 units

Also: Delete duplicate playlist PL3d2Tsr13ihMoB5EqMRXUrp8c6cYHuo9Y in Studio!

Usage:
    python fix_soundies_playlist.py --dry-run   # Show what would be added
    python fix_soundies_playlist.py --apply      # Add to playlist
"""

import os
import sys
import json
import time

PLAYLIST_ID = "PL3d2Tsr13ihMFH1EDv8To7SBS04OW5tBL"

MISSING_SOUNDIES = [
    {"id": "340C9lsoyYk", "title": "Tica Ti Tica Ta (1940s) | Soundie | 8K HQ (4K UHD)"},
    {"id": "A8LWgWF5f5k", "title": "The Hut-Sut Song (1940s) | Soundie | 8K HQ (4K UHD)"},
    {"id": "DHogGPBbzRI", "title": "Sweet Sue (Just You) (1940s) | Soundie | 8K HQ (4K UHD)"},
]


def get_youtube_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    token_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "token.json"))
    if not os.path.exists(token_path):
        print(f"❌ token.json not found at {token_path}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def dry_run():
    print("=" * 60)
    print("DRY RUN — Add 3 Soundies to Playlist")
    print("=" * 60)
    print(f"\nPlaylist: {PLAYLIST_ID}")
    print(f"Current: 30 videos → After: 33 videos\n")
    for s in MISSING_SOUNDIES:
        print(f"  ➕ {s['id']}  {s['title']}")
    print(f"\nQuota: 3 × 50 = 150 units")
    print(f"\n⚠️  Also delete duplicate playlist in Studio:")
    print(f"    PL3d2Tsr13ihMoB5EqMRXUrp8c6cYHuo9Y")
    print(f"\nRun with --apply to execute.")


def apply_changes():
    youtube = get_youtube_service()
    print("=" * 60)
    print("APPLYING — Adding 3 Soundies to Playlist")
    print("=" * 60)

    added = 0
    for s in MISSING_SOUNDIES:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": PLAYLIST_ID,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": s["id"]
                        }
                    }
                }
            ).execute()
            added += 1
            print(f"  ✅ {s['id']}  {s['title']}")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ {s['id']}  ERROR: {str(e)[:100]}")
            if "quotaExceeded" in str(e):
                print("\n🛑 QUOTA EXHAUSTED!")
                break

    print(f"\n✅ Added {added}/3 Soundies to playlist")
    print(f"💰 Quota: ~{added * 50} units")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_soundies_playlist.py --dry-run | --apply")
        sys.exit(1)

    if sys.argv[1] == "--dry-run":
        dry_run()
    elif sys.argv[1] == "--apply":
        apply_changes()
    else:
        print(f"Unknown: {sys.argv[1]}")


if __name__ == "__main__":
    main()
