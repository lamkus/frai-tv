#!/usr/bin/env python3
"""Verbleibende Entwürfe anzeigen"""
import json
from pathlib import Path

scan = json.loads(Path("config/full_channel_scan.json").read_text(encoding="utf-8"))
private = [v for v in scan["all_videos"] if v["status"] == "private"]

print("Verbleibende private Entwuerfe:")
print("=" * 60)

for v in private:
    t = v["title"]
    vid = v["id"]
    # Skip bereits optimierte
    if "Soundie:" in t or "BraveStarr (" in t:
        continue
    print(f"  {vid} | {t[:50]}")
