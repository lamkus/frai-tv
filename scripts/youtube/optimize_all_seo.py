#!/usr/bin/env python3
"""Fix Alfred J. Kwak (1/52) and Marihuana hashtags, then optimize tags/hashtags for all."""
import json
import os
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
OAUTH_PATH = os.path.join(CONFIG_DIR, 'youtube_oauth.json')

def load_credentials():
    with open(OAUTH_PATH, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    if creds.expired:
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(OAUTH_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    return creds

def get_category_tags(title):
    """Get optimal tags based on video category."""
    title_lower = title.lower()
    
    base_tags = ['8K', 'remAIke', 'public domain', 'restored', 'AI upscale']
    
    if 'betty boop' in title_lower:
        return base_tags + ['Betty Boop', 'Fleischer', 'vintage animation', '1930s', 'cartoon', 'classic cartoon']
    elif 'popeye' in title_lower:
        return base_tags + ['Popeye', 'Fleischer', 'vintage animation', 'cartoon', 'Olive Oyl', 'spinach']
    elif 'superman' in title_lower or 'fleischer' in title_lower:
        return base_tags + ['Superman', 'Fleischer', 'vintage animation', 'superhero', 'DC', 'classic cartoon']
    elif 'looney tunes' in title_lower or 'bugs bunny' in title_lower:
        return base_tags + ['Looney Tunes', 'Warner Bros', 'Bugs Bunny', 'cartoon', 'classic animation']
    elif 'felix' in title_lower:
        return base_tags + ['Felix the Cat', 'silent film', 'vintage animation', '1920s', 'cartoon']
    elif 'soundie' in title_lower:
        return base_tags + ['Soundie', 'vintage music', '1940s', 'jazz', 'swing', 'jukebox', 'music video']
    elif 'wochenschau' in title_lower:
        return base_tags + ['Wochenschau', 'newsreel', 'history', 'WW2', 'documentary', 'German']
    elif 'alfred' in title_lower or 'kwak' in title_lower or 'quack' in title_lower:
        return base_tags + ['Alfred J Kwak', 'Alfred Jodokus Kwak', 'cartoon', 'anime', 'German dub', '1990s']
    elif 'christmas' in title_lower or 'xmas' in title_lower:
        return base_tags + ['Christmas', 'holiday', 'vintage', 'classic', 'Xmas']
    elif 'asterix' in title_lower:
        return base_tags + ['Asterix', 'comic', 'animation', 'French', 'Obelix']
    elif 'bravestarr' in title_lower:
        return base_tags + ['BraveStarr', 'Filmation', '1980s', 'cartoon', 'western', 'sci-fi']
    else:
        return base_tags + ['vintage', 'classic', 'film', 'movie']

def get_category_hashtags(title):
    """Get optimal hashtags based on video category."""
    title_lower = title.lower()
    
    base = '#8K #remAIke #PublicDomain'
    
    if 'betty boop' in title_lower:
        return f'{base} #BettyBoop #VintageAnimation #Fleischer'
    elif 'popeye' in title_lower:
        return f'{base} #Popeye #VintageAnimation #Fleischer'
    elif 'superman' in title_lower:
        return f'{base} #Superman #VintageAnimation #Fleischer'
    elif 'looney tunes' in title_lower:
        return f'{base} #LooneyTunes #VintageAnimation #WarnerBros'
    elif 'felix' in title_lower:
        return f'{base} #FelixTheCat #SilentFilm #VintageAnimation'
    elif 'soundie' in title_lower:
        return f'{base} #Soundie #VintageMusic #1940s #Jazz'
    elif 'wochenschau' in title_lower:
        return f'{base} #Wochenschau #History #WW2 #Newsreel'
    elif 'alfred' in title_lower or 'kwak' in title_lower:
        return f'{base} #AlfredJKwak #Cartoon #Anime #German'
    elif 'christmas' in title_lower:
        return f'{base} #Christmas #Holiday #VintageAnimation'
    elif 'asterix' in title_lower:
        return f'{base} #Asterix #Comic #Animation'
    elif 'bravestarr' in title_lower:
        return f'{base} #BraveStarr #Filmation #1980s #Cartoon'
    else:
        return f'{base} #VintageFilm #Classic'

def fix_description_hashtags(desc, title):
    """Remove excessive hashtags and add proper ones."""
    lines = desc.split('\n')
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Keep if not a hashtag line (or if it's a chapter timestamp like 0:00)
        if not stripped.startswith('#') or (len(stripped) > 1 and stripped[1].isdigit()):
            new_lines.append(line)
    
    # Clean up trailing empty lines
    while new_lines and not new_lines[-1].strip():
        new_lines.pop()
    
    # Add proper hashtags
    proper_hashtags = get_category_hashtags(title)
    new_desc = '\n'.join(new_lines)
    new_desc = f"{new_desc}\n\n{proper_hashtags}"
    
    return new_desc

def main():
    print("=" * 70)
    print("🔧 FIX REMAINING ISSUES + OPTIMIZE TAGS/HASHTAGS")
    print("=" * 70)
    
    # Load data
    data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))
    videos = [v for v in data['videos'] if v.get('status', {}).get('privacyStatus') == 'public']
    
    print(f"📊 {len(videos)} public videos")
    
    # Load credentials
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    fixes_applied = 0
    
    # PHASE 1: Fix critical videos
    print("\n" + "=" * 70)
    print("📌 PHASE 1: Fix critical videos")
    print("=" * 70)
    
    critical_fixes = [
        {
            'id': 'gx6eICiEYLo',
            'new_title': 'Alfred J. Kwak (1): Hurra, er ist da! | 8K HQ | @remAIke_IT',
            'reason': 'Alfred J. Kwak (1/52) - 91 chars, 8K HQ am Anfang'
        },
        {
            'id': 'CSLfwklQq9s',
            'fix_hashtags_only': True,
            'reason': 'Marihuana - 45 Hashtags → 5-6'
        }
    ]
    
    for fix in critical_fixes:
        try:
            response = youtube.videos().list(part='snippet', id=fix['id']).execute()
            if not response.get('items'):
                print(f"❌ Video nicht gefunden: {fix['id']}")
                continue
            
            snippet = response['items'][0]['snippet']
            
            if fix.get('new_title'):
                snippet['title'] = fix['new_title']
            
            if fix.get('fix_hashtags_only'):
                snippet['description'] = fix_description_hashtags(snippet['description'], snippet['title'])
            
            youtube.videos().update(part='snippet', body={'id': fix['id'], 'snippet': snippet}).execute()
            print(f"✅ {fix['reason']}")
            fixes_applied += 1
            
        except Exception as e:
            print(f"❌ Fehler bei {fix['id']}: {e}")
    
    # PHASE 2: Fix tags for videos with bad tags
    print("\n" + "=" * 70)
    print("📌 PHASE 2: Optimize tags (videos with <5 or >15 tags)")
    print("=" * 70)
    
    tag_fixes = 0
    for v in videos:
        video_id = v['id']
        snippet = v['snippet']
        title = snippet['title']
        tags = snippet.get('tags', [])
        
        # Only fix if tags are problematic
        if len(tags) >= 5 and len(tags) <= 15:
            continue
        
        try:
            # Get fresh data
            response = youtube.videos().list(part='snippet', id=video_id).execute()
            if not response.get('items'):
                continue
            
            snippet = response['items'][0]['snippet']
            optimal_tags = get_category_tags(title)
            
            # Only update if different
            if set(snippet.get('tags', [])) != set(optimal_tags):
                snippet['tags'] = optimal_tags
                youtube.videos().update(part='snippet', body={'id': video_id, 'snippet': snippet}).execute()
                tag_fixes += 1
                if tag_fixes <= 10:
                    print(f"✅ Tags: {title[:50]}...")
                elif tag_fixes == 11:
                    print("   ... (weitere werden nicht einzeln geloggt)")
            
        except Exception as e:
            if 'quotaExceeded' in str(e):
                print(f"⚠️ QUOTA EXCEEDED! Stopping...")
                break
    
    print(f"📊 Tags optimiert: {tag_fixes}")
    fixes_applied += tag_fixes
    
    # PHASE 3: Fix hashtags
    print("\n" + "=" * 70)
    print("📌 PHASE 3: Fix hashtags (videos with <3 or >8)")
    print("=" * 70)
    
    hashtag_fixes = 0
    for v in videos:
        video_id = v['id']
        snippet = v['snippet']
        title = snippet['title']
        desc = snippet.get('description', '')
        
        # Count hashtags
        hashtag_count = len(re.findall(r'#\w+', desc))
        
        # Only fix if problematic
        if hashtag_count >= 3 and hashtag_count <= 8:
            continue
        
        try:
            response = youtube.videos().list(part='snippet', id=video_id).execute()
            if not response.get('items'):
                continue
            
            snippet = response['items'][0]['snippet']
            new_desc = fix_description_hashtags(snippet['description'], title)
            
            if snippet['description'] != new_desc:
                snippet['description'] = new_desc
                youtube.videos().update(part='snippet', body={'id': video_id, 'snippet': snippet}).execute()
                hashtag_fixes += 1
                if hashtag_fixes <= 10:
                    print(f"✅ Hashtags: {title[:50]}...")
                elif hashtag_fixes == 11:
                    print("   ... (weitere werden nicht einzeln geloggt)")
            
        except Exception as e:
            if 'quotaExceeded' in str(e):
                print(f"⚠️ QUOTA EXCEEDED! Stopping...")
                break
    
    print(f"📊 Hashtags optimiert: {hashtag_fixes}")
    fixes_applied += hashtag_fixes
    
    print("\n" + "=" * 70)
    print("📊 ERGEBNIS")
    print("=" * 70)
    print(f"   ✅ Fixes angewendet: {fixes_applied}")
    print(f"   📊 API Units verbraucht: ~{fixes_applied * 50}")

if __name__ == '__main__':
    main()
