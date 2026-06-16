"""
Fix 4_2qWUEje-c — Clever & Smart: In geheimer Mission
Same research-based SEO as the other video.
Currently: garbage title, empty description, Category 27 (WRONG), 0 tags, no localizations
"""

import json, os, sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = r"D:\remaike.TV\token.json"
CLIENT_SECRET = r"D:\remaike.TV\config\client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

VIDEO_ID = "4_2qWUEje-c"

def get_youtube():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def main():
    yt = get_youtube()

    new_title = "Clever & Smart: In geheimer Mission (2014) | 8K HQ"

    new_description = """🎬 Clever & Smart – In geheimer Mission (2014) | Mortadelo y Filemón contra Jimmy el Cachondo

Goya-prämierter 3D-Animationsfilm basierend auf dem legendären spanischen Comic von Francisco Ibáñez (seit 1958). Die Geheimagenten Fred Clever (Mortadelo) und Jeff Smart (Filemón) vom T.I.A. müssen den Erzfeind Jimmy el Cachondo aufhalten, der streng geheime Dokumente gestohlen hat.

🏆 Regie: Javier Fesser
🏆 2x Goya Award (Bester Animationsfilm + Bestes Drehbuch 2014)
🏆 Gaudí Award • Forqué Award • CEC Medal
🎬 Produktion: Ilion Animation Studios / Warner Bros. Spain
📚 Comic: Francisco Ibáñez, 222 Alben seit 1958

🌍 INTERNATIONAL NAMES:
🇪🇸 Mortadelo y Filemón contra Jimmy el Cachondo
🇬🇧 Mortadelo and Filemon: Mission Implausible
🇩🇪 Clever & Smart – In geheimer Mission
🇫🇷 Mortadel et Filémon
🇮🇹 Fortune & Fortuni
🇯🇵 モートとフィル (Mōto to Firu)
🇨🇳 特工二人组 (Tegong errenzu)
🇵🇹 Mortadelo e Salaminho
🇳🇱 Paling & Ko
🇸🇪 Flink och Fummel
🇫🇮 Älli ja Tälli
🇩🇰 Flip & Flop
🇹🇷 Dörtgöz ve Dazlak
🇸🇦 شاطر و ماكر
🇬🇷 Αντιριξ και Συμφωνιξ
🇵🇪 Los súper agentes locos (Peru)
🇲🇽 Mortadelo y Filemón contra Jimmy el Locuaz (Mexiko)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed the film!
💬 COMMENT your favorite Clever & Smart moment!
🔔 SUBSCRIBE for more classic animation!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#CleverUndSmart #MortadeloYFilemon #Animation #8K #SpanishComics"""

    new_tags = [
        "Clever und Smart",
        "Mortadelo y Filemón",
        "In geheimer Mission",
        "Mission Implausible",
        "Francisco Ibáñez",
        "Javier Fesser",
        "Goya Award",
        "Spanish Animation",
        "8K",
        "モートとフィル",
        "特工二人组",
        "Mortadel et Filémon",
        "Fred Clever Jeff Smart",
        "TIA Agenten",
        "Warner Bros Animation"
    ]

    localizations = {
        "es": {
            "title": "Mortadelo y Filemón contra Jimmy el Cachondo (2014) | 8K HQ",
            "description": "🎬 Película animada en 3D basada en el legendario cómic español de Francisco Ibáñez.\n\n🏆 2x Premio Goya (Mejor Película de Animación + Mejor Guion Adaptado)\n🎬 Dirección: Javier Fesser\n📚 Comic: 222 álbumes desde 1958\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👆 ¡Dale LIKE si te gustó!\n💬 ¡COMENTA tu momento favorito!\n🔔 ¡SUSCRÍBETE para más animación clásica!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#MortadeloYFilemon #CleverUndSmart #Animación #8K #ComicEspañol"
        },
        "en": {
            "title": "Mortadelo & Filemon: Mission Implausible (2014) | 8K HQ",
            "description": "🎬 Goya Award-winning 3D animated film based on Spain's legendary comic by Francisco Ibáñez (since 1958).\n\nSecret agents Mort (Mortadelo) & Phil (Filemón) from the T.I.A. must stop arch-enemy Jimmy the Freak.\n\n🏆 Director: Javier Fesser\n🏆 2x Goya (Best Animated Film + Best Adapted Screenplay 2014)\n🎬 Production: Ilion Animation Studios / Warner Bros. Spain\n📚 Comic: 222 albums since 1958\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👆 LIKE if you enjoyed this!\n💬 COMMENT your thoughts!\n🔔 SUBSCRIBE for more classic animation!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#MortadeloAndFilemon #MissionImplausible #Animation #8K #SpanishComics"
        },
        "fr": {
            "title": "Mortadel et Filémon: Mission Implausible (2014) | 8K HQ",
            "description": "🎬 Film d'animation 3D primé aux Goya, basé sur la légendaire bande dessinée espagnole de Francisco Ibáñez.\n\n🏆 2x Prix Goya (Meilleur Film d'Animation + Meilleur Scénario Adapté)\n🎬 Réalisation: Javier Fesser\n📚 BD: 222 albums depuis 1958\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#MortadelEtFilemon #Animation #8K #BDEspagnole"
        },
        "pt": {
            "title": "Mortadelo e Salaminho: Missão Implausível (2014) | 8K HQ",
            "description": "🎬 Filme de animação 3D premiado com Goya, baseado na lendária banda desenhada espanhola de Francisco Ibáñez.\n\n🏆 2x Prêmio Goya (Melhor Filme de Animação + Melhor Roteiro Adaptado)\n🎬 Direção: Javier Fesser\n📚 Quadrinhos: 222 álbuns desde 1958\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#MortadeloEFilemon #Animação #8K #QuadrinhosEspanhóis"
        },
        "ja": {
            "title": "モートとフィル: ミッション・インプラウジブル (2014) | 8K HQ",
            "description": "🎬 スペインの伝説的コミック「モートとフィル」(フランシスコ・イバニェス原作)に基づくゴヤ賞受賞3Dアニメ映画。\n\n🏆 ゴヤ賞2冠（最優秀アニメ映画＋最優秀脚色賞 2014年）\n🎬 監督: ハビエル・フェッセル\n📚 原作コミック: 1958年から222巻\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#モートとフィル #スペインアニメ #8K #クラシックアニメ"
        },
        "zh": {
            "title": "特工二人组: 不可能的任务 (2014) | 8K HQ",
            "description": "🎬 基于弗朗西斯科·伊巴涅斯传奇西班牙漫画的戈雅奖获奖3D动画电影。\n\n🏆 2项戈雅奖（最佳动画片 + 最佳改编剧本 2014年）\n🎬 导演: 哈维尔·费塞尔\n📚 原著漫画: 自1958年起222卷\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#特工二人组 #西班牙动画 #8K #经典动画"
        },
        "ko": {
            "title": "모르타델로와 필레몬: 임파서블 미션 (2014) | 8K HQ",
            "description": "🎬 프란시스코 이바녜스의 전설적인 스페인 만화를 원작으로 한 고야상 수상 3D 애니메이션 영화.\n\n🏆 고야상 2관왕 (최우수 애니메이션 + 최우수 각색상 2014)\n🎬 감독: 하비에르 페세르\n📚 원작 만화: 1958년부터 222권\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#모르타델로 #스페인애니 #8K #클래식애니"
        },
        "nl": {
            "title": "Paling & Ko: Mission Implausible (2014) | 8K HQ",
            "description": "🎬 Goya Award-winnende 3D-animatiefilm gebaseerd op de legendarische Spaanse strip van Francisco Ibáñez.\n\n🏆 2x Goya (Beste Animatiefilm + Beste Bewerkt Scenario)\n🎬 Regie: Javier Fesser\n📚 Strip: 222 albums sinds 1958\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n\n#PalingEnKo #MortadeloYFilemon #Animatie #8K"
        }
    }

    print(f"{'='*60}")
    print(f"FIXING 4_2qWUEje-c — Clever & Smart")
    print(f"{'='*60}")

    resp = yt.videos().list(part="snippet", id=VIDEO_ID).execute()
    if not resp.get("items"):
        print(f"ERROR: Video {VIDEO_ID} not found!")
        sys.exit(1)

    video = resp["items"][0]
    old_title = video["snippet"]["title"]
    old_cat = video["snippet"]["categoryId"]
    old_desc = video["snippet"].get("description", "")

    print(f"OLD Title:    {old_title}")
    print(f"OLD Category: {old_cat}")
    print(f"OLD Desc:     {'(EMPTY)' if not old_desc.strip() else old_desc[:60]+'...'}")
    print(f"OLD Tags:     {len(video['snippet'].get('tags', []))}")
    print()
    print(f"NEW Title:    {new_title}")
    print(f"NEW Category: 1 (Film & Animation)")
    print(f"NEW Tags:     {len(new_tags)}")
    print(f"NEW Locs:     {len(localizations)} languages")
    print(f"NEW Desc:     {len(new_description)} chars")

    body = {
        "id": VIDEO_ID,
        "snippet": {
            "title": new_title,
            "description": new_description,
            "tags": new_tags,
            "categoryId": "1",
            "defaultLanguage": "de",
            "defaultAudioLanguage": "de"
        },
        "localizations": localizations
    }

    print(f"\n🔄 Updating...")
    result = yt.videos().update(part="snippet,localizations", body=body).execute()

    print(f"✅ DONE!")
    print(f"   Title: {result['snippet']['title']}")
    print(f"   Category: {result['snippet']['categoryId']}")
    print(f"   Tags: {len(result['snippet'].get('tags', []))}")
    print(f"   Locs: {len(result.get('localizations', {}))}")
    print(f"   Lang: {result['snippet'].get('defaultLanguage')}")
    print(f"\n💰 Quota: 51 units")

    report = {
        "video_id": VIDEO_ID,
        "old_title": old_title,
        "new_title": new_title,
        "old_category": old_cat,
        "new_category": "1",
        "old_description": "(EMPTY)" if not old_desc.strip() else "had content",
        "tags_added": len(new_tags),
        "localizations": list(localizations.keys()),
        "status": "SUCCESS"
    }
    with open(r"D:\remaike.TV\config\clever_smart_fix2_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📋 Report saved")

if __name__ == "__main__":
    main()
