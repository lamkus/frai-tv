#!/usr/bin/env python3
"""Audit titles for Best Practice: keyword first + 8K within first 18 chars"""
import json
import re

def ensure_8k_early(title: str) -> str:
    original = title
    lower = title.lower()

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()

    def insert_after_prefix(t: str) -> str:
        # If colon early, insert after it
        for sep in [":", "–", "-", "|", ")"]:
            idx = t.find(sep)
            if 0 <= idx <= 18:
                return f"{t[:idx+1]} 8K {t[idx+1:].lstrip()}"
        # Otherwise insert after first word
        parts = t.split(" ", 1)
        if len(parts) == 1:
            return f"{parts[0]} 8K"
        return f"{parts[0]} 8K {parts[1]}"

    # Ensure @remAIke_IT at end
    if "@remAIke_IT" not in title:
        title = f"{title} | @remAIke_IT"

    # If no 8K at all, insert early
    if "8k" not in lower:
        title = insert_after_prefix(title)
        return title

    # If 8K already early, keep
    idx = title.lower().find("8k")
    if 0 <= idx <= 18:
        return title

    # Move first 8K occurrence earlier
    title = re.sub(r"\s*\|?\s*8k\s*", " ", title, flags=re.IGNORECASE, count=1).strip()
    title = insert_after_prefix(title)
    return title


def main():
    with open("config/fresh_channel_scan.json", encoding="utf-8") as f:
        data = json.load(f)

    candidates = []
    for v in data.get("videos", []):
        if v.get("kind") != "youtube#video":
            continue
        if v.get("status", {}).get("privacyStatus") != "public":
            continue
        title = v["snippet"]["title"]
        new_title = ensure_8k_early(title)
        if new_title != title:
            candidates.append({
                "id": v["id"],
                "title": title,
                "new_title": new_title
            })

    print(f"Public videos: {data.get('public', 0)}")
    print(f"Candidates for Best Practice update: {len(candidates)}")
    print("Examples:")
    for c in candidates[:15]:
        print(f"[{c['id']}] {c['title'][:70]} -> {c['new_title'][:70]}")

    with open("config/pending_updates/title_best_practice_candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

    print("\nSaved: config/pending_updates/title_best_practice_candidates.json")


if __name__ == "__main__":
    main()
