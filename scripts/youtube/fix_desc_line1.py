"""
P0 Fix: Description Line 1 Optimization for Top-17 Videos
============================================================

Problem: Desc Zeile 1 = Titel-Kopie (verschwendet sichtbare Search-Zeile!)
Fix: Keyword-reiche, einzigartige Zeile 1 + Zeile 2

YouTube 2026 Algo: Zeile 1-2 sichtbar in Search Results!
- NICHT den Titel wiederholen
- Genre + "remastered" + "restored" + Kontext

QUOTA: 17 × 51 = ~867 Units
BUG-FIX: NUR part='snippet'!

Usage:
    python fix_desc_line1.py --dry-run   # Preview
    python fix_desc_line1.py --apply      # Execute
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

API_KEY = os.getenv("YOUTUBE_API_KEY")

# ── Individuelle Description-Opener (Zeile 1+2) ──
# Formatiert für YouTube Search Preview (max ~120 chars sichtbar)
DESC_OPENERS = {
    "d8Ak1R_eOlY": (  # White Zombie — 32,809 views
        "🎬 The FIRST zombie horror film ever made! Bela Lugosi stars in this 1932 cult classic, now AI remastered in stunning 8K quality.",
        "Originally a low-budget production, White Zombie became one of the most influential horror films in cinema history."
    ),
    "fFanPpOArKs": (  # Felix at the Circus — 25,045 views
        "🎬 Classic 1921 silent cartoon masterpiece! Felix the Cat visits the circus in this iconic vintage animation, restored and upscaled to 8K.",
        "One of the earliest Felix the Cat shorts, showcasing the golden age of American animation from the silent era."
    ),
    "6A2_RKWP2X4": (  # Superman (1941) — 20,287 views
        "🎬 The legendary first Superman cartoon by Fleischer Studios (1941)! Academy Award-nominated animation, now AI remastered in breathtaking 8K.",
        "This groundbreaking Fleischer Superman short introduced the iconic phrase 'It's a bird! It's a plane!' to pop culture."
    ),
    "5WVJHELSD7A": (  # Cabinet of Dr. Caligari — 16,593 views
        "🎬 The masterpiece of German Expressionist cinema! This 1920 silent horror classic pioneered surreal set design, now restored in 8K quality.",
        "Das Cabinet des Dr. Caligari revolutionized filmmaking with its twisted, dreamlike visuals and psychological horror storytelling."
    ),
    "z8FqTSpp6Kg": (  # Dinner for One — 14,158 views
        "🎬 The most repeated TV sketch in history! 'Dinner for One' (1963) with Freddie Frinton, now remastered in crystal-clear 8K quality.",
        "Broadcast every New Year's Eve across Europe, this legendary comedy sketch holds the Guinness World Record for most repeated TV program."
    ),
    "PSdJJaxI4gM": (  # Charade — 7,698 views (actually 1963, not 1953)
        "🎬 Hitchcock-style mystery thriller starring Cary Grant & Audrey Hepburn (1963)! This classic suspense film is now AI remastered in 8K.",
        "Often called 'the best Hitchcock movie Hitchcock never made,' Charade blends romance, comedy, and mystery perfectly."
    ),
    "EMnokZOLpzU": (  # Grim Game — 6,758 views
        "🎬 Harry Houdini's legendary 1919 silent thriller, long thought lost! Rediscovered and now AI remastered in stunning 8K quality.",
        "Watch the legendary escape artist perform real stunts including a terrifying mid-air plane collision filmed without special effects."
    ),
    "yIQCHpjp4NE": (  # Batman & Robin Christmas — 5,562 views
        "🎬 Rare 1966 Batman holiday special! The Dynamic Duo meets Santa Claus in this vintage Christmas classic, now remastered in 8K.",
        "A nostalgic piece of Batman history from the classic Adam West era, perfect for the holiday season."
    ),
    "tJMJlCQc0UE": (  # Betty Boop Minnie the Moocher — 5,428 views
        "🎬 Betty Boop's most iconic cartoon featuring Cab Calloway's legendary jazz performance (1932)! AI remastered in stunning 8K resolution.",
        "Cab Calloway's rotoscoped dance moves and haunting vocals make this one of the greatest animated shorts ever produced."
    ),
    "unzHtnrKeOU": (  # Superman Japoteurs — 4,379 views
        "🎬 Wartime Superman classic from Fleischer Studios (1942)! The Man of Steel battles saboteurs in this vintage WWII-era cartoon, now in 8K.",
        "One of the most action-packed Fleischer Superman shorts, featuring stunning Art Deco animation and thrilling aerial combat."
    ),
    "qZU5lVJMkoM": (  # Felix Minds the Kid — 4,284 views
        "🎬 Hilarious 1922 silent cartoon classic! Felix the Cat babysits in this vintage animation gem, now restored and upscaled to 8K quality.",
        "A charming early Felix the Cat adventure showcasing Pat Sullivan's creative slapstick comedy in the golden age of silent animation."
    ),
    "Nzi6aRKDoEs": (  # Nosferatu — 4,094 views
        "🎬 The original vampire masterpiece! F.W. Murnau's unauthorized Dracula adaptation (1922), now AI remastered in breathtaking 8K quality.",
        "Max Schreck's terrifying Count Orlok remains one of cinema's most iconic monsters — a century later, still genuinely unsettling."
    ),
    "M0-tJK4H3lo": (  # Tokyo Jokio — 4,086 views
        "🎬 Rare WWII-era Merrie Melodies propaganda cartoon (1943)! A fascinating historical document, now restored in 8K for educational purposes.",
        "This wartime animated short provides unique insight into the propaganda techniques used during World War II."
    ),
    "_3Z1GTYFUAM": (  # Buster Keaton Convict 13 — 4,054 views
        "🎬 Buster Keaton's hilarious 1920 silent comedy classic! The master of physical comedy escapes from prison in this vintage gem, now in 8K.",
        "Watch Keaton's incredible stunts and deadpan humor in one of the greatest silent comedies ever made, beautifully restored."
    ),
    "-623U3tgryM": (  # Peter and the Wolf — 4,041 views
        "🎬 The beloved children's classic brought to life in animation (1960)! Prokofiev's musical masterpiece, now AI remastered in 8K quality.",
        "This charming Mel-O-Toons adaptation features Prokofiev's iconic orchestral fairy tale with beautiful vintage hand-drawn animation."
    ),
    "3NagSoFaAwI": (  # Airship Destroyed — 3,998 views
        "🎬 One of the earliest science fiction films ever made (1909)! This pioneering silent short predates WWI aviation, now restored in 8K.",
        "A fascinating glimpse into early 20th century filmmaking and the public's imagination about the future of flight and warfare."
    ),
    "LEM6FkBTDNs": (  # 20,000 Leagues — 3,019 views
        "🎬 The very first feature-length sci-fi film in history (1916)! Jules Verne's underwater adventure, now AI remastered in stunning 8K.",
        "This groundbreaking silent film used real underwater photography — a revolutionary technique that amazed audiences over a century ago."
    ),
}


def get_oauth_credentials():
    """Load OAuth credentials for write operations."""
    token_path = Path(__file__).parent.parent.parent / "token.json"
    if not token_path.exists():
        print(f"ERROR: {token_path} not found!")
        sys.exit(1)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    creds = Credentials.from_authorized_user_file(str(token_path))
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    return creds


def fetch_videos_public(video_ids: list[str]) -> list[dict]:
    """Fetch video snippets via Public API."""
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = requests.get(
            "https://youtube.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",
                "id": ",".join(batch),
                "key": API_KEY,
            }
        )
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code}: {resp.text[:200]}")
            return results
        data = resp.json()
        results.extend(data.get("items", []))
    return results


def fix_description(video_id: str, current_desc: str) -> tuple[str, bool]:
    """
    Replace description line 1 (title echo) with keyword-rich opener.
    Preserves everything after the title echo.
    """
    if video_id not in DESC_OPENERS:
        return current_desc, False

    line1, line2 = DESC_OPENERS[video_id]
    lines = current_desc.split("\n")

    # Find where the actual content starts (skip title echo + blank lines)
    content_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and i > 0:
            # First non-empty line after line 0
            content_start = i
            break
        elif not stripped and i > 0:
            continue
    else:
        content_start = len(lines)

    # Keep everything from content_start onwards
    remaining = lines[content_start:]

    # Build new description
    new_desc = f"{line1}\n{line2}\n\n" + "\n".join(remaining)

    # Clean up excessive blank lines
    while "\n\n\n\n" in new_desc:
        new_desc = new_desc.replace("\n\n\n\n", "\n\n\n")

    return new_desc.strip(), True


def apply_update(creds, video_id: str, new_desc: str, snippet: dict) -> bool:
    """Apply description update via OAuth. part='snippet' ONLY!"""
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", credentials=creds)

    snippet_copy = dict(snippet)
    snippet_copy["description"] = new_desc
    if "categoryId" not in snippet_copy:
        snippet_copy["categoryId"] = "1"

    try:
        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet_copy,
            }
        ).execute()
        return True
    except Exception as e:
        print(f"  ERROR updating {video_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix Description Line 1 for Top Videos")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Usage: --dry-run or --apply")
        sys.exit(1)

    if not API_KEY:
        print("ERROR: YOUTUBE_API_KEY not set!")
        sys.exit(1)

    video_ids = list(DESC_OPENERS.keys())
    print(f"{'DRY RUN' if args.dry_run else 'APPLYING'}: Fix Description Line 1 on {len(video_ids)} top videos")
    print(f"Total views affected: ~180,000")
    print(f"Estimated quota: {len(video_ids) * 51} units\n")

    # Step 1: Fetch current descriptions
    print("Step 1: Fetching current video data (Public API)...")
    videos = fetch_videos_public(video_ids)
    print(f"  Got {len(videos)} videos\n")

    # Step 2: Generate fixes
    changes = []
    for video in videos:
        vid = video["id"]
        title = video["snippet"]["title"]
        current_desc = video["snippet"].get("description", "")
        current_line1 = current_desc.split("\n")[0] if current_desc else ""

        new_desc, changed = fix_description(vid, current_desc)
        new_line1 = new_desc.split("\n")[0] if new_desc else ""

        if changed:
            changes.append({
                "id": vid,
                "title": title[:60],
                "old_line1": current_line1[:80],
                "new_line1": new_line1[:80],
                "new_desc": new_desc,
                "snippet": video["snippet"],
            })
            print(f"  [{vid}] {title[:55]}")
            print(f"    OLD: {current_line1[:70]}...")
            print(f"    NEW: {new_line1[:70]}...")
        else:
            print(f"  [{vid}] {title[:55]} — SKIP (no opener)")

    print(f"\n--- Summary ---")
    print(f"Videos to fix: {len(changes)}/{len(videos)}")
    print(f"Quota needed: {len(changes) * 50 + 1} units")

    if args.dry_run:
        out_path = Path(__file__).parent.parent.parent / "config" / "desc_line1_preview.json"
        preview = [{
            "id": c["id"],
            "title": c["title"],
            "old_line1": c["old_line1"],
            "new_line1": c["new_line1"],
        } for c in changes]
        out_path.write_text(json.dumps(preview, indent=2, ensure_ascii=False))
        print(f"\nPreview saved to: {out_path}")
        return

    # Step 3: Apply
    if not changes:
        print("Nothing to fix!")
        return

    print(f"\nStep 3: Applying {len(changes)} updates...")
    creds = get_oauth_credentials()

    success = 0
    errors = 0
    for i, change in enumerate(changes):
        result = apply_update(creds, change["id"], change["new_desc"], change["snippet"])
        if result:
            success += 1
            print(f"  [{i+1}/{len(changes)}] OK {change['id']}")
        else:
            errors += 1
            print(f"  [{i+1}/{len(changes)}] FAIL {change['id']}")
        time.sleep(0.5)

    print(f"\n--- Results ---")
    print(f"Success: {success}")
    print(f"Errors:  {errors}")
    print(f"Quota used: ~{success * 50 + 1} units")

    result_path = Path(__file__).parent.parent.parent / "config" / "desc_line1_result.json"
    result_path.write_text(json.dumps({
        "date": datetime.now().isoformat(),
        "success": success,
        "errors": errors,
        "quota_used": success * 50 + 1,
    }, indent=2, ensure_ascii=False))
    print(f"Result saved to: {result_path}")


if __name__ == "__main__":
    main()
