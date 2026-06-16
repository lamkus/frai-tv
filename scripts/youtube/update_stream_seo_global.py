"""
update_stream_seo_global.py – Apply FULL multilingual SEO to live broadcast
==========================================================================
Uses: docs/templates/WOCHENSCHAU_MULTILINGUAL_SEO.md (14 languages)
      config/wochenschau_events.json (252 episodes)
      .github/copilot-instructions.md (channel SEO rules)

Updates:
  - Broadcast title (SEO-optimised, 8K HQ (4K UHD), no @channel)
  - Description (14 languages, community CTA, archive status)
  - Tags (multilingual, max 500 chars, top YouTube markets first)

Quota: 1× liveBroadcasts.list + 1× liveBroadcasts.update = ~50 units
"""
import json, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOKEN    = os.path.join(BASE_DIR, 'token.json')
STATE_F  = os.path.join(BASE_DIR, 'config', 'broadcast_state.json')
EVENTS_F = os.path.join(BASE_DIR, 'config', 'wochenschau_events.json')

D_DIR = os.path.join(BASE_DIR, 'wochenschau_rendered')
E_DIR = r'E:\wochenschau_rendered'

# ── Count rendered episodes ───────────────────────────────────────────────────
rendered = set()
for d in [D_DIR, E_DIR]:
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith('.mp4') and 'Nr' in f:
                try: rendered.add(int(f.split('Nr')[1].split('_')[0]))
                except: pass

with open(EVENTS_F, 'r', encoding='utf-8') as f:
    raw = json.load(f)
    events = raw.get('events', raw)
total_known = len([k for k in events if str(k).isdigit()])

with open(STATE_F) as f:
    state = json.load(f)
bid = state['broadcast_id']

# ══════════════════════════════════════════════════════════════════════════════
# SEO TITLE – per copilot-instructions.md rules:
#   Keyword first, 8K HQ (4K UHD), no @channel, max ~70 chars
# ══════════════════════════════════════════════════════════════════════════════
NEW_TITLE = 'Deutsche Wochenschau 1939–1945 | 24/7 Livestream | 8K HQ (4K UHD)'

# ══════════════════════════════════════════════════════════════════════════════
# SEO DESCRIPTION – 14 languages, community CTA, archive status
# First 2 lines = visible in YouTube search → HIGH VALUE KEYWORDS
# Per copilot-instructions: first 2 lines ≠ title, keyword-rich + context
# ══════════════════════════════════════════════════════════════════════════════
NEW_DESC = f"""🎬 Complete Deutsche Wochenschau WWII Archive – AI remastered in stunning 8K quality, streaming 24/7.
Original German newsreels 1939–1945, restored and upscaled to 4K UHD. Free historical footage, public domain.

⚠️ HISTORISCHES DOKUMENT | HISTORICAL DOCUMENT
Dieses Material dient ausschließlich der historischen Dokumentation und Bildung.
Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.
This content does NOT reflect the views of the uploader. Educational purposes only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 ARCHIV-STATUS | ARCHIVE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Currently streaming:         {len(rendered)} episodes
🔄 Full archive target:         {total_known} episodes (1939–1945)
📦 Remaining to be restored:    {total_known - len(rendered)} episodes

WE ARE BUILDING THE COMPLETE ARCHIVE!
WIR BAUEN DAS VOLLSTÄNDIGE ARCHIV AUF!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 COMMUNITY – MITMACHEN | GET INVOLVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ Which episode is missing? Comment "Nr. XXX" or a date!
📚 Historical questions or corrections? Write them below!
🔍 Looking for a specific battle or event? We prioritise your requests!

This archive lives through YOUR demand.
The more you request, the faster the next episode becomes available.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you value preserved history!
💬 COMMENT which episode you want next!
🔔 SUBSCRIBE – new episodes added regularly!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 SEARCH IN YOUR LANGUAGE | SUCHE IN DEINER SPRACHE:

🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg, Kriegsdokumentation, historisches Archiv
🇬🇧 German Newsreel, World War II, WWII documentary, vintage war footage, remastered
🇪🇸 Noticiero alemán, Segunda Guerra Mundial, documental histórico, metraje de guerra
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial, documentário histórico, imagens de guerra
🇫🇷 Actualités allemandes, Seconde Guerre mondiale, documentaire historique, archives
🇷🇺 Немецкая кинохроника, Вторая мировая война, историческая документация
🇯🇵 ドイツニュース映画, 第二次世界大戦, 歴史ドキュメンタリー, 戦争映像
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध, ऐतिहासिक वृत्तचित्र, युद्ध फुटेज
🇨🇳 德国新闻片, 二战, 第二次世界大战, 历史纪录片, 战争影像
🇸🇦 النشرة الإخبارية الألمانية, الحرب العالمية الثانية, وثائقي تاريخي
🇮🇩 Berita Jerman, Perang Dunia II, dokumenter sejarah, rekaman perang
🇻🇳 Tin tức Đức, Thế chiến thứ hai, phim tài liệu lịch sử
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı, tarihi belgesel, savaş görüntüleri
🇰🇷 독일 뉴스릴, 제2차 세계대전, 역사 다큐멘터리, 전쟁 영상

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT
🎬 Playlist: https://www.youtube.com/playlist?list=PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg

📜 Source: Public Domain (UFA/DW 1939–1945)
⚠️ Educational & Historical Documentation Only

#Wochenschau #WWII #8K #History #PublicDomain"""

# ══════════════════════════════════════════════════════════════════════════════
# TAGS – multilingual, max ~500 chars, top YouTube markets first
# Per template: Core → DE → EN → ES → PT → JA → HI → AR → ID → FR → TR
# ══════════════════════════════════════════════════════════════════════════════
TAGS_RAW = [
    # Core brand (PFLICHT)
    "remAIke", "8K", "4K UHD", "remastered", "restored",
    # Series (PFLICHT)
    "Wochenschau", "Deutsche Wochenschau", "German newsreel",
    # DE (PFLICHT)
    "Zweiter Weltkrieg", "Geschichte",
    # EN (PFLICHT)
    "WWII", "World War II", "WW2", "documentary", "war footage",
    "public domain", "historical footage",
    # ES (PFLICHT)
    "Segunda Guerra Mundial",
    # PT (PFLICHT)
    "cinejornal alemão",
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
    # Livestream
    "vintage newsreel",
]
# Deduplicate and enforce 500 char limit
seen = set()
TAGS = []
char_count = 0
for t in TAGS_RAW:
    if t.lower() not in seen:
        seen.add(t.lower())
        new_count = char_count + len(t)
        if new_count <= 490:  # safety margin
            TAGS.append(t)
            char_count = new_count

# ── Apply via API ─────────────────────────────────────────────────────────────
creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN, 'w') as f:
        f.write(creds.to_json())
yt = build('youtube', 'v3', credentials=creds)

# Fetch current snippet
r = yt.liveBroadcasts().list(part='snippet', id=bid).execute()
if not r.get('items'):
    print(f'❌ Broadcast {bid} not found!')
    exit(1)

snippet = r['items'][0]['snippet']
old_title = snippet.get('title', '')

# Update
snippet['title'] = NEW_TITLE
snippet['description'] = NEW_DESC

yt.liveBroadcasts().update(
    part='snippet',
    body={'id': bid, 'snippet': snippet}
).execute()

# Tags + defaultLanguage via video resource (broadcast ID = video ID)
try:
    vr = yt.videos().list(part='snippet,localizations', id=bid).execute()
    if vr.get('items'):
        vs = vr['items'][0]['snippet']
        vs['tags'] = TAGS
        vs['categoryId'] = '27'  # Education (per Wochenschau rules)
        vs['defaultLanguage'] = 'de'
        vs['defaultAudioLanguage'] = 'de'
        yt.videos().update(
            part='snippet',
            body={'id': bid, 'snippet': vs}
        ).execute()
        print(f'✅ Tags applied: {len(TAGS)} multilingual tags ({sum(len(t) for t in TAGS)} chars)')
        print(f'✅ Category: 27 (Education)')
        print(f'✅ Default language: de')
    else:
        print(f'⚠️  Video {bid} not found for tags')
except Exception as e:
    print(f'⚠️  Tags/language update: {e}')

# Localizations (title + description in other languages) — requires defaultLanguage set above
try:
    localizations = {
        'de': {
            'title': 'Deutsche Wochenschau 1939–1945 | 24/7 Livestream | 8K HQ (4K UHD)',
            'description': '🎬 Komplettes Wochenschau-Archiv des Zweiten Weltkriegs – KI-restauriert in 8K. Originalaufnahmen 1939–1945, kostenlos und gemeinfrei.\n\n⚠️ HISTORISCHES DOKUMENT – Ausschließlich für Bildungszwecke.\n\n💬 Welche Ausgabe fehlt? Kommentiert \"Nr. XXX\" oder ein Datum!\n🔔 ABONNIERT für regelmäßig neue Episoden!'
        },
        'en': {
            'title': 'German Newsreel WWII 1939–1945 | 24/7 Stream | 8K HQ (4K UHD)',
            'description': '🎬 Complete Deutsche Wochenschau WWII archive – AI remastered in 8K. Original 1939–1945 footage, free and public domain.\n\n⚠️ HISTORICAL DOCUMENT – Educational purposes only.\n\n💬 Which episode is missing? Comment "Nr. XXX" or a date!\n🔔 SUBSCRIBE for new episodes!'
        },
        'es': {
            'title': 'Noticiero Alemán WWII 1939–1945 | 24/7 En Vivo | 8K HQ (4K UHD)',
            'description': '🎬 Archivo completo del noticiero alemán de la Segunda Guerra Mundial – remasterizado en 8K. Imágenes originales 1939–1945, dominio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Solo con fines educativos.\n\n💬 ¿Qué episodio falta? Comenta "Nr. XXX"!\n🔔 ¡SUSCRÍBETE!'
        },
        'pt': {
            'title': 'Cinejornal Alemão WWII 1939–1945 | 24/7 Ao Vivo | 8K HQ (4K UHD)',
            'description': '🎬 Arquivo completo do cinejornal alemão da Segunda Guerra Mundial – remasterizado em 8K. Imagens originais 1939–1945, domínio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Apenas para fins educacionais.\n\n💬 Qual episódio está faltando? Comente "Nr. XXX"!\n🔔 INSCREVA-SE!'
        },
        'fr': {
            'title': 'Actualités Allemandes WWII 1939–1945 | 24/7 En Direct | 8K HQ (4K UHD)',
            'description': '🎬 Archives complètes des actualités allemandes de la Seconde Guerre mondiale – remastérisées en 8K. Images originales 1939–1945, domaine public.\n\n⚠️ DOCUMENT HISTORIQUE – Usage éducatif uniquement.\n\n💬 Quel épisode manque ? Commentez "Nr. XXX" !\n🔔 ABONNEZ-VOUS !'
        },
        'ja': {
            'title': 'ドイツ週間ニュース 1939–1945 | 24/7配信 | 8K HQ (4K UHD)',
            'description': '🎬 第二次世界大戦ドイツニュース映画の完全アーカイブ – AIで8Kリマスター。1939–1945年のオリジナル映像、パブリックドメイン。\n\n⚠️ 歴史的文書 – 教育目的のみ。\n\n💬 どのエピソードが必要？「Nr. XXX」とコメント！\n🔔 チャンネル登録！'
        },
        'hi': {
            'title': 'जर्मन न्यूज़रील WWII 1939–1945 | 24/7 लाइव | 8K HQ (4K UHD)',
            'description': '🎬 द्वितीय विश्व युद्ध के जर्मन न्यूज़रील का पूर्ण संग्रह – AI से 8K में पुनर्निर्मित। 1939–1945 की मूल फुटेज, सार्वजनिक डोमेन।\n\n⚠️ ऐतिहासिक दस्तावेज़ – केवल शैक्षिक उद्देश्यों के लिए।\n\n💬 कौन सा एपिसोड चाहिए? "Nr. XXX" लिखें!\n🔔 सब्सक्राइब करें!'
        },
        'id': {
            'title': 'Berita Jerman WWII 1939–1945 | 24/7 Siaran Langsung | 8K HQ (4K UHD)',
            'description': '🎬 Arsip lengkap berita Jerman Perang Dunia II – diremaster AI dalam 8K. Rekaman asli 1939–1945, domain publik.\n\n⚠️ DOKUMEN SEJARAH – Hanya untuk tujuan pendidikan.\n\n💬 Episode mana yang hilang? Komentar "Nr. XXX"!\n🔔 SUBSCRIBE!'
        },
        'ar': {
            'title': 'النشرة الإخبارية الألمانية 1939–1945 | بث مباشر 24/7 | 8K HQ',
            'description': '🎬 أرشيف كامل للنشرة الإخبارية الألمانية في الحرب العالمية الثانية – مُعاد ترميمه بالذكاء الاصطناعي بجودة 8K.\n\n⚠️ وثيقة تاريخية – للأغراض التعليمية فقط.\n\n💬 أي حلقة مفقودة؟ اكتب "Nr. XXX"!\n🔔 اشترك!'
        },
        'tr': {
            'title': 'Alman Haber Filmi WWII 1939–1945 | 7/24 Canlı | 8K HQ (4K UHD)',
            'description': '🎬 İkinci Dünya Savaşı Alman haber filmlerinin tam arşivi – AI ile 8K\'da yeniden düzenlenmiş. 1939–1945 orijinal görüntüler.\n\n⚠️ TARİHİ BELGE – Yalnızca eğitim amaçlı.\n\n💬 Hangi bölüm eksik? "Nr. XXX" yazın!\n🔔 ABONE OLUN!'
        },
        'ko': {
            'title': '독일 뉴스릴 WWII 1939–1945 | 24/7 라이브 | 8K HQ (4K UHD)',
            'description': '🎬 제2차 세계대전 독일 뉴스릴 완전 아카이브 – AI로 8K 리마스터링. 1939–1945 원본 영상, 퍼블릭 도메인.\n\n⚠️ 역사적 문서 – 교육 목적으로만 사용.\n\n💬 어떤 에피소드가 필요한가요? "Nr. XXX"을 댓글로!\n🔔 구독하세요!'
        },
        'ru': {
            'title': 'Немецкая кинохроника 1939–1945 | 24/7 Стрим | 8K HQ (4K UHD)',
            'description': '🎬 Полный архив немецкой кинохроники Второй мировой войны – ремастеринг ИИ в 8K. Оригинальные кадры 1939–1945, общественное достояние.\n\n⚠️ ИСТОРИЧЕСКИЙ ДОКУМЕНТ – Только в образовательных целях.\n\n💬 Какой выпуск нужен? Напишите "Nr. XXX"!\n🔔 ПОДПИСЫВАЙТЕСЬ!'
        },
        'vi': {
            'title': 'Tin tức Đức WWII 1939–1945 | Phát trực tiếp 24/7 | 8K HQ (4K UHD)',
            'description': '🎬 Kho lưu trữ đầy đủ tin tức Đức trong Thế chiến II – phục chế AI ở chất lượng 8K. Hình ảnh gốc 1939–1945.\n\n⚠️ TÀI LIỆU LỊCH SỬ – Chỉ dành cho mục đích giáo dục.\n\n💬 Tập nào còn thiếu? Bình luận "Nr. XXX"!\n🔔 ĐĂNG KÝ!'
        },
        'zh-Hans': {
            'title': '德国新闻片 1939–1945 | 24/7直播 | 8K HQ (4K UHD)',
            'description': '🎬 二战德国新闻片完整档案 – AI修复8K画质。1939–1945年原始影像，公共领域。\n\n⚠️ 历史文献 – 仅供教育目的。\n\n💬 缺少哪一集？评论 "Nr. XXX"！\n🔔 订阅频道！'
        },
    }
    yt.videos().update(
        part='localizations',
        body={'id': bid, 'localizations': localizations}
    ).execute()
    print(f'✅ Localizations: {len(localizations)} languages applied')
except Exception as e:
    print(f'⚠️  Localizations: {e}')


tag_chars = sum(len(t) for t in TAGS)
print(f'\n{"="*60}')
print(f'  BROADCAST {bid} – GLOBAL SEO APPLIED')
print(f'{"="*60}')
print(f'  Title: {NEW_TITLE}')
print(f'  Old title: {old_title}')
print(f'  Description: 14 languages, community CTA')
print(f'  Archive status: {len(rendered)}/{total_known}')
print(f'  Tags: {len(TAGS)} ({tag_chars} chars / 500 limit)')
print(f'  Localizations: DE EN ES PT FR JA HI ID AR TR KO RU VI ZH')
print(f'  Category: 27 (Education)')
print(f'  Quota used: ~150 units (list+update×3)')
print(f'{"="*60}')
