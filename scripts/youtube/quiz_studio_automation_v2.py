#!/usr/bin/env python3
"""
YouTube Studio Quiz Automation v2 — remAIke.TV
==================================================
Uses the REAL installed Chrome browser (not Playwright's Chromium)
to avoid Google's "Anmeldung nicht möglich" block.

APPROACH:
  1. Launch real Chrome with --remote-debugging-port
  2. Connect Playwright via CDP (Chrome DevTools Protocol)
  3. = Google sees real Chrome, not automated bot!

OFFIZIELLE YOUTUBE-DOKU (support.google.com/youtube/answer/7124474):
  ZWEI QUIZ-TYPEN:
    A) Community Post Quizzes — Standalone Posts auf der Community-Seite
    B) Video Quizzes — Direkt in Video eingebettet (das wollen wir!)

  VIDEO QUIZ SPECS:
    - Hinzufügbar über: YouTube Studio → Video → "Details" oder "Editor" Pane
    - Bei neuen Uploads: Im Upload-Flow unter "Video Elements"
    - Jedes Quiz braucht einen TIMESTAMP (Zeitpunkt im Video)
    - Max 10 Quizzes pro Video
    - 2-4 Antworten pro Quiz, genau 1 richtige
    - Antworten: max 80 Zeichen (30 mit Bild)
    - Optionale Erklärung: max 500 Zeichen
    - NICHT editierbar nach Speichern! → Löschen + Neu erstellen
    - Quizzes erscheinen als interaktive Karte beim Timestamp

  TIMING / PLATZIERUNG:
    - Quiz erscheint als Overlay/Card beim gewählten Timestamp
    - Zuschauer sieht Frage + Antworten, kann klicken
    - Richtig/Falsch-Feedback + Erklärung wird angezeigt
    - Video läuft weiter nach Beantwortung
    - Optimal: 25%, 50%, 75% der Videolänge für 3 Quizzes

  ENGAGEMENT-EFFEKT:
    - Zuschauer interagieren aktiv → höheres Engagement-Signal
    - Watch Time steigt (Zuschauer pausieren für Quiz)
    - Satisfaction-Signal an Algorithmus
    - Besonders stark bei Educational Content (Category 27)

USAGE:
  python quiz_studio_automation_v2.py --login
  python quiz_studio_automation_v2.py --scout
  python quiz_studio_automation_v2.py --test --dry-run
  python quiz_studio_automation_v2.py --test
  python quiz_studio_automation_v2.py --run --limit 10
  python quiz_studio_automation_v2.py --status
"""

import json
import sys
import os
import time
import argparse
import random
import subprocess
import signal
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# =========================================================
# CONFIGURATION
# =========================================================
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
STUDIO_BASE = "https://studio.youtube.com"

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
QUIZ_DB_FILE = os.path.join(BASE_DIR, 'config', 'quiz_database_psychology_v3.json')
PROGRESS_FILE = os.path.join(BASE_DIR, 'config', 'quiz_automation_progress.json')
LOGS_DIR = os.path.join(BASE_DIR, 'logs', 'quiz_automation')

# Real Chrome paths
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
# Use a SEPARATE profile to avoid conflicts with running Chrome
CHROME_DEBUG_PROFILE = os.path.join(BASE_DIR, '.chrome_debug_profile')

# Timing (Sekunden) — menschlich wirken
DELAY_SHORT = (1.5, 2.5)
DELAY_MEDIUM = (3.0, 5.0)
DELAY_LONG = (5.0, 8.0)
DELAY_BETWEEN_VIDEOS = (8, 15)

# Quiz timestamps: 30s, 90s, 180s (kurz, mitte, spät)
DEFAULT_TIMESTAMPS = ["0:30", "1:30", "3:00"]


def delay(timing=DELAY_SHORT):
    """Random human-like delay."""
    time.sleep(random.uniform(*timing))


def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)


# =========================================================
# CHROME MANAGEMENT (using launch_persistent_context)
# =========================================================
# Uses Playwright's launch_persistent_context with the REAL
# Chrome executable. This avoids:
#   1. Google blocking Playwright's Chromium
#   2. Interfering with already-running Chrome windows
#   3. Needing manual Chrome restarts
# The separate profile dir persists the Google login session.

def launch_chrome_persistent(start_url=None):
    """Launch real Chrome via Playwright persistent context.
    
    Returns (pw, context, page) — context acts as both browser+context.
    The page is ready to use immediately.
    """
    from playwright.sync_api import sync_playwright
    
    print(f"🌐 Starte echten Chrome via Playwright persistent context...")
    print(f"   Chrome EXE: {CHROME_EXE}")
    print(f"   Profil: {CHROME_DEBUG_PROFILE}")
    
    os.makedirs(CHROME_DEBUG_PROFILE, exist_ok=True)
    
    pw = sync_playwright().start()
    
    try:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=CHROME_DEBUG_PROFILE,
            executable_path=CHROME_EXE,
            headless=False,
            slow_mo=150,
            no_viewport=True,
            args=[
                '--window-size=1920,1080',
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check',
            ],
            ignore_default_args=['--enable-automation'],
        )
        
        # Get or create a page
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()
        
        if start_url:
            page.goto(start_url)
            delay(DELAY_LONG)
        
        print(f"   ✅ Chrome gestartet und verbunden!")
        print(f"   🔒 Google sieht echten Chrome — kein Login-Block!")
        
        return pw, context, page
        
    except Exception as e:
        print(f"   ❌ Chrome-Start fehlgeschlagen: {e}")
        print(f"   → Tipp: Schließe ALLE Chrome-Fenster und versuche es noch mal")
        pw.stop()
        return None, None, None


def cleanup_chrome_persistent(pw, context):
    """Close Playwright persistent context."""
    try:
        if context:
            context.close()
    except:
        pass
    try:
        if pw:
            pw.stop()
    except:
        pass


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
# LOGIN
# =========================================================
def do_login():
    """Open real Chrome for Google login."""
    ensure_dirs()
    
    print("=" * 60)
    print("🔑 YOUTUBE STUDIO LOGIN (via echtem Chrome)")
    print("=" * 60)
    print()
    print("Es öffnet sich ein ECHTES Chrome-Fenster mit eigenem Profil.")
    print("Dort:")
    print("  1. Bei Google einloggen (remAIke Account)")
    print("  2. YouTube Studio Dashboard abwarten")
    print("  3. Hierher zurückkommen und ENTER drücken")
    print()
    print("⚠️ Falls Chrome nicht startet: schließe ALLE anderen Chrome-Fenster!")
    print()
    
    start_url = f"{STUDIO_BASE}/channel/{CHANNEL_ID}"
    pw, context, page = launch_chrome_persistent(start_url=start_url)
    
    if not context:
        print("❌ Chrome konnte nicht gestartet werden!")
        return
    
    input("\n>>> ENTER wenn du eingeloggt bist und das Studio Dashboard siehst...")
    
    current_url = page.url
    print(f"\n   Aktuelle URL: {current_url}")
    
    if "studio.youtube.com" in current_url:
        print("   ✅ Login erfolgreich! Session ist gespeichert im Chrome-Profil.")
        print(f"   📁 Profil: {CHROME_DEBUG_PROFILE}")
        print("   → Beim nächsten Start bist du automatisch eingeloggt!")
    else:
        print("   ⚠️ Du scheinst nicht im YouTube Studio zu sein.")
        print(f"   URL: {current_url}")
    
    cleanup_chrome_persistent(pw, context)


# =========================================================
# SCOUT MODE
# =========================================================
def scout_mode():
    """Open a video in Studio and discover UI elements."""
    ensure_dirs()
    
    db = load_quiz_db()
    video = sorted(db['videos'], key=lambda v: v['views'], reverse=True)[0]
    
    print("=" * 60)
    print("🔍 SCOUT MODE — UI-Elemente erkunden")
    print("=" * 60)
    print(f"  Video: {video['title']}")
    print(f"  ID:    {video['video_id']}")
    print(f"  URL:   {STUDIO_BASE}/video/{video['video_id']}/edit")
    print()
    
    # Launch Chrome with persistent context
    edit_url = f"{STUDIO_BASE}/video/{video['video_id']}/edit"
    pw, context, page = launch_chrome_persistent(start_url=edit_url)
    
    if not context:
        print("❌ Chrome konnte nicht gestartet werden!")
        return
    
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except:
        pass
    delay(DELAY_MEDIUM)
    
    # Check for login issues
    if "accounts.google.com" in page.url:
        print("\n   ❌ Nicht eingeloggt! Erst: --login")
        pw.stop()
        return
    
    # === DUMP ALL INTERACTIVE ELEMENTS ===
    print("\n📋 === SICHTBARE BUTTONS & CONTROLS ===")
    elements = page.evaluate("""() => {
        const results = [];
        const sels = 'button, ytcp-button, tp-yt-paper-button, [role="button"], [role="tab"], input, textarea, [contenteditable="true"], ytcp-dropdown-trigger';
        document.querySelectorAll(sels).forEach(el => {
            if (el.offsetParent !== null || el.offsetWidth > 0) {
                const text = (el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 100);
                const rect = el.getBoundingClientRect();
                if ((text || el.getAttribute('aria-label') || el.id) && rect.y > 0) {
                    results.push({
                        tag: el.tagName.toLowerCase(),
                        text: text.substring(0, 80),
                        aria: el.getAttribute('aria-label') || '',
                        id: el.id || '',
                        testId: el.getAttribute('test-id') || '',
                        classes: (el.className || '').toString().substring(0, 80),
                        y: Math.round(rect.y),
                        visible: rect.width > 0 && rect.height > 0
                    });
                }
            }
        });
        return results.sort((a, b) => a.y - b.y).slice(0, 80);
    }""")
    
    for el in elements:
        vis = "👁" if el.get('visible') else " "
        txt = el.get('text', '')[:60]
        aria = el.get('aria', '')[:40]
        tag = el.get('tag', '')[:20]
        tid = el.get('testId', '')[:30] or el.get('id', '')[:30]
        y = el.get('y', 0)
        print(f"  {vis} y={y:4d} [{tag:20s}] text=\"{txt}\" aria=\"{aria}\" id=\"{tid}\"")
    
    # === LOOK SPECIFICALLY FOR QUIZ-RELATED ELEMENTS ===
    print("\n📋 === QUIZ-SPEZIFISCHE SUCHE ===")
    quiz_els = page.evaluate("""() => {
        const results = [];
        // Search entire DOM for quiz-related text
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_ELEMENT,
            null
        );
        let node;
        while (node = walker.nextNode()) {
            const text = (node.textContent || '').toLowerCase();
            const aria = (node.getAttribute('aria-label') || '').toLowerCase();
            const cls = (node.className || '').toString().toLowerCase();
            const id = (node.id || '').toLowerCase();
            
            if (text.includes('quiz') || aria.includes('quiz') || 
                cls.includes('quiz') || id.includes('quiz')) {
                const rect = node.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    results.push({
                        tag: node.tagName.toLowerCase(),
                        text: (node.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 100),
                        aria: node.getAttribute('aria-label') || '',
                        id: node.id || '',
                        classes: (node.className || '').toString().substring(0, 100),
                        y: Math.round(rect.y),
                        w: Math.round(rect.width),
                        h: Math.round(rect.height)
                    });
                }
            }
        }
        // Deduplicate by position
        const unique = [];
        const seen = new Set();
        for (const el of results) {
            const key = `${el.y}-${el.tag}-${el.text.substring(0, 20)}`;
            if (!seen.has(key)) {
                seen.add(key);
                unique.push(el);
            }
        }
        return unique.sort((a, b) => a.y - b.y).slice(0, 30);
    }""")
    
    if quiz_els:
        for el in quiz_els:
            print(f"  🎯 y={el['y']:4d} [{el['tag']:20s}] {el['w']}x{el['h']} text=\"{el['text'][:60]}\"")
            if el.get('aria'): print(f"     aria=\"{el['aria']}\"")
            if el.get('id'): print(f"     id=\"{el['id']}\"")
            if el.get('classes'): print(f"     class=\"{el['classes'][:80]}\"")
    else:
        print("  ❌ Keine Quiz-Elemente gefunden!")
        print("  → Möglicherweise muss man erst zum 'Editor' Tab navigieren")
    
    # === CHECK FOR TABS (Details, Editor, etc.) ===
    print("\n📋 === TABS IM STUDIO ===")
    tabs = page.evaluate("""() => {
        const results = [];
        document.querySelectorAll('[role="tab"], .tab, ytcp-ve, a[href*="/edit"], a[href*="/editor"]').forEach(el => {
            if (el.offsetWidth > 0) {
                results.push({
                    tag: el.tagName.toLowerCase(),
                    text: (el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 60),
                    href: el.getAttribute('href') || '',
                    selected: el.getAttribute('aria-selected') || '',
                });
            }
        });
        return results;
    }""")
    
    for tab in tabs:
        sel = " ✓" if tab.get('selected') == 'true' else ""
        print(f"  [{tab['tag']}] \"{tab['text']}\" href=\"{tab.get('href', '')}\" {sel}")
    
    # Take screenshot
    ss_path = os.path.join(LOGS_DIR, 'scout_screenshot.png')
    page.screenshot(path=ss_path, full_page=False)
    print(f"\n📸 Screenshot gespeichert: {ss_path}")
    
    # Save page HTML for offline analysis
    html_path = os.path.join(LOGS_DIR, 'scout_page.html')
    html = page.content()
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"📄 HTML gespeichert: {html_path}")
    
    print("\n✅ Scout abgeschlossen. Analysiere die Ausgabe oben.")
    print("   Chrome wird geschlossen.")
    
    cleanup_chrome_persistent(pw, context)


# =========================================================
# QUIZ ENTRY
# =========================================================
def enter_quizzes_for_video(page, video_id, quizzes, video_title, dry_run=False):
    """Navigate to video in Studio and add quizzes."""
    
    print(f"\n{'='*60}")
    print(f"📺 {video_title}")
    print(f"   ID: {video_id} | Quizzes: {len(quizzes)}")
    
    if dry_run:
        for qi, quiz in enumerate(quizzes):
            print(f"\n   [DRY RUN] Quiz {qi+1}:")
            print(f"   Frage: {quiz['question']}")
            for ai, ans in enumerate(quiz['answers']):
                mark = "✅" if ans.get('correct') else "  "
                print(f"   {mark} {ai+1}. {ans['text']}")
            print(f"   Erklärung: {quiz['explanation'][:80]}...")
            print(f"   Timestamp: {DEFAULT_TIMESTAMPS[qi] if qi < len(DEFAULT_TIMESTAMPS) else '5:00'}")
        return True
    
    # Navigate to video edit page
    edit_url = f"{STUDIO_BASE}/video/{video_id}/edit"
    page.goto(edit_url)
    delay(DELAY_LONG)
    
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except:
        delay(DELAY_MEDIUM)
    
    # Check if we're logged in
    if "accounts.google.com" in page.url:
        print("   ❌ Login abgelaufen!")
        return False
    
    # Look for quiz-related UI elements
    # Strategy: Try multiple known selectors from YouTube Studio
    
    # First check if quizzes already exist on this video
    existing = page.evaluate("""() => {
        const text = document.body.innerText || '';
        const quizCount = (text.match(/quiz/gi) || []).length;
        return { quizCount, bodySnippet: text.substring(0, 500) };
    }""")
    
    # Try to find the quiz section
    # YouTube Studio uses Shadow DOM and web components heavily
    # We need to explore the actual DOM structure
    
    quiz_added = False
    
    for qi, quiz in enumerate(quizzes):
        print(f"\n   Quiz {qi+1}/{len(quizzes)}: {quiz['question'][:50]}...")
        timestamp = DEFAULT_TIMESTAMPS[qi] if qi < len(DEFAULT_TIMESTAMPS) else "5:00"
        
        # === STRATEGY 1: Look for "Quiz" / "Quiz hinzufügen" button ===
        btn_found = False
        for selector in [
            'text="Quiz hinzufügen"',
            'text="Add Quiz"',
            'text="Quiz"',
            'button:has-text("Quiz")',
            'ytcp-button:has-text("Quiz")',
            '[aria-label*="Quiz"]',
            '[aria-label*="quiz"]',
            '#quiz-add-button',
            'tp-yt-paper-button:has-text("Quiz")',
            '.quiz-add-button',
        ]:
            try:
                loc = page.locator(selector).first
                if loc.is_visible(timeout=2000):
                    loc.click()
                    delay(DELAY_MEDIUM)
                    btn_found = True
                    print(f"     ✅ Quiz-Button gefunden: {selector}")
                    break
            except:
                continue
        
        if not btn_found:
            # Try scrolling down
            page.evaluate("window.scrollTo(0, 2000)")
            delay(DELAY_SHORT)
            
            for selector in [
                'text="Quiz hinzufügen"',
                'text="Add Quiz"',
                'button:has-text("Quiz")',
            ]:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=2000):
                        loc.click()
                        delay(DELAY_MEDIUM)
                        btn_found = True
                        print(f"     ✅ Quiz-Button (nach Scroll): {selector}")
                        break
                except:
                    continue
        
        if not btn_found:
            # Maybe we need to go to the Editor tab first
            for tab_sel in [
                'text="Editor"',
                'a[href*="editor"]',
                '[role="tab"]:has-text("Editor")',
            ]:
                try:
                    loc = page.locator(tab_sel).first
                    if loc.is_visible(timeout=2000):
                        loc.click()
                        delay(DELAY_LONG)
                        print(f"     ↪ Wechsel zu Editor-Tab")
                        
                        # Now look for quiz button in editor
                        for q_sel in [
                            'text="Quiz hinzufügen"',
                            'text="Add Quiz"',
                            'text="Quiz"',
                            'button:has-text("Quiz")',
                        ]:
                            try:
                                loc2 = page.locator(q_sel).first
                                if loc2.is_visible(timeout=3000):
                                    loc2.click()
                                    delay(DELAY_MEDIUM)
                                    btn_found = True
                                    print(f"     ✅ Quiz-Button im Editor: {q_sel}")
                                    break
                            except:
                                continue
                        break
                except:
                    continue
        
        if not btn_found:
            print(f"     ❌ Quiz-Button nicht gefunden!")
            # Screenshot for debugging
            ss = os.path.join(LOGS_DIR, f'error_{video_id}_q{qi}.png')
            page.screenshot(path=ss)
            print(f"     📸 {ss}")
            return False
        
        # === FILL IN QUIZ FIELDS ===
        # After clicking "Add Quiz", look for the form fields
        delay(DELAY_SHORT)
        
        # Question field
        question_filled = False
        for q_input_sel in [
            'textarea[aria-label*="Frage"]',
            'textarea[aria-label*="Question"]',
            'textarea[placeholder*="Frage"]',
            'textarea[placeholder*="Question"]',
            '#quiz-question-input',
            'textarea.question-input',
            'div[contenteditable="true"]:near(:text("Frage"))',
        ]:
            try:
                loc = page.locator(q_input_sel).first
                if loc.is_visible(timeout=2000):
                    loc.click()
                    delay(DELAY_SHORT)
                    loc.fill(quiz['question'])
                    delay(DELAY_SHORT)
                    question_filled = True
                    print(f"     ✅ Frage eingetragen")
                    break
            except:
                continue
        
        if not question_filled:
            # Fallback: find all visible textareas
            try:
                textareas = page.locator('textarea:visible')
                count = textareas.count()
                if count > 0:
                    textareas.first.click()
                    delay(DELAY_SHORT)
                    textareas.first.fill(quiz['question'])
                    question_filled = True
                    print(f"     ✅ Frage (Fallback textarea)")
            except:
                pass
        
        if not question_filled:
            print(f"     ❌ Frage-Feld nicht gefunden!")
            ss = os.path.join(LOGS_DIR, f'error_question_{video_id}_q{qi}.png')
            page.screenshot(path=ss)
            return False
        
        # Answer fields
        for ai, answer in enumerate(quiz['answers']):
            answer_filled = False
            
            for a_sel in [
                f'textarea[aria-label*="Antwort {ai+1}"]',
                f'textarea[aria-label*="Answer {ai+1}"]',
                f'input[aria-label*="Antwort {ai+1}"]',
                f'input[aria-label*="Answer {ai+1}"]',
                f'textarea[placeholder*="Antwort"]',
                f'input[placeholder*="Answer"]',
            ]:
                try:
                    loc = page.locator(a_sel).first
                    if loc.is_visible(timeout=1500):
                        loc.click()
                        delay(DELAY_SHORT)
                        loc.fill(answer['text'])
                        delay(DELAY_SHORT)
                        answer_filled = True
                        break
                except:
                    continue
            
            if not answer_filled:
                # Fallback: nth textarea/input after the question
                try:
                    inputs = page.locator('textarea:visible, input[type="text"]:visible')
                    idx = ai + 1  # skip question field
                    if inputs.count() > idx:
                        inputs.nth(idx).click()
                        delay(DELAY_SHORT)
                        inputs.nth(idx).fill(answer['text'])
                        answer_filled = True
                except:
                    pass
            
            if not answer_filled:
                # Maybe need to click "Add answer" first
                for add_sel in [
                    'text="Antwort hinzufügen"',
                    'text="Add answer"',
                    'button:has-text("Antwort")',
                    'button:has-text("answer")',
                ]:
                    try:
                        loc = page.locator(add_sel).first
                        if loc.is_visible(timeout=1500):
                            loc.click()
                            delay(DELAY_SHORT)
                            break
                    except:
                        continue
            
            # Mark correct answer
            if answer.get('correct'):
                for corr_sel in [
                    f'input[type="radio"]:nth-of-type({ai+1})',
                    f'[data-answer-index="{ai}"] input[type="radio"]',
                    f'[role="radio"]:nth-of-type({ai+1})',
                ]:
                    try:
                        loc = page.locator(corr_sel).first
                        if loc.is_visible(timeout=1500):
                            loc.click()
                            delay(DELAY_SHORT)
                            break
                    except:
                        continue
            
            mark = "✅" if answer.get('correct') else "  "
            status = "✅" if answer_filled else "❌"
            print(f"     {status} {mark} Antwort {ai+1}: {answer['text'][:40]}")
        
        # Explanation field
        for expl_sel in [
            'textarea[aria-label*="Erklärung"]',
            'textarea[aria-label*="Explanation"]',
            'textarea[placeholder*="Erklärung"]',
            'textarea[placeholder*="Explanation"]',
            '#quiz-explanation',
        ]:
            try:
                loc = page.locator(expl_sel).first
                if loc.is_visible(timeout=2000):
                    loc.click()
                    delay(DELAY_SHORT)
                    loc.fill(quiz['explanation'])
                    delay(DELAY_SHORT)
                    print(f"     ✅ Erklärung ({len(quiz['explanation'])} Zeichen)")
                    break
            except:
                continue
        
        # Timestamp
        for ts_sel in [
            'input[aria-label*="Timestamp"]',
            'input[aria-label*="Zeitstempel"]',
            'input[aria-label*="time"]',
            'input[placeholder*="0:00"]',
        ]:
            try:
                loc = page.locator(ts_sel).first
                if loc.is_visible(timeout=2000):
                    loc.triple_click()  # Select all existing text
                    delay(DELAY_SHORT)
                    loc.fill(timestamp)
                    delay(DELAY_SHORT)
                    print(f"     ✅ Timestamp: {timestamp}")
                    break
            except:
                continue
        
        quiz_added = True
        delay(DELAY_MEDIUM)
    
    # === SAVE ===
    if quiz_added:
        for save_sel in [
            '#save-button',
            'ytcp-button#save',
            'button:has-text("Speichern")',
            'button:has-text("Save")',
            'tp-yt-paper-button:has-text("Save")',
            '[aria-label*="Speichern"]',
            '[aria-label*="Save"]',
        ]:
            try:
                loc = page.locator(save_sel).first
                if loc.is_visible(timeout=3000):
                    loc.click()
                    delay(DELAY_LONG)
                    
                    # Handle confirmation dialog (quizzes can't be edited after save)
                    for confirm_sel in [
                        'button:has-text("Speichern")',
                        'button:has-text("Save")',
                        'button:has-text("Bestätigen")',
                        'button:has-text("Confirm")',
                    ]:
                        try:
                            dlg = page.locator(confirm_sel).first
                            if dlg.is_visible(timeout=3000):
                                dlg.click()
                                delay(DELAY_MEDIUM)
                                break
                        except:
                            continue
                    
                    print(f"\n   💾 GESPEICHERT!")
                    break
            except:
                continue
    
    return quiz_added


# =========================================================
# MAIN AUTOMATION
# =========================================================
def run_automation(start=0, limit=None, dry_run=False, test_mode=False):
    """Main automation loop."""
    ensure_dirs()
    
    db = load_quiz_db()
    progress = load_progress()
    
    videos = sorted(db['videos'], key=lambda v: v['views'], reverse=True)
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
    print(f"🎬 QUIZ AUTOMATION v2 — {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60)
    print(f"  Videos gesamt:    {len(db['videos'])}")
    print(f"  Bereits fertig:   {len(completed_ids)}")
    print(f"  Zu bearbeiten:    {total}")
    print(f"  Quizzes zu setzen: {total * 3}")
    if dry_run:
        print(f"  ⚠️ DRY RUN — NICHTS wird gespeichert!")
    print()
    
    if total == 0:
        print("✅ Alle Videos haben bereits Quizzes!")
        return
    
    if dry_run:
        # Dry run doesn't need Chrome
        for vi, video in enumerate(pending):
            enter_quizzes_for_video(None, video['video_id'], video['quizzes'], video['title'], dry_run=True)
        print(f"\n✅ DRY RUN kann abgeschlossen: {total} Videos validiert.")
        return
    
    # Connect to Chrome
    start_url = f"{STUDIO_BASE}/channel/{CHANNEL_ID}"
    pw, context, page = launch_chrome_persistent(start_url=start_url)
    if not context:
        print("❌ Chrome nicht gestartet! Erst --login starten.")
        return
    
    if not progress['started']:
        progress['started'] = datetime.now().isoformat()
    
    success_count = 0
    fail_count = 0
    
    for vi, video in enumerate(pending):
        try:
            result = enter_quizzes_for_video(
                page, video['video_id'], video['quizzes'], video['title']
            )
            
            if result:
                progress['completed_videos'].append(video['video_id'])
                save_progress(progress)
                success_count += 1
                print(f"   ✅ {vi+1}/{total} ({video['views']:,} Views)")
            else:
                progress['failed_videos'].append({
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'error': 'UI element not found',
                    'timestamp': datetime.now().isoformat()
                })
                save_progress(progress)
                fail_count += 1
            
            if vi < total - 1:
                wait = random.uniform(*DELAY_BETWEEN_VIDEOS)
                print(f"\n   ⏳ Warte {wait:.0f}s...")
                time.sleep(wait)
                
        except KeyboardInterrupt:
            print(f"\n\n⚡ ABGEBROCHEN!")
            save_progress(progress)
            break
        except Exception as e:
            print(f"\n   ❌ FEHLER: {e}")
            fail_count += 1
            progress['failed_videos'].append({
                'video_id': video['video_id'],
                'title': video['title'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            save_progress(progress)
    cleanup_chrome_persistent(pw, context
    pw.stop()
    
    print(f"\n{'='*60}")
    print(f"📊 ERGEBNIS")
    print(f"{'='*60}")
    print(f"  Erfolgreich:     {success_count}")
    print(f"  Fehlgeschlagen:  {fail_count}")
    print(f"  Gesamt fertig:   {len(progress['completed_videos'])}/{len(db['videos'])}")


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
    print("📊 QUIZ AUTOMATION — STATUS")
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


# =========================================================
# MAIN
# =========================================================
def main():
    parser = argparse.ArgumentParser(description='YouTube Studio Quiz Automation v2')
    parser.add_argument('--login', action='store_true', help='Google Login via echtem Chrome')
    parser.add_argument('--scout', action='store_true', help='UI-Elemente erkunden')
    parser.add_argument('--test', action='store_true', help='Nur 1 Video testen')
    parser.add_argument('--run', action='store_true', help='Alle Videos durchlaufen')
    parser.add_argument('--dry-run', action='store_true', help='Nur simulieren')
    parser.add_argument('--start', type=int, default=0, help='Ab Video Nr. X')
    parser.add_argument('--limit', type=int, default=None, help='Max. Videos')
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
        save_progress({"completed_videos": [], "failed_videos": [], "started": None})
        print("✅ Fortschritt zurückgesetzt!")
    elif args.test:
        run_automation(test_mode=True, dry_run=args.dry_run)
    elif args.run:
        run_automation(start=args.start, limit=args.limit, dry_run=args.dry_run)
    else:
        parser.print_help()
        print()
        print("📌 QUICK START:")
        print("  Schritt 1: Schließe ALLE Chrome-Fenster")
        print("  Schritt 2: python quiz_studio_automation_v2.py --login")
        print("  Schritt 3: python quiz_studio_automation_v2.py --scout")
        print("  Schritt 4: python quiz_studio_automation_v2.py --test --dry-run")
        print("  Schritt 5: python quiz_studio_automation_v2.py --run")


if __name__ == '__main__':
    main()
