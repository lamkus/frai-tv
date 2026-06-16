"""
Fix Skylab video: Full metadata overhaul.
JSC-627 = NASA Johnson Space Center Film #627
"Skylab: The 2nd Manned Mission — A Scientific Harvest" (1974)
Skylab 3 / SL-3 mission, Jul 28 – Sep 25 1973, crew: Bean, Garriott, Lousma
Duration: 37:18 — NASA public domain documentary
"""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
VID = "sp1AzW-_rV0"

def get_yt():
    creds_data = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=creds_data.get("access_token"),
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data.get("scopes", ["https://www.googleapis.com/auth/youtube"])
    )
    if creds.expired:
        creds.refresh(Request())
        creds_data["access_token"] = creds.token
        json.dump(creds_data, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)

# ═══════════════════════════════════════════
# NEW METADATA
# ═══════════════════════════════════════════

NEW_TITLE = "Skylab 3: A Scientific Harvest (1974) | NASA | 8K HQ"
assert len(NEW_TITLE) <= 70, f"Title too long: {len(NEW_TITLE)}"

NEW_DESC = """Skylab 3: A Scientific Harvest — The complete NASA documentary about the second manned Skylab mission (SL-3), originally produced as JSC Film 627 by NASA's Johnson Space Center.

🚀 Mission: Skylab 3 (SL-3) — July 28 to September 25, 1973 (59 days)
👨‍🚀 Crew: Commander Alan Bean, Science Pilot Owen Garriott, Pilot Jack Lousma
🛰️ Achievements: 1,084 hours of experiments, 3 EVAs (13+ hours), Earth & solar observations

This documentary covers the crew's scientific work aboard America's first space station, including materials processing, Earth resources photography, solar astronomy, and medical experiments in microgravity.

Restored and enhanced to 8K resolution from NASA archival film.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Skylab #NASA #SpaceHistory #8K #PublicDomain"""

NEW_TAGS = [
    "Skylab", "Skylab 3", "NASA", "space station", "1973",
    "Alan Bean", "Owen Garriott", "Jack Lousma",
    "NASA documentary", "space exploration", "8K",
    "public domain", "JSC-627", "vintage NASA", "space history"
]
assert len(NEW_TAGS) <= 15, f"Too many tags: {len(NEW_TAGS)}"

# Category: 27 (Education) ← already correct for documentary
NEW_CATEGORY = "27"

# Localizations (5 languages)
LOCALIZATIONS = {
    "en": {
        "title": "Skylab 3: A Scientific Harvest (1974) | NASA | 8K HQ",
        "description": "The complete NASA documentary about the second manned Skylab mission (SL-3). Crew: Alan Bean, Owen Garriott, Jack Lousma. 59 days in space, 1,084 hours of experiments. Restored to 8K from NASA archival film.\n\n👆 LIKE if you found this valuable!\n💬 COMMENT your thoughts!\n🔔 SUBSCRIBE for more vintage content!\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#Skylab #NASA #SpaceHistory #8K #PublicDomain"
    },
    "de": {
        "title": "Skylab 3: Eine wissenschaftliche Ernte (1974) | NASA | 8K HQ",
        "description": "Die vollständige NASA-Dokumentation über die zweite bemannte Skylab-Mission (SL-3). Besatzung: Alan Bean, Owen Garriott, Jack Lousma. 59 Tage im All, 1.084 Stunden Experimente. In 8K restauriert aus NASA-Archivmaterial.\n\n👆 LIKE wenn dir das Video gefällt!\n💬 KOMMENTIERE deine Gedanken!\n🔔 ABONNIERE für mehr Vintage-Inhalte!\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#Skylab #NASA #Weltraumgeschichte #8K #PublicDomain"
    },
    "es": {
        "title": "Skylab 3: Una Cosecha Científica (1974) | NASA | 8K HQ",
        "description": "El documental completo de la NASA sobre la segunda misión tripulada del Skylab (SL-3). Tripulación: Alan Bean, Owen Garriott, Jack Lousma. 59 días en el espacio. Restaurado en 8K del archivo de la NASA.\n\n👆 ¡Dale LIKE si te gustó!\n💬 ¡COMENTA tus pensamientos!\n🔔 ¡SUSCRÍBETE para más contenido vintage!\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#Skylab #NASA #HistoriaEspacial #8K #PublicDomain"
    },
    "fr": {
        "title": "Skylab 3 : Une Récolte Scientifique (1974) | NASA | 8K HQ",
        "description": "Le documentaire complet de la NASA sur la deuxième mission habitée de Skylab (SL-3). Équipage : Alan Bean, Owen Garriott, Jack Lousma. 59 jours dans l'espace. Restauré en 8K à partir des archives de la NASA.\n\n👆 LIKE si vous avez apprécié !\n💬 COMMENTEZ vos impressions !\n🔔 ABONNEZ-VOUS pour plus de contenu vintage !\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#Skylab #NASA #HistoireSpatiale #8K #PublicDomain"
    },
    "pt": {
        "title": "Skylab 3: Uma Colheita Científica (1974) | NASA | 8K HQ",
        "description": "O documentário completo da NASA sobre a segunda missão tripulada do Skylab (SL-3). Tripulação: Alan Bean, Owen Garriott, Jack Lousma. 59 dias no espaço. Restaurado em 8K a partir do arquivo da NASA.\n\n👆 LIKE se gostou!\n💬 COMENTE suas impressões!\n🔔 INSCREVA-SE para mais conteúdo vintage!\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#Skylab #NASA #HistóriaEspacial #8K #PublicDomain"
    }
}

# Validate all loc titles
for lang, loc in LOCALIZATIONS.items():
    assert len(loc["title"]) <= 70, f"{lang} title too long: {len(loc['title'])}"

# ═══════════════════════════════════════════
# SHOW PLAN
# ═══════════════════════════════════════════
print("="*70)
print(f"  SKYLAB VIDEO FIX: {VID}")
print("="*70)
print(f"\n  OLD: jsc627 skylab the 2nd manned mission a scientific harvest wmv sls ARCHIVE BLURRED")
print(f"  NEW: {NEW_TITLE} [{len(NEW_TITLE)} chars]")
print(f"\n  Category: 27 (Education) ← stays")
print(f"  Tags: {len(NEW_TAGS)}")
print(f"  Localizations: {list(LOCALIZATIONS.keys())}")
print(f"  Description: {len(NEW_DESC)} chars")
print(f"  Hashtags: {[w for w in NEW_DESC.split() if w.startswith('#')]}")

DRY_RUN = "--apply" not in sys.argv
if DRY_RUN:
    print("\n  DRY RUN — pass --apply")
    sys.exit(0)

# ═══════════════════════════════════════════
# APPLY
# ═══════════════════════════════════════════
yt = get_yt()

# Fetch current to preserve structure
resp = yt.videos().list(part="snippet,status", id=VID).execute()
item = resp["items"][0]
snippet = item["snippet"]

# Update snippet
snippet["title"] = NEW_TITLE
snippet["description"] = NEW_DESC
snippet["tags"] = NEW_TAGS
snippet["categoryId"] = NEW_CATEGORY
snippet["defaultLanguage"] = "en"

# Update with localizations
try:
    result = yt.videos().update(
        part="snippet,localizations",
        body={
            "id": VID,
            "snippet": snippet,
            "localizations": LOCALIZATIONS
        }
    ).execute()
    print(f"\n  ✅ Updated: {result['snippet']['title']}")
    print(f"     Locs: {list(result.get('localizations',{}).keys())}")
    print(f"     Tags: {len(result['snippet'].get('tags',[]))}")
    print(f"     Cat:  {result['snippet']['categoryId']}")
    print(f"     Lang: {result['snippet'].get('defaultLanguage')}")
    print(f"\n  Quota: ~51 units (1 read + 50 write)")
except Exception as e:
    print(f"\n  ❌ FAILED: {e}")
