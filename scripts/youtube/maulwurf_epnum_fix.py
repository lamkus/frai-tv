"""
Maulwurf Episode Number & Year Fix
===================================
Fixes 6 YouTube videos with wrong episode numbers based on verified CZ Wikipedia data.
Uses the definitive Czech episode list (Seznam dílů seriálu O krtkovi).

Sources:
- https://cs.wikipedia.org/wiki/Seznam_dílů_seriálu_O_krtkovi (CZ episode list, 49 episodes)
- https://en.wikipedia.org/wiki/The_Little_Mole (EN filmography cross-reference)

Series: 49 episodes total (43 shorts + 6 features), 1957-2002, directed by Zdeněk Miler.

CORRECTIONS needed (CZ Wikipedia numbering):
  wjpCNxf5SsY: E16 → E17 (Streichhölzer / zápalky)
  3GM123aC4bE: E20 → E22 (Hühnerei / vejce)
  j4aBiGJcEY8: E21 → E23 (Fotograf / fotografem)
  MlzpyJ6CyHw: E63 (1998) → E49 (2002) (kleine Frosch / žabka - LAST episode EVER)
  EZxjMpAY9Wk: E59 → E45 (Quelle / pramen)
  tMaYrApYlxc: E60 → E44 (Flöte / flétna)

Cost: 6 × 51 = 306 quota
"""

import json
import os
import sys
from datetime import datetime

# OAuth setup
sys.path.insert(0, os.path.dirname(__file__))
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
CLIENT_SECRET = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'maulwurf_complete_database.json')

# === VERIFIED CORRECTIONS (from CZ Wikipedia) ===
FIXES = [
    {
        "video_id": "wjpCNxf5SsY",
        "old_ep": 16,
        "new_ep": 17,
        "year": 1974,  # year is correct
        "de_title": "Der Maulwurf und die Streichhölzer",
        "source": "CZ Wiki #17: Krtek a zápalky (1974)"
    },
    {
        "video_id": "3GM123aC4bE",
        "old_ep": 20,
        "new_ep": 22,
        "year": 1975,  # year is correct
        "de_title": "Der Maulwurf und das Hühnerei",
        "source": "CZ Wiki #22: Krtek a vejce (1975)"
    },
    {
        "video_id": "j4aBiGJcEY8",
        "old_ep": 21,
        "new_ep": 23,
        "year": 1975,  # year is correct
        "de_title": "Der Maulwurf als Fotograf",
        "source": "CZ Wiki #23: Krtek fotografem (1975)"
    },
    {
        "video_id": "MlzpyJ6CyHw",
        "old_ep": 63,
        "new_ep": 49,
        "year": 2002,  # YEAR FIX! Was showing (1998) in title, should be (2002)
        "de_title": "Der Maulwurf und der kleine Frosch",
        "source": "CZ Wiki #49: Krtek a žabka (2002) — the LAST episode ever made"
    },
    {
        "video_id": "EZxjMpAY9Wk",
        "old_ep": 59,
        "new_ep": 45,
        "year": 1999,  # year is correct
        "de_title": "Der Maulwurf und die Quelle",
        "source": "CZ Wiki #45: Krtek a pramen (1999)"
    },
    {
        "video_id": "tMaYrApYlxc",
        "old_ep": 60,
        "new_ep": 44,
        "year": 1999,  # year is correct
        "de_title": "Der Maulwurf und die Flöte",
        "source": "CZ Wiki #44: Krtek a flétna (1999)"
    }
]


def get_youtube():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)


def fix_title(old_title, old_ep, new_ep, year):
    """Replace episode number in title and fix year if needed."""
    new_title = old_title.replace(f"E{old_ep:02d}:", f"E{new_ep:02d}:")
    # Also handle non-zero-padded
    new_title = new_title.replace(f"E{old_ep}:", f"E{new_ep:02d}:")
    # Fix year in parentheses if needed (for EP49/formerly EP63: 1998 → 2002)
    if old_ep == 63 and new_ep == 49:
        new_title = new_title.replace("(1998)", f"({year})")
    return new_title


def fix_localizations(locs, old_ep, new_ep, year):
    """Fix episode numbers in all localized titles."""
    fixed = {}
    for lang, data in locs.items():
        new_data = dict(data)
        if 'title' in new_data:
            new_data['title'] = fix_title(new_data['title'], old_ep, new_ep, year)
        fixed[lang] = new_data
    return fixed


def fix_description(desc, old_ep, new_ep, year):
    """Fix episode references in description."""
    if not desc:
        return desc
    result = desc
    # Fix "Episode XX" references
    result = result.replace(f"Episode {old_ep}", f"Episode {new_ep}")
    result = result.replace(f"E{old_ep:02d}", f"E{new_ep:02d}")
    result = result.replace(f"E{old_ep}", f"E{new_ep:02d}")
    result = result.replace(f"Folge {old_ep}", f"Folge {new_ep}")
    result = result.replace(f"エピソード{old_ep}", f"エピソード{new_ep}")
    result = result.replace(f"第{old_ep}集", f"第{new_ep}集")
    # Fix year for EP49
    if old_ep == 63 and new_ep == 49:
        result = result.replace("(1998)", f"({year})")
    # Fix "49 episodes" references that say "63 episodes"
    result = result.replace("63 Episoden", "49 Episoden")
    result = result.replace("63 episodes", "49 episodes")
    result = result.replace("63集", "49集")
    return result


def main():
    print("=" * 60)
    print("MAULWURF EPISODE NUMBER FIX")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Videos to fix: {len(FIXES)}")
    print(f"Estimated quota: {len(FIXES) * 51} units")
    print("=" * 60)

    # Step 1: Fix the JSON database
    print("\n📝 Step 1: Fixing maulwurf_complete_database.json...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    # Fix total_episodes
    db['series_info']['total_episodes'] = 49
    db['series_info']['note'] = "49 episodes total: 43 shorts + 6 features. Numbering per CZ Wikipedia."

    db_fixes = 0
    for fix in FIXES:
        for vid in db['our_videos']:
            if vid['video_id'] == fix['video_id']:
                old_ep = vid['ep_num']
                vid['ep_num'] = fix['new_ep']
                vid['yt_title'] = f"Krtek E{fix['new_ep']:02d}: {fix['de_title']} ({fix['year']}) | 8K HQ"
                vid['source'] = fix['source']
                if fix['video_id'] == 'MlzpyJ6CyHw':
                    vid.pop('note', None)  # Remove old note about year discrepancy
                print(f"  DB: EP{old_ep} → EP{fix['new_ep']} ({fix['de_title']})")
                db_fixes += 1
                break

    # Also fix the complete_episodes list if ep_num references exist
    if 'complete_episodes' in db:
        for ep in db['complete_episodes']:
            if ep.get('ep_num') and ep['ep_num'] > 49:
                # These numbers don't exist in the real series
                pass

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {db_fixes} entries fixed in database")

    # Step 2: Fix YouTube videos
    print("\n📺 Step 2: Fixing YouTube videos...")
    youtube = get_youtube()

    results = []
    total_quota = 0

    for fix in FIXES:
        vid_id = fix['video_id']
        print(f"\n  {'='*50}")
        print(f"  Fixing: {fix['de_title']}")
        print(f"  EP{fix['old_ep']} → EP{fix['new_ep']} | Year: {fix['year']}")
        print(f"  Source: {fix['source']}")

        try:
            # Read current state (1 quota)
            resp = youtube.videos().list(
                part='snippet,localizations',
                id=vid_id
            ).execute()
            total_quota += 1

            if not resp.get('items'):
                print(f"  ❌ Video {vid_id} not found!")
                results.append({"video_id": vid_id, "status": "NOT_FOUND"})
                continue

            video = resp['items'][0]
            snippet = video['snippet']
            old_title = snippet['title']

            # Fix title
            new_title = fix_title(old_title, fix['old_ep'], fix['new_ep'], fix['year'])

            # Fix description
            new_desc = fix_description(snippet.get('description', ''), fix['old_ep'], fix['new_ep'], fix['year'])

            # Fix localizations
            locs = video.get('localizations', {})
            new_locs = fix_localizations(locs, fix['old_ep'], fix['new_ep'], fix['year'])

            print(f"  Title: {old_title}")
            print(f"     →  {new_title}")
            print(f"  Localizations: {len(new_locs)} languages")

            # Verify something actually changed
            if new_title == old_title and new_locs == locs:
                print(f"  ⏩ No changes needed (already correct)")
                results.append({"video_id": vid_id, "status": "ALREADY_CORRECT", "title": old_title})
                continue

            # Push update (50 quota)
            snippet['title'] = new_title
            if new_desc:
                snippet['description'] = new_desc

            update_body = {
                'id': vid_id,
                'snippet': snippet,
                'localizations': new_locs
            }

            youtube.videos().update(
                part='snippet,localizations',
                body=update_body
            ).execute()
            total_quota += 50

            print(f"  ✅ Updated! (51 quota)")
            results.append({
                "video_id": vid_id,
                "status": "FIXED",
                "old_title": old_title,
                "new_title": new_title,
                "old_ep": fix['old_ep'],
                "new_ep": fix['new_ep'],
                "year": fix['year'],
                "localizations_fixed": len(new_locs),
                "source": fix['source']
            })

        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ ERROR: {error_msg}")
            if 'quotaExceeded' in error_msg:
                print("\n🛑 QUOTA EXCEEDED! Stopping.")
                results.append({"video_id": vid_id, "status": "QUOTA_ERROR"})
                break
            results.append({"video_id": vid_id, "status": "ERROR", "error": error_msg})

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    fixed = sum(1 for r in results if r['status'] == 'FIXED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    skipped = sum(1 for r in results if r['status'] == 'ALREADY_CORRECT')
    print(f"  Fixed:   {fixed}/{len(FIXES)}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors:  {errors}")
    print(f"  Quota:   {total_quota} units")

    # Save report
    report = {
        "date": datetime.now().isoformat(),
        "operation": "maulwurf_episode_number_fix",
        "source": "CZ Wikipedia - Seznam dílů seriálu O krtkovi",
        "db_fixes": db_fixes,
        "youtube_results": results,
        "total_quota": total_quota,
        "summary": {
            "fixed": fixed,
            "errors": errors,
            "skipped": skipped
        }
    }
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'maulwurf_epnum_fix_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  Report: config/maulwurf_epnum_fix_report.json")


if __name__ == '__main__':
    main()
