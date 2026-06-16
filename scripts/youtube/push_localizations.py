#!/usr/bin/env python3
"""
Multilingual Localization Push for remAIke_IT
==============================================
- Fixes wrong defaultLanguage (Soundies de→en, vi→en, ko→en)
- Adds localizations in EN, DE, ES, FR, PT for all public videos
- Single API call per video (50 quota) — fixes + localizations combined
- Dry-run by default, --apply to execute
- Auto-stops on quota error
- Resume support (skips videos that already have ≥4 localizations)

Usage:
  python push_localizations.py              # Dry-run
  python push_localizations.py --apply      # Live push
  python push_localizations.py --limit 5    # Only process 5 videos
"""

import json, os, sys, time
from datetime import datetime
from collections import Counter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ============================================================
# CONFIG
# ============================================================
APPLY = '--apply' in sys.argv
LIMIT = None
for i, arg in enumerate(sys.argv):
    if arg == '--limit' and i + 1 < len(sys.argv):
        LIMIT = int(sys.argv[i + 1])

TARGET_LANGUAGES = ['en', 'de', 'es', 'fr', 'pt']
OAUTH_FILE = 'config/youtube_oauth.json'
SNAPSHOT_FILE = 'config/channel_snapshot_2026_02_06.json'
TIMESTAMP = datetime.now().strftime("%Y_%m_%d_%H%M")
OUTPUT_FILE = f'config/localization_push_{TIMESTAMP}.json'

quota_used = 0
MAX_QUOTA = 7500  # safety headroom

# ============================================================
# CATEGORY DETECTION
# ============================================================
def detect_category(title):
    """Classify video by title into content category."""
    t = title.lower()
    if 'betty boop' in t: return 'betty_boop'
    if 'soundie' in t: return 'soundie'
    if 'wochenschau' in t: return 'wochenschau'
    if 'alfred' in t and 'kwak' in t: return 'alfred'
    if 'superman' in t and ('/17)' in title or 'fleischer' in t): return 'superman'
    if 'popeye' in t: return 'popeye'
    if 'felix' in t and ('cat' in t or '/175)' in title): return 'felix'
    if 'casper' in t: return 'casper'
    if 'maulwurf' in t: return 'maulwurf'
    if 'ken block' in t or 'gymkhana' in t or 'getaway in stockholm' in t: return 'ken_block'
    if any(x in t for x in ['looney', 'porky', 'merrie', 'bosko']): return 'looney_tunes'
    if any(x in t for x in ['christmas', 'santa', 'snowflake', 'rudolph', 'coca-cola', 'coca‑cola']): return 'christmas'
    if 'astro boy' in t: return 'astro_boy'
    if 'bravestarr' in t: return 'bravestarr'
    if 'asterix' in t: return 'asterix'
    return 'other'

def correct_default_language(current_lang, category, title):
    """Determine correct defaultLanguage. Returns new lang or None if no change."""
    # Always wrong: Vietnamese, Korean
    if current_lang in ('vi', 'ko'):
        return 'en'
    # Soundies are English music videos
    if category == 'soundie' and current_lang != 'en':
        return 'en'
    # Keep everything else as-is (descriptions match current lang)
    return None

# ============================================================
# LOCALIZED DESCRIPTION TEMPLATES
# ============================================================

# CTA blocks per language
CTA = {
    'en': """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts below!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
    'de': """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE wenn es dir gefallen hat!
💬 KOMMENTIERE deine Meinung!
🔔 ABONNIERE für mehr Vintage-Content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
    'es': """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 ¡Dale LIKE si te gustó!
💬 ¡COMENTA tu opinión!
🔔 ¡SUSCRÍBETE para más contenido vintage en 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
    'fr': """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE si vous avez aimé !
💬 COMMENTEZ vos impressions !
🔔 ABONNEZ-VOUS pour plus de contenu vintage en 8K !
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
    'pt': """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 Dê LIKE se gostou!
💬 COMENTE sua opinião!
🔔 INSCREVA-SE para mais conteúdo vintage em 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
}

LINKS_BLOCK = """🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

# Category intros per language
# {cat: {lang: "intro text"}}
CATEGORY_INTROS = {
    'betty_boop': {
        'en': "🎬 Classic Betty Boop cartoon by Fleischer Studios, remastered in stunning 8K quality. This public domain animation gem has been AI-upscaled to bring the 1930s to life like never before.",
        'de': "🎬 Klassischer Betty Boop Cartoon von Fleischer Studios, remastered in atemberaubender 8K-Qualität. Dieses Public-Domain-Animationsjuwel wurde mit KI-Upscaling zum Leben erweckt.",
        'es': "🎬 Clásico dibujo animado de Betty Boop de Fleischer Studios, remasterizado en impresionante calidad 8K. Esta joya de animación de dominio público fue mejorada con IA.",
        'fr': "🎬 Classique dessin animé Betty Boop des studios Fleischer, remasterisé en qualité 8K époustouflante. Ce joyau d'animation du domaine public a été amélioré par IA.",
        'pt': "🎬 Clássico desenho animado da Betty Boop dos estúdios Fleischer, remasterizado em impressionante qualidade 8K. Esta joia da animação de domínio público foi aprimorada por IA.",
    },
    'soundie': {
        'en': "🎵 Vintage Soundie music video from the 1940s, remastered in 8K. Soundies were short musical films played on coin-operated visual jukeboxes — the original music videos!",
        'de': "🎵 Vintage Soundie-Musikvideo aus den 1940er Jahren, remastered in 8K. Soundies waren kurze Musikfilme, die auf münzbetriebenen Video-Jukeboxen liefen — die ersten Musikvideos!",
        'es': "🎵 Video musical Soundie vintage de los años 1940, remasterizado en 8K. Los Soundies eran cortometrajes musicales reproducidos en rocolas visuales — ¡los videos musicales originales!",
        'fr': "🎵 Soundie vintage des années 1940, remasterisé en 8K. Les Soundies étaient de courts films musicaux diffusés sur des juke-box visuels — les tout premiers clips musicaux !",
        'pt': "🎵 Vídeo musical Soundie vintage dos anos 1940, remasterizado em 8K. Soundies eram curtas-metragens musicais reproduzidos em jukeboxes visuais — os primeiros videoclipes!",
    },
    'wochenschau': {
        'en': "📰 German WWII Newsreel (Wochenschau), preserved and remastered in 8K for historical education. This primary source document serves exclusively as a historical record.\n\n⚠️ HISTORICAL DOCUMENT: This footage was originally produced as wartime propaganda. It is presented here solely for educational and documentary purposes. The views expressed do not reflect the opinions of the uploader.",
        'de': "📰 Deutsche Wochenschau aus dem Zweiten Weltkrieg, bewahrt und remastered in 8K für die historische Bildung. Dieses Primärquellendokument dient ausschließlich als historische Aufzeichnung.\n\n⚠️ HISTORISCHES DOKUMENT: Dieses Material wurde ursprünglich als Kriegspropaganda produziert. Es wird hier ausschließlich zu Bildungs- und Dokumentationszwecken präsentiert. Die dargestellten Ansichten spiegeln nicht die Meinung des Uploaders wider.",
        'es': "📰 Noticiario alemán de la Segunda Guerra Mundial (Wochenschau), preservado y remasterizado en 8K con fines educativos históricos.\n\n⚠️ DOCUMENTO HISTÓRICO: Este material fue producido originalmente como propaganda bélica. Se presenta aquí exclusivamente con fines educativos y documentales.",
        'fr': "📰 Actualités allemandes de la Seconde Guerre mondiale (Wochenschau), préservées et remasterisées en 8K à des fins éducatives.\n\n⚠️ DOCUMENT HISTORIQUE : Ces images ont été produites à l'origine comme propagande de guerre. Elles sont présentées ici exclusivement à des fins éducatives et documentaires.",
        'pt': "📰 Noticiário alemão da Segunda Guerra Mundial (Wochenschau), preservado e remasterizado em 8K para educação histórica.\n\n⚠️ DOCUMENTO HISTÓRICO: Este material foi originalmente produzido como propaganda de guerra. É apresentado aqui exclusivamente para fins educacionais e documentais.",
    },
    'alfred': {
        'en': "🦆 Alfred J. Kwak (Alfred Jodocus Kwak) — beloved Dutch-Japanese animated series, remastered in 8K. Follow the adventures of Alfred the duck in a world that mirrors real historical events.",
        'de': "🦆 Alfred J. Kwak (Alfred Jodocus Kwak) — die beliebte niederländisch-japanische Zeichentrickserie, remastered in 8K. Erlebe die Abenteuer von Ente Alfred in einer Welt, die reale historische Ereignisse widerspiegelt.",
        'es': "🦆 Alfred J. Kwak — querida serie animada holandesa-japonesa, remasterizada en 8K. Sigue las aventuras del pato Alfred en un mundo que refleja eventos históricos reales.",
        'fr': "🦆 Alfred J. Kwak — la série d'animation néerlandaise-japonaise tant aimée, remasterisée en 8K. Suivez les aventures du canard Alfred dans un monde qui reflète des événements historiques réels.",
        'pt': "🦆 Alfred J. Kwak — adorada série animada holandesa-japonesa, remasterizada em 8K. Acompanhe as aventuras do pato Alfred em um mundo que reflete eventos históricos reais.",
    },
    'superman': {
        'en': "🦸 Classic Superman cartoon by Fleischer Studios (1941-1943), remastered in stunning 8K. These groundbreaking animations set the standard for superhero media and remain masterpieces of American animation.",
        'de': "🦸 Klassischer Superman-Cartoon von Fleischer Studios (1941-1943), remastered in atemberaubender 8K-Qualität. Diese bahnbrechenden Animationen setzten den Standard für Superhelden-Medien.",
        'es': "🦸 Clásico dibujo animado de Superman de Fleischer Studios (1941-1943), remasterizado en 8K. Estas animaciones revolucionarias establecieron el estándar para los medios de superhéroes.",
        'fr': "🦸 Classique dessin animé Superman des studios Fleischer (1941-1943), remasterisé en 8K. Ces animations révolutionnaires ont défini le standard des médias de super-héros.",
        'pt': "🦸 Clássico desenho animado do Superman dos estúdios Fleischer (1941-1943), remasterizado em 8K. Estas animações revolucionárias definiram o padrão para a mídia de super-heróis.",
    },
    'popeye': {
        'en': "💪 Classic Popeye the Sailor cartoon by Fleischer Studios, remastered in 8K quality. The spinach-loving sailor's adventures brought to life with AI upscaling.",
        'de': "💪 Klassischer Popeye der Seemann Cartoon von Fleischer Studios, remastered in 8K-Qualität. Die Abenteuer des spinatliebenden Seemanns in neuem Glanz.",
        'es': "💪 Clásico dibujo animado de Popeye el Marino de Fleischer Studios, remasterizado en calidad 8K. Las aventuras del marinero amante de las espinacas.",
        'fr': "💪 Classique dessin animé Popeye le Marin des studios Fleischer, remasterisé en qualité 8K. Les aventures du marin amateur d'épinards.",
        'pt': "💪 Clássico desenho animado do Popeye, o Marinheiro, dos estúdios Fleischer, remasterizado em qualidade 8K.",
    },
    'felix': {
        'en': "🐱 Felix the Cat — one of the most iconic cartoon characters in history! This silent-era classic has been remastered in 8K. Felix first appeared in 1919 and became the world's first animated superstar.",
        'de': "🐱 Felix the Cat — eine der ikonischsten Zeichentrickfiguren der Geschichte! Dieser Stummfilm-Klassiker wurde in 8K remastered. Felix trat 1919 erstmals auf und wurde der erste animierte Superstar der Welt.",
        'es': "🐱 El Gato Félix — ¡uno de los personajes de dibujos animados más icónicos de la historia! Este clásico de la era del cine mudo fue remasterizado en 8K.",
        'fr': "🐱 Félix le Chat — l'un des personnages de dessins animés les plus emblématiques de l'histoire ! Ce classique du cinéma muet a été remasterisé en 8K.",
        'pt': "🐱 Gato Félix — um dos personagens de desenhos animados mais icônicos da história! Este clássico da era do cinema mudo foi remasterizado em 8K.",
    },
    'casper': {
        'en': "👻 Casper the Friendly Ghost — the lovable cartoon ghost from Famous Studios, remastered in 8K. These charming shorts prove that not all ghosts are scary!",
        'de': "👻 Casper, das freundliche Gespenst — der liebenswerte Zeichentrickgeist von Famous Studios, remastered in 8K.",
        'es': "👻 Gasparín, el fantasma amigable — de Famous Studios, remasterizado en 8K.",
        'fr': "👻 Casper le fantôme amical — des studios Famous, remasterisé en 8K.",
        'pt': "👻 Gasparzinho, o fantasminha camarada — dos estúdios Famous, remasterizado em 8K.",
    },
    'maulwurf': {
        'en': "🐀 Krtek (The Little Mole) — beloved Czech animated series by Zdeněk Miler, remastered in 8K. This charming character has delighted audiences worldwide since 1956.",
        'de': "🐀 Der kleine Maulwurf (Krtek) — die beliebte tschechische Zeichentrickserie von Zdeněk Miler, remastered in 8K. Diese charmante Figur begeistert seit 1956 Zuschauer weltweit.",
        'es': "🐀 El Topito (Krtek) — querida serie animada checa de Zdeněk Miler, remasterizada en 8K.",
        'fr': "🐀 La Petite Taupe (Krtek) — adorable série d'animation tchèque de Zdeněk Miler, remasterisée en 8K.",
        'pt': "🐀 A Toupeira (Krtek) — adorada série animada tcheca de Zdeněk Miler, remasterizada em 8K.",
    },
    'ken_block': {
        'en': "🏎️ Ken Block legendary motorsport footage, remastered in stunning 8K quality. Experience the iconic Gymkhana series and street racing like never before.",
        'de': "🏎️ Ken Block legendäres Motorsport-Material, remastered in atemberaubender 8K-Qualität. Erlebe die ikonische Gymkhana-Serie wie nie zuvor.",
        'es': "🏎️ Imágenes legendarias de Ken Block, remasterizadas en calidad 8K. Experimenta la icónica serie Gymkhana como nunca antes.",
        'fr': "🏎️ Séquences légendaires de Ken Block, remasterisées en qualité 8K. Vivez l'iconique série Gymkhana comme jamais auparavant.",
        'pt': "🏎️ Imagens lendárias de Ken Block, remasterizadas em qualidade 8K. Experimente a icônica série Gymkhana como nunca antes.",
    },
    'looney_tunes': {
        'en': "🐰 Classic Warner Bros. cartoon from the golden age of animation, remastered in 8K quality. Looney Tunes and Merrie Melodies brought to life with AI upscaling.",
        'de': "🐰 Klassischer Warner Bros. Cartoon aus dem goldenen Zeitalter der Animation, remastered in 8K-Qualität.",
        'es': "🐰 Clásico dibujo animado de Warner Bros. de la edad de oro de la animación, remasterizado en calidad 8K.",
        'fr': "🐰 Classique dessin animé Warner Bros. de l'âge d'or de l'animation, remasterisé en qualité 8K.",
        'pt': "🐰 Clássico desenho animado da Warner Bros. da era de ouro da animação, remasterizado em qualidade 8K.",
    },
    'christmas': {
        'en': "🎄 Classic Christmas film remastered in 8K quality. Enjoy this timeless holiday classic with stunning AI-enhanced visuals.",
        'de': "🎄 Klassischer Weihnachtsfilm remastered in 8K-Qualität. Genieße diesen zeitlosen Feiertagsklassiker in atemberaubender KI-verbesserter Bildqualität.",
        'es': "🎄 Clásica película navideña remasterizada en calidad 8K. Disfruta de este clásico navideño con visuales mejorados por IA.",
        'fr': "🎄 Film de Noël classique remasterisé en qualité 8K. Profitez de ce classique des fêtes avec des visuels améliorés par IA.",
        'pt': "🎄 Clássico filme de Natal remasterizado em qualidade 8K. Aproveite este clássico natalino com visuais aprimorados por IA.",
    },
    'astro_boy': {
        'en': "🤖 Astro Boy (Tetsuwan Atom) — the legendary anime by Osamu Tezuka, remastered in 8K. The godfather of manga and anime created this timeless masterpiece.",
        'de': "🤖 Astro Boy (Tetsuwan Atom) — der legendäre Anime von Osamu Tezuka, remastered in 8K. Der Urvater des Manga und Anime schuf dieses zeitlose Meisterwerk.",
        'es': "🤖 Astro Boy (Tetsuwan Atom) — el legendario anime de Osamu Tezuka, remasterizado en 8K.",
        'fr': "🤖 Astro Boy (Tetsuwan Atom) — l'anime légendaire d'Osamu Tezuka, remasterisé en 8K.",
        'pt': "🤖 Astro Boy (Tetsuwan Atom) — o lendário anime de Osamu Tezuka, remasterizado em 8K.",
    },
}

# Fallback for categories not explicitly listed
DEFAULT_INTROS = {
    'en': "🎬 Classic film remastered in stunning 8K quality with AI upscaling technology. This public domain gem has been preserved and enhanced for modern audiences.",
    'de': "🎬 Klassischer Film remastered in atemberaubender 8K-Qualität mit KI-Upscaling. Dieses Public-Domain-Juwel wurde für moderne Zuschauer bewahrt und verbessert.",
    'es': "🎬 Película clásica remasterizada en impresionante calidad 8K con tecnología de IA. Esta joya de dominio público ha sido preservada y mejorada.",
    'fr': "🎬 Film classique remasterisé en qualité 8K époustouflante avec technologie IA. Ce joyau du domaine public a été préservé et amélioré.",
    'pt': "🎬 Filme clássico remasterizado em impressionante qualidade 8K com tecnologia de IA. Esta joia de domínio público foi preservada e aprimorada.",
}

# Hashtags per category
CATEGORY_HASHTAGS = {
    'betty_boop':   '#BettyBoop #8K #PublicDomain #VintageAnimation #Fleischer',
    'soundie':      '#Soundie #8K #VintageMusic #1940s #Jazz',
    'wochenschau':  '#Wochenschau #WWII #8K #History #PublicDomain',
    'alfred':       '#AlfredJKwak #8K #Animation #ClassicCartoon',
    'superman':     '#Superman #8K #Fleischer #ClassicAnimation #PublicDomain',
    'popeye':       '#Popeye #8K #Fleischer #ClassicAnimation #PublicDomain',
    'felix':        '#FelixTheCat #8K #SilentFilm #ClassicAnimation #PublicDomain',
    'casper':       '#Casper #8K #ClassicAnimation #PublicDomain',
    'maulwurf':     '#Krtek #DerKleineMaulwurf #8K #CzechAnimation',
    'ken_block':    '#KenBlock #Gymkhana #8K #Motorsport',
    'looney_tunes': '#LooneyTunes #8K #WarneBros #ClassicAnimation',
    'christmas':    '#Christmas #8K #ClassicFilm #Holiday #PublicDomain',
    'astro_boy':    '#AstroBoy #8K #Anime #OsamuTezuka #ClassicAnime',
    'other':        '#8K #PublicDomain #ClassicFilm #Remastered',
}


def build_localized_description(lang, category, original_title):
    """Build a localized description for a non-default language."""
    intros = CATEGORY_INTROS.get(category, DEFAULT_INTROS)
    intro = intros.get(lang, intros.get('en', DEFAULT_INTROS['en']))
    cta = CTA.get(lang, CTA['en'])
    hashtags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['other'])
    
    return f"""{intro}

{cta}
{LINKS_BLOCK}

{hashtags}"""


# ============================================================
# YOUTUBE API HELPERS
# ============================================================

def get_youtube_client():
    """Build authenticated YouTube API client with auto-refresh."""
    creds_data = json.load(open(OAUTH_FILE))
    creds = Credentials(
        token=creds_data['access_token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)


def fetch_video_details(video_ids, yt):
    """Fetch snippet+localizations for videos in batches of 50."""
    global quota_used
    all_videos = {}
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        try:
            resp = yt.videos().list(
                part='snippet,localizations',
                id=','.join(batch),
                maxResults=50
            ).execute()
            quota_used += 1
            
            for item in resp.get('items', []):
                vid = item['id']
                all_videos[vid] = {
                    'snippet': item.get('snippet', {}),
                    'localizations': item.get('localizations', {})
                }
            
            print(f"  Fetched {min(i+50, len(video_ids))}/{len(video_ids)} videos...")
        
        except Exception as e:
            err_str = str(e)
            print(f"  ❌ Fetch error: {err_str[:120]}")
            if 'quotaExceeded' in err_str:
                print("  🛑 QUOTA EXCEEDED! Stopping.")
                return None
    
    return all_videos


def update_video(video_id, snippet_update, localizations, yt):
    """Update a single video's snippet and localizations."""
    global quota_used
    
    body = {
        'id': video_id,
        'snippet': snippet_update,
        'localizations': localizations
    }
    
    try:
        yt.videos().update(
            part='snippet,localizations',
            body=body
        ).execute()
        quota_used += 50
        return True, None
    except Exception as e:
        err_str = str(e)
        # Don't count quota on 403 rejected requests
        if '403' not in err_str:
            quota_used += 50
        return False, err_str[:200]


# ============================================================
# MAIN
# ============================================================

def main():
    global quota_used
    
    mode = "🔴 LIVE" if APPLY else "🟡 DRY-RUN"
    print(f"{'='*60}")
    print(f"  MULTILINGUAL LOCALIZATION PUSH — {mode}")
    print(f"  Target languages: {', '.join(TARGET_LANGUAGES)}")
    if LIMIT:
        print(f"  Limit: {LIMIT} videos")
    print(f"{'='*60}\n")
    
    # 1. Load snapshot for video list
    print("📂 Loading channel snapshot...")
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)
    
    # Deduplicate and filter to public only
    seen = set()
    video_ids = []
    for v in snapshot['all_videos']:
        if v['privacy'] == 'public' and v['id'] not in seen:
            seen.add(v['id'])
            video_ids.append(v['id'])
    
    print(f"  Found {len(video_ids)} unique public videos\n")
    
    # 2. Build YouTube client (auto-refreshes token)
    print("🔑 Building YouTube API client...")
    yt = get_youtube_client()
    
    # 3. Fetch current video details (READ = cheap)
    print("📡 Fetching current video details (snippet + localizations)...")
    video_data = fetch_video_details(video_ids, yt)
    if video_data is None:
        print("💀 Fetch failed due to quota. Aborting.")
        return
    
    print(f"  ✅ Got details for {len(video_data)} videos (quota used: {quota_used})\n")
    
    # 4. Analyze and prepare updates
    print("🔍 Analyzing videos and preparing updates...\n")
    
    updates = []
    stats = {
        'lang_fix': 0,
        'already_localized': 0,
        'to_update': 0,
        'categories': Counter(),
    }
    
    for vid in video_ids:
        if vid not in video_data:
            continue
        
        vd = video_data[vid]
        snippet = vd['snippet']
        existing_locs = vd.get('localizations', {})
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        category_id = snippet.get('categoryId', '1')
        current_lang = snippet.get('defaultLanguage', '')
        
        # Detect content category
        cat = detect_category(title)
        stats['categories'][cat] += 1
        
        # Check if already has proper localizations (≥4 = already done)
        if len(existing_locs) >= 4:
            stats['already_localized'] += 1
            continue
        
        # Determine correct defaultLanguage
        new_lang = correct_default_language(current_lang, cat, title)
        effective_lang = new_lang if new_lang else current_lang
        if new_lang:
            stats['lang_fix'] += 1
        
        # Build snippet update (MUST include required fields to avoid wipe)
        snippet_update = {
            'title': title,
            'description': description,
            'categoryId': category_id,
            'defaultLanguage': effective_lang,
        }
        # Preserve tags if present
        if snippet.get('tags'):
            snippet_update['tags'] = snippet['tags']
        
        # Build localizations
        new_localizations = {}
        
        # Default language localization = current title + description
        new_localizations[effective_lang] = {
            'title': title,
            'description': description
        }
        
        # Add other target languages
        for lang in TARGET_LANGUAGES:
            if lang == effective_lang:
                continue  # Already set above
            new_localizations[lang] = {
                'title': title,  # Keep original title (proper nouns)
                'description': build_localized_description(lang, cat, title)
            }
        
        updates.append({
            'video_id': vid,
            'title': title,
            'category': cat,
            'lang_fix': f"{current_lang}→{effective_lang}" if new_lang else None,
            'snippet_update': snippet_update,
            'localizations': new_localizations,
            'langs_added': [l for l in TARGET_LANGUAGES if l != effective_lang],
        })
    
    stats['to_update'] = len(updates)
    
    # Apply limit
    if LIMIT and len(updates) > LIMIT:
        updates = updates[:LIMIT]
        print(f"  ⚠️ Limited to {LIMIT} videos\n")
    
    # Print summary
    print(f"{'='*60}")
    print(f"  ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"  Videos to update:        {stats['to_update']}")
    print(f"  Already localized (skip): {stats['already_localized']}")
    print(f"  defaultLanguage fixes:    {stats['lang_fix']}")
    print(f"  Quota for updates:        {len(updates) * 50} units")
    print(f"  Quota already used:       {quota_used} units")
    print()
    print(f"  Content categories:")
    for cat, count in stats['categories'].most_common():
        print(f"    {cat}: {count}")
    print()
    
    # Show first 5 planned changes
    print(f"  📋 First {min(5, len(updates))} planned updates:")
    for u in updates[:5]:
        fix_str = f" [FIX: {u['lang_fix']}]" if u['lang_fix'] else ""
        print(f"    {u['video_id']} | {u['category']:15s} | +{','.join(u['langs_added'])}{fix_str}")
        print(f"      {u['title'][:70]}")
    print()
    
    # 5. Execute updates
    if not APPLY:
        print(f"🟡 DRY-RUN complete. Use --apply to push {len(updates)} updates.")
        print(f"   Estimated quota: {len(updates) * 50 + quota_used} units total")
    else:
        print(f"🔴 APPLYING {len(updates)} updates...")
        success = 0
        failed = 0
        results = []
        
        for i, u in enumerate(updates):
            if quota_used >= MAX_QUOTA:
                print(f"\n  ⚠️ Quota safety limit reached ({quota_used}/{MAX_QUOTA}). Stopping.")
                break
            
            ok, err = update_video(u['video_id'], u['snippet_update'], u['localizations'], yt)
            
            if ok:
                success += 1
                status_str = "✅"
            else:
                failed += 1
                status_str = f"❌ {err}"
                # Stop on quota exceeded
                if 'quotaExceeded' in str(err) or 'exceeded' in str(err).lower() or '403' in str(err):
                    print(f"\n  🛑 QUOTA EXCEEDED at video {i+1}! Stopping.")
                    results.append({'id': u['video_id'], 'ok': False, 'error': err})
                    break
            
            results.append({
                'id': u['video_id'],
                'ok': ok,
                'error': err,
                'lang_fix': u['lang_fix'],
                'langs_added': u['langs_added'],
            })
            
            print(f"  [{i+1}/{len(updates)}] {status_str} {u['video_id']} | {u['title'][:50]}...")
            
            # Rate limit: 1.5s between writes
            if i < len(updates) - 1:
                time.sleep(1.5)
        
        print(f"\n{'='*60}")
        print(f"  RESULTS: {success} ✅ | {failed} ❌ | Quota used: {quota_used}")
        print(f"{'='*60}")
        
        # Save results
        report = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'LIVE',
            'total_attempted': len(results),
            'success': success,
            'failed': failed,
            'quota_used': quota_used,
            'results': results,
        }
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  📄 Report saved: {OUTPUT_FILE}")
    
    # Always save dry-run plan
    if not APPLY:
        plan = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'DRY-RUN',
            'total_updates': len(updates),
            'lang_fixes': stats['lang_fix'],
            'already_localized': stats['already_localized'],
            'estimated_quota': len(updates) * 50 + quota_used,
            'updates': [{
                'video_id': u['video_id'],
                'title': u['title'][:80],
                'category': u['category'],
                'lang_fix': u['lang_fix'],
                'langs_added': u['langs_added'],
            } for u in updates]
        }
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"  📄 Plan saved: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
