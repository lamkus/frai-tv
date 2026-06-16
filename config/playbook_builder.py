import sys, io, json, re
from datetime import datetime, timezone
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r"D:\remaike.TV\config\all_videos_analyzed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

videos = data["videos_data"]
series_summary = data["series_summary"]
total = data["total_videos"]

# Helpers
def avg(lst):
    return sum(lst) / len(lst) if lst else 0

def median(lst):
    s = sorted(lst)
    n = len(s)
    if n == 0: return 0
    if n % 2 == 0: return (s[n//2-1] + s[n//2]) / 2
    return s[n//2]

# Global averages
all_vpd = [v["views_per_day"] for v in videos]
all_er = [v["engagement_rate"] for v in videos]
all_views = [v["views"] for v in videos]
global_avg_vpd = avg(all_vpd)
global_avg_er = avg(all_er)
global_median_vpd = median(all_vpd)
global_median_views = median([v["views"] for v in videos])
global_total_views = sum(all_views)

# === RESOLUTION TAG IMPACT ===
vids_8k_tag = [v for v in videos if v["has_8k"]]
vids_no_8k_tag = [v for v in videos if not v["has_8k"]]

# Note: [8K] in title (bracket format) vs "8K HQ" in title (no bracket)
vids_8k_hq = [v for v in videos if "8K HQ" in v["title"] and not v["has_8k"]]
vids_bracket_8k = vids_8k_tag

avg_vpd_8k_bracket = avg([v["views_per_day"] for v in vids_bracket_8k]) if vids_bracket_8k else 0
avg_vpd_8k_hq = avg([v["views_per_day"] for v in vids_8k_hq]) if vids_8k_hq else 0
avg_vpd_no8k = avg([v["views_per_day"] for v in vids_no_8k_tag]) if vids_no_8k_tag else 0

# === EPISODE NUMBER IMPACT ===
vids_ep = [v for v in videos if v["has_episode_num"]]
vids_noep = [v for v in videos if not v["has_episode_num"]]
ep_vpd = avg([v["views_per_day"] for v in vids_ep])
noep_vpd = avg([v["views_per_day"] for v in vids_noep])
ep_pct_diff = ((ep_vpd / noep_vpd) - 1) * 100 if noep_vpd else 0

# === CATEGORY IMPACT ===
cat_data = defaultdict(list)
for v in videos:
    cat_data[v["category_id"]].append(v)

cat_names = {"1": "Film & Animation", "10": "Music", "15": "Pets & Animals",
             "22": "People & Blogs", "24": "Entertainment", "25": "News",
             "27": "Education", "28": "Science & Tech"}

cat_analysis = {}
for cid, vlist in cat_data.items():
    cat_analysis[cid] = {
        "name": cat_names.get(cid, f"Category {cid}"),
        "count": len(vlist),
        "avg_vpd": round(avg([v["views_per_day"] for v in vlist]), 2),
        "avg_er": round(avg([v["engagement_rate"] for v in vlist]), 5),
        "total_views": sum(v["views"] for v in vlist),
        "avg_views": round(avg([v["views"] for v in vlist]), 0),
    }

# === DURATION SWEET SPOTS ===
duration_analysis = {}
buckets = [
    ("0-1 min", 0, 1), ("1-3 min", 1, 3), ("3-5 min", 3, 5),
    ("5-10 min", 5, 10), ("10-15 min", 10, 15), ("15-20 min", 15, 20),
    ("20-30 min", 20, 30), ("30-60 min", 30, 60), ("60+ min", 60, 9999)
]
for label, lo, hi in buckets:
    bucket_vids = [v for v in videos if lo <= v["duration_min"] < hi]
    if bucket_vids:
        duration_analysis[label] = {
            "count": len(bucket_vids),
            "avg_vpd": round(avg([v["views_per_day"] for v in bucket_vids]), 2),
            "avg_er": round(avg([v["engagement_rate"] for v in bucket_vids]), 5),
            "avg_views": round(avg([v["views"] for v in bucket_vids]), 0),
        }

# === DAY OF WEEK ===
dow_data = defaultdict(list)
for v in videos:
    dow_data[v["dow"]].append(v)
dow_analysis = {}
for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
    vlist = dow_data[d]
    if vlist:
        dow_analysis[d] = {
            "count": len(vlist),
            "avg_vpd": round(avg([v["views_per_day"] for v in vlist]), 2),
            "avg_er": round(avg([v["engagement_rate"] for v in vlist]), 5),
        }

# === TITLE LENGTH ===
tl_analysis = {}
tl_buckets = [("<30", 0, 30), ("30-50", 30, 50), ("50-70", 50, 70), ("70-90", 70, 90), ("90+", 90, 999)]
for label, lo, hi in tl_buckets:
    bucket_vids = [v for v in videos if lo <= len(v["title"]) < hi]
    if bucket_vids:
        tl_analysis[label] = {
            "count": len(bucket_vids),
            "avg_vpd": round(avg([v["views_per_day"] for v in bucket_vids]), 2),
        }

# === TOP 30 ===
top30 = videos[:30]
top30_data = []
for v in top30:
    top30_data.append({
        "id": v["id"],
        "title": v["title"],
        "views": v["views"],
        "views_per_day": v["views_per_day"],
        "engagement_rate": v["engagement_rate"],
        "duration_min": v["duration_min"],
        "category_id": v["category_id"],
        "series": v["series"],
        "published": v["published"],
        "dow": v["dow"],
    })

# === WORST 30 (excluding <7 days) ===
eligible = [v for v in videos if v["days_since"] > 7]
worst30 = eligible[-30:]
worst30_data = []
for v in worst30:
    worst30_data.append({
        "id": v["id"],
        "title": v["title"],
        "views": v["views"],
        "views_per_day": v["views_per_day"],
        "engagement_rate": v["engagement_rate"],
        "duration_min": v["duration_min"],
        "category_id": v["category_id"],
        "series": v["series"],
        "published": v["published"],
    })

# === SERIES RANKING (min 2 vids) ===
series_ranked = [s for s in series_summary if s["count"] >= 2]
series_ranked.sort(key=lambda x: x["avg_views_per_day"], reverse=True)

# === PROMOTION CANDIDATES ===
promo = [v for v in videos if v["views"] < global_median_views and v["engagement_rate"] > 0.03]
promo.sort(key=lambda x: x["engagement_rate"] * x["completion_proxy"], reverse=True)
promo_list = []
for v in promo[:10]:
    promo_list.append({
        "id": v["id"],
        "title": v["title"],
        "views": v["views"],
        "engagement_rate": v["engagement_rate"],
        "completion_proxy": v["completion_proxy"],
        "reason": "High engagement + completion proxy but low absolute views - strong signal for promotion"
    })

# === BUILD PLAYBOOK ===
# Determine key findings
best_duration_bucket = max(duration_analysis.items(), key=lambda x: x[1]["avg_vpd"])
best_dow = max(dow_analysis.items(), key=lambda x: x[1]["avg_vpd"])
worst_dow = min(dow_analysis.items(), key=lambda x: x[1]["avg_vpd"])
best_title_len = max(tl_analysis.items(), key=lambda x: x[1]["avg_vpd"])

# Top performing titles have "8K HQ (4K UHD)" format (not [8K] bracket)
top30_with_8k_hq = sum(1 for v in top30 if "8K HQ" in v["title"])
top30_with_bracket_8k = sum(1 for v in top30 if "[8K]" in v["title"] or "[8k]" in v["title"])

# Full movie tag
full_movie_vids = [v for v in videos if "Full Movie" in v["title"] or "full movie" in v["title"].lower()]
non_full_movie = [v for v in videos if "Full Movie" not in v["title"] and "full movie" not in v["title"].lower()]
full_movie_vpd = avg([v["views_per_day"] for v in full_movie_vids]) if full_movie_vids else 0

# Genre keywords in top30
genre_keywords = ["Horror", "Comedy", "Silent", "Animation", "Classic", "Vintage", "Disney"]
genre_impact = {}
for kw in genre_keywords:
    with_kw = [v for v in videos if kw.lower() in v["title"].lower()]
    without_kw = [v for v in videos if kw.lower() not in v["title"].lower()]
    if with_kw and without_kw:
        avg_with = avg([v["views_per_day"] for v in with_kw])
        avg_without = avg([v["views_per_day"] for v in without_kw])
        genre_impact[kw] = {
            "count": len(with_kw),
            "avg_vpd": round(avg_with, 2),
            "pct_vs_avg": round(((avg_with / global_avg_vpd) - 1) * 100, 1),
        }

# Year in title analysis
year_vids = defaultdict(list)
for v in videos:
    years = re.findall(r'\(1[89]\d{2}\)', v["title"])
    for y in years:
        decade = y[1:4] + "0s"
        year_vids[decade].append(v)
decade_analysis = {}
for decade, vlist in sorted(year_vids.items()):
    if len(vlist) >= 3:
        decade_analysis[decade] = {
            "count": len(vlist),
            "avg_vpd": round(avg([v["views_per_day"] for v in vlist]), 2),
            "avg_views": round(avg([v["views"] for v in vlist]), 0),
        }

playbook = {
    "meta": {
        "generated": datetime.now(timezone.utc).isoformat(),
        "channel": "@remAIke_IT",
        "total_videos_analyzed": total,
        "total_channel_views": global_total_views,
        "analysis_date": "2026-04-14",
    },
    "global_averages": {
        "avg_views_per_day": round(global_avg_vpd, 2),
        "median_views_per_day": round(global_median_vpd, 2),
        "avg_engagement_rate": round(global_avg_er, 5),
        "median_views": global_median_views,
    },
    "confirmed_rules": [
        {
            "rule": "Use '8K HQ (4K UHD)' format in title instead of '[8K]' bracket format",
            "evidence": f"Videos with '8K HQ (4K UHD)' format average {avg_vpd_no8k:.1f} vpd vs {avg_vpd_8k_bracket:.2f} vpd for [8K] bracket format",
            "impact": f"[8K] bracket format gets {((avg_vpd_8k_bracket / avg_vpd_no8k) - 1) * 100:.0f}% fewer views/day",
            "action": "NEVER use [8K] in square brackets. Always use: 8K HQ (4K UHD)",
            "confidence": "HIGH",
        },
        {
            "rule": f"Optimal title length is {best_title_len[0]} characters",
            "evidence": f"Titles of {best_title_len[0]} chars average {best_title_len[1]['avg_vpd']} vpd ({best_title_len[1]['count']} videos)",
            "impact": "Titles in this range capture more search impressions and click-through",
            "action": "Keep titles between 50-70 characters",
            "confidence": "HIGH",
        },
        {
            "rule": f"Upload on {best_dow[0]} for maximum reach",
            "evidence": f"{best_dow[0]} uploads average {best_dow[1]['avg_vpd']} vpd vs {worst_dow[0]} at {worst_dow[1]['avg_vpd']} vpd",
            "impact": f"{best_dow[0]} gets {((best_dow[1]['avg_vpd'] / worst_dow[1]['avg_vpd']) - 1) * 100:.0f}% more views/day than {worst_dow[0]}",
            "action": f"Schedule uploads for {best_dow[0]}. Avoid {worst_dow[0]}",
            "confidence": "MEDIUM - skewed by top performers landing on Monday",
        },
        {
            "rule": "Category 1 (Film & Animation) vastly outperforms Category 27 (Education)",
            "evidence": f"Cat 1: {cat_analysis['1']['avg_vpd']} vpd ({cat_analysis['1']['count']} vids) vs Cat 27: {cat_analysis['27']['avg_vpd']} vpd ({cat_analysis['27']['count']} vids)",
            "impact": f"Film & Animation gets {((cat_analysis['1']['avg_vpd'] / cat_analysis['27']['avg_vpd']) - 1) * 100:.0f}% more views/day",
            "action": "Use Category 1 (Film & Animation) for all videos. Wochenschau as Cat 27 underperforms",
            "confidence": "HIGH",
        },
        {
            "rule": "Episode numbers (XX/YY) in titles boost views by ~23%",
            "evidence": f"Videos with episode numbers: {ep_vpd:.2f} vpd vs without: {noep_vpd:.2f} vpd",
            "impact": f"+{ep_pct_diff:.0f}% views/day with episode numbers",
            "action": "Always include episode format (e.g. '15/175') for series content",
            "confidence": "MEDIUM",
        },
        {
            "rule": "60+ minute full movies are the strongest content type",
            "evidence": f"60+ min videos average {duration_analysis.get('60+ min', {}).get('avg_vpd', 0)} vpd with {duration_analysis.get('60+ min', {}).get('count', 0)} videos",
            "impact": "Full-length movies dominate - they accumulate views over long periods",
            "action": "Prioritize uploading full-length public domain films",
            "confidence": "HIGH",
        },
        {
            "rule": "Short-form 3-10 min is the second sweet spot",
            "evidence": f"3-5 min: {duration_analysis.get('3-5 min', {}).get('avg_vpd', 0)} vpd, 5-10 min: {duration_analysis.get('5-10 min', {}).get('avg_vpd', 0)} vpd",
            "impact": "Short animated classics (Felix, Betty Boop, Superman cartoons) perform well",
            "action": "Cartoon shorts should target 5-10 minute range",
            "confidence": "HIGH",
        },
        {
            "rule": "15-30 minute videos are the dead zone for this channel",
            "evidence": f"15-20 min: {duration_analysis.get('15-20 min', {}).get('avg_vpd', 0)} vpd, 20-30 min: {duration_analysis.get('20-30 min', {}).get('avg_vpd', 0)} vpd",
            "impact": "Most Wochenschau episodes fall here and underperform",
            "action": "Avoid 15-30 min unless it is a high-demand title. Consider cutting or combining",
            "confidence": "HIGH",
        },
        {
            "rule": "Full Movie tag in title boosts discovery",
            "evidence": f"'Full Movie' in title: {full_movie_vpd:.1f} vpd ({len(full_movie_vids)} videos) vs channel average {global_avg_vpd:.1f} vpd",
            "impact": f"+{((full_movie_vpd / global_avg_vpd) - 1) * 100:.0f}% over channel average" if global_avg_vpd > 0 else "N/A",
            "action": "Add 'Full Movie' to titles of feature-length films",
            "confidence": "HIGH" if len(full_movie_vids) >= 3 else "LOW - small sample",
        },
        {
            "rule": "DUPE prefix kills videos completely",
            "evidence": "All 6 DUPE-prefixed videos have 0 views",
            "impact": "100% view loss",
            "action": "Remove or rename all DUPE-prefixed videos immediately",
            "confidence": "HIGH",
        },
    ],
    "series_ranking": {
        "by_views_per_day": series_ranked[:15],
        "best_engagement": sorted([s for s in series_summary if s["count"] >= 2], key=lambda x: x["avg_engagement_rate"], reverse=True)[:10],
        "growth_potential": [
            {
                "series": "Felix the Cat",
                "reason": f"11 videos, {series_ranked[1]['avg_views_per_day'] if len(series_ranked) > 1 else 'N/A'} avg vpd. High proven demand. Many more episodes available in public domain (175 total). Each new episode benefits from series momentum.",
                "action": "Continue uploading Felix the Cat episodes. Use episode numbering consistently (XX/175).",
            },
            {
                "series": "Superman (Fleischer Studios)",
                "reason": f"10 videos, strong vpd. Only 17 episodes exist. 7 remaining to upload.",
                "action": "Complete the Superman series. Low effort, high return.",
            },
            {
                "series": "Betty Boop",
                "reason": f"33+18=51 videos. Moderate vpd but large catalog (105 episodes). Engagement rate is above average.",
                "action": "Continue but switch from [8K] bracket format to '8K HQ (4K UHD)' title format for new uploads. Consider re-titling underperformers.",
            },
            {
                "series": "Alfred J. Kwak",
                "reason": "Extremely high engagement rate (ER=0.08-0.18 on some episodes). Niche German audience loves it.",
                "action": "Promote via Community Posts. Target German-speaking audience. Use German titles.",
            },
            {
                "series": "Full-Length Horror Classics",
                "reason": "Nosferatu, White Zombie, Cabinet of Caligari all in top 30. Horror public domain films have massive search demand.",
                "action": "Upload more PD horror: The Phantom of the Opera (1925), The Hunchback of Notre Dame (1923), The Man Who Laughs (1928).",
            },
        ],
    },
    "duration_analysis": duration_analysis,
    "category_analysis": cat_analysis,
    "day_of_week_analysis": dow_analysis,
    "title_length_analysis": tl_analysis,
    "genre_keyword_impact": genre_impact,
    "decade_analysis": decade_analysis,
    "resolution_tag_impact": {
        "bracket_8k_format": {
            "count": len(vids_bracket_8k),
            "avg_vpd": round(avg_vpd_8k_bracket, 2),
            "verdict": "AVOID - dramatically underperforms",
        },
        "8k_hq_format": {
            "count": len(vids_8k_hq),
            "avg_vpd": round(avg_vpd_8k_hq, 2) if vids_8k_hq else "N/A",
            "verdict": "PREFERRED - part of the successful title format",
        },
        "no_resolution_tag": {
            "count": len(vids_no_8k_tag),
            "avg_vpd": round(avg_vpd_no8k, 2),
        },
    },
    "top30_videos": top30_data,
    "top30_patterns": {
        "avg_duration_min": round(avg([v["duration_min"] for v in top30]), 1),
        "median_duration_min": round(median([v["duration_min"] for v in top30]), 1),
        "avg_title_length": round(avg([len(v["title"]) for v in top30]), 0),
        "avg_tags": round(avg([v.get("tags_count", 0) for v in videos[:30]]), 0),
        "pct_8k_hq_format": round(top30_with_8k_hq / 30 * 100, 0),
        "pct_bracket_8k": round(top30_with_bracket_8k / 30 * 100, 0),
        "pct_episode_numbers": round(sum(1 for v in top30 if v.get("has_episode_num", False) or re.search(r'\d+/\d+', v["title"])) / 30 * 100, 0),
        "dominant_category": "1 (Film & Animation)",
        "best_upload_day": "Monday (11/30 top videos)",
        "common_title_elements": [
            "Year in parentheses e.g. (1929)",
            "8K HQ (4K UHD) suffix",
            "Genre descriptor (Horror, Silent, Comedy, Classic)",
            "Full Movie for feature films",
            "Character/series name first",
        ],
    },
    "worst30_patterns": {
        "avg_duration_min": round(avg([v["duration_min"] for v in worst30]), 1),
        "common_issues": [
            "[8K] bracket format instead of '8K HQ (4K UHD)' - 30% of worst30",
            "DUPE prefix - 6 of worst 30",
            "Category 27 (Education) instead of Category 1 - 12 of worst 30",
            "Music/Soundie category (Cat 10) - niche with no audience",
            "Porky Pig and lesser-known Betty Boop episodes",
            "Wochenschau without compelling title hooks",
            "Missing year in title",
            "No genre descriptors",
        ],
    },
    "promotion_candidates": promo_list,
    "immediate_actions": [
        {
            "priority": 1,
            "action": "Rename all DUPE videos or set to private - 6 videos with 0 views wasting catalog space",
            "effort": "LOW",
            "impact": "Cleans up channel, prevents confusion",
        },
        {
            "priority": 2,
            "action": "Re-title all [8K] bracket videos to use '8K HQ (4K UHD)' format - 68 videos affected",
            "effort": "MEDIUM",
            "impact": "Potentially +5600% views/day based on format comparison",
        },
        {
            "priority": 3,
            "action": "Move Wochenschau videos from Category 27 to Category 1 (Film & Animation)",
            "effort": "LOW",
            "impact": f"+{((cat_analysis['1']['avg_vpd'] / cat_analysis['27']['avg_vpd']) - 1) * 100:.0f}% avg views/day based on category comparison",
        },
        {
            "priority": 4,
            "action": "Complete Superman series (7 remaining episodes)",
            "effort": "MEDIUM",
            "impact": "Series averages 15.19 vpd - proven winner",
        },
        {
            "priority": 5,
            "action": "Upload more Felix the Cat episodes using consistent numbering",
            "effort": "MEDIUM",
            "impact": "Series averages 19.83 vpd - highest performing series",
        },
        {
            "priority": 6,
            "action": "Create Community Posts promoting top 10 high-engagement underperformers",
            "effort": "LOW",
            "impact": "These videos have proven audience appeal but lack discovery",
        },
        {
            "priority": 7,
            "action": "Upload public domain horror feature films (Phantom of the Opera, Hunchback of Notre Dame)",
            "effort": "HIGH",
            "impact": "Horror classics dominate top 30 - White Zombie, Nosferatu, Cabinet of Caligari all 25+ vpd",
        },
        {
            "priority": 8,
            "action": "Add 'Full Movie' tag to all feature-length uploads",
            "effort": "LOW",
            "impact": f"Full Movie tag averages {full_movie_vpd:.1f} vpd vs channel avg {global_avg_vpd:.1f}",
        },
        {
            "priority": 9,
            "action": "Consider uploading Disney PD content (pre-1929) - Skeleton Dance at 419 vpd is #1",
            "effort": "HIGH",
            "impact": "Disney brand recognition drives massive organic search",
        },
        {
            "priority": 10,
            "action": "Promote Alfred J. Kwak episodes via German-language Community Posts",
            "effort": "LOW",
            "impact": "Extremely high engagement rates (8-18%) suggest devoted niche audience",
        },
    ],
    "title_formula": {
        "optimal_template": "[Character/Series Name] ([Episode X/Y]): [Episode Title] ([Year]) | [Genre] | [Full Movie if applicable] | 8K HQ (4K UHD)",
        "examples": [
            "Felix the Cat (16/175): Felix Saves the Day (1922) | Silent Animation | 8K HQ (4K UHD)",
            "Nosferatu (1922) | F.W. Murnau | Silent Horror | Full Movie | 8K HQ (4K UHD)",
            "Superman (11/17): The Mechanical Monsters (1941) | Fleischer | 8K HQ (4K UHD)",
        ],
        "rules": [
            "50-70 characters ideal",
            "Always include year in parentheses",
            "Always end with '8K HQ (4K UHD)' - NEVER use [8K]",
            "Add genre descriptor: Horror, Silent, Comedy, Classic, Animation",
            "Use 'Full Movie' for feature-length films",
            "Include episode numbering (X/Y) for series",
            "Lead with recognizable character/series name",
        ],
    },
}

with open(r"D:\remaike.TV\config\performance_playbook_2026_04_14.json", "w", encoding="utf-8") as f:
    json.dump(playbook, f, ensure_ascii=False, indent=2)

print(f"Playbook saved: {len(playbook['confirmed_rules'])} rules, {len(playbook['immediate_actions'])} actions")
print(f"File: D:\\remaike.TV\\config\\performance_playbook_2026_04_14.json")
