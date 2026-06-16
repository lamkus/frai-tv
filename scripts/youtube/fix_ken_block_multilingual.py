#!/usr/bin/env python3
"""Fix Ken Block with 18 languages"""

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

KEN_BLOCK_DESC = '''How would you feel sitting next to Ken Block? 🏎️💨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🇺🇸 ENGLISH:
This legendary Jump Jam event at the DiRT 2 video game launch showcases Ken Block's insane driving skills – jumps, drifts, and pure adrenaline! Rally legend, Gymkhana pioneer, and co-founder of Hoonigan. RIP Ken Block (1967-2023). 🔥

🇩🇪 DEUTSCH:
Dieses legendäre Jump Jam Event beim DiRT 2 Launch zeigt Ken Blocks wahnsinnige Fahrkünste – Sprünge, Drifts und pures Adrenalin! Rally-Legende, Gymkhana-Pionier und Mitgründer von Hoonigan. RIP Ken Block (1967-2023). 🔥

🇪🇸 ESPAÑOL:
Este legendario evento Jump Jam en el lanzamiento de DiRT 2 muestra las locas habilidades de conducción de Ken Block – saltos, derrapes y pura adrenalina! Leyenda del rally, pionero del Gymkhana. RIP Ken Block (1967-2023). 🔥

🇫🇷 FRANÇAIS:
Cet événement légendaire Jump Jam au lancement de DiRT 2 montre les compétences de conduite folles de Ken Block – sauts, drifts et pure adrénaline! Légende du rallye, pionnier du Gymkhana. RIP Ken Block (1967-2023). 🔥

🇵🇹 PORTUGUÊS:
Este lendário evento Jump Jam no lançamento do DiRT 2 mostra as habilidades de direção insanas de Ken Block – saltos, drifts e pura adrenalina! Lenda do rali, pioneiro do Gymkhana. RIP Ken Block (1967-2023). 🔥

🇮🇹 ITALIANO:
Questo leggendario evento Jump Jam al lancio di DiRT 2 mostra le pazze abilità di guida di Ken Block – salti, derapate e pura adrenalina! Leggenda del rally, pioniere del Gymkhana. RIP Ken Block (1967-2023). 🔥

🇳🇱 NEDERLANDS:
Dit legendarische Jump Jam evenement bij de DiRT 2 lancering toont Ken Block's waanzinnige rijvaardigheden – sprongen, drifts en pure adrenaline! Rally-legende, Gymkhana-pionier. RIP Ken Block (1967-2023). 🔥

🇵🇱 POLSKI:
To legendarne wydarzenie Jump Jam na premierze DiRT 2 pokazuje szalone umiejętności jazdy Ken Blocka – skoki, drifty i czystą adrenalinę! Legenda rajdów, pionier Gymkhany. RIP Ken Block (1967-2023). 🔥

🇷🇺 РУССКИЙ:
Это легендарное событие Jump Jam на запуске DiRT 2 демонстрирует безумные навыки вождения Кена Блока – прыжки, дрифты и чистый адреналин! Легенда ралли, пионер Gymkhana. RIP Ken Block (1967-2023). 🔥

🇯🇵 日本語:
DiRT 2発売イベントでの伝説的なジャンプジャムで、ケン・ブロックの狂気の運転スキル – ジャンプ、ドリフト、純粋なアドレナリン！ラリーの伝説、ジムカーナのパイオニア。RIP Ken Block (1967-2023). 🔥

🇨🇳 中文:
DiRT 2发布会上的这场传奇Jump Jam展示了Ken Block疯狂的驾驶技术 – 跳跃、漂移和纯粹的肾上腺素！拉力赛传奇，Gymkhana先驱。RIP Ken Block (1967-2023). 🔥

🇰🇷 한국어:
DiRT 2 출시 이벤트에서의 전설적인 점프 잼은 켄 블록의 미친 운전 기술을 보여줍니다 – 점프, 드리프트, 순수한 아드레날린! 랠리 전설, 짐카나 개척자. RIP Ken Block (1967-2023). 🔥

🇹🇷 TÜRKÇE:
DiRT 2 lansmanındaki bu efsanevi Jump Jam etkinliği Ken Block'un çılgın sürüş becerilerini sergiliyor – atlamalar, driftler ve saf adrenalin! Ralli efsanesi, Gymkhana öncüsü. RIP Ken Block (1967-2023). 🔥

🇸🇦 العربية:
هذا الحدث الأسطوري جامب جام في إطلاق DiRT 2 يُظهر مهارات القيادة المجنونة لكين بلوك – قفزات، انزلاقات وأدرينالين خالص! أسطورة الرالي، رائد جيمخانا. RIP Ken Block (1967-2023). 🔥

🇮🇳 हिंदी:
DiRT 2 लॉन्च इवेंट में यह महान जंप जैम केन ब्लॉक की पागल ड्राइविंग स्किल्स दिखाता है – जंप, ड्रिफ्ट और शुद्ध एड्रेनालाइन! रैली लीजेंड, जिमखाना पायनियर। RIP Ken Block (1967-2023). 🔥

🇹🇭 ไทย:
งาน Jump Jam ในตำนานในงานเปิดตัว DiRT 2 แสดงทักษะการขับรถบ้าคลั่งของ Ken Block – กระโดด ดริฟท์ และอะดรีนาลีนบริสุทธิ์! ตำนานแรลลี่ ผู้บุกเบิก Gymkhana RIP Ken Block (1967-2023). 🔥

🇻🇳 TIẾNG VIỆT:
Sự kiện Jump Jam huyền thoại tại buổi ra mắt DiRT 2 thể hiện kỹ năng lái xe điên cuồng của Ken Block – nhảy, drift và adrenaline thuần túy! Huyền thoại rally, tiên phong Gymkhana. RIP Ken Block (1967-2023). 🔥

🇮🇩 BAHASA INDONESIA:
Acara Jump Jam legendaris di peluncuran DiRT 2 ini menampilkan keterampilan mengemudi gila Ken Block – lompatan, drift, dan adrenalin murni! Legenda reli, pelopor Gymkhana. RIP Ken Block (1967-2023). 🔥

🇸🇪 SVENSKA:
Detta legendariska Jump Jam-event vid DiRT 2-lanseringen visar Ken Blocks galna körförmåga – hopp, drifts och ren adrenalin! Rally-legend, Gymkhana-pionjär. RIP Ken Block (1967-2023). 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 KEN BLOCK (1967-2023)
Rally legend, Gymkhana pioneer, co-founder of DC Shoes & Hoonigan Racing Division

🎮 DiRT 2 LAUNCH EVENT (2009)
Exclusive footage from the game launch – gaming meets motorsport!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if Ken Block was a legend!
💬 COMMENT: Would YOU sit next to Ken Block?
🔔 SUBSCRIBE @remAIke_IT for more!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT

#KenBlock #JumpJam #DiRT2 #Rally #Gymkhana #Hoonigan #Motorsport #8K #Legend #RIP #remAIke'''

VIDEO_ID = '174AyltH9OI'
response = youtube.videos().list(part='snippet', id=VIDEO_ID).execute()
video = response['items'][0]

print(f"Updating: {video['snippet']['title']}")
video['snippet']['description'] = KEN_BLOCK_DESC

youtube.videos().update(
    part='snippet',
    body={'id': VIDEO_ID, 'snippet': video['snippet']}
).execute()

print(f"✅ Ken Block updated with 18 languages!")
print(f"Description: {len(KEN_BLOCK_DESC)} chars")
