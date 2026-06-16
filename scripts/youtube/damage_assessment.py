#!/usr/bin/env python3
"""
Quick damage assessment: Check recent SEO changes and identify potential CTR killers.
Uses existing OAuth credentials from config/youtube_oauth.json
"""

import json
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"

# Load OAuth credentials
with open(CONFIG_DIR / 'youtube_oauth.json', 'r') as f:
    td = json.load(f)

yt = build('youtube', 'v3', credentials=Credentials(
    token=td['token'],
    refresh_token=td['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=td['client_id'],
    client_secret=td['client_secret']
))

def get_channel_videos(max_results=50):
    """Fetch recent videos from the channel."""
    channel_id = "UCVFv6Egpl0LDvigpFbQXNeQ"
    
    # Get uploads playlist
    ch_response = yt.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get recent videos
    videos = []
    pl_response = yt.playlistItems().list(
        part='contentDetails',
        playlistId=uploads_playlist,
        maxResults=max_results
    ).execute()
    
    video_ids = [item['contentDetails']['videoId'] for item in pl_response['items']]
    
    # Get full details
    v_response = yt.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    ).execute()
    
    return v_response['items']

def analyze_title_issues(title):
    """Check for common title problems."""
    issues = []
    
    # Lowercase title (looks unprofessional)
    if title[0].islower():
        issues.append("Starts with lowercase")
    
    # Missing brand
    if "@remAIke_IT" not in title:
        issues.append("Missing @remAIke_IT")
    
    # Missing quality indicator
    if "8K" not in title and "4K" not in title:
        issues.append("Missing quality (8K/4K)")
    
    # Too long (truncated in search)
    if len(title) > 70:
        issues.append(f"Too long ({len(title)} chars)")
    
    # Soundie format check
    if "soundie" in title.lower():
        if not title.startswith("Soundie:"):
            issues.append("Soundie: wrong format (should be 'Soundie: Title')")
    
    return issues

def analyze_tag_issues(tags):
    """Check for tag problems."""
    issues = []
    
    if len(tags) > 15:
        issues.append(f"Excessive tags ({len(tags)} - YouTube recommends <15)")
    
    # Check for spammy tags
    spammy = ["Official Audio", "Topic", "auto-generated", "official video"]
    found_spam = [t for t in tags if t in spammy]
    if found_spam:
        issues.append(f"Spammy tags: {found_spam}")
    
    return issues

def main():
    print("=" * 70)
    print("DAMAGE ASSESSMENT - remAIke.TV Channel")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    videos = get_channel_videos(50)
    
    title_issues_count = 0
    tag_issues_count = 0
    critical_videos = []
    
    for video in videos:
        vid = video['id']
        snippet = video['snippet']
        stats = video.get('statistics', {})
        
        title = snippet['title']
        tags = snippet.get('tags', [])
        views = int(stats.get('viewCount', 0))
        
        title_issues = analyze_title_issues(title)
        tag_issues = analyze_tag_issues(tags)
        
        if title_issues:
            title_issues_count += 1
        if tag_issues:
            tag_issues_count += 1
        
        # High-view videos with issues = critical
        if views > 500 and (title_issues or tag_issues):
            critical_videos.append({
                'id': vid,
                'title': title,
                'views': views,
                'title_issues': title_issues,
                'tag_issues': tag_issues,
                'tag_count': len(tags)
            })
    
    print(f"\n📊 SUMMARY ({len(videos)} videos analyzed):")
    print(f"   Videos with title issues: {title_issues_count}")
    print(f"   Videos with tag issues:   {tag_issues_count}")
    
    # Sort critical by views (highest first)
    critical_videos.sort(key=lambda x: x['views'], reverse=True)
    
    print(f"\n🚨 CRITICAL VIDEOS (>500 views + issues): {len(critical_videos)}")
    print("-" * 70)
    
    for i, v in enumerate(critical_videos[:20]):  # Top 20
        print(f"\n{i+1}. [{v['views']:,} views] {v['title'][:50]}...")
        print(f"   ID: {v['id']}")
        if v['title_issues']:
            print(f"   ❌ Title: {', '.join(v['title_issues'])}")
        if v['tag_issues']:
            print(f"   ❌ Tags: {', '.join(v['tag_issues'])}")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_analyzed': len(videos),
        'title_issues_count': title_issues_count,
        'tag_issues_count': tag_issues_count,
        'critical_videos': critical_videos
    }
    
    output_file = CONFIG_DIR / 'damage_assessment_20260126.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n📁 Full report saved: {output_file}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    print("""
1. TAG TRIM (Priority: HIGH)
   - Trim all videos to ≤12 tags
   - Remove: 'Official Audio', 'Topic', 'auto-generated'
   - File ready: config/pending_updates/tags_trim_remaike_20260126.json

2. TITLE FIXES (Priority: MEDIUM)
   - Soundies: 'Soundie: Title | 8K HQ | @remAIke_IT'
   - File ready: config/pending_updates/title_format_fix_20260126.json

3. A/B TEST (Priority: LOW)
   - Pick 5 high-view videos
   - Fix one at a time
   - Wait 72h between changes
   - Monitor CTR in YouTube Studio
""")

if __name__ == "__main__":
    main()
