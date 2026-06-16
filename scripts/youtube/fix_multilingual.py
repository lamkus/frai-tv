#!/usr/bin/env python3
"""
Fix videos with FULL 18-language descriptions
Like the original Marihuana video standard
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Full 18-language template for Reefer Madness
REEFER_MADNESS_DESC = '''🔥 The most infamous propaganda film ever made!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🇺🇸 ENGLISH:
"Tell Your Children" – the anti-cannabis hysteria film that became a stoner cult classic. Originally financed by a church group, now a legendary piece of cinema history. The ultimate example of propaganda gone hilariously wrong! 🔥

🇩🇪 DEUTSCH:
"Erzählt es euren Kindern" – der Anti-Cannabis-Hysterie-Film, der zum Stoner-Kultobjekt wurde. Der ultimative Beweis dafür, wie Propaganda spektakulär nach hinten losgehen kann! 🔥

🇪🇸 ESPAÑOL:
"Díselo a tus hijos" – la película de histeria anti-cannabis que se convirtió en un clásico de culto stoner. ¡El ejemplo definitivo de propaganda que salió terriblemente mal! 🔥

🇫🇷 FRANÇAIS:
"Dis-le à tes enfants" – le film d'hystérie anti-cannabis devenu culte chez les stoners. L'exemple ultime de propagande qui a terriblement mal tourné! 🔥

🇵🇹 PORTUGUÊS:
"Conte aos seus filhos" – o filme de histeria anti-cannabis que se tornou um clássico cult stoner. O exemplo definitivo de propaganda que deu terrivelmente errado! 🔥

🇮🇹 ITALIANO:
"Dillo ai tuoi figli" – il film di isteria anti-cannabis diventato un classico cult degli stoner. L'esempio definitivo di propaganda andata terribilmente storta! 🔥

🇳🇱 NEDERLANDS:
"Vertel het je kinderen" – de anti-cannabis hysterie film die een stoner cultklassieker werd. Het ultieme voorbeeld van propaganda die verschrikkelijk misging! 🔥

🇵🇱 POLSKI:
"Powiedz swoim dzieciom" – film o antykonopnej histerii, który stał się kultowy wśród stonerów. Ostateczny przykład propagandy, która poszła strasznie źle! 🔥

🇷🇺 РУССКИЙ:
"Расскажи своим детям" – фильм антиканнабисной истерии, ставший культовым среди стоунеров. Идеальный пример пропаганды, которая ужасно провалилась! 🔥

🇯🇵 日本語:
「子供たちに伝えよ」– ストーナーのカルト的名作となった反大麻ヒステリー映画。見事に失敗したプロパガンダの究極の例！🔥

🇨🇳 中文:
"告诉你的孩子们" – 成为大麻文化崇拜经典的反大麻歇斯底里电影。宣传严重失败的终极案例！🔥

🇰🇷 한국어:
"아이들에게 말해라" – 스토너 컬트 클래식이 된 반대마 히스테리 영화. 끔찍하게 실패한 선전의 궁극적인 예! 🔥

🇹🇷 TÜRKÇE:
"Çocuklarına Söyle" – stoner kült klasiği haline gelen esrar karşıtı histeri filmi. Korkunç şekilde ters giden propagandanın nihai örneği! 🔥

🇸🇦 العربية:
"أخبر أطفالك" – فيلم الهستيريا المعادية للقنب الذي أصبح كلاسيكية ثقافة الستونر. المثال النهائي على الدعاية التي فشلت بشكل فظيع! 🔥

🇮🇳 हिंदी:
"अपने बच्चों को बताओ" – भांग विरोधी हिस्टीरिया फिल्म जो स्टोनर कल्ट क्लासिक बन गई। भयानक रूप से गलत हुए प्रचार का अंतिम उदाहरण! 🔥

🇹🇭 ไทย:
"บอกลูกของคุณ" – ภาพยนตร์ฮิสทีเรียต่อต้านกัญชาที่กลายเป็นคลาสสิกวัฒนธรรมสโตนเนอร์ ตัวอย่างสุดท้ายของโฆษณาชวนเชื่อที่ล้มเหลวอย่างน่ากลัว! 🔥

🇻🇳 TIẾNG VIỆT:
"Hãy nói với con bạn" – bộ phim cuồng loạn chống cần sa đã trở thành tác phẩm kinh điển của văn hóa stoner. Ví dụ cuối cùng về tuyên truyền thất bại thảm hại! 🔥

🇮🇩 BAHASA INDONESIA:
"Katakan pada Anak-anakmu" – film histeria anti-ganja yang menjadi klasik kultus stoner. Contoh utama propaganda yang gagal total! 🔥

🇸🇪 SVENSKA:
"Berätta för dina barn" – anti-cannabis hysteri-filmen som blev en stoner-kulklassiker. Det ultimata exemplet på propaganda som gick fruktansvärt fel! 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 REEFER MADNESS (1936)
• Original Title: "Tell Your Children"
• Director: Louis J. Gasnier
• Runtime: 66 minutes
• Also known as: "The Burning Question", "Dope Addict", "Love Madness"
• Public Domain since 1972

🎭 CAST:
Dorothy Short, Kenneth Craig, Lillian Miles, Dave O'Brien, Thelma White

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you love cult classics!
💬 COMMENT: Is this the worst propaganda ever?
🔔 SUBSCRIBE @remAIke_IT for more!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT

#ReeferMadness #TellYourChildren #CultClassic #Propaganda #Cannabis #1936 #PublicDomain #8K #Restored #Vintage #ClassicFilm #Marijuana #420 #remAIke'''

# Update Reefer Madness
VIDEO_ID = 'oGw7_7xazhU'
response = youtube.videos().list(part='snippet', id=VIDEO_ID).execute()
video = response['items'][0]

print(f"Updating: {video['snippet']['title']}")
video['snippet']['description'] = REEFER_MADNESS_DESC

youtube.videos().update(
    part='snippet',
    body={'id': VIDEO_ID, 'snippet': video['snippet']}
).execute()

print(f"✅ Reefer Madness updated with 18 languages!")
print(f"Description: {len(REEFER_MADNESS_DESC)} chars")
