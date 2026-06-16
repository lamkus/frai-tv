#!/usr/bin/env python3
"""
Fix remaining 11 videos with SEO issues.
Excludes: Ken Block Short, Livestream (different rules)
"""

import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Paths
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
OAUTH_PATH = os.path.join(CONFIG_DIR, 'youtube_oauth.json')

# Videos to fix (excluding Ken Block Short and Livestream)
FIXES = [
    {
        "id": "CSLfwklQq9s",
        "old_title": "8K Marihuana | Cannabis | Ganja | 1936| 大麻 | Конопля | マリファナ",
        "new_title": "Marihuana (1936) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#PublicDomain #VintageFilm #8K #1930s #remAIke"
    },
    {
        "id": "GufKY_3dPDU",
        "old_title": "Teaserama (1955) Short: Icky Lynn | BLUR | 8K HQ (4K UHD) | @remAIke_IT",
        "new_title": "Teaserama: Icky Lynn (1955) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#PublicDomain #VintageFilm #8K #1950s #remAIke #Burlesque"
    },
    {
        "id": "_9GLuLakxgw",
        "old_title": "Teaserama (1955) Short: Cherry Knight | 8K HQ (4K UHD) | @remAIke_IT",
        "new_title": "Teaserama: Cherry Knight (1955) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#PublicDomain #VintageFilm #8K #1950s #remAIke #Burlesque"
    },
    {
        "id": "s_0yOzCKDa8",
        "old_title": "December 7th (1943) | Pearl Harbor | 8K HQ (4K UHD) | @remAIke_IT",
        "new_title": "December 7th: Pearl Harbor (1943) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#Documentary #PearlHarbor #8K #WW2 #remAIke #History"
    },
    {
        "id": "lNcvMYyLPVU",
        "old_title": "Astro Boy (1/52): Astro Boys Geburt | Deutsch | 8K HQ | Anime",
        "new_title": "Astro Boy (1): Astro Boys Geburt | 8K HQ | @remAIke_IT",
        "fix_hashtags": False
    },
    {
        "id": "dpF2uQVgCsM",
        "old_title": "The Fast and the Furious (1954) | 8K HQ | See the Film That Started It All!",
        "new_title": "The Fast and the Furious (1954) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#PublicDomain #VintageFilm #8K #1950s #remAIke #ActionMovie"
    },
    {
        "id": "dfUyhjEnAqw",
        "old_title": "The Frog (1908) | 8K HQ | @remAIke_IT",
        "new_title": "The Frog (1908) | Silent Film | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#SilentFilm #PublicDomain #8K #1900s #remAIke #VintageAnimation"
    },
    {
        "id": "Ukabxz6LK0c",
        "old_title": "Astro Boy (2/6): Astro gegen Atlas | Deutsch | 8K HQ (4K UHD)",
        "new_title": "Astro Boy (2): Astro gegen Atlas | 8K HQ | @remAIke_IT",
        "fix_hashtags": False
    },
    {
        "id": "ihaeGBIJMAE",
        "old_title": "The Old Man of the Mountain (1933) | Betty Boop | 8K HQ (4K UHD)",
        "new_title": "Betty Boop: Old Man of the Mountain (1933) | 8K HQ | @remAIke_IT",
        "fix_hashtags": True,
        "new_hashtags": "#BettyBoop #VintageAnimation #8K #1930s #remAIke #Fleischer"
    }
]

def load_credentials():
    """Load OAuth credentials."""
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
        print("🔄 Token refreshed")
    
    return creds

def apply_fix(youtube, fix, index, total):
    """Apply a single fix."""
    video_id = fix['id']
    
    try:
        # Get current video data
        response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            print(f"[{index}/{total}] ❌ Video nicht gefunden: {video_id}")
            return False
        
        video = response['items'][0]
        snippet = video['snippet']
        current_title = snippet['title']
        
        # Update title
        snippet['title'] = fix['new_title']
        
        # Update hashtags in description if needed
        if fix.get('fix_hashtags') and fix.get('new_hashtags'):
            desc = snippet.get('description', '')
            
            # Remove old hashtags (lines starting with #)
            lines = desc.split('\n')
            new_lines = []
            for line in lines:
                # Keep line if it doesn't start with # (unless it's a chapter timestamp)
                stripped = line.strip()
                if not stripped.startswith('#') or stripped[1:2].isdigit():
                    new_lines.append(line)
            
            # Add new hashtags at the end
            desc = '\n'.join(new_lines).rstrip()
            desc = f"{desc}\n\n{fix['new_hashtags']}"
            snippet['description'] = desc
        
        # Apply update
        youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        print(f"[{index}/{total}] ✅ {fix['new_title'][:50]}...")
        return True
        
    except Exception as e:
        print(f"[{index}/{total}] ❌ Fehler: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 FIX REMAINING 9 VIDEOS")
    print("=" * 70)
    print(f"📊 Videos to fix: {len(FIXES)}")
    print(f"📊 Estimated API Cost: {len(FIXES) * 50} Units")
    print()
    
    # Load credentials
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    success = 0
    failed = 0
    
    for i, fix in enumerate(FIXES, 1):
        if apply_fix(youtube, fix, i, len(FIXES)):
            success += 1
        else:
            failed += 1
    
    print()
    print("=" * 70)
    print("📊 ERGEBNIS")
    print("=" * 70)
    print(f"   ✅ Erfolgreich: {success}")
    print(f"   ❌ Fehlgeschlagen: {failed}")
    print(f"   📊 API Units verbraucht: ~{success * 50}")

if __name__ == '__main__':
    main()
