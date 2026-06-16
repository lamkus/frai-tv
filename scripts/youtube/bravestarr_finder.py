#!/usr/bin/env python3
"""BraveStarr Videos finden und analysieren"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "config/videos.json").read_text(encoding="utf-8"))

# Suche nach BraveStarr
keywords = ["brave", "bravestar", "marshal", "new texas"]
videos = []

for v in data["videos"]:
    title = v.get("title", "").lower()
    if any(kw in title for kw in keywords):
        videos.append(v)

print(f"BraveStarr Videos gefunden: {len(videos)}\n")
for v in videos:
    print(f"ID: {v['id']}")
    print(f"Title: {v['title']}")
    print(f"Tags: {len(v.get('tags', []))}")
    print("-" * 60)
