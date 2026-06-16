"""
Live Channel Update - Fetches ALL current data from YouTube API
and creates a comprehensive channel snapshot.

Quota: ~10 units (channel + playlists + video batches)
"""
import json, os, sys
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Setup
creds_data = json.load(open('config/youtube_oauth.json'))
creds = Credentials(
    token=creds_data['access_token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
yt = build('youtube', 'v3', credentials=creds)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

print("=" * 60)
print("  remAIke_IT — LIVE CHANNEL UPDATE")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

# ── 1. CHANNEL STATS ──
print("\n📊 Fetching channel stats...")
ch = yt.channels().list(
    part='snippet,statistics,brandingSettings,contentDetails,status',
    id=CHANNEL_ID
).execute()
c = ch['items'][0]
stats = c['statistics']

channel_info = {
    'channel_id': CHANNEL_ID,
    'name': c['snippet']['title'],
    'handle': '@remAIke_IT',
    'subscribers': int(stats['subscriberCount']),
    'total_views': int(stats['viewCount']),
    'video_count': int(stats['videoCount']),
    'published_at': c['snippet']['publishedAt'],
    'country': c['snippet'].get('country', 'N/A'),
    'upload_playlist': UPLOAD_PL,
    'keywords': c.get('brandingSettings', {}).get('channel', {}).get('keywords', ''),
}

print(f"  Channel: {channel_info['name']}")
print(f"  Subscribers: {channel_info['subscribers']:,}")
print(f"  Total Views: {channel_info['total_views']:,}")
print(f"  Video Count: {channel_info['video_count']}")
print(f"  Country: {channel_info['country']}")

# ── 2. ALL VIDEOS ──
print("\n🎬 Fetching all videos from upload playlist...")
all_video_ids = []
next_page = None
while True:
    pl_resp = yt.playlistItems().list(
        part='contentDetails',
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=next_page
    ).execute()
    for item in pl_resp['items']:
        all_video_ids.append(item['contentDetails']['videoId'])
    next_page = pl_resp.get('nextPageToken')
    if not next_page:
        break
print(f"  Found {len(all_video_ids)} videos in upload playlist")

# ── 3. VIDEO DETAILS ──
print("\n📋 Fetching video details (batches of 50)...")
all_videos = []
for i in range(0, len(all_video_ids), 50):
    batch = all_video_ids[i:i+50]
    vid_resp = yt.videos().list(
        part='snippet,statistics,contentDetails,status',
        id=','.join(batch)
    ).execute()
    for v in vid_resp.get('items', []):
        vid = {
            'id': v['id'],
            'title': v['snippet']['title'],
            'published': v['snippet']['publishedAt'],
            'category': v['snippet']['categoryId'],
            'tags': v['snippet'].get('tags', []),
            'description_length': len(v['snippet'].get('description', '')),
            'duration': v['contentDetails']['duration'],
            'privacy': v['status']['privacyStatus'],
            'views': int(v['statistics'].get('viewCount', 0)),
            'likes': int(v['statistics'].get('likeCount', 0)),
            'comments': int(v['statistics'].get('commentCount', 0)),
        }
        all_videos.append(vid)
    print(f"  Batch {i//50 + 1}: {len(vid_resp.get('items', []))} videos")

print(f"  Total videos fetched: {len(all_videos)}")

# ── 4. PLAYLISTS ──
print("\n📂 Fetching all playlists...")
all_playlists = []
next_page = None
while True:
    pl_resp = yt.playlists().list(
        part='snippet,contentDetails',
        channelId=CHANNEL_ID,
        maxResults=50,
        pageToken=next_page
    ).execute()
    for pl in pl_resp['items']:
        all_playlists.append({
            'id': pl['id'],
            'title': pl['snippet']['title'],
            'video_count': pl['contentDetails']['itemCount'],
            'description': pl['snippet'].get('description', '')[:100],
        })
    next_page = pl_resp.get('nextPageToken')
    if not next_page:
        break
print(f"  Found {len(all_playlists)} playlists")

# ── 5. ANALYSIS ──
print("\n" + "=" * 60)
print("  📊 ANALYSIS")
print("=" * 60)

# Privacy breakdown
public = [v for v in all_videos if v['privacy'] == 'public']
private = [v for v in all_videos if v['privacy'] == 'private']
unlisted = [v for v in all_videos if v['privacy'] == 'unlisted']
print(f"\n  Privacy: {len(public)} public | {len(private)} private | {len(unlisted)} unlisted")

# Views distribution
total_views = sum(v['views'] for v in public)
total_likes = sum(v['likes'] for v in public)
total_comments = sum(v['comments'] for v in public)

views_0 = len([v for v in public if v['views'] == 0])
views_1_99 = len([v for v in public if 0 < v['views'] < 100])
views_100_999 = len([v for v in public if 100 <= v['views'] < 1000])
views_1k_5k = len([v for v in public if 1000 <= v['views'] < 5000])
views_5k_plus = len([v for v in public if v['views'] >= 5000])

print(f"\n  Total Views: {total_views:,}")
print(f"  Total Likes: {total_likes:,}")
print(f"  Total Comments: {total_comments:,}")
print(f"  Avg Views/Video: {total_views / max(len(public), 1):.0f}")
print(f"  Avg Likes/Video: {total_likes / max(len(public), 1):.1f}")

print(f"\n  Views Distribution:")
print(f"    0 views:     {views_0:>4} ({views_0/max(len(public),1)*100:.1f}%)")
print(f"    1-99 views:  {views_1_99:>4} ({views_1_99/max(len(public),1)*100:.1f}%)")
print(f"    100-999:     {views_100_999:>4} ({views_100_999/max(len(public),1)*100:.1f}%)")
print(f"    1K-5K:       {views_1k_5k:>4} ({views_1k_5k/max(len(public),1)*100:.1f}%)")
print(f"    5K+:         {views_5k_plus:>4} ({views_5k_plus/max(len(public),1)*100:.1f}%)")

# Top 20 videos
print(f"\n  🏆 Top 20 Videos:")
sorted_vids = sorted(public, key=lambda v: v['views'], reverse=True)
for i, v in enumerate(sorted_vids[:20], 1):
    print(f"    {i:>2}. {v['views']:>7,} views | {v['likes']:>3} likes | {v['title'][:60]}")

# Content classification
def classify(title):
    tl = title.lower()
    if 'betty boop' in tl: return 'Betty Boop'
    if 'alfred' in tl and ('kwak' in tl or 'quack' in tl): return 'Alfred J. Kwak'
    if 'superman' in tl or 'fleischer' in tl: return 'Superman/Fleischer'
    if 'felix' in tl and 'cat' in tl: return 'Felix the Cat'
    if 'popeye' in tl: return 'Popeye'
    if 'porky' in tl or 'looney' in tl or 'merrie' in tl or 'bosko' in tl or 'daffy' in tl: return 'Looney Tunes/WB'
    if 'soundie' in tl: return 'Soundies'
    if 'wochenschau' in tl or 'newsreel' in tl: return 'Wochenschau'
    if 'bravestarr' in tl or 'brave starr' in tl: return 'BraveStarr'
    if 'maulwurf' in tl or 'krtek' in tl: return 'Der kleine Maulwurf'
    if 'casper' in tl: return 'Casper'
    if 'christmas' in tl or 'xmas' in tl or 'holiday' in tl or 'santa' in tl: return 'Christmas'
    if 'chaplin' in tl: return 'Charlie Chaplin'
    if 'keaton' in tl or 'buster' in tl: return 'Buster Keaton'
    if 'mel-o-toon' in tl or 'melotoon' in tl: return 'Mel-O-Toons'
    if 'astro boy' in tl: return 'Astro Boy'
    if 'ken block' in tl or 'gymkhana' in tl: return 'Ken Block'
    if 'glücksbärchi' in tl or 'care bear' in tl: return 'Glücksbärchis'
    if any(x in tl for x in ['méliès', 'melies', 'astronomer']): return 'Georges Méliès'
    if 'dinner for one' in tl: return 'Dinner for One'
    return 'Other'

categories = {}
for v in all_videos:
    cat = classify(v['title'])
    if cat not in categories:
        categories[cat] = {'count': 0, 'public': 0, 'private': 0, 'views': 0, 'likes': 0, 'comments': 0, 'videos': []}
    categories[cat]['count'] += 1
    if v['privacy'] == 'public':
        categories[cat]['public'] += 1
        categories[cat]['views'] += v['views']
        categories[cat]['likes'] += v['likes']
        categories[cat]['comments'] += v['comments']
    else:
        categories[cat]['private'] += 1
    categories[cat]['videos'].append({'id': v['id'], 'title': v['title'], 'views': v['views'], 'privacy': v['privacy']})

print(f"\n  📂 Content Categories (sorted by avg views):")
print(f"  {'Category':<25} {'Total':>5} {'Pub':>4} {'Priv':>4} {'Views':>8} {'Ø Views':>8} {'Likes':>5}")
print(f"  {'-'*25} {'-----':>5} {'----':>4} {'----':>4} {'--------':>8} {'--------':>8} {'-----':>5}")

sorted_cats = sorted(categories.items(), key=lambda x: x[1]['views']/max(x[1]['public'],1), reverse=True)
for cat, data in sorted_cats:
    avg_v = data['views'] / max(data['public'], 1)
    print(f"  {cat:<25} {data['count']:>5} {data['public']:>4} {data['private']:>4} {data['views']:>8,} {avg_v:>8,.0f} {data['likes']:>5}")

# Category distribution (YouTube category IDs)
print(f"\n  🏷️ YouTube Categories:")
cat_ids = {}
for v in public:
    cid = v['category']
    cat_ids[cid] = cat_ids.get(cid, 0) + 1
cat_names = {'1': 'Film & Animation', '10': 'Music', '22': 'People & Blogs', 
             '24': 'Entertainment', '25': 'News & Politics', '27': 'Education',
             '17': 'Sports', '15': 'Pets & Animals', '20': 'Gaming'}
for cid, count in sorted(cat_ids.items(), key=lambda x: x[1], reverse=True):
    name = cat_names.get(cid, f'Category {cid}')
    print(f"    {name} ({cid}): {count}")

# Playlists
print(f"\n  📋 Playlists ({len(all_playlists)}):")
for pl in sorted(all_playlists, key=lambda x: x['video_count'], reverse=True):
    print(f"    {pl['video_count']:>4} videos | {pl['title'][:55]}")

# ── 6. SAVE SNAPSHOT ──
snapshot = {
    'snapshot_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'channel': channel_info,
    'summary': {
        'total_videos': len(all_videos),
        'public': len(public),
        'private': len(private),
        'unlisted': len(unlisted),
        'total_views': total_views,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avg_views_per_video': round(total_views / max(len(public), 1), 1),
        'views_distribution': {
            '0': views_0,
            '1-99': views_1_99,
            '100-999': views_100_999,
            '1K-5K': views_1k_5k,
            '5K+': views_5k_plus,
        }
    },
    'categories': {cat: {k: v for k, v in data.items() if k != 'videos'} for cat, data in sorted_cats},
    'top_20': [{'id': v['id'], 'title': v['title'], 'views': v['views'], 'likes': v['likes']} for v in sorted_vids[:20]],
    'playlists': all_playlists,
    'all_videos': all_videos,
}

out_file = 'config/channel_snapshot_2026_02_06.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(snapshot, f, ensure_ascii=False, indent=2)
print(f"\n✅ Snapshot saved: {out_file}")
print(f"   Quota used: ~{2 + len(all_video_ids)//50 + 2 + 1} units")
