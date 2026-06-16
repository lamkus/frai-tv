"""
fix_broadcast_title_viral.py – Viral, TV-style, hype-loaded broadcast title
============================================================================
Replaces boring generic title with click-worthy, TV-branded, quality-focused title.
Updates all 14 localizations with equally viral versions.
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
# VIRAL TITLE — TV-branded, quality hook, hype-loaded
# Rules: Keyword first, 8K + 4K both present, attention-grabbing
# ══════════════════════════════════════════════════════════════════════════════
NEW_TITLE = '🔴 LIVE 24/7 | WWII Original Footage RESTORED in 8K Best Quality (4K UHD) | WochenschauTV'

# ── Viral localizations ──────────────────────────────────────────────────────
localizations = {
    'de': {
        'title': '🔴 LIVE 24/7 | WWII Originalaufnahmen RESTAURIERT in 8K Best Quality (4K UHD) | WochenschauTV',
        'description': '🎬 Das komplette Wochenschau-Archiv – KI-restauriert in atemberaubender 8K Qualität. 24/7 Non-Stop!\nOriginalaufnahmen 1939–1945, restauriert und hochskaliert für moderne Bildschirme. Kostenlos, gemeinfrei.\n\n⚠️ HISTORISCHES DOKUMENT – Ausschließlich für Bildungszwecke.\nDie dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.\n\n💬 Welche Ausgabe fehlt? Kommentiert \"Nr. XXX\"!\n🔔 ABONNIERT – neue Episoden regelmäßig!\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'
    },
    'en': {
        'title': '🔴 LIVE 24/7 | WWII Original Footage RESTORED in 8K Best Quality (4K UHD) | WochenschauTV',
        'description': '🎬 The COMPLETE German Newsreel Archive – AI restored in stunning 8K quality. 24/7 Non-Stop!\nOriginal WWII footage 1939–1945, restored and upscaled. Free, public domain.\n\n⚠️ HISTORICAL DOCUMENT – Educational purposes only.\n\n💬 Which episode is missing? Comment "Nr. XXX"!\n🔔 SUBSCRIBE for new episodes!\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'
    },
    'es': {
        'title': '🔴 EN VIVO 24/7 | WWII Imágenes Originales RESTAURADAS en 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Archivo completo del noticiero alemán – restaurado con IA en 8K. ¡24/7 sin parar!\nImágenes originales 1939–1945, dominio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Solo fines educativos.\n\n💬 ¿Qué episodio falta? Comenta "Nr. XXX"!\n🔔 ¡SUSCRÍBETE!\n\n🌐 www.remaike.IT'
    },
    'pt': {
        'title': '🔴 AO VIVO 24/7 | WWII Imagens Originais RESTAURADAS em 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Arquivo completo do cinejornal alemão – restaurado com IA em 8K. 24/7 sem parar!\nImagens originais 1939–1945, domínio público.\n\n⚠️ DOCUMENTO HISTÓRICO – Apenas para fins educacionais.\n\n💬 Qual episódio está faltando? Comente "Nr. XXX"!\n🔔 INSCREVA-SE!\n\n🌐 www.remaike.IT'
    },
    'fr': {
        'title': '🔴 EN DIRECT 24/7 | WWII Images Originales RESTAURÉES en 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Archives complètes des actualités allemandes – restaurées par IA en 8K. 24/7 non-stop!\nImages originales 1939–1945, domaine public.\n\n⚠️ DOCUMENT HISTORIQUE – Usage éducatif uniquement.\n\n💬 Quel épisode manque ? Commentez "Nr. XXX" !\n🔔 ABONNEZ-VOUS !\n\n🌐 www.remaike.IT'
    },
    'ja': {
        'title': '🔴 24時間配信 | WWII オリジナル映像 8K最高画質で復元 (4K UHD) | WochenschauTV',
        'description': '🎬 ドイツ週間ニュース完全アーカイブ – AIで8K復元。24時間ノンストップ！\n1939–1945年オリジナル映像、パブリックドメイン。\n\n⚠️ 歴史的文書 – 教育目的のみ。\n\n💬 「Nr. XXX」とコメント！\n🔔 チャンネル登録！\n\n🌐 www.remaike.IT'
    },
    'hi': {
        'title': '🔴 लाइव 24/7 | WWII मूल फुटेज 8K में पुनर्स्थापित (4K UHD) | WochenschauTV',
        'description': '🎬 जर्मन न्यूज़रील का पूर्ण संग्रह – AI द्वारा 8K में पुनर्निर्मित। 24/7 नॉन-स्टॉप!\n1939–1945 की मूल फुटेज, सार्वजनिक डोमेन।\n\n⚠️ ऐतिहासिक दस्तावेज़ – केवल शैक्षिक उद्देश्य।\n\n💬 "Nr. XXX" लिखें!\n🔔 सब्सक्राइब करें!\n\n🌐 www.remaike.IT'
    },
    'id': {
        'title': '🔴 LIVE 24/7 | WWII Rekaman Asli DIRESTORASI dalam 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Arsip lengkap berita Jerman – direstorasi AI dalam 8K. 24/7 non-stop!\nRekaman asli 1939–1945, domain publik.\n\n⚠️ DOKUMEN SEJARAH – Hanya untuk pendidikan.\n\n💬 Episode mana yang hilang? Komentar "Nr. XXX"!\n🔔 SUBSCRIBE!\n\n🌐 www.remaike.IT'
    },
    'ar': {
        'title': '🔴 بث مباشر 24/7 | لقطات أصلية من الحرب العالمية الثانية بأفضل جودة 8K | WochenschauTV',
        'description': '🎬 أرشيف كامل للنشرة الإخبارية الألمانية – مُعاد ترميمه بالذكاء الاصطناعي بجودة 8K. بث متواصل!\n\n⚠️ وثيقة تاريخية – للأغراض التعليمية فقط.\n\n💬 أي حلقة مفقودة؟ اكتب "Nr. XXX"!\n🔔 اشترك!\n\n🌐 www.remaike.IT'
    },
    'tr': {
        'title': '🔴 CANLI 24/7 | WWII Orijinal Görüntüler 8K RESTORE (4K UHD) | WochenschauTV',
        'description': '🎬 Alman haber filmlerinin tam arşivi – AI ile 8K\'da restore edilmiş. 24/7 kesintisiz!\n1939–1945 orijinal görüntüler.\n\n⚠️ TARİHİ BELGE – Yalnızca eğitim amaçlı.\n\n💬 "Nr. XXX" yazın!\n🔔 ABONE OLUN!\n\n🌐 www.remaike.IT'
    },
    'ko': {
        'title': '🔴 24시간 라이브 | WWII 원본 영상 8K 최고 화질로 복원 (4K UHD) | WochenschauTV',
        'description': '🎬 독일 뉴스릴 완전 아카이브 – AI로 8K 복원. 24시간 논스톱!\n1939–1945 원본 영상, 퍼블릭 도메인.\n\n⚠️ 역사적 문서 – 교육 목적만.\n\n💬 "Nr. XXX" 댓글로!\n🔔 구독하세요!\n\n🌐 www.remaike.IT'
    },
    'ru': {
        'title': '🔴 СТРИМ 24/7 | WWII Оригинальные Кадры ВОССТАНОВЛЕНЫ в 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Полный архив немецкой кинохроники – ремастеринг ИИ в 8K. 24/7 без остановки!\n1939–1945 оригинальные кадры, общественное достояние.\n\n⚠️ ИСТОРИЧЕСКИЙ ДОКУМЕНТ – Только в образовательных целях.\n\n💬 Напишите "Nr. XXX"!\n🔔 ПОДПИСЫВАЙТЕСЬ!\n\n🌐 www.remaike.IT'
    },
    'vi': {
        'title': '🔴 TRỰC TIẾP 24/7 | WWII Hình Ảnh Gốc PHỤC HỒI 8K (4K UHD) | WochenschauTV',
        'description': '🎬 Kho lưu trữ đầy đủ tin tức Đức – phục chế AI ở 8K. 24/7 không ngừng!\n1939–1945 hình ảnh gốc.\n\n⚠️ TÀI LIỆU LỊCH SỬ – Chỉ dành cho giáo dục.\n\n💬 "Nr. XXX" bình luận!\n🔔 ĐĂNG KÝ!\n\n🌐 www.remaike.IT'
    },
    'zh-Hans': {
        'title': '🔴 24/7直播 | 二战原始影像 8K最佳画质修复 (4K UHD) | WochenschauTV',
        'description': '🎬 德国新闻片完整档案 – AI修复8K画质。24/7不间断！\n1939–1945年原始影像，公共领域。\n\n⚠️ 历史文献 – 仅供教育目的。\n\n💬 评论 "Nr. XXX"！\n🔔 订阅频道！\n\n🌐 www.remaike.IT'
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: Update broadcast snippet (title + description stays as-is)
# ══════════════════════════════════════════════════════════════════════════════
r = yt.liveBroadcasts().list(part='snippet', id=bid).execute()
if not r.get('items'):
    print(f'❌ Broadcast {bid} not found!'); exit(1)

snippet = r['items'][0]['snippet']
old_title = snippet.get('title', '')
snippet['title'] = NEW_TITLE

yt.liveBroadcasts().update(
    part='snippet',
    body={'id': bid, 'snippet': snippet}
).execute()
print(f'✅ Broadcast title updated')
print(f'   OLD: {old_title}')
print(f'   NEW: {NEW_TITLE}')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: Update video snippet (title for video resource too) + localizations
# ══════════════════════════════════════════════════════════════════════════════
vr = yt.videos().list(part='snippet,localizations', id=bid).execute()
if vr.get('items'):
    vs = vr['items'][0]['snippet']
    vs['title'] = NEW_TITLE  # Sync video title with broadcast
    yt.videos().update(part='snippet', body={'id': bid, 'snippet': vs}).execute()
    print(f'✅ Video title synced')

    # Apply localizations — must include snippet with defaultLanguage
    vr2 = yt.videos().list(part='snippet,localizations', id=bid).execute()
    vs2 = vr2['items'][0]['snippet']
    vs2['defaultLanguage'] = 'de'
    yt.videos().update(
        part='snippet,localizations',
        body={'id': bid, 'snippet': vs2, 'localizations': localizations}
    ).execute()
    print(f'✅ Localizations: {len(localizations)} viral titles applied')

print(f'\n{"="*70}')
print(f'  🔴 BROADCAST {bid} – VIRAL TITLE APPLIED')
print(f'{"="*70}')
print(f'  NEW: {NEW_TITLE}')
print()
print(f'  Hooks used:')
print(f'    🔴 LIVE 24/7    → Red dot = urgency/attention')
print(f'    RESTORED        → Quality narrative, trend keyword')
print(f'    8K Best Quality → Quality superlative')
print(f'    (4K UHD)        → Search keyword coverage')
print(f'    WochenschauTV   → TV branding = channel identity')
print(f'    WWII Original   → Authenticity hook')
print(f'{"="*70}')
