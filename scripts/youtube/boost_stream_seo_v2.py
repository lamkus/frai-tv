"""
boost_stream_seo_v2.py – Add hype emojis + fill remaining tag budget
====================================================================
Changes:
  - Title: Add ⚡ for energy + "NEW Episodes" hype signal
  - Tags: Fill up to ~490 chars (currently 366)
  - All 14 localizations: Updated with native "NEW" equivalents
"""
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

bid = '2xheXbR48Z8'

# ══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED TITLE – Emojis: 🔴 (urgency) + ⚡ (energy/new)
# Max ~100 chars. Hooks: LIVE → NEW → WWII → RESTORED → 8K → TV brand
# ══════════════════════════════════════════════════════════════════════════════
NEW_TITLE = '🔴 LIVE 24/7 ⚡ NEW | WWII Footage RESTORED in 8K Best Quality (4K UHD) | WochenschauTV'

# ══════════════════════════════════════════════════════════════════════════════
# TAGS – Fill remaining ~130 chars budget (currently 366, limit 500)
# Adding: missing high-value keywords from research
# ══════════════════════════════════════════════════════════════════════════════
TAGS = [
    # Core brand (PFLICHT)
    "remAIke", "8K", "4K UHD", "remastered", "restored",
    # Series (PFLICHT)
    "Wochenschau", "Deutsche Wochenschau", "German newsreel",
    # DE (PFLICHT)
    "Zweiter Weltkrieg", "Geschichte",
    # EN (PFLICHT) – expanded with missing high-value
    "WWII", "World War II", "WW2", "documentary", "war footage",
    "public domain", "historical footage",
    "vintage newsreel",
    # NEW high-value keywords (safe, proven)
    "war documentary",
    "history documentary",
    "free documentary",
    "8K video",
    # ES (PFLICHT)
    "Segunda Guerra Mundial",
    # PT (PFLICHT)
    "cinejornal",
    # JA (PFLICHT)
    "第二次世界大戦",
    # HI (WICHTIG)
    "द्वितीय विश्व युद्ध",
    # AR
    "الحرب العالمية الثانية",
    # ID
    "Perang Dunia II",
    # FR
    "Seconde Guerre mondiale",
    # TR
    "İkinci Dünya Savaşı",
    # KO
    "제2차 세계대전",
    # RU
    "Вторая мировая война",
]

# Deduplicate + enforce 490 char limit
seen = set()
final_tags = []
char_count = 0
for t in TAGS:
    if t.lower() not in seen:
        seen.add(t.lower())
        if char_count + len(t) <= 490:
            final_tags.append(t)
            char_count += len(t)

print(f'Tags: {len(final_tags)} ({char_count} chars / 500 limit)')

# ══════════════════════════════════════════════════════════════════════════════
# LOCALIZATIONS – Updated with ⚡ NEW + native equivalents
# ══════════════════════════════════════════════════════════════════════════════
localizations = {
    'de': {
        'title': '🔴 LIVE 24/7 ⚡ NEU | WWII Originalaufnahmen RESTAURIERT in 8K Best Quality (4K UHD) | WochenschauTV',
        'description': '🎬 Das komplette Wochenschau-Archiv – KI-restauriert in atemberaubender 8K Qualität. 24/7 Non-Stop!\nOriginalaufnahmen 1939–1945, kostenlos und gemeinfrei.\n\n⚠️ HISTORISCHES DOKUMENT – Ausschließlich für Bildungszwecke.\n\n💬 Welche Ausgabe fehlt? Kommentiert \"Nr. XXX\"!\n🔔 ABONNIERT – neue Episoden regelmäßig!\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'
    },
    'en': {
        'title': '🔴 LIVE 24/7 ⚡ NEW | WWII Footage RESTORED in 8K Best Quality (4K UHD) | WochenschauTV',
        'description': '🎬 The COMPLETE German Newsreel Archive – AI restored in stunning 8K. 24/7 Non-Stop!\nOriginal WWII footage 1939–1945, free & public domain.\n\n⚠️ HISTORICAL DOCUMENT – Educational purposes only.\n\n💬 Which episode is missing? Comment "Nr. XXX"!\n🔔 SUBSCRIBE for new episodes!\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'
    },
    'es': {
        'title': '🔴 EN VIVO 24/7 ⚡ NUEVO | WWII Imágenes RESTAURADAS en 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Archivo completo del noticiero alemán WWII – restaurado con IA en 8K. ¡24/7!\nImágenes originales 1939–1945, dominio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Solo fines educativos.\n\n💬 ¿Qué episodio falta? Comenta "Nr. XXX"!\n🔔 ¡SUSCRÍBETE!\n\n🌐 www.remaike.IT'
    },
    'pt': {
        'title': '🔴 AO VIVO 24/7 ⚡ NOVO | WWII Imagens RESTAURADAS em 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Arquivo completo do cinejornal alemão WWII – restaurado com IA em 8K. 24/7!\nImagens originais 1939–1945, domínio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Fins educacionais.\n\n💬 Qual episódio falta? Comente "Nr. XXX"!\n🔔 INSCREVA-SE!\n\n🌐 www.remaike.IT'
    },
    'fr': {
        'title': '🔴 EN DIRECT 24/7 ⚡ NOUVEAU | WWII Images RESTAURÉES en 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Archives complètes des actualités WWII – restaurées par IA en 8K. 24/7!\nImages originales 1939–1945, domaine public.\n\n⚠️ DOCUMENT HISTORIQUE – Usage éducatif.\n\n💬 Quel épisode manque? Commentez "Nr. XXX"!\n🔔 ABONNEZ-VOUS!\n\n🌐 www.remaike.IT'
    },
    'ja': {
        'title': '🔴 24時間配信 ⚡ NEW | WWII オリジナル映像 8K復元 (4K UHD) | WochenschauTV',
        'description': '🎬 ドイツ週間ニュース完全アーカイブ – AIで8K復元。24時間ノンストップ！\n1939–1945年オリジナル映像、パブリックドメイン。\n\n⚠️ 歴史的文書 – 教育目的のみ。\n\n💬 「Nr. XXX」とコメント！\n🔔 チャンネル登録！\n\n🌐 www.remaike.IT'
    },
    'hi': {
        'title': '🔴 लाइव 24/7 ⚡ नया | WWII फुटेज 8K में पुनर्स्थापित (4K UHD) | WochenschauTV',
        'description': '🎬 जर्मन न्यूज़रील का पूर्ण संग्रह – AI द्वारा 8K में पुनर्निर्मित। 24/7 नॉन-स्टॉप!\n1939–1945 मूल फुटेज, सार्वजनिक डोमेन।\n\n⚠️ ऐतिहासिक दस्तावेज़ – शैक्षिक उद्देश्य।\n\n💬 "Nr. XXX" लिखें!\n🔔 सब्सक्राइब!\n\n🌐 www.remaike.IT'
    },
    'id': {
        'title': '🔴 LIVE 24/7 ⚡ BARU | WWII Rekaman Asli DIRESTORASI 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Arsip lengkap berita Jerman WWII – direstorasi AI dalam 8K. 24/7!\nRekaman asli 1939–1945, domain publik.\n\n⚠️ DOKUMEN SEJARAH – Untuk pendidikan.\n\n💬 Episode mana yang hilang? "Nr. XXX"!\n🔔 SUBSCRIBE!\n\n🌐 www.remaike.IT'
    },
    'ar': {
        'title': '🔴 بث مباشر 24/7 ⚡ جديد | لقطات أصلية WWII بجودة 8K | WochenschauTV',
        'description': '🎬 أرشيف كامل للنشرة الألمانية WWII – مُعاد ترميمه بالذكاء الاصطناعي بجودة 8K.\n\n⚠️ وثيقة تاريخية – للأغراض التعليمية فقط.\n\n💬 "Nr. XXX" اكتب!\n🔔 اشترك!\n\n🌐 www.remaike.IT'
    },
    'tr': {
        'title': '🔴 CANLI 24/7 ⚡ YENİ | WWII Orijinal Görüntüler 8K RESTORE (4K UHD) | WochenschauTV',
        'description': '🎬 Alman haber filmlerinin tam arşivi – AI ile 8K restore. 24/7!\n1939–1945 orijinal görüntüler.\n\n⚠️ TARİHİ BELGE – Eğitim amaçlı.\n\n💬 "Nr. XXX" yazın!\n🔔 ABONE OLUN!\n\n🌐 www.remaike.IT'
    },
    'ko': {
        'title': '🔴 24시간 라이브 ⚡ NEW | WWII 원본 영상 8K 복원 (4K UHD) | WochenschauTV',
        'description': '🎬 독일 뉴스릴 완전 아카이브 – AI 8K 복원. 24시간 논스톱!\n1939–1945 원본 영상, 퍼블릭 도메인.\n\n⚠️ 역사적 문서 – 교육 목적.\n\n💬 "Nr. XXX" 댓글로!\n🔔 구독!\n\n🌐 www.remaike.IT'
    },
    'ru': {
        'title': '🔴 СТРИМ 24/7 ⚡ НОВОЕ | WWII Кадры ВОССТАНОВЛЕНЫ в 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Полный архив немецкой кинохроники – ремастеринг ИИ в 8K. 24/7!\n1939–1945 оригинальные кадры, общественное достояние.\n\n⚠️ ИСТОРИЧЕСКИЙ ДОКУМЕНТ – Образовательные цели.\n\n💬 "Nr. XXX" напишите!\n🔔 ПОДПИСЫВАЙТЕСЬ!\n\n🌐 www.remaike.IT'
    },
    'vi': {
        'title': '🔴 TRỰC TIẾP 24/7 ⚡ MỚI | WWII Hình Ảnh Gốc PHỤC HỒI 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Kho lưu trữ tin tức Đức WWII – phục chế AI 8K. 24/7!\n1939–1945 hình ảnh gốc.\n\n⚠️ TÀI LIỆU LỊCH SỬ – Giáo dục.\n\n💬 "Nr. XXX" bình luận!\n🔔 ĐĂNG KÝ!\n\n🌐 www.remaike.IT'
    },
    'zh-Hans': {
        'title': '🔴 24/7直播 ⚡ 最新 | 二战原始影像 8K修复 (4K UHD) | WochenschauTV',
        'description': '🎬 德国新闻片完整档案 – AI修复8K。24/7不间断！\n1939–1945原始影像，公共领域。\n\n⚠️ 历史文献 – 仅供教育。\n\n💬 "Nr. XXX" 评论！\n🔔 订阅！\n\n🌐 www.remaike.IT'
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# APPLY
# ══════════════════════════════════════════════════════════════════════════════

# Step 1: Broadcast title
r = yt.liveBroadcasts().list(part='snippet', id=bid).execute()
if not r.get('items'):
    print(f'ERROR: Broadcast {bid} not found!'); exit(1)

snippet = r['items'][0]['snippet']
old_title = snippet.get('title', '')
snippet['title'] = NEW_TITLE
yt.liveBroadcasts().update(part='snippet', body={'id': bid, 'snippet': snippet}).execute()
print(f'✅ Broadcast title: {NEW_TITLE}')

# Step 2: Video snippet (tags + title sync + defaultLanguage)
vr = yt.videos().list(part='snippet,localizations', id=bid).execute()
if vr.get('items'):
    vs = vr['items'][0]['snippet']
    vs['title'] = NEW_TITLE
    vs['tags'] = final_tags
    vs['categoryId'] = '27'
    vs['defaultLanguage'] = 'de'
    vs['defaultAudioLanguage'] = 'de'
    yt.videos().update(part='snippet', body={'id': bid, 'snippet': vs}).execute()
    print(f'✅ Tags: {len(final_tags)} ({char_count} chars)')
    print(f'✅ Category: 27 (Education)')

    # Step 3: Localizations
    yt.videos().update(
        part='snippet,localizations',
        body={'id': bid, 'snippet': vs, 'localizations': localizations}
    ).execute()
    print(f'✅ Localizations: {len(localizations)} languages')

print(f'\n{"="*70}')
print(f'  ⚡ BROADCAST {bid} – V2 BOOST APPLIED')
print(f'{"="*70}')
print(f'  OLD: {old_title}')
print(f'  NEW: {NEW_TITLE}')
print(f'  Tags: {len(final_tags)} ({char_count}/500 chars)')
print(f'  Localizations: {len(localizations)} with native ⚡NEW')
print(f'{"="*70}')
