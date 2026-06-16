"""
Filter international (non-German) videos that need multilingual descriptions
"""
import json

with open('config/multilingual_check.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data['videos_needing_update']

# Filter: NICHT deutsche Inhalte
german_keywords = [
    'Wochenschau', 'Deutsch', 'German', 'Alfred Jodokus', 'Alfred J. Kwak',
    'BraveStarr', 'Astro Boy', 'Ferdy', 'Asterix'  # Diese sind deutsch synchronisiert
]

international_videos = []
german_videos = []

for v in videos:
    title = v['title']
    is_german = any(kw.lower() in title.lower() for kw in german_keywords)
    
    if is_german:
        german_videos.append(v)
    else:
        international_videos.append(v)

print(f"=== FILTER ERGEBNIS ===")
print(f"🌍 International (English): {len(international_videos)}")
print(f"🇩🇪 Deutsch-spezifisch: {len(german_videos)}")
print()

# Kategorisiere internationale Videos
categories = {
    'Betty Boop': [],
    'Soundie': [],
    'Popeye': [],
    'Superman': [],
    'Casper': [],
    'Felix the Cat': [],
    'Looney Tunes': [],
    'Porky Pig': [],
    'Christmas': [],
    'Silent Films': [],
    'Documentaries': [],
    'Other': []
}

for v in international_videos:
    title = v['title']
    categorized = False
    
    for cat in categories:
        if cat.lower() in title.lower():
            categories[cat].append(v)
            categorized = True
            break
    
    # Special checks
    if not categorized:
        if any(x in title for x in ['Skeleton Dance', 'Christmas', 'Santa', 'Rudolph', 'Suzy Snowflake']):
            categories['Christmas'].append(v)
            categorized = True
        elif any(x in title for x in ['Nosferatu', 'Frankenstein', 'Caligari', 'Metropolis', 'Phantom']):
            categories['Silent Films'].append(v)
            categorized = True
        elif any(x in title for x in ['Documentary', 'Newsreel', 'Atomic', 'Duck and Cover']):
            categories['Documentaries'].append(v)
            categorized = True
    
    if not categorized:
        categories['Other'].append(v)

print("=== INTERNATIONALE VIDEOS NACH KATEGORIE ===")
for cat, vids in categories.items():
    if vids:
        print(f"\n📁 {cat}: {len(vids)} Videos")
        for v in vids[:5]:
            print(f"   {v['id']} | {v['title'][:50]}")
        if len(vids) > 5:
            print(f"   ... und {len(vids) - 5} weitere")

# Save filtered list
result = {
    'total_international': len(international_videos),
    'total_german': len(german_videos),
    'categories': {k: v for k, v in categories.items() if v},
    'international_videos': international_videos
}

with open('config/international_videos.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n📁 Saved to config/international_videos.json")
