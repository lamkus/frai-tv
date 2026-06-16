"""
Fix remaining problem videos - 2026-02-08
Fixes: titles, descriptions, tags, categories, hashtags
"""
import json, os, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

# Standard CTA block
CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT
"""

# Videos to fix with their new metadata
FIXES = [
    {
        'id': 'HGg-g6SwrrQ',
        'new_title': 'Reefer Madness (1938) | Anti-Cannabis Propaganda | 8K HQ (4K UHD)',
        'fix_desc': True,  # remove excess hashtags, add CTA + links
        'fix_tags': True,
        'new_tags': ['Reefer Madness', '1938', 'anti-cannabis', 'propaganda film', 'public domain', 
                     '8K', 'vintage film', 'drug propaganda', 'classic movie', 'restored'],
    },
    {
        'id': 'TWodj8k8-zU',
        'new_title': 'Alfred J. Kwak (29/52): Die Burengänse | 8K HQ (4K UHD)',
        'fix_desc': True,
        'fix_tags': True,
        'new_tags': ['Alfred J. Kwak', 'Alfred Jodocus Kwak', 'Die Burengänse', 'Episode 29',
                     '8K', 'anime', 'classic cartoon', 'Herman van Veen', 'Kwak Quack',
                     'vintage animation', 'restored'],
    },
    {
        'id': 's_0yOzCKDa8',
        'new_title': 'December 7th: Pearl Harbor (1943) | Documentary | 8K HQ (4K UHD)',
        'fix_desc': True,
        'fix_tags': True,
        'new_tags': ['Pearl Harbor', 'December 7th', '1943', 'WWII', 'World War II', 'documentary',
                     '8K', 'public domain', 'John Ford', 'war documentary', 'historical'],
    },
    {
        'id': 'A8LWgWF5f5k',
        'new_title': 'The Hut-Sut Song (1940s) | Soundie | 8K HQ (4K UHD)',
        'fix_desc': True,
        'fix_tags': True,
        'new_tags': ['soundie', 'Hut-Sut Song', '1940s', 'vintage music', 'jazz', 'swing',
                     '8K', 'public domain', 'jukebox music', 'classic music'],
        'category': '10',  # Music
    },
    {
        'id': 'eX5cbYwNvnI',
        'new_title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ (4K UHD)',
        'fix_desc': True,
        'fix_tags': True,
        'new_tags': ['Betty Boop', 'Betty Boop Limited', '1932', 'Fleischer Studios', 'Max Fleischer',
                     '8K', 'vintage animation', 'classic cartoon', 'public domain', 'restored'],
    },
    {
        'id': 'eF81rBeXbzk',
        'new_title': 'The Hindenburg Explodes (1937) | Disaster Documentary | 8K HQ (4K UHD)',
        'fix_desc': True,
        'fix_tags': True,
        'new_tags': ['Hindenburg', 'Hindenburg disaster', '1937', 'zeppelin', 'airship',
                     '8K', 'historical footage', 'public domain', 'documentary', 'disaster'],
    },
]

def fix_description(desc):
    """Fix description: trim hashtags to max 5, add CTA + links if missing"""
    lines = desc.split('\n')
    
    # Count and trim hashtags
    new_lines = []
    hashtag_count = 0
    hashtags_kept = []
    
    for line in lines:
        words = line.split()
        new_words = []
        for word in words:
            if word.startswith('#') and len(word) > 1:
                hashtag_count += 1
                if len(hashtags_kept) < 5:
                    hashtags_kept.append(word)
                    new_words.append(word)
                # else: skip excess hashtag
            else:
                new_words.append(word)
        new_line = ' '.join(new_words).strip()
        if new_line or not words:  # Keep empty lines
            new_lines.append(new_line)
    
    desc = '\n'.join(new_lines)
    
    # Add CTA block if missing
    has_cta = any(w in desc.upper() for w in ['SUBSCRIBE', 'LIKE IF', 'COMMENT YOUR'])
    if not has_cta:
        desc = desc.rstrip() + '\n' + CTA_BLOCK
    
    # Add website link if missing
    if 'remaike.it' not in desc.lower() and 'remaike.tv' not in desc.lower():
        if '🌐' not in desc:
            desc += '\n🌐 www.remaike.IT'
    
    # Add channel link if missing
    if '@remAIke_IT' not in desc and 'youtube.com/@remAIke' not in desc:
        if '📺' not in desc:
            desc += '\n📺 https://www.youtube.com/@remAIke_IT'
    
    return desc

def main():
    print("🔧 Fixing remaining problem videos...")
    youtube = get_youtube()
    
    fixed = 0
    errors = 0
    
    for fix in FIXES:
        vid_id = fix['id']
        print(f"\n--- Processing: {vid_id} ---")
        
        try:
            # GET current video
            res = youtube.videos().list(part='snippet', id=vid_id).execute()
            if not res['items']:
                print(f"  ❌ Video not found: {vid_id}")
                errors += 1
                continue
            
            snippet = res['items'][0]['snippet']
            old_title = snippet['title']
            
            # Apply title fix
            snippet['title'] = fix['new_title']
            print(f"  Title: {old_title[:50]}...")
            print(f"     →   {fix['new_title'][:50]}...")
            
            # Fix description
            if fix.get('fix_desc'):
                snippet['description'] = fix_description(snippet['description'])
            
            # Fix tags
            if fix.get('fix_tags') and fix.get('new_tags'):
                snippet['tags'] = fix['new_tags']
            
            # Fix category
            if fix.get('category'):
                snippet['categoryId'] = fix['category']
            
            # UPDATE
            youtube.videos().update(
                part='snippet',
                body={'id': vid_id, 'snippet': snippet}
            ).execute()
            
            print(f"  ✅ Updated successfully!")
            fixed += 1
            time.sleep(1)
            
        except Exception as e:
            if 'quotaExceeded' in str(e):
                print("🛑 QUOTA EXCEEDED! Stopping.")
                break
            print(f"  ❌ Error: {e}")
            errors += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Fixed: {fixed}")
    print(f"❌ Errors: {errors}")
    print(f"Quota used: ~{fixed * 51} units")

if __name__ == '__main__':
    main()
