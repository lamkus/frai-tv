"""
Fix remaining diverged videos + add missing Soundies to playlist.
Phase A: i18n for 5 public videos (250 quota)
Phase B: Category fix for 2 private Wochenschau (100 quota)
Phase C: Add missing Soundies to playlist (variable)
"""
import os, sys, json, time, requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = r"D:\remaike.TV\token.json"
DRY_RUN = "--apply" not in sys.argv

# ── Phase A: 5 public videos needing i18n ──────────────────────────
I18N_FIXES = {
    'h6rDmu7FBzo': {  # Bettie Page Dancing
        'de': {'title': 'Bettie Page Dancing in 8K', 'description': 'Bettie Page tanzt in atemberaubendem 8K. Pin-Up-Ikone der 1950er Jahre. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'en': {'title': 'Bettie Page Dancing in 8K', 'description': 'Bettie Page dancing in stunning 8K. 1950s pin-up icon. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'es': {'title': 'Bettie Page Bailando en 8K', 'description': 'Bettie Page bailando en impresionante 8K. Icono pin-up de los años 1950. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'fr': {'title': 'Bettie Page Danse en 8K', 'description': 'Bettie Page danse en 8K. Icône pin-up des années 1950. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'ja': {'title': 'ベティ・ページ ダンス 8K', 'description': 'ベティ・ページのダンス映像を8Kで復元。1950年代のピンナップアイコン。パブリックドメイン。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
    },
    'ZJOXUwDX-mA': {  # Betty Boop: Minding the Baby
        'de': {'title': 'Betty Boop (6/105): Minding the Baby (1931) | 8K HQ', 'description': 'Betty Boop Folge 6: Minding the Baby (1931). Max Fleischer Studios. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'en': {'title': 'Betty Boop (6/105): Minding the Baby (1931) | 8K HQ', 'description': 'Betty Boop Episode 6: Minding the Baby (1931). Max Fleischer Studios. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'es': {'title': 'Betty Boop (6/105): Minding the Baby (1931) | 8K HQ', 'description': 'Betty Boop Episodio 6: Minding the Baby (1931). Max Fleischer Studios. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'fr': {'title': 'Betty Boop (6/105): Minding the Baby (1931) | 8K HQ', 'description': 'Betty Boop Épisode 6: Minding the Baby (1931). Max Fleischer Studios. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'ja': {'title': 'ベティ・ブープ (6/105): Minding the Baby (1931) | 8K HQ', 'description': 'ベティ・ブープ 第6話：Minding the Baby (1931)。マックス・フライシャー・スタジオ制作。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
    },
    'gVsamT781zU': {  # Teaserama Chris La Chris
        'de': {'title': 'Teaserama (1955): Chris La Chris | 8K HQ', 'description': 'Teaserama (1955) – Burlesque Short mit Chris La Chris. Vintage-Performance. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'en': {'title': 'Teaserama (1955): Chris La Chris | 8K HQ', 'description': 'Teaserama (1955) – Burlesque short featuring Chris La Chris. Vintage performance. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'es': {'title': 'Teaserama (1955): Chris La Chris | 8K HQ', 'description': 'Teaserama (1955) – Corto burlesque con Chris La Chris. Actuación vintage. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'fr': {'title': 'Teaserama (1955): Chris La Chris | 8K HQ', 'description': 'Teaserama (1955) – Court métrage burlesque avec Chris La Chris. Performance vintage. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'ja': {'title': 'ティーズラマ (1955): クリス・ラ・クリス | 8K HQ', 'description': 'ティーズラマ (1955) – クリス・ラ・クリス出演のバーレスク・ショート。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
    },
    'ZglrHGrG_oY': {  # Teaserama Trudy Wayne
        'de': {'title': 'Teaserama (1955): Trudy Wayne | 8K HQ', 'description': 'Teaserama (1955) – Burlesque Short mit Trudy Wayne. Vintage-Performance. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'en': {'title': 'Teaserama (1955): Trudy Wayne | 8K HQ', 'description': 'Teaserama (1955) – Burlesque short featuring Trudy Wayne. Vintage performance. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'es': {'title': 'Teaserama (1955): Trudy Wayne | 8K HQ', 'description': 'Teaserama (1955) – Corto burlesque con Trudy Wayne. Actuación vintage. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'fr': {'title': 'Teaserama (1955): Trudy Wayne | 8K HQ', 'description': 'Teaserama (1955) – Court métrage burlesque avec Trudy Wayne. Performance vintage. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'ja': {'title': 'ティーズラマ (1955): トゥルーディ・ウェイン | 8K HQ', 'description': 'ティーズラマ (1955) – トゥルーディ・ウェイン出演のバーレスク・ショート。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
    },
    '_9GLuLakxgw': {  # Burlesque Shorts
        'de': {'title': 'Burlesque 1955 in 8K | Vintage Performance', 'description': 'Burlesque-Performance aus dem Jahr 1955 in 8K. Vintage-Unterhaltung. Public Domain, restauriert.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'en': {'title': '1955 Burlesque in 8K | Vintage Performance', 'description': '1955 burlesque performance restored to 8K. Vintage entertainment. Public domain.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'es': {'title': 'Burlesque 1955 en 8K | Actuación Vintage', 'description': 'Actuación burlesque de 1955 restaurada en 8K. Entretenimiento vintage. Dominio público.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'fr': {'title': 'Burlesque 1955 en 8K | Performance Vintage', 'description': 'Performance burlesque de 1955 restaurée en 8K. Divertissement vintage. Domaine public.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        'ja': {'title': 'バーレスク 1955 8K | ヴィンテージ', 'description': '1955年のバーレスク・パフォーマンスを8Kで復元。パブリックドメイン。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
    },
}

# ── Phase B: 2 private Wochenschau wrong category ──────────────────
CATEGORY_FIXES = {
    'D_kLmNFlbZI': 27,  # Wochenschau 513 (was 25)
    '1O8sVLS-zfI': 27,  # Wochenschau 524 (was 25)
}

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def apply_i18n(youtube, vid_id, localizations):
    resp = youtube.videos().list(part="snippet,localizations", id=vid_id).execute()
    if not resp['items']:
        return False, "Not found"
    video = resp['items'][0]
    snippet = video['snippet']
    current_locs = video.get('localizations', {})
    merged = {**current_locs, **localizations}
    youtube.videos().update(
        part="snippet,localizations",
        body={
            'id': vid_id,
            'snippet': {
                'title': snippet['title'],
                'description': snippet['description'],
                'tags': snippet.get('tags', []),
                'categoryId': snippet['categoryId'],
            },
            'localizations': merged,
        }
    ).execute()
    return True, f"{len(localizations)} langs added"

def apply_category(youtube, vid_id, cat_id):
    resp = youtube.videos().list(part="snippet", id=vid_id).execute()
    if not resp['items']:
        return False, "Not found"
    snippet = resp['items'][0]['snippet']
    snippet['categoryId'] = str(cat_id)
    youtube.videos().update(
        part="snippet",
        body={'id': vid_id, 'snippet': {
            'title': snippet['title'],
            'description': snippet['description'],
            'tags': snippet.get('tags', []),
            'categoryId': str(cat_id),
        }}
    ).execute()
    return True, f"Category → {cat_id}"

def get_soundies_playlist_status(youtube):
    """Find Soundies playlist and check which videos are missing."""
    # List all playlists
    all_pl = []
    req = youtube.playlists().list(part="snippet", channelId="UCVFv6Egpl0LDvigpFbQXNeQ", maxResults=50)
    while req:
        resp = req.execute()
        all_pl.extend(resp['items'])
        req = youtube.playlists().list_next(req, resp)
    
    # Find main Soundies playlist (not the duplicate)
    soundies_pl = None
    dupe_pl = None
    for pl in all_pl:
        t = pl['snippet']['title'].lower()
        if 'soundie' in t:
            if soundies_pl is None or len(pl['snippet']['title']) > len(soundies_pl['snippet']['title']):
                if soundies_pl:
                    dupe_pl = soundies_pl
                soundies_pl = pl
            else:
                dupe_pl = pl
    
    if not soundies_pl:
        return None, None, []
    
    pl_id = soundies_pl['id']
    print(f"  Main playlist: {soundies_pl['snippet']['title']} ({pl_id})")
    if dupe_pl:
        print(f"  Duplicate: {dupe_pl['snippet']['title']} ({dupe_pl['id']}) ← DELETE IN STUDIO!")
    
    # Get all videos currently in playlist
    in_playlist = set()
    req = youtube.playlistItems().list(part="contentDetails", playlistId=pl_id, maxResults=50)
    while req:
        resp = req.execute()
        for item in resp['items']:
            in_playlist.add(item['contentDetails']['videoId'])
        req = youtube.playlistItems().list_next(req, resp)
    
    print(f"  Videos in playlist: {len(in_playlist)}")
    
    # Get ALL channel videos, find Soundies not in playlist
    all_vids = []
    req = youtube.playlistItems().list(part="contentDetails", playlistId="UUVFv6Egpl0LDvigpFbQXNeQ", maxResults=50)
    while req:
        resp = req.execute()
        all_vids.extend([item['contentDetails']['videoId'] for item in resp['items']])
        req = youtube.playlistItems().list_next(req, resp)
    
    # Check each video if it's a Soundie
    missing = []
    for i in range(0, len(all_vids), 50):
        batch = all_vids[i:i+50]
        resp = youtube.videos().list(part="snippet,status", id=','.join(batch), maxResults=50).execute()
        for v in resp['items']:
            if v['status']['privacyStatus'] != 'public':
                continue
            title = v['snippet']['title'].lower()
            tags = [t.lower() for t in v['snippet'].get('tags', [])]
            is_soundie = 'soundie' in title or 'soundie' in tags or 'soundies' in tags
            if is_soundie and v['id'] not in in_playlist:
                missing.append({'id': v['id'], 'title': v['snippet']['title']})
    
    return pl_id, in_playlist, missing

def main():
    mode = "DRY RUN" if DRY_RUN else "APPLYING"
    print(f"{'='*60}")
    print(f"  REMAINING FIXES — {mode}")
    print(f"{'='*60}\n")
    
    youtube = get_youtube()
    total_quota = 0
    
    # ── Phase A: i18n ──
    print(f"PHASE A: i18n for {len(I18N_FIXES)} public videos")
    print("-" * 40)
    fixed_a = 0
    for vid_id, locs in I18N_FIXES.items():
        if DRY_RUN:
            print(f"  [DRY] {vid_id}: +{len(locs)} languages")
            fixed_a += 1
        else:
            try:
                ok, msg = apply_i18n(youtube, vid_id, locs)
                print(f"  {'✅' if ok else '❌'} {vid_id}: {msg}")
                if ok: fixed_a += 1
                time.sleep(1.2)
            except Exception as e:
                print(f"  ❌ {vid_id}: {str(e)[:80]}")
    total_quota += fixed_a * 50
    print(f"  → {fixed_a}/{len(I18N_FIXES)} fixed ({fixed_a * 50} quota)\n")
    
    # ── Phase B: Category fixes ──
    print(f"PHASE B: Category fix for {len(CATEGORY_FIXES)} private Wochenschau")
    print("-" * 40)
    fixed_b = 0
    for vid_id, cat in CATEGORY_FIXES.items():
        if DRY_RUN:
            print(f"  [DRY] {vid_id}: Category → {cat}")
            fixed_b += 1
        else:
            try:
                ok, msg = apply_category(youtube, vid_id, cat)
                print(f"  {'✅' if ok else '❌'} {vid_id}: {msg}")
                if ok: fixed_b += 1
                time.sleep(1.2)
            except Exception as e:
                print(f"  ❌ {vid_id}: {str(e)[:80]}")
    total_quota += fixed_b * 50
    print(f"  → {fixed_b}/{len(CATEGORY_FIXES)} fixed ({fixed_b * 50} quota)\n")
    
    # ── Phase C: Soundies Playlist ──
    print("PHASE C: Soundies Playlist Check")
    print("-" * 40)
    pl_id, in_playlist, missing = get_soundies_playlist_status(youtube)
    if not pl_id:
        print("  ❌ No Soundies playlist found!")
    elif not missing:
        print("  ✅ All Soundies already in playlist!")
    else:
        print(f"  Missing from playlist: {len(missing)}")
        fixed_c = 0
        for m in missing:
            if DRY_RUN:
                print(f"    [DRY] Would add: {m['title'][:55]}")
                fixed_c += 1
            else:
                try:
                    youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            'snippet': {
                                'playlistId': pl_id,
                                'resourceId': {
                                    'kind': 'youtube#video',
                                    'videoId': m['id']
                                }
                            }
                        }
                    ).execute()
                    print(f"    ✅ Added: {m['title'][:55]}")
                    fixed_c += 1
                    time.sleep(1.2)
                except Exception as e:
                    print(f"    ❌ {m['id']}: {str(e)[:80]}")
        total_quota += fixed_c * 50
        print(f"  → {fixed_c}/{len(missing)} added ({fixed_c * 50} quota)")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL: ~{total_quota} quota used")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
