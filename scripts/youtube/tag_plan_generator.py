#!/usr/bin/env python3
"""Offline YouTube tag plan generator (quota-safe).

- Reads local cache: config/videos.json
- Generates per-video tag suggestions that satisfy MANA_RULES:
  - min 20 tags
  - max 500 characters total (comma-separated)
- Writes:
  - config/tags_plan.json (per video)
  - config/tags_plan_report.json (summary stats)

No YouTube API calls.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
CONFIG_VIDEOS = ROOT / "config" / "videos.json"
OUT_PLAN = ROOT / "config" / "tags_plan.json"
OUT_REPORT = ROOT / "config" / "tags_plan_report.json"


@dataclass(frozen=True)
class TagResult:
    tags: List[str]
    tag_string: str
    tag_chars: int


def _normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _clean_tag(tag: str) -> str:
    tag = str(tag or "")
    tag = tag.replace("#", " ")
    tag = _normalize_spaces(tag)
    # YouTube tags can contain many chars, but keep them tidy.
    tag = tag.strip(" ,;\t\n\r")
    return tag


def _dedupe_preserve_order(tags: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for t in tags:
        t = _clean_tag(t)
        if not t:
            continue
        key = t.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _tag_string(tags: List[str]) -> str:
    # How YouTube internally counts isn’t perfectly documented, but
    # comma-separated length is a good proxy for Studio input limit.
    return ",".join(tags)


def _truncate_to_500_chars(tags: List[str], min_tags: int) -> TagResult:
    kept: List[str] = []
    for tag in tags:
        candidate = kept + [tag]
        s = _tag_string(candidate)
        if len(s) <= 500:
            kept = candidate
        else:
            break

    # If we fell under min_tags, try to backfill with very short tags.
    # (Only if there’s room; otherwise we keep the best possible set.)
    if len(kept) < min_tags:
        short_pool = [
            "8K",
            "4K",
            "UHD",
            "HD",
            "restored",
            "remastered",
            "classic",
            "vintage",
            "animation",
            "cartoon",
            "public domain",
        ]
        for t in short_pool:
            if t.casefold() in {x.casefold() for x in kept}:
                continue
            candidate = kept + [t]
            s = _tag_string(candidate)
            if len(s) <= 500:
                kept = candidate
            if len(kept) >= min_tags:
                break

    s = _tag_string(kept)
    return TagResult(tags=kept, tag_string=s, tag_chars=len(s))


def extract_year(text: str) -> Optional[int]:
    text = text or ""
    # Prefer explicit (1933)
    m = re.search(r"\((\d{4})\)", text)
    if m:
        y = int(m.group(1))
        if 1890 <= y <= 1985:
            return y

    # Fallback: any 4-digit year
    m = re.search(r"\b(19\d{2})\b", text)
    if m:
        y = int(m.group(1))
        if 1890 <= y <= 1985:
            return y

    return None


def detect_language(title: str, description: str) -> str:
    t = f"{title} {description}".lower()
    if "🇩🇪" in t or " deutsch" in t or "german" in t:
        return "de"
    if "🇬🇧" in t or " english" in t:
        return "en"
    return "unknown"


def detect_series(title: str, description: str) -> Optional[str]:
    t = f"{title} {description}".lower()

    series_rules = [
        ("alfred_j_kwak", ["alfred j", "alfred j.", "alfred jodokus", "kwak", "quack"]),
        ("betty_boop", ["betty boop"]),
        ("popeye", ["popeye"]),
        ("superman_fleischer", ["fleischer", "superman"]),
        ("casper", ["casper", "friendly ghost"]),
        ("felix", ["felix the cat", "felix"]),
        ("astro_boy", ["astro boy"]),
        ("dinner_for_one", ["dinner for one"]),
    ]

    for key, needles in series_rules:
        if all(any(n in t for n in [needle]) for needle in needles[:1]):
            # Special handling: Alfred needs at least one of kwak/quack too.
            if key == "alfred_j_kwak":
                if "alfred" in t and ("kwak" in t or "quack" in t):
                    return key
                continue
            return key

    return None


def series_tag_pack(series_key: str) -> List[str]:
    packs = {
        "alfred_j_kwak": [
            "Alfred J. Kwak",
            "Alfred Jodokus Quack",
            "Alfred Jodokus Kwak",
            "Alfred Jodocus Kwak",
            "Alfred Jodocus Quack",
            "Kwak",
            "Quack",
            "Alfred der kleine Rabe",
            "Herman van Veen",
            "Harald Siepermann",
            "Zeichentrick",
            "Zeichentrickserie",
            "Kinder",
            "Kinderserie",
            "Deutsch",
            "German",
            "nostalgie",
            "80er",
            "90er",
        ],
        "betty_boop": [
            "Betty Boop",
            "Fleischer Studios",
            "classic cartoon",
            "classic cartoons",
            "vintage animation",
            "golden age animation",
            "1930s",
            "jazz age",
            "public domain",
        ],
        "popeye": [
            "Popeye",
            "Popeye the Sailor",
            "Fleischer Studios",
            "spinach",
            "classic cartoons",
            "vintage animation",
            "public domain",
        ],
        "superman_fleischer": [
            "Superman",
            "Fleischer Superman",
            "Fleischer Studios",
            "superhero",
            "classic cartoons",
            "vintage animation",
        ],
        "casper": [
            "Casper",
            "Casper the Friendly Ghost",
            "Famous Studios",
            "classic cartoons",
            "vintage animation",
        ],
        "felix": [
            "Felix the Cat",
            "Felix",
            "classic cartoons",
            "silent cartoon",
            "vintage animation",
            "public domain",
        ],
        "astro_boy": [
            "Astro Boy",
            "anime",
            "classic anime",
            "science fiction",
            "Deutsch",
            "German",
        ],
        "dinner_for_one": [
            "Dinner for One",
            "Silvester",
            "New Year's Eve",
            "Neujahr",
            "classic tv",
        ],
    }
    return packs.get(series_key, [])


def category_tag_pack(title: str, description: str) -> List[str]:
    t = f"{title} {description}".lower()

    if any(k in t for k in ["cartoon", "animation", "zeichentrick", "anime"]):
        return [
            "cartoon",
            "animation",
            "classic animation",
            "vintage animation",
        ]

    if any(k in t for k in ["silent", "classic film", "vintage movie", "movie"]):
        return [
            "classic film",
            "vintage movie",
            "classic cinema",
        ]

    if any(k in t for k in ["porsche", "stockholm", "getaway"]):
        return [
            "Porsche 911",
            "car culture",
            "street racing",
            "Stockholm",
            "automotive",
        ]

    return ["classic", "vintage"]


def quality_tag_pack(title: str, description: str) -> List[str]:
    t = f"{title} {description}".lower()
    out = ["8K", "4K UHD", "restored", "remastered", "AI upscaled", "AI restoration"]

    if "best online version" in t:
        out.append("best online version")

    return out


def brand_tag_pack() -> List[str]:
    return ["remAIke", "@remAIke_IT", "reAImastered", "FRai.TV"]


def build_tags_for_video(title: str, description: str) -> TagResult:
    language = detect_language(title, description)
    series = detect_series(title, description)
    year = extract_year(title) or extract_year(description)

    high: List[str] = []
    medium: List[str] = []
    low: List[str] = []

    # Primary keyword first
    if series == "alfred_j_kwak":
        high.append("Alfred J. Kwak")
    elif series == "betty_boop":
        high.append("Betty Boop")
    elif series == "popeye":
        high.append("Popeye")
    elif series == "superman_fleischer":
        high.append("Superman")
    elif series == "astro_boy":
        high.append("Astro Boy")
    elif series == "dinner_for_one":
        high.append("Dinner for One")

    if year:
        medium.extend([str(year), f"{(year // 10) * 10}s"])

    if language == "de":
        medium.extend(["Deutsch", "German"])
    elif language == "en":
        medium.extend(["English"])

    # Packs
    if series:
        high.extend(series_tag_pack(series))

    medium.extend(category_tag_pack(title, description))
    medium.extend(quality_tag_pack(title, description))
    medium.extend(brand_tag_pack())

    # Gentle keyword extraction (avoid spam)
    words = re.findall(r"\b[a-zA-Z]{4,}\b", title)
    keywords = []
    for w in words:
        lw = w.lower()
        if lw in {"best", "online", "version", "deutsch", "german", "restored", "remastered"}:
            continue
        keywords.append(w)
    low.extend(keywords[:6])

    # De-dupe and enforce limits
    tags = _dedupe_preserve_order(high + medium + low)

    # Ensure min 20 tags and max 500 chars
    return _truncate_to_500_chars(tags, min_tags=20)


def main() -> None:
    if not CONFIG_VIDEOS.exists():
        raise SystemExit(f"Missing: {CONFIG_VIDEOS}")

    data = json.loads(CONFIG_VIDEOS.read_text(encoding="utf-8"))
    videos = data.get("videos") or []

    plan_items = []
    counts = []
    char_counts = []
    below_20 = 0

    tag_frequency = Counter()

    for v in videos:
        video_id = v.get("id")
        title = v.get("title") or ""
        description = v.get("description") or ""

        res = build_tags_for_video(title, description)

        counts.append(len(res.tags))
        char_counts.append(res.tag_chars)
        if len(res.tags) < 20:
            below_20 += 1

        for t in res.tags:
            tag_frequency[t.casefold()] += 1

        plan_items.append(
            {
                "id": video_id,
                "title": title,
                "suggested_tags": res.tags,
                "tags_csv": res.tag_string,
                "tags_chars": res.tag_chars,
                "tags_count": len(res.tags),
            }
        )

    OUT_PLAN.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "source": str(CONFIG_VIDEOS.relative_to(ROOT)).replace("\\", "/"),
                "count": len(plan_items),
                "videos": plan_items,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    report = {
        "generated_at": datetime.now().isoformat(),
        "videos": len(plan_items),
        "tags_count_min": min(counts) if counts else 0,
        "tags_count_avg": (sum(counts) / len(counts)) if counts else 0,
        "tags_count_max": max(counts) if counts else 0,
        "tags_chars_min": min(char_counts) if char_counts else 0,
        "tags_chars_avg": (sum(char_counts) / len(char_counts)) if char_counts else 0,
        "tags_chars_max": max(char_counts) if char_counts else 0,
        "below_min_20_tags": below_20,
        "top_tags": [
            {"tag": k, "count": c}
            for k, c in tag_frequency.most_common(30)
        ],
    }

    OUT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote: {OUT_PLAN}")
    print(f"Wrote: {OUT_REPORT}")


if __name__ == "__main__":
    main()
