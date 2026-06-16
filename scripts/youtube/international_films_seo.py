"""
International SEO Fix — Silent Films, Classics & Other Public Domain
====================================================================
Research-based multilingual SEO for our internationally relevant content:
- Silent Films: Nosferatu, Metropolis, Phantom, Häxan, Blackmail, Méliès
- Classic Cartoons: Skeleton Dance, Porky Pig, Looney Tunes, Fleischer
- Documentaries: Hindenburg, Pearl Harbor, Skylab/NASA  
- Other: Reefer Madness, Boxing Cats, Glücksbärchis, Clever & Smart

Each gets:
- Proper English-first/bilingual title (these are international content!)
- Multilingual localizations (DE, EN, ES, FR, JA, PT, RU)
- Proper tags with international keywords
- CTA + links in description
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

youtube = get_yt()
quota_used = 0
updated = 0
errors = []

CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this classic!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more 8K restorations!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

# ═══════════════════════════════════════════════════════════
# FILM DATABASE — Researched from Wikipedia + IMDB
# ═══════════════════════════════════════════════════════════

films = [
    # ── SILENT FILM MASTERPIECES ──
    {
        "id": "Nzi6aRKDoEs",
        "title": "Nosferatu (1922) | F.W. Murnau | Silent Horror | 8K HQ",
        "desc_intro": "Nosferatu – Eine Symphonie des Grauens (1922)\nDirector: F.W. Murnau | Stars: Max Schreck, Gustav von Wangenheim\nThe first vampire film ever made – an unauthorized adaptation of Bram Stoker's Dracula.\nAI Remastered in 8K by remAIke.TV – the HIGHEST QUALITY version on the internet!",
        "tags": ["Nosferatu", "F.W. Murnau", "Max Schreck", "Silent Film", "Horror", "8K", "Stummfilm", "Vampire", "1922", "German Expressionism", "Public Domain", "Dracula", "Remastered", "Classic Horror", "4K UHD"],
        "localizations": {
            "de": {"title": "Nosferatu (1922) | F.W. Murnau | Stummfilm Horror | 8K HQ"},
            "en": {"title": "Nosferatu (1922) | F.W. Murnau | Silent Horror | 8K HQ"},
            "ja": {"title": "ノスフェラトゥ (1922) | サイレントホラー | 8K HQ"},
            "es": {"title": "Nosferatu (1922) | F.W. Murnau | Cine Mudo | 8K HQ"},
            "fr": {"title": "Nosferatu (1922) | F.W. Murnau | Film Muet | 8K HQ"},
            "pt": {"title": "Nosferatu (1922) | F.W. Murnau | Cinema Mudo | 8K HQ"},
            "ru": {"title": "Носферату (1922) | Ф.В. Мурнау | Немое кино | 8K HQ"},
            "ko": {"title": "노스페라투 (1922) | 무성 공포영화 | 8K HQ"},
            "zh": {"title": "诺斯费拉图 (1922) | 默片恐怖 | 8K HQ"}
        },
        "hashtags": "#Nosferatu #SilentFilm #Horror #8K #FWMurnau"
    },
    {
        "id": "8lLtNb11NKU",
        "title": "Metropolis (1927) | Fritz Lang | Sci-Fi Masterpiece | 8K HQ",
        "desc_intro": "Metropolis (1927)\nDirector: Fritz Lang | Stars: Brigitte Helm, Alfred Abel, Gustav Fröhlich\nThe most influential science fiction film of all time. A dystopian masterpiece of German Expressionism.\nAI Remastered in 8K by remAIke.TV – the HIGHEST QUALITY version on the internet!",
        "tags": ["Metropolis", "Fritz Lang", "Brigitte Helm", "Silent Film", "Sci-Fi", "8K", "Stummfilm", "Science Fiction", "1927", "German Expressionism", "Public Domain", "Dystopia", "Remastered", "Classic Cinema", "4K UHD"],
        "localizations": {
            "de": {"title": "Metropolis (1927) | Fritz Lang | Sci-Fi Meisterwerk | 8K HQ"},
            "en": {"title": "Metropolis (1927) | Fritz Lang | Sci-Fi Masterpiece | 8K HQ"},
            "ja": {"title": "メトロポリス (1927) | フリッツ・ラング | SF映画 | 8K HQ"},
            "es": {"title": "Metrópolis (1927) | Fritz Lang | Ciencia Ficción | 8K HQ"},
            "fr": {"title": "Metropolis (1927) | Fritz Lang | Science-Fiction | 8K HQ"},
            "pt": {"title": "Metrópolis (1927) | Fritz Lang | Ficção Científica | 8K HQ"},
            "ru": {"title": "Метрополис (1927) | Фриц Ланг | Научная фантастика | 8K"},
            "ko": {"title": "메트로폴리스 (1927) | 프리츠 랑 | SF 영화 | 8K HQ"},
            "zh": {"title": "大都会 (1927) | 弗里茨·朗 | 科幻经典 | 8K HQ"}
        },
        "hashtags": "#Metropolis #FritzLang #SilentFilm #8K #SciFi"
    },
    {
        "id": "b4cqLlJ7t4M",
        "title": "Phantom of the Opera (1925) | Lon Chaney | Silent | 8K HQ",
        "desc_intro": "The Phantom of the Opera (1925)\nDirector: Rupert Julian | Star: Lon Chaney ('Man of a Thousand Faces')\nThe original horror masterpiece. Chaney's self-designed makeup remains iconic 100 years later.\nAI Remastered in 8K by remAIke.TV – the HIGHEST QUALITY version on the internet!",
        "tags": ["Phantom of the Opera", "Lon Chaney", "Silent Film", "Horror", "8K", "1925", "Classic Horror", "Public Domain", "Das Phantom der Oper", "Remastered", "Universal Monsters", "Stummfilm", "4K UHD", "Opera", "Gothic"],
        "localizations": {
            "de": {"title": "Das Phantom der Oper (1925) | Lon Chaney | Stummfilm | 8K HQ"},
            "en": {"title": "Phantom of the Opera (1925) | Lon Chaney | Silent | 8K HQ"},
            "ja": {"title": "オペラ座の怪人 (1925) | ロン・チェイニー | 8K HQ"},
            "es": {"title": "El Fantasma de la Ópera (1925) | Lon Chaney | 8K HQ"},
            "fr": {"title": "Le Fantôme de l'Opéra (1925) | Lon Chaney | 8K HQ"},
            "pt": {"title": "O Fantasma da Ópera (1925) | Lon Chaney | 8K HQ"},
            "ru": {"title": "Призрак оперы (1925) | Лон Чейни | Немое кино | 8K HQ"},
            "ko": {"title": "오페라의 유령 (1925) | 론 채니 | 무성영화 | 8K HQ"},
            "zh": {"title": "歌剧魅影 (1925) | 朗·钱尼 | 默片 | 8K HQ"}
        },
        "hashtags": "#PhantomOfTheOpera #LonChaney #SilentFilm #8K #Horror"
    },
    {
        "id": "exukLdxugy8",
        "title": "Häxan (1922) | Witchcraft Through the Ages | 8K HQ",
        "desc_intro": "Häxan – Witchcraft Through the Ages / Die Hexe (1922)\nDirector: Benjamin Christensen | Swedish-Danish silent horror documentary\nOne of the most remarkable films ever made – a visual essay on witchcraft, superstition and hysteria.\nAI Remastered in 8K by remAIke.TV – the HIGHEST QUALITY version on the internet!",
        "tags": ["Häxan", "Haxan", "Witchcraft", "Silent Film", "Horror", "8K", "1922", "Benjamin Christensen", "Documentary", "Public Domain", "Die Hexe", "Hexerei", "Remastered", "Classic Horror", "4K UHD"],
        "localizations": {
            "de": {"title": "Häxan – Hexerei im Wandel der Zeiten (1922) | 8K HQ"},
            "en": {"title": "Häxan – Witchcraft Through the Ages (1922) | 8K HQ"},
            "ja": {"title": "魔女 (1922) | 時代を超えた魔術 | 8K HQ"},
            "es": {"title": "Häxan – La Brujería a Través de los Tiempos (1922) | 8K HQ"},
            "fr": {"title": "Häxan – La Sorcellerie à Travers les Âges (1922) | 8K HQ"},
            "pt": {"title": "Häxan – Feitiçaria Através dos Tempos (1922) | 8K HQ"},
            "ru": {"title": "Ведьмы (1922) | Колдовство сквозь века | 8K HQ"},
            "ko": {"title": "핵산 (1922) | 시대를 초월한 마법 | 8K HQ"},
            "zh": {"title": "女巫 (1922) | 历代巫术 | 8K HQ"}
        },
        "hashtags": "#Häxan #Witchcraft #SilentFilm #8K #Horror"
    },
    {
        "id": "HCj_w3pBxlc",
        "title": "Blackmail (1929) | Hitchcock's First Talkie | 8K HQ",
        "desc_intro": "Blackmail (1929) – Erpressung\nDirector: Alfred Hitchcock | Stars: Anny Ondra, John Longden\nHitchcock's first sound film and the first British 'talkie'. A thriller about a woman who kills her assailant in self-defense.\nAI Remastered in 8K by remAIke.TV!",
        "tags": ["Blackmail", "Alfred Hitchcock", "1929", "8K", "British Film", "Thriller", "Anny Ondra", "Silent Film", "Talkie", "Public Domain", "Erpressung", "Classic Cinema", "Remastered", "Suspense", "4K UHD"],
        "localizations": {
            "de": {"title": "Erpressung (1929) | Hitchcocks erster Tonfilm | 8K HQ"},
            "en": {"title": "Blackmail (1929) | Hitchcock's First Talkie | 8K HQ"},
            "ja": {"title": "恐喝 (1929) | ヒッチコック初のトーキー | 8K HQ"},
            "es": {"title": "Chantaje (1929) | El Primer Sonoro de Hitchcock | 8K HQ"},
            "fr": {"title": "Chantage (1929) | Le Premier Film Parlant de Hitchcock | 8K HQ"},
            "pt": {"title": "Chantagem (1929) | O Primeiro Filme Falado de Hitchcock | 8K HQ"},
            "ru": {"title": "Шантаж (1929) | Первый звуковой фильм Хичкока | 8K"},
            "ko": {"title": "공갈 (1929) | 히치콕 첫 유성영화 | 8K HQ"},
            "zh": {"title": "讹诈 (1929) | 希区柯克首部有声电影 | 8K HQ"}
        },
        "hashtags": "#Blackmail #Hitchcock #8K #ClassicCinema #Thriller"
    },
    {
        "id": "tk3DHvp9CFs",
        "title": "The Astronomer's Dream (1898) | Georges Méliès | 8K HQ",
        "desc_intro": "La Lune à un mètre / The Astronomer's Dream (1898)\nDirector: Georges Méliès | One of the earliest science fiction films ever made.\nMéliès was a pioneer of special effects and the father of cinematic fantasy.\nAI Remastered in 8K by remAIke.TV!",
        "tags": ["Georges Méliès", "Astronomer's Dream", "1898", "8K", "Silent Film", "Sci-Fi", "Early Cinema", "Public Domain", "La Lune", "Special Effects", "Pioneer", "Classic Cinema", "Remastered", "Fantasy", "4K UHD"],
        "localizations": {
            "de": {"title": "Der Traum des Astronomen (1898) | Georges Méliès | 8K HQ"},
            "en": {"title": "The Astronomer's Dream (1898) | Georges Méliès | 8K HQ"},
            "ja": {"title": "天文学者の夢 (1898) | ジョルジュ・メリエス | 8K HQ"},
            "es": {"title": "El Sueño del Astrónomo (1898) | Georges Méliès | 8K HQ"},
            "fr": {"title": "La Lune à un mètre (1898) | Georges Méliès | 8K HQ"},
            "pt": {"title": "O Sonho do Astrônomo (1898) | Georges Méliès | 8K HQ"},
            "ru": {"title": "Мечта астронома (1898) | Жорж Мельес | 8K HQ"},
            "ko": {"title": "천문학자의 꿈 (1898) | 조르주 멜리에스 | 8K HQ"},
            "zh": {"title": "天文学家之梦 (1898) | 乔治·梅里爱 | 8K HQ"}
        },
        "hashtags": "#GeorgesMéliès #SilentFilm #EarlyCinema #8K #SciFi"
    },
    
    # ── DISNEY / SKELETON DANCE ──
    {
        "id": "TLdsnAi8bWg",
        "title": "Silly Symphony: The Skeleton Dance (1929) | Disney | 8K HQ",
        "desc_intro": "Silly Symphony: The Skeleton Dance (1929)\nDirected by: Walt Disney | Music: Carl Stalling\nThe very first Silly Symphony – a revolutionary animated short featuring dancing skeletons.\nPublic Domain classic. AI Remastered in 8K by remAIke.TV!",
        "tags": ["Silly Symphony", "Skeleton Dance", "Walt Disney", "1929", "8K", "Animation", "Halloween", "Public Domain", "Carl Stalling", "Classic Cartoon", "Remastered", "Dancing Skeletons", "Vintage Animation", "4K UHD", "Disney"],
        "localizations": {
            "de": {"title": "Silly Symphony: Der Skelett-Tanz (1929) | Disney | 8K HQ"},
            "en": {"title": "Silly Symphony: The Skeleton Dance (1929) | Disney | 8K HQ"},
            "ja": {"title": "シリー・シンフォニー: 骸骨の踊り (1929) | ディズニー | 8K"},
            "es": {"title": "Silly Symphony: La Danza de los Esqueletos (1929) | 8K HQ"},
            "fr": {"title": "Silly Symphony: La Danse des Squelettes (1929) | 8K HQ"},
            "pt": {"title": "Silly Symphony: A Dança dos Esqueletos (1929) | 8K HQ"},
            "ru": {"title": "Танец скелетов (1929) | Уолт Дисней | 8K HQ"},
            "ko": {"title": "실리 심포니: 해골의 춤 (1929) | 디즈니 | 8K HQ"},
            "zh": {"title": "糊涂交响曲: 骷髅之舞 (1929) | 迪士尼 | 8K HQ"}
        },
        "hashtags": "#SkeletonDance #Disney #SillySymphony #8K #Halloween"
    },
    
    # ── DOCUMENTARIES ──
    {
        "id": "eF81rBeXbzk",
        "title": "Hindenburg Disaster (1937) | Full Documentary | 8K HQ",
        "desc_intro": "The Hindenburg Disaster – May 6, 1937, Lakehurst, New Jersey\nThe most famous airship disaster in history. 'Oh, the humanity!' – Herbert Morrison's live radio broadcast.\nOriginal newsreel footage AI Remastered in 8K by remAIke.TV!",
        "tags": ["Hindenburg", "Disaster", "1937", "8K", "Airship", "Zeppelin", "Documentary", "Public Domain", "Lakehurst", "Oh the Humanity", "Newsreel", "History", "Remastered", "LZ 129", "4K UHD"],
        "localizations": {
            "de": {"title": "Hindenburg Katastrophe (1937) | Dokumentation | 8K HQ"},
            "en": {"title": "Hindenburg Disaster (1937) | Full Documentary | 8K HQ"},
            "ja": {"title": "ヒンデンブルク号の惨事 (1937) | ドキュメンタリー | 8K"},
            "es": {"title": "Desastre del Hindenburg (1937) | Documental | 8K HQ"},
            "fr": {"title": "Catastrophe du Hindenburg (1937) | Documentaire | 8K HQ"},
            "pt": {"title": "Desastre do Hindenburg (1937) | Documentário | 8K HQ"},
            "ru": {"title": "Катастрофа Гинденбурга (1937) | Документальный | 8K"},
            "ko": {"title": "힌덴부르크 참사 (1937) | 다큐멘터리 | 8K HQ"},
            "zh": {"title": "兴登堡号灾难 (1937) | 纪录片 | 8K HQ"}
        },
        "hashtags": "#Hindenburg #Disaster #Documentary #8K #History"
    },
    {
        "id": "s_0yOzCKDa8",
        "title": "December 7th: Pearl Harbor (1943) | John Ford | 8K HQ",
        "desc_intro": "December 7th (1943) – Academy Award Winner (Best Documentary Short)\nDirectors: John Ford, Gregg Toland | A dramatized account of the attack on Pearl Harbor.\nWon the Oscar for Best Documentary Short Subject 1944.\nAI Remastered in 8K by remAIke.TV!",
        "tags": ["Pearl Harbor", "December 7th", "John Ford", "1943", "8K", "WWII", "Documentary", "Public Domain", "Oscar Winner", "World War 2", "Gregg Toland", "History", "Remastered", "US Navy", "4K UHD"],
        "localizations": {
            "de": {"title": "December 7th: Pearl Harbor (1943) | John Ford | 8K HQ"},
            "en": {"title": "December 7th: Pearl Harbor (1943) | John Ford | 8K HQ"},
            "ja": {"title": "12月7日: 真珠湾攻撃 (1943) | ジョン・フォード | 8K HQ"},
            "es": {"title": "7 de Diciembre: Pearl Harbor (1943) | John Ford | 8K HQ"},
            "fr": {"title": "7 Décembre: Pearl Harbor (1943) | John Ford | 8K HQ"},
            "pt": {"title": "7 de Dezembro: Pearl Harbor (1943) | John Ford | 8K HQ"},
            "ru": {"title": "7 декабря: Перл-Харбор (1943) | Джон Форд | 8K HQ"},
            "ko": {"title": "12월 7일: 진주만 (1943) | 존 포드 | 8K HQ"},
            "zh": {"title": "十二月七日: 珍珠港 (1943) | 约翰·福特 | 8K HQ"}
        },
        "hashtags": "#PearlHarbor #WWII #JohnFord #8K #Documentary"
    },
    {
        "id": "bhnnR0WX_X0",
        "title": "Boxing Cats (1894) | Edison | World's First Cat Video | 8K HQ",
        "desc_intro": "Boxing Cats (Prof. Welton's) – 1894, Thomas Edison's Black Maria Studio\nDirector: William K.L. Dickson\nONE OF THE OLDEST CAT VIDEOS EVER FILMED! Possibly the world's first 'cat video'.\nShot on Kinetoscope. AI Remastered in 8K by remAIke.TV!",
        "tags": ["Boxing Cats", "Edison", "1894", "8K", "Cat Video", "Kinetoscope", "Oldest Film", "Public Domain", "William Dickson", "Early Cinema", "Remastered", "Thomas Edison", "Cat", "Film History", "4K UHD"],
        "localizations": {
            "de": {"title": "Boxing Cats (1894) | Edison | Ältestes Katzenvideo | 8K HQ"},
            "en": {"title": "Boxing Cats (1894) | Edison | World's First Cat Video | 8K HQ"},
            "ja": {"title": "ボクシング・キャッツ (1894) | 世界最古の猫動画 | 8K HQ"},
            "es": {"title": "Gatos Boxeadores (1894) | Edison | Primer Video de Gatos | 8K"},
            "fr": {"title": "Chats Boxeurs (1894) | Edison | Plus Ancienne Vidéo de Chats | 8K"},
            "pt": {"title": "Gatos Boxeadores (1894) | Edison | Primeiro Vídeo de Gatos | 8K"},
            "ru": {"title": "Боксирующие коты (1894) | Эдисон | 8K HQ"},
            "ko": {"title": "복싱 고양이 (1894) | 에디슨 | 세계 최초 고양이 영상 | 8K"},
            "zh": {"title": "拳击猫 (1894) | 爱迪生 | 世界最早猫视频 | 8K HQ"}
        },
        "hashtags": "#BoxingCats #Edison #OldestCatVideo #8K #FilmHistory"
    },
    {
        "id": "HGg-g6SwrrQ",
        "title": "Reefer Madness (1936) | Cult Propaganda Classic | 8K HQ",
        "desc_intro": "Reefer Madness (1936) – aka 'Tell Your Children'\nDirector: Louis J. Gasnier | Originally a propaganda film warning about marijuana.\nBecame an unintentional comedy classic and cult film icon.\nAI Remastered in 8K by remAIke.TV!",
        "tags": ["Reefer Madness", "1936", "8K", "Cult Film", "Propaganda", "Public Domain", "Cannabis", "Classic Cinema", "Exploitation Film", "Tell Your Children", "Remastered", "Vintage Film", "Comedy", "So Bad Its Good", "4K UHD"],
        "localizations": {
            "de": {"title": "Reefer Madness (1936) | Kult-Propaganda-Klassiker | 8K HQ"},
            "en": {"title": "Reefer Madness (1936) | Cult Propaganda Classic | 8K HQ"},
            "ja": {"title": "リーファー・マッドネス (1936) | カルト映画 | 8K HQ"},
            "es": {"title": "Reefer Madness (1936) | Clásico de Propaganda | 8K HQ"},
            "fr": {"title": "Reefer Madness (1936) | Film de Propagande Culte | 8K HQ"},
            "pt": {"title": "Reefer Madness (1936) | Clássico de Propaganda | 8K HQ"},
            "ru": {"title": "Косяковое безумие (1936) | Культовый фильм | 8K HQ"},
            "ko": {"title": "리퍼 매드니스 (1936) | 컬트 영화 | 8K HQ"},
            "zh": {"title": "大麻狂潮 (1936) | 邪典经典 | 8K HQ"}
        },
        "hashtags": "#ReeferMadness #CultFilm #8K #Propaganda #ClassicCinema"
    },
]


def build_full_desc(film):
    """Build complete description for a film."""
    desc = film['desc_intro']
    
    # International titles block
    locs = film['localizations']
    intl = "\n\n🌍 AVAILABLE IN YOUR LANGUAGE:"
    for lang, data in locs.items():
        flag = {'de':'🇩🇪','en':'🇬🇧','ja':'🇯🇵','es':'🇪🇸','fr':'🇫🇷','pt':'🇧🇷',
                'ru':'🇷🇺','ko':'🇰🇷','zh':'🇨🇳','cs':'🇨🇿','pl':'🇵🇱'}.get(lang, '🌐')
        intl += f"\n{flag} {data['title'][:70]}"
    
    desc += intl
    desc += "\n" + CTA_BLOCK
    desc += "\n\n" + film['hashtags']
    
    return desc.strip()


def update_film(film):
    """Apply international SEO to one film."""
    global quota_used, updated
    
    vid_id = film['id']
    
    # Read current
    res = youtube.videos().list(part="snippet,localizations", id=vid_id).execute()
    quota_used += 1
    
    if not res['items']:
        print(f"  ⏩ {vid_id} — not found")
        return
    
    snippet = res['items'][0]['snippet']
    old_title = snippet['title']
    
    # Update snippet
    snippet['title'] = film['title']
    snippet['description'] = build_full_desc(film)
    snippet['tags'] = film['tags']
    snippet['defaultLanguage'] = 'en'  # International content = English default
    
    # Build localizations
    localizations = {}
    for lang, data in film['localizations'].items():
        loc_desc = build_full_desc(film)  # Same rich description for all
        localizations[lang] = {
            'title': data['title'][:100],
            'description': loc_desc
        }
    
    body = {
        'id': vid_id,
        'snippet': snippet,
        'localizations': localizations
    }
    
    youtube.videos().update(part="snippet,localizations", body=body).execute()
    quota_used += 50
    updated += 1
    
    lang_count = len(film['localizations'])
    print(f"  ✅ [{quota_used:>4}q] {old_title[:40]}")
    print(f"       → {film['title'][:60]}")
    print(f"       → {lang_count} localizations")


# ═══════════════════════════════════════════════════════════
# EXECUTE
# ═══════════════════════════════════════════════════════════

print("═" * 65)
print("  INTERNATIONAL FILMS SEO UPDATE")
print(f"  {len(films)} films × 9 languages × researched data")
print("═" * 65)

for film in films:
    try:
        update_film(film)
        time.sleep(0.5)
    except Exception as e:
        if 'quotaExceeded' in str(e):
            print(f"\n🛑 QUOTA EXCEEDED at {quota_used} units!")
            break
        errors.append({'id': film['id'], 'error': str(e)})
        print(f"  ❌ {film['id']}: {e}")

print(f"\n{'═' * 65}")
print(f"  COMPLETE")
print(f"{'═' * 65}")
print(f"  Updated:   {updated} / {len(films)}")
print(f"  Errors:    {len(errors)}")
print(f"  Quota:     {quota_used} units")

if errors:
    for e in errors:
        print(f"    {e['id']}: {e['error'][:80]}")

# Report
report = {
    'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    'films_updated': updated,
    'quota_used': quota_used,
    'errors': errors,
}
with open('config/international_films_seo_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"  Report: config/international_films_seo_report.json")
