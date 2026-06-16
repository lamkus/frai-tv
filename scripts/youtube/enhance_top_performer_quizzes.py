#!/usr/bin/env python3
"""
Enhance Psychology Quiz DB with individual Top-Performer quizzes.
Videos with >500 views get UNIQUE quizzes based on their specific content,
IN ADDITION to (replacing) the series template quizzes.

Uses Wikipedia-verified facts from previous research.
"""
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# INDIVIDUAL QUIZZES FOR TOP PERFORMERS
# Key = video_id, Value = list of 3 quizzes (Easy/Medium/Hard)
# All facts Wikipedia-verified Feb 2026
# ============================================================

INDIVIDUAL_QUIZZES = {
    # ═══════════════════════════════════════════════════════════
    # VIDEO IDs verified from quiz_database_psychology_v3.json
    # ═══════════════════════════════════════════════════════════

    # ─── WHITE ZOMBIE (32,808 views) ───
    "d8Ak1R_eOlY": [
        {
            "question": "What makes 'White Zombie' (1932) a piece of film history?",
            "answers": [
                {"text": "It's the FIRST feature-length zombie film ever made", "correct": True},
                {"text": "It was the first horror film with sound", "correct": False},
                {"text": "It introduced the word 'zombie' to English", "correct": False},
                {"text": "It was Bela Lugosi's debut film", "correct": False}
            ],
            "explanation": "White Zombie (1932) IS the birthplace of zombie cinema! Every zombie film since – from Night of the Living Dead to The Walking Dead – traces back to this movie. Shot in just 11 DAYS for $50,000 using leftover sets from Dracula and Frankenstein!"
        },
        {
            "question": "Which famous rock musician named their band after this film?",
            "answers": [
                {"text": "Rob Zombie (band: White Zombie)", "correct": True},
                {"text": "Ozzy Osbourne", "correct": False},
                {"text": "Alice Cooper", "correct": False},
                {"text": "Marilyn Manson", "correct": False}
            ],
            "explanation": "Rob Zombie was so inspired by this 1932 film that he named his entire BAND 'White Zombie'! The band sold over 5 million albums. Rob Zombie later became a horror film director himself – completing the circle from classic to modern horror. Art inspiring art!"
        },
        {
            "question": "How was this film physically made under extreme conditions?",
            "answers": [
                {"text": "Shot in only 11 days using borrowed sets from other horror films", "correct": True},
                {"text": "Filmed over 6 months in Haiti", "correct": False},
                {"text": "Made without a script – entirely improvised", "correct": False},
                {"text": "The actors performed all their own makeup effects", "correct": False}
            ],
            "explanation": "11 days! The production borrowed sets from Dracula, Frankenstein, and Hunchback of Notre Dame – those Universal horror classics were literally recycled to create a new genre. The zombie extras' makeup was done by Jack Pierce, the same artist behind Frankenstein's monster!"
        }
    ],

    # ─── FELIX AT THE CIRCUS (25,042 views) ───
    "fFanPpOArKs": [
        {
            "question": "Felix the Cat appeared almost a DECADE before which famous character?",
            "answers": [
                {"text": "Mickey Mouse (1928)", "correct": True},
                {"text": "Betty Boop (1930)", "correct": False},
                {"text": "Popeye (1929)", "correct": False},
                {"text": "Donald Duck (1934)", "correct": False}
            ],
            "explanation": "Felix debuted in 1919 – nine years before Mickey Mouse (1928)! Felix was the world's FIRST animated superstar, recognized globally. His image was even used for the first TV test broadcast in 1928. Felix truly paved the way for every cartoon character that followed!"
        },
        {
            "question": "What TECHNOLOGICAL milestone is Felix the Cat directly connected to?",
            "answers": [
                {"text": "His doll was used for the first TV test broadcast in 1928", "correct": True},
                {"text": "He was the first character animated by computer", "correct": False},
                {"text": "His cartoons were the first shown in cinemas", "correct": False},
                {"text": "He starred in the first color animated film", "correct": False}
            ],
            "explanation": "In 1928, RCA engineers placed a Felix the Cat doll on a rotating turntable for the very FIRST television test broadcast! Poor Felix spun for HOURS while engineers adjusted the signal. Felix didn't just star in cartoons – he literally helped invent television!"
        },
        {
            "question": "What controversy surrounds Felix the Cat's creation?",
            "answers": [
                {"text": "Dispute between Pat Sullivan (producer) and Otto Messmer (animator)", "correct": True},
                {"text": "Disney claimed Felix was copied from Mickey", "correct": False},
                {"text": "The character was stolen from a European artist", "correct": False},
                {"text": "Felix's design was based on a real cat that was never credited", "correct": False}
            ],
            "explanation": "The great Felix debate! Producer Pat Sullivan took credit, but animator Otto Messmer actually DREW Felix. For decades, Sullivan got the glory. Only after both men died was Messmer recognized as the true creative genius behind Felix. Art history's biggest uncredited artist!"
        }
    ],

    # ─── SUPERMAN (1941) (20,287 views) ───
    "6A2_RKWP2X4": [
        {
            "question": "What happened to Superman's powers BECAUSE of this cartoon?",
            "answers": [
                {"text": "He gained the ability to FLY (he could only leap before)", "correct": True},
                {"text": "He gained X-ray vision", "correct": False},
                {"text": "He became bulletproof", "correct": False},
                {"text": "He gained super speed", "correct": False}
            ],
            "explanation": "This cartoon CHANGED Superman forever! Originally he could only 'leap tall buildings.' Fleischer animators found leaping looked silly in animation, so they asked DC: 'Can he just fly?' DC agreed – and a cartoon decision permanently altered one of fiction's most iconic characters!"
        },
        {
            "question": "What award recognition did this specific Superman cartoon receive?",
            "answers": [
                {"text": "Academy Award nomination for Best Animated Short Film", "correct": True},
                {"text": "It won the Palme d'Or at Cannes", "correct": False},
                {"text": "It received a Golden Globe", "correct": False},
                {"text": "It was inducted into the Smithsonian", "correct": False}
            ],
            "explanation": "This pilot episode 'Superman' (1941) was nominated for an Academy Award for Best Animated Short! Each Superman cartoon cost $50,000 – FOUR TIMES the normal budget. The cinematic quality and rotoscope animation were so ahead of their time that they still look stunning today!"
        },
        {
            "question": "How did voice actor Bud Collyer differentiate Clark Kent from Superman?",
            "answers": [
                {"text": "He dropped his voice an octave when saying 'This is a job for Superman!'", "correct": True},
                {"text": "He used a different accent for each character", "correct": False},
                {"text": "Two different actors actually voiced them", "correct": False},
                {"text": "He spoke faster as Superman", "correct": False}
            ],
            "explanation": "Genius voice acting! Bud Collyer spoke in a higher pitch as mild Clark Kent, then dramatically DROPPED his voice for Superman's iconic catchphrase. This dual-voice technique became the template for EVERY Superman voice actor since. Collyer voiced Superman for over a decade!"
        }
    ],

    # ─── CABINET OF DR. CALIGARI (16,591 views) ───
    "5WVJHELSD7A": [
        {
            "question": "What film genre did 'The Cabinet of Dr. Caligari' (1920) essentially CREATE?",
            "answers": [
                {"text": "German Expressionist cinema and psychological horror", "correct": True},
                {"text": "The musical film genre", "correct": False},
                {"text": "Science fiction films", "correct": False},
                {"text": "Documentary filmmaking", "correct": False}
            ],
            "explanation": "Caligari is THE founding film of Expressionism! Its distorted, painted sets and angular shadows created a visual language for psychological horror that influenced EVERY horror filmmaker since. Made for just $12,000, it ran for 7 YEARS straight in a Paris cinema!"
        },
        {
            "question": "What's unusual about the film's sets compared to other movies?",
            "answers": [
                {"text": "The sets are painted on flat canvases with intentionally distorted angles", "correct": True},
                {"text": "They were filmed in real locations only", "correct": False},
                {"text": "They used the first computer-generated backgrounds", "correct": False},
                {"text": "The sets were built underwater", "correct": False}
            ],
            "explanation": "Nothing is straight in Caligari! ALL sets were painted on flat canvases with jagged, tilted lines to create a nightmare world. Windows are crooked, streets twist impossibly. This artistic choice was made to save money on lighting – and accidentally invented a revolutionary film style!"
        },
        {
            "question": "How was this $12,000 film received by audiences?",
            "answers": [
                {"text": "It ran for 7 consecutive years in one Paris cinema", "correct": True},
                {"text": "It was banned in all European countries", "correct": False},
                {"text": "It failed at the box office completely", "correct": False},
                {"text": "Only critics liked it – audiences hated it", "correct": False}
            ],
            "explanation": "A $12,000 film that became a world sensation! It played for SEVEN consecutive years at the Cine Opera in Paris. Rotten Tomatoes gives it 96%! The film's twist ending – one of cinema's FIRST – was not in the original script and was added by director Robert Wiene."
        }
    ],

    # ─── DINNER FOR ONE (14,152 views) ───
    "z8FqTSpp6Kg": [
        {
            "question": "What world record does 'Dinner for One' hold?",
            "answers": [
                {"text": "Most frequently repeated TV program in history", "correct": True},
                {"text": "Oldest surviving TV recording", "correct": False},
                {"text": "Most watched single broadcast ever", "correct": False},
                {"text": "Longest running TV series", "correct": False}
            ],
            "explanation": "Guinness World Record holder! 'Dinner for One' has been broadcast on German TV every New Year's Eve since 1963 – making it the most repeated TV show EVER. An estimated 15-20 million Germans watch it EVERY YEAR. The ultimate 'Same procedure as every year!'"
        },
        {
            "question": "What's the biggest irony about 'Dinner for One'?",
            "answers": [
                {"text": "It's a British sketch that's unknown in Britain but legendary in Germany", "correct": True},
                {"text": "The actors never knew it was being recorded", "correct": False},
                {"text": "It was originally a drama, not a comedy", "correct": False},
                {"text": "The tiger rug was a real tiger", "correct": False}
            ],
            "explanation": "Maximum irony! This quintessentially BRITISH sketch by Freddie Frinton is a national institution in GERMANY but virtually unknown in the UK! Even King Charles III has referenced it. It was recorded in 1963 by German TV channel NDR in Hamburg – a British cultural export that never made it home!"
        },
        {
            "question": "What's the mathematical drinking challenge butler James faces?",
            "answers": [
                {"text": "16 drinks: 4 toasts x 4 imaginary guests", "correct": True},
                {"text": "8 drinks: 2 toasts x 4 guests", "correct": False},
                {"text": "12 drinks: 3 toasts x 4 guests", "correct": False},
                {"text": "20 drinks: 5 toasts x 4 guests", "correct": False}
            ],
            "explanation": "Poor James! Miss Sophie's 4 imaginary guests each get 4 toasts = 16 drinks James must consume while serving! He gets progressively drunker, tripping over the same tiger rug each time. Freddie Frinton's physical comedy is MASTERFUL – each trip is slightly different. Pure genius!"
        }
    ],

    # ─── NOSFERATU (4,094 views) ───
    "Nzi6aRKDoEs": [
        {
            "question": "Why was 'Nosferatu' (1922) almost lost forever?",
            "answers": [
                {"text": "A court ordered ALL copies destroyed for copyright violation", "correct": True},
                {"text": "The original negative was accidentally burned", "correct": False},
                {"text": "The studio went bankrupt and threw them away", "correct": False},
                {"text": "The film was banned by the government", "correct": False}
            ],
            "explanation": "Nosferatu was an UNAUTHORIZED adaptation of Bram Stoker's 'Dracula'! The Stoker estate sued and WON – a court ordered every copy destroyed. But some prints survived in private collections! Without those lucky survivors, one of cinema's greatest masterpieces would be gone forever."
        },
        {
            "question": "What's remarkable about lead actor Max Schreck's name?",
            "answers": [
                {"text": "'Schreck' means 'terror' or 'fright' in German", "correct": True},
                {"text": "It was a stage name he chose for the role", "correct": False},
                {"text": "Schreck means 'shadow' in German", "correct": False},
                {"text": "He changed his name after the film became famous", "correct": False}
            ],
            "explanation": "You can't make this up! The actor playing cinema's most terrifying vampire was ACTUALLY named 'Max Schreck' – literally 'Maximum TERROR' in German! His performance was so eerie that urban legends claimed he was a REAL vampire. The 2000 film 'Shadow of the Vampire' explored this myth!"
        },
        {
            "question": "What filmmaking technique did Nosferatu pioneer?",
            "answers": [
                {"text": "Using shadows and silhouettes to create psychological horror", "correct": True},
                {"text": "The first use of color tinting in horror", "correct": False},
                {"text": "Stop-motion special effects", "correct": False},
                {"text": "Underwater filming techniques", "correct": False}
            ],
            "explanation": "Count Orlok's shadow climbing the stairs is one of cinema's most ICONIC images! Director F.W. Murnau pioneered using shadows as a character – the vampire's shadow acts independently, reaching for victims. This technique influenced EVERY horror filmmaker from Hitchcock to modern cinema!"
        }
    ],

    # ─── BUSTER KEATON: CONVICT 13 (4,054 views) ───
    "_3Z1GTYFUAM": [
        {
            "question": "Why was Buster Keaton nicknamed 'The Great Stone Face'?",
            "answers": [
                {"text": "He NEVER changed his facial expression during films", "correct": True},
                {"text": "He wore heavy makeup that couldn't move", "correct": False},
                {"text": "He played stone statues in multiple films", "correct": False},
                {"text": "It was a reference to Mount Rushmore", "correct": False}
            ],
            "explanation": "Keaton's genius: ZERO expression while chaos erupts around him! The contrast between his calm deadpan face and the insane stunts created unique comedy. His nickname 'Buster' came from HARRY HOUDINI, who saw 18-month-old Keaton fall downstairs and exclaimed: 'That was a real buster!'"
        },
        {
            "question": "What death-defying stunt made Keaton a legend?",
            "answers": [
                {"text": "A real 2-ton building facade fell on him – he stood in the window gap", "correct": True},
                {"text": "He jumped from a real moving train", "correct": False},
                {"text": "He performed all his stunts on a tightrope", "correct": False},
                {"text": "He was dragged behind a real horse at full speed", "correct": False}
            ],
            "explanation": "In 'Steamboat Bill Jr.' (1928), an ACTUAL building wall falls on Keaton. He survives by standing exactly where the open window passes over – with only INCHES of clearance on each side! No stunt doubles, no wires, no safety net. One wrong step = death. Cinema's greatest practical stunt!"
        },
        {
            "question": "How did the legendary Harry Houdini play a role in Keaton's life?",
            "answers": [
                {"text": "Houdini gave baby Keaton his stage name 'Buster'", "correct": True},
                {"text": "Houdini taught him all his stunt techniques", "correct": False},
                {"text": "Houdini produced Keaton's first films", "correct": False},
                {"text": "They were related by marriage", "correct": False}
            ],
            "explanation": "Family friend Harry Houdini witnessed 18-month-old Joseph Keaton tumble down a flight of stairs WITHOUT CRYING. Houdini exclaimed: 'That was a real buster!' – and the nickname stuck for life! Keaton grew up to become the greatest physical comedian in film history."
        }
    ],

    # ─── KEN BLOCK GYMKHANA (8,679 views) ───
    "90UleF637FA": [
        {
            "question": "What makes Gymkhana videos unique in motorsport history?",
            "answers": [
                {"text": "All stunts are REAL – no CGI or digital effects", "correct": True},
                {"text": "They were filmed by drone for the first time", "correct": False},
                {"text": "They used autonomous driving technology", "correct": False},
                {"text": "They were the first motorsport videos in 4K", "correct": False}
            ],
            "explanation": "Every tire-smoking drift, every near-miss with a wall – 100% REAL! Ken Block's precision driving required months of practice and multiple takes. The Gymkhana series earned over 500 MILLION views, proving that authentic skill beats CGI every time!"
        },
        {
            "question": "What company did Ken Block co-found before becoming famous for driving?",
            "answers": [
                {"text": "DC Shoes", "correct": True},
                {"text": "Red Bull Racing", "correct": False},
                {"text": "Monster Energy", "correct": False},
                {"text": "GoPro", "correct": False}
            ],
            "explanation": "Before becoming the world's most famous rally driver on YouTube, Ken Block co-founded DC SHOES in 1994! The skateboard shoe brand made him a multi-millionaire, funding his racing passion. He pioneered the concept of 'branded automotive entertainment' that others now copy."
        },
        {
            "question": "What tragic event makes these videos even more precious?",
            "answers": [
                {"text": "Ken Block died in a snowmobile accident in January 2023", "correct": True},
                {"text": "The original cars were all destroyed in a warehouse fire", "correct": False},
                {"text": "YouTube removed the series for safety concerns", "correct": False},
                {"text": "The filming locations no longer exist", "correct": False}
            ],
            "explanation": "Ken Block tragically passed away on January 2, 2023 at age 55 in a snowmobile accident in Utah. His Gymkhana videos remain as a permanent testament to his extraordinary skill and creativity. These are not just videos – they're the legacy of a driving artist."
        }
    ],

    # ─── BETTY BOOP: MINNIE THE MOOCHER (5,427 views) ───
    "tJMJlCQc0UE": [
        {
            "question": "What legendary musician actually APPEARS in this cartoon?",
            "answers": [
                {"text": "Cab Calloway – his dance moves were rotoscoped", "correct": True},
                {"text": "Louis Armstrong played trumpet in the background", "correct": False},
                {"text": "Duke Ellington performed live for the recording", "correct": False},
                {"text": "Ella Fitzgerald sang the title song", "correct": False}
            ],
            "explanation": "Cab Calloway's REAL dance moves were rotoscoped (traced from live footage) to animate the ghost walrus character! This was groundbreaking: a real performer's movements preserved in animation forever. Calloway's signature 'hi-de-ho' call-and-response became a cultural phenomenon!"
        },
        {
            "question": "Why is 'Minnie the Moocher' considered one of animation's greatest achievements?",
            "answers": [
                {"text": "It perfectly blends live music performance with surreal animation", "correct": True},
                {"text": "It was the first cartoon with color", "correct": False},
                {"text": "It was the longest cartoon ever made at the time", "correct": False},
                {"text": "It was the first cartoon shown in theaters", "correct": False}
            ],
            "explanation": "This 1932 short is regularly ranked among the GREATEST animated films ever made! It pioneered the fusion of jazz music and surreal animation – scary, funny, and musically brilliant all at once. The rotoscoped Cab Calloway dance sequence was decades ahead of motion capture!"
        },
        {
            "question": "What was Betty Boop's ORIGINAL form when she first appeared?",
            "answers": [
                {"text": "A French poodle with floppy ears", "correct": True},
                {"text": "A fairy with wings", "correct": False},
                {"text": "Already the human character we know", "correct": False},
                {"text": "A cartoon version of Mae West", "correct": False}
            ],
            "explanation": "Betty Boop first appeared in 1930 as a POODLE with long floppy ears! She gradually became human by 1932, but kept those floppy ear-like earrings. Voice actress Mae Questel provided Betty's voice for most of the 90+ cartoons. Singer Helen Kane sued – claiming Betty stole her style!"
        }
    ],

    # ─── CHARADE (7,698 views) ───
    "PSdJJaxI4gM": [
        {
            "question": "What makes classic short films from the golden era special?",
            "answers": [
                {"text": "They tell complete stories in just minutes with incredible craft", "correct": True},
                {"text": "They were always filmed in color", "correct": False},
                {"text": "They had bigger budgets than feature films", "correct": False},
                {"text": "Only famous directors made short films", "correct": False}
            ],
            "explanation": "Golden era short films were miniature masterpieces! Studios employed top talent to create complete, polished stories in 7-20 minutes. These shorts played before feature films in cinemas and represented some of the most creative filmmaking of their time. Every frame counts!"
        },
        {
            "question": "Why did movie studios stop making short films for cinemas?",
            "answers": [
                {"text": "Television replaced cinema shorts as the main entertainment format", "correct": True},
                {"text": "Audiences complained they were too short", "correct": False},
                {"text": "The government banned them", "correct": False},
                {"text": "Color film made them too expensive", "correct": False}
            ],
            "explanation": "When TV arrived in the 1950s, cinemas stopped showing short films before features to save time. The entire short film industry collapsed! Ironically, streaming platforms like YouTube have revived the short film format – we've come full circle, 70 years later!"
        },
        {
            "question": "What's the connection between vintage short films and YouTube today?",
            "answers": [
                {"text": "YouTube revived the short-form format that cinemas abandoned", "correct": True},
                {"text": "YouTube was created to show vintage short films", "correct": False},
                {"text": "All YouTube content is based on classic shorts", "correct": False},
                {"text": "There is no connection", "correct": False}
            ],
            "explanation": "Full circle! Cinema shorts (1920s-1950s) were 3-20 minute entertainment shown before features. When TV killed them, short-form content disappeared for decades. YouTube and TikTok have brought back what our grandparents loved – bite-sized visual storytelling. History repeats!"
        }
    ],

    # ─── THE GRIM GAME (1919) - HOUDINI (6,757 views) ───
    "EMnokZOLpzU": [
        {
            "question": "What was Harry Houdini BEFORE becoming a movie star?",
            "answers": [
                {"text": "The world's most famous escape artist and magician", "correct": True},
                {"text": "A professional boxer", "correct": False},
                {"text": "A circus ringmaster", "correct": False},
                {"text": "A newspaper reporter", "correct": False}
            ],
            "explanation": "Harry Houdini (born Erik Weisz in Budapest!) was the greatest escape artist in HISTORY – handcuffs, straitjackets, locked underwater boxes. His fame was so massive that Hollywood came calling! He performed ALL his own stunts in films, making modern action stars look tame."
        },
        {
            "question": "What happened during filming that made this movie legendary?",
            "answers": [
                {"text": "A real mid-air plane collision occurred during an aerial stunt", "correct": True},
                {"text": "Houdini actually drowned and was revived", "correct": False},
                {"text": "The entire set burned down during filming", "correct": False},
                {"text": "A lion escaped and attacked the crew", "correct": False}
            ],
            "explanation": "During filming of The Grim Game, two biplanes ACTUALLY COLLIDED mid-air while Houdini was supposed to be in one of them! The cameras kept rolling and captured real footage of the crash. A stunt double was used for that specific shot – but the footage was REAL disaster!"
        },
        {
            "question": "What connection does Houdini have to Buster Keaton?",
            "answers": [
                {"text": "Houdini gave baby Keaton the nickname 'Buster'", "correct": True},
                {"text": "They starred in films together", "correct": False},
                {"text": "Keaton was Houdini's assistant", "correct": False},
                {"text": "They were brothers", "correct": False}
            ],
            "explanation": "True story! Family friend Houdini saw 18-month-old Joseph Keaton tumble down stairs WITHOUT crying and exclaimed: 'That was a real buster!' The nickname stuck – and 'Buster' Keaton became cinema's greatest stuntman. Two legends of physical performance, connected by one fall!"
        }
    ],

    # ─── BATMAN CHRISTMAS (5,562 views) ───
    "yIQCHpjp4NE": [
        {
            "question": "What classic Batman era does this special come from?",
            "answers": [
                {"text": "The 1966 Adam West 'campy' Batman TV series", "correct": True},
                {"text": "The Tim Burton Batman films", "correct": False},
                {"text": "The original 1940s Batman serials", "correct": False},
                {"text": "The DC Animated Universe", "correct": False}
            ],
            "explanation": "The 1966 Batman series starring Adam West is the CAMPIEST superhero show ever made! 'POW!' 'BAM!' 'ZONK!' appeared on screen during fight scenes. Today it's a beloved cult classic – intentionally funny and wildly creative. Even modern Batman actors reference it!"
        },
        {
            "question": "What made Adam West's Batman portrayal revolutionary?",
            "answers": [
                {"text": "He played Batman completely straight despite the absurd comedy", "correct": True},
                {"text": "He was the first actor to wear a real Batman costume", "correct": False},
                {"text": "He performed all stunts without a stunt double", "correct": False},
                {"text": "He wrote all his own dialogue", "correct": False}
            ],
            "explanation": "Adam West's GENIUS was that he never winked at the camera! While everything around him was absurd – Shark Repellent Bat Spray, anyone? – West played Batman with total sincerity. This deadpan delivery against camp comedy was revolutionary and influenced comedy for decades!"
        },
        {
            "question": "How many episodes of the 1966 Batman show were produced?",
            "answers": [
                {"text": "120 episodes over 3 seasons", "correct": True},
                {"text": "52 episodes over 1 season", "correct": False},
                {"text": "200 episodes over 5 seasons", "correct": False},
                {"text": "75 episodes over 2 seasons", "correct": False}
            ],
            "explanation": "120 episodes of pure Bat-entertainment from 1966-1968! The show was SO popular that it aired TWICE a week. Each story was a two-parter with a cliffhanger. In 1966, Batman merchandise outsold Superman for the first time in comic book history. Bat-mania was real!"
        }
    ],

    # ─── SUPERMAN: JAPOTEURS (4,379 views) ───
    "unzHtnrKeOU": [
        {
            "question": "What makes the Fleischer Superman cartoons technically remarkable?",
            "answers": [
                {"text": "Each cartoon cost $50,000 – FOUR times the normal animation budget", "correct": True},
                {"text": "They used live action footage as backgrounds", "correct": False},
                {"text": "They were the first cartoons with stereo sound", "correct": False},
                {"text": "Each cartoon took 3 years to produce", "correct": False}
            ],
            "explanation": "While other studios spent $10-15K per cartoon, Fleischer Studios invested $50,000 EACH! The result: cinematic quality that still impresses today. Rotoscoped animation, dramatic lighting, and film noir influences made these the most beautiful cartoons of their era. Art costs money!"
        },
        {
            "question": "How many Superman cartoons were produced by Fleischer Studios?",
            "answers": [
                {"text": "17 short films between 1941-1943", "correct": True},
                {"text": "52 weekly episodes", "correct": False},
                {"text": "Over 100 cartoons across 5 years", "correct": False},
                {"text": "Only 3 pilot episodes", "correct": False}
            ],
            "explanation": "Only 17 Superman cartoons were made – but what a legacy! Each one is a miniature cinematic masterpiece. Fleischer Studios produced 9, then Famous Studios completed 8 more. All 17 are considered among the greatest animated shorts ever created. Quality over quantity!"
        },
        {
            "question": "What animation technique gives these cartoons their unique look?",
            "answers": [
                {"text": "Rotoscoping – tracing over live-action footage for realistic movement", "correct": True},
                {"text": "Stop-motion animation with clay figures", "correct": False},
                {"text": "Computer-assisted drawing (early digital)", "correct": False},
                {"text": "Only hand-drawn without any reference material", "correct": False}
            ],
            "explanation": "Fleischer used ROTOSCOPING – filming live actors, then tracing their movements frame by frame! This gave Superman incredibly fluid, realistic motion that other cartoons couldn't match. The same studio invented rotoscoping in 1915 – and used it to make Superman look truly superhuman!"
        }
    ],

    # ─── GETAWAY IN STOCKHOLM (4,143 views) ───
    "NcfUWqlfSm0": [
        {
            "question": "What makes the Getaway in Stockholm videos legendary among car fans?",
            "answers": [
                {"text": "Real high-speed driving through city streets – not staged", "correct": True},
                {"text": "They used the world's most expensive cars", "correct": False},
                {"text": "They were filmed by the Swedish police as evidence", "correct": False},
                {"text": "Professional race drivers competed against each other", "correct": False}
            ],
            "explanation": "The Getaway in Stockholm series features REAL high-speed drives through actual Stockholm streets! Originally distributed on DVD, these videos became legendary in the underground car community. The drivers' identities remain a mystery to this day!"
        },
        {
            "question": "What iconic film inspired the Getaway in Stockholm concept?",
            "answers": [
                {"text": "C'était un Rendez-vous (1976) – the famous Paris drive film", "correct": True},
                {"text": "The Italian Job (1969)", "correct": False},
                {"text": "Bullitt (1968) with Steve McQueen", "correct": False},
                {"text": "The Fast and the Furious (2001)", "correct": False}
            ],
            "explanation": "Claude Lelouch's 'C'était un Rendez-vous' (1976) started everything – a real Ferrari driven at 140mph through Paris streets at dawn. The Getaway in Stockholm creators took this concept and created a SERIES! Both remain among the most thrilling driving footage ever filmed."
        },
        {
            "question": "Why are these videos considered cultural artifacts of car culture?",
            "answers": [
                {"text": "They capture raw automotive passion before the era of dashcams and social media", "correct": True},
                {"text": "They were sponsored by major car manufacturers", "correct": False},
                {"text": "They were used as police training videos", "correct": False},
                {"text": "They showed cars that no longer exist", "correct": False}
            ],
            "explanation": "Before YouTube, GoPros, and dashcams – the Getaway videos were shared on DVD and VHS among enthusiasts. They represent a pre-social-media era of car culture: raw, unfiltered, mysterious. You'll never see anything like this again in our surveillance age!"
        }
    ],

    # ─── TOKYO JOKIO (WWII PROPAGANDA) (4,085 views) ───
    "M0-tJK4H3lo": [
        {
            "question": "What type of cartoon is 'Tokyo Jokio' (1943)?",
            "answers": [
                {"text": "A WWII wartime propaganda cartoon by Warner Bros.", "correct": True},
                {"text": "A Japanese anime from the 1940s", "correct": False},
                {"text": "An educational documentary about Japan", "correct": False},
                {"text": "A children's comedy about a Japanese cat", "correct": False}
            ],
            "explanation": "Tokyo Jokio is a piece of WWII history – a propaganda cartoon made by Warner Bros. to boost American morale. It uses racist caricatures typical of wartime media. Today it serves as a historical document showing how animation was weaponized. History must be understood, not hidden!"
        },
        {
            "question": "Which Warner Bros. series produced this wartime cartoon?",
            "answers": [
                {"text": "Merrie Melodies / Looney Tunes", "correct": True},
                {"text": "Tom and Jerry", "correct": False},
                {"text": "Popeye the Sailor", "correct": False},
                {"text": "Mickey Mouse Shorts", "correct": False}
            ],
            "explanation": "Warner Bros.' Merrie Melodies created MANY WWII propaganda cartoons – featuring Bugs Bunny, Daffy Duck, and others in wartime settings. Hollywood's biggest studios ALL contributed to the war effort through animation. These cartoons reached millions in cinemas before feature films."
        },
        {
            "question": "Why do historians consider propaganda cartoons important to preserve?",
            "answers": [
                {"text": "They document how media shapes public opinion during wartime", "correct": True},
                {"text": "They contain artistic techniques not found elsewhere", "correct": False},
                {"text": "They were banned and therefore became rare collectors' items", "correct": False},
                {"text": "They predict future historical events", "correct": False}
            ],
            "explanation": "These cartoons are primary historical sources! They show EXACTLY how governments used entertainment to influence populations. Understanding propaganda techniques makes us better at recognizing manipulation TODAY. That's why preserving uncomfortable history is so important!"
        }
    ],

    # ─── PETER AND THE WOLF (4,041 views) ───
    "-623U3tgryM": [
        {
            "question": "Who composed the original music for 'Peter and the Wolf'?",
            "answers": [
                {"text": "Sergei Prokofiev in 1936", "correct": True},
                {"text": "Tchaikovsky in 1890", "correct": False},
                {"text": "Mozart as a children's piece", "correct": False},
                {"text": "Walt Disney's studio composers", "correct": False}
            ],
            "explanation": "Sergei Prokofiev composed Peter and the Wolf in just TWO WEEKS in 1936! His genius idea: each character is represented by a DIFFERENT instrument. Peter=strings, bird=flute, duck=oboe, cat=clarinet, wolf=horns. The most brilliant music education piece ever created!"
        },
        {
            "question": "What musical innovation makes 'Peter and the Wolf' unique?",
            "answers": [
                {"text": "Each character is represented by a specific musical instrument", "correct": True},
                {"text": "It was the first classical piece composed for children", "correct": False},
                {"text": "The audience votes on the ending", "correct": False},
                {"text": "It uses only percussion instruments", "correct": False}
            ],
            "explanation": "Pure genius! The bird is a FLUTE (high, quick notes), the duck is an OBOE (waddling sound), the cat is a CLARINET (sneaky, smooth), the grandfather is a BASSOON (grumpy, low), and the wolf is FRENCH HORNS (dark, powerful). Music IS storytelling! Millions of children learned orchestral instruments this way."
        },
        {
            "question": "How quickly did Prokofiev compose this masterpiece?",
            "answers": [
                {"text": "In only 2 weeks", "correct": True},
                {"text": "Over 5 years", "correct": False},
                {"text": "In 6 months", "correct": False},
                {"text": "It took his entire career", "correct": False}
            ],
            "explanation": "TWO WEEKS! Prokofiev was commissioned by the Central Children's Theatre in Moscow. He finished the entire score in 14 days. Ironically, the premiere was a disappointment – but the piece went on to become one of the most performed and beloved orchestral works in HISTORY!"
        }
    ],

    # ─── AIRSHIP DESTROYED (1909) (3,998 views) ───
    "3NagSoFaAwI": [
        {
            "question": "What makes 'Airship Destroyed' (1909) special in film history?",
            "answers": [
                {"text": "It's one of the earliest science fiction films ever made", "correct": True},
                {"text": "It documented a real airship disaster", "correct": False},
                {"text": "It was the first film with sound", "correct": False},
                {"text": "It was the most expensive film of 1909", "correct": False}
            ],
            "explanation": "This 1909 short is among the EARLIEST sci-fi films ever produced! Filmmakers were already imagining aerial warfare and destruction just 6 years after the Wright Brothers' first flight. Visionary cinema from over 115 years ago!"
        },
        {
            "question": "How did early filmmakers create 'special effects' in 1909?",
            "answers": [
                {"text": "Miniature models, double exposures, and stop-motion tricks", "correct": True},
                {"text": "Early CGI on mechanical computers", "correct": False},
                {"text": "They used real explosions only", "correct": False},
                {"text": "Hand-painted directly onto the film frames", "correct": False}
            ],
            "explanation": "Before CGI, filmmakers were INCREDIBLY creative! Miniature models on wires, multiple exposures (filming the same film twice), and stop-motion cuts created illusions that amazed audiences. Georges Méliès pioneered these techniques in France – every Marvel movie today owes him!"
        },
        {
            "question": "What was happening in REAL aviation when this film was made?",
            "answers": [
                {"text": "The Wright Brothers had only flown 6 years earlier in 1903", "correct": True},
                {"text": "Commercial airlines were already operating", "correct": False},
                {"text": "Airplanes had already crossed the Atlantic", "correct": False},
                {"text": "Military aviation was already established", "correct": False}
            ],
            "explanation": "Context is amazing! In 1909, aviation was BRAND NEW – the Wright Brothers flew just 6 years prior. Yet filmmakers were already imagining aerial combat and airship destruction! Science fiction has ALWAYS been ahead of science. This film predicted WWI aerial warfare 5 years early!"
        }
    ],

    # ─── 20,000 LEAGUES UNDER THE SEA (1916) (3,019 views) ───
    "LEM6FkBTDNs": [
        {
            "question": "What technological first does this 1916 film hold?",
            "answers": [
                {"text": "It contains the first UNDERWATER footage ever filmed", "correct": True},
                {"text": "It was the first film in color", "correct": False},
                {"text": "It had the first film soundtrack", "correct": False},
                {"text": "It was the first film over 2 hours long", "correct": False}
            ],
            "explanation": "This 1916 film contains some of the FIRST underwater cinematography in movie history! The Williamson brothers developed a special underwater viewing tube and camera housing. Audiences in 1916 had never seen the ocean floor – this was their Avatar moment!"
        },
        {
            "question": "Which famous author wrote the original novel?",
            "answers": [
                {"text": "Jules Verne in 1870", "correct": True},
                {"text": "H.G. Wells in 1895", "correct": False},
                {"text": "Edgar Allan Poe in 1845", "correct": False},
                {"text": "Arthur Conan Doyle in 1912", "correct": False}
            ],
            "explanation": "Jules Verne published '20,000 Leagues Under the Sea' in 1870 – predicting submarines, scuba diving, and underwater technology DECADES before they existed! The 1916 film adaptation brought his vision to screen just 16 years after the first practical submarine. Verne = the original futurist!"
        },
        {
            "question": "What year was the MORE famous Disney adaptation released?",
            "answers": [
                {"text": "1954, starring Kirk Douglas and James Mason", "correct": True},
                {"text": "1937, as Disney's second animated feature", "correct": False},
                {"text": "1968, with real submarine footage", "correct": False},
                {"text": "1975, directed by Steven Spielberg", "correct": False}
            ],
            "explanation": "Disney's 1954 live-action version won TWO Academy Awards and is a cinema classic! But this 1916 version came FIRST – 38 years earlier. Captain Nemo has been portrayed in over 20 film/TV adaptations, but these two remain the most iconic. Some stories are simply timeless!"
        }
    ],

    # ─── LITTLE NEMO (1911) - WINSOR McCay (2,871 views) ───
    "T8AnrW3H5i8": [
        {
            "question": "Why is Winsor McCay considered the 'Father of Animation'?",
            "answers": [
                {"text": "He drew 4,000+ frames BY HAND for 'Little Nemo', proving animation was art", "correct": True},
                {"text": "He invented the movie camera", "correct": False},
                {"text": "He created the first computer animation", "correct": False},
                {"text": "He founded Walt Disney Studios", "correct": False}
            ],
            "explanation": "Winsor McCay drew over 4,000 individual frames ON RICE PAPER – by himself! No team, no assistants. This 1911 film proved that hand-drawn images could move fluidly and tell stories. EVERY animated film – from Disney to Pixar – exists because McCay proved it possible!"
        },
        {
            "question": "What was Winsor McCay's 'day job' while revolutionizing animation?",
            "answers": [
                {"text": "Newspaper comic strip artist (Little Nemo in Slumberland)", "correct": True},
                {"text": "University professor of art", "correct": False},
                {"text": "Vaudeville magician", "correct": False},
                {"text": "He was a full-time filmmaker", "correct": False}
            ],
            "explanation": "McCay's 'Little Nemo in Slumberland' newspaper comic (1905-1914) was a MASTERPIECE of visual storytelling and Art Nouveau design. He animated his own comic characters as a SIDE PROJECT! His newspaper work alone would make him legendary – the animation was bonus genius!"
        },
        {
            "question": "How many drawings did McCay make for his later film 'Gertie the Dinosaur'?",
            "answers": [
                {"text": "About 10,000 drawings on rice paper", "correct": True},
                {"text": "About 500 drawings", "correct": False},
                {"text": "About 100 key poses only", "correct": False},
                {"text": "Over 50,000 drawings", "correct": False}
            ],
            "explanation": "TEN THOUSAND drawings – all by McCay's own hand! 'Gertie the Dinosaur' (1914) is considered the first cartoon with a distinctive animated PERSONALITY. McCay performed live alongside the projected film, pretending to interact with Gertie. The first interactive animation experience!"
        }
    ],

    # ─── FRANKENSTEIN (1910) - EDISON STUDIOS (2,131 views) ───
    "hPQN992PMUY": [
        {
            "question": "What makes this 1910 'Frankenstein' historically significant?",
            "answers": [
                {"text": "It's the FIRST horror film adaptation of a novel ever made", "correct": True},
                {"text": "It used the first ever makeup prosthetics", "correct": False},
                {"text": "It was directed by Thomas Edison personally", "correct": False},
                {"text": "It was the first film banned by censors", "correct": False}
            ],
            "explanation": "This 1910 EDISON STUDIOS production is the very first film adaptation of Mary Shelley's 'Frankenstein' (1818)! Made just 14 years after the first films existed. It was considered LOST for decades until a private collector's copy surfaced in the 1970s. A miraculous survival!"
        },
        {
            "question": "What company produced this legendary horror film?",
            "answers": [
                {"text": "Edison Studios – Thomas Edison's film company", "correct": True},
                {"text": "Universal Pictures", "correct": False},
                {"text": "MGM Studios", "correct": False},
                {"text": "Paramount Pictures", "correct": False}
            ],
            "explanation": "Thomas Edison – the inventor of the light bulb and phonograph – also produced HUNDREDS of films! His Edison Studios was one of the first movie companies in the world. This Frankenstein was just one of many films from his studio. Edison didn't just illuminate rooms – he illuminated cinema!"
        },
        {
            "question": "How was the Monster's creation scene filmed using 1910 technology?",
            "answers": [
                {"text": "They burned a puppet and played the film in REVERSE", "correct": True},
                {"text": "An actor wore makeup that took 8 hours to apply", "correct": False},
                {"text": "They used stop-motion clay animation", "correct": False},
                {"text": "They used a mirror trick to create the illusion", "correct": False}
            ],
            "explanation": "Brilliant 1910 ingenuity! They built a puppet, SET IT ON FIRE, filmed it burning to ashes – then played the footage BACKWARDS! The result: the Monster appears to form out of nothing. This reverse-filming trick was GROUNDBREAKING and predated modern VFX by 80 years!"
        }
    ],

    # ─── POPEYE: ANCIENT FISTORY (2,383 views) ───
    "unbwEeI4bEE": [
        {
            "question": "Where did Popeye FIRST appear – before becoming an animated star?",
            "answers": [
                {"text": "In the newspaper comic strip 'Thimble Theatre' in 1929", "correct": True},
                {"text": "In a Fleischer Brothers animated film in 1933", "correct": False},
                {"text": "In a radio play in 1925", "correct": False},
                {"text": "In a children's book in 1928", "correct": False}
            ],
            "explanation": "E.C. Segar created Popeye in 1929 for the comic strip 'Thimble Theatre' – which had ALREADY been running for 10 YEARS without him! Popeye was meant to be a one-time character, but readers loved him so much he took over the entire strip. The biggest 'guest star' in comic history!"
        },
        {
            "question": "What real-world effect did Popeye have on American children?",
            "answers": [
                {"text": "Spinach consumption increased by 33% among US children", "correct": True},
                {"text": "Children started wearing sailor hats to school", "correct": False},
                {"text": "Pipe smoking increased among teenagers", "correct": False},
                {"text": "Children demanded anchor tattoos", "correct": False}
            ],
            "explanation": "Popeye literally changed American DIETS! Spinach consumption rose 33% among US children. The town of Crystal City, Texas – the 'Spinach Capital' – erected a STATUE of Popeye in 1937 to thank him! A cartoon character that changed real eating habits. That's cultural impact!"
        },
        {
            "question": "What city erected a real statue of Popeye – and why?",
            "answers": [
                {"text": "Crystal City, Texas – the 'Spinach Capital of the World'", "correct": True},
                {"text": "New York – where the Fleischer Studios were located", "correct": False},
                {"text": "Hollywood – at the Walk of Fame", "correct": False},
                {"text": "Popeye, Illinois – a town named after the character", "correct": False}
            ],
            "explanation": "Crystal City, Texas erected a Popeye statue in 1937 because the character's spinach obsession BOOSTED their spinach industry! The local economy literally benefited from a cartoon. It's the world's first monument to a comic character's influence on real commerce!"
        }
    ],

    # ─── SCARLET STREET - Fritz Lang (2,476 views) ───
    "_aUNgDJoWoU": [
        {
            "question": "Who directed 'Scarlet Street' (1945)?",
            "answers": [
                {"text": "Fritz Lang – the legendary German-American director", "correct": True},
                {"text": "Alfred Hitchcock", "correct": False},
                {"text": "Orson Welles", "correct": False},
                {"text": "Billy Wilder", "correct": False}
            ],
            "explanation": "Fritz Lang – the genius behind 'Metropolis' (1927) and 'M' (1931) – fled Nazi Germany in 1934 and reinvented himself in Hollywood! 'Scarlet Street' is one of his darkest American films. Lang's visual style influenced film noir, thriller, and every dark crime movie since!"
        },
        {
            "question": "What genre does 'Scarlet Street' define?",
            "answers": [
                {"text": "Film Noir – dark crime drama with moral ambiguity", "correct": True},
                {"text": "Western", "correct": False},
                {"text": "Musical comedy", "correct": False},
                {"text": "Science fiction", "correct": False}
            ],
            "explanation": "Film Noir = French for 'dark film.' Low-key lighting, morally ambiguous characters, femme fatales, and tragic endings define the genre. Fritz Lang's expressionist background made him PERFECT for noir. 'Scarlet Street' is so dark it was banned in several US cities upon release!"
        },
        {
            "question": "What was controversial about 'Scarlet Street' upon its release?",
            "answers": [
                {"text": "It was banned in several cities for its dark, morally complex ending", "correct": True},
                {"text": "It used real crime footage", "correct": False},
                {"text": "The actors refused to promote it", "correct": False},
                {"text": "It was filmed without studio permission", "correct": False}
            ],
            "explanation": "Several US cities BANNED 'Scarlet Street' because the villain essentially gets away unpunished! In 1945, the Production Code demanded good triumphs over evil. Lang's film broke this rule – showing that crime sometimes DOES pay. Revolutionary (and disturbing) for its time!"
        }
    ],

    # ─── COMMODORE 64 DOCUMENTARY (2,573 views) ───
    "j4r3bPPQza0": [
        {
            "question": "What record does the Commodore 64 hold in computer history?",
            "answers": [
                {"text": "Best-selling single computer model of all time", "correct": True},
                {"text": "First computer with a color screen", "correct": False},
                {"text": "First computer to connect to the internet", "correct": False},
                {"text": "Smallest computer ever built at the time", "correct": False}
            ],
            "explanation": "The Commodore 64 sold between 12.5 and 17 MILLION units – the best-selling single computer model in HISTORY! Produced from 1982-1994, it brought computing to ordinary families. At just $595, it cost less than most competitors' keyboards alone. The people's computer!"
        },
        {
            "question": "What year was the Commodore 64 introduced?",
            "answers": [
                {"text": "1982", "correct": True},
                {"text": "1976", "correct": False},
                {"text": "1990", "correct": False},
                {"text": "1984", "correct": False}
            ],
            "explanation": "January 1982 at the Consumer Electronics Show! The '64' stands for 64 kilobytes of RAM. For comparison, your phone today has about 100,000 TIMES more RAM. Yet the C64 ran thousands of games, taught a generation to program, and spawned the home computer revolution!"
        },
        {
            "question": "What does the '64' in Commodore 64 refer to?",
            "answers": [
                {"text": "64 kilobytes of RAM memory", "correct": True},
                {"text": "It was the company's 64th product", "correct": False},
                {"text": "It could display 64 colors", "correct": False},
                {"text": "It weighed 6.4 pounds", "correct": False}
            ],
            "explanation": "64 KB of RAM was MASSIVE in 1982! Most competitors had 1-16 KB. That extra memory meant better games, better graphics, and better sound (the legendary SID chip!). The C64 launched careers of countless programmers who are TODAY's tech industry leaders."
        }
    ],

    # ─── RUDOLPH THE RED-NOSED REINDEER (1948) ───
    "YzvGVo8mAQM": [
        {
            "question": "How did Rudolph originally start – before becoming a cartoon?",
            "answers": [
                {"text": "As a 1939 coloring book for a department store", "correct": True},
                {"text": "As a Disney animated feature", "correct": False},
                {"text": "As a Christmas radio play", "correct": False},
                {"text": "As a children's book by Dr. Seuss", "correct": False}
            ],
            "explanation": "Rudolph was created in 1939 by Robert L. May for Montgomery Ward department stores as a FREE coloring book! 2.4 million copies were given away the first year. The famous song came 10 years later in 1949, sung by Gene Autry – selling 25 million copies!"
        },
        {
            "question": "What makes the Rudolph story so psychologically powerful?",
            "answers": [
                {"text": "The 'outcast becomes hero' narrative resonates with everyone", "correct": True},
                {"text": "It was the first Christmas cartoon ever made", "correct": False},
                {"text": "Santa is portrayed as an action hero", "correct": False},
                {"text": "The animation uses real snow footage", "correct": False}
            ],
            "explanation": "Rudolph's power is universal psychology: EVERY person has felt like an outsider. The message that your unique 'flaw' (the red nose) becomes your greatest STRENGTH is timeless. It's why Rudolph remains one of the most beloved Christmas characters 85+ years later!"
        },
        {
            "question": "How many copies of the Rudolph song were sold?",
            "answers": [
                {"text": "25 million – making it the second best-selling single ever", "correct": True},
                {"text": "About 1 million copies", "correct": False},
                {"text": "5 million copies", "correct": False},
                {"text": "100 million copies", "correct": False}
            ],
            "explanation": "Gene Autry's 'Rudolph the Red-Nosed Reindeer' (1949) sold 25 MILLION copies – second only to 'White Christmas' by Bing Crosby! A free department store coloring book from 1939 became one of the best-selling songs in HISTORY. That's the power of a great story!"
        }
    ],
}


def enhance_database():
    """Load psychology DB and add individual top-performer quizzes."""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'quiz_database_psychology_v3.json')
    db_path = os.path.normpath(db_path)
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"Loaded {len(db['videos'])} videos from psychology DB")
    
    enhanced_count = 0
    for video in db['videos']:
        vid = video['video_id']
        if vid in INDIVIDUAL_QUIZZES:
            video['quizzes'] = INDIVIDUAL_QUIZZES[vid]
            enhanced_count += 1
            print(f"  Enhanced: {video['title'][:50]:50s} ({video['views']:>6,} views)")
    
    # Update meta
    total_q = sum(len(v['quizzes']) for v in db['videos'])
    total_a = sum(sum(len(q['answers']) for q in v['quizzes']) for v in db['videos'])
    db['_meta']['total_quizzes'] = total_q
    db['_meta']['total_answers'] = total_a
    db['_meta']['individual_top_performer_quizzes'] = enhanced_count
    db['_meta']['updated'] = '2026-02-14'
    
    # Validate
    errors = 0
    max_expl = 0
    for video in db['videos']:
        for qi, quiz in enumerate(video['quizzes']):
            correct = sum(1 for a in quiz['answers'] if a.get('correct'))
            if correct != 1:
                print(f"  ERROR: {video['video_id']} Q{qi+1}: {correct} correct answers!")
                errors += 1
            if len(quiz['answers']) < 2 or len(quiz['answers']) > 4:
                print(f"  ERROR: {video['video_id']} Q{qi+1}: {len(quiz['answers'])} answers!")
                errors += 1
            el = len(quiz['explanation'])
            if el > 500:
                print(f"  ERROR: {video['video_id']} Q{qi+1}: explanation {el} chars (>500)!")
                errors += 1
            max_expl = max(max_expl, el)
    
    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"RESULTS:")
    print(f"  Total videos:    {len(db['videos'])}")
    print(f"  Total quizzes:   {total_q}")
    print(f"  Total answers:   {total_a}")
    print(f"  Enhanced (individual): {enhanced_count} top performers")
    print(f"  Series template:       {len(db['videos']) - enhanced_count} videos")
    print(f"  Longest explanation:   {max_expl} chars (limit: 500)")
    print(f"  Errors:          {errors}")
    print(f"\n  Saved to: {db_path}")


if __name__ == '__main__':
    enhance_database()
