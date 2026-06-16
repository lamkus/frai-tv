#!/usr/bin/env python3
"""
YouTube Studio Quiz Automation — remAIke.TV
==================================================
Playwright-basierte Browser-Automation zum automatischen Eintragen
von Quizzes in YouTube Studio.

OFFIZIELLE YOUTUBE-DOKU (support.google.com/youtube/answer/7124474):
  - Video Quizzes → Details ODER Editor Pane in YouTube Studio
  - Jedes Quiz braucht einen TIMESTAMP
  - Max 10 Quizzes pro Video, 2-4 Antworten
  - Genau 1 richtige Antwort
  - Optionale Erklärung (max 500 Zeichen)
  - Quizzes NICHT editierbar nach Speichern → löschen + neu

WORKFLOW:
  1. --login       → Browser öffnet sich, Google Login, Session gespeichert
  2. --scout       → UI-Elemente entdecken (1 Video)
  3. --test        → 1 Video testen (optional --dry-run)
  4. --run         → Alle Videos durchlaufen
  5. --verify      → Prüfen ob Quizzes sichtbar sind (Browser-basiert)

USAGE:
  python quiz_studio_automation.py --login
  python quiz_studio_automation.py --scout
  python quiz_studio_automation.py --test --dry-run
  python quiz_studio_automation.py --test
  python quiz_studio_automation.py --run --limit 10
  python quiz_studio_automation.py --verify --limit 5
  python quiz_studio_automation.py --status
  python quiz_studio_automation.py --reset
"""

import json
import sys
import os
import time
import argparse
import random
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# =========================================================
# CONFIGURATION
# =========================================================
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
STUDIO_BASE = "https://studio.youtube.com"
WATCH_BASE = "https://www.youtube.com/watch"

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUTH_STATE_FILE = os.path.join(BASE_DIR, '.playwright', 'youtube_auth.json')
QUIZ_DB_FILE = os.path.join(BASE_DIR, 'config', 'quiz_database_psychology_v3.json')
PROGRESS_FILE = os.path.join(BASE_DIR, 'config', 'quiz_automation_progress.json')
LOGS_DIR = os.path.join(BASE_DIR, 'logs', 'quiz_automation')

# Timing (Sekunden) — menschlich wirken, kein Bot-Flag
DELAY_SHORT = (1.5, 2.5)
DELAY_MEDIUM = (3.0, 5.0)
DELAY_LONG = (4.0, 7.0)
DELAY_BETWEEN_VIDEOS = (8, 15)

# Quiz timestamps: place at 25%, 50%, 75% of typical video length
# Since we don't know exact duration, use fixed offsets
DEFAULT_TIMESTAMPS = ["0:30", "1:30", "3:00"]


def delay(timing=DELAY_SHORT):
    """Random human-like delay."""
    time.sleep(random.uniform(*timing))


def ensure_dirs():
    """Ensure log directories exist."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(AUTH_STATE_FILE), exist_ok=True)


# =========================================================
# PROGRESS TRACKING
# =========================================================
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_videos": [], "failed_videos": [], "started": None, "last_updated": None}


def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_quiz_db():
    with open(QUIZ_DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# =========================================================
# LOGIN / AUTH
# =========================================================
def do_login():
    """Open browser for manual Google login, save auth state."""
    from playwright.sync_api import sync_playwright

    ensure_dirs()

    print("=" * 60)
    print("🔑 YOUTUBE STUDIO LOGIN")
    print("=" * 60)
    print()
    print("Ein Browser öffnet sich gleich.")
    print("Bitte:")
    print("  1. Bei Google einloggen (remAIke Account)")
    print("  2. YouTube Studio Dashboard abwarten")
    print("  3. ENTER hier im Terminal drücken")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-DE"
        )
        page = context.new_page()
        page.goto(f"{STUDIO_BASE}/channel/{CHANNEL_ID}")

        input(">>> ENTER wenn eingeloggt und Studio Dashboard sichtbar...")

        context.storage_state(path=AUTH_STATE_FILE)
        print(f"\n✅ Login gespeichert: {AUTH_STATE_FILE}")

        browser.close()


# =========================================================
# SCOUT MODE — Entdecke UI-Elemente
# =========================================================
def scout_mode():
    """Open video in Studio and dump ALL visible UI elements for debugging."""
    from playwright.sync_api import sync_playwright

    if not os.path.exists(AUTH_STATE_FILE):
        print("❌ Noch nicht eingeloggt! Erst: --login")
        return

    db = load_quiz_db()
    video = sorted(db['videos'], key=lambda v: v['views'], reverse=True)[0]

    print("=" * 60)
    print("🔍 SCOUT MODE — UI-Elemente erkunden")
    print("=" * 60)
    print(f"Video: {video['title']}")
    print(f"ID:    {video['video_id']}")
    print(f"URL:   {STUDIO_BASE}/video/{video['video_id']}/edit")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            storage_state=AUTH_STATE_FILE,
            viewport={"width": 1920, "height": 1080},
            locale="de-DE"
        )
        page = context.new_page()
        page.goto(f"{STUDIO_BASE}/video/{video['video_id']}/edit")

        delay(DELAY_LONG)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except:
            pass
        delay(DELAY_MEDIUM)

        # === 1. ALL INTERACTIVE ELEMENTS ===
        print("\n📋 === ALLE INTERAKTIVEN ELEMENTE ===")
        elements = page.evaluate("""() => {
            const results = [];
            const sels = 'button, ytcp-button, tp-yt-paper-button, [role="button"], [role="tab"], a[href], input, textarea, select, [contenteditable="true"]';
            document.querySelectorAll(sels).forEach(el => {
                if (el.offsetParent !== null || el.offsetWidth > 0) {
                    const text = (el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 80);
                    if (text || el.getAttribute('aria-label') || el.id) {
                        results.push({
                            tag: el.tagName.toLowerCase(),
                            text: text,
                            ariaLabel: el.getAttribute('aria-label') || '',
                            id: el.id || '',
                            testId: el.getAttribute('test-id') || el.getAttribute('data-testid') || '',
                            role: el.getAttribute('role') || '',
                            classes: (el.className || '').toString().substring(0, 100),
                            y: Math.round(el.getBoundingClientRect().y)
                        });
                    }
                }
            });
            return results.slice(0, 120);
        }""")

        for el in elements:
            parts = []
            if el.get('text'): parts.append(f'text="{el["text"][:60]}"')
            if el.get('ariaLabel'): parts.append(f'aria="{el["ariaLabel"][:50]}"')
            if el.get('id'): parts.append(f'id="{el["id"]}"')
            if el.get('testId'): parts.append(f'testId="{el["testId"]}"')
            if parts:
                print(f"  [{el['tag']:20s}] y={el.get('y',0):4d} | {' | '.join(parts)}")

        # === 2. QUIZ-RELATED ELEMENTS ===
        print("\n🎯 === QUIZ-BEZOGENE ELEMENTE ===")
        quiz_els = page.evaluate("""() => {
            const terms = ['quiz', 'Quiz', 'question', 'Frage', 'answer', 'Antwort', 'engagement'];
            const results = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.offsetParent === null && el.offsetWidth === 0) return;
                const text = (el.textContent || '').toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                for (const term of terms) {
                    if (text.includes(term.toLowerCase()) || aria.includes(term.toLowerCase()) || id.includes(term.toLowerCase())) {
                        if (el.children.length < 5) {
                            results.push({
                                tag: el.tagName.toLowerCase(),
                                text: (el.textContent || '').trim().substring(0, 100),
                                ariaLabel: el.getAttribute('aria-label') || '',
                                id: el.id || '',
                                outerHtml: el.outerHTML.substring(0, 250)
                            });
                        }
                        break;
                    }
                }
            });
            return results.slice(0, 40);
        }""")

        if quiz_els:
            for el in quiz_els:
                print(f"  [{el['tag']}] text=\"{el['text'][:60]}\"")
                if el.get('outerHtml'):
                    print(f"    HTML: {el['outerHtml'][:200]}")
        else:
            print("  ⚠️ Keine Quiz-Elemente gefunden auf der Details-Seite!")
            print("  → Scrolle runter oder wechsle zum 'Editor' Tab")

        # === 3. TABS / NAVIGATION ===
        print("\n📑 === TABS / NAVIGATION ===")
        tabs = page.evaluate("""() => {
            const tabs = [];
            document.querySelectorAll('[role="tab"], .tab, [class*="tab"]').forEach(el => {
                if (el.offsetParent !== null || el.offsetWidth > 0) {
                    tabs.push({
                        text: (el.textContent || '').trim().substring(0, 40),
                        href: el.getAttribute('href') || '',
                        selected: el.getAttribute('aria-selected') || ''
                    });
                }
            });
            return tabs.slice(0, 20);
        }""")
        for tab in tabs:
            sel = "→" if tab.get('selected') == 'true' else " "
            print(f"  {sel} [{tab['text']}] href={tab.get('href', '')}")

        # === 4. FULL PAGE SCROLL + RE-SCAN ===
        print("\n📜 Scrolle nach unten und scanne erneut...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        delay(DELAY_MEDIUM)

        bottom_els = page.evaluate("""() => {
            const terms = ['quiz', 'Quiz', 'engagement', 'Engagement', 'element', 'Element', 'add', 'hinzufügen'];
            const results = [];
            document.querySelectorAll('button, ytcp-button, tp-yt-paper-button, [role="button"]').forEach(el => {
                if (el.offsetParent === null && el.offsetWidth === 0) return;
                const text = (el.textContent || '').toLowerCase();
                for (const term of terms) {
                    if (text.includes(term)) {
                        results.push({
                            tag: el.tagName.toLowerCase(),
                            text: (el.textContent || '').trim().substring(0, 80),
                            y: Math.round(el.getBoundingClientRect().y)
                        });
                        break;
                    }
                }
            });
            return results;
        }""")

        if bottom_els:
            print("  Gefunden nach Scroll:")
            for el in bottom_els:
                print(f"    [{el['tag']}] y={el.get('y',0)} text=\"{el['text'][:60]}\"")

        # Screenshot
        ensure_dirs()
        ss_path = os.path.join(LOGS_DIR, 'scout_screenshot.png')
        page.screenshot(path=ss_path, full_page=True)
        print(f"\n📸 Full-page Screenshot: {ss_path}")

        # Save scout log
        scout_log = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video['video_id'],
            'video_title': video['title'],
            'elements': elements,
            'quiz_elements': quiz_els,
            'tabs': tabs,
            'bottom_elements': bottom_els
        }
        log_path = os.path.join(LOGS_DIR, 'scout_log.json')
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(scout_log, f, ensure_ascii=False, indent=2)
        print(f"📄 Scout-Log: {log_path}")

        input("\n>>> Erkunde den Browser, dann ENTER zum Beenden...")

        context.storage_state(path=AUTH_STATE_FILE)
        browser.close()


# =========================================================
# QUIZ ENTRY — Single Video
# =========================================================
def enter_quizzes_for_video(page, video_id, quizzes, video_title, dry_run=False):
    """Navigate to video in Studio, find quiz section, enter quizzes."""

    url = f"{STUDIO_BASE}/video/{video_id}/edit"
    print(f"\n{'='*60}")
    print(f"📺 {video_title}")
    print(f"   ID: {video_id} | Quizzes: {len(quizzes)}")

    if dry_run:
        for qi, quiz in enumerate(quizzes):
            correct = [a['text'] for a in quiz['answers'] if a.get('correct')]
            print(f"   Q{qi+1}: {quiz['question'][:60]}")
            print(f"       ✅ {correct[0][:50] if correct else '???'}")
            print(f"       📝 {quiz['explanation'][:60]}...")
        return True

    # Navigate to video edit page
    page.goto(url)
    delay(DELAY_LONG)

    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except:
        pass
    delay(DELAY_MEDIUM)

    # Check for existing quizzes to avoid duplicates
    has_existing = page.evaluate("""() => {
        const text = document.body.innerText.toLowerCase();
        return text.includes('quiz bearbeiten') || text.includes('edit quiz') ||
               text.includes('quiz löschen') || text.includes('delete quiz');
    }""")

    if has_existing:
        print(f"   ⚠️ Video hat bereits Quizzes — ÜBERSPRUNGEN")
        return True  # Mark as success (already done)

    for qi, quiz in enumerate(quizzes):
        print(f"\n   Quiz {qi+1}/{len(quizzes)}: {quiz['question'][:50]}...")

        # === FIND QUIZ ADD BUTTON ===
        quiz_button = find_quiz_button(page)

        if not quiz_button:
            print(f"   ❌ Quiz-Button nicht gefunden!")
            ensure_dirs()
            ss = os.path.join(LOGS_DIR, f'no_quiz_btn_{video_id}.png')
            page.screenshot(path=ss, full_page=True)
            print(f"   📸 {ss}")
            dump_page_buttons(page)
            return False

        quiz_button.click()
        delay(DELAY_MEDIUM)

        # === TIMESTAMP ===
        ts = DEFAULT_TIMESTAMPS[qi] if qi < len(DEFAULT_TIMESTAMPS) else "2:00"
        set_timestamp(page, ts)

        # === QUESTION ===
        if not set_question(page, quiz['question']):
            ensure_dirs()
            page.screenshot(path=os.path.join(LOGS_DIR, f'no_question_{video_id}_{qi}.png'), full_page=True)
            return False

        # === ANSWERS ===
        set_answers(page, quiz['answers'])

        # === EXPLANATION ===
        set_explanation(page, quiz['explanation'])

        # === CONFIRM THIS QUIZ (if per-quiz confirm exists) ===
        confirm_quiz(page)

        delay(DELAY_MEDIUM)

    # === SAVE ALL ===
    if not save_page(page, video_id):
        return False

    return True


def find_quiz_button(page):
    """Find the Quiz Add button on the video edit page. Multiple strategies."""
    selectors = [
        # German locale
        'button:has-text("Quiz hinzufügen")',
        'ytcp-button:has-text("Quiz hinzufügen")',
        'tp-yt-paper-button:has-text("Quiz")',
        'button:has-text("Quiz")',
        'ytcp-button:has-text("Quiz")',
        # English locale
        'button:has-text("Add quiz")',
        'ytcp-button:has-text("Add quiz")',
        'button:has-text("Add Quiz")',
        # Aria labels
        '[aria-label*="Quiz"]',
        '[aria-label*="quiz"]',
        # Test IDs
        '[test-id*="quiz"]',
        '[data-testid*="quiz"]',
        # YouTube Studio custom elements
        '#quiz-add-button',
        'ytve-quiz-add-button',
        '#video-quiz-section button',
        # Engagement section
        '#engagement button:has-text("Quiz")',
        '#engagement ytcp-button:has-text("Quiz")',
        # Generic engagement/element section
        'button:has-text("Hinzufügen"):near(:text("Quiz"))',
    ]

    # First pass — current scroll position
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1500):
                print(f"     🎯 Quiz-Button gefunden: {sel}")
                return btn
        except:
            continue

    # Scroll to middle and try again
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    delay(DELAY_SHORT)

    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1000):
                print(f"     🎯 Quiz-Button gefunden (Mitte): {sel}")
                return btn
        except:
            continue

    # Full scroll down and try
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    delay(DELAY_SHORT)

    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1000):
                print(f"     🎯 Quiz-Button gefunden (unten): {sel}")
                return btn
        except:
            continue

    # Brute-force: scan ALL buttons for "quiz" text
    try:
        all_btns = page.locator('button, ytcp-button, tp-yt-paper-button, [role="button"]')
        count = all_btns.count()
        for i in range(count):
            btn = all_btns.nth(i)
            try:
                txt = btn.inner_text(timeout=500).lower()
                if 'quiz' in txt:
                    print(f"     🎯 Quiz-Button gefunden (brute): \"{txt.strip()[:40]}\"")
                    return btn
            except:
                continue
    except:
        pass

    return None


def set_timestamp(page, timestamp):
    """Set the timestamp for a quiz."""
    selectors = [
        'input[aria-label*="Timestamp"]',
        'input[aria-label*="Zeitstempel"]',
        'input[aria-label*="timestamp"]',
        'input[placeholder*="0:00"]',
        'input[type="text"][class*="timestamp"]',
        '#timestamp-input',
        'ytcp-form-input-container input[type="text"]',
    ]

    for sel in selectors:
        try:
            inp = page.locator(sel).first
            if inp.is_visible(timeout=2000):
                inp.click()
                inp.fill(timestamp)
                delay(DELAY_SHORT)
                print(f"     ⏱️ Timestamp: {timestamp}")
                return True
        except:
            continue

    print(f"     ⚠️ Timestamp-Feld nicht gefunden (evtl. optional)")
    return False


def set_question(page, question):
    """Enter the quiz question."""
    selectors = [
        'textarea[aria-label*="Frage"]',
        'textarea[aria-label*="Question"]',
        'textarea[aria-label*="question"]',
        'input[aria-label*="Frage"]',
        'input[aria-label*="Question"]',
        '#quiz-question-input',
        'textarea[placeholder*="Frage"]',
        'textarea[placeholder*="Question"]',
        'div[contenteditable="true"]',
        'ytcp-form-textarea textarea',
    ]

    for sel in selectors:
        try:
            inp = page.locator(sel).first
            if inp.is_visible(timeout=2000):
                inp.click()
                delay(DELAY_SHORT)
                inp.fill(question)
                delay(DELAY_SHORT)
                print(f"     ✅ Frage eingetragen")
                return True
        except:
            continue

    # Fallback: first visible textarea in new dialog/form
    try:
        inp = page.locator('textarea:visible').first
        if inp.is_visible(timeout=1500):
            inp.click()
            inp.fill(question)
            delay(DELAY_SHORT)
            print(f"     ✅ Frage eingetragen (fallback)")
            return True
    except:
        pass

    print(f"     ❌ Frage-Feld nicht gefunden!")
    return False


def set_answers(page, answers):
    """Enter answers and mark the correct one."""
    for ai, answer in enumerate(answers):
        # For answers 3 and 4, need to click "Add answer" first
        if ai >= 2:
            for add_sel in [
                'button:has-text("Antwort hinzufügen")',
                'button:has-text("Add answer")',
                'button:has-text("Add option")',
                'button:has-text("Hinzufügen")',
                '[aria-label*="Antwort hinzufügen"]',
                '[aria-label*="Add answer"]',
                'ytcp-button:has-text("Antwort")',
                'ytcp-button:has-text("Add")',
            ]:
                try:
                    add_btn = page.locator(add_sel).first
                    if add_btn.is_visible(timeout=1500):
                        add_btn.click()
                        delay(DELAY_SHORT)
                        break
                except:
                    continue

        # Find and fill the answer input
        answer_input = find_answer_input(page, ai)

        if answer_input:
            answer_input.click()
            delay(DELAY_SHORT)
            answer_input.fill(answer['text'])
            delay(DELAY_SHORT)

            # Mark correct answer
            if answer.get('correct'):
                mark_correct_answer(page, ai)

            icon = "✅" if answer.get('correct') else "  "
            print(f"     {icon} Antwort {ai+1}: {answer['text'][:45]}")
        else:
            print(f"     ⚠️ Antwort {ai+1} Feld nicht gefunden")


def find_answer_input(page, index):
    """Find the answer input field by index."""
    # Strategy 1: by aria-label with index
    indexed_selectors = [
        f'input[aria-label*="Antwort"][aria-label*="{index+1}"]',
        f'input[aria-label*="Answer"][aria-label*="{index+1}"]',
        f'textarea[aria-label*="Antwort"]',
        f'textarea[aria-label*="Answer"]',
        f'input[placeholder*="Antwort"]',
        f'input[placeholder*="Answer"]',
    ]

    for sel in indexed_selectors:
        try:
            # If the selector uses index, try first match
            if str(index+1) in sel:
                inp = page.locator(sel).first
            else:
                # For generic selectors, use nth(index)
                inp = page.locator(sel).nth(index)
            if inp.is_visible(timeout=1000):
                return inp
        except:
            continue

    # Strategy 2: by class containing "answer"
    try:
        ans_inputs = page.locator('input[class*="answer"], textarea[class*="answer"], input[aria-label*="ntwort"], input[aria-label*="nswer"]')
        if ans_inputs.count() > index:
            inp = ans_inputs.nth(index)
            if inp.is_visible(timeout=1000):
                return inp
    except:
        pass

    # Strategy 3: look for all text inputs in the quiz form area
    try:
        # Usually the question textarea comes first, then answer inputs
        all_inputs = page.locator('input[type="text"]:visible, textarea:visible')
        count = all_inputs.count()
        # Answer inputs start after the question (index 0 = question, 1+ = answers)
        target_idx = index + 1  # Skip question field
        if count > target_idx:
            return all_inputs.nth(target_idx)
    except:
        pass

    return None


def mark_correct_answer(page, index):
    """Mark the correct answer by clicking its radio/checkbox."""
    selectors = [
        f'[data-answer-index="{index}"] [type="radio"]',
        f'[data-answer-index="{index}"] [type="checkbox"]',
        f'[aria-label*="richtig"]',
        f'[aria-label*="correct"]',
        f'[aria-label*="Correct"]',
        f'[aria-label*="Richtige"]',
        f'input[type="radio"]',
        f'[role="radio"]',
    ]

    for sel in selectors:
        try:
            els = page.locator(sel)
            if 'index' in sel or 'richtig' in sel.lower() or 'correct' in sel.lower():
                el = els.first
            else:
                # For generic radio, pick the one at our answer index
                if els.count() > index:
                    el = els.nth(index)
                else:
                    continue
            if el.is_visible(timeout=1000):
                el.click()
                delay(DELAY_SHORT)
                return True
        except:
            continue

    return False


def set_explanation(page, explanation):
    """Enter the quiz explanation."""
    selectors = [
        'textarea[aria-label*="Erklärung"]',
        'textarea[aria-label*="Explanation"]',
        'textarea[aria-label*="explanation"]',
        'input[aria-label*="Erklärung"]',
        'input[aria-label*="Explanation"]',
        'textarea[placeholder*="Erklärung"]',
        'textarea[placeholder*="Explanation"]',
        '#quiz-explanation',
        '[class*="explanation"] textarea',
    ]

    for sel in selectors:
        try:
            inp = page.locator(sel).first
            if inp.is_visible(timeout=2000):
                inp.click()
                delay(DELAY_SHORT)
                inp.fill(explanation)
                delay(DELAY_SHORT)
                print(f"     ✅ Erklärung ({len(explanation)} Zeichen)")
                return True
        except:
            continue

    print(f"     ⚠️ Erklärung-Feld nicht gefunden (optional)")
    return False


def confirm_quiz(page):
    """Click per-quiz confirm/done button if it exists."""
    for sel in [
        'button:has-text("Fertig")',
        'button:has-text("Done")',
        'button:has-text("Hinzufügen")',
        'button:has-text("Add")',
        'ytcp-button:has-text("Fertig")',
        'ytcp-button:has-text("Done")',
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1500):
                btn.click()
                delay(DELAY_MEDIUM)
                return True
        except:
            continue
    return False


def save_page(page, video_id):
    """Save the video edit page."""
    selectors = [
        '#save-button',
        'ytcp-button#save',
        'button:has-text("Speichern")',
        'button:has-text("Save")',
        '[aria-label*="Speichern"]',
        '[aria-label*="Save"]',
        'ytcp-button:has-text("Speichern")',
        'ytcp-button:has-text("Save")',
    ]

    save_btn = None
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                save_btn = btn
                break
        except:
            continue

    if not save_btn:
        print(f"\n   ⚠️ Save-Button nicht gefunden!")
        ensure_dirs()
        page.screenshot(path=os.path.join(LOGS_DIR, f'no_save_{video_id}.png'), full_page=True)
        return False

    # Check if enabled (has unsaved changes)
    try:
        if save_btn.is_disabled():
            print(f"\n   ⚠️ Save deaktiviert — keine Änderungen erkannt?")
            return False
    except:
        pass

    save_btn.click()
    delay(DELAY_LONG)

    # Handle confirmation dialog (quizzes can't be edited after saving)
    for confirm_sel in [
        'tp-yt-paper-dialog button:has-text("Speichern")',
        'tp-yt-paper-dialog button:has-text("Save")',
        'ytcp-confirmation-dialog button:has-text("Speichern")',
        'ytcp-confirmation-dialog button:has-text("Save")',
        'ytcp-confirmation-dialog button:has-text("Bestätigen")',
        'ytcp-confirmation-dialog button:has-text("Confirm")',
        '#confirm-button',
    ]:
        try:
            dlg_btn = page.locator(confirm_sel).first
            if dlg_btn.is_visible(timeout=3000):
                dlg_btn.click()
                delay(DELAY_MEDIUM)
                print(f"   ✅ Bestätigungs-Dialog bestätigt")
                break
        except:
            continue

    print(f"\n   💾 GESPEICHERT!")
    return True


def dump_page_buttons(page):
    """Debug helper: dump all visible buttons."""
    try:
        info = page.evaluate("""() => {
            return {
                url: window.location.href,
                title: document.title,
                buttons: Array.from(document.querySelectorAll('button, [role="button"]'))
                    .filter(el => el.offsetParent !== null)
                    .map(el => (el.textContent || '').trim().substring(0, 50))
                    .filter(t => t.length > 0)
                    .slice(0, 25)
            };
        }""")
        print(f"   URL: {info['url']}")
        print(f"   Buttons: {info['buttons']}")
    except:
        pass


# =========================================================
# VERIFY QUIZZES (Browser-basiert, da API keine Quizzes kennt)
# =========================================================
def verify_quizzes(limit=5):
    """Check if quizzes were added by visiting Studio video pages."""
    from playwright.sync_api import sync_playwright

    if not os.path.exists(AUTH_STATE_FILE):
        print("❌ Noch nicht eingeloggt! Erst: --login")
        return

    db = load_quiz_db()
    progress = load_progress()
    completed = progress.get('completed_videos', [])

    if not completed:
        print("❌ Noch keine Videos bearbeitet! Erst: --run")
        return

    videos = [v for v in db['videos'] if v['video_id'] in completed][:limit]

    print("=" * 60)
    print(f"🔍 QUIZ VERIFICATION — {len(videos)} Videos prüfen")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            storage_state=AUTH_STATE_FILE,
            viewport={"width": 1920, "height": 1080},
            locale="de-DE"
        )
        page = context.new_page()

        results = []
        for vi, video in enumerate(videos):
            vid = video['video_id']
            print(f"\n  {vi+1}/{len(videos)}: {video['title'][:50]}...")

            # Check Studio page for quiz indicators
            page.goto(f"{STUDIO_BASE}/video/{vid}/edit")
            delay(DELAY_LONG)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except:
                pass
            delay(DELAY_MEDIUM)

            has_quiz = page.evaluate("""() => {
                const text = document.body.innerText.toLowerCase();
                return text.includes('quiz bearbeiten') ||
                       text.includes('edit quiz') ||
                       text.includes('quiz löschen') ||
                       text.includes('delete quiz') ||
                       text.includes('quizzes (');
            }""")

            status = "✅" if has_quiz else "❓"
            results.append({'video_id': vid, 'title': video['title'], 'has_quiz': has_quiz})
            print(f"    {status} Quiz vorhanden: {has_quiz}")

        browser.close()

    found = sum(1 for r in results if r['has_quiz'])
    print(f"\n{'='*60}")
    print(f"📊 ERGEBNIS: {found}/{len(results)} Videos haben Quiz-Indikatoren")

    # Save verification result
    ensure_dirs()
    verify_path = os.path.join(LOGS_DIR, 'verify_result.json')
    with open(verify_path, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'results': results}, f, ensure_ascii=False, indent=2)
    print(f"📄 {verify_path}")


# =========================================================
# MAIN AUTOMATION LOOP
# =========================================================
def run_automation(start=0, limit=None, dry_run=False, test_mode=False):
    """Main automation loop."""
    from playwright.sync_api import sync_playwright

    if not dry_run and not os.path.exists(AUTH_STATE_FILE):
        print("❌ Noch nicht eingeloggt! Erst: --login")
        return

    db = load_quiz_db()
    progress = load_progress()

    # Sort by views (highest first)
    videos = sorted(db['videos'], key=lambda v: v['views'], reverse=True)

    # Filter completed
    completed_ids = set(progress['completed_videos'])
    pending = [v for v in videos if v['video_id'] not in completed_ids]

    if start > 0:
        pending = pending[start:]
    if limit:
        pending = pending[:limit]
    if test_mode:
        pending = pending[:1]

    total = len(pending)
    print("=" * 60)
    print(f"🎬 QUIZ AUTOMATION — {'DRY RUN' if dry_run else 'LIVE MODE'}")
    print("=" * 60)
    print(f"  Videos gesamt:    {len(db['videos'])}")
    print(f"  Bereits fertig:   {len(completed_ids)}")
    print(f"  Zu bearbeiten:    {total}")
    print(f"  Quizzes gesamt:   {total * 3}")
    if dry_run:
        print(f"\n  ⚠️ DRY RUN — es wird NICHTS geändert!")
    print()

    if total == 0:
        print("✅ Alle Videos haben bereits Quizzes!")
        return

    if dry_run:
        for vi, video in enumerate(pending):
            enter_quizzes_for_video(None, video['video_id'], video['quizzes'], video['title'], dry_run=True)
        print(f"\n{'='*60}")
        print(f"DRY RUN COMPLETE: {total} Videos × 3 Quizzes = {total*3} Quizzes bereit")
        return

    if not test_mode:
        print("⚠️ Browser öffnet sich gleich. CTRL+C zum Abbrechen.")
        input("\n>>> ENTER zum Starten...")

    if not progress['started']:
        progress['started'] = datetime.now().isoformat()
        save_progress(progress)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=['--start-maximized']
        )
        context = browser.new_context(
            storage_state=AUTH_STATE_FILE,
            viewport={"width": 1920, "height": 1080},
            locale="de-DE",
            no_viewport=True
        )
        page = context.new_page()

        # Verify login
        page.goto(f"{STUDIO_BASE}/channel/{CHANNEL_ID}")
        delay(DELAY_LONG)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass

        if "studio.youtube.com" not in page.url:
            print("❌ Login abgelaufen! Bitte erneut: --login")
            browser.close()
            return

        print(f"\n✅ Login OK\n")

        success = 0
        fail = 0

        for vi, video in enumerate(pending):
            try:
                result = enter_quizzes_for_video(
                    page, video['video_id'], video['quizzes'],
                    video['title'], dry_run=False
                )

                if result:
                    progress['completed_videos'].append(video['video_id'])
                    save_progress(progress)
                    success += 1
                    print(f"   ✅ {vi+1}/{total} ({video['views']:,} Views)")
                else:
                    progress['failed_videos'].append({
                        'video_id': video['video_id'],
                        'title': video['title'],
                        'error': 'UI element not found',
                        'timestamp': datetime.now().isoformat()
                    })
                    save_progress(progress)
                    fail += 1

                if vi < total - 1:
                    wait = random.uniform(*DELAY_BETWEEN_VIDEOS)
                    print(f"\n   ⏳ {wait:.0f}s Pause...")
                    time.sleep(wait)

            except KeyboardInterrupt:
                print(f"\n\n⚡ ABGEBROCHEN!")
                save_progress(progress)
                break
            except Exception as e:
                print(f"\n   ❌ FEHLER: {e}")
                fail += 1
                progress['failed_videos'].append({
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                save_progress(progress)

        try:
            context.storage_state(path=AUTH_STATE_FILE)
        except:
            pass
        browser.close()

    print(f"\n{'='*60}")
    print(f"📊 ERGEBNIS")
    print(f"{'='*60}")
    print(f"  ✅ Erfolgreich:     {success}")
    print(f"  ❌ Fehlgeschlagen:  {fail}")
    print(f"  Total fertig:      {len(progress['completed_videos'])}/{len(db['videos'])}")

    if progress['failed_videos']:
        print(f"\n  Letzte Fehler:")
        for fv in progress['failed_videos'][-5:]:
            print(f"    - {fv['title'][:40]}: {fv['error'][:40]}")


# =========================================================
# STATUS
# =========================================================
def show_status():
    db = load_quiz_db()
    progress = load_progress()
    total = len(db['videos'])
    done = len(progress['completed_videos'])
    failed = len(progress['failed_videos'])

    print("=" * 60)
    print("📊 QUIZ AUTOMATION STATUS")
    print("=" * 60)
    print(f"  Videos gesamt:     {total}")
    print(f"  ✅ Fertig:         {done}")
    print(f"  ❌ Fehlgeschlagen: {failed}")
    print(f"  ⏳ Ausstehend:     {total - done}")
    print(f"  Fortschritt:       {done/total*100:.1f}%")
    if progress.get('started'):
        print(f"  Gestartet:         {progress['started']}")
    if progress.get('last_updated'):
        print(f"  Letztes Update:    {progress['last_updated']}")

    if failed > 0:
        print(f"\n  Letzte Fehler:")
        for fv in progress['failed_videos'][-5:]:
            print(f"    - {fv['title'][:40]}: {fv.get('error','')[:40]}")


# =========================================================
# MAIN
# =========================================================
def main():
    parser = argparse.ArgumentParser(description='YouTube Studio Quiz Automation')
    parser.add_argument('--login', action='store_true', help='Google Login (einmalig)')
    parser.add_argument('--scout', action='store_true', help='UI-Elemente erkunden')
    parser.add_argument('--test', action='store_true', help='1 Video testen')
    parser.add_argument('--run', action='store_true', help='Automation starten')
    parser.add_argument('--verify', action='store_true', help='Quizzes verifizieren')
    parser.add_argument('--dry-run', action='store_true', help='Nur simulieren')
    parser.add_argument('--start', type=int, default=0, help='Ab Video Nr. X')
    parser.add_argument('--limit', type=int, default=None, help='Max Videos')
    parser.add_argument('--status', action='store_true', help='Fortschritt anzeigen')
    parser.add_argument('--reset', action='store_true', help='Fortschritt zurücksetzen')

    args = parser.parse_args()

    if args.login:
        do_login()
    elif args.scout:
        scout_mode()
    elif args.status:
        show_status()
    elif args.reset:
        save_progress({"completed_videos": [], "failed_videos": [], "started": None, "last_updated": None})
        print("✅ Fortschritt zurückgesetzt!")
    elif args.verify:
        verify_quizzes(limit=args.limit or 5)
    elif args.test:
        run_automation(test_mode=True, dry_run=args.dry_run)
    elif args.run:
        run_automation(start=args.start, limit=args.limit, dry_run=args.dry_run)
    else:
        parser.print_help()
        print("\n📌 WORKFLOW:")
        print("  1. python quiz_studio_automation.py --login")
        print("  2. python quiz_studio_automation.py --scout")
        print("  3. python quiz_studio_automation.py --test --dry-run")
        print("  4. python quiz_studio_automation.py --test")
        print("  5. python quiz_studio_automation.py --run")
        print("  6. python quiz_studio_automation.py --verify")


if __name__ == '__main__':
    main()
