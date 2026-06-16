#!/usr/bin/env python3
"""
Build Wochenschau reach fix plan from API-free yt-dlp audit.

Input:
- config/reach_audit_ytdlp_20260504.json
- config/wochenschau_events.json
- config/wochenschau_complete_locations.json

Output:
- config/pending_updates/wochenschau_reach_fix_20260504.json

No API calls. No quota. This creates the metadata payload for later OAuth apply.
"""
import json
import re
from datetime import datetime
from pathlib import Path

AUDIT_PATH = Path("config/reach_audit_ytdlp_20260504.json")
EVENTS_PATH = Path("config/wochenschau_events.json")
LOCATIONS_PATH = Path("config/wochenschau_complete_locations.json")
OUT_PATH = Path("config/pending_updates/wochenschau_reach_fix_20260504.json")

TARGET_LOCS = ["de", "en", "es", "pt", "hi", "id"]

TAG_BASE = [
    "wochenschau",
    "german newsreel",
    "wwii history",
    "historical footage",
    "vintage newsreel",
    "restored",
    "remastered",
    "8K",
    "4K",
    "public domain",
    "documentary",
    "AI enhanced",
]

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def de_date(iso_date):
    year, month, day = iso_date.split("-")
    return f"{day}.{month}.{year}"

def en_date(iso_date):
    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%B %-d, %Y") if False else datetime.strptime(iso_date, "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")

def extract_nr(title):
    match = re.search(r"(?:No\.?|Nr\.?|Newsreel\s+|Wochenschau\s+)(\d{3})", title, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"\b(4\d{2}|5\d{2}|6\d{2}|7\d{2})\b", title)
    return match.group(1) if match else None

def shorten_event(event):
    replacements = {
        "Bialystok-Minsk and Riga": "Bialystok-Minsk",
        "Karl Benz, Western Front, V-2": "Western Front V-2",
        "Yugoslavia and Greece Campaign": "Balkan Campaign",
        "Channel Islands and Air War": "Channel Air War",
        "Refugees, Katowice and Budapest": "Eastern Collapse",
    }
    return replacements.get(event, event)

def build_title(event_en, date_de):
    event = shorten_event(event_en)
    title = f"Wochenschau: {event} ({date_de}) | 8K HQ (4K UHD)"
    if len(title) <= 70:
        return title
    event = event.replace("Conference", "Conf.").replace("Offensive", "Off.").replace("Campaign", "Camp.")
    title = f"Wochenschau: {event} ({date_de}) | 8K HQ (4K UHD)"
    return title[:70].rstrip()

def build_tags(nr, year, event_en, location_desc):
    tags = TAG_BASE + [year, f"Wochenschau {nr}", event_en.lower(), location_desc.lower()]
    out = []
    seen = set()
    for tag in tags:
        clean = str(tag).strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean[:100])
        if len(out) >= 15:
            break
    return out

def build_description(nr, event_de, event_en, note, iso_date, location_desc, video_id):
    date_de = de_date(iso_date)
    date_en = en_date(iso_date)
    year = iso_date.split("-")[0]
    return f"""Classic German WWII newsreel footage, AI remastered and restored in 8K HQ (4K UHD).
Original Deutsche Wochenschau Nr. {nr} from {date_en}, covering {event_en} with historical context and archive location data.

HISTORICAL DOCUMENT - EDUCATIONAL USE ONLY
This footage is wartime propaganda presented in historical context for documentation, research and education.

DE:
Die Deutsche Wochenschau Nr. {nr} vom {date_de}.
{event_de} - {note}
Ort: {location_desc}
Originales Archivmaterial, restauriert fuer moderne 4K- und 8K-Displays.

EN:
German Weekly Newsreel No. {nr}, dated {date_en}.
{event_en} - {note}
Location: {location_desc}
Original archive footage, restored for modern 4K and 8K displays.

ES:
Noticiero Semanal Aleman Nr. {nr} del {date_de}.
{event_en} - documento historico de la Segunda Guerra Mundial.
Ubicacion: {location_desc}

Global search terms:
World War II footage, WWII newsreel, historical documentary, restored archive film, German newsreel, 4K UHD, 8K remastered.
Segunda Guerra Mundial, documentario historico, Perang Dunia II, द्वितीय विश्व युद्ध.

Archive links:
Watch organized archive: https://frai.tv/watch/{video_id}
Project hub: https://www.remaike.IT
YouTube channel: https://www.youtube.com/@remAIke_IT

LIKE if you found this valuable.
COMMENT with the Wochenschau number or event you want next.
SUBSCRIBE for restored historical footage.

#Wochenschau #WWII #{year} #8K #PublicDomain"""

def build_localizations(title, description, nr, event_de, event_en, iso_date, location_desc, video_id):
    date_de = de_date(iso_date)
    year = iso_date.split("-")[0]
    base_link = f"https://frai.tv/watch/{video_id}"
    return {
        "de": {
            "title": f"Deutsche Wochenschau: {event_de} ({date_de}) | 8K HQ (4K UHD)"[:100],
            "description": description,
        },
        "en": {
            "title": title,
            "description": description,
        },
        "es": {
            "title": f"Noticiero aleman: {event_en} ({year}) | 8K HQ (4K UHD)"[:100],
            "description": f"Noticiero aleman historico de la Segunda Guerra Mundial, restaurado en 8K HQ (4K UHD).\nWochenschau Nr. {nr}, {date_de}. Ubicacion: {location_desc}.\nArchivo organizado: {base_link}\nProyecto: https://www.remaike.IT",
        },
        "pt": {
            "title": f"Cinejornal alemao: {event_en} ({year}) | 8K HQ (4K UHD)"[:100],
            "description": f"Cinejornal historico da Segunda Guerra Mundial, remasterizado em 8K HQ (4K UHD).\nWochenschau Nr. {nr}, {date_de}. Localizacao: {location_desc}.\nArquivo organizado: {base_link}\nProjeto: https://www.remaike.IT",
        },
        "hi": {
            "title": f"German WWII Newsreel: {event_en} ({year}) | 8K HQ (4K UHD)"[:100],
            "description": f"द्वितीय विश्व युद्ध का ऐतिहासिक जर्मन न्यूज़रील, 8K HQ (4K UHD) में restored.\nWochenschau No. {nr}, {date_de}. Location: {location_desc}.\nArchive: {base_link}\nProject: https://www.remaike.IT",
        },
        "id": {
            "title": f"Berita Jerman WWII: {event_en} ({year}) | 8K HQ (4K UHD)"[:100],
            "description": f"Rekaman berita Jerman Perang Dunia II, direstorasi dalam 8K HQ (4K UHD).\nWochenschau No. {nr}, {date_de}. Lokasi: {location_desc}.\nArsip: {base_link}\nProyek: https://www.remaike.IT",
        },
    }

def main():
    audit = load_json(AUDIT_PATH)
    events_root = load_json(EVENTS_PATH)
    events = events_root.get("events", events_root)
    locations_root = load_json(LOCATIONS_PATH)
    locations = locations_root.get("locations", locations_root)

    updates = []
    skipped = []
    for video in audit.get("videos", []):
        video_id = video.get("videoId")
        current_title = video.get("title", "")
        nr = extract_nr(current_title)
        if not nr:
            skipped.append({"videoId": video_id, "title": current_title, "reason": "no_nr_found"})
            continue
        event = events.get(nr)
        location_record = locations.get(nr)
        if not event or not location_record:
            skipped.append({"videoId": video_id, "title": current_title, "nr": nr, "reason": "missing_event_or_location"})
            continue
        iso_date = event["date"]
        date_de = de_date(iso_date)
        event_en = event.get("event_en", "World War II")
        event_de = event.get("event_de", event_en)
        note = event.get("note", event_en)
        location_desc = location_record.get("location", {}).get("desc") or location_record.get("location", "Historical location")
        title = build_title(event_en, date_de)
        description = build_description(nr, event_de, event_en, note, iso_date, location_desc, video_id)
        tags = build_tags(nr, iso_date.split("-")[0], event_en, location_desc)
        localizations = build_localizations(title, description, nr, event_de, event_en, iso_date, location_desc, video_id)
        updates.append({
            "videoId": video_id,
            "video_nr": int(nr),
            "current_title": current_title,
            "correct_title": title,
            "title_length": len(title),
            "correct_description": description,
            "correct_tags": tags,
            "correct_category": "27",
            "defaultLanguage": "de",
            "defaultAudioLanguage": "de",
            "localizations": localizations,
            "source_issues": video.get("issues", []),
            "frai_watch_link": f"https://frai.tv/watch/{video_id}",
            "location": location_desc,
        })

    updates.sort(key=lambda item: item["video_nr"])
    result = {
        "_meta": {
            "created": "2026-05-04",
            "source_audit": str(AUDIT_PATH),
            "purpose": "Restore global Wochenschau reach: 4K+8K title, AEO first lines, GEO location, frai.tv/remaike.IT authority links, German audio language and market localizations.",
            "videos_total_in_audit": audit.get("wochenschau_count"),
            "updates_count": len(updates),
            "skipped_count": len(skipped),
            "quota_cost_apply": len(updates) * 50,
            "rules": [
                "Title includes 8K HQ (4K UHD)",
                "No @remAIke_IT in title",
                "Category 27 Education",
                "defaultLanguage=de and defaultAudioLanguage=de",
                "Description first two lines answer global search intent",
                "Description includes https://frai.tv/watch/VIDEO_ID",
                "Description includes https://www.remaike.IT and YouTube channel link",
                "GEO location from config/wochenschau_complete_locations.json",
                "Localizations for de, en, es, pt, hi, id",
                "Max 15 tags",
            ],
        },
        "videos": updates,
        "skipped": skipped,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Updates: {len(updates)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Quota to apply: {len(updates) * 50}")
    print(f"Saved: {OUT_PATH}")
    if skipped:
        print("Skipped examples:")
        for item in skipped[:10]:
            print(f"  {item}")

if __name__ == "__main__":
    main()
