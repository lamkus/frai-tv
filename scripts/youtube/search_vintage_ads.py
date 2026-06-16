"""Search Archive.org for era-matched vintage commercials for WochenschauKino."""
import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output')

queries = [
    # War Bonds / Victory - perfekt zur Wochenschau-Aera
    ('War Bonds Commercials',
     'title:(war bond) AND mediatype:movies AND date:[1940 TO 1950]'),
    # Victory Gardens, Home Front
    ('Victory / Home Front',
     '(victory garden OR home front OR ration) AND mediatype:movies AND date:[1940 TO 1950]'),
    # 1940s Cinema Ads
    ('1940s Cinema Adverts',
     '(cinema advert OR theater ad OR newsreel ad) AND mediatype:movies AND date:[1935 TO 1955]'),
    # Coca-Cola vintage
    ('Coca-Cola 1940s',
     'title:(coca cola) AND mediatype:movies AND date:[1935 TO 1960]'),
    # Wartime propaganda shorts (Buy Bonds, Save Rubber etc)
    ('Wartime Propaganda Shorts',
     'subject:(propaganda OR war effort) AND mediatype:movies AND date:[1940 TO 1946] AND -collection:feature_films'),
    # Cigarette ads (die Grossen)
    ('Cigarette Ads 40s',
     '(chesterfield OR old gold OR philip morris) AND commercial AND mediatype:movies'),
    # General 1940s commercials
    ('General 1940s Ads',
     'subject:commercials AND mediatype:movies AND date:[1938 TO 1952]'),
    # Movie theater intermission / drive-in ads
    ('Drive-In / Theater Ads',
     '(drive-in OR intermission OR snack bar OR refreshment) AND (ad OR commercial OR trailer) AND mediatype:movies AND date:[1940 TO 1965]'),
    # Household products 1940s (Soap, Detergent etc)
    ('Household Products 1940s',
     '(soap OR detergent OR washing OR household) AND (commercial OR advertisement) AND mediatype:movies AND date:[1940 TO 1960]'),
    # German / European wartime
    ('German/European Wartime',
     '(german OR deutsche OR werbung OR reklame) AND (commercial OR advertisement OR werbung) AND mediatype:movies AND date:[1930 TO 1960]'),
]

results = {}
for name, q in queries:
    try:
        r = requests.get('https://archive.org/advancedsearch.php', params={
            'q': q, 'output': 'json', 'rows': 25,
            'fl[]': 'identifier,title,date,downloads,description,year',
            'sort[]': 'downloads desc'
        }, timeout=20)
        data = r.json()
        total = data.get('response', {}).get('numFound', 0)
        docs = data.get('response', {}).get('docs', [])
        results[name] = {'total': total, 'top': docs[:15]}
        print(f"\n=== {name} === ({total} results)")
        for d in docs[:15]:
            dl = d.get('downloads', '?')
            yr = d.get('year', d.get('date', '?'))
            ident = d.get('identifier', '?')
            title = d.get('title', '?')[:75]
            print(f"  [{dl:>8}] {yr} | {ident[:50]:50s} | {title}")
    except Exception as e:
        print(f"ERROR {name}: {e}")

# Save
os.makedirs(OUTPUT_DIR, exist_ok=True)
outpath = os.path.join(OUTPUT_DIR, 'vintage_ad_search_results.json')
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {outpath}")
print(f"\nTotal unique queries: {len(queries)}")
total_found = sum(r['total'] for r in results.values())
print(f"Total results across all queries: {total_found}")
