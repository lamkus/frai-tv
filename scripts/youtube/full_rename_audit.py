#!/usr/bin/env python3
"""
Full Channel Rename Audit - Scannt alle Public Videos und schlägt SEO-konforme Titel vor.

Regeln:
- Format: [KEYWORD]: [Titel] ([Jahr]) | 8K HQ | @remAIke_IT
- Max 70 Zeichen (ideal 50-70)
- Keyword am ANFANG
- Bei Alfred: Kwak UND Quack
- 8K HQ konsistent
- @remAIke_IT Branding
"""

import os
import json
import re
import requests
from datetime import datetime

API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOADS_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Kategorie-Keywords für Titel-Anfang
CATEGORY_KEYWORDS = {
    'betty boop': 'Betty Boop',
    'popeye': 'Popeye',
    'superman': 'Superman',
    'looney tunes': 'Looney Tunes',
    'felix': 'Felix the Cat',
    'soundie': 'Soundie',
    'alfred': 'Alfred J. Kwak',
    'kwak': 'Alfred J. Kwak',
    'quack': 'Alfred J. Kwak',
    'bravestarr': 'BraveStarr',
    'brave starr': 'BraveStarr',
    'astro boy': 'Astro Boy',
    'wochenschau': 'Wochenschau',
    'newsreel': 'Newsreel',
    'christmas': 'Christmas Classic',
    'charlie chaplin': 'Charlie Chaplin',
    'chaplin': 'Charlie Chaplin',
    'buster keaton': 'Buster Keaton',
    'laurel': 'Laurel & Hardy',
    'hardy': 'Laurel & Hardy',
    'three stooges': 'Three Stooges',
    'documentary': 'Documentary',
    'dokumentation': 'Dokumentation',
    'kirby': 'Kirby',
    'maulwurf': 'Der kleine Maulwurf',
    'krtek': 'Der kleine Maulwurf',
    'asterix': 'Asterix',
    'cricket': 'Cricket on the Hearth',
}

def get_all_public_videos():
    """Holt alle Public Videos via Public API"""
    videos = []
    next_page = None
    
    while True:
        url = 'https://youtube.googleapis.com/youtube/v3/playlistItems'
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': UPLOADS_PLAYLIST,
            'maxResults': 50,
            'key': API_KEY
        }
        if next_page:
            params['pageToken'] = next_page
            
        response = requests.get(url, params=params)
        data = response.json()
        
        for item in data.get('items', []):
            vid_id = item['contentDetails']['videoId']
            snippet = item['snippet']
            videos.append({
                'id': vid_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'published': snippet['publishedAt'][:10]
            })
        
        next_page = data.get('nextPageToken')
        if not next_page:
            break
    
    return videos

def detect_category(title, description):
    """Erkennt Kategorie aus Titel/Description"""
    text = (title + ' ' + description).lower()
    
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in text:
            return category
    
    return None

def extract_year(title, description):
    """Extrahiert Jahr aus Titel oder Description"""
    # Suche Jahr in Klammern im Titel
    match = re.search(r'\((\d{4})\)', title)
    if match:
        return match.group(1)
    
    # Suche Jahr im Titel ohne Klammern
    match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', title)
    if match:
        return match.group(1)
    
    # Suche in Description
    match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', description[:500])
    if match:
        return match.group(1)
    
    return None

def clean_title_content(title):
    """Extrahiert den Kern-Titel ohne Formatierung"""
    # Entferne existierende Formatierung
    title = re.sub(r'\s*\|\s*8K\s*(HQ)?\s*', ' ', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*\|\s*@remAIke_IT\s*', ' ', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*@remAIke_IT\s*', ' ', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*8K\s*(HQ)?\s*', ' ', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*HQ\s*', ' ', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*#\w+\s*', ' ', title)  # Hashtags entfernen
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def generate_seo_title(video):
    """Generiert SEO-konformen Titel"""
    title = video['title']
    desc = video['description']
    
    # Prüfe ob bereits perfekt formatiert
    if re.match(r'^[A-Z].*\|.*8K HQ.*\|.*@remAIke_IT$', title):
        return None  # Bereits OK
    
    category = detect_category(title, desc)
    year = extract_year(title, desc)
    clean = clean_title_content(title)
    
    # Entferne Jahr aus clean title wenn vorhanden
    if year:
        clean = re.sub(rf'\s*\(?{year}\)?', '', clean).strip()
    
    # Entferne Kategorie-Prefix wenn bereits vorhanden
    if category:
        for keyword in CATEGORY_KEYWORDS:
            pattern = rf'^{re.escape(keyword)}[:\s-]*'
            clean = re.sub(pattern, '', clean, flags=re.IGNORECASE).strip()
    
    # Baue neuen Titel
    if category:
        if year:
            new_title = f"{category}: {clean} ({year}) | 8K HQ | @remAIke_IT"
        else:
            new_title = f"{category}: {clean} | 8K HQ | @remAIke_IT"
    else:
        if year:
            new_title = f"{clean} ({year}) | 8K HQ | @remAIke_IT"
        else:
            new_title = f"{clean} | 8K HQ | @remAIke_IT"
    
    # Kürze wenn zu lang (max 100 für YouTube, ideal 70)
    if len(new_title) > 90:
        # Kürze den clean Teil
        max_clean = 90 - len(f"{category}: " if category else "") - len(f" ({year})" if year else "") - len(" | 8K HQ | @remAIke_IT")
        clean = clean[:max_clean].strip()
        if category:
            if year:
                new_title = f"{category}: {clean} ({year}) | 8K HQ | @remAIke_IT"
            else:
                new_title = f"{category}: {clean} | 8K HQ | @remAIke_IT"
        else:
            if year:
                new_title = f"{clean} ({year}) | 8K HQ | @remAIke_IT"
            else:
                new_title = f"{clean} | 8K HQ | @remAIke_IT"
    
    # Nur zurückgeben wenn wirklich anders
    if new_title.lower() == title.lower():
        return None
    
    return new_title

def analyze_title_issues(video):
    """Analysiert Probleme im aktuellen Titel"""
    title = video['title']
    issues = []
    
    # Check: Hat 8K?
    if '8K' not in title.upper():
        issues.append('❌ Kein 8K')
    elif '8K HQ' not in title:
        issues.append('⚠️ 8K ohne HQ')
    
    # Check: Hat Branding?
    if '@remAIke_IT' not in title:
        issues.append('❌ Kein @remAIke_IT')
    
    # Check: Länge
    if len(title) > 100:
        issues.append(f'❌ Zu lang ({len(title)} chars)')
    elif len(title) > 80:
        issues.append(f'⚠️ Lang ({len(title)} chars)')
    
    # Check: Hashtags im Titel
    if '#' in title:
        issues.append('❌ Hashtag im Titel')
    
    # Check: Jahr vorhanden
    if not re.search(r'\(\d{4}\)', title):
        issues.append('⚠️ Kein Jahr in Klammern')
    
    # Check: Konsistente Formatierung
    if '|' not in title:
        issues.append('⚠️ Keine | Trenner')
    
    return issues

def main():
    print("🔍 FULL CHANNEL RENAME AUDIT")
    print("=" * 60)
    print(f"Scan-Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    print("📥 Lade alle Public Videos (Public API)...")
    videos = get_all_public_videos()
    print(f"✅ {len(videos)} Videos gefunden")
    print()
    
    # Analysiere alle Videos
    needs_rename = []
    perfect = []
    
    for video in videos:
        issues = analyze_title_issues(video)
        new_title = generate_seo_title(video)
        
        if issues or new_title:
            needs_rename.append({
                'id': video['id'],
                'current': video['title'],
                'suggested': new_title,
                'issues': issues,
                'year': extract_year(video['title'], video['description']),
                'category': detect_category(video['title'], video['description'])
            })
        else:
            perfect.append(video)
    
    # Sortiere nach Kategorie
    needs_rename.sort(key=lambda x: (x['category'] or 'ZZZ', x['current']))
    
    # Report
    print("=" * 60)
    print(f"📊 ERGEBNIS")
    print("=" * 60)
    print(f"✅ Perfekt formatiert: {len(perfect)}")
    print(f"🔧 Brauchen Umbenennung: {len(needs_rename)}")
    print()
    
    # Gruppiere nach Kategorie
    by_category = {}
    for item in needs_rename:
        cat = item['category'] or 'Uncategorized'
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    print("📂 NACH KATEGORIE:")
    for cat, items in sorted(by_category.items()):
        print(f"  {cat}: {len(items)} Videos")
    print()
    
    # Detail-Report
    print("=" * 60)
    print("🔧 UMBENENNUNGS-VORSCHLÄGE")
    print("=" * 60)
    
    rename_plan = []
    
    for cat, items in sorted(by_category.items()):
        print(f"\n### {cat} ({len(items)} Videos)")
        print("-" * 50)
        
        for item in items[:10]:  # Max 10 pro Kategorie anzeigen
            print(f"\n📺 {item['id']}")
            print(f"   AKTUELL:  {item['current']}")
            if item['suggested']:
                print(f"   NEU:      {item['suggested']}")
                rename_plan.append({
                    'id': item['id'],
                    'current': item['current'],
                    'new': item['suggested'],
                    'category': item['category']
                })
            if item['issues']:
                print(f"   ISSUES:   {', '.join(item['issues'])}")
        
        if len(items) > 10:
            print(f"\n   ... und {len(items) - 10} weitere")
    
    # Speichere Rename-Plan
    output = {
        'scan_date': datetime.now().isoformat(),
        'total_videos': len(videos),
        'perfect': len(perfect),
        'needs_rename': len(needs_rename),
        'rename_plan': rename_plan,
        'by_category': {k: len(v) for k, v in by_category.items()}
    }
    
    with open('config/rename_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n💾 Gespeichert: config/rename_audit_result.json")
    print(f"📋 {len(rename_plan)} Videos im Rename-Plan")
    
    return output

if __name__ == '__main__':
    main()
