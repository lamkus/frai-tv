#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry script for the 18 videos that hit quota limits.
Run after quota resets (midnight Pacific = 9:00 AM CET).
"""
import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

OAUTH_PATH   = r"D:\remaike.TV\config\youtube_oauth.json"
REPORT_PATH  = r"D:\remaike.TV\config\critical_title_fix_2026_04_14.json"

def load_oauth():
    with open(OAUTH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def refresh_access_token(oauth):
    data = urllib.parse.urlencode({
        "client_id": oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "refresh_token": oauth["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    oauth["token"] = result["access_token"]
    with open(OAUTH_PATH, "w", encoding="utf-8") as f:
        json.dump(oauth, f, indent=2, ensure_ascii=False)
    print("[AUTH] Token refreshed.")
    return oauth

def yt_update_video(token, video_id, snippet_patch, category_id=None):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("items"):
        return {"error": f"Video {video_id} not found"}
    item = data["items"][0]
    snippet = item["snippet"]
    for k, v in snippet_patch.items():
        snippet[k] = v
    if category_id:
        snippet["categoryId"] = category_id
    snippet.pop("thumbnails", None)
    body = json.dumps({"id": video_id, "snippet": snippet}, ensure_ascii=False).encode("utf-8")
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet"
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8")}

# Remaining videos from the report
RETRY_LIST = [
    # 5 Wochenschau category fixes (27 -> 1, no title change)
    {"video_id": "iEEvt-s1XhQ", "tasks": ["fix_wochenschau_category"], "title_change": None, "new_cat": "1"},
    {"video_id": "w2UvksMOs3c", "tasks": ["fix_wochenschau_category"], "title_change": None, "new_cat": "1"},
    {"video_id": "6YLPpJLgVXk", "tasks": ["fix_wochenschau_category"], "title_change": None, "new_cat": "1"},
    {"video_id": "T-EsdXGhqog", "tasks": ["fix_wochenschau_category"], "title_change": None, "new_cat": "1"},
    {"video_id": "3rB80OGKzrg", "tasks": ["fix_wochenschau_category"], "title_change": None, "new_cat": "1"},
    # 13 Full Movie additions
    {"video_id": "jPzc1XtrMds", "tasks": ["add_full_movie"],
     "title_change": "Asterix \u2013 Sieg \u00fcber C\u00e4sar (1985) | \U0001f1e9\U0001f1ea German | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "70Ni30lbXRc", "tasks": ["add_full_movie"],
     "title_change": "Gl\u00fccksb\u00e4rchis: Abenteuer im Wunderland (1987) | Deutsch | Full Movie | 8K (4K UHD)", "new_cat": None},
    {"video_id": "HCj_w3pBxlc", "tasks": ["add_full_movie"],
     "title_change": "Blackmail (1929) | Hitchcock's First Talkie | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "V9zhjG_6cHU", "tasks": ["add_full_movie"],
     "title_change": "New Year's Eve 1950s TV Supercut (74 Min) | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "q_Mgt80t5JA", "tasks": ["add_full_movie"],
     "title_change": "Guy Lombardo New Year's Eve (1957) | CBS Kinescope | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "cCNm8nNHing", "tasks": ["add_full_movie"],
     "title_change": "Glenn Morris Only Film as Tarzan Upgrade Complete | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "8lLtNb11NKU", "tasks": ["add_full_movie"],
     "title_change": "Metropolis (1927) | Fritz Lang | Sci-Fi Masterpiece | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "b4cqLlJ7t4M", "tasks": ["add_full_movie"],
     "title_change": "Phantom of the Opera (1925) | Lon Chaney | Silent | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "pqrCPhUCpxE", "tasks": ["add_full_movie"],
     "title_change": "Voyage to the Planet of Prehistoric Women (1968) | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "dGD2CeoZX68", "tasks": ["add_full_movie"],
     "title_change": "A Christmas Carol (1984) | George C. Scott | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "exukLdxugy8", "tasks": ["add_full_movie"],
     "title_change": "H\u00e4xan (1922) | Witchcraft Through the Ages | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "Nzi6aRKDoEs", "tasks": ["add_full_movie"],
     "title_change": "Nosferatu (1922) | F.W. Murnau | Silent Horror | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
    {"video_id": "5WVJHELSD7A", "tasks": ["add_full_movie"],
     "title_change": "The Cabinet of Dr. Caligari (1920) | Silent Horror | Full Movie | 8K HQ (4K UHD)", "new_cat": None},
]

def main():
    print("=" * 60)
    print("RETRY: 18 remaining videos (quota-limited)")
    print("=" * 60)

    oauth = load_oauth()
    oauth = refresh_access_token(oauth)
    token = oauth["token"]

    report = json.load(open(REPORT_PATH, "r", encoding="utf-8"))
    success = 0
    errors = 0

    for i, item in enumerate(RETRY_LIST):
        vid = item["video_id"]
        snippet_patch = {}
        if item["title_change"]:
            snippet_patch["title"] = item["title_change"]

        print(f"[{i+1}/{len(RETRY_LIST)}] {'+'.join(item['tasks'])} | {vid}")
        try:
            result = yt_update_video(token, vid, snippet_patch, item["new_cat"])
            if "error" in result:
                if "401" in str(result.get("error", "")):
                    oauth = refresh_access_token(oauth)
                    token = oauth["token"]
                    result = yt_update_video(token, vid, snippet_patch, item["new_cat"])
                if "error" in result:
                    print(f"  -> ERROR: {result['error']}")
                    errors += 1
                    continue
            t = result.get("snippet", {}).get("title", "?")
            c = result.get("snippet", {}).get("categoryId", "?")
            print(f"  -> OK: title=\"{t}\" cat={c}")
            # Update report
            report["errors"] = [e for e in report["errors"] if e["video_id"] != vid]
            report["results"].append({
                "video_id": vid, "tasks": item["tasks"],
                "new_title": t, "new_category": c, "status": "success_retry"
            })
            success += 1
        except Exception as e:
            print(f"  -> EXCEPTION: {e}")
            errors += 1

    report["summary"]["success"] += success
    report["summary"]["errors"] = len(report["errors"])
    report["summary"]["retry_success"] = success
    report["summary"]["retry_errors"] = errors

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nRETRY DONE: {success} success, {errors} errors")

if __name__ == "__main__":
    main()
