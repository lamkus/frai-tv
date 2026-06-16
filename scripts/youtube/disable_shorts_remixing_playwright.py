#!/usr/bin/env python3
"""
disable_shorts_remixing_playwright.py

Automatisiert das Deaktivieren von "Shorts remixing" und "audio sampling"
für Wochenschau-Videos im YouTube Studio per Browser-Automation (Playwright).

WICHTIG: Dieses Script führt Aktionen in DEINEM YouTube-Studio-Account aus.
Du musst lokal angemeldet sein (Chrome-Profil) und das Script im "Dry-Run"
Modus testen bevor Änderungen angewendet werden.

Usage:
  python disable_shorts_remixing_playwright.py --user-data-dir "C:/Users/me/AppData/Local/Google/Chrome/User Data" --channel-id UCVFv6Egpl0LDvigpFbQXNeQ --dry-run
  python disable_shorts_remixing_playwright.py --user-data-dir "..." --channel-id UCVF... --confirm

Flags:
  --dry-run     : Nur loggen, NICHT klicken (empfohlen zuerst)
  --confirm     : Tatsächlich klicken und speichern
  --headless    : Headless mode (default: False)
  --limit N     : Max Anzahl Videos bearbeiten (default: all)

Requirements:
  pip install playwright
  playwright install

Sicherheit:
  - Skript NICHT in einem fremden Account ausführen
  - Verwende persistenten Chrome-Profil-Ordner, damit bereits angemeldet ist

"""

import argparse
import time
import sys
from pathlib import Path
from typing import List

from playwright.sync_api import sync_playwright, TimeoutError


def find_video_links(page, text_filter: str = "Wochenschau") -> List[str]:
    # Find anchors that link to /video/ and contain the Wochenschau text
    # Using Playwright's has_text is robust across locales
    locator = page.locator("a[href*='/video/']", has_text=text_filter)
    count = locator.count()
    links = []
    for i in range(count):
        handle = locator.nth(i)
        href = handle.get_attribute('href')
        if href:
            links.append(href)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for h in links:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def find_toggles_for_labels(page, labels: List[str]):
    # Search for elements containing the label text (case-insensitive)
    # and attempt to locate a nearby toggle control.
    found = []
    for label in labels:
        try:
            # Use a case-insensitive xpath search
            xpath = f"//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"
            elements = page.locator(f"xpath={xpath}")
            for i in range(elements.count()):
                el = elements.nth(i)
                # Look for toggle button/input in the same container or following siblings
                toggle = None
                try:
                    toggle = el.locator("xpath=..//tp-yt-paper-toggle-button|..//ytd-toggle-button-renderer|..//input[@type='checkbox']|..//button[@role='switch']").first
                except Exception:
                    toggle = None
                if not toggle:
                    # fallback: find following button
                    try:
                        toggle = el.locator("xpath=following::button[1]").first
                    except Exception:
                        toggle = None
                found.append((label, el, toggle))
        except Exception as e:
            print(f"  [warn] label search failed for '{label}': {e}")
    return found


def get_toggle_state(toggle) -> str:
    # Many toggles expose aria-pressed/aria-checked or a 'checked' attribute
    if toggle is None:
        return 'unknown'
    try:
        attr = toggle.get_attribute('aria-pressed')
        if attr is not None:
            return 'on' if attr in ('true', 'pressed') else 'off'
        attr = toggle.get_attribute('aria-checked')
        if attr is not None:
            return 'on' if attr in ('true', 'checked') else 'off'
        checked = toggle.get_attribute('checked')
        if checked is not None:
            return 'on' if checked in ('true', 'checked') else 'off'
        class_attr = toggle.get_attribute('class') or ''
        if 'on' in class_attr or 'enabled' in class_attr or 'checked' in class_attr:
            return 'on'
        # fallback: try text
        text = toggle.inner_text().lower() if toggle else ''
        if 'on' in text:
            return 'on'
    except Exception:
        pass
    return 'unknown'


def toggle_off(page, toggle, dry_run: bool, label: str) -> bool:
    state = get_toggle_state(toggle)
    print(f"    - {label}: current state -> {state}")
    if state == 'on':
        if dry_run:
            print(f"      [dry-run] would click to disable")
            return True
        print(f"      clicking to disable...")
        try:
            toggle.click()
            time.sleep(0.6)
            new_state = get_toggle_state(toggle)
            print(f"      new state -> {new_state}")
            return True
        except Exception as e:
            print(f"      [error] failed to click toggle: {e}")
            return False
    elif state == 'off':
        print(f"      already off")
        return True
    else:
        print(f"      unknown toggle state; skipping")
        return False


def process_video(page, url: str, dry_run: bool, confirm: bool):
    print(f"\nProcessing video: {url}")
    page.goto(url)
    # Wait for editor to load
    try:
        page.wait_for_selector("text=Details", timeout=10_000)
    except TimeoutError:
        # still continue; page may be loaded but label differs
        time.sleep(1)
    time.sleep(1.0)

    # Ensure 'Show more' is expanded
    try:
        show_more = page.locator("xpath=//tp-yt-paper-toggle-button//yt-formatted-string[contains(., 'Show more') or contains(., 'Mehr anzeigen')]")
        if show_more.count() > 0:
            # click if collapsed
            pass
    except Exception:
        pass

    labels = [
        'shorts remix', 'shorts remixing', 'shorts-remix', 'shorts-remix zulassen',
        'audio sampling', 'allow audio sampling', 'audio-sampling', 'audio sampling zulassen'
    ]

    found = find_toggles_for_labels(page, labels)
    if not found:
        print("  [warn] Keine Remix/Sampling-Labels gefunden (lokaler Text könnte anders sein)")
        return {'url': url, 'changed': False, 'notes': 'not found'}

    any_changed = False
    for label, el, toggle in found:
        if toggle is None:
            print(f"    - {label}: toggle element NOT found")
            continue
        state = get_toggle_state(toggle)
        # Only do action if confirm flag passed
        if confirm:
            ok = toggle_off(page, toggle, dry_run, label)
            any_changed = any_changed or ok
        else:
            print(f"    - {label}: state={state} (no confirm, skipping)")

    # After changes, save by clicking Save button if present and we made changes
    if confirm and not dry_run and any_changed:
        try:
            save_btn = page.locator("xpath=//ytcp-button//span[contains(., 'Save') or contains(., 'Speichern')]").first
            if save_btn and save_btn.is_visible():
                print("    - clicking Save")
                save_btn.click()
                time.sleep(0.8)
        except Exception:
            pass

    return {'url': url, 'changed': any_changed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-data-dir', required=True, help='Chrome user data dir to persist login session')
    parser.add_argument('--channel-id', required=True, help='YouTube channel id (e.g., UCVFv...)')
    parser.add_argument('--dry-run', action='store_true', help='Nur simulierter Lauf (keine Klicks)')
    parser.add_argument('--confirm', action='store_true', help='Tatsaechlich klicken und speichern')
    parser.add_argument('--headless', action='store_true', help='Headless mode')
    parser.add_argument('--limit', type=int, default=0, help='Max number of videos to process (0 = all)')
    args = parser.parse_args()

    # Safety
    if args.confirm and args.dry_run:
        print('Fehler: --confirm und --dry-run koennen nicht zusammen verwendet werden')
        sys.exit(1)

    print('Starte Playwright Automation (lokal)')
    print('Bitte sicherstellen: Du bist im angegebenen Chrome-Profil eingeloggt in YouTube Studio')

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=args.user_data_dir,
            headless=args.headless,
            args=['--start-maximized']
        )
        page = browser.new_page()

        videos_page = f'https://studio.youtube.com/channel/{args.channel_id}/videos'
        page.goto(videos_page)
        print(f'Gehe zu: {videos_page}')

        # wait for videos list
        try:
            page.wait_for_selector("a[href*='/video/']", timeout=10000)
        except TimeoutError:
            print('Timeout beim Laden der Video-Liste. Bitte manuell anmelden und erneut versuchen.')
            browser.close()
            sys.exit(1)

        links = find_video_links(page, text_filter='Wochenschau')
        print(f'Gefundene Wochenschau Videos: {len(links)}')
        if args.limit and args.limit > 0:
            links = links[:args.limit]

        results = []
        for i, link in enumerate(links, start=1):
            print(f'[{i}/{len(links)}]')
            res = process_video(page, link, dry_run=args.dry_run, confirm=args.confirm)
            results.append(res)

        print('\nFertig. Zusammenfassung:')
        changed = [r for r in results if r.get('changed')]
        print(f'  Videos geändert: {len(changed)} / {len(results)}')

        browser.close()


if __name__ == '__main__':
    main()
