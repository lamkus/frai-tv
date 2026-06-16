"""
Comprehensive Seasonal Analysis of ALL 365 videos on @remAIke_IT
Analyzes every video for seasonal/holiday marketing potential.
"""
import json
import re
from collections import defaultdict

DB_PATH = "config/video_master_db_v3.json"

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

videos = db["videos"]

# Print total count
print(f"Total videos in database: {len(videos)}")
print("="*120)

# Collect all videos with key info
all_videos = []
for vid_id, v in videos.items():
    title = v.get("current", {}).get("title", "UNKNOWN")
    series = v.get("series", "unknown")
    views = v.get("metrics", {}).get("views", 0)
    desc = v.get("current", {}).get("description", "")
    tags = v.get("current", {}).get("tags", [])
    privacy = v.get("status", {}).get("privacy", "unknown")
    
    all_videos.append({
        "id": vid_id,
        "title": title,
        "series": series,
        "views": views,
        "privacy": privacy,
        "desc": desc,
        "tags": tags,
    })

# Sort by series then title
all_videos.sort(key=lambda x: (x["series"], x["title"]))

# Print ALL titles grouped by series
print("\n📋 ALL VIDEOS BY SERIES:")
print("="*120)
current_series = None
for v in all_videos:
    if v["series"] != current_series:
        current_series = v["series"]
        series_count = sum(1 for x in all_videos if x["series"] == current_series)
        print(f"\n{'─'*80}")
        print(f"📂 {current_series.upper()} ({series_count} videos)")
        print(f"{'─'*80}")
    status = "🔒" if v["privacy"] == "private" else "✅"
    print(f"  {status} [{v['views']:>6} views] {v['title']}")

print(f"\n\n{'='*120}")
print("SEASONAL KEYWORD ANALYSIS")
print(f"{'='*120}")

# Define seasonal categories with keywords
SEASONS = {
    "💝 Valentine's Day (Feb 14)": {
        "title_kw": ["love", "heart", "kiss", "romance", "sweetheart", "cupid", "beauty", "beautiful", "beloved", "darling", "boop", "flirt", "date", "charm", "minnie the moocher", "cab calloway", "sexy", "seduction", "pin-up", "burlesque", "teaserama", "bettie page", "tempest storm", "strip", "dance", "dancing", "dancer", "tease"],
        "series_auto": [],  # No auto-include
        "desc_kw": ["love", "romance", "heart", "kiss", "beauty", "dance", "sexy", "seduction", "flirt", "charming", "desire"],
    },
    "🖤 Anti-Valentine's (Feb 14)": {
        "title_kw": ["horror", "monster", "nosferatu", "frankenstein", "dracula", "vampire", "ghost", "phantom", "dead", "death", "dark", "evil", "demon", "terror", "scream", "fear", "haunted", "nightmare", "jekyll", "hyde", "mad doctor", "mad scientist"],
        "series_auto": [],
        "desc_kw": ["horror", "monster", "dark", "evil", "terror", "nightmare"],
    },
    "🎭 Carnival/Mardi Gras (Feb-Mar)": {
        "title_kw": ["carnival", "mardi gras", "party", "parade", "costume", "mask", "celebration", "festival", "fiesta"],
        "series_auto": [],
        "desc_kw": ["carnival", "parade", "celebration", "festival", "party", "dance"],
    },
    "🏈 Super Bowl (Feb)": {
        "title_kw": ["sport", "action", "fight", "battle", "champion", "hero", "power", "strength", "knockout", "punch", "block", "gymkhana", "drift", "race", "car"],
        "series_auto": ["ken_block"],
        "desc_kw": ["action", "fight", "battle", "champion", "hero", "sport"],
    },
    "✊ Black History Month (Feb)": {
        "title_kw": ["jazz", "blues", "swing", "cab calloway", "louis jordan", "duke ellington", "count basie", "harlem", "cotton club", "negro", "boogie", "jive"],
        "series_auto": [],
        "desc_kw": ["jazz", "blues", "swing", "african american", "black artist", "harlem", "cotton club"],
    },
    "👩 Women's History Month / IWD (Mar)": {
        "title_kw": ["betty boop", "bettie page", "tempest storm", "woman", "girl", "queen", "princess", "lady", "female", "she", "her"],
        "series_auto": ["betty_boop", "teaserama"],
        "desc_kw": ["woman", "female", "icon", "pioneer", "empowerment"],
    },
    "🐣 Easter (April)": {
        "title_kw": ["easter", "bunny", "rabbit", "egg", "spring", "chick", "lamb", "garden", "flower", "nature", "bloom"],
        "series_auto": [],
        "desc_kw": ["easter", "spring", "bunny", "rabbit", "nature", "garden"],
    },
    "🌍 Earth Day (Apr 22)": {
        "title_kw": ["nature", "earth", "animal", "forest", "garden", "mole", "maulwurf", "krtek", "tree", "flower", "ocean", "sea", "environment", "planet", "green"],
        "series_auto": ["krtek"],
        "desc_kw": ["nature", "environment", "earth", "animal", "ecology", "garden", "forest"],
    },
    "🎖️ Memorial Day (May) / Veterans Day (Nov)": {
        "title_kw": ["war", "battle", "army", "military", "soldier", "navy", "marine", "bomber", "tank", "invasion", "d-day", "front", "offensive", "wochenschau", "newsreel", "torpedo", "submarine", "blitz", "surrender"],
        "series_auto": ["wochenschau"],
        "desc_kw": ["war", "military", "battle", "soldier", "wwii", "world war"],
    },
    "☀️ Summer (Jun-Aug)": {
        "title_kw": ["beach", "summer", "sun", "vacation", "swim", "ocean", "sea", "island", "tropical", "adventure", "sail", "boat", "surf", "water"],
        "series_auto": [],
        "desc_kw": ["beach", "summer", "sun", "vacation", "tropical", "adventure", "ocean"],
    },
    "🎃 Halloween (Oct)": {
        "title_kw": ["ghost", "casper", "spook", "haunt", "witch", "monster", "skeleton", "skull", "vampire", "dracula", "nosferatu", "frankenstein", "zombie", "horror", "scream", "phantom", "mad", "evil", "dark", "night", "shadow", "bat", "cat", "trick", "treat", "pumpkin", "terror", "fear", "devil", "demon", "jekyll", "hyde"],
        "series_auto": ["casper"],
        "desc_kw": ["ghost", "horror", "monster", "spooky", "haunted", "witch", "halloween"],
    },
    "🎄 Christmas / New Year (Dec-Jan)": {
        "title_kw": ["christmas", "xmas", "santa", "winter", "snow", "holiday", "gift", "rudolph", "reindeer", "carol", "jingle", "bell", "new year", "frosty", "nutcracker", "north pole", "noel", "silent night"],
        "series_auto": ["christmas"],
        "desc_kw": ["christmas", "holiday", "santa", "winter", "snow", "new year"],
    },
    "🎵 Music/Jazz (ALWAYS)": {
        "title_kw": ["music", "jazz", "swing", "band", "orchestra", "song", "sing", "singer", "vocal", "boogie", "blues", "rhythm", "melody", "piano", "trumpet", "sax", "drum", "jive", "jukebox", "soundie"],
        "series_auto": ["soundie"],
        "desc_kw": ["music", "jazz", "swing", "song", "performance"],
    },
    "📼 Nostalgia/Retro (ALWAYS)": {
        "title_kw": [],  # ALL videos qualify
        "series_auto": [],  # Check tag/desc for retro
        "desc_kw": ["vintage", "classic", "retro", "nostalgia", "restored", "8k"],
        "all_qualify": True,  # Every single video
    },
    "🚀 Space / Science (Year-round)": {
        "title_kw": ["space", "nasa", "skylab", "rocket", "moon", "star", "planet", "orbit", "astronaut", "cosmos", "galaxy", "satellite"],
        "series_auto": ["nasa"],
        "desc_kw": ["space", "nasa", "astronaut", "mission", "rocket"],
    },
    "🐱 World Animal Day (Oct 4)": {
        "title_kw": ["cat", "dog", "mouse", "bird", "duck", "rabbit", "fish", "horse", "bear", "lion", "mole", "maulwurf", "krtek", "felix", "animal", "pet", "bugs bunny", "daffy", "tweety", "sylvester", "porky"],
        "series_auto": ["felix_the_cat", "krtek"],
        "desc_kw": ["animal", "cat", "dog", "nature", "pet"],
    },
    "🎬 Classic Film Day (Year-round)": {
        "title_kw": ["film noir", "chaplin", "keaton", "silent", "classic", "cinema"],
        "series_auto": ["film_noir", "chaplin", "buster_keaton", "silly_symphony"],
        "desc_kw": ["film", "cinema", "classic", "silent era"],
    },
    "👶 Children's Day / Family (Year-round)": {
        "title_kw": ["kwak", "quack", "alfred", "maulwurf", "krtek", "casper", "bravestarr", "astro boy", "ferdy", "cartoon", "kids"],
        "series_auto": ["alfred_j_kwak", "krtek", "casper", "bravestarr", "astro_boy"],
        "desc_kw": ["children", "kids", "family", "cartoon", "animation"],
    },
}

# Analyze each video
video_seasons = {}
season_counts = defaultdict(list)

for v in all_videos:
    title_lower = v["title"].lower()
    desc_lower = v["desc"].lower()
    tags_lower = " ".join(v["tags"]).lower()
    combined = f"{title_lower} {desc_lower} {tags_lower}"
    matched_seasons = []
    
    for season_name, rules in SEASONS.items():
        match = False
        reason = []
        
        # Check series auto-include
        if v["series"] in rules.get("series_auto", []):
            match = True
            reason.append(f"series={v['series']}")
        
        # Check all_qualify flag  
        if rules.get("all_qualify"):
            match = True
            reason.append("all_videos")
        
        # Check title keywords
        for kw in rules.get("title_kw", []):
            if kw in title_lower:
                match = True
                reason.append(f"title:'{kw}'")
                break  # one match is enough
        
        # Check description keywords (only if not already matched)
        if not match:
            for kw in rules.get("desc_kw", []):
                if kw in desc_lower:
                    match = True
                    reason.append(f"desc:'{kw}'")
                    break
        
        if match:
            matched_seasons.append((season_name, reason))
            season_counts[season_name].append(v)
    
    video_seasons[v["id"]] = {
        "title": v["title"],
        "series": v["series"],
        "views": v["views"],
        "privacy": v["privacy"],
        "seasons": matched_seasons,
    }

# Print results grouped by season
print("\n\n" + "="*120)
print("📊 SEASONAL CATEGORIZATION RESULTS")
print("="*120)

# Sort seasons by relevance (February first)
season_order = [
    "💝 Valentine's Day (Feb 14)",
    "🖤 Anti-Valentine's (Feb 14)",
    "🏈 Super Bowl (Feb)",
    "✊ Black History Month (Feb)",
    "🎭 Carnival/Mardi Gras (Feb-Mar)",
    "👩 Women's History Month / IWD (Mar)",
    "🐣 Easter (April)",
    "🌍 Earth Day (Apr 22)",
    "🎖️ Memorial Day (May) / Veterans Day (Nov)",
    "☀️ Summer (Jun-Aug)",
    "🎃 Halloween (Oct)",
    "🐱 World Animal Day (Oct 4)",
    "🎄 Christmas / New Year (Dec-Jan)",
    "🎵 Music/Jazz (ALWAYS)",
    "🚀 Space / Science (Year-round)",
    "🎬 Classic Film Day (Year-round)",
    "👶 Children's Day / Family (Year-round)",
    "📼 Nostalgia/Retro (ALWAYS)",
]

for season in season_order:
    vids = season_counts.get(season, [])
    public_vids = [v for v in vids if v["privacy"] == "public"]
    print(f"\n{'━'*120}")
    print(f"  {season}")
    print(f"  📊 {len(public_vids)} public videos ({len(vids)} total incl. private)")
    print(f"{'━'*120}")
    
    # Sort by views descending
    vids_sorted = sorted(vids, key=lambda x: x["views"], reverse=True)
    for v in vids_sorted:
        status = "🔒" if v["privacy"] == "private" else "  "
        # Find reason
        info = video_seasons[v["id"]]
        reasons = []
        for sn, r in info["seasons"]:
            if sn == season:
                reasons = r
                break
        reason_str = ", ".join(reasons[:3])
        print(f"  {status} [{v['views']:>6} views] {v['series']:>20} | {v['title'][:75]:<75} | {reason_str}")

# Summary table
print(f"\n\n{'='*120}")
print("📊 SUMMARY: VIDEO COUNT PER SEASONAL CATEGORY")
print(f"{'='*120}")
print(f"{'Season':<55} {'Public':>8} {'Total':>8} {'Top Views':>10}")
print(f"{'─'*55} {'─'*8} {'─'*8} {'─'*10}")
for season in season_order:
    vids = season_counts.get(season, [])
    public_vids = [v for v in vids if v["privacy"] == "public"]
    top_views = max((v["views"] for v in vids), default=0)
    print(f"{season:<55} {len(public_vids):>8} {len(vids):>8} {top_views:>10}")

total_public = sum(1 for v in all_videos if v["privacy"] == "public")
total = len(all_videos)
print(f"\n{'─'*55} {'─'*8} {'─'*8}")
print(f"{'TOTAL VIDEOS':<55} {total_public:>8} {total:>8}")

# IMMEDIATE OPPORTUNITIES: Valentine's + February
print(f"\n\n{'='*120}")
print("🔥 IMMEDIATE OPPORTUNITY: VALENTINE'S DAY (Feb 14) - FULL EXPANSION")
print(f"{'='*120}")
print("""
The original detection found only 8 videos. Here's the EXPANDED list with creative angles:
""")

valentine_expanded = []
for v in all_videos:
    if v["privacy"] != "public":
        continue
    title_lower = v["title"].lower()
    desc_lower = v["desc"].lower()
    reasons = []
    
    # Direct love/romance keywords
    love_kw = ["love", "heart", "kiss", "romance", "sweetheart", "cupid", "beauty", "beautiful", "darling", "boop-oop-a-doop"]
    for kw in love_kw:
        if kw in title_lower or kw in desc_lower:
            reasons.append(f"💝 {kw}")
    
    # Betty Boop = sex appeal, flirting, Valentine's icon
    if v["series"] == "betty_boop":
        reasons.append("💋 Betty Boop = Valentine's icon")
    
    # Teaserama = pin-up, beauty, seduction
    if v["series"] == "teaserama":
        reasons.append("💃 Pin-up/burlesque = Valentine's adjacent")
    
    # Soundies with dance/music = romantic mood
    if v["series"] == "soundie":
        reasons.append("🎵 Vintage music = romantic mood")
    
    # Dance keywords
    dance_kw = ["dance", "dancing", "dancer", "tango", "waltz", "ballroom"]
    for kw in dance_kw:
        if kw in title_lower or kw in desc_lower:
            reasons.append(f"💃 {kw}")
    
    # Music/singing = mood setting
    music_kw = ["song", "sing", "serenade", "melody", "blues"]
    for kw in music_kw:
        if kw in title_lower:
            reasons.append(f"🎵 {kw}")
    
    # Night/moon = romantic
    night_kw = ["night", "moon", "moonlight", "star", "evening"]
    for kw in night_kw:
        if kw in title_lower:
            reasons.append(f"🌙 {kw}")
    
    # Couples/characters in love themes
    couple_kw = ["sailor", "girl", "boy", "minnie", "olive", "lois"]
    for kw in couple_kw:
        if kw in title_lower:
            reasons.append(f"👫 {kw}")
    
    if reasons:
        valentine_expanded.append({
            "title": v["title"],
            "series": v["series"],
            "views": v["views"],
            "reasons": reasons,
            "id": v["id"],
        })

valentine_expanded.sort(key=lambda x: len(x["reasons"]), reverse=True)
print(f"EXPANDED Valentine's potential: {len(valentine_expanded)} videos (was 8!)\n")
for i, v in enumerate(valentine_expanded, 1):
    reason_str = " | ".join(v["reasons"][:4])
    print(f"  {i:>3}. [{v['views']:>6} views] {v['series']:>15} | {v['title'][:65]:<65} | {reason_str}")

# Also: Anti-Valentine's
print(f"\n\n{'='*120}")
print("🖤 ANTI-VALENTINE'S DAY ANGLE")
print(f"{'='*120}")
anti_valentine = []
for v in all_videos:
    if v["privacy"] != "public":
        continue
    title_lower = v["title"].lower()
    reasons = []
    horror_kw = ["ghost", "casper", "monster", "horror", "nosferatu", "frankenstein", "vampire", "dracula", "phantom", "mad doctor", "jekyll", "hyde", "evil", "dark", "night", "death", "dead", "skeleton", "skull", "fear", "terror", "haunted", "witch", "demon", "devil", "spook"]
    for kw in horror_kw:
        if kw in title_lower:
            reasons.append(f"🖤 {kw}")
    if v["series"] == "casper":
        reasons.append("👻 Casper series")
    if reasons:
        anti_valentine.append({
            "title": v["title"],
            "series": v["series"],
            "views": v["views"],
            "reasons": reasons,
        })
anti_valentine.sort(key=lambda x: x["views"], reverse=True)
print(f"\nAnti-Valentine's potential: {len(anti_valentine)} videos\n")
for v in anti_valentine:
    reason_str = " | ".join(v["reasons"][:3])
    print(f"  [{v['views']:>6} views] {v['series']:>15} | {v['title'][:65]:<65} | {reason_str}")

print("\n\nDONE.")
