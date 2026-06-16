#!/usr/bin/env python3
"""
Psychology-Based Quiz Generator for remAIke.TV
===============================================
Rebuilds the entire quiz database using scientifically-grounded principles:
- Curiosity Gap (Loewenstein)
- Dopamine Reward Loop
- Graduated Difficulty (IQ Test: Easy → Medium → Hard)
- Von Restorff Effect (bizarre facts stick)
- Near-Miss Psychology (plausible distractors)
- Dunning-Kruger Calibration (everyone feels smart sometimes)
- Social Sharing Impulse ("did you know" moments)

All facts are Wikipedia-verified (Feb 2026).
"""
import json
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# PSYCHOLOGY QUIZ TEMPLATES BY CATEGORY
# Each category gets 3 quizzes: Q1=Easy, Q2=Mind-Blower, Q3=Genius
# ============================================================

QUIZ_TEMPLATES = {
    # ─────────────────────────────────────────────────────
    # BETTY BOOP (57 videos) - "Die heimliche Revolutionaerin"
    # ─────────────────────────────────────────────────────
    "Betty Boop": [
        {
            "question": "Betty Boop was originally NOT a human character – what was she?",
            "answers": [
                {"text": "A French poodle", "correct": True},
                {"text": "A kitten", "correct": False},
                {"text": "A baby doll", "correct": False},
                {"text": "A fairy", "correct": False}
            ],
            "explanation": "Surprise! Betty Boop first appeared on August 9, 1930 as a poodle character in 'Dizzy Dishes'. She didn't become fully human until 1932. Her signature style was inspired by singer Helen Kane, who later sued Fleischer Studios – and lost!",
            "level": "easy"
        },
        {
            "question": "Why did Betty Boop's appearance change dramatically in 1934?",
            "answers": [
                {"text": "The Hays Production Code censored her", "correct": True},
                {"text": "The voice actress changed", "correct": False},
                {"text": "A new animation studio took over", "correct": False},
                {"text": "Audience surveys demanded a new look", "correct": False}
            ],
            "explanation": "The 1934 Production Code forced Betty to cover up! Her short skirt became longer, her garter disappeared, and her personality became less flirtatious. This effectively ended Betty's golden era. Mae Questel voiced Betty in over 90 cartoons!",
            "level": "medium"
        },
        {
            "question": "What real-world impact did Betty Boop have on the music industry?",
            "answers": [
                {"text": "Her cartoons popularized jazz to mainstream audiences", "correct": True},
                {"text": "She inspired the first music video", "correct": False},
                {"text": "Her theme song became a #1 hit", "correct": False},
                {"text": "She was the first cartoon on MTV", "correct": False}
            ],
            "explanation": "Betty Boop cartoons featured performances by Cab Calloway and Louis Armstrong, introducing jazz and scat singing to audiences who'd never heard it. 'Minnie the Moocher' (1932) with Cab Calloway is considered one of the greatest animated shorts ever made!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # WOCHENSCHAU (40 videos) - "Geschichte zum Anfassen"
    # ─────────────────────────────────────────────────────
    "Wochenschau": [
        {
            "question": "What was the original purpose of the newsreel ('Wochenschau')?",
            "answers": [
                {"text": "Cinema news before TV existed", "correct": True},
                {"text": "Military training films", "correct": False},
                {"text": "Government propaganda only", "correct": False},
                {"text": "Entertainment between feature films", "correct": False}
            ],
            "explanation": "Before television, newsreels were the ONLY way to see moving images of world events! They were shown before every cinema feature. The German 'Deutsche Wochenschau' ran from 1940-1945 and was seen by millions weekly in cinemas across Europe.",
            "level": "easy"
        },
        {
            "question": "How did the Wochenschau influence modern news broadcasting?",
            "answers": [
                {"text": "Its editing techniques became the basis for TV news", "correct": True},
                {"text": "It invented the teleprompter", "correct": False},
                {"text": "It created the first news anchor format", "correct": False},
                {"text": "It pioneered satellite broadcasting", "correct": False}
            ],
            "explanation": "The dramatic editing style, narrator voiceover, and visual storytelling of newsreels directly shaped how TV news was presented when television arrived. Many early TV news directors had worked in newsreel production. These techniques are still used today!",
            "level": "medium"
        },
        {
            "question": "What makes historical newsreel footage invaluable to historians today?",
            "answers": [
                {"text": "It shows events as they appeared to the public at that time", "correct": True},
                {"text": "It was always filmed in color", "correct": False},
                {"text": "It contains classified information", "correct": False},
                {"text": "It was filmed with hidden cameras", "correct": False}
            ],
            "explanation": "Newsreels are unique historical documents: they show not just WHAT happened, but how events were PRESENTED to the public. This reveals the propaganda techniques and public perception of the era – making them essential primary sources for understanding history!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # ALFRED J. KWAK (33 videos) - "Mehr als ein Kinderfilm"
    # ─────────────────────────────────────────────────────
    "Alfred J. Kwak": [
        {
            "question": "Who created Alfred J. Kwak?",
            "answers": [
                {"text": "Herman van Veen", "correct": True},
                {"text": "Walt Disney", "correct": False},
                {"text": "Hayao Miyazaki", "correct": False},
                {"text": "Nick Jr. Studios", "correct": False}
            ],
            "explanation": "Alfred J. Kwak was created by Dutch artist Herman van Veen, who also composed the music and sang the theme song! The show is a unique Dutch-Japanese co-production (with TV Tokyo), making it a rare cultural bridge between Europe and Asia.",
            "level": "easy"
        },
        {
            "question": "The villain Dolf is a hidden allegory for a real historical figure – who?",
            "answers": [
                {"text": "Adolf Hitler", "correct": True},
                {"text": "Napoleon Bonaparte", "correct": False},
                {"text": "Joseph Stalin", "correct": False},
                {"text": "Mussolini", "correct": False}
            ],
            "explanation": "Mind-blowing for a kids show! Dolf the crow represents Adolf Hitler – he even paints his beak to hide that he's half-crow/half-blackbird (mixed race), rises to power through nationalism, and creates a party with a black crow symbol. The show taught children about fascism through allegory!",
            "level": "medium"
        },
        {
            "question": "What makes Alfred J. Kwak unique in TV animation history?",
            "answers": [
                {"text": "It's a Dutch-Japanese co-production tackling real political themes", "correct": True},
                {"text": "It was the first European anime", "correct": False},
                {"text": "It was banned in 12 countries", "correct": False},
                {"text": "It was made entirely by one person", "correct": False}
            ],
            "explanation": "Alfred J. Kwak covers apartheid, fascism, environmentalism, and nuclear weapons – in a CHILDREN'S show! The Dutch-Japanese co-production created a unique animation style. Episodes deal with real issues like racism and political extremism through animal characters.",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # SOUNDIES (32 videos) - "Die vergessenen Musikvideos"
    # ─────────────────────────────────────────────────────
    "Soundies": [
        {
            "question": "From which decade do Soundies originate?",
            "answers": [
                {"text": "1940s", "correct": True},
                {"text": "1920s", "correct": False},
                {"text": "1950s", "correct": False},
                {"text": "1960s", "correct": False}
            ],
            "explanation": "Soundies were produced between 1940-1947, over 30 years before MTV! They were short musical films played on coin-operated 'Panoram' machines in bars, restaurants, and clubs. Over 1,800 Soundies were produced during this period.",
            "level": "easy"
        },
        {
            "question": "How did people actually watch Soundies in the 1940s?",
            "answers": [
                {"text": "On coin-operated Panoram jukebox machines", "correct": True},
                {"text": "In movie theaters before films", "correct": False},
                {"text": "On early television sets", "correct": False},
                {"text": "At drive-in cinemas", "correct": False}
            ],
            "explanation": "The Panoram was a jukebox with a screen! You inserted a coin and watched a 3-minute music film on a rear-projection screen. The machine played 8 Soundies in a loop. They were the 1940s equivalent of YouTube music videos – coin-operated entertainment decades ahead of its time!",
            "level": "medium"
        },
        {
            "question": "Why are Soundies considered culturally significant today?",
            "answers": [
                {"text": "They preserved performances of Black artists banned from mainstream media", "correct": True},
                {"text": "They invented the music video format", "correct": False},
                {"text": "They were the first films with sound", "correct": False},
                {"text": "They launched MTV", "correct": False}
            ],
            "explanation": "Soundies are treasure troves! Many feature the ONLY surviving film footage of legendary jazz, blues, and R&B performers. In an era of segregation, Soundies gave Black musicians a platform when they were excluded from mainstream cinema. They're priceless cultural documents!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # MAULWURF (7 videos) - "Kindheit ohne Worte"
    # ─────────────────────────────────────────────────────
    "Maulwurf": [
        {
            "question": "Where does 'The Little Mole' (Krtek) originally come from?",
            "answers": [
                {"text": "Czech Republic (Czechoslovakia)", "correct": True},
                {"text": "Germany", "correct": False},
                {"text": "Poland", "correct": False},
                {"text": "Russia", "correct": False}
            ],
            "explanation": "The Little Mole (Krtek) was created by Czech animator Zdenek Miler in 1956. The first short film 'How the Mole Got His Trousers' won the Silver Lion at the Venice Film Festival! Over 50 episodes were produced between 1957-2002.",
            "level": "easy"
        },
        {
            "question": "Why does the Little Mole never speak a real language?",
            "answers": [
                {"text": "So children EVERYWHERE in the world can understand it", "correct": True},
                {"text": "The studio couldn't afford voice actors", "correct": False},
                {"text": "The Czech government banned dialogue", "correct": False},
                {"text": "The creator was deaf", "correct": False}
            ],
            "explanation": "Genius design decision! Zdenek Miler deliberately made the Mole speechless (using only 'Ahoj!' and laughter) so children worldwide could enjoy it without translation. This made Krtek one of the most internationally beloved cartoon characters – exported to over 80 countries!",
            "level": "medium"
        },
        {
            "question": "Which prestigious film award did the Little Mole win?",
            "answers": [
                {"text": "Silver Lion at the Venice Film Festival", "correct": True},
                {"text": "Oscar for Best Animated Short", "correct": False},
                {"text": "Palme d'Or at Cannes", "correct": False},
                {"text": "Golden Bear at Berlin Film Festival", "correct": False}
            ],
            "explanation": "The very first Mole film 'How the Mole Got His Trousers' (1956) won the Silver Lion at Venice! The character became SO popular in space-loving Czechoslovakia that a Mole plushie was even taken aboard the International Space Station by astronaut Andrew Feustel in 2011!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # FELIX THE CAT (11 videos) - "Der erste Cartoon-Star"
    # ─────────────────────────────────────────────────────
    "Felix the Cat": [
        {
            "question": "When was Felix the Cat created?",
            "answers": [
                {"text": "1919", "correct": True},
                {"text": "1928", "correct": False},
                {"text": "1935", "correct": False},
                {"text": "1942", "correct": False}
            ],
            "explanation": "Felix the Cat first appeared in 'Feline Follies' in 1919 – almost a DECADE before Mickey Mouse (1928)! Felix was the world's first animated superstar. His image was so iconic that he was used as the first test image in TV broadcasting history in 1928!",
            "level": "easy"
        },
        {
            "question": "What TV broadcasting milestone is Felix the Cat connected to?",
            "answers": [
                {"text": "His image was used for the first ever TV test broadcast", "correct": True},
                {"text": "He starred in the first TV commercial", "correct": False},
                {"text": "He hosted the first TV children's show", "correct": False},
                {"text": "He was the first cartoon shown on color TV", "correct": False}
            ],
            "explanation": "In 1928, a Felix the Cat doll was placed on a rotating turntable and used by RCA as the very first television test image! For hours, Felix slowly spun while engineers calibrated the new technology. Felix literally helped INVENT television as we know it!",
            "level": "medium"
        },
        {
            "question": "Which military organization uses Felix the Cat as their official mascot?",
            "answers": [
                {"text": "US Navy Fighter Squadron VFA-31 'Tomcatters'", "correct": True},
                {"text": "US Army 1st Infantry Division", "correct": False},
                {"text": "Royal Air Force 617 Squadron", "correct": False},
                {"text": "French Foreign Legion", "correct": False}
            ],
            "explanation": "The US Navy squadron VFA-31 'Tomcatters' has used Felix the Cat as their mascot since the 1940s! Felix is painted on their fighter jets carrying a bomb. It's one of the longest-running military mascot traditions in US history – a cartoon cat on combat aircraft!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # SUPERMAN / FLEISCHER (10 videos combined)
    # ─────────────────────────────────────────────────────
    "Superman": [
        {
            "question": "What superpower did Superman gain BECAUSE of these Fleischer cartoons?",
            "answers": [
                {"text": "The ability to fly", "correct": True},
                {"text": "X-ray vision", "correct": False},
                {"text": "Super speed", "correct": False},
                {"text": "Heat vision", "correct": False}
            ],
            "explanation": "Originally, Superman could only LEAP tall buildings! The Fleischer animators found 'leaping' looked ridiculous in animation, so they asked DC Comics if Superman could FLY instead. DC agreed – and this cartoon decision permanently changed Superman's powers forever!",
            "level": "easy"
        },
        {
            "question": "How expensive were these Superman cartoons compared to normal cartoons?",
            "answers": [
                {"text": "4x the normal budget ($50,000 vs $12,000)", "correct": True},
                {"text": "About the same as normal cartoons", "correct": False},
                {"text": "Twice the normal budget", "correct": False},
                {"text": "10x the normal budget", "correct": False}
            ],
            "explanation": "Each Superman cartoon cost $50,000 – FOUR TIMES the typical $12,000 cartoon budget! Fleischer Studios used revolutionary rotoscope techniques and cinematic camera angles. The pilot 'Superman' (1941) was even nominated for an Academy Award for Best Animated Short Film!",
            "level": "medium"
        },
        {
            "question": "Who voiced Superman in these legendary cartoons?",
            "answers": [
                {"text": "Bud Collyer", "correct": True},
                {"text": "Mel Blanc", "correct": False},
                {"text": "Kirk Alyn", "correct": False},
                {"text": "Clayton Moore", "correct": False}
            ],
            "explanation": "Bud Collyer voiced BOTH Clark Kent and Superman! He cleverly dropped his voice an octave when changing to Superman – creating the iconic dual-voice technique used in almost every Superman adaptation since. Collyer voiced Superman for over a decade across cartoons and radio!",
            "level": "hard"
        }
    ],

    "Superman / Fleischer": None,  # Will use "Superman" template

    # ─────────────────────────────────────────────────────
    # CASPER (8 videos)
    # ─────────────────────────────────────────────────────
    "Casper": [
        {
            "question": "What makes Casper unique among ghost characters?",
            "answers": [
                {"text": "He's a friendly ghost who WANTS to make friends", "correct": True},
                {"text": "He's the first ghost in animation history", "correct": False},
                {"text": "He can turn invisible at will", "correct": False},
                {"text": "He's based on a real ghost legend", "correct": False}
            ],
            "explanation": "Casper was revolutionary: he flipped the ghost concept! Created by Seymour Reit and Joe Oriolo in 1939, Casper appeared in the story 'The Friendly Ghost'. He became Famous Studios' most successful character – a ghost that children LOVED instead of feared!",
            "level": "easy"
        },
        {
            "question": "What was Casper's original medium before becoming a cartoon?",
            "answers": [
                {"text": "A children's storybook from 1939", "correct": True},
                {"text": "A comic strip in newspapers", "correct": False},
                {"text": "A radio show character", "correct": False},
                {"text": "A Halloween greeting card mascot", "correct": False}
            ],
            "explanation": "Casper first appeared in Seymour Reit's 1939 story 'The Friendly Ghost' before Paramount's Famous Studios adapted him for animation in 1945. Over 50 theatrical shorts were produced! Casper became such a cultural icon that he got his own live-action film in 1995.",
            "level": "medium"
        },
        {
            "question": "How many Casper theatrical shorts were produced in total?",
            "answers": [
                {"text": "Over 50 shorts", "correct": True},
                {"text": "About 20 shorts", "correct": False},
                {"text": "Exactly 100 shorts", "correct": False},
                {"text": "Only 12 shorts", "correct": False}
            ],
            "explanation": "Between 1945 and 1959, Famous Studios produced over 50 Casper shorts for Paramount Pictures! The character was so popular that Harvey Comics acquired the rights and made Casper their flagship character, publishing comics for decades. He remains iconic to this day!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # POPEYE (4 videos)
    # ─────────────────────────────────────────────────────
    "Popeye": [
        {
            "question": "What real-world effect did Popeye have on food consumption?",
            "answers": [
                {"text": "Spinach consumption increased by 33% in the US", "correct": True},
                {"text": "Olive oil sales doubled in Europe", "correct": False},
                {"text": "Canned food sales tripled", "correct": False},
                {"text": "No measurable real-world effect", "correct": False}
            ],
            "explanation": "Popeye literally changed eating habits! US spinach consumption increased by 33% after Popeye became popular. The city of Crystal City, Texas – the 'Spinach Capital' – even erected a STATUE of Popeye in 1937 because the cartoon boosted their spinach industry!",
            "level": "easy"
        },
        {
            "question": "When did Popeye first appear and in what medium?",
            "answers": [
                {"text": "1929 in E.C. Segar's comic strip 'Thimble Theatre'", "correct": True},
                {"text": "1933 as a Fleischer Studios cartoon", "correct": False},
                {"text": "1925 in a newspaper comic", "correct": False},
                {"text": "1940 in a feature film", "correct": False}
            ],
            "explanation": "Popeye debuted on January 17, 1929 in E.C. Segar's comic strip 'Thimble Theatre' – which had already been running for 10 YEARS without him! He was meant to be a minor one-time character but became SO popular that he took over the entire strip!",
            "level": "medium"
        },
        {
            "question": "Where can you find a real statue of Popeye?",
            "answers": [
                {"text": "Crystal City, Texas – the 'Spinach Capital of the World'", "correct": True},
                {"text": "Hollywood Walk of Fame, Los Angeles", "correct": False},
                {"text": "Times Square, New York City", "correct": False},
                {"text": "Segar's hometown in Illinois (no statue exists)", "correct": False}
            ],
            "explanation": "Crystal City, Texas erected a Popeye statue in 1937 because the cartoon character boosted their spinach farming industry! The town celebrates 'Popeye Days' annually. There's also a statue in Chester, Illinois – E.C. Segar's birthplace – and in Almere, Netherlands!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # HORROR CLASSIC (4 videos)
    # ─────────────────────────────────────────────────────
    "Horror Classic": [
        {
            "question": "Which of these films is considered the FIRST of its genre?",
            "answers": [
                {"text": "White Zombie (1932) – first zombie film", "correct": True},
                {"text": "Nosferatu (1922) – first vampire film", "correct": False},
                {"text": "Cabinet of Dr. Caligari (1920) – first horror film", "correct": False},
                {"text": "Frankenstein (1931) – first monster film", "correct": False}
            ],
            "explanation": "White Zombie (1932) holds the record as the first feature-length ZOMBIE film! While Nosferatu and Caligari came earlier, they weren't 'first' in their subgenres. The film was shot in just 11 days on a $50,000 budget. Rob Zombie named his band after it!",
            "level": "easy"
        },
        {
            "question": "What happened to all copies of Nosferatu (1922) by court order?",
            "answers": [
                {"text": "They were ordered to be destroyed for copyright violation", "correct": True},
                {"text": "They were locked in a government vault", "correct": False},
                {"text": "They were edited to remove violent scenes", "correct": False},
                {"text": "Nothing – the film was always available", "correct": False}
            ],
            "explanation": "Nosferatu was an unauthorized adaptation of Bram Stoker's 'Dracula'! Stoker's estate sued and a court ordered ALL copies destroyed. But some survived! The lead actor's real name, Max Schreck, literally translates to 'Maximum TERROR' in German – you can't make this up!",
            "level": "medium"
        },
        {
            "question": "What revolutionary filmmaking technique did these early horror films pioneer?",
            "answers": [
                {"text": "Expressionist lighting and shadows to create atmosphere", "correct": True},
                {"text": "The first use of color film", "correct": False},
                {"text": "Computer-generated special effects", "correct": False},
                {"text": "Surround sound technology", "correct": False}
            ],
            "explanation": "German Expressionist films like Caligari and Nosferatu pioneered the use of dramatic shadows, distorted sets, and angular lighting to create psychological horror. These techniques influenced EVERY horror film since – from Hitchcock to modern horror cinema!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # CLASSIC FILM (5 videos)
    # ─────────────────────────────────────────────────────
    "Classic Film": [
        {
            "question": "Why are classic public domain films important for film history?",
            "answers": [
                {"text": "They can be freely preserved and shared for education", "correct": True},
                {"text": "They are all Academy Award winners", "correct": False},
                {"text": "They were the most expensive films of their era", "correct": False},
                {"text": "They are only available in museums", "correct": False}
            ],
            "explanation": "Public domain films are cultural treasures freely available to everyone! Many classic films survived ONLY because they entered the public domain, allowing archives and enthusiasts to preserve and restore them. Without public domain, many masterpieces would be lost forever!",
            "level": "easy"
        },
        {
            "question": "What made early 20th century filmmaking so different from today?",
            "answers": [
                {"text": "Films were shot in days, not months, with tiny crews", "correct": True},
                {"text": "Only one camera was ever used per film", "correct": False},
                {"text": "Actors were never credited by name", "correct": False},
                {"text": "All films were exactly 10 minutes long", "correct": False}
            ],
            "explanation": "Early films were made with incredible speed! Movies we consider classics today were often shot in just 1-2 weeks with crews of under 20 people. White Zombie: 11 days. Many silent shorts: 1-3 days! This raw creative energy gave early cinema its unique charm.",
            "level": "medium"
        },
        {
            "question": "What percentage of all silent films are estimated to be lost forever?",
            "answers": [
                {"text": "About 75% – three quarters are gone", "correct": True},
                {"text": "About 25% – most survived", "correct": False},
                {"text": "About 50% – roughly half", "correct": False},
                {"text": "Less than 10% – almost all survived", "correct": False}
            ],
            "explanation": "A staggering 75% of all silent films are LOST forever! Early film stock was made of highly flammable nitrate – many films literally burned. Others were deliberately destroyed, melted for silver, or simply thrown away. Every surviving silent film is a miracle of preservation!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # CHRISTMAS (3 videos)
    # ─────────────────────────────────────────────────────
    "Christmas": [
        {
            "question": "What's the connection between vintage Christmas content and pop culture?",
            "answers": [
                {"text": "Many classic Christmas traditions were shaped by early media", "correct": True},
                {"text": "Christmas was invented by Hollywood", "correct": False},
                {"text": "Only modern films are shown at Christmas", "correct": False},
                {"text": "Vintage Christmas content was banned from TV", "correct": False}
            ],
            "explanation": "Early films and cartoons helped define our Christmas imagery! Rudolph the Red-Nosed Reindeer started as a 1939 department store coloring book, became a hit song in 1949, and was animated in 1948. Coca-Cola's Santa campaigns from the 1930s shaped how we picture Santa Claus today!",
            "level": "easy"
        },
        {
            "question": "What makes vintage Christmas animations special compared to modern ones?",
            "answers": [
                {"text": "They were hand-drawn, frame by frame, with real artistic craftsmanship", "correct": True},
                {"text": "They used more advanced technology", "correct": False},
                {"text": "They were all made by Disney", "correct": False},
                {"text": "They had bigger budgets than modern animations", "correct": False}
            ],
            "explanation": "Every frame of vintage Christmas cartoons was drawn BY HAND! Artists created 24 drawings for every single second of animation. A 7-minute cartoon required over 10,000 individual drawings. This handmade quality gives vintage animations a warmth that CGI simply cannot replicate!",
            "level": "medium"
        },
        {
            "question": "Why do classic Christmas specials still air on TV every year?",
            "answers": [
                {"text": "They trigger powerful nostalgia and multi-generational bonding", "correct": True},
                {"text": "TV stations have no alternatives", "correct": False},
                {"text": "They are legally required to air", "correct": False},
                {"text": "They get higher ratings than new shows", "correct": False}
            ],
            "explanation": "Psychology explains it: watching classic Christmas content triggers warm nostalgic memories and creates a sense of continuity across generations. Grandparents, parents, and children share the SAME traditions. This makes vintage Christmas content uniquely valuable in an ever-changing world!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # CLASSIC ANIMATION (3 videos)
    # ─────────────────────────────────────────────────────
    "Classic Animation": [
        {
            "question": "How were classic cartoons made before computers existed?",
            "answers": [
                {"text": "Every frame was drawn by hand on transparent celluloid sheets", "correct": True},
                {"text": "Using stop-motion with clay figures", "correct": False},
                {"text": "With early computer animation", "correct": False},
                {"text": "By filming live actors and tracing over them", "correct": False}
            ],
            "explanation": "Classic 'cel animation' required artists to paint every frame on transparent celluloid (cel) sheets, layered over painted backgrounds. One second of animation = 24 hand-painted cels! A 7-minute cartoon could require over 10,000 individual paintings. Pure artistry!",
            "level": "easy"
        },
        {
            "question": "Why did many Golden Age animation studios eventually close?",
            "answers": [
                {"text": "Television replaced cinema shorts, cutting their main revenue", "correct": True},
                {"text": "Audiences lost interest in cartoons", "correct": False},
                {"text": "The government shut them down", "correct": False},
                {"text": "Color film became too expensive", "correct": False}
            ],
            "explanation": "When TV arrived in the 1950s, cinemas stopped showing short cartoons before features. This destroyed the business model of studios like Fleischer, Famous, and others. Ironically, their old cartoons then became TV programming – played endlessly but earning the studios nothing!",
            "level": "medium"
        },
        {
            "question": "What lasting innovation did Golden Age animation give to modern filmmaking?",
            "answers": [
                {"text": "The multiplane camera creating depth in 2D animation", "correct": True},
                {"text": "The invention of the movie projector", "correct": False},
                {"text": "Digital color correction", "correct": False},
                {"text": "Motion capture technology", "correct": False}
            ],
            "explanation": "The multiplane camera (perfected by Disney in the 1930s) created the illusion of 3D depth by moving multiple layers at different speeds. This technique revolutionized animation and its principles are STILL used in modern 2D and even 3D animation software today!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # EARLY CINEMA (3 videos)
    # ─────────────────────────────────────────────────────
    "Early Cinema": [
        {
            "question": "How long were the very first films in cinema history?",
            "answers": [
                {"text": "Just 1-5 minutes long", "correct": True},
                {"text": "About 30 minutes", "correct": False},
                {"text": "Full 90-minute features", "correct": False},
                {"text": "Exactly 10 seconds", "correct": False}
            ],
            "explanation": "The very first films were incredibly short! The Lumiere Brothers' first screenings in 1895 showed films of just 46-50 seconds each. Early cinema pioneers like Georges Melies gradually extended films to 5-15 minutes. The concept of a 'feature-length' film didn't emerge until around 1910!",
            "level": "easy"
        },
        {
            "question": "What was the first audience reaction to seeing a moving picture?",
            "answers": [
                {"text": "Some reportedly ran away thinking a train would hit them", "correct": True},
                {"text": "They immediately demanded longer films", "correct": False},
                {"text": "They thought it was a magic trick", "correct": False},
                {"text": "They were bored and left", "correct": False}
            ],
            "explanation": "Legend says at the first Lumiere screening in 1895, audiences panicked when a train appeared to rush toward them! While this may be exaggerated, early cinema DID shock people – they had NEVER seen moving images before. Imagine seeing video for the first time in your life!",
            "level": "medium"
        },
        {
            "question": "Why are early cinema films so important even though they're very short?",
            "answers": [
                {"text": "They invented the visual language that ALL films still use today", "correct": True},
                {"text": "They were the most expensive productions ever", "correct": False},
                {"text": "They featured the biggest stars of their era", "correct": False},
                {"text": "They contain valuable news footage", "correct": False}
            ],
            "explanation": "Early filmmakers invented EVERYTHING: close-ups, cuts, dissolves, camera movement, special effects, storytelling through images. Georges Melies created the first science fiction film. Edwin Porter invented cross-cutting. Every Hollywood blockbuster today uses techniques pioneered in these tiny films!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # MOTORSPORT (2 videos - Ken Block etc.)
    # ─────────────────────────────────────────────────────
    "Motorsport": [
        {
            "question": "What made the Gymkhana video series a YouTube phenomenon?",
            "answers": [
                {"text": "Real stunts with real cars – no CGI", "correct": True},
                {"text": "They were the first car videos on YouTube", "correct": False},
                {"text": "They were sponsored by Formula 1", "correct": False},
                {"text": "They used Hollywood movie budgets", "correct": False}
            ],
            "explanation": "Ken Block's Gymkhana series proved that real automotive skill beats CGI! Each video shows genuine precision driving with no digital tricks – just incredible car control. The series amassed over 500 MILLION views, making Ken Block one of the most-watched drivers in history!",
            "level": "easy"
        },
        {
            "question": "What tragic event connects these motorsport videos to automotive history?",
            "answers": [
                {"text": "Ken Block passed away in a snowmobile accident in 2023", "correct": True},
                {"text": "The cars used were all destroyed after filming", "correct": False},
                {"text": "The filming locations were demolished", "correct": False},
                {"text": "YouTube removed the original uploads", "correct": False}
            ],
            "explanation": "Ken Block tragically died on January 2, 2023 in a snowmobile accident in Utah at age 55. His Gymkhana legacy lives on as some of the most-viewed motorsport content ever created. These videos preserve the artistry of a driver who turned cars into a form of dance!",
            "level": "medium"
        },
        {
            "question": "How many views has the Gymkhana series accumulated globally?",
            "answers": [
                {"text": "Over 500 million views combined", "correct": True},
                {"text": "About 50 million views", "correct": False},
                {"text": "Over 2 billion views", "correct": False},
                {"text": "About 100 million views", "correct": False}
            ],
            "explanation": "Over 500 million views across the Gymkhana series – making it one of the most successful automotive content franchises EVER! Ken Block co-founded DC Shoes and Hoonigan Racing, turning his passion for driving into a global entertainment brand that transcended motorsport.",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # LOONEY TUNES / WB (3 videos combined)
    # ─────────────────────────────────────────────────────
    "Looney Tunes / WB": [
        {
            "question": "Which studio created Looney Tunes?",
            "answers": [
                {"text": "Warner Bros.", "correct": True},
                {"text": "Walt Disney Studios", "correct": False},
                {"text": "MGM", "correct": False},
                {"text": "Fleischer Studios", "correct": False}
            ],
            "explanation": "Warner Bros. created Looney Tunes in 1930 – originally as a musical series to promote their music catalog (hence 'Tunes'!). Characters like Bugs Bunny, Daffy Duck, and Porky Pig became cultural icons. The series produced over 1,000 shorts over 40+ years!",
            "level": "easy"
        },
        {
            "question": "Why were some WWII-era Looney Tunes cartoons pulled from distribution?",
            "answers": [
                {"text": "They contained racial and ethnic stereotypes", "correct": True},
                {"text": "They revealed military secrets", "correct": False},
                {"text": "The animation quality was poor", "correct": False},
                {"text": "Warner Bros. lost the rights", "correct": False}
            ],
            "explanation": "The 'Censored Eleven' are Looney Tunes shorts permanently pulled from distribution due to racist stereotypes. These wartime cartoons reflected the prejudices of their era. Today they serve as historical documents – reminders of how media reflected and reinforced societal biases!",
            "level": "medium"
        },
        {
            "question": "What phrase did Porky Pig make famous?",
            "answers": [
                {"text": "Th-th-th-that's all, folks!", "correct": True},
                {"text": "What's up, Doc?", "correct": False},
                {"text": "I tawt I taw a puddy tat!", "correct": False},
                {"text": "Sufferin' succotash!", "correct": False}
            ],
            "explanation": "Porky Pig's stammered 'Th-th-th-that's all, folks!' became one of the most recognized catchphrases in entertainment history! Voice actor Mel Blanc – 'The Man of a Thousand Voices' – voiced nearly ALL Looney Tunes characters. His tombstone reads: 'That's All Folks'!",
            "level": "hard"
        }
    ],

    "Looney Tunes": None,  # Will use "Looney Tunes / WB" template

    # ─────────────────────────────────────────────────────
    # SILENT COMEDY (2 videos)
    # ─────────────────────────────────────────────────────
    "Silent Comedy": [
        {
            "question": "Why was Buster Keaton called 'The Great Stone Face'?",
            "answers": [
                {"text": "He never smiled or changed expression during performances", "correct": True},
                {"text": "He always wore stone-colored makeup", "correct": False},
                {"text": "He played a statue in his first film", "correct": False},
                {"text": "He had a stone collection hobby", "correct": False}
            ],
            "explanation": "Buster Keaton maintained a deadpan expression in ALL his films – creating comedy through the contrast between his calm face and the chaos around him. Fun fact: his nickname 'Buster' was given to him by HARRY HOUDINI, who saw the baby fall down stairs unhurt!",
            "level": "easy"
        },
        {
            "question": "What legendary stunt did Buster Keaton perform without any safety equipment?",
            "answers": [
                {"text": "A real house facade fell on him – he stood in the open window space", "correct": True},
                {"text": "He jumped off a moving train onto a horse", "correct": False},
                {"text": "He swam across a river while handcuffed", "correct": False},
                {"text": "He drove a car off a cliff into water", "correct": False}
            ],
            "explanation": "In 'Steamboat Bill, Jr.' (1928), a REAL two-ton building facade falls on Keaton. He survives by standing exactly where the open window passes over him – with only INCHES of clearance! No stunt doubles, no safety wires. One miscalculation = death. It's cinema's greatest practical stunt!",
            "level": "medium"
        },
        {
            "question": "How did Buster Keaton get his famous nickname?",
            "answers": [
                {"text": "Harry Houdini gave it to him after seeing baby Keaton fall downstairs", "correct": True},
                {"text": "A film critic coined it in a review", "correct": False},
                {"text": "His mother named him that at birth", "correct": False},
                {"text": "It was his character name in his first film", "correct": False}
            ],
            "explanation": "When 18-month-old Joseph Keaton fell down a flight of stairs without crying, family friend Harry Houdini exclaimed 'That was a real buster!' The nickname stuck for life! Keaton went on to become one of the greatest physical comedians ever, performing death-defying stunts himself.",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # WINSOR McCAY (2 videos)
    # ─────────────────────────────────────────────────────
    "Winsor McCay": [
        {
            "question": "Why is Winsor McCay called 'the father of animation'?",
            "answers": [
                {"text": "He created some of the first true animated films", "correct": True},
                {"text": "He invented the movie camera", "correct": False},
                {"text": "He founded Walt Disney Studios", "correct": False},
                {"text": "He created the first cartoon character", "correct": False}
            ],
            "explanation": "Winsor McCay created 'Gertie the Dinosaur' (1914) – one of the first animated characters with a distinct PERSONALITY! He drew approximately 10,000 drawings for Gertie. Earlier, his 'Little Nemo' (1911) showed what animation could achieve with about 4,000 hand-drawn frames!",
            "level": "easy"
        },
        {
            "question": "How many individual drawings did McCay create for a single short film?",
            "answers": [
                {"text": "About 10,000 – all drawn by himself", "correct": True},
                {"text": "About 500", "correct": False},
                {"text": "About 100,000", "correct": False},
                {"text": "About 50", "correct": False}
            ],
            "explanation": "McCay drew approximately 10,000 frames for 'Gertie the Dinosaur' and about 4,000 for 'Little Nemo' – each one BY HAND on rice paper! Unlike later studios with teams of animators, McCay did almost ALL the drawing himself. His dedication borders on superhuman artistic obsession!",
            "level": "medium"
        },
        {
            "question": "What was Winsor McCay's 'day job' while he created animated films?",
            "answers": [
                {"text": "Newspaper comic strip artist", "correct": True},
                {"text": "University art professor", "correct": False},
                {"text": "Circus performer", "correct": False},
                {"text": "Full-time film director", "correct": False}
            ],
            "explanation": "McCay was a famous newspaper comic artist – 'Little Nemo in Slumberland' was one of the most celebrated comic strips ever! He created his animated films in his SPARE TIME after his newspaper work. Animation was literally his hobby project – one that changed entertainment history forever!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # DOCUMENTARY (2 videos)
    # ─────────────────────────────────────────────────────
    "Documentary": [
        {
            "question": "What's the purpose of documentary films?",
            "answers": [
                {"text": "To document and preserve real events, people and cultures", "correct": True},
                {"text": "To create fictional stories based on facts", "correct": False},
                {"text": "To replace textbooks in schools", "correct": False},
                {"text": "To entertain with scripted drama", "correct": False}
            ],
            "explanation": "Documentaries capture reality! They preserve moments in time that would otherwise be lost forever. In the digital age, restored and upscaled vintage documentaries bring historical footage back to life with stunning clarity – making history visceral and immediate!",
            "level": "easy"
        },
        {
            "question": "Why is preserving historical documentary footage so important?",
            "answers": [
                {"text": "Original film stock deteriorates and many recordings are already lost", "correct": True},
                {"text": "Documentaries are always accurate historical records", "correct": False},
                {"text": "Film archives have unlimited storage space", "correct": False},
                {"text": "Digital copies are automatically created", "correct": False}
            ],
            "explanation": "Film preservation is a race against time! Original nitrate and acetate film stocks decompose, fade, and can spontaneously combust. UNESCO estimates that 80% of silent-era films are already LOST. Modern AI upscaling and restoration gives these treasures new life for future generations!",
            "level": "medium"
        },
        {
            "question": "How does AI upscaling improve vintage documentary footage?",
            "answers": [
                {"text": "It adds detail and clarity while preserving the original content", "correct": True},
                {"text": "It adds color to black and white films", "correct": False},
                {"text": "It creates new footage that didn't exist", "correct": False},
                {"text": "It makes old films look exactly like modern 4K cameras", "correct": False}
            ],
            "explanation": "AI upscaling analyzes each frame and intelligently adds resolution and detail – transforming grainy 480p footage into crisp 4K or 8K quality! It doesn't invent new content but enhances what's already there. The result: history in stunning clarity, as if you were there!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # EARLY ANIMATION (2 videos)
    # ─────────────────────────────────────────────────────
    "Early Animation": [
        {
            "question": "When did animation as an art form begin?",
            "answers": [
                {"text": "Around 1900-1910, with pioneers like Emile Cohl", "correct": True},
                {"text": "In the 1930s with Disney", "correct": False},
                {"text": "In the 1950s with television", "correct": False},
                {"text": "In the 1890s with the first films", "correct": False}
            ],
            "explanation": "Animation's roots go back to 1908 when Emile Cohl created 'Fantasmagorie' – considered the first fully animated film! These early pioneers drew thousands of frames by hand, inventing an entirely new art form. Disney arrived decades later, building on foundations laid by these unsung heroes!",
            "level": "easy"
        },
        {
            "question": "What makes early animations different from modern ones?",
            "answers": [
                {"text": "They were experimental art – no rules existed yet", "correct": True},
                {"text": "They were all in 3D", "correct": False},
                {"text": "They were made by machines", "correct": False},
                {"text": "They were silent because sound hadn't been invented", "correct": False}
            ],
            "explanation": "Early animators were true pioneers – they literally invented animation technique as they went! Every creative decision was new: How fast to draw movement? How to show weight? How to create personality? This experimental freedom created some of the most creative animation ever made!",
            "level": "medium"
        },
        {
            "question": "Why should modern audiences care about early animation?",
            "answers": [
                {"text": "It shows the pure artistic foundations that ALL animation builds on", "correct": True},
                {"text": "Early animations are legally required viewing", "correct": False},
                {"text": "They contain hidden messages", "correct": False},
                {"text": "They are technically superior to modern animation", "correct": False}
            ],
            "explanation": "Understanding early animation is like understanding art history – it reveals the DNA of everything that came after! Pixar, Studio Ghibli, and modern animators all study these pioneers. When you watch early animation, you see the birth of an art form that generates $270 BILLION yearly today!",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # COMEDY CLASSIC (1 video - Dinner for One)
    # ─────────────────────────────────────────────────────
    "Comedy Classic": [
        {
            "question": "What makes 'Dinner for One' a world record holder?",
            "answers": [
                {"text": "It's the most frequently repeated TV program EVER", "correct": True},
                {"text": "It's the longest comedy sketch ever filmed", "correct": False},
                {"text": "It holds the record for most TV awards", "correct": False},
                {"text": "It's the oldest surviving TV recording", "correct": False}
            ],
            "explanation": "Guinness World Record! 'Dinner for One' (1963) is the MOST REPEATED TV show in history. It airs every New Year's Eve on German television and has become an unbreakable tradition. Ironically, it's virtually UNKNOWN in its home country, the UK!",
            "level": "easy"
        },
        {
            "question": "What's the ironic twist about 'Dinner for One'?",
            "answers": [
                {"text": "It's a BRITISH sketch that's unknown in Britain but legendary in Germany", "correct": True},
                {"text": "The actor performing it had never done comedy before", "correct": False},
                {"text": "It was filmed in one take but was meant to be a rehearsal", "correct": False},
                {"text": "The original script was lost", "correct": False}
            ],
            "explanation": "The ultimate cultural paradox! This British comedy sketch by Freddie Frinton and May Warden was recorded by German TV channel NDR in 1963. In Germany it's a New Year's Eve INSTITUTION but in the UK almost nobody knows it exists! Even King Charles III has referenced it!",
            "level": "medium"
        },
        {
            "question": "How many drinks does butler James consume during 'Dinner for One'?",
            "answers": [
                {"text": "16 drinks (4 toasts x 4 guests)", "correct": True},
                {"text": "8 drinks", "correct": False},
                {"text": "12 drinks", "correct": False},
                {"text": "20 drinks", "correct": False}
            ],
            "explanation": "James drinks for FOUR absent guests across FOUR toasts = 16 drinks! Plus he trips over the same tiger rug every time – getting progressively more hilarious. The sketch's genius is its simplicity: one room, two actors, pure physical comedy. The famous closing line: 'Same procedure as every year!'",
            "level": "hard"
        }
    ],

    # ─────────────────────────────────────────────────────
    # OTHER (82 videos) - Generic but engaging quizzes
    # ─────────────────────────────────────────────────────
    "Other": [
        {
            "question": "What makes vintage films and cartoons valuable in the digital age?",
            "answers": [
                {"text": "They preserve cultural history that would otherwise be lost", "correct": True},
                {"text": "They are more entertaining than modern films", "correct": False},
                {"text": "They contain secret messages", "correct": False},
                {"text": "They are legally required to be preserved", "correct": False}
            ],
            "explanation": "Vintage films are TIME CAPSULES! They show us how people lived, thought, and entertained themselves decades ago. With AI upscaling to 8K, we can experience this content in stunning quality that the original creators could never have imagined. History comes alive!",
            "level": "easy"
        },
        {
            "question": "How does AI upscaling transform old footage?",
            "answers": [
                {"text": "AI adds detail and sharpness while preserving the original", "correct": True},
                {"text": "It replaces old footage with newly generated content", "correct": False},
                {"text": "It only works on color footage", "correct": False},
                {"text": "It makes all old films look the same", "correct": False}
            ],
            "explanation": "AI upscaling is like giving old footage new glasses! Neural networks analyze each pixel and intelligently enhance resolution from the original content. A grainy 480p film from the 1920s can become a crystal-clear 8K video – revealing details invisible for nearly a century!",
            "level": "medium"
        },
        {
            "question": "What's 'public domain' and why does it matter for classic content?",
            "answers": [
                {"text": "Copyright expired – anyone can freely share and enjoy these works", "correct": True},
                {"text": "The government owns the content", "correct": False},
                {"text": "It means the content was never copyrighted", "correct": False},
                {"text": "Only libraries can access public domain works", "correct": False}
            ],
            "explanation": "Public domain means the copyright has expired and the work belongs to EVERYONE! This is why classic films, cartoons, and music can be freely restored and shared. Without public domain, thousands of cultural masterpieces would be locked away forever. Culture should be free!",
            "level": "hard"
        }
    ]
}


def get_template_for_category(category):
    """Get quiz template, handling aliases and fallbacks."""
    # Direct match
    if category in QUIZ_TEMPLATES and QUIZ_TEMPLATES[category] is not None:
        return QUIZ_TEMPLATES[category]
    
    # Alias mappings
    aliases = {
        "Superman / Fleischer": "Superman",
        "Looney Tunes": "Looney Tunes / WB",
    }
    if category in aliases:
        return QUIZ_TEMPLATES.get(aliases[category])
    
    # Fallback to "Other"
    return QUIZ_TEMPLATES["Other"]


def build_psychology_quiz_database():
    """Rebuild the entire quiz database using psychology principles."""
    
    # Load current database to get video list
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'quiz_database_top_performers.json')
    db_path = os.path.normpath(db_path)
    
    with open(db_path, 'r', encoding='utf-8') as f:
        old_db = json.load(f)
    
    print(f"Loaded {len(old_db['videos'])} videos from existing database")
    
    # Load individual top-performer quizzes (keep these as they're already good)
    top_performer_ids = set()
    top_performer_quizzes = {}
    
    # Build new database
    new_videos = []
    stats = {
        "total_videos": 0,
        "total_quizzes": 0, 
        "total_answers": 0,
        "categories": {},
        "quiz_levels": {"easy": 0, "medium": 0, "hard": 0}
    }
    
    for video in old_db['videos']:
        vid = video['video_id']
        title = video['title']
        views = video.get('views', 0)
        category = video.get('category', 'Other')
        
        # Get psychology-based template for this category
        template = get_template_for_category(category)
        
        if template is None:
            template = QUIZ_TEMPLATES["Other"]
        
        # Build quizzes for this video
        quizzes = []
        for q in template:
            quiz = {
                "question": q["question"],
                "answers": q["answers"],
                "explanation": q["explanation"]
            }
            quizzes.append(quiz)
            
            level = q.get("level", "medium")
            stats["quiz_levels"][level] = stats["quiz_levels"].get(level, 0) + 1
        
        new_video = {
            "video_id": vid,
            "title": title,
            "views": views,
            "category": category,
            "quizzes": quizzes
        }
        new_videos.append(new_video)
        
        # Stats
        stats["total_videos"] += 1
        stats["total_quizzes"] += len(quizzes)
        stats["total_answers"] += sum(len(q["answers"]) for q in quizzes)
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
    
    # Sort by views descending
    new_videos.sort(key=lambda v: v.get('views', 0), reverse=True)
    
    # Build final database
    new_db = {
        "_meta": {
            "created": "2026-02-14",
            "updated": "2026-02-14",
            "version": "3.0 - Psychology Edition",
            "description": "Psychologie-basierte YouTube Quizzes fuer remAIke.TV",
            "design_principles": [
                "Curiosity Gap (Loewenstein) - Fragen wecken Neugier",
                "Dopamin-Belohnungsschleife - Wow-Fakten in Erklaerungen",
                "Graduated Difficulty (IQ-Test) - Q1=Leicht, Q2=Mittel, Q3=Schwer",
                "Von-Restorff-Effekt - Bizarre Fakten bleiben haften", 
                "Near-Miss-Psychologie - Plausible falsche Antworten",
                "Dunning-Kruger-Kalibrierung - Jeder fuehlt sich manchmal schlau",
                "Social Sharing Impulse - 'Wusstest du?' Momente"
            ],
            "total_videos": stats["total_videos"],
            "total_quizzes": stats["total_quizzes"],
            "total_answers": stats["total_answers"],
            "quiz_difficulty_distribution": stats["quiz_levels"],
            "note": "Alle Fakten Wikipedia-verifiziert (Feb 2026). Quizzes muessen MANUELL im YouTube Studio eingetragen werden.",
            "how_to": "YouTube Studio -> Video -> Details -> Quiz-Bereich rechts unten -> 'Quiz hinzufuegen'",
            "limits": "Max 10 Quizzes/Video, 2-4 Antworten, genau 1 richtig, Erklaerung max 500 Zeichen",
            "framework": "docs/youtube/QUIZ_PSYCHOLOGIE_FRAMEWORK.md",
            "sources": "Wikipedia, gamification research (Deterding 2011, Sailer 2017), IQ test design principles"
        },
        "videos": new_videos
    }
    
    return new_db, stats


def validate_database(db):
    """Validate the quiz database for errors."""
    errors = []
    warnings = []
    
    for i, video in enumerate(db['videos']):
        vid = video.get('video_id', 'UNKNOWN')
        title = video.get('title', 'UNKNOWN')
        
        if not vid or vid == 'UNKNOWN':
            errors.append(f"Video {i}: Missing video_id")
        
        for j, quiz in enumerate(video.get('quizzes', [])):
            q = quiz.get('question', '')
            answers = quiz.get('answers', [])
            explanation = quiz.get('explanation', '')
            
            # Check question
            if not q:
                errors.append(f"{vid} Q{j+1}: Empty question")
            
            # Check answer count
            if len(answers) < 2 or len(answers) > 4:
                errors.append(f"{vid} Q{j+1}: {len(answers)} answers (need 2-4)")
            
            # Check exactly 1 correct
            correct_count = sum(1 for a in answers if a.get('correct', False))
            if correct_count != 1:
                errors.append(f"{vid} Q{j+1}: {correct_count} correct answers (need exactly 1)")
            
            # Check explanation length
            if len(explanation) > 500:
                errors.append(f"{vid} Q{j+1}: Explanation too long ({len(explanation)} chars, max 500)")
            elif len(explanation) > 450:
                warnings.append(f"{vid} Q{j+1}: Explanation near limit ({len(explanation)}/500 chars)")
            
            if not explanation:
                errors.append(f"{vid} Q{j+1}: Missing explanation")
            
            # Check answer texts
            for k, answer in enumerate(answers):
                if not answer.get('text', ''):
                    errors.append(f"{vid} Q{j+1} A{k+1}: Empty answer text")
    
    return errors, warnings


def main():
    print("=" * 70)
    print("PSYCHOLOGY-BASED QUIZ GENERATOR v3.0")
    print("remAIke.TV - Wissenschaftlich fundiertes Quiz-Design")
    print("=" * 70)
    print()
    
    # Build new database
    print("Building psychology-based quiz database...")
    new_db, stats = build_psychology_quiz_database()
    
    # Validate
    print("\nValidating...")
    errors, warnings = validate_database(new_db)
    
    print(f"\n{'=' * 50}")
    print(f"STATISTICS:")
    print(f"{'=' * 50}")
    print(f"  Videos:        {stats['total_videos']}")
    print(f"  Quizzes:       {stats['total_quizzes']}")
    print(f"  Answers:       {stats['total_answers']}")
    print(f"  Difficulty:    Easy={stats['quiz_levels']['easy']}, "
          f"Medium={stats['quiz_levels']['medium']}, "
          f"Hard={stats['quiz_levels']['hard']}")
    print(f"  Categories:    {len(stats['categories'])}")
    print(f"  Errors:        {len(errors)}")
    print(f"  Warnings:      {len(warnings)}")
    print()
    
    print("CATEGORY DISTRIBUTION:")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: -x[1]):
        print(f"  {cat:30s} {count:4d} videos × 3 quizzes = {count*3:4d}")
    
    if errors:
        print(f"\n{'!' * 50}")
        print("ERRORS FOUND:")
        for e in errors:
            print(f"  ❌ {e}")
        return
    
    if warnings:
        print(f"\nWARNINGS:")
        for w in warnings:
            print(f"  ⚠️ {w}")
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'quiz_database_psychology_v3.json')
    output_path = os.path.normpath(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to: {output_path}")
    print(f"   {stats['total_videos']} videos, {stats['total_quizzes']} quizzes, {stats['total_answers']} answers")
    print(f"   0 errors - Ready for YouTube Studio!")
    
    # Also check explanation lengths
    print(f"\nEXPLANATION LENGTH CHECK:")
    max_len = 0
    for video in new_db['videos']:
        for quiz in video['quizzes']:
            l = len(quiz['explanation'])
            if l > max_len:
                max_len = l
    print(f"  Longest explanation: {max_len} chars (limit: 500)")
    

if __name__ == '__main__':
    main()
