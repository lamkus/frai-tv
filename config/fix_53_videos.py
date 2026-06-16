# -*- coding: utf-8 -*-
"""
Fix remaining 53 videos on @remAIke_IT
Issues: LOW_LOC, NO_CTA, UNTRANSLATED_JA, NO_HASHTAGS, NO_QUALITY_TAG, NO_TAGS, SHORT_DESC, NO_WEBSITE
"""
import json, sys, io, time, urllib.request, urllib.parse, urllib.error, os, re, traceback
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ─── CONFIG ───
OAUTH_PATH = r"D:\remaike.TV\config\youtube_oauth.json"
AUDIT_PATH = r"D:\remaike.TV\config\deep_audit_2026_04_15.json"
REPORT_PATH = r"D:\remaike.TV\config\final_fixes_2026_04_15.json"

CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 SUBSCRIBE: https://www.youtube.com/@remAIke_IT?sub_confirmation=1
🌐 Watch on FRai.TV: https://frai.tv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

TARGET_LANGS = ["de", "en", "ja", "fr", "es", "pt-BR", "hi", "ko"]

# ─── OAUTH ───
with open(OAUTH_PATH, "r", encoding="utf-8") as f:
    oauth = json.load(f)

ACCESS_TOKEN = None

def refresh_access_token():
    global ACCESS_TOKEN
    data = urllib.parse.urlencode({
        "client_id": oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "refresh_token": oauth["refresh_token"],
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    ACCESS_TOKEN = result["access_token"]
    print(f"[AUTH] Token refreshed, expires_in={result.get('expires_in')}")

def yt_api(method, endpoint, params=None, body=None):
    """Generic YouTube API call."""
    base = "https://www.googleapis.com/youtube/v3/" + endpoint
    if params:
        base += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(base, data=data, method=method)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    if body:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[API ERROR] {e.code}: {err_body[:500]}")
        raise

def get_video(video_id):
    """Get video snippet + localizations. Cost: 1 unit."""
    return yt_api("GET", "videos", {"part": "snippet,localizations", "id": video_id})

def update_video(video_id, snippet, localizations=None):
    """Update video snippet + localizations. Cost: 50 units."""
    body = {
        "id": video_id,
        "snippet": snippet,
    }
    parts = ["snippet"]
    if localizations is not None:
        body["localizations"] = localizations
        parts.append("localizations")
    return yt_api("PUT", "videos", {"part": ",".join(parts)}, body)

# ─── TRANSLATION MAPS ───
# Character name translations for known series
CHAR_TRANSLATIONS = {
    "Betty Boop": {"de": "Betty Boop", "en": "Betty Boop", "ja": "ベティ・ブープ", "fr": "Betty Boop", "es": "Betty Boop", "pt-BR": "Betty Boop", "hi": "बेट्टी बूप", "ko": "베티 붑"},
    "Felix": {"de": "Felix", "en": "Felix", "ja": "フィリックス", "fr": "Félix", "es": "Félix", "pt-BR": "Félix", "hi": "फ़ेलिक्स", "ko": "펠릭스"},
    "Superman": {"de": "Superman", "en": "Superman", "ja": "スーパーマン", "fr": "Superman", "es": "Superman", "pt-BR": "Superman", "hi": "सुपरमैन", "ko": "슈퍼맨"},
    "Gabby": {"de": "Gabby", "en": "Gabby", "ja": "ギャビー", "fr": "Gabby", "es": "Gabby", "pt-BR": "Gabby", "hi": "गैबी", "ko": "개비"},
    "Tarzan": {"de": "Tarzan", "en": "Tarzan", "ja": "ターザン", "fr": "Tarzan", "es": "Tarzán", "pt-BR": "Tarzan", "hi": "टार्ज़न", "ko": "타잔"},
    "Kirby": {"de": "Kirby", "en": "Kirby", "ja": "カービィ", "fr": "Kirby", "es": "Kirby", "pt-BR": "Kirby", "hi": "कर्बी", "ko": "커비"},
}

# Descriptor translations
DESC_TRANSLATIONS = {
    "Full Movie": {"de": "Ganzer Film", "en": "Full Movie", "ja": "映画全編", "fr": "Film Complet", "es": "Película Completa", "pt-BR": "Filme Completo", "hi": "पूरी फ़िल्म", "ko": "전체 영화"},
    "Silent Horror": {"de": "Stummfilm-Horror", "en": "Silent Horror", "ja": "サイレントホラー", "fr": "Horreur Muette", "es": "Terror Mudo", "pt-BR": "Terror Mudo", "hi": "मूक हॉरर", "ko": "무성 호러"},
    "Rib Solo": {"de": "Rippen-Solo", "en": "Rib Solo", "ja": "リブ・ソロ", "fr": "Solo de Côtes", "es": "Solo de Costillas", "pt-BR": "Solo de Costelas", "hi": "रिब सोलो", "ko": "갈비뼈 솔로"},
    "Anti-Weed Propaganda": {"de": "Anti-Marihuana-Propaganda", "en": "Anti-Weed Propaganda", "ja": "反マリファナ・プロパガンダ", "fr": "Propagande Anti-Cannabis", "es": "Propaganda Anti-Marihuana", "pt-BR": "Propaganda Anti-Maconha", "hi": "मारिजुआना विरोधी प्रचार", "ko": "반대마 선전"},
    "Funny Anime Parody": {"de": "Lustige Anime-Parodie", "en": "Funny Anime Parody", "ja": "アニメパロディ", "fr": "Parodie Anime Drôle", "es": "Parodia Anime Divertida", "pt-BR": "Paródia Anime Engraçada", "hi": "मज़ेदार एनीमे पैरोडी", "ko": "재미있는 애니메 패러디"},
    "Colorized Home Movies": {"de": "Kolorierte Heimfilme", "en": "Colorized Home Movies", "ja": "カラー化ホームムービー", "fr": "Films Amateurs Colorisés", "es": "Películas Caseras Coloreadas", "pt-BR": "Filmes Caseiros Colorizados", "hi": "रंगीन होम मूवी", "ko": "컬러화 홈무비"},
    "Fleischer": {"de": "Fleischer", "en": "Fleischer", "ja": "フライシャー", "fr": "Fleischer", "es": "Fleischer", "pt-BR": "Fleischer", "hi": "फ्लीशर", "ko": "플라이셔"},
    "Fleischer Classic": {"de": "Fleischer-Klassiker", "en": "Fleischer Classic", "ja": "フライシャー・クラシック", "fr": "Classique Fleischer", "es": "Clásico Fleischer", "pt-BR": "Clássico Fleischer", "hi": "फ्लीशर क्लासिक", "ko": "플라이셔 클래식"},
    "Disney": {"de": "Disney", "en": "Disney", "ja": "ディズニー", "fr": "Disney", "es": "Disney", "pt-BR": "Disney", "hi": "डिज़्नी", "ko": "디즈니"},
    "ComiColor": {"de": "ComiColor", "en": "ComiColor", "ja": "コミカラー", "fr": "ComiColor", "es": "ComiColor", "pt-BR": "ComiColor", "hi": "कॉमीकलर", "ko": "코미컬러"},
    "Hepburn": {"de": "Hepburn", "en": "Hepburn", "ja": "ヘプバーン", "fr": "Hepburn", "es": "Hepburn", "pt-BR": "Hepburn", "hi": "हेपबर्न", "ko": "헵번"},
    "Soundie": {"de": "Soundie", "en": "Soundie", "ja": "サウンディ", "fr": "Soundie", "es": "Soundie", "pt-BR": "Soundie", "hi": "साउंडी", "ko": "사운디"},
    "Vintage Compilation": {"de": "Vintage-Zusammenstellung", "en": "Vintage Compilation", "ja": "ヴィンテージ総集編", "fr": "Compilation Vintage", "es": "Compilación Vintage", "pt-BR": "Compilação Vintage", "hi": "विंटेज संकलन", "ko": "빈티지 모음"},
    "Upgrade Complete": {"de": "Upgrade abgeschlossen", "en": "Upgrade Complete", "ja": "アップグレード完了", "fr": "Mise à Jour Terminée", "es": "Actualización Completa", "pt-BR": "Atualização Completa", "hi": "अपग्रेड पूर्ण", "ko": "업그레이드 완료"},
}

# Series detection for hashtags
SERIES_HASHTAGS = {
    "Wochenschau": "#Wochenschau",
    "Alfred J. Kwak": "#AlfredJKwak",
    "Der 7. Sinn": "#Der7Sinn",
    "Betty Boop": "#BettyBoop",
    "Skeleton Dance": "#SkeletonDance",
    "ComiColor": "#ComiColor",
    "Mel-O-Toons": "#MelOToons",
    "Mel‑O‑Toons": "#MelOToons",
    "Marihuana": "#Propaganda",
    "Times Square": "#TimesSquare",
    "Tarzan": "#Tarzan",
    "Gabby": "#Fleischer",
    "Clever & Smart": "#CleverUndSmart",
    "Kirby": "#Kirby",
    "Pigs In A Polka": "#WB",
    "Lucy": "#TheLucyShow",
    "Atomic Bomb": "#Newsreel",
    "Soviet Experiment": "#Documentary",
    "New Year": "#NewYear",
    "Fleischer": "#Fleischer",
    "Hut-Sut Song": "#Soundie",
    "Wonderful World": "#ClassicFilm",
    "Bill of Divorcement": "#KatharineHepburn",
    "Livestream": "#Livestream",
}

def detect_series_hashtag(title):
    for key, tag in SERIES_HASHTAGS.items():
        if key.lower() in title.lower():
            return tag
    return "#ClassicFilm"

def translate_title(title, lang):
    """
    Translate a video title to the target language.
    Keep film titles in original language, translate descriptors and character names.
    """
    result = title
    # Translate descriptors
    for eng, trans in DESC_TRANSLATIONS.items():
        if eng in result and lang in trans:
            result = result.replace(eng, trans[lang])
    # For non-latin scripts, also translate some common words
    return result

def generate_localized_title(title, lang):
    """Generate a localized title for a given language."""
    if lang in ("de", "en"):
        return translate_title(title, lang)

    t = translate_title(title, lang)
    return t

def generate_localized_description(desc, lang):
    """Generate a localized description. Keep links, translate CTA if present."""
    if not desc:
        return desc

    subscribe_translations = {
        "de": "🔔 ABONNIEREN",
        "en": "🔔 SUBSCRIBE",
        "ja": "🔔 チャンネル登録",
        "fr": "🔔 S'ABONNER",
        "es": "🔔 SUSCRÍBETE",
        "pt-BR": "🔔 INSCREVA-SE",
        "hi": "🔔 सब्सक्राइब करें",
        "ko": "🔔 구독하기",
    }
    watch_translations = {
        "de": "🌐 Auf FRai.TV ansehen",
        "en": "🌐 Watch on FRai.TV",
        "ja": "🌐 FRai.TVで視聴",
        "fr": "🌐 Regarder sur FRai.TV",
        "es": "🌐 Ver en FRai.TV",
        "pt-BR": "🌐 Assistir no FRai.TV",
        "hi": "🌐 FRai.TV पर देखें",
        "ko": "🌐 FRai.TV에서 시청",
    }

    result = desc
    if lang in subscribe_translations:
        result = result.replace("🔔 SUBSCRIBE", subscribe_translations[lang])
    if lang in watch_translations:
        result = result.replace("🌐 Watch on FRai.TV", watch_translations[lang])
    return result

# ─── UNTRANSLATED_JA fixes ───
JA_FIXES = {
    "3AtirtgrfUI": ("Fall of Warsaw", "ワルシャワ陥落"),    # Wochenschau 473
    "iql1XOHf0t0": ("Fall of Warsaw", "ワルシャワ陥落"),    # Wochenschau 474
    "T1pUCPyDrl4": ("Eastern Retreats", "東部戦線撤退"),   # Wochenschau 692
    "RsfUriJTAvE": ("Tehran Conference", "テヘラン会談"),   # Wochenschau 690
}

# ─── SPECIAL VIDEO: deutsche wochenschau nr696 1944 ───
SPECIAL_ID = "10eYnX7MjGY"
SPECIAL_NEW_TITLE = "Wochenschau 696: Ostfront Winter 1944 (22.12.1943) | 8K HQ (4K UHD)"
SPECIAL_NEW_DESC = """Deutsche Wochenschau Nr. 696 vom 22. Dezember 1943 – Ostfront im Winter 1944. Originalaufnahmen der UFA-Wochenschau zeigen die Kämpfe an der Ostfront und die Winteroffensive.

Historisches Filmmaterial, digital restauriert und auf 8K hochskaliert mit KI-Upscaling für maximale Bildqualität.

🎬 Alle Wochenschau-Folgen: https://frai.tv/wochenschau

#remAIke #8K #Wochenschau

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 SUBSCRIBE: https://www.youtube.com/@remAIke_IT?sub_confirmation=1
🌐 Watch on FRai.TV: https://frai.tv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
SPECIAL_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "Nr 696", "1943", "1944",
    "Ostfront", "Winter 1944", "UFA", "Newsreel", "WWII",
    "World War 2", "8K", "4K UHD", "remAIke", "frai.tv"
]

# ─── LIVESTREAM VIDEO ───
LIVESTREAM_ID = "ynPokHSSMss"
LIVESTREAM_NEW_TITLE = "Livestream von remAIke_IT | 8K HQ (4K UHD)"
LIVESTREAM_NEW_DESC = """Willkommen zum remAIke_IT Livestream! Klassische Filme, Cartoons und historische Aufnahmen – digital restauriert und auf 8K hochskaliert mit KI-Upscaling.

Besucht unseren Kanal für hunderte restaurierte Klassiker aus Film und Fernsehen.

🎬 Alle Videos: https://frai.tv

#remAIke #8K #Livestream

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 SUBSCRIBE: https://www.youtube.com/@remAIke_IT?sub_confirmation=1
🌐 Watch on FRai.TV: https://frai.tv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
LIVESTREAM_TAGS = [
    "remAIke", "Livestream", "8K", "4K UHD", "Classic Films",
    "Restored", "AI Upscaling", "frai.tv", "Classic Cartoons",
    "Vintage", "Public Domain", "Film Restoration"
]

# Wochenschau localization templates
WOCHENSCHAU_TITLE_TRANSLATIONS = {
    "de": "Wochenschau {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "en": "Newsreel {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "ja": "ニュース映画 {num}: {event_ja} ({date}) | 8K HQ (4K UHD)",
    "fr": "Actualités {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "es": "Noticiario {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "pt-BR": "Cinejornal {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "hi": "समाचार रील {num}: {event} ({date}) | 8K HQ (4K UHD)",
    "ko": "뉴스릴 {num}: {event} ({date}) | 8K HQ (4K UHD)",
}

WOCHENSCHAU_EVENT_JA = {
    "Fall of Warsaw": "ワルシャワ陥落",
    "Eastern Retreats": "東部戦線撤退",
    "Tehran Conference": "テヘラン会談",
    "Ostfront Winter 1944": "東部戦線 冬1944",
}

# ─── MAIN LOGIC ───
def main():
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        audit = json.load(f)

    videos = audit["issues_detail"]

    # Deduplicate by id
    seen = set()
    unique_videos = []
    for v in videos:
        if v["id"] not in seen:
            seen.add(v["id"])
            unique_videos.append(v)

    print(f"[INFO] Total unique videos to fix: {len(unique_videos)}")

    refresh_access_token()

    report = {
        "date": "2026-04-15",
        "total_videos": len(unique_videos),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "quota_used": 0,
        "details": []
    }

    for idx, video_info in enumerate(unique_videos):
        vid = video_info["id"]
        issues = video_info["issues"]
        title_hint = video_info["title"]

        print(f"\n[{idx+1}/{len(unique_videos)}] Processing {vid}: {title_hint[:60]}...")
        print(f"  Issues: {issues}")

        detail = {"id": vid, "title": title_hint, "issues": issues, "actions": [], "status": "pending"}

        try:
            # Refresh token every 40 minutes (proactive)
            if idx > 0 and idx % 30 == 0:
                refresh_access_token()

            # GET video data (1 quota unit)
            resp = get_video(vid)
            report["quota_used"] += 1

            if not resp.get("items"):
                print(f"  [SKIP] Video not found")
                detail["status"] = "not_found"
                report["skipped"] += 1
                report["details"].append(detail)
                continue

            item = resp["items"][0]
            snippet = item["snippet"]
            existing_locs = item.get("localizations", {})

            # Preserve ALL snippet fields
            updated_snippet = {
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "tags": snippet.get("tags", []),
                "categoryId": snippet["categoryId"],
            }
            if "defaultLanguage" in snippet:
                updated_snippet["defaultLanguage"] = snippet["defaultLanguage"]
            if "defaultAudioLanguage" in snippet:
                updated_snippet["defaultAudioLanguage"] = snippet["defaultAudioLanguage"]

            updated_locs = dict(existing_locs)
            needs_snippet_update = False
            needs_loc_update = False

            # ─── SPECIAL VIDEO ───
            if vid == SPECIAL_ID:
                updated_snippet["title"] = SPECIAL_NEW_TITLE
                updated_snippet["description"] = SPECIAL_NEW_DESC
                updated_snippet["tags"] = SPECIAL_TAGS
                updated_snippet["defaultLanguage"] = "de"
                updated_snippet["defaultAudioLanguage"] = "de"
                needs_snippet_update = True
                detail["actions"].append("SPECIAL_FULL_REWRITE")

                # Generate all 8 localizations for special video
                for lang in TARGET_LANGS:
                    loc_title = WOCHENSCHAU_TITLE_TRANSLATIONS.get(lang, "Wochenschau 696: {event} ({date}) | 8K HQ (4K UHD)")
                    if lang == "ja":
                        loc_title = loc_title.format(num="696", event_ja="東部戦線 冬1944", date="22.12.1943")
                    else:
                        event_text = "Ostfront Winter 1944" if lang == "de" else "Eastern Front Winter 1944"
                        loc_title = loc_title.format(num="696", event=event_text, date="22.12.1943")

                    loc_desc = generate_localized_description(SPECIAL_NEW_DESC, lang)
                    updated_locs[lang] = {"title": loc_title, "description": loc_desc}
                needs_loc_update = True
                detail["actions"].append("FULL_LOCALIZATIONS_8")

            # ─── LIVESTREAM VIDEO ───
            elif vid == LIVESTREAM_ID:
                updated_snippet["title"] = LIVESTREAM_NEW_TITLE
                updated_snippet["description"] = LIVESTREAM_NEW_DESC
                updated_snippet["tags"] = LIVESTREAM_TAGS
                updated_snippet["defaultLanguage"] = "de"
                updated_snippet["defaultAudioLanguage"] = "de"
                needs_snippet_update = True
                detail["actions"].append("LIVESTREAM_FULL_REWRITE")

                # Localizations for livestream
                livestream_titles = {
                    "de": "Livestream von remAIke_IT | 8K HQ (4K UHD)",
                    "en": "remAIke_IT Livestream | 8K HQ (4K UHD)",
                    "ja": "remAIke_IT ライブ配信 | 8K HQ (4K UHD)",
                    "fr": "Diffusion en direct remAIke_IT | 8K HQ (4K UHD)",
                    "es": "Transmisión en vivo remAIke_IT | 8K HQ (4K UHD)",
                    "pt-BR": "Transmissão ao vivo remAIke_IT | 8K HQ (4K UHD)",
                    "hi": "remAIke_IT लाइवस्ट्रीम | 8K HQ (4K UHD)",
                    "ko": "remAIke_IT 라이브 스트리밍 | 8K HQ (4K UHD)",
                }
                for lang in TARGET_LANGS:
                    loc_desc = generate_localized_description(LIVESTREAM_NEW_DESC, lang)
                    updated_locs[lang] = {"title": livestream_titles.get(lang, LIVESTREAM_NEW_TITLE), "description": loc_desc}
                needs_loc_update = True
                detail["actions"].append("FULL_LOCALIZATIONS_8")

            else:
                # ─── Process each issue type ───

                # NO_QUALITY_TAG: Add "| 8K HQ (4K UHD)" to title
                if any("NO_QUALITY_TAG" in i for i in issues):
                    if "8K HQ" not in updated_snippet["title"]:
                        updated_snippet["title"] = updated_snippet["title"].rstrip() + " | 8K HQ (4K UHD)"
                        needs_snippet_update = True
                        detail["actions"].append("ADD_QUALITY_TAG")

                # SHORT_DESC: Expand description
                if any("SHORT_DESC" in i for i in issues):
                    current_desc = updated_snippet["description"]
                    if len(current_desc) < 200:
                        # Build a proper description from title
                        expanded = build_description(updated_snippet["title"], current_desc)
                        updated_snippet["description"] = expanded
                        needs_snippet_update = True
                        detail["actions"].append("EXPAND_DESC")

                # NO_TAGS: Add tags
                if any("NO_TAGS" in i for i in issues):
                    if not updated_snippet["tags"]:
                        updated_snippet["tags"] = generate_tags(updated_snippet["title"])
                        needs_snippet_update = True
                        detail["actions"].append("ADD_TAGS")

                # NO_WEBSITE: Add frai.tv link
                if any("NO_WEBSITE" in i for i in issues):
                    if "frai.tv" not in updated_snippet["description"]:
                        updated_snippet["description"] = updated_snippet["description"].rstrip() + "\n\n🎬 More on FRai.TV: https://frai.tv"
                        needs_snippet_update = True
                        detail["actions"].append("ADD_WEBSITE")

                # NO_HASHTAGS: Add hashtags
                if any("NO_HASHTAGS" in i for i in issues):
                    if "#remAIke" not in updated_snippet["description"]:
                        series_tag = detect_series_hashtag(updated_snippet["title"])
                        updated_snippet["description"] = updated_snippet["description"].rstrip() + f"\n\n#remAIke #8K {series_tag}"
                        needs_snippet_update = True
                        detail["actions"].append("ADD_HASHTAGS")

                # NO_CTA: Add subscribe CTA
                if any("NO_CTA" in i for i in issues):
                    if "sub_confirmation=1" not in updated_snippet["description"]:
                        updated_snippet["description"] = updated_snippet["description"].rstrip() + CTA_BLOCK
                        needs_snippet_update = True
                        detail["actions"].append("ADD_CTA")

                # UNTRANSLATED_JA: Fix Japanese localizations
                if any("UNTRANSLATED_JA" in i for i in issues) and vid in JA_FIXES:
                    eng_event, ja_event = JA_FIXES[vid]
                    ja_loc = updated_locs.get("ja", {})
                    ja_title = ja_loc.get("title", "")
                    ja_desc = ja_loc.get("description", "")

                    if eng_event in ja_title:
                        ja_title = ja_title.replace(eng_event, ja_event)
                    if eng_event in ja_desc:
                        ja_desc = ja_desc.replace(eng_event, ja_event)

                    # If no ja loc exists, build one from the main title
                    if not ja_title:
                        ja_title = updated_snippet["title"].replace(eng_event, ja_event)
                    if not ja_desc:
                        ja_desc = updated_snippet["description"]

                    updated_locs["ja"] = {"title": ja_title, "description": ja_desc}
                    needs_loc_update = True
                    detail["actions"].append(f"FIX_JA:{eng_event}->{ja_event}")

                # LOW_LOC: Add missing localizations
                if any("LOW_LOC" in i for i in issues):
                    existing_langs = set(updated_locs.keys())
                    missing = [l for l in TARGET_LANGS if l not in existing_langs]

                    if missing:
                        for lang in missing:
                            loc_title = generate_localized_title(updated_snippet["title"], lang)
                            loc_desc = generate_localized_description(updated_snippet["description"], lang)
                            updated_locs[lang] = {"title": loc_title, "description": loc_desc}

                        needs_loc_update = True
                        detail["actions"].append(f"ADD_LOC:{','.join(missing)}")

            # ─── SEND UPDATE ───
            if needs_snippet_update or needs_loc_update:
                locs_to_send = updated_locs if needs_loc_update else None

                result = update_video(vid, updated_snippet, locs_to_send)
                report["quota_used"] += 50

                detail["status"] = "success"
                report["success"] += 1
                print(f"  [OK] Updated. Actions: {detail['actions']}")
            else:
                detail["status"] = "no_changes_needed"
                report["skipped"] += 1
                print(f"  [SKIP] No changes needed")

            # Rate limiting: ~3 requests per second max
            time.sleep(0.5)

        except Exception as e:
            detail["status"] = "error"
            detail["error"] = str(e)
            report["failed"] += 1
            print(f"  [ERROR] {e}")
            traceback.print_exc()
            time.sleep(1)

        report["details"].append(detail)

    # ─── SAVE REPORT ───
    report["completed_at"] = datetime.now().isoformat()
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"REPORT SAVED: {REPORT_PATH}")
    print(f"Total: {report['total_videos']} | Success: {report['success']} | Failed: {report['failed']} | Skipped: {report['skipped']}")
    print(f"Quota used: {report['quota_used']} units")
    print(f"{'='*60}")


def build_description(title, existing_desc):
    """Build a 200+ char description from title context."""
    # Parse title for context
    desc = existing_desc.strip() + "\n\n" if existing_desc.strip() else ""

    if "Wochenschau" in title or "wochenschau" in title:
        desc += "Deutsche Wochenschau – Historisches Filmmaterial, digital restauriert und auf 8K hochskaliert mit KI-Upscaling für maximale Bildqualität. Originalaufnahmen der UFA-Wochenschau."
    elif "Alfred J. Kwak" in title:
        desc += "Alfred J. Kwak – Die beliebte Zeichentrickserie, digital restauriert und auf 8K hochskaliert mit KI-Upscaling für maximale Bildqualität."
    else:
        desc += f"Klassiker digital restauriert und auf 8K hochskaliert mit KI-Upscaling für maximale Bildqualität. Erleben Sie historisches Filmmaterial in nie dagewesener Qualität auf remAIke_IT."

    desc += "\n\n🎬 Mehr auf FRai.TV: https://frai.tv"
    return desc


def generate_tags(title):
    """Generate 10-15 relevant tags from title."""
    tags = ["remAIke", "8K", "4K UHD", "Restauriert", "AI Upscaling", "frai.tv"]

    if "Wochenschau" in title or "wochenschau" in title:
        tags += ["Wochenschau", "Deutsche Wochenschau", "Newsreel", "WWII", "World War 2", "UFA", "History"]
    elif "Alfred J. Kwak" in title:
        tags += ["Alfred J Kwak", "Zeichentrick", "Cartoon", "Anime", "Classic Cartoon", "Animation"]
    elif "Livestream" in title:
        tags += ["Livestream", "Live", "Classic Films", "Vintage", "Public Domain"]
    else:
        # Extract words from title for tags
        words = re.findall(r'[A-Za-zÀ-ÿ]{3,}', title)
        for w in words[:6]:
            if w not in ("HQ", "UHD", "remAIke") and w not in tags:
                tags.append(w)

    return tags[:15]


if __name__ == "__main__":
    main()
