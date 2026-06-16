import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
INPUT_FILE = CONFIG_DIR / "live_seo_report.json"
OUTPUT_DIR = CONFIG_DIR / "pending_updates"
OUTPUT_FILE = OUTPUT_DIR / f"tags_trim_{Path.cwd().stem}_20260126.json"

# Tags that should be removed if present (spammy/irrelevant or policy-risk)
BLOCKLIST = {
    "Official Audio",
    "official video",
    "Topic",
    "auto-generated",
}

# Maximum number of tags to keep (YouTube recommends minimal role; 5-15)
MAX_TAGS = 12

def load_live_report(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def trim_tags(tags):
    # Remove blocklisted tags (case-insensitive compare)
    filtered = [t for t in tags if t.lower() not in {b.lower() for b in BLOCKLIST}]
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for t in filtered:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(t)
    # Cap to MAX_TAGS
    return deduped[:MAX_TAGS]

def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_live_report(INPUT_FILE)
    items = data.get("results", [])

    proposals = []
    for item in items:
        video_id = item.get("id")
        current_tags = item.get("new_tags") or []
        # If new_tags not present, skip
        if not video_id or not current_tags:
            continue
        trimmed = trim_tags(current_tags)
        if len(current_tags) > len(trimmed):
            proposals.append({
                "id": video_id,
                "action": "update_tags",
                "from_count": len(current_tags),
                "to_count": len(trimmed),
                "new_tags": trimmed,
                "title": item.get("title")
            })

    output = {
        "timestamp": os.environ.get("TIMESTAMP_OVERRIDE") or "2026-01-26",
        "total": len(proposals),
        "note": "Trim tags to <=12 and remove spammy entries per YouTube 2026 guidance.",
        "proposals": proposals
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote proposals: {OUTPUT_FILE} (items={len(proposals)})")

if __name__ == "__main__":
    main()
