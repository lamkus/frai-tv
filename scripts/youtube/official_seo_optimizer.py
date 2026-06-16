#!/usr/bin/env python3
"""
YouTube SEO Optimizer - Based on OFFICIAL YouTube Guidelines 2026

Sources:
- https://support.google.com/youtube/answer/146402 (Tags)
- https://support.google.com/youtube/answer/16090438 (Search Ranking)
- https://support.google.com/youtube/answer/2801973 (Spam Policy)
- https://developers.google.com/youtube/v3/docs/videos (API Docs)

OFFICIAL RULES:
1. Tags have MINIMAL role - title/thumbnail/description are MORE IMPORTANT
2. Tags max 500 CHARACTERS total (not 500 tags!)
3. Excessive tags = SPAM POLICY VIOLATION
4. Search ranking: Relevance > Engagement > Quality (E-A-T)
5. Title max 100 chars
"""

import json
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = CONFIG_DIR / "pending_updates"

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

# OFFICIAL LIMITS
MAX_TAG_CHARS = 500  # YouTube API limit
MAX_TITLE_CHARS = 100  # YouTube API limit
RECOMMENDED_TAG_COUNT = 8  # Best practice: focused, relevant tags

# Tags that are SPAM per YouTube policy (misleading/deceptive)
SPAM_TAGS = {
    "Official Audio",  # Misleading - we're not official
    "Topic",  # Auto-generated channel indicator
    "auto-generated",  # Misleading
    "official video",  # Misleading - we're not the official source
}

def get_all_channel_videos():
    """Fetch all videos from channel."""
    channel_id = "UCVFv6Egpl0LDvigpFbQXNeQ"
    
    ch_response = yt.channels().list(part='contentDetails', id=channel_id).execute()
    uploads_playlist = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
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
    
    all_videos = []
    for i in range(0, len(all_video_ids), 50):
        batch = all_video_ids[i:i+50]
        v_response = yt.videos().list(
            part='snippet,statistics',
            id=','.join(batch)
        ).execute()
        all_videos.extend(v_response['items'])
    
    return all_videos

def calculate_tag_chars(tags):
    """Calculate total character count for tags (YouTube's actual limit)."""
    # Tags with spaces count as quoted: "Foo Baz" = 9 chars (including quotes)
    total = 0
    for tag in tags:
        if ' ' in tag:
            total += len(tag) + 2  # +2 for quotes
        else:
            total += len(tag)
        total += 1  # comma separator
    return total - 1 if tags else 0  # remove last comma

def optimize_tags(current_tags, title):
    """
    Optimize tags following OFFICIAL YouTube guidelines:
    - Remove spam/misleading tags
    - Keep within 500 char limit
    - Focus on relevance (match title keywords)
    """
    if not current_tags:
        return []
    
    # Step 1: Remove spam tags
    clean_tags = [t for t in current_tags if t not in SPAM_TAGS]
    
    # Step 2: Prioritize tags that match title keywords (relevance!)
    title_words = set(title.lower().split())
    
    def tag_priority(tag):
        tag_lower = tag.lower()
        # Higher priority if tag words appear in title
        matches = sum(1 for word in tag_lower.split() if word in title_words)
        return -matches  # Negative for sorting (more matches = higher priority)
    
    # Sort by relevance to title
    sorted_tags = sorted(clean_tags, key=tag_priority)
    
    # Step 3: Keep within 500 char limit, prefer ~8 focused tags
    final_tags = []
    char_count = 0
    
    for tag in sorted_tags:
        tag_chars = len(tag) + 2 if ' ' in tag else len(tag)
        if char_count + tag_chars + 1 <= MAX_TAG_CHARS:
            final_tags.append(tag)
            char_count += tag_chars + 1
            
            # Stop at recommended count unless we have very relevant tags
            if len(final_tags) >= RECOMMENDED_TAG_COUNT * 2:  # Allow up to 16 if all relevant
                break
    
    return final_tags

def analyze_and_fix_video(video):
    """Analyze video and generate fix if needed."""
    snippet = video['snippet']
    stats = video.get('statistics', {})
    
    video_id = video['id']
    title = snippet['title']
    current_tags = snippet.get('tags', [])
    views = int(stats.get('viewCount', 0))
    
    issues = []
    fixes = {}
    
    # Check tag issues
    current_tag_chars = calculate_tag_chars(current_tags)
    has_spam = any(t in SPAM_TAGS for t in current_tags)
    
    if current_tag_chars > MAX_TAG_CHARS:
        issues.append(f"tags_over_limit_{current_tag_chars}_chars")
    if has_spam:
        issues.append("has_spam_tags")
    if len(current_tags) > 20:
        issues.append(f"excessive_tag_count_{len(current_tags)}")
    
    # Check title issues
    if len(title) > MAX_TITLE_CHARS:
        issues.append(f"title_too_long_{len(title)}_chars")
    
    # Generate fixes if needed
    if issues:
        optimized_tags = optimize_tags(current_tags, title)
        
        # Only include tag fix if actually different
        if set(optimized_tags) != set(current_tags):
            fixes['tags'] = {
                'old_count': len(current_tags),
                'old_chars': current_tag_chars,
                'new_tags': optimized_tags,
                'new_count': len(optimized_tags),
                'new_chars': calculate_tag_chars(optimized_tags)
            }
    
    return {
        'id': video_id,
        'title': title,
        'views': views,
        'issues': issues,
        'fixes': fixes,
        'needs_fix': bool(fixes)
    }

def main():
    print("=" * 70)
    print("YOUTUBE SEO OPTIMIZER - OFFICIAL GUIDELINES 2026")
    print("=" * 70)
    print("""
📚 BASED ON OFFICIAL SOURCES:
   • Tags have MINIMAL role (YouTube Support)
   • Max 500 CHARACTERS for tags (API Docs)
   • Excessive tags = SPAM violation (Policy)
   • Title/Thumbnail/Description > Tags (Official)
""")
    
    print("🔄 Fetching all videos...")
    videos = get_all_channel_videos()
    print(f"📺 Found {len(videos)} videos\n")
    
    # Analyze all videos
    results = [analyze_and_fix_video(v) for v in videos]
    
    # Statistics
    needs_fix = [r for r in results if r['needs_fix']]
    has_spam = [r for r in results if 'has_spam_tags' in r['issues']]
    over_limit = [r for r in results if any('over_limit' in i for i in r['issues'])]
    excessive = [r for r in results if any('excessive' in i for i in r['issues'])]
    
    print("📊 ANALYSIS RESULTS:")
    print(f"   Total videos:           {len(results)}")
    print(f"   Videos needing fixes:   {len(needs_fix)}")
    print(f"   With spam tags:         {len(has_spam)}")
    print(f"   Over 500 char limit:    {len(over_limit)}")
    print(f"   Excessive tag count:    {len(excessive)}")
    
    # Sort by views (fix high-performers first)
    needs_fix.sort(key=lambda x: x['views'], reverse=True)
    
    print(f"\n🔧 TOP 10 HIGH-VIEW VIDEOS NEEDING FIXES:")
    print("-" * 70)
    
    for i, r in enumerate(needs_fix[:10]):
        print(f"\n{i+1}. [{r['views']:,} views] {r['title'][:50]}...")
        print(f"   Issues: {', '.join(r['issues'])}")
        if r['fixes'].get('tags'):
            tf = r['fixes']['tags']
            print(f"   Tags: {tf['old_count']} ({tf['old_chars']} chars) → {tf['new_count']} ({tf['new_chars']} chars)")
    
    # Save fix plan
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    fix_plan = {
        'timestamp': datetime.now().isoformat(),
        'based_on': 'Official YouTube Guidelines 2026',
        'sources': [
            'https://support.google.com/youtube/answer/146402',
            'https://support.google.com/youtube/answer/16090438',
            'https://support.google.com/youtube/answer/2801973',
        ],
        'summary': {
            'total_videos': len(results),
            'needs_fix': len(needs_fix),
            'spam_tags_found': len(has_spam),
            'over_char_limit': len(over_limit),
            'excessive_count': len(excessive)
        },
        'fixes': needs_fix
    }
    
    output_file = OUTPUT_DIR / 'official_seo_fixes_20260126.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fix_plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n📁 Fix plan saved: {output_file}")
    
    print("\n" + "=" * 70)
    print("⏭️ NEXT STEPS:")
    print("=" * 70)
    print("""
1. REVIEW the fix plan in: config/pending_updates/official_seo_fixes_20260126.json
2. RUN the apply script with --dry-run first
3. APPLY fixes in batches (50 videos max per day to avoid algorithm shock)
4. MONITOR CTR in YouTube Studio for 72h after each batch
""")

if __name__ == "__main__":
    main()
