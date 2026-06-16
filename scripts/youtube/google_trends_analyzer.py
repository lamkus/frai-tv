#!/usr/bin/env python3
"""
GOOGLE TRENDS ANALYZER für remAIke.TV
=====================================
Analysiert Suchtrends für bessere Video-SEO.

Liefert:
- Interest over Time für Keywords
- Related Queries (was Leute sonst suchen)
- Regional Interest (DE, AT, CH)
- Rising Topics (was gerade trending ist)
"""

from pytrends.request import TrendReq
import json
from datetime import datetime
import time

CONFIG_DIR = 'd:/remaike.TV/config'

# Keywords die für unseren Channel relevant sind
REMAIKE_KEYWORDS = {
    'series': [
        'Betty Boop',
        'Alfred J Kwak',
        'Superman cartoon',
        'Casper cartoon',
        'Popeye cartoon',
        'Felix the Cat',
    ],
    'themes': [
        'classic cartoons',
        'vintage animation',
        'public domain movies',
        '8K restored',
        'old cartoons',
        'retro cartoons',
    ],
    'german': [
        'Zeichentrickfilme klassiker',
        'alte Zeichentrickserien',
        'Alfred Jodokus Kwak',
        'Zeichentrick 80er',
    ],
}


def analyze_trends(keywords: list, geo: str = 'DE', timeframe: str = 'today 12-m') -> dict:
    """
    Analysiere Google Trends für Keywords.
    
    Args:
        keywords: Max 5 Keywords pro Request
        geo: Ländercode (DE, AT, CH, US, '')
        timeframe: 'today 12-m', 'today 3-m', 'now 7-d'
    """
    pytrends = TrendReq(hl='de-DE', tz=60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'geo': geo,
        'timeframe': timeframe,
        'keywords': {},
    }
    
    # Google Trends erlaubt max 5 Keywords pro Request
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        
        try:
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo=geo)
            
            # Interest over Time
            interest = pytrends.interest_over_time()
            if not interest.empty:
                for kw in batch:
                    if kw in interest.columns:
                        avg_interest = interest[kw].mean()
                        max_interest = interest[kw].max()
                        latest = interest[kw].iloc[-1] if len(interest) > 0 else 0
                        
                        results['keywords'][kw] = {
                            'average_interest': round(avg_interest, 1),
                            'max_interest': int(max_interest),
                            'latest_interest': int(latest),
                            'trend': 'rising' if latest > avg_interest else 'declining',
                        }
            
            # Related Queries
            related = pytrends.related_queries()
            for kw in batch:
                if kw in related and related[kw]['rising'] is not None:
                    rising = related[kw]['rising'].head(5).to_dict('records')
                    results['keywords'].setdefault(kw, {})['related_rising'] = [
                        r['query'] for r in rising
                    ]
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            for kw in batch:
                results['keywords'][kw] = {'error': str(e)}
    
    return results


def get_trending_searches(geo: str = 'DE') -> list:
    """Hole aktuell trending Searches."""
    pytrends = TrendReq(hl='de-DE', tz=60)
    
    try:
        trending = pytrends.trending_searches(pn='germany' if geo == 'DE' else 'united_states')
        return trending[0].tolist()[:20]
    except Exception as e:
        return [f'Error: {e}']


def run_full_trends_analysis():
    """Vollständige Trends-Analyse für remAIke.TV."""
    
    print('╔═══════════════════════════════════════════════════════════════╗')
    print('║  📈 GOOGLE TRENDS ANALYZER für remAIke.TV                     ║')
    print('╚═══════════════════════════════════════════════════════════════╝')
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'series_trends': {},
        'theme_trends': {},
        'german_trends': {},
        'trending_now': [],
        'recommendations': [],
    }
    
    # Series Keywords (Betty Boop, Alfred, etc.)
    print('\n📊 Analysiere Serien-Keywords...')
    series_data = analyze_trends(REMAIKE_KEYWORDS['series'], geo='DE')
    results['series_trends'] = series_data
    
    for kw, data in series_data.get('keywords', {}).items():
        if 'error' not in data:
            trend_icon = '📈' if data.get('trend') == 'rising' else '📉'
            print(f"   {trend_icon} {kw}: {data.get('average_interest', 0)}/100 avg")
    
    # Theme Keywords
    print('\n🎯 Analysiere Themen-Keywords...')
    theme_data = analyze_trends(REMAIKE_KEYWORDS['themes'], geo='')  # Global
    results['theme_trends'] = theme_data
    
    for kw, data in theme_data.get('keywords', {}).items():
        if 'error' not in data:
            trend_icon = '📈' if data.get('trend') == 'rising' else '📉'
            print(f"   {trend_icon} {kw}: {data.get('average_interest', 0)}/100 avg")
    
    # German Keywords
    print('\n🇩🇪 Analysiere deutsche Keywords...')
    german_data = analyze_trends(REMAIKE_KEYWORDS['german'], geo='DE')
    results['german_trends'] = german_data
    
    for kw, data in german_data.get('keywords', {}).items():
        if 'error' not in data:
            trend_icon = '📈' if data.get('trend') == 'rising' else '📉'
            print(f"   {trend_icon} {kw}: {data.get('average_interest', 0)}/100 avg")
    
    # Trending Now
    print('\n🔥 Aktuell trending in Deutschland...')
    trending = get_trending_searches('DE')
    results['trending_now'] = trending[:10]
    for t in trending[:5]:
        print(f"   • {t}")
    
    # Generate Recommendations
    print('\n💡 Generiere SEO-Empfehlungen...')
    
    # Find best performing keywords
    all_keywords = {}
    for category in [series_data, theme_data, german_data]:
        for kw, data in category.get('keywords', {}).items():
            if 'error' not in data:
                all_keywords[kw] = data.get('average_interest', 0)
    
    # Sort by interest
    sorted_kw = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)
    
    recommendations = []
    
    # Top keywords to use in titles/tags
    top_keywords = [kw for kw, score in sorted_kw[:5] if score > 10]
    if top_keywords:
        recommendations.append({
            'type': 'tags',
            'action': 'Diese Keywords in Titel/Tags priorisieren',
            'keywords': top_keywords,
        })
    
    # Rising keywords
    rising_keywords = [
        kw for kw, data in all_keywords.items() 
        if isinstance(results.get('series_trends', {}).get('keywords', {}).get(kw), dict)
        and results['series_trends']['keywords'].get(kw, {}).get('trend') == 'rising'
    ]
    if rising_keywords:
        recommendations.append({
            'type': 'opportunity',
            'action': 'Diese Keywords sind im Aufwärtstrend',
            'keywords': rising_keywords,
        })
    
    results['recommendations'] = recommendations
    
    for rec in recommendations:
        print(f"\n   📌 {rec['action']}:")
        for kw in rec.get('keywords', [])[:5]:
            print(f"      • {kw}")
    
    # Save
    output_path = f'{CONFIG_DIR}/google_trends_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f'\n📄 Gespeichert: {output_path}')
    
    return results


if __name__ == '__main__':
    run_full_trends_analysis()
