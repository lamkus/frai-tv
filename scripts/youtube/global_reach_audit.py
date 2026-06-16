
import json
import re
import os

# --- 2026 REACH STANDARD ---
# Title: Must contain "8K" AND ("4K" OR "UHD")
# Tags: Max 15, Must contain "8K", "4K", "UHD", "Remastered"
# Hashtags: Max 5
# Branding: Must contain "@remAIke_IT" only in Description, not Title (per previous instruction, but user said "ensure branding" in prompt, let's stick to Description for branding to save Title space for 4K/UHD)

def calculate_reach_score(video):
    score = 0
    issues = []
    
    snippet = video.get('snippet', {})
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    # 1. TITLE ANALYSIS (40 pts)
    # Check for 8K
    if "8K" in title.upper():
        score += 20
    else:
        issues.append("MISSING_TITLE_8K")
        
    # Check for 4K/UHD
    if "4K" in title.upper() or "UHD" in title.upper():
        score += 20
    else:
        issues.append("MISSING_TITLE_4K_UHD")
        
    # 2. TAG ANALYSIS (30 pts)
    # Count
    if len(tags) > 15:
        issues.append(f"TOO_MANY_TAGS ({len(tags)})")
        score += 0 # Penalty
    elif len(tags) < 5:
        issues.append("TOO_FEW_TAGS")
        score += 10
    else:
        score += 10
        
    # Keywords
    upper_tags = [t.upper() for t in tags]
    if "4K" in upper_tags and "8K" in upper_tags:
        score += 20
    else:
        issues.append("MISSING_CORE_TAGS_(4K/8K)")
        
    # 3. DESCRIPTION & HASHTAGS (30 pts)
    # Hashtag Count
    hashtags = [word for word in desc.split() if word.startswith('#')]
    if len(hashtags) > 5:
        issues.append(f"HASHTAG_SPAM ({len(hashtags)})")
        score += 0
    elif len(hashtags) == 0:
        issues.append("NO_HASHTAGS")
        score += 0
    else:
        score += 15
        
    # Links
    if "remaike.it" in desc.lower() or "remaike.tv" in desc.lower():
        score += 15
    else:
        issues.append("MISSING_WEBSITE_LINK")
        
    return score, issues

def detect_series(title):
    title_lower = title.lower()
    if "alfred j. kwak" in title_lower: return "Alfred J. Kwak"
    if "betty boop" in title_lower: return "Betty Boop"
    if "popeye" in title_lower: return "Popeye"
    if "superman" in title_lower: return "Superman"
    if "felix the cat" in title_lower: return "Felix the Cat"
    if "gulliver" in title_lower: return "Gulliver's Travels"
    if "bravestarr" in title_lower: return "Bravestarr"
    if "soundie" in title_lower: return "Soundies"
    if "wochenschau" in title_lower: return "Wochenschau"
    if "looney tunes" in title_lower: return "Looney Tunes"
    if "merrie melodies" in title_lower: return "Looney Tunes" # Grouping
    if "color classic" in title_lower: return "Color Classics"
    return "Misc"

def main():
    print("🚀 Starting Global Reach & Optimization Audit (2026 Standards)...")
    
    with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    videos = data.get('videos', [])
    public_videos = [v for v in videos if v['status']['privacyStatus'] == 'public']
    
    print(f"📊 Analyzing {len(public_videos)} Public Videos...")
    
    results = {
        "summary": {
            "total_checked": len(public_videos),
            "perfect_score": 0,
            "needs_work": 0,
            "avg_score": 0
        },
        "series_breakdown": {},
        "details": []
    }
    
    total_score = 0
    
    for v in public_videos:
        score, issues = calculate_reach_score(v)
        series = detect_series(v['snippet']['title'])
        
        # Stats
        total_score += score
        if score == 100:
            results["summary"]["perfect_score"] += 1
        else:
            results["summary"]["needs_work"] += 1
            
        # Series Stats
        if series not in results["series_breakdown"]:
            results["series_breakdown"][series] = {"count": 0, "avg_score": 0, "total_series_score": 0}
        
        results["series_breakdown"][series]["count"] += 1
        results["series_breakdown"][series]["total_series_score"] += score
        
        # Log Detail Only if NOT perfect
        if score < 100:
            results["details"].append({
                "id": v['id'],
                "title": v['snippet']['title'],
                "series": series,
                "score": score,
                "issues": issues
            })
            
    # Finalize Averages
    results["summary"]["avg_score"] = round(total_score / len(public_videos), 1)
    
    for s in results["series_breakdown"]:
        data = results["series_breakdown"][s]
        data["avg_score"] = round(data["total_series_score"] / data["count"], 1)
        del data["total_series_score"] # Cleanup
        
    # Sort Breakdown by Score (ascending - worst first)
    sorted_breakdown = dict(sorted(results["series_breakdown"].items(), key=lambda item: item[1]['avg_score']))
    results["series_breakdown"] = sorted_breakdown
        
    # Output
    with open('config/global_reach_audit.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"✅ Audit Complete. Avg Score: {results['summary']['avg_score']}/100")
    print("\n📉 WORST PERFORMING SERIES:")
    for k, v in list(sorted_breakdown.items())[:5]:
        print(f"   • {k}: {v['avg_score']}/100 ({v['count']} videos)")
        
    print("\n📄 Full report saved to 'config/global_reach_audit.json'")

if __name__ == "__main__":
    main()
