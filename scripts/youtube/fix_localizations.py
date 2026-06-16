#!/usr/bin/env python3
"""
fix_localizations.py — Add missing EN/DE localizations to 28 videos.

Reads config/localizations_scan_2026_02_19.json, generates the missing
language localization for each video, then updates via YouTube API.

Usage:
    python fix_localizations.py              # Dry-run (default)
    python fix_localizations.py --apply      # Actually update on YouTube

Quota: ~1,428 Units (28 × 51: 1 read + 50 write each)
"""

import json
import os
import sys
import re
from datetime import datetime

# ── OAuth ──────────────────────────────────────────────────────────
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = os.path.join(BASE, "token.json")
CLIENT_SECRET = os.path.join(BASE, "config", "youtube_oauth.json")
SCAN_FILE = os.path.join(BASE, "config", "localizations_scan_2026_02_19.json")
REPORT_FILE = os.path.join(BASE, "config", "localizations_fix_report.json")

# ── EN Translations for DE-only videos ─────────────────────────────
# Alfred J. Kwak episode titles (from Wikipedia EN)
ALFRED_EN_TITLES = {
    "E01": "Hello, I'm Alfred!",
    "E08": "The Spy",
    "E10": "The Genie in the Bottle",
    "E11": "Humans Are on the Loose!",
    "E13": "Stop the Thief!",
    "E16": "The Journey to the South Pole",
    "E17": "Rescue from Outer Space",
    "E18": "In the Eternal Ice",
    "E36": "Michael Duckson",
    "E38": "Trouble with the Neighbours",
    "E49": "The Rainbow",
}

# Krtek/Maulwurf episode titles
KRTEK_EN_TITLES = {
    "E23": "The Mole in the Desert",
    "E24": "The Mole and the Christmas",
    "E42": "The Mole and the Flood",
    "E43": "The Mole and the Snowman",
}

# BraveStarr
BRAVESTARR_EN_TITLES = {
    "1/65": "New Texas Blues",
    "4/65": "Skuzz and Fuzz",
    "Intro": "Intro",
}


def get_youtube():
    """Authenticate via OAuth and return youtube service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def extract_episode_key(title):
    """Extract episode key from title for lookup."""
    # Alfred: (E08), (E01), etc.
    m = re.search(r'\(E(\d+)\)', title)
    if m:
        return f"E{m.group(1).zfill(2)}"
    # BraveStarr: (1/65), (4/65)
    m = re.search(r'\((\d+/65)\)', title)
    if m:
        return m.group(1)
    # Krtek: E24, E42, etc.
    m = re.search(r'Krtek E(\d+)', title)
    if m:
        return f"E{m.group(1).zfill(2)}"
    return None


def detect_category(title):
    """Detect video category from title."""
    if "Alfred J. Kwak" in title:
        if "Trailer" in title:
            return "alfred_trailer"
        return "alfred"
    if "Wochenschau" in title:
        return "wochenschau"
    if "BraveStarr" in title:
        if "Intro" in title:
            return "bravestarr_intro"
        return "bravestarr"
    if "Krtek" in title or "Maulwurf" in title:
        return "krtek"
    if "7. Sinn" in title:
        return "7sinn"
    if "NASA" in title or "Apollo" in title or "Skylab" in title:
        return "nasa"
    return "other"


def generate_en_title(video):
    """Generate English title for a DE-only video."""
    title = video["title"]
    cat = detect_category(title)

    if cat == "alfred":
        ep_key = extract_episode_key(title)
        en_ep = ALFRED_EN_TITLES.get(ep_key, None)
        if en_ep:
            # Alfred J. Kwak (E08) The Spy | EN | 8K HQ (4K UHD)
            return re.sub(
                r'\(E\d+\)\s+[^|]+\|\s*DE\s*\|',
                f'({ep_key}) {en_ep} | EN |',
                title
            )
        return title.replace("| DE |", "| EN |")

    elif cat == "alfred_trailer":
        return "Alfred J. Kwak / Quack – Animated Series Trailer | 8K HQ (4K UHD)"

    elif cat == "wochenschau":
        # Already has English event name, title is fine for EN
        return title

    elif cat == "bravestarr":
        ep_key = extract_episode_key(title)
        en_ep = BRAVESTARR_EN_TITLES.get(ep_key, None)
        if en_ep:
            if "Deutsch" in title:
                return title.replace("Deutsch", "English").replace("Das Musikfestival", en_ep)
            # BraveStarr (4/65): Skuzz and Fuzz (1987) | 8K HQ (4K UHD) — already EN
            return title
        return title

    elif cat == "bravestarr_intro":
        return "BraveStarr Intro | 8K HQ (4K UHD) | English"

    elif cat == "krtek":
        ep_key = extract_episode_key(title)
        en_ep = KRTEK_EN_TITLES.get(ep_key, None)
        if en_ep:
            # Krtek E24: The Mole and the Christmas (1975) | 8K HQ (4K UHD)
            return re.sub(
                r'Krtek E\d+:\s+[^(]+',
                f'Krtek {ep_key[1:]}: {en_ep} ',
                title
            )
        return title

    elif cat == "7sinn":
        # Der 7. Sinn: Frauen am Steuer → The 7th Sense: Women at the Wheel
        return (title
                .replace("Der 7. Sinn:", "The 7th Sense:")
                .replace("Frauen am Steuer", "Women at the Wheel")
                .replace("Teil 1", "Part 1")
                .replace("Teil 3", "Part 3"))

    return title


def generate_de_title(video):
    """Generate German title for an EN-only video (NASA)."""
    title = video["title"]

    if "Skylab Space Station" in title:
        return title.replace("Skylab Space Station", "Skylab Raumstation")
    elif "Skylab 2: Launch" in title:
        return title.replace("Skylab 2: Launch", "Skylab 2: Start")
    elif "Apollo 11: Descent & Landing" in title:
        return title.replace("Apollo 11: Descent & Landing", "Apollo 11: Abstieg und Landung")
    elif "Apollo 11 Moonwalk" in title:
        return title.replace("Apollo 11 Moonwalk", "Apollo 11 Mondspaziergang")
    return title


def generate_en_description(video, full_desc):
    """Generate English description for a DE-only video."""
    cat = detect_category(video["title"])

    if cat in ("alfred", "alfred_trailer"):
        # The description already starts with EN text for newer Alfred videos
        # Just ensure the first line is in English
        if full_desc.startswith("🎬 Alfred J. Kwak"):
            # Already has EN content at beginning, use as-is for EN loc
            return full_desc
        # For older format, prepend EN intro
        en_title = generate_en_title(video)
        return f"🎬 {en_title}\n\n{full_desc}"

    elif cat == "wochenschau":
        # Description starts with ⚠️ HISTORISCHES DOKUMENT, add EN at top
        en_disclaimer = (
            "⚠️ HISTORICAL DOCUMENT — This video shows original NS propaganda newsreel footage. "
            "It serves exclusively for historical documentation and education. "
            "The content shown does NOT reflect the views of the uploader.\n\n"
        )
        # Keep the rest of the description
        return en_disclaimer + full_desc

    elif cat in ("bravestarr", "bravestarr_intro"):
        return full_desc  # Already has EN content mixed in

    elif cat == "krtek":
        # Replace German Krtek description intro
        return full_desc.replace(
            "Der kleine Maulwurf (Krtek)",
            "The Little Mole (Krtek)"
        )

    elif cat == "7sinn":
        return full_desc.replace(
            "Der 7. Sinn:", "The 7th Sense:"
        ).replace(
            "Frauen am Steuer", "Women at the Wheel"
        )

    return full_desc


def generate_de_description(video, full_desc):
    """Generate German description for an EN-only video (NASA)."""
    title = video["title"]

    if "Skylab" in title or "Apollo" in title:
        de_intro = (
            "🚀 " + generate_de_title(video).split("|")[0].strip() +
            " — Archivmaterial der NASA, KI-remastered in atemberaubender 8K-Qualität.\n\n"
        )
        return de_intro + full_desc

    return full_desc


def main():
    apply = "--apply" in sys.argv
    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== Localization Fix [{mode}] ===\n")

    # Load scan results
    with open(SCAN_FILE, "r", encoding="utf-8") as f:
        scan = json.load(f)

    videos = scan["videos"]
    print(f"📋 {len(videos)} videos to process\n")

    youtube = get_youtube()
    quota_used = 0
    results = []

    for i, v in enumerate(videos, 1):
        vid = v["id"]
        title = v["title"]
        has_en = v["has_en"]
        has_de = v["has_de"]
        cat = detect_category(title)
        need_lang = "en" if not has_en else "de"

        print(f"[{i:02d}/{len(videos)}] {title[:60]}")
        print(f"  Category: {cat} | Need: {need_lang.upper()}")

        # Fetch current video data
        try:
            resp = youtube.videos().list(
                part="snippet,localizations",
                id=vid
            ).execute()
            quota_used += 1
        except Exception as e:
            print(f"  ❌ Fetch error: {e}")
            results.append({"id": vid, "title": title, "status": "fetch_error", "error": str(e)})
            continue

        if not resp.get("items"):
            print(f"  ❌ Video not found!")
            results.append({"id": vid, "title": title, "status": "not_found"})
            continue

        item = resp["items"][0]
        snippet = item.get("snippet", {})
        existing_locs = item.get("localizations", {})
        full_desc = snippet.get("description", "")

        # Build localizations dict (keep existing + add new)
        locs = dict(existing_locs)

        if need_lang == "en":
            en_title = generate_en_title(v)
            en_desc = generate_en_description(v, full_desc)
            locs["en"] = {"title": en_title, "description": en_desc}
            print(f"  + EN: {en_title[:60]}")
        else:
            de_title = generate_de_title(v)
            de_desc = generate_de_description(v, full_desc)
            locs["de"] = {"title": de_title, "description": de_desc}
            print(f"  + DE: {de_title[:60]}")

        result_entry = {
            "id": vid,
            "title": title,
            "category": cat,
            "added_lang": need_lang,
            "new_title": locs[need_lang]["title"],
        }

        if apply:
            try:
                # YouTube requires defaultLanguage in snippet when setting localizations
                default_lang = v.get("default_lang", "de")
                update_body = {
                    "id": vid,
                    "snippet": {
                        "title": snippet.get("title", title),
                        "description": snippet.get("description", ""),
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", "1"),
                        "defaultLanguage": default_lang,
                    },
                    "localizations": locs
                }
                youtube.videos().update(
                    part="snippet,localizations",
                    body=update_body
                ).execute()
                quota_used += 50
                result_entry["status"] = "updated"
                print(f"  ✅ Updated (defaultLanguage={default_lang})")
            except Exception as e:
                result_entry["status"] = "update_error"
                result_entry["error"] = str(e)
                print(f"  ❌ Update error: {e}")
        else:
            result_entry["status"] = "dry_run"
            print(f"  🔍 [DRY-RUN] Would update")

        results.append(result_entry)
        print()

    # Summary
    updated = sum(1 for r in results if r["status"] == "updated")
    dry_run = sum(1 for r in results if r["status"] == "dry_run")
    errors = sum(1 for r in results if "error" in r.get("status", ""))

    print(f"\n{'='*50}")
    print(f"📊 Results: {updated} updated, {dry_run} dry-run, {errors} errors")
    print(f"📊 Quota used: {quota_used} units")

    # Save report
    report = {
        "date": datetime.now().isoformat(),
        "mode": mode,
        "total": len(videos),
        "updated": updated,
        "dry_run": dry_run,
        "errors": errors,
        "quota_used": quota_used,
        "results": results,
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"💾 Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
