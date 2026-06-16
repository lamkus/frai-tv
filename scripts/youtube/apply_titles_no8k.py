#!/usr/bin/env python3
"""Apply Best Practice titles ONLY where no '8K' is present in the title"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def ensure_8k_early(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    lower = title.lower()

    def insert_after_prefix(t: str) -> str:
        for sep in [":", "–", "-", "|", ")"]:
            idx = t.find(sep)
            if 0 <= idx <= 18:
                return f"{t[:idx+1]} 8K {t[idx+1:].lstrip()}"
        parts = t.split(" ", 1)
        if len(parts) == 1:
            return f"{parts[0]} 8K"
        return f"{parts[0]} 8K {parts[1]}"

    if "@remAIke_IT" not in title:
        title = f"{title} | @remAIke_IT"

    if "8k" not in lower:
        return insert_after_prefix(title)

    idx = title.lower().find("8k")
    if 0 <= idx <= 18:
        return title

    title = re.sub(r"\s*\|?\s*8k\s*", " ", title, flags=re.IGNORECASE, count=1).strip()
    return insert_after_prefix(title)


def main():
    with open("config/fresh_channel_scan.json", encoding="utf-8") as f:
        data = json.load(f)

    targets = []
    for v in data.get("videos", []):
        if v.get("kind") != "youtube#video":
            continue
        if v.get("status", {}).get("privacyStatus") != "public":
            continue
        title = v["snippet"]["title"]
        if "8k" not in title.lower():
            targets.append({"id": v["id"], "title": title})

    print(f"Public videos without 8K in title: {len(targets)}")

    if not targets:
        return

    with open("config/youtube_oauth.json") as f:
        oauth = json.load(f)

    creds = Credentials(
        token=oauth["token"],
        refresh_token=oauth["refresh_token"],
        token_uri=oauth["token_uri"],
        client_id=oauth["client_id"],
        client_secret=oauth["client_secret"],
    )

    youtube = build("youtube", "v3", credentials=creds)

    updated = 0
    report = []

    for item in targets:
        video_id = item["id"]
        current = youtube.videos().list(part="snippet", id=video_id).execute()
        if not current["items"]:
            continue

        snippet = current["items"][0]["snippet"]
        title = snippet["title"]
        new_title = ensure_8k_early(title)

        if not new_title.strip():
            report.append({"id": video_id, "title": title, "new_title": new_title, "updated": False, "error": "empty_title"})
            continue

        if new_title == title:
            report.append({"id": video_id, "title": title, "new_title": new_title, "updated": False})
            continue

        try:
            snippet["title"] = new_title
            youtube.videos().update(
                part="snippet",
                body={"id": video_id, "snippet": snippet}
            ).execute()

            report.append({"id": video_id, "title": title, "new_title": new_title, "updated": True})
            updated += 1
        except Exception as exc:
            report.append({"id": video_id, "title": title, "new_title": new_title, "updated": False, "error": str(exc)})

    with open("config/pending_updates/title_no8k_update_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Updated: {updated}")
    print("Report saved: config/pending_updates/title_no8k_update_report.json")


if __name__ == "__main__":
    main()
