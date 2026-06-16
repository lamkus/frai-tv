"""Quick validation of video_master_db_v2.json"""
import json
from collections import Counter

db = json.load(open("D:/remaike.TV/config/video_master_db_v2.json", encoding="utf-8"))

print("=" * 72)
print("  VIDEO MASTER DB v2 — VALIDATION")
print("=" * 72)

# 1. Total coverage
pub = db["stats"]["by_privacy"].get("public", 0)
priv = db["stats"]["by_privacy"].get("private", 0)
print(f"\n  📺 Total: {db['meta']['total_videos']} videos ({pub} public, {priv} private)")
print(f"  📋 Playlists: {len(db['playlists'])}")

# 2. Series detection
print(f"\n  📊 Series Detection:")
for s, d in sorted(db["stats"]["by_series"].items(), key=lambda x: -x[1]["count"]):
    print(f"     {s:20s}: {d['count']:3d} videos | {d['total_views']:>8,d} views | SEO {d['avg_score']:.1f}")

# 3. Spot-check entries
print(f"\n  🔍 Sample Entries:")
for series in ["krtek", "betty_boop", "soundie", "wochenschau", "superman", "other"]:
    vids = [v for v in db["videos"].values() if v["series"] == series]
    if vids:
        v = vids[0]
        print(f"\n  [{series}] {v['current']['title'][:60]}")
        print(f"    Ideal:     {v['ideal']['title'][:60]}")
        print(f"    Score:     {v['audit']['seo_score']}  Issues: {v['audit']['issue_count']}  Changes: {v['has_changes']}")
        print(f"    Privacy:   {v['status']['privacy']}  Views: {v['metrics']['views']}  Likes: {v['metrics']['likes']}")
        print(f"    Tags:      {v['current']['tag_count']}  Loc langs: {v['current']['localization_langs']}")
        pls = [p["playlist_title"] for p in v["playlists"]]
        print(f"    Playlists: {pls}")
        if v["audit"]["all_issues"][:3]:
            print(f"    Issues:    {v['audit']['all_issues'][:3]}")

# 4. Krtek localization check
print(f"\n  🐸 Krtek Localization Check:")
krtek_vids = [v for v in db["videos"].values() if v["series"] == "krtek"]
for v in krtek_vids[:3]:
    print(f"    {v['current']['title'][:50]}")
    locs = v["current"]["localizations"]
    for lang in ["en", "de", "es", "fr", "pt"]:
        cur = locs.get(lang, {}).get("title", "(none)")[:50]
        ideal = v["ideal"]["localizations"].get(lang, "(none)")[:50]
        match = "✅" if cur == ideal else "❌"
        print(f"      {lang}: {match} cur={cur}")
        if cur != ideal:
            print(f"           ideal={ideal}")

# 5. Change types
print(f"\n  🔄 Change Types:")
type_counts = Counter()
for v in db["videos"].values():
    for ct in v["change_types"]:
        type_counts[ct] += 1
for ct, count in type_counts.most_common():
    print(f"     {ct:20s}: {count}")

# 6. Playlist coverage
print(f"\n  📋 Playlist Coverage:")
public_vids = [v for v in db["videos"].values() if v["status"]["privacy"] == "public"]
in_pl = sum(1 for v in public_vids if v["in_playlist"])
print(f"     {in_pl}/{len(public_vids)} public videos in at least 1 playlist")
no_pl = [v for v in public_vids if not v["in_playlist"]]
if no_pl:
    print(f"     ⚠️  {len(no_pl)} public videos NOT in any playlist:")
    for v in no_pl[:8]:
        print(f"        {v['series']:15s} | {v['current']['title'][:50]}")
    if len(no_pl) > 8:
        print(f"        ... and {len(no_pl)-8} more")

# 7. Push queue summary
pq = db["push_queue"]
print(f"\n  🚀 Push Queue: {len(pq)} videos, {db['stats']['total_quota_needed']:,d} quota needed")
print(f"     Top 5 priority:")
for item in pq[:5]:
    print(f"     [{item['priority']:3d}] {item['series']:15s} | {', '.join(item['change_types']):20s} | {item['title'][:45]}")

# 8. Fields per entry
sample = list(db["videos"].values())[0]
print(f"\n  📋 Fields per entry: {len(sample)} top-level keys")
for key in sample:
    val = sample[key]
    if isinstance(val, dict):
        print(f"     {key}: dict({len(val)} keys)")
    elif isinstance(val, list):
        print(f"     {key}: list({len(val)} items)")
    else:
        print(f"     {key}: {type(val).__name__}")

print(f"\n  📦 DB Size: {len(json.dumps(db)) / 1024:.0f} KB")
print("  ✅ Validation complete!")
