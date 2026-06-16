#!/usr/bin/env python3
"""
Reach Audit 2026-05-04 (yt-dlp fallback, no API key).

Public channel scan without YouTube API quota. This checks the public-facing data
that affects search and user discovery:
- 4K + 8K title keywords
- Description first two lines (AEO/snippet quality)
- frai.tv / frai.tv/watch/<VIDEO_ID> / remaike.IT / channel links
- GEO location markers in description
- Tags/categories as exposed by yt-dlp
- Subtitles/automatic captions presence

Limitations:
- Cannot read YouTube Data API fields defaultAudioLanguage/defaultLanguage reliably
- Cannot read Data API localizations reliably
Use reach_audit_public_20260504.py for those once YOUTUBE_API_KEY is set.
"""
import json
import re
import sys
from pathlib import Path

import yt_dlp

CHANNEL_URL = "https://www.youtube.com/@remAIke_IT/videos"
OUT_PATH = Path("config/reach_audit_ytdlp_20260504.json")

NEWSREEL_RE = re.compile(
    r"^(wochenschau|deutsche\s+wochenschau|german\s+(wwii\s+)?newsreel|newsreel\s+\d+|ufa\s+sound\s+newsreel)",
    re.IGNORECASE,
)

def extract_flat_channel():
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "ignoreerrors": True,
        "playlistend": 700,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(CHANNEL_URL, download=False)

def extract_video(video_id):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

def audit_video(info):
    video_id = info.get("id", "")
    title = info.get("title", "") or ""
    description = info.get("description", "") or ""
    desc_lower = description.lower()
    tags = info.get("tags") or []
    categories = info.get("categories") or []
    subtitles = info.get("subtitles") or {}
    automatic_captions = info.get("automatic_captions") or {}

    desc_lines = description.splitlines()
    desc_line1 = desc_lines[0].strip() if desc_lines else ""
    desc_line2 = desc_lines[1].strip() if len(desc_lines) > 1 else ""
    first_two = f"{desc_line1} {desc_line2}".lower()

    aeo_terms = ["german", "newsreel", "wwii", "world war", "remastered", "restored", "8k", "4k", "historical"]
    aeo_hits = sum(1 for term in aeo_terms if term in first_two)

    has_4k = bool(re.search(r"\b4K\b", title, re.IGNORECASE))
    has_8k = bool(re.search(r"\b8K\b", title, re.IGNORECASE))
    title_repeated = title.lower()[:25] in desc_line1.lower() if desc_line1 else False
    has_frai = "frai.tv" in desc_lower
    has_frai_deep = f"frai.tv/watch/{video_id.lower()}" in desc_lower
    has_remaike = "remaike.it" in desc_lower
    has_channel = "youtube.com/@remaike_it" in desc_lower
    has_geo = any(marker in description for marker in ["📍", "Ort:", "Location:", "Ubicación:"])
    has_subtitle_signal = bool(subtitles or automatic_captions)
    has_education_category = any(cat.lower() == "education" for cat in categories)

    issues = []
    if not has_4k:
        issues.append("missing_4k_keyword")
    if not has_8k:
        issues.append("missing_8k_keyword")
    if title_repeated:
        issues.append("desc_line1_repeats_title")
    if aeo_hits < 4 or "http" in first_two:
        issues.append("desc_first_two_not_aeo_optimized")
    if not has_frai:
        issues.append("missing_frai_tv_link")
    if not has_frai_deep:
        issues.append("missing_frai_watch_deeplink")
    if not has_remaike:
        issues.append("missing_remaike_it_link")
    if not has_channel:
        issues.append("missing_youtube_channel_link")
    if not has_geo:
        issues.append("missing_geo_location_signal")
    if not has_subtitle_signal:
        issues.append("missing_caption_or_autocaption_signal")
    if categories and not has_education_category:
        issues.append("category_not_education_public_view")
    if len(tags) < 10:
        issues.append("too_few_public_tags")

    return {
        "videoId": video_id,
        "title": title,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "view_count": info.get("view_count"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "categories": categories,
        "tags_count": len(tags),
        "subtitles_langs": sorted(subtitles.keys()),
        "automatic_captions_langs": sorted(automatic_captions.keys())[:30],
        "has_4k_in_title": has_4k,
        "has_8k_in_title": has_8k,
        "desc_line1": desc_line1[:160],
        "desc_line2": desc_line2[:160],
        "aeo_hits_first_two_lines": aeo_hits,
        "has_frai_tv_link": has_frai,
        "has_frai_watch_deeplink": has_frai_deep,
        "has_remaike_it_link": has_remaike,
        "has_youtube_channel_link": has_channel,
        "has_geo_location_signal": has_geo,
        "has_subtitle_signal": has_subtitle_signal,
        "issues": issues,
    }

def main():
    print("Extracting public channel list via yt-dlp...")
    channel = extract_flat_channel()
    entries = [entry for entry in (channel.get("entries") or []) if entry]
    print(f"Public entries discovered: {len(entries)}")

    wochenschau_entries = [
        entry for entry in entries
        if NEWSREEL_RE.search(entry.get("title") or "")
    ]
    print(f"Wochenschau public entries: {len(wochenschau_entries)}")

    audits = []
    for index, entry in enumerate(wochenschau_entries, start=1):
        video_id = entry.get("id")
        title = entry.get("title", "")
        print(f"[{index}/{len(wochenschau_entries)}] {video_id} | {title[:70]}")
        info = extract_video(video_id)
        if not info:
            audits.append({"videoId": video_id, "title": title, "issues": ["extract_failed"]})
            continue
        audits.append(audit_video(info))

    issue_summary = {}
    for audit in audits:
        for issue in audit.get("issues", []):
            issue_summary[issue] = issue_summary.get(issue, 0) + 1

    sorted_by_views = sorted(
        [a for a in audits if isinstance(a.get("view_count"), int)],
        key=lambda item: item["view_count"],
        reverse=True,
    )

    result = {
        "audit_date": "2026-05-04",
        "method": "yt_dlp_no_api_key",
        "channel_url": CHANNEL_URL,
        "total_public_entries": len(entries),
        "wochenschau_count": len(wochenschau_entries),
        "issue_summary": issue_summary,
        "top_10_by_views": sorted_by_views[:10],
        "bottom_10_by_views": sorted_by_views[-10:],
        "videos": audits,
        "limitations": [
            "No Data API defaultAudioLanguage/defaultLanguage/localizations fields",
            "Public videos only; private/draft videos require OAuth",
        ],
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nIssue summary:")
    for issue, count in sorted(issue_summary.items(), key=lambda item: item[1], reverse=True):
        print(f"  {issue}: {count}")
    print(f"\nSaved: {OUT_PATH}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(130)
