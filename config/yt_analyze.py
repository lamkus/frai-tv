import sys, io, json, urllib.request, urllib.parse, urllib.error, time, math, re
from datetime import datetime, timezone
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open(r"D:\remaike.TV\config\youtube_oauth.json", "r", encoding="utf-8") as f:
    oauth = json.load(f)

def refresh_access_token():
    data = urllib.parse.urlencode({
        "client_id": oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "refresh_token": oauth["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["access_token"]

access_token = refresh_access_token()
print("Token refreshed successfully", file=sys.stderr)

def yt_api(endpoint, params):
    params_str = urllib.parse.urlencode(params)
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{params_str}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {access_token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {body}", file=sys.stderr)
        raise

# STEP 1: Get ALL video IDs via search
print("Fetching all video IDs...", file=sys.stderr)
all_video_ids = []
page_token = None
page_num = 0
while True:
    params = {
        "part": "id",
        "forMine": "true",
        "type": "video",
        "maxResults": 50,
    }
    if page_token:
        params["pageToken"] = page_token

    result = yt_api("search", params)
    ids = [item["id"]["videoId"] for item in result.get("items", [])]
    all_video_ids.extend(ids)
    page_num += 1
    print(f"  Page {page_num}: got {len(ids)} IDs (total: {len(all_video_ids)})", file=sys.stderr)

    page_token = result.get("nextPageToken")
    if not page_token:
        break
    time.sleep(0.3)

print(f"Total video IDs: {len(all_video_ids)}", file=sys.stderr)

# STEP 2: Get details for all videos in batches of 50
print("Fetching video details...", file=sys.stderr)
all_videos = []
for i in range(0, len(all_video_ids), 50):
    batch = all_video_ids[i:i+50]
    result = yt_api("videos", {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(batch)
    })
    all_videos.extend(result.get("items", []))
    print(f"  Batch {i//50+1}: got {len(result.get('items',[]))} details (total: {len(all_videos)})", file=sys.stderr)
    time.sleep(0.3)

print(f"Total videos with details: {len(all_videos)}", file=sys.stderr)

with open(r"D:\remaike.TV\config\all_videos_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=2)
print("Raw data saved.", file=sys.stderr)

def parse_duration(d):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h*3600 + mi*60 + s

now = datetime.now(timezone.utc)

videos_data = []
for v in all_videos:
    snippet = v.get("snippet", {})
    stats = v.get("statistics", {})
    content = v.get("contentDetails", {})

    vid = v["id"]
    title = snippet.get("title", "")
    published = snippet.get("publishedAt", "")
    description = snippet.get("description", "")
    tags = snippet.get("tags", [])
    category_id = snippet.get("categoryId", "")

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))

    duration_iso = content.get("duration", "PT0S")
    duration_sec = parse_duration(duration_iso)

    try:
        pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        days_since = max((now - pub_dt).days, 1)
    except:
        pub_dt = now
        days_since = 1

    try:
        dow = pub_dt.strftime("%A")
    except:
        dow = "Unknown"

    views_per_day = views / days_since
    engagement_rate = (likes + comments) / views if views > 0 else 0
    completion_proxy = likes / views if views > 0 else 0

    has_8k = "[8K]" in title or "[8k]" in title
    has_4k = "[4K]" in title or "[4k]" in title

    ep_match = re.search(r'(\d+)/(\d+)', title)
    has_episode_num = ep_match is not None

    series = "Unknown"
    if ep_match:
        series_part = title[:ep_match.start()].strip()
        series_part = re.sub(r'\[(?:8K|4K|HD|UHD)\]', '', series_part, flags=re.IGNORECASE).strip()
        if series_part:
            series = series_part
    else:
        for delim in [" - ", " | ", ": "]:
            if delim in title:
                series = title.split(delim)[0].strip()
                series = re.sub(r'\[(?:8K|4K|HD|UHD)\]', '', series, flags=re.IGNORECASE).strip()
                break

    videos_data.append({
        "id": vid,
        "title": title,
        "published": published,
        "days_since": days_since,
        "dow": dow,
        "views": views,
        "likes": likes,
        "comments": comments,
        "duration_sec": duration_sec,
        "duration_min": round(duration_sec / 60, 1),
        "category_id": category_id,
        "tags_count": len(tags),
        "desc_length": len(description),
        "views_per_day": round(views_per_day, 2),
        "engagement_rate": round(engagement_rate, 5),
        "completion_proxy": round(completion_proxy, 5),
        "has_8k": has_8k,
        "has_4k": has_4k,
        "has_episode_num": has_episode_num,
        "series": series,
        "tags": tags,
    })

videos_data.sort(key=lambda x: x["views_per_day"], reverse=True)

print(f"\n=== TOTAL VIDEOS ANALYZED: {len(videos_data)} ===\n")

# SERIES ANALYSIS
series_stats = defaultdict(lambda: {"videos": [], "total_views": 0, "total_vpd": 0, "total_er": 0, "total_cp": 0})
for v in videos_data:
    s = v["series"]
    series_stats[s]["videos"].append(v)
    series_stats[s]["total_views"] += v["views"]
    series_stats[s]["total_vpd"] += v["views_per_day"]
    series_stats[s]["total_er"] += v["engagement_rate"]
    series_stats[s]["total_cp"] += v["completion_proxy"]

print("=== SERIES ANALYSIS ===")
series_summary = []
for s, data in series_stats.items():
    n = len(data["videos"])
    avg_vpd = data["total_vpd"] / n
    avg_er = data["total_er"] / n
    avg_views = data["total_views"] / n
    avg_cp = data["total_cp"] / n
    series_summary.append({
        "series": s,
        "count": n,
        "avg_views_per_day": round(avg_vpd, 2),
        "avg_engagement_rate": round(avg_er, 5),
        "avg_views": round(avg_views, 0),
        "total_views": data["total_views"],
        "avg_completion_proxy": round(avg_cp, 5),
    })

series_summary.sort(key=lambda x: x["avg_views_per_day"], reverse=True)
print("\nTop 25 Series by avg views/day (min 2 videos):")
shown = 0
for s in series_summary:
    if s["count"] >= 2:
        shown += 1
        print(f"  {shown}. {s['series']} ({s['count']} vids): vpd={s['avg_views_per_day']}, ER={s['avg_engagement_rate']}, avg_views={s['avg_views']}, CP={s['avg_completion_proxy']}")
        if shown >= 25:
            break

print("\nTop 25 Series by engagement rate (min 2 videos):")
series_by_er = sorted([s for s in series_summary if s["count"] >= 2], key=lambda x: x["avg_engagement_rate"], reverse=True)
for i, s in enumerate(series_by_er[:25]):
    print(f"  {i+1}. {s['series']} ({s['count']} vids): ER={s['avg_engagement_rate']}, vpd={s['avg_views_per_day']}")

# DURATION ANALYSIS
print("\n=== DURATION ANALYSIS ===")
duration_buckets = defaultdict(lambda: {"count": 0, "total_vpd": 0, "total_er": 0, "total_views": 0})
for v in videos_data:
    dm = v["duration_min"]
    if dm < 1: bucket = "0-1 min"
    elif dm < 3: bucket = "1-3 min"
    elif dm < 5: bucket = "3-5 min"
    elif dm < 10: bucket = "5-10 min"
    elif dm < 15: bucket = "10-15 min"
    elif dm < 20: bucket = "15-20 min"
    elif dm < 30: bucket = "20-30 min"
    elif dm < 60: bucket = "30-60 min"
    else: bucket = "60+ min"

    duration_buckets[bucket]["count"] += 1
    duration_buckets[bucket]["total_vpd"] += v["views_per_day"]
    duration_buckets[bucket]["total_er"] += v["engagement_rate"]
    duration_buckets[bucket]["total_views"] += v["views"]

bucket_order = ["0-1 min", "1-3 min", "3-5 min", "5-10 min", "10-15 min", "15-20 min", "20-30 min", "30-60 min", "60+ min"]
for b in bucket_order:
    d = duration_buckets[b]
    if d["count"] > 0:
        avg_vpd = d["total_vpd"] / d["count"]
        avg_er = d["total_er"] / d["count"]
        avg_views = d["total_views"] / d["count"]
        print(f"  {b}: {d['count']} videos, avg_vpd={avg_vpd:.2f}, avg_er={avg_er:.5f}, avg_views={avg_views:.0f}")

# 8K vs non-8K
print("\n=== 8K TAG ANALYSIS ===")
vids_8k = [v for v in videos_data if v["has_8k"]]
vids_no8k = [v for v in videos_data if not v["has_8k"]]
if vids_8k:
    avg_vpd_8k = sum(v["views_per_day"] for v in vids_8k) / len(vids_8k)
    avg_er_8k = sum(v["engagement_rate"] for v in vids_8k) / len(vids_8k)
    avg_views_8k = sum(v["views"] for v in vids_8k) / len(vids_8k)
    print(f"  [8K] videos: {len(vids_8k)}, avg_vpd={avg_vpd_8k:.2f}, avg_er={avg_er_8k:.5f}, avg_views={avg_views_8k:.0f}")
if vids_no8k:
    avg_vpd_no8k = sum(v["views_per_day"] for v in vids_no8k) / len(vids_no8k)
    avg_er_no8k = sum(v["engagement_rate"] for v in vids_no8k) / len(vids_no8k)
    avg_views_no8k = sum(v["views"] for v in vids_no8k) / len(vids_no8k)
    print(f"  Non-[8K] videos: {len(vids_no8k)}, avg_vpd={avg_vpd_no8k:.2f}, avg_er={avg_er_no8k:.5f}, avg_views={avg_views_no8k:.0f}")
if vids_8k and vids_no8k:
    vpd_diff = ((avg_vpd_8k / avg_vpd_no8k) - 1) * 100
    print(f"  8K difference: {vpd_diff:+.1f}% views/day")

# 4K analysis
print("\n=== 4K TAG ANALYSIS ===")
vids_4k = [v for v in videos_data if v["has_4k"]]
vids_no_res = [v for v in videos_data if not v["has_4k"] and not v["has_8k"]]
if vids_4k:
    avg_vpd_4k = sum(v["views_per_day"] for v in vids_4k) / len(vids_4k)
    avg_er_4k = sum(v["engagement_rate"] for v in vids_4k) / len(vids_4k)
    print(f"  [4K] videos: {len(vids_4k)}, avg_vpd={avg_vpd_4k:.2f}, avg_er={avg_er_4k:.5f}")
if vids_no_res:
    avg_vpd_nores = sum(v["views_per_day"] for v in vids_no_res) / len(vids_no_res)
    avg_er_nores = sum(v["engagement_rate"] for v in vids_no_res) / len(vids_no_res)
    print(f"  No resolution tag: {len(vids_no_res)}, avg_vpd={avg_vpd_nores:.2f}, avg_er={avg_er_nores:.5f}")

# Episode number analysis
print("\n=== EPISODE NUMBER ANALYSIS ===")
vids_ep = [v for v in videos_data if v["has_episode_num"]]
vids_noep = [v for v in videos_data if not v["has_episode_num"]]
if vids_ep:
    avg_vpd_ep = sum(v["views_per_day"] for v in vids_ep) / len(vids_ep)
    avg_er_ep = sum(v["engagement_rate"] for v in vids_ep) / len(vids_ep)
    print(f"  With episode numbers: {len(vids_ep)}, avg_vpd={avg_vpd_ep:.2f}, avg_er={avg_er_ep:.5f}")
if vids_noep:
    avg_vpd_noep = sum(v["views_per_day"] for v in vids_noep) / len(vids_noep)
    avg_er_noep = sum(v["engagement_rate"] for v in vids_noep) / len(vids_noep)
    print(f"  Without episode numbers: {len(vids_noep)}, avg_vpd={avg_vpd_noep:.2f}, avg_er={avg_er_noep:.5f}")
if vids_ep and vids_noep:
    ep_diff = ((avg_vpd_ep / avg_vpd_noep) - 1) * 100
    print(f"  Episode number difference: {ep_diff:+.1f}% views/day")

# Category analysis
print("\n=== CATEGORY ANALYSIS ===")
cat_stats = defaultdict(lambda: {"count": 0, "total_vpd": 0, "total_er": 0, "total_views": 0})
cat_names = {"1": "Film & Animation", "10": "Music", "15": "Pets & Animals", "17": "Sports",
             "20": "Gaming", "22": "People & Blogs", "24": "Entertainment", "25": "News",
             "26": "Howto & Style", "27": "Education", "28": "Science & Tech"}
for v in videos_data:
    c = v["category_id"]
    cat_stats[c]["count"] += 1
    cat_stats[c]["total_vpd"] += v["views_per_day"]
    cat_stats[c]["total_er"] += v["engagement_rate"]
    cat_stats[c]["total_views"] += v["views"]

for c, d in sorted(cat_stats.items(), key=lambda x: x[1]["total_vpd"]/x[1]["count"] if x[1]["count"]>0 else 0, reverse=True):
    cname = cat_names.get(c, f"Cat-{c}")
    avg_vpd = d["total_vpd"] / d["count"]
    avg_er = d["total_er"] / d["count"]
    avg_views = d["total_views"] / d["count"]
    print(f"  {cname} (id={c}): {d['count']} videos, avg_vpd={avg_vpd:.2f}, avg_er={avg_er:.5f}, avg_views={avg_views:.0f}")

# TOP 30
print("\n=== TOP 30 VIDEOS (by views_per_day) ===")
top30 = videos_data[:30]
for i, v in enumerate(top30):
    print(f"  {i+1}. [{v['views_per_day']} vpd] {v['title']} (views={v['views']}, dur={v['duration_min']}m, ER={v['engagement_rate']}, cat={v['category_id']}, days={v['days_since']})")

print("\n--- TOP 30 PATTERNS ---")
top_durations = [v["duration_min"] for v in top30]
top_title_lens = [len(v["title"]) for v in top30]
top_desc_lens = [v["desc_length"] for v in top30]
top_tag_counts = [v["tags_count"] for v in top30]
top_dows = defaultdict(int)
for v in top30:
    top_dows[v["dow"]] += 1
top_8k = sum(1 for v in top30 if v["has_8k"])
top_4k = sum(1 for v in top30 if v["has_4k"])
top_ep = sum(1 for v in top30 if v["has_episode_num"])
top_cats = Counter(v["category_id"] for v in top30)

print(f"  Avg duration: {sum(top_durations)/len(top_durations):.1f} min (median: {sorted(top_durations)[15]:.1f})")
print(f"  Duration range: {min(top_durations):.1f} - {max(top_durations):.1f} min")
print(f"  Avg title length: {sum(top_title_lens)/len(top_title_lens):.0f} chars")
print(f"  Avg description length: {sum(top_desc_lens)/len(top_desc_lens):.0f} chars")
print(f"  Avg tag count: {sum(top_tag_counts)/len(top_tag_counts):.0f}")
print(f"  With [8K]: {top_8k}/{len(top30)} ({top_8k/len(top30)*100:.0f}%)")
print(f"  With [4K]: {top_4k}/{len(top30)} ({top_4k/len(top30)*100:.0f}%)")
print(f"  With episode numbers: {top_ep}/{len(top30)} ({top_ep/len(top30)*100:.0f}%)")
print(f"  Upload days: {dict(sorted(top_dows.items(), key=lambda x: x[1], reverse=True))}")
print(f"  Categories: {dict(top_cats.most_common())}")

top_series_list = Counter(v["series"] for v in top30).most_common(10)
print(f"  Top series in TOP30: {top_series_list}")

all_words = []
for v in top30:
    words = re.findall(r'[A-Za-z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]{3,}', v["title"])
    all_words.extend([w.lower() for w in words])
word_counts = Counter(all_words).most_common(25)
print(f"  Top title keywords: {word_counts}")

# WORST 30
print("\n=== WORST 30 VIDEOS (by views_per_day, excl. <7 days old) ===")
eligible = [v for v in videos_data if v["days_since"] > 7]
worst30 = eligible[-30:]
for i, v in enumerate(worst30):
    print(f"  {i+1}. [{v['views_per_day']} vpd] {v['title']} (views={v['views']}, dur={v['duration_min']}m, ER={v['engagement_rate']}, cat={v['category_id']}, days={v['days_since']})")

print("\n--- WORST 30 PATTERNS ---")
w_durations = [v["duration_min"] for v in worst30]
w_title_lens = [len(v["title"]) for v in worst30]
w_desc_lens = [v["desc_length"] for v in worst30]
w_tag_counts = [v["tags_count"] for v in worst30]
w_dows = defaultdict(int)
for v in worst30:
    w_dows[v["dow"]] += 1
w_8k = sum(1 for v in worst30 if v["has_8k"])
w_4k = sum(1 for v in worst30 if v["has_4k"])
w_ep = sum(1 for v in worst30 if v["has_episode_num"])
w_cats = Counter(v["category_id"] for v in worst30)

print(f"  Avg duration: {sum(w_durations)/len(w_durations):.1f} min (median: {sorted(w_durations)[15]:.1f})")
print(f"  Duration range: {min(w_durations):.1f} - {max(w_durations):.1f} min")
print(f"  Avg title length: {sum(w_title_lens)/len(w_title_lens):.0f} chars")
print(f"  Avg description length: {sum(w_desc_lens)/len(w_desc_lens):.0f} chars")
print(f"  Avg tag count: {sum(w_tag_counts)/len(w_tag_counts):.0f}")
print(f"  With [8K]: {w_8k}/{len(worst30)} ({w_8k/len(worst30)*100:.0f}%)")
print(f"  With [4K]: {w_4k}/{len(worst30)} ({w_4k/len(worst30)*100:.0f}%)")
print(f"  With episode numbers: {w_ep}/{len(worst30)} ({w_ep/len(worst30)*100:.0f}%)")
print(f"  Upload days: {dict(sorted(w_dows.items(), key=lambda x: x[1], reverse=True))}")
print(f"  Categories: {dict(w_cats.most_common())}")

w_series_list = Counter(v["series"] for v in worst30).most_common(10)
print(f"  Top series in WORST30: {w_series_list}")

w_words = []
for v in worst30:
    words = re.findall(r'[A-Za-z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]{3,}', v["title"])
    w_words.extend([w.lower() for w in words])
w_word_counts = Counter(w_words).most_common(25)
print(f"  Top title keywords: {w_word_counts}")

# Day of week overall analysis
print("\n=== DAY OF WEEK ANALYSIS ===")
dow_stats = defaultdict(lambda: {"count": 0, "total_vpd": 0, "total_er": 0})
for v in videos_data:
    dow_stats[v["dow"]]["count"] += 1
    dow_stats[v["dow"]]["total_vpd"] += v["views_per_day"]
    dow_stats[v["dow"]]["total_er"] += v["engagement_rate"]
for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    s = dow_stats[d]
    if s["count"] > 0:
        print(f"  {d}: {s['count']} videos, avg_vpd={s['total_vpd']/s['count']:.2f}, avg_er={s['total_er']/s['count']:.5f}")

# Title length vs performance correlation
print("\n=== TITLE LENGTH ANALYSIS ===")
tl_buckets = defaultdict(lambda: {"count": 0, "total_vpd": 0})
for v in videos_data:
    tl = len(v["title"])
    if tl < 30: bucket = "<30"
    elif tl < 50: bucket = "30-50"
    elif tl < 70: bucket = "50-70"
    elif tl < 90: bucket = "70-90"
    else: bucket = "90+"
    tl_buckets[bucket]["count"] += 1
    tl_buckets[bucket]["total_vpd"] += v["views_per_day"]
for b in ["<30", "30-50", "50-70", "70-90", "90+"]:
    d = tl_buckets[b]
    if d["count"] > 0:
        print(f"  {b} chars: {d['count']} videos, avg_vpd={d['total_vpd']/d['count']:.2f}")

# Save analyzed data
output = {
    "videos_data": [{k: v for k, v in vd.items() if k != "tags"} for vd in videos_data],
    "series_summary": series_summary,
    "total_videos": len(videos_data),
}
with open(r"D:\remaike.TV\config\all_videos_analyzed.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Identify top 10 promotion candidates: high engagement but not yet high views
print("\n=== TOP 10 PROMOTION CANDIDATES ===")
print("(High engagement rate + completion proxy, but below-median views)")
median_views = sorted([v["views"] for v in videos_data])[len(videos_data)//2]
promo_candidates = [v for v in videos_data if v["views"] < median_views and v["engagement_rate"] > 0.03]
promo_candidates.sort(key=lambda x: x["engagement_rate"] * x["completion_proxy"], reverse=True)
for i, v in enumerate(promo_candidates[:10]):
    print(f"  {i+1}. {v['title']} (views={v['views']}, ER={v['engagement_rate']}, CP={v['completion_proxy']}, vpd={v['views_per_day']})")

print("\n=== ALL DATA COLLECTION COMPLETE ===")
