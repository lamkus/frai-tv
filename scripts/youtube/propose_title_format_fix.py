import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
INPUT_FILE = CONFIG_DIR / "live_seo_report.json"
OUTPUT_DIR = CONFIG_DIR / "pending_updates"
OUTPUT_FILE = OUTPUT_DIR / "title_format_fix_20260126.json"

def title_needs_fix(title: str) -> bool:
    if not title:
        return False
    t = title.strip()
    # Soundies should start with "Soundie:" and include brand suffix
    needs_prefix = t.lower().startswith("soundie ") or t.lower().startswith("soundie:") is False
    needs_brand = "@remAIke_IT" not in t
    needs_quality = "8K" not in t
    return needs_prefix or needs_brand or needs_quality

def propose_title(title: str) -> str:
    t = title.strip()
    # Normalize starting word
    if t.lower().startswith("soundie"):
        # Extract rest after the word 'soundie'
        rest = t[len("soundie"):].strip(" :-")
        # Simple cleanup: title case the rest
        rest_norm = rest.title()
        base = f"Soundie: {rest_norm}"
    else:
        base = t
    # Ensure quality and brand suffix present
    suffix = " | 8K HQ | @remAIke_IT"
    if base.endswith(suffix):
        return base
    else:
        return base + suffix

def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    proposals = []
    for item in data.get("results", []):
        title = item.get("title") or ""
        if title_needs_fix(title):
            proposals.append({
                "id": item.get("id"),
                "action": "update_title",
                "old_title": title,
                "new_title": propose_title(title)
            })

    output = {
        "timestamp": "2026-01-26",
        "total": len(proposals),
        "note": "Normalize Soundie titles to 'Soundie: <Title> | 8K HQ | @remAIke_IT'",
        "proposals": proposals
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote proposals: {OUTPUT_FILE} (items={len(proposals)})")

if __name__ == "__main__":
    main()
