#!/usr/bin/env python3
"""
Deep analysis: Fetch ALL videos and find the real damage.
Focus on high-performing videos that may have been hurt.
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

def get_all_videos():
    """Fetch ALL videos from the channel."""
    channel_id = "UCVFv6Egpl0LDvigpFbQXNeQ"
    
    # Get uploads playlist
    ch_response = yt.channels().list(
        part='contentDetails,statistics',
        id=channel_id
    ).execute()
    
    channel_stats = ch_response['items'][0]['statistics']
    print(f"📺 Channel: {channel_stats.get('videoCount', '?')} videos, {channel_stats.get('viewCount', '?')} total views")
    
    uploads_playlist = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Paginate through ALL videos
    all_video_ids = []
    next_page = None
    
    while True:
        pl_response = yt.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        all_video_ids.extend([item['contentDetails']['videoId'] for item in pl_response['items']])
        next_page = pl_response.get('nextPageToken')
        
        if not next_page:
            break
    
    print(f"📼 Found {len(all_video_ids)} videos")
    
    # Batch fetch video details (50 at a time)
    all_videos = []
    for i in range(0, len(all_video_ids), 50):
        batch = all_video_ids[i:i+50]
        v_response = yt.videos().list(
            part='snippet,statistics',
            id=','.join(batch)
        ).execute()
        all_videos.extend(v_response['items'])
    
    return all_videos

def analyze_video(video):
    """Return issues dict for a video."""
    snippet = video['snippet']
    stats = video.get('statistics', {})
    
    title = snippet['title']
    tags = snippet.get('tags', [])
    views = int(stats.get('viewCount', 0))
    
    issues = {
        'title': [],
        'tags': []
    }
    
    # Title checks
    if title[0].islower():
        issues['title'].append("lowercase_start")
    if "@remAIke_IT" not in title:
        issues['title'].append("missing_brand")
    if "8K" not in title and "4K" not in title:
        issues['title'].append("missing_quality")
    if len(title) > 70:
        issues['title'].append("too_long")
    if "soundie" in title.lower() and not title.startswith("Soundie:"):
        issues['title'].append("wrong_soundie_format")
    
    # Tag checks
    if len(tags) > 15:
        issues['tags'].append(f"excessive_{len(tags)}")
    
    spammy = ["Official Audio", "Topic", "auto-generated", "official video"]
    if any(t in spammy for t in tags):
        issues['tags'].append("spammy_tags")
    
    return {
        'id': video['id'],
        'title': title,
        'views': views,
        'tag_count': len(tags),
        'issues': issues,
        'has_issues': bool(issues['title'] or issues['tags'])
    }

def main():
    print("=" * 70)
    print("FULL CHANNEL DAMAGE ASSESSMENT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    videos = get_all_videos()
    
    # Analyze all
    results = [analyze_video(v) for v in videos]
    
    # Sort by views
    results.sort(key=lambda x: x['views'], reverse=True)
    
    # Stats
    with_issues = [r for r in results if r['has_issues']]
    high_view_issues = [r for r in with_issues if r['views'] > 1000]
    
    print(f"\n📊 FULL ANALYSIS ({len(results)} videos):")
    print(f"   Total with issues:      {len(with_issues)}")
    print(f"   High-view (>1000) + issues: {len(high_view_issues)}")
    
    # Breakdown
    title_issues = {}
    tag_issues = {}
    
    for r in with_issues:
        for issue in r['issues']['title']:
            title_issues[issue] = title_issues.get(issue, 0) + 1
        for issue in r['issues']['tags']:
            tag_issues[issue] = tag_issues.get(issue, 0) + 1
    
    print(f"\n📝 TITLE ISSUES BREAKDOWN:")
    for issue, count in sorted(title_issues.items(), key=lambda x: -x[1]):
        print(f"   {count:3d}x {issue}")
    
    print(f"\n🏷️ TAG ISSUES BREAKDOWN:")
    for issue, count in sorted(tag_issues.items(), key=lambda x: -x[1]):
        print(f"   {count:3d}x {issue}")
    
    # Top 20 high-view videos with issues
    print(f"\n🚨 TOP 20 HIGH-VIEW VIDEOS WITH ISSUES:")
    print("-" * 70)
    
    for i, r in enumerate(high_view_issues[:20]):
        print(f"\n{i+1}. [{r['views']:,} views] {r['title'][:55]}...")
        print(f"   ID: https://youtube.com/watch?v={r['id']}")
        print(f"   Tags: {r['tag_count']}")
        if r['issues']['title']:
            print(f"   ❌ Title: {', '.join(r['issues']['title'])}")
        if r['issues']['tags']:
            print(f"   ❌ Tags: {', '.join(r['issues']['tags'])}")
    
    # Save full report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_videos': len(results),
        'videos_with_issues': len(with_issues),
        'high_view_issues': len(high_view_issues),
        'title_issues_breakdown': title_issues,
        'tag_issues_breakdown': tag_issues,
        'top_problem_videos': high_view_issues[:50]
    }
    
    output_file = CONFIG_DIR / 'full_damage_report_20260126.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n📁 Full report: {output_file}")

if __name__ == "__main__":
    main()
