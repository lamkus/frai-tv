#!/usr/bin/env python3
"""Rename draft (private) videos to Best Practice title format"""
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

    # Pull private videos via search (drafts)
    drafts = []
    next_page = None
    while True:
        res = youtube.search().list(
            part="snippet",
            forMine=True,
            type="video",
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in res.get("items", []):
            vid = item["id"]["videoId"]
            drafts.append(vid)

        next_page = res.get("nextPageToken")
        if not next_page:
            break

    # Fetch details
    report = []
    updated = 0
    for i in range(0, len(drafts), 50):
        batch = drafts[i:i+50]
        vids = youtube.videos().list(
            part="snippet,status",
            id=",".join(batch)
        ).execute()

        for v in vids.get("items", []):
            if v.get("status", {}).get("privacyStatus") != "private":
                continue

            title = v["snippet"]["title"]
            new_title = ensure_8k_early(title)

            if new_title == title:
                report.append({"id": v["id"], "title": title, "new_title": new_title, "updated": False})
                continue

            v["snippet"]["title"] = new_title
            youtube.videos().update(
                part="snippet",
                body={"id": v["id"], "snippet": v["snippet"]}
            ).execute()

            report.append({"id": v["id"], "title": title, "new_title": new_title, "updated": True})
            updated += 1

    with open("config/pending_updates/draft_seo_rename_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Drafts processed: {len(report)}")
    print(f"Drafts updated: {updated}")
    print("Report saved: config/pending_updates/draft_seo_rename_report.json")


if __name__ == "__main__":
    main()
