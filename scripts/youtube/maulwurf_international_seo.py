"""
Maulwurf International SEO Update — Proper Research-Based Fix
============================================================
- Replaces generic titles with researched episode-specific titles
- Adds Krtek (THE international search keyword) to every title
- Adds episode numbering (E03-E63)
- Creates multilingual descriptions (DE/EN/CZ/JP/CN/ES/FR/RU/KO/PL)
- Sets proper localizations for 5+ languages
- Sets correct tags with multilingual keywords
- Follows ALL remAIke SEO rules (2026 algo)

Cost: ~12 reads (12 units) + 12 writes (600 units) = 612 units
"""
import os, json, time, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

os.chdir(r'D:\remaike.TV')
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_yt():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

# Load database
with open('config/maulwurf_complete_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

series = db['series_info']
videos = db['our_videos']

youtube = get_yt()
quota_used = 0
updated = 0
errors = []

def build_description(vid):
    """Build the PERFECT multilingual description for a Maulwurf episode."""
    t = vid['titles']
    ep = vid['ep_num']
    year = vid['year']
    dur = vid['duration']
    composer = vid['composer']
    vtype = vid['type']
    
    # Episode label
    if ep:
        ep_label_de = f"Folge {ep} von 63"
        ep_label_en = f"Episode {ep} of 63"
    else:
        ep_label_de = "Zusammenstellung"
        ep_label_en = "Compilation"
    
    # Type label
    type_labels = {
        'short': 'Kurzfilm',
        'feature': 'Spielfilm',
        'clip': 'Clip',
        'compilation': 'Zusammenstellung'
    }
    type_label = type_labels.get(vtype, 'Kurzfilm')
    
    # Composer info
    composer_line = f"🎵 {composer}" if composer else ""
    year_line = f"📅 {year}" if year else ""
    dur_line = f"⏱️ {dur}" if dur else ""
    
    desc = f"""{t['cs']} | {t['de']} | {t['en']}
Krtek (Der kleine Maulwurf / The Little Mole) in höchster 8K Qualität – AI Remastered von remAIke.TV! Die weltweit berühmte tschechische Zeichentrickserie von Zdeněk Miler, ausgestrahlt in über 80 Ländern.

🌍 INTERNATIONAL TITLES:
🇨🇿 {t['cs']} | 🇩🇪 {t['de']} | 🇬🇧 {t['en']}
🇯🇵 {t['ja']} | 🇨🇳 {t['zh']} | 🇪🇸 {t['es']}
🇫🇷 {t['fr']} | 🇷🇺 {t['ru']} | 🇰🇷 {t['ko']} | 🇵🇱 {t['pl']}

📺 Der kleine Maulwurf (Krteček) | {ep_label_de}
🎬 Zdeněk Miler | {composer_line} | {year_line} | 🇨🇿 Krátký Film Praha
{dur_line} | Qualität: 8K HQ (4K UHD) – Höchste Qualität weltweit!

Der kleine Maulwurf (tschechisch: Krtek/Krteček, クルテク, 鼹鼠的故事) ist eine der bekanntesten und beliebtesten Zeichentrickserien der Welt. Erschaffen 1957 von Zdeněk Miler in Prag, gewann der erste Film den Silbernen Löwen in Venedig. Die Serie wurde in über 80 Ländern ausgestrahlt – darunter Deutschland (Die Sendung mit der Maus), Japan, China, Russland und ganz Osteuropa. Der Maulwurf spricht fast nie – damit ihn Kinder auf der ganzen Welt verstehen können. Er flog sogar mit dem Space Shuttle Endeavour (STS-134, 2011) und der Sojus MS-08 (2018) ins All!

The Little Mole (Czech: Krtek/Krteček, Japanese: クルテク) is one of the world's most beloved cartoon characters, created by Zdeněk Miler in Prague in 1957. Winner of the Silver Lion at the Venice Film Festival. Broadcast in 80+ countries. The mole rarely speaks – so children everywhere can understand. This is the HIGHEST QUALITY version available anywhere: AI-enhanced 8K!

🕐 CHAPTERS:
0:00 {t['de']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you love Krtek!
💬 COMMENT: What's your favorite Maulwurf episode?
🔔 SUBSCRIBE for more 8K vintage cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krtek #DerKleineMaulwurf #8K #ZdenekMiler #CzechAnimation"""
    
    return desc.strip()


def build_localization(vid, lang):
    """Build localized title and description for a specific language."""
    t = vid['titles']
    ep = vid['ep_num']
    year = vid['year']
    vtype = vid['type']
    
    if lang == 'en':
        if ep and vtype == 'clip':
            title = f"Krtek Clip: {t['en']} ({year}) | 8K HQ"
        elif ep:
            title = f"Krtek E{ep:02d}: {t['en']} ({year}) | 8K HQ"
        else:
            title = f"Krtek: {t['en']} | 8K HQ"
        desc = f"""{t['en']} | {t['cs']} | Krtek / The Little Mole
The world-famous Czech animated series by Zdeněk Miler in the highest possible quality: 8K AI Remastered!

Loved in 80+ countries. The Little Mole rarely speaks – so children everywhere can understand.
This is the BEST QUALITY version of Krtek available anywhere on the internet!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krtek #TheLittleMole #8K #CzechAnimation #ZdenekMiler"""

    elif lang == 'cs':
        if ep and vtype == 'clip':
            title = f"Krtek (klip): {t['cs']} ({year}) | 8K HQ"
        elif ep:
            title = f"Krtek E{ep:02d}: {t['cs']} ({year}) | 8K HQ"
        else:
            title = f"Krtek: {t['cs']} | 8K HQ"
        desc = f"""{t['cs']} | Krteček / Der kleine Maulwurf / The Little Mole
Slavný český animovaný seriál Zdeňka Milera v nejvyšší možné kvalitě: 8K AI Remastered!

Vysíláno v 80+ zemích světa. Toto je NEJLEPŠÍ kvalita Krtka dostupná kdekoli na internetu!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krtek #Krteček #8K #ZdeněkMiler #ČeskáAnimace"""

    elif lang == 'ja':
        if ep and vtype == 'clip':
            title = f"クルテク (クリップ): {t['ja']} ({year}) | 8K"
        elif ep:
            title = f"クルテク E{ep:02d}: {t['ja']} ({year}) | 8K"
        else:
            title = f"クルテク: {t['ja']} | 8K"
        desc = f"""{t['ja']} | Krtek / クルテク / もぐらくん
チェコの名作アニメーション、ズデニェク・ミレル作。世界80カ国以上で放送。
AI技術で8Kにリマスター – インターネット上で最高画質のクルテク！

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#クルテク #もぐらくん #8K #チェコアニメ #ZdenekMiler"""

    elif lang == 'zh':
        if ep and vtype == 'clip':
            title = f"鼹鼠的故事 (短片): {t['zh']} ({year}) | 8K"
        elif ep:
            title = f"鼹鼠的故事 E{ep:02d}: {t['zh']} ({year}) | 8K"
        else:
            title = f"鼹鼠的故事: {t['zh']} | 8K"
        desc = f"""{t['zh']} | Krtek / 鼹鼠的故事 / 小鼹鼠
捷克经典动画系列，兹德涅克·米勒创作。在全球80多个国家播出。
AI技术重制8K画质 – 互联网上最高画质的小鼹鼠！

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#鼹鼠的故事 #小鼹鼠 #8K #捷克动画 #ZdenekMiler"""

    elif lang == 'es':
        if ep and vtype == 'clip':
            title = f"Krtek (Clip): {t['es']} ({year}) | 8K HQ"
        elif ep:
            title = f"Krtek E{ep:02d}: {t['es']} ({year}) | 8K HQ"
        else:
            title = f"Krtek: {t['es']} | 8K HQ"
        desc = f"""{t['es']} | Krtek / El pequeño Topo / The Little Mole
La famosa serie de animación checa de Zdeněk Miler en la más alta calidad: ¡8K AI Remastered!

Emitida en más de 80 países. ¡La MEJOR calidad de Krtek disponible en internet!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krtek #ElPequeñoTopo #8K #AnimaciónCheca #ZdenekMiler"""

    elif lang == 'fr':
        if ep and vtype == 'clip':
            title = f"Krtek (Clip): {t['fr']} ({year}) | 8K HQ"
        elif ep:
            title = f"Krtek E{ep:02d}: {t['fr']} ({year}) | 8K HQ"
        else:
            title = f"Krtek: {t['fr']} | 8K HQ"
        desc = f"""{t['fr']} | Krtek / La Petite Taupe / The Little Mole
La célèbre série d'animation tchèque de Zdeněk Miler en qualité maximale : 8K AI Remastered !

Diffusée dans plus de 80 pays. La MEILLEURE qualité de Krtek disponible sur internet !

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krtek #LaPetiteTaupe #8K #AnimationTchèque #ZdenekMiler"""

    elif lang == 'ru':
        if ep and vtype == 'clip':
            title = f"Кротик (клип): {t['ru']} ({year}) | 8K"
        elif ep:
            title = f"Кротик E{ep:02d}: {t['ru']} ({year}) | 8K"
        else:
            title = f"Кротик: {t['ru']} | 8K"
        desc = f"""{t['ru']} | Krtek / Кротик / The Little Mole
Знаменитый чешский мультсериал Зденека Милера в максимальном качестве: 8K AI Remastered!

Показан в 80+ странах. ЛУЧШЕЕ качество Кротика в интернете!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Кротик #Krtek #8K #ЧешскаяАнимация #ZdenekMiler"""

    elif lang == 'ko':
        if ep and vtype == 'clip':
            title = f"크르텍 (클립): {t['ko']} ({year}) | 8K"
        elif ep:
            title = f"크르텍 E{ep:02d}: {t['ko']} ({year}) | 8K"
        else:
            title = f"크르텍: {t['ko']} | 8K"
        desc = f"""{t['ko']} | Krtek / 크르텍 / The Little Mole
유명한 체코 애니메이션 시리즈, 즈데녜크 밀레르 제작. 80개국 이상에서 방영.
AI 기술로 8K 리마스터링 – 인터넷에서 최고 화질의 크르텍!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#크르텍 #Krtek #8K #체코애니메이션 #ZdenekMiler"""

    elif lang == 'pl':
        if ep and vtype == 'clip':
            title = f"Krecik (klip): {t['pl']} ({year}) | 8K"
        elif ep:
            title = f"Krecik E{ep:02d}: {t['pl']} ({year}) | 8K"
        else:
            title = f"Krecik: {t['pl']} | 8K"
        desc = f"""{t['pl']} | Krtek / Krecik / The Little Mole
Słynny czeski serial animowany Zdeňka Milera w najwyższej jakości: 8K AI Remastered!

Emitowany w ponad 80 krajach. NAJLEPSZA jakość Krecika dostępna w internecie!

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Krecik #Krtek #8K #CzeskaAnimacja #ZdenekMiler"""
    
    else:
        return None
    
    return {'title': title[:100], 'description': desc.strip()}


def update_video(vid):
    """Apply the complete international SEO update for one Maulwurf video."""
    global quota_used, updated
    
    vid_id = vid['video_id']
    
    # Read current state
    res = youtube.videos().list(part="snippet,localizations", id=vid_id).execute()
    quota_used += 1
    
    if not res['items']:
        print(f"  ⏩ {vid_id} — not found")
        return
    
    item = res['items'][0]
    snippet = item['snippet']
    old_title = snippet['title']
    
    # New title
    new_title = vid['yt_title']
    
    # New description
    new_desc = build_description(vid)
    
    # New tags
    new_tags = vid['tags']
    
    # Apply to snippet
    snippet['title'] = new_title
    snippet['description'] = new_desc
    snippet['tags'] = new_tags
    snippet['defaultLanguage'] = 'de'
    
    # Build localizations (9 languages!)
    localizations = {}
    for lang in ['en', 'cs', 'ja', 'zh', 'es', 'fr', 'ru', 'ko', 'pl']:
        loc = build_localization(vid, lang)
        if loc:
            localizations[lang] = loc
    
    # Also add DE localization (same as default)
    localizations['de'] = {
        'title': new_title,
        'description': new_desc
    }
    
    # Write update
    body = {
        'id': vid_id,
        'snippet': snippet,
        'localizations': localizations
    }
    
    youtube.videos().update(part="snippet,localizations", body=body).execute()
    quota_used += 50
    updated += 1
    
    print(f"  ✅ [{quota_used:>4}q] {old_title[:35]}")
    print(f"       → {new_title}")
    print(f"       → 10 localizations (DE/EN/CS/JA/ZH/ES/FR/RU/KO/PL)")


# ═══════════════════════════════════════════════════════════
# EXECUTE
# ═══════════════════════════════════════════════════════════

print("═" * 65)
print("  MAULWURF INTERNATIONAL SEO UPDATE")
print("  12 videos × 10 languages × researched episode data")
print("═" * 65)
print(f"  Database: {len(db['complete_episode_list'])} episodes mapped")
print(f"  Our videos: {len(videos)} to update")
print(f"  Languages: DE, EN, CS, JA, ZH, ES, FR, RU, KO, PL")
print(f"  Estimated quota: ~612 units")
print("═" * 65)

for vid in videos:
    try:
        update_video(vid)
        time.sleep(0.5)
    except Exception as e:
        if 'quotaExceeded' in str(e):
            print(f"\n🛑 QUOTA EXCEEDED at {quota_used} units!")
            sys.exit(1)
        errors.append({'id': vid['video_id'], 'error': str(e)})
        print(f"  ❌ {vid['video_id']}: {e}")

print(f"\n{'═' * 65}")
print(f"  COMPLETE")
print(f"{'═' * 65}")
print(f"  Updated:   {updated} / {len(videos)}")
print(f"  Errors:    {len(errors)}")
print(f"  Quota:     {quota_used} units")
print(f"  Languages: 10 per video")

if errors:
    print(f"\n  Errors:")
    for e in errors:
        print(f"    {e['id']}: {e['error'][:80]}")

# Save report
report = {
    'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    'videos_updated': updated,
    'languages': ['de', 'en', 'cs', 'ja', 'zh', 'es', 'fr', 'ru', 'ko', 'pl'],
    'quota_used': quota_used,
    'errors': errors,
    'details': [{'video_id': v['video_id'], 'title': v['yt_title'], 'ep_num': v['ep_num']} for v in videos]
}
with open('config/maulwurf_seo_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n  Report: config/maulwurf_seo_report.json")
