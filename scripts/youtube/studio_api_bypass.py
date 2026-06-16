#!/usr/bin/env python3
"""
studio_api_bypass.py - YouTube Studio Internal API (0 QUOTA!)

Nutzt YouTubes interne Innertube-API (die gleiche die YouTube Studio im Browser nutzt)
um Video-Metadaten zu aktualisieren - OHNE API-Quota zu verbrauchen!

FUNKTIONEN:
  - Video-Titel ändern
  - Video-Beschreibung ändern
  - Video-Tags ändern
  - Video-Kategorie ändern
  - Playlist-Management
  - Video-Details lesen
  - Alle Videos listen

AUTHENTIFIZIERUNG:
  Option A: Automatisch via Playwright (empfohlen)
    → Extrahiert Cookies aus deinem Chrome-Profil
    
  Option B: Manuell Cookies aus DevTools kopieren
    → SID, HSID, SSID, APISID, SAPISID aus .youtube.com Cookies

QUOTA-KOSTEN: 0 (ZERO!) - Nutzt interne Browser-API

USAGE:
  # Cookies extrahieren (einmalig pro Session, ~24h gültig)
  python studio_api_bypass.py --extract-cookies
  
  # Video-Metadaten updaten (0 Quota!)
  python studio_api_bypass.py --update-video VIDEO_ID --title "Neuer Titel" --description "Neue Desc"
  
  # Batch-Update aus JSON-Config
  python studio_api_bypass.py --batch-update config/pending_studio_updates.json
  
  # Alle Videos listen (0 Quota!)
  python studio_api_bypass.py --list-videos
  
  # Dry-Run (nur zeigen, nichts ändern)
  python studio_api_bypass.py --batch-update config/xyz.json --dry-run

WARNUNG:
  - Cookies laufen nach ~24h ab → neu extrahieren
  - Nicht übermäßig schnell hintereinander aufrufen (Rate Limiting)
  - YouTube kann interne API jederzeit ändern (Unofficial!)

Basiert auf: https://github.com/adasq/youtube-studio (MIT License)
"""

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

import requests

# ─────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────
YT_STUDIO_URL = 'https://studio.youtube.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'  # remAIke_IT

COOKIES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'studio_cookies.json')
REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')

# Rate limiting: min seconds between API calls
MIN_DELAY_SECONDS = 1.5


# ─────────────────────────────────────────────────
# SAPISIDHASH Generation (YouTube Auth)
# ─────────────────────────────────────────────────
def generate_sapisidhash(sapisid: str, origin: str = YT_STUDIO_URL) -> str:
    """Generate SAPISIDHASH for YouTube authentication."""
    timestamp = str(int(time.time()))
    hash_input = f"{timestamp} {sapisid} {origin}"
    hash_value = hashlib.sha1(hash_input.encode('utf-8')).hexdigest()
    return f"{timestamp}_{hash_value}"


# ─────────────────────────────────────────────────
# Cookie Extraction via Playwright
# ─────────────────────────────────────────────────
def _is_chrome_running() -> bool:
    """Check if Chrome is currently running (Windows)."""
    import subprocess
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/NH'],
            capture_output=True, text=True, timeout=5
        )
        return 'chrome.exe' in result.stdout.lower()
    except Exception:
        return False


def _extract_via_playwright(user_data_dir: str, headless: bool) -> Dict:
    """Extract cookies by launching Playwright with Chrome user data dir."""
    from playwright.sync_api import sync_playwright
    
    required_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
    optional_cookies = ['LOGIN_INFO', 'VISITOR_INFO1_LIVE', '__Secure-1PSID', '__Secure-3PSID']
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check'
            ],
            ignore_default_args=['--enable-automation']
        )
        
        page = browser.new_page()
        print("  → Lade YouTube Studio...")
        page.goto('https://studio.youtube.com', wait_until='networkidle', timeout=45000)
        time.sleep(3)
        
        # Get all cookies for .youtube.com
        all_cookies = browser.cookies('https://www.youtube.com')
        
        cookie_dict = {}
        for cookie in all_cookies:
            if cookie['name'] in required_cookies + optional_cookies:
                cookie_dict[cookie['name']] = cookie['value']
        
        # Extract session token
        session_token = None
        try:
            session_token = page.evaluate('''() => {
                try {
                    return window.ytcfg?.data_?.XSRF_TOKEN || 
                           document.querySelector('script[nonce]')?.textContent?.match(/"XSRF_TOKEN":"([^"]+)"/)?.[1] ||
                           null;
                } catch(e) { return null; }
            }''')
        except Exception:
            pass
        
        # Extract innertube config
        innertube_config = None
        try:
            innertube_config = page.evaluate('''() => {
                try {
                    return {
                        INNERTUBE_API_KEY: window.ytcfg?.data_?.INNERTUBE_API_KEY,
                        DELEGATED_SESSION_ID: window.ytcfg?.data_?.DELEGATED_SESSION_ID,
                        CHANNEL_ID: window.ytcfg?.data_?.CHANNEL_ID,
                        VISITOR_DATA: window.ytcfg?.data_?.VISITOR_DATA
                    };
                } catch(e) { return null; }
            }''')
        except Exception:
            pass
        
        browser.close()
    
    return cookie_dict, session_token, innertube_config


def _extract_via_cdp(port: int = 9222) -> Dict:
    """Extract cookies by connecting to a running Chrome via CDP."""
    from playwright.sync_api import sync_playwright
    
    required_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
    optional_cookies = ['LOGIN_INFO', 'VISITOR_INFO1_LIVE', '__Secure-1PSID', '__Secure-3PSID']
    
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f'http://127.0.0.1:{port}')
        
        # Use existing context or create new page
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        
        print("  → Lade YouTube Studio (via CDP)...")
        page.goto('https://studio.youtube.com', wait_until='networkidle', timeout=45000)
        time.sleep(3)
        
        all_cookies = context.cookies('https://www.youtube.com')
        
        cookie_dict = {}
        for cookie in all_cookies:
            if cookie['name'] in required_cookies + optional_cookies:
                cookie_dict[cookie['name']] = cookie['value']
        
        session_token = None
        try:
            session_token = page.evaluate('''() => {
                try {
                    return window.ytcfg?.data_?.XSRF_TOKEN || null;
                } catch(e) { return null; }
            }''')
        except Exception:
            pass
        
        innertube_config = None
        try:
            innertube_config = page.evaluate('''() => {
                try {
                    return {
                        INNERTUBE_API_KEY: window.ytcfg?.data_?.INNERTUBE_API_KEY,
                        DELEGATED_SESSION_ID: window.ytcfg?.data_?.DELEGATED_SESSION_ID,
                        CHANNEL_ID: window.ytcfg?.data_?.CHANNEL_ID,
                        VISITOR_DATA: window.ytcfg?.data_?.VISITOR_DATA
                    };
                } catch(e) { return null; }
            }''')
        except Exception:
            pass
        
        page.close()
        browser.close()
    
    return cookie_dict, session_token, innertube_config


def extract_cookies_manual() -> Dict:
    """Guide user to manually extract cookies from Chrome DevTools."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🍪 MANUELLE COOKIE-EXTRAKTION                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1. Öffne Chrome → https://studio.youtube.com                ║
║  2. F12 (DevTools) → Application Tab → Cookies               ║
║  3. Klicke auf "https://studio.youtube.com"                   ║
║  4. Kopiere die Werte für:                                    ║
║     - SID                                                     ║
║     - HSID                                                    ║
║     - SSID                                                    ║
║     - APISID                                                  ║
║     - SAPISID                                                 ║
║                                                               ║
║  5. In der Console (F12 → Console) eingeben:                  ║
║     copy(JSON.stringify(window.ytcfg?.data_))                 ║
║     → Das gibt dir den Innertube Config als JSON!             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    cookies = {}
    for name in ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']:
        value = input(f"  {name}: ").strip()
        if not value:
            print(f"  ❌ {name} ist Pflicht!")
            sys.exit(1)
        cookies[name] = value
    
    print("\n  Optional (Enter zum Überspringen):")
    for name in ['LOGIN_INFO']:
        value = input(f"  {name}: ").strip()
        if value:
            cookies[name] = value
    
    # Innertube config
    innertube_config = None
    ytcfg_json = input("\n  ytcfg JSON (optional, Enter zum Überspringen): ").strip()
    if ytcfg_json:
        try:
            ytcfg = json.loads(ytcfg_json)
            innertube_config = {
                'INNERTUBE_API_KEY': ytcfg.get('INNERTUBE_API_KEY'),
                'DELEGATED_SESSION_ID': ytcfg.get('DELEGATED_SESSION_ID'),
                'CHANNEL_ID': ytcfg.get('CHANNEL_ID'),
                'VISITOR_DATA': ytcfg.get('VISITOR_DATA')
            }
        except json.JSONDecodeError:
            print("  ⚠️ JSON ungültig, übersprungen")
    
    return cookies, None, innertube_config


def extract_cookies_playwright(user_data_dir: str = None, headless: bool = False, 
                                cdp_port: int = 0, manual: bool = False) -> Dict[str, str]:
    """
    Extract YouTube cookies. Tries multiple methods:
    
    1. CDP (connect to running Chrome with --remote-debugging-port)
    2. Playwright persistent context (Chrome must be CLOSED)
    3. Manual entry (fallback)
    
    Args:
        user_data_dir: Path to Chrome user data dir
        headless: Run headless
        cdp_port: CDP port if Chrome is running with remote debugging
        manual: Skip auto-detection, go straight to manual entry
    """
    if manual:
        cookie_dict, session_token, innertube_config = extract_cookies_manual()
    elif cdp_port > 0:
        print(f"🔑 Verbinde via CDP auf Port {cdp_port}...")
        cookie_dict, session_token, innertube_config = _extract_via_cdp(cdp_port)
    else:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("ERROR: Playwright nicht installiert!")
            print("  pip install playwright")
            print("  playwright install chromium")
            sys.exit(1)
        
        if not user_data_dir:
            user_data_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
            if not os.path.exists(user_data_dir):
                print(f"ERROR: Chrome User Data nicht gefunden: {user_data_dir}")
                sys.exit(1)
        
        # Check if Chrome is running
        if _is_chrome_running():
            print("⚠️  Chrome läuft! Playwright kann das User-Data-Dir nicht teilen.")
            print()
            print("  OPTIONEN:")
            print("  ─────────")
            print("  A) Chrome SCHLIESSEN und erneut ausführen")
            print("  B) Chrome mit Remote Debugging starten:")
            print('     chrome.exe --remote-debugging-port=9222')
            print("     Dann: python studio_api_bypass.py --extract-cookies --cdp-port 9222")
            print("  C) Cookies MANUELL eingeben:")
            print("     python studio_api_bypass.py --extract-cookies --manual")
            print()
            
            choice = input("  Wähle [A/B/C] oder Enter für Abbruch: ").strip().upper()
            if choice == 'A':
                print("\n  ⏳ Warte 5 Sekunden... bitte Chrome schließen!")
                time.sleep(5)
                if _is_chrome_running():
                    print("  ❌ Chrome läuft immer noch! Bitte komplett schließen (auch Tray).")
                    sys.exit(1)
                # Fall through to Playwright
            elif choice == 'C':
                cookie_dict, session_token, innertube_config = extract_cookies_manual()
                # Skip Playwright flow
                return _save_cookies(cookie_dict, session_token, innertube_config)
            else:
                print("  Abgebrochen.")
                sys.exit(0)
        
        print(f"🔑 Extrahiere Cookies aus Chrome-Profil...")
        print(f"   Pfad: {user_data_dir}")
        
        try:
            cookie_dict, session_token, innertube_config = _extract_via_playwright(user_data_dir, headless)
        except Exception as e:
            error_msg = str(e)
            if 'Target' in error_msg and 'closed' in error_msg:
                print(f"\n❌ Chrome-Profil gesperrt! Chrome ist vermutlich noch aktiv.")
                print("   → Chrome komplett schließen (inkl. Hintergrundprozesse)")
                print("   → Oder: --manual für manuelle Eingabe")
            else:
                print(f"\n❌ Playwright Fehler: {e}")
            sys.exit(1)
    
    return _save_cookies(cookie_dict, session_token, innertube_config)


def _save_cookies(cookie_dict: Dict, session_token: str, innertube_config: Dict) -> Dict:
    """Validate and save extracted cookies."""
    required_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
    
    missing = [c for c in required_cookies if c not in cookie_dict]
    if missing:
        print(f"ERROR: Fehlende Cookies: {missing}")
        print("Bist du in Chrome bei YouTube angemeldet?")
        sys.exit(1)
    
    result = {
        'cookies': cookie_dict,
        'session_token': session_token,
        'innertube_config': innertube_config,
        'extracted_at': datetime.now().isoformat(),
        'expires_hint': 'Cookies sind ~24h gültig. Danach neu extrahieren!'
    }
    
    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Cookies gespeichert: {COOKIES_FILE}")
    print(f"   SID: {cookie_dict.get('SID', 'N/A')[:20]}...")
    print(f"   Innertube Key: {innertube_config.get('INNERTUBE_API_KEY', 'N/A') if innertube_config else 'N/A'}")
    print(f"   Channel: {innertube_config.get('CHANNEL_ID', 'N/A') if innertube_config else 'N/A'}")
    print(f"   ⚠️ Gültig für ~24 Stunden")
    
    return result


# ─────────────────────────────────────────────────
# YouTube Studio Internal API Client
# ─────────────────────────────────────────────────
class YouTubeStudioAPI:
    """Client for YouTube Studio's internal Innertube API. 0 Quota!"""
    
    def __init__(self, cookies_file: str = COOKIES_FILE):
        """Initialize with saved cookies."""
        if not os.path.exists(cookies_file):
            print(f"ERROR: Cookies-Datei nicht gefunden: {cookies_file}")
            print("Zuerst ausführen: python studio_api_bypass.py --extract-cookies")
            sys.exit(1)
        
        with open(cookies_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.cookies = data['cookies']
        self.session_token = data.get('session_token', '')
        self.innertube_config = data.get('innertube_config', {})
        
        # Build auth headers
        sapisid = self.cookies.get('SAPISID', '')
        sapisidhash = generate_sapisidhash(sapisid)
        
        cookie_str = '; '.join(f"{k}={v}" for k, v in self.cookies.items())
        
        self.headers = {
            'authorization': f'SAPISIDHASH {sapisidhash}',
            'content-type': 'application/json',
            'cookie': cookie_str,
            'x-origin': YT_STUDIO_URL,
            'user-agent': USER_AGENT,
            'x-goog-authuser': '0',
        }
        
        if self.innertube_config and self.innertube_config.get('VISITOR_DATA'):
            self.headers['x-goog-visitor-id'] = self.innertube_config['VISITOR_DATA']
        
        self.api_key = (self.innertube_config or {}).get('INNERTUBE_API_KEY', '')
        self.delegated_session_id = (self.innertube_config or {}).get('DELEGATED_SESSION_ID', '')
        self.channel_id = (self.innertube_config or {}).get('CHANNEL_ID', CHANNEL_ID)
        
        self._last_call_time = 0
        self.stats = {'reads': 0, 'writes': 0, 'errors': 0}
    
    def _rate_limit(self):
        """Enforce minimum delay between API calls."""
        elapsed = time.time() - self._last_call_time
        if elapsed < MIN_DELAY_SECONDS:
            time.sleep(MIN_DELAY_SECONDS - elapsed)
        self._last_call_time = time.time()
    
    def _build_context(self) -> Dict:
        """Build the standard innertube context object."""
        return {
            "client": {
                "clientName": 62,
                "clientVersion": "1.20240219.03.00",
                "hl": "de",
                "gl": "DE",
                "experimentsToken": "",
                "utcOffsetMinutes": 60,
                "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                "screenWidthPoints": 1920,
                "screenHeightPoints": 1080,
                "screenPixelDensity": 1,
                "screenDensityFloat": 1
            },
            "request": {
                "returnLogEntry": True,
                "internalExperimentFlags": [],
                "sessionInfo": {
                    "token": self.session_token or ''
                }
            },
            "user": {
                "onBehalfOfUser": self.delegated_session_id,
                "delegationContext": {
                    "externalChannelId": self.channel_id,
                    "roleType": {
                        "channelRoleType": "CREATOR_CHANNEL_ROLE_TYPE_OWNER"
                    }
                },
                "serializedDelegationContext": ""
            },
            "clientScreenNonce": ""
        }
    
    def _api_call(self, endpoint: str, body: Dict) -> Dict:
        """Make an internal API call to YouTube Studio."""
        self._rate_limit()
        
        url = f"{YT_STUDIO_URL}/youtubei/v1/{endpoint}?alt=json"
        if self.api_key:
            url += f"&key={self.api_key}"
        
        try:
            response = requests.post(url, headers=self.headers, json=body, timeout=30)
            
            if response.status_code == 401:
                print("❌ ERROR 401: Unauthorized - Cookies abgelaufen!")
                print("   → python studio_api_bypass.py --extract-cookies")
                return {'error': 'unauthorized', 'status': 401}
            
            if response.status_code == 403:
                print("❌ ERROR 403: Forbidden - Session Token ungültig!")
                print("   → python studio_api_bypass.py --extract-cookies")
                return {'error': 'forbidden', 'status': 403}
            
            if response.status_code != 200:
                print(f"❌ ERROR {response.status_code}: {response.text[:200]}")
                return {'error': f'http_{response.status_code}', 'status': response.status_code}
            
            return response.json()
            
        except Exception as e:
            print(f"❌ API Call Error: {e}")
            self.stats['errors'] += 1
            return {'error': str(e)}
    
    # ──────────────────────────────────────────
    # READ Operations (0 Quota!)
    # ──────────────────────────────────────────
    
    def get_video(self, video_id: str) -> Dict:
        """Get video details via internal API. 0 Quota!"""
        body = {
            "externalVideoId": video_id,
            "videoIds": [video_id],
            "mask": {
                "channelId": True,
                "videoId": True,
                "lengthSeconds": True,
                "title": True,
                "description": True,
                "draftStatus": True,
                "downloadUrl": True,
                "watchUrl": True,
                "privacy": True,
                "status": True,
                "statusDetails": {"all": True},
                "thumbnailDetails": {"all": True},
                "titleFormattedString": {"all": True},
                "descriptionFormattedString": {"all": True},
                "metrics": {"all": True},
                "permissions": {"all": True},
                "timeCreatedSeconds": True,
                "timePublishedSeconds": True,
                "origin": True,
                "features": {"all": True},
                "responseStatus": {"all": True},
                "monetization": {"all": True},
                "visibility": {"all": True},
                "contentType": True,
                "videoResolutions": {"all": True},
                "tags": True,
                "category": True,
                "audienceRestriction": {"all": True},
                "shorts": {"all": True},
                "remix": {"isSource": True}
            },
            "context": self._build_context()
        }
        
        result = self._api_call('creator/get_creator_videos', body)
        self.stats['reads'] += 1
        return result
    
    def list_videos(self, page_size: int = 50, page_token: str = None) -> Dict:
        """List all channel videos via internal API. 0 Quota!"""
        body = {
            "filter": {
                "and": {
                    "operands": [
                        {"channelIdIs": {"value": self.channel_id}},
                        {"videoOriginIs": {"value": "VIDEO_ORIGIN_UPLOAD"}}
                    ]
                }
            },
            "order": "VIDEO_ORDER_DISPLAY_TIME_DESC",
            "pageSize": page_size,
            "mask": {
                "channelId": True,
                "videoId": True,
                "lengthSeconds": True,
                "title": True,
                "description": True,
                "privacy": True,
                "status": True,
                "timeCreatedSeconds": True,
                "timePublishedSeconds": True,
                "metrics": {"all": True},
                "category": True,
                "tags": True,
                "origin": True,
                "livestream": {"all": True},
                "premiere": {"all": True}
            },
            "context": self._build_context()
        }
        
        if page_token:
            body['pageToken'] = page_token
        
        result = self._api_call('creator/list_creator_videos', body)
        self.stats['reads'] += 1
        return result
    
    # ──────────────────────────────────────────
    # WRITE Operations (0 Quota!)
    # ──────────────────────────────────────────
    
    def update_video_metadata(self, video_id: str, 
                               title: str = None,
                               description: str = None,
                               tags: List[str] = None,
                               category: int = None,
                               privacy: str = None,
                               made_for_kids: bool = None,
                               dry_run: bool = False) -> Dict:
        """
        Update video metadata via internal API. 0 Quota!
        
        Args:
            video_id: YouTube video ID
            title: New title (None = don't change)
            description: New description (None = don't change)
            tags: New tags list (None = don't change)
            category: Category ID (None = don't change)
            privacy: 'PUBLIC', 'PRIVATE', 'UNLISTED' (None = don't change)
            made_for_kids: True/False (None = don't change)
            dry_run: If True, only show what would be done
        
        Returns:
            API response dict
        """
        changes = []
        if title: changes.append(f"Title: {title[:60]}...")
        if description: changes.append(f"Desc: {len(description)} chars")
        if tags: changes.append(f"Tags: {len(tags)} tags")
        if category: changes.append(f"Category: {category}")
        if privacy: changes.append(f"Privacy: {privacy}")
        
        print(f"  📝 {video_id}: {', '.join(changes)}")
        
        if dry_run:
            print(f"     [DRY-RUN] Keine Änderung")
            return {'dry_run': True, 'video_id': video_id, 'changes': changes}
        
        # Build the metadata update request
        body = {
            "encryptedVideoId": video_id,
            "videoReadMask": {},
            "context": self._build_context()
        }
        
        # Add title
        if title is not None:
            body["title"] = {"newTitle": title}
        
        # Add description
        if description is not None:
            body["description"] = {
                "newDescription": description,
                "shouldSegment": True
            }
        
        # Add tags
        if tags is not None:
            body["tags"] = {
                "newTags": tags
            }
        
        # Add category
        if category is not None:
            body["category"] = {
                "newCategoryId": category
            }
        
        # Add privacy
        if privacy is not None:
            privacy_map = {
                'PUBLIC': 'PUBLIC',
                'PRIVATE': 'PRIVATE', 
                'UNLISTED': 'UNLISTED'
            }
            body["privacy"] = {
                "newPrivacy": privacy_map.get(privacy.upper(), privacy)
            }
        
        # Add made for kids
        if made_for_kids is not None:
            body["madeForKids"] = {
                "newMfk": "MFK_ON" if made_for_kids else "MFK_OFF"
            }
        
        # Self-certification (required for metadata updates)
        body["selfCertification"] = {
            "newSelfCertificationData": {
                "questionnaireAnswers": [
                    {"question": q, "answer": "VIDEO_SELF_CERTIFICATION_ANSWER_SKIPPED"}
                    for q in [
                        "VIDEO_SELF_CERTIFICATION_QUESTION_PY",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_SC",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_VG",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_HD",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_DG",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_HH",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_FM",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_SE",
                        "VIDEO_SELF_CERTIFICATION_QUESTION_SK"
                    ]
                ],
                "certificationMethod": "VIDEO_SELF_CERTIFICATION_METHOD_DEFAULT_NONE",
                "questionnaireVersion": "VIDEO_SELF_CERTIFICATION_QUESTIONNAIRE_VERSION_8"
            }
        }
        
        result = self._api_call('video_manager/metadata_update', body)
        self.stats['writes'] += 1
        
        # Check for success
        if 'error' not in result:
            overall = result.get('overallResult', {}).get('resultCode', 'UNKNOWN')
            if overall == 'UPDATE_SUCCESS':
                print(f"     ✅ Erfolgreich!")
            else:
                print(f"     ⚠️ Result: {overall}")
                # Check individual fields
                for field in ['title', 'description', 'tags', 'category', 'privacy']:
                    field_result = result.get(field, {})
                    if field_result and not field_result.get('success', True):
                        print(f"     ❌ {field}: FAILED")
        
        return result
    
    def set_endscreen(self, video_id: str, video_length_sec: int, 
                      elements: List[Dict] = None, dry_run: bool = False) -> Dict:
        """Set endscreen for a video. 0 Quota!"""
        if dry_run:
            print(f"  🎬 {video_id}: Endscreen setzen [DRY-RUN]")
            return {'dry_run': True}
        
        start_ms = (video_length_sec - 20) * 1000
        
        if elements is None:
            # Default: Recent upload + Subscribe
            elements = [
                {
                    "left": 0.022807017,
                    "top": 0.13084112,
                    "aspectRatio": 1.7777777777777777,
                    "width": 0.32280701754385965,
                    "offsetMs": 0,
                    "durationMs": 20000,
                    "videoEndscreenElement": {
                        "videoType": "VIDEO_TYPE_RECENT_UPLOAD"
                    }
                },
                {
                    "left": 0.654386,
                    "top": 0.13084112,
                    "aspectRatio": 1.7777777777777777,
                    "width": 0.15438597000000004,
                    "offsetMs": 0,
                    "durationMs": 20000,
                    "channelEndscreenElement": {
                        "channelId": self.channel_id,
                        "isSubscribe": True,
                        "metadata": ""
                    }
                }
            ]
        
        body = {
            "endscreenEdit": {
                "endscreen": {
                    "responseStatus": {"statusCode": "CREATOR_ENTITY_STATUS_OK"},
                    "encryptedVideoId": video_id,
                    "startMs": start_ms,
                    "elements": elements
                }
            },
            "externalVideoId": video_id,
            "context": self._build_context()
        }
        
        result = self._api_call('video_editor/edit_video', body)
        self.stats['writes'] += 1
        return result
    
    # ──────────────────────────────────────────
    # BATCH Operations
    # ──────────────────────────────────────────
    
    def batch_update(self, updates: List[Dict], dry_run: bool = False) -> List[Dict]:
        """
        Batch update multiple videos from a list of update dicts.
        
        Each dict should have:
            {
                "video_id": "abc123",
                "title": "New Title",       # optional
                "description": "New Desc",  # optional
                "tags": ["tag1", "tag2"],    # optional
                "category": 27,             # optional
            }
        
        Returns list of results.
        """
        results = []
        total = len(updates)
        success = 0
        failed = 0
        skipped = 0
        
        print(f"\n{'='*60}")
        print(f"🚀 BATCH UPDATE: {total} Videos")
        print(f"   Mode: {'DRY-RUN' if dry_run else '🔴 LIVE'}")
        print(f"   Quota-Kosten: 0 (Studio Internal API)")
        print(f"{'='*60}\n")
        
        for i, update in enumerate(updates, 1):
            video_id = update.get('video_id')
            if not video_id:
                print(f"  [{i}/{total}] ⚠️ Kein video_id - übersprungen")
                skipped += 1
                continue
            
            print(f"  [{i}/{total}] ", end='')
            
            try:
                result = self.update_video_metadata(
                    video_id=video_id,
                    title=update.get('title'),
                    description=update.get('description'),
                    tags=update.get('tags'),
                    category=update.get('category'),
                    privacy=update.get('privacy'),
                    made_for_kids=update.get('made_for_kids'),
                    dry_run=dry_run
                )
                
                results.append({
                    'video_id': video_id,
                    'status': 'success' if 'error' not in result else 'error',
                    'result': result
                })
                
                if 'error' not in result:
                    success += 1
                else:
                    failed += 1
                    # Stop on auth errors
                    if result.get('status') in [401, 403]:
                        print("\n🛑 Auth-Fehler! Abbruch. Cookies neu extrahieren!")
                        break
                
            except Exception as e:
                print(f"     ❌ Exception: {e}")
                failed += 1
                results.append({
                    'video_id': video_id,
                    'status': 'exception',
                    'error': str(e)
                })
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 ERGEBNIS:")
        print(f"   ✅ Erfolgreich: {success}")
        print(f"   ❌ Fehlgeschlagen: {failed}")
        print(f"   ⏭️ Übersprungen: {skipped}")
        print(f"   📊 API Calls: {self.stats['reads']} reads, {self.stats['writes']} writes")
        print(f"   💰 Quota verbraucht: 0")
        print(f"{'='*60}")
        
        return results


# ─────────────────────────────────────────────────
# Converter: Existing configs → Studio API format
# ─────────────────────────────────────────────────
def convert_channel_fix_to_updates(fix_file: str) -> List[Dict]:
    """
    Convert our existing channel_master_fix_prioritized.json format
    to Studio API batch update format.
    """
    with open(fix_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updates = []
    
    # Handle different config formats
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and 'videos' in data:
        items = data['videos']
    elif isinstance(data, dict) and 'updates' in data:
        items = data['updates']
    else:
        # Try to find video entries in any format
        items = data if isinstance(data, list) else [data]
    
    for item in items:
        update = {}
        
        # Map from various config formats
        video_id = (item.get('video_id') or item.get('id') or 
                    item.get('videoId') or item.get('video_id'))
        if not video_id:
            continue
        
        update['video_id'] = video_id
        
        # Title
        new_title = item.get('new_title') or item.get('title') or item.get('newTitle')
        if new_title:
            update['title'] = new_title
        
        # Description
        new_desc = (item.get('new_description') or item.get('description') or 
                    item.get('newDescription'))
        if new_desc:
            update['description'] = new_desc
        
        # Tags
        new_tags = item.get('new_tags') or item.get('tags') or item.get('newTags')
        if new_tags:
            update['tags'] = new_tags if isinstance(new_tags, list) else [new_tags]
        
        # Category
        new_cat = item.get('new_category') or item.get('category') or item.get('categoryId')
        if new_cat:
            update['category'] = int(new_cat)
        
        if len(update) > 1:  # Has at least video_id + one change
            updates.append(update)
    
    return updates


# ─────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='YouTube Studio Internal API - 0 Quota Updates!',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
BEISPIELE:
  # Cookies extrahieren (einmalig, ~24h gültig)
  python studio_api_bypass.py --extract-cookies
  
  # Ein Video updaten
  python studio_api_bypass.py --update-video VIDEO_ID --title "Neuer Titel"
  
  # Batch-Update aus Config-Datei
  python studio_api_bypass.py --batch-update config/pending_updates.json
  
  # Alle Videos listen
  python studio_api_bypass.py --list-videos
  
  # Dry-Run (nur zeigen)
  python studio_api_bypass.py --batch-update config/xyz.json --dry-run
        """
    )
    
    # Actions
    parser.add_argument('--extract-cookies', action='store_true',
                        help='Cookies aus Chrome-Profil extrahieren')
    parser.add_argument('--update-video', type=str, metavar='VIDEO_ID',
                        help='Einzelnes Video updaten')
    parser.add_argument('--batch-update', type=str, metavar='JSON_FILE',
                        help='Batch-Update aus JSON-Config')
    parser.add_argument('--list-videos', action='store_true',
                        help='Alle Channel-Videos listen')
    parser.add_argument('--get-video', type=str, metavar='VIDEO_ID',
                        help='Video-Details abrufen')
    
    # Update parameters
    parser.add_argument('--title', type=str, help='Neuer Titel')
    parser.add_argument('--description', type=str, help='Neue Beschreibung')
    parser.add_argument('--tags', type=str, nargs='+', help='Neue Tags')
    parser.add_argument('--category', type=int, help='Neue Kategorie-ID')
    parser.add_argument('--privacy', type=str, choices=['PUBLIC', 'PRIVATE', 'UNLISTED'],
                        help='Neue Privacy-Einstellung')
    
    # Options
    parser.add_argument('--dry-run', action='store_true',
                        help='Nur simulieren, keine Änderungen')
    parser.add_argument('--user-data-dir', type=str,
                        help='Chrome User Data Verzeichnis')
    parser.add_argument('--headless', action='store_true',
                        help='Browser unsichtbar starten')
    parser.add_argument('--cdp-port', type=int, default=0,
                        help='CDP Port (Chrome mit --remote-debugging-port starten)')
    parser.add_argument('--manual', action='store_true',
                        help='Cookies manuell eingeben (kein Browser nötig)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Max. Anzahl Videos verarbeiten')
    parser.add_argument('--delay', type=float, default=1.5,
                        help='Pause zwischen API-Calls (Sekunden)')
    parser.add_argument('--save-report', type=str, metavar='FILE',
                        help='Ergebnis-Report speichern')
    
    args = parser.parse_args()
    
    # ────────────────────────────────────────
    # Action: Extract Cookies
    # ────────────────────────────────────────
    if args.extract_cookies:
        extract_cookies_playwright(
            user_data_dir=args.user_data_dir,
            headless=args.headless,
            cdp_port=args.cdp_port,
            manual=args.manual
        )
        return
    
    # ────────────────────────────────────────
    # Action: List Videos
    # ────────────────────────────────────────
    if args.list_videos:
        api = YouTubeStudioAPI()
        print("\n📋 Channel Videos (via Studio Internal API, 0 Quota):\n")
        
        all_videos = []
        page_token = None
        page = 1
        
        while True:
            result = api.list_videos(page_size=50, page_token=page_token)
            
            if 'error' in result:
                print(f"❌ Fehler: {result['error']}")
                break
            
            videos = result.get('videos', [])
            if not videos:
                break
            
            for v in videos:
                vid = v.get('videoId', '?')
                title = v.get('title', {}).get('runs', [{}])[0].get('text', v.get('title', '?'))
                if isinstance(title, dict):
                    title = str(title)
                status = v.get('status', '?')
                privacy = v.get('privacy', '?')
                views = v.get('metrics', {}).get('views', '?')
                
                all_videos.append({
                    'id': vid,
                    'title': title[:80],
                    'status': status,
                    'privacy': privacy,
                    'views': views
                })
                
                print(f"  {vid} | {privacy:10s} | {str(views):>8s} views | {str(title)[:70]}")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
            page += 1
        
        print(f"\n📊 Gesamt: {len(all_videos)} Videos geladen (0 Quota!)")
        
        if args.save_report:
            report_path = args.save_report
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(all_videos, f, indent=2, ensure_ascii=False)
            print(f"📄 Report gespeichert: {report_path}")
        
        return
    
    # ────────────────────────────────────────
    # Action: Get Video Details
    # ────────────────────────────────────────
    if args.get_video:
        api = YouTubeStudioAPI()
        result = api.get_video(args.get_video)
        
        if 'error' not in result:
            videos = result.get('videos', [])
            if videos:
                v = videos[0]
                print(f"\n📹 Video Details (0 Quota!):")
                print(f"   ID: {v.get('videoId')}")
                print(f"   Title: {v.get('title')}")
                print(f"   Status: {v.get('status')}")
                print(f"   Privacy: {v.get('privacy')}")
                print(f"   Length: {v.get('lengthSeconds')}s")
                print(f"   Category: {v.get('category')}")
                
                desc = v.get('description', {})
                if isinstance(desc, dict):
                    desc_text = desc.get('runs', [{}])[0].get('text', str(desc))
                else:
                    desc_text = str(desc)
                print(f"   Description: {desc_text[:200]}...")
                
                tags = v.get('tags', [])
                print(f"   Tags: {tags}")
                
                metrics = v.get('metrics', {})
                print(f"   Views: {metrics.get('views', '?')}")
                print(f"   Likes: {metrics.get('likes', '?')}")
                print(f"   Comments: {metrics.get('comments', '?')}")
        else:
            print(f"❌ Fehler: {result}")
        
        return
    
    # ────────────────────────────────────────
    # Action: Update Single Video
    # ────────────────────────────────────────
    if args.update_video:
        if not any([args.title, args.description, args.tags, args.category, args.privacy]):
            print("ERROR: Mindestens eine Änderung angeben (--title, --description, --tags, --category, --privacy)")
            sys.exit(1)
        
        api = YouTubeStudioAPI()
        global MIN_DELAY_SECONDS
        MIN_DELAY_SECONDS = args.delay
        
        result = api.update_video_metadata(
            video_id=args.update_video,
            title=args.title,
            description=args.description,
            tags=args.tags,
            category=args.category,
            privacy=args.privacy,
            dry_run=args.dry_run
        )
        
        if args.save_report:
            with open(args.save_report, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        return
    
    # ────────────────────────────────────────
    # Action: Batch Update
    # ────────────────────────────────────────
    if args.batch_update:
        if not os.path.exists(args.batch_update):
            print(f"ERROR: Datei nicht gefunden: {args.batch_update}")
            sys.exit(1)
        
        api = YouTubeStudioAPI()
        MIN_DELAY_SECONDS = args.delay
        
        # Try to load as our format or convert from existing config format
        updates = convert_channel_fix_to_updates(args.batch_update)
        
        if args.limit > 0:
            updates = updates[:args.limit]
        
        if not updates:
            print("❌ Keine Updates in der Datei gefunden!")
            sys.exit(1)
        
        results = api.batch_update(updates, dry_run=args.dry_run)
        
        # Save report
        report_file = args.save_report or os.path.join(
            REPORT_DIR,
            f"studio_bypass_report_{datetime.now().strftime('%Y_%m_%d_%H%M')}.json"
        )
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'source': args.batch_update,
                'dry_run': args.dry_run,
                'total': len(updates),
                'results': results,
                'stats': api.stats
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Report: {report_file}")
        return
    
    # No action specified
    parser.print_help()


if __name__ == '__main__':
    main()
