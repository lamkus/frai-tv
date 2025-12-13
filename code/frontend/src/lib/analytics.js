/**
 * remAIke.TV Analytics System
 *

import { initExternalAnalytics, trackExternalEvent, trackExternalPageView } from './externalAnalytics';
 * Umfassendes Tracking-System für Nutzerverhalten:
 * - Seitenaufrufe & Navigation
 * - Video-Interaktionen (Play, Pause, Seek, Complete)
 * - Watchtime & Engagement
 * - Klick-Heatmaps
 * - Session-Tracking
 * - Geräte & Browser-Infos
 *
 * DSGVO-konform: Daten werden nur lokal gespeichert
 * oder nach expliziter Zustimmung an Server gesendet.
 */

// ============================================================================
// STORAGE KEYS
// ============================================================================

const STORAGE_KEYS = {
  SESSIONS: 'remaike_analytics_sessions',
  CURRENT_SESSION: 'remaike_analytics_current',
  VIDEO_EVENTS: 'remaike_analytics_videos',
  PAGE_VIEWS: 'remaike_analytics_pages',
  INTERACTIONS: 'remaike_analytics_interactions',
  CONSENT: 'remaike_analytics_consent',
};

function hasExplicitConsent() {
  try {
    return localStorage.getItem(STORAGE_KEYS.CONSENT) === 'true';
  } catch {
    return false;
  }
}

// ============================================================================
// SESSION MANAGEMENT
// ============================================================================

let currentSession = null;
let sessionStartTime = null;
let pageStartTime = null;
let currentPagePath = null;

/**
 * Generiert eine eindeutige Session-ID
 */
function generateSessionId() {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Generiert eine anonyme Visitor-ID (persistent)
 */
function getVisitorId() {
  let visitorId = localStorage.getItem('remaike_visitor_id');
  if (!visitorId) {
    visitorId = `visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('remaike_visitor_id', visitorId);
  }
  return visitorId;
}

/**
 * Startet eine neue Analytics-Session
 */
export function startSession() {
  if (!hasExplicitConsent()) return null;
  sessionStartTime = Date.now();
  // lastActivityTime = sessionStartTime;

  currentSession = {
    id: generateSessionId(),
    visitorId: getVisitorId(),
    startTime: new Date().toISOString(),
    endTime: null,

    // Geräteinformationen
    device: getDeviceInfo(),

    // Engagement-Metriken
    pageViews: 0,
    totalTimeOnSite: 0,
    videosWatched: 0,
    totalWatchTime: 0,
    interactions: 0,

    // Navigation-Pfad
    navigationPath: [],

    // Referrer
    referrer: document.referrer || 'direct',
    entryPage: window.location.pathname,
  };

  // Session in SessionStorage speichern
  sessionStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, JSON.stringify(currentSession));

  // Activity-Listener
  setupActivityTracking();

  console.log('[Analytics] Session gestartet:', currentSession.id);

  return currentSession;
}

/**
 * Beendet die aktuelle Session
 */
export function endSession() {
  if (!hasExplicitConsent()) return;
  if (!currentSession) return;

  currentSession.endTime = new Date().toISOString();
  currentSession.totalTimeOnSite = Math.round((Date.now() - sessionStartTime) / 1000);

  // Session zu Historie hinzufügen
  const sessions = JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSIONS) || '[]');
  sessions.push(currentSession);

  // Nur die letzten 100 Sessions behalten
  if (sessions.length > 100) {
    sessions.splice(0, sessions.length - 100);
  }

  localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
  sessionStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION);

  console.log('[Analytics] Session beendet:', currentSession.id);

  currentSession = null;
}

/**
 * Holt Geräteinformationen
 */
function getDeviceInfo() {
  const ua = navigator.userAgent;

  return {
    // Browser
    browser: getBrowserName(ua),
    browserVersion: getBrowserVersion(ua),

    // Betriebssystem
    os: getOS(ua),

    // Gerät
    deviceType: getDeviceType(),
    screenWidth: window.screen.width,
    screenHeight: window.screen.height,
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    pixelRatio: window.devicePixelRatio || 1,

    // Verbindung
    connectionType: navigator.connection?.effectiveType || 'unknown',

    // Sprache
    language: navigator.language,
    languages: navigator.languages?.slice(0, 3) || [navigator.language],

    // Zeitzone
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  };
}

function getBrowserName(ua) {
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Chrome')) return 'Chrome';
  if (ua.includes('Safari')) return 'Safari';
  if (ua.includes('Edge')) return 'Edge';
  if (ua.includes('Opera')) return 'Opera';
  return 'Unknown';
}

function getBrowserVersion(ua) {
  const match = ua.match(/(Firefox|Chrome|Safari|Edge|Opera)[/\s](\d+)/);
  return match ? match[2] : 'Unknown';
}

function getOS(ua) {
  if (ua.includes('Windows')) return 'Windows';
  if (ua.includes('Mac')) return 'macOS';
  if (ua.includes('Linux')) return 'Linux';
  if (ua.includes('Android')) return 'Android';
  if (ua.includes('iOS') || ua.includes('iPhone') || ua.includes('iPad')) return 'iOS';
  return 'Unknown';
}

function getDeviceType() {
  const width = window.innerWidth;
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
}

// ============================================================================
// PAGE VIEW TRACKING
// ============================================================================

/**
 * Trackt einen Seitenaufruf
 */
export function trackPageView(path, title) {
  if (!hasExplicitConsent()) return;
  if (!currentSession) startSession();

  const now = Date.now();

  // Vorherige Seite abschließen
  if (currentPagePath && pageStartTime) {
    const timeOnPage = Math.round((now - pageStartTime) / 1000);
    savePageViewDuration(currentPagePath, timeOnPage);
  }

  // Neue Seite starten
  currentPagePath = path || window.location.pathname;
  pageStartTime = now;

  const pageView = {
    sessionId: currentSession.id,
    path: currentPagePath,
    title: title || document.title,
    timestamp: new Date().toISOString(),
    referrerPath: currentSession.navigationPath.slice(-1)[0] || null,
  };

  // Zur Navigation hinzufügen
  currentSession.navigationPath.push(currentPagePath);
  currentSession.pageViews++;

  // Speichern
  const pageViews = JSON.parse(localStorage.getItem(STORAGE_KEYS.PAGE_VIEWS) || '[]');
  pageViews.push(pageView);

  // Nur die letzten 1000 Page Views behalten
  if (pageViews.length > 1000) {
    pageViews.splice(0, pageViews.length - 1000);
  }

  localStorage.setItem(STORAGE_KEYS.PAGE_VIEWS, JSON.stringify(pageViews));

  console.log('[Analytics] Page View:', currentPagePath);

  // External analytics
  try {
    initExternalAnalytics();
    trackExternalPageView(currentPagePath, pageView.title);
  } catch {
    // ignore
  }
}

function savePageViewDuration(path, duration) {
  const pageViews = JSON.parse(localStorage.getItem(STORAGE_KEYS.PAGE_VIEWS) || '[]');

  // Finde den letzten Eintrag für diesen Pfad
  for (let i = pageViews.length - 1; i >= 0; i--) {
    if (pageViews[i].path === path && !pageViews[i].duration) {
      pageViews[i].duration = duration;
      break;
    }
  }

  localStorage.setItem(STORAGE_KEYS.PAGE_VIEWS, JSON.stringify(pageViews));
}

// ============================================================================
// VIDEO ANALYTICS
// ============================================================================

const videoSessions = new Map();

/**
 * Startet das Tracking für ein Video
 */
export function trackVideoStart(videoId, videoTitle, startPosition = 0) {
  if (!hasExplicitConsent()) return null;
  if (!currentSession) startSession();

  const videoSession = {
    videoId,
    videoTitle,
    sessionId: currentSession.id,
    startTime: new Date().toISOString(),
    startPosition,

    // Engagement-Metriken
    totalWatchTime: 0,
    completionRate: 0,
    seekCount: 0,
    pauseCount: 0,
    replayCount: 0,

    // Qualitätsänderungen
    qualityChanges: [],

    // Watchtime-Segmente (welche Teile wurden gesehen)
    watchedSegments: [],

    // Events
    events: [],
  };

  videoSessions.set(videoId, videoSession);

  currentSession.videosWatched++;

  trackVideoEvent(videoId, 'start', { position: startPosition });

  console.log('[Analytics] Video Start:', videoId);
  try {
    initExternalAnalytics();
    trackExternalEvent('Video', 'start', videoId, startPosition);
  } catch {
    // ignore
  }

  return videoSession;
}

/**
 * Trackt Video-Events (play, pause, seek, etc.)
 */
export function trackVideoEvent(videoId, eventType, data = {}) {
  if (!hasExplicitConsent()) return;
  const videoSession = videoSessions.get(videoId);
  if (!videoSession) return;

  const event = {
    type: eventType,
    timestamp: new Date().toISOString(),
    position: data.position || 0,
    ...data,
  };

  videoSession.events.push(event);

  // Spezifische Event-Handler
  switch (eventType) {
    case 'play':
      videoSession.lastPlayTime = Date.now();
      break;

    case 'pause':
      videoSession.pauseCount++;
      if (videoSession.lastPlayTime) {
        const watchTime = (Date.now() - videoSession.lastPlayTime) / 1000;
        videoSession.totalWatchTime += watchTime;
        videoSession.lastPlayTime = null;
      }
      break;

    case 'seek':
      videoSession.seekCount++;
      break;

    case 'quality_change':
      videoSession.qualityChanges.push({
        from: data.from,
        to: data.to,
        timestamp: event.timestamp,
      });
      break;

    case 'progress':
      // Watchtime-Segment tracken
      if (data.position && data.duration) {
        const segmentIndex = Math.floor((data.position / data.duration) * 10);
        if (!videoSession.watchedSegments.includes(segmentIndex)) {
          videoSession.watchedSegments.push(segmentIndex);
        }
        videoSession.completionRate = Math.max(
          videoSession.completionRate,
          (data.position / data.duration) * 100
        );
      }
      break;

    case 'complete':
      videoSession.completionRate = 100;
      break;

    case 'replay':
      videoSession.replayCount++;
      break;
  }

  // Session updaten
  if (currentSession) {
    currentSession.totalWatchTime = Array.from(videoSessions.values()).reduce(
      (sum, vs) => sum + vs.totalWatchTime,
      0
    );
  }

  // External analytics (keep it lightweight)
  try {
    initExternalAnalytics();
    trackExternalEvent('Video', eventType, videoId, data.position);
  } catch {
    // ignore
  }
}

/**
 * Beendet das Video-Tracking
 */
export function trackVideoEnd(videoId) {
  if (!hasExplicitConsent()) return;
  const videoSession = videoSessions.get(videoId);
  if (!videoSession) return;

  // Falls noch am Abspielen, Watchtime berechnen
  if (videoSession.lastPlayTime) {
    const watchTime = (Date.now() - videoSession.lastPlayTime) / 1000;
    videoSession.totalWatchTime += watchTime;
  }

  videoSession.endTime = new Date().toISOString();

  // Video-Event speichern
  const videoEvents = JSON.parse(localStorage.getItem(STORAGE_KEYS.VIDEO_EVENTS) || '[]');
  videoEvents.push({
    ...videoSession,
    events: videoSession.events.slice(-50), // Nur die letzten 50 Events
  });

  // Nur die letzten 500 Video-Sessions behalten
  if (videoEvents.length > 500) {
    videoEvents.splice(0, videoEvents.length - 500);
  }

  localStorage.setItem(STORAGE_KEYS.VIDEO_EVENTS, JSON.stringify(videoEvents));

  videoSessions.delete(videoId);

  console.log('[Analytics] Video End:', videoId, {
    watchTime: Math.round(videoSession.totalWatchTime),
    completion: Math.round(videoSession.completionRate),
  });

  try {
    initExternalAnalytics();
    trackExternalEvent('Video', 'end', videoId, videoSession.totalWatchTime);
  } catch {
    // ignore
  }
}

// ============================================================================
// INTERACTION TRACKING
// ============================================================================

/**
 * Trackt Benutzerinteraktionen
 */
export function trackInteraction(type, target, data = {}) {
  if (!hasExplicitConsent()) return;
  if (!currentSession) startSession();

  const interaction = {
    sessionId: currentSession.id,
    type, // 'click', 'hover', 'scroll', 'search', 'filter', etc.
    target, // Element-Identifier
    timestamp: new Date().toISOString(),
    page: window.location.pathname,
    ...data,
  };

  currentSession.interactions++;

  const interactions = JSON.parse(localStorage.getItem(STORAGE_KEYS.INTERACTIONS) || '[]');
  interactions.push(interaction);

  // Nur die letzten 2000 Interaktionen behalten
  if (interactions.length > 2000) {
    interactions.splice(0, interactions.length - 2000);
  }

  localStorage.setItem(STORAGE_KEYS.INTERACTIONS, JSON.stringify(interactions));

  try {
    initExternalAnalytics();
    trackExternalEvent('Interaction', type, String(target || ''), undefined);
  } catch {
    // ignore
  }
}

/**
 * Trackt Klicks mit Position (für Heatmaps)
 */
export function trackClick(event, elementId) {
  const rect = event.target.getBoundingClientRect();

  trackInteraction('click', elementId || event.target.tagName, {
    x: event.clientX,
    y: event.clientY,
    elementX: rect.left,
    elementY: rect.top,
    elementWidth: rect.width,
    elementHeight: rect.height,
    relativeX: ((event.clientX - rect.left) / rect.width) * 100,
    relativeY: ((event.clientY - rect.top) / rect.height) * 100,
  });
}

/**
 * Trackt Scroll-Tiefe
 */
export function trackScrollDepth(percentage) {
  trackInteraction('scroll', 'page', {
    depth: percentage,
    viewportHeight: window.innerHeight,
    documentHeight: document.documentElement.scrollHeight,
  });
}

/**
 * Trackt Suchanfragen
 */
export function trackSearch(query, resultsCount) {
  trackInteraction('search', 'search_bar', {
    query,
    resultsCount,
  });
}

/**
 * Trackt Filter-Nutzung
 */
export function trackFilter(filterType, filterValue) {
  trackInteraction('filter', filterType, {
    value: filterValue,
  });
}

// ============================================================================
// ANALYTICS REPORTS
// ============================================================================

/**
 * Holt alle Analytics-Daten
 */
export function getAnalyticsData() {
  return {
    sessions: JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSIONS) || '[]'),
    pageViews: JSON.parse(localStorage.getItem(STORAGE_KEYS.PAGE_VIEWS) || '[]'),
    videoEvents: JSON.parse(localStorage.getItem(STORAGE_KEYS.VIDEO_EVENTS) || '[]'),
    interactions: JSON.parse(localStorage.getItem(STORAGE_KEYS.INTERACTIONS) || '[]'),
    currentSession,
  };
}

/**
 * Generiert einen Dashboard-Report
 */
export function getDashboardReport(days = 7) {
  const data = getAnalyticsData();
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  // Filter nach Zeitraum
  const recentSessions = data.sessions.filter((s) => new Date(s.startTime) >= cutoffDate);
  const recentPageViews = data.pageViews.filter((p) => new Date(p.timestamp) >= cutoffDate);
  const recentVideoEvents = data.videoEvents.filter((v) => new Date(v.startTime) >= cutoffDate);
  const recentInteractions = data.interactions.filter((i) => new Date(i.timestamp) >= cutoffDate);

  // Unique Visitors
  const uniqueVisitors = new Set(recentSessions.map((s) => s.visitorId)).size;

  // Durchschnittliche Session-Dauer
  const avgSessionDuration =
    recentSessions.length > 0
      ? recentSessions.reduce((sum, s) => sum + (s.totalTimeOnSite || 0), 0) / recentSessions.length
      : 0;

  // Gesamte Watchtime
  const totalWatchTime = recentVideoEvents.reduce((sum, v) => sum + (v.totalWatchTime || 0), 0);

  // Top Videos
  const videoStats = {};
  recentVideoEvents.forEach((v) => {
    if (!videoStats[v.videoId]) {
      videoStats[v.videoId] = {
        videoId: v.videoId,
        title: v.videoTitle,
        views: 0,
        totalWatchTime: 0,
        avgCompletion: 0,
      };
    }
    videoStats[v.videoId].views++;
    videoStats[v.videoId].totalWatchTime += v.totalWatchTime || 0;
    videoStats[v.videoId].avgCompletion += v.completionRate || 0;
  });

  const topVideos = Object.values(videoStats)
    .map((v) => ({
      ...v,
      avgCompletion: v.views > 0 ? v.avgCompletion / v.views : 0,
    }))
    .sort((a, b) => b.views - a.views)
    .slice(0, 10);

  // Top Seiten
  const pageStats = {};
  recentPageViews.forEach((p) => {
    if (!pageStats[p.path]) {
      pageStats[p.path] = {
        path: p.path,
        views: 0,
        totalTime: 0,
      };
    }
    pageStats[p.path].views++;
    pageStats[p.path].totalTime += p.duration || 0;
  });

  const topPages = Object.values(pageStats)
    .sort((a, b) => b.views - a.views)
    .slice(0, 10);

  // Geräte-Verteilung
  const deviceDistribution = {};
  recentSessions.forEach((s) => {
    const device = s.device?.deviceType || 'unknown';
    deviceDistribution[device] = (deviceDistribution[device] || 0) + 1;
  });

  // Browser-Verteilung
  const browserDistribution = {};
  recentSessions.forEach((s) => {
    const browser = s.device?.browser || 'unknown';
    browserDistribution[browser] = (browserDistribution[browser] || 0) + 1;
  });

  // Traffic-Quellen
  const trafficSources = {};
  recentSessions.forEach((s) => {
    const source = s.referrer === 'direct' ? 'Direct' : new URL(s.referrer).hostname;
    trafficSources[source] = (trafficSources[source] || 0) + 1;
  });

  // Tägliche Aufschlüsselung
  const dailyStats = {};
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    dailyStats[dateStr] = {
      date: dateStr,
      sessions: 0,
      pageViews: 0,
      videoViews: 0,
      watchTime: 0,
    };
  }

  recentSessions.forEach((s) => {
    const dateStr = s.startTime.split('T')[0];
    if (dailyStats[dateStr]) {
      dailyStats[dateStr].sessions++;
    }
  });

  recentPageViews.forEach((p) => {
    const dateStr = p.timestamp.split('T')[0];
    if (dailyStats[dateStr]) {
      dailyStats[dateStr].pageViews++;
    }
  });

  recentVideoEvents.forEach((v) => {
    const dateStr = v.startTime.split('T')[0];
    if (dailyStats[dateStr]) {
      dailyStats[dateStr].videoViews++;
      dailyStats[dateStr].watchTime += v.totalWatchTime || 0;
    }
  });

  return {
    period: { days, from: cutoffDate.toISOString(), to: new Date().toISOString() },

    // Übersicht
    overview: {
      totalSessions: recentSessions.length,
      uniqueVisitors,
      totalPageViews: recentPageViews.length,
      totalVideoViews: recentVideoEvents.length,
      totalWatchTime: Math.round(totalWatchTime),
      avgSessionDuration: Math.round(avgSessionDuration),
      totalInteractions: recentInteractions.length,
    },

    // Top Content
    topVideos,
    topPages,

    // Audience
    deviceDistribution,
    browserDistribution,
    trafficSources,

    // Trend
    dailyStats: Object.values(dailyStats).reverse(),
  };
}

/**
 * Holt Video-Performance-Report
 */
export function getVideoReport(videoId) {
  const data = getAnalyticsData();

  const videoEvents = data.videoEvents.filter((v) => v.videoId === videoId);

  if (videoEvents.length === 0) {
    return null;
  }

  // Aggregierte Metriken
  const totalViews = videoEvents.length;
  const totalWatchTime = videoEvents.reduce((sum, v) => sum + (v.totalWatchTime || 0), 0);
  const avgWatchTime = totalWatchTime / totalViews;
  const avgCompletion =
    videoEvents.reduce((sum, v) => sum + (v.completionRate || 0), 0) / totalViews;

  // Segment-Heatmap (welche Teile werden am meisten gesehen)
  const segmentViews = Array(10).fill(0);
  videoEvents.forEach((v) => {
    (v.watchedSegments || []).forEach((seg) => {
      segmentViews[seg]++;
    });
  });

  // Abbruchpunkte
  const dropoffPoints = videoEvents
    .filter((v) => v.completionRate < 100)
    .map((v) => v.completionRate);

  return {
    videoId,
    title: videoEvents[0]?.videoTitle,

    metrics: {
      totalViews,
      totalWatchTime: Math.round(totalWatchTime),
      avgWatchTime: Math.round(avgWatchTime),
      avgCompletion: Math.round(avgCompletion),
      replayRate: (videoEvents.filter((v) => v.replayCount > 0).length / totalViews) * 100,
    },

    engagement: {
      segmentViews,
      avgSeeksPerView: videoEvents.reduce((sum, v) => sum + (v.seekCount || 0), 0) / totalViews,
      avgPausesPerView: videoEvents.reduce((sum, v) => sum + (v.pauseCount || 0), 0) / totalViews,
    },

    dropoff: {
      points: dropoffPoints,
      avgDropoff:
        dropoffPoints.length > 0
          ? dropoffPoints.reduce((a, b) => a + b, 0) / dropoffPoints.length
          : 100,
    },
  };
}

// ============================================================================
// ACTIVITY TRACKING (Inaktivität erkennen)
// ============================================================================

let activityTimeout = null;

function setupActivityTracking() {
  const resetActivity = () => {
    // lastActivityTime = Date.now();

    // Timeout zurücksetzen (Session endet nach 30 Min Inaktivität)
    if (activityTimeout) clearTimeout(activityTimeout);
    activityTimeout = setTimeout(() => {
      console.log('[Analytics] Session timeout wegen Inaktivität');
      endSession();
    }, 30 * 60 * 1000);
  };

  // Activity-Events
  ['mousemove', 'keydown', 'scroll', 'click', 'touchstart'].forEach((event) => {
    document.addEventListener(event, resetActivity, { passive: true });
  });

  // Visibility Change
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      // Tab wurde verlassen
      trackInteraction('visibility', 'tab', { state: 'hidden' });
    } else {
      // Tab wurde wieder aktiv
      trackInteraction('visibility', 'tab', { state: 'visible' });
      resetActivity();
    }
  });

  // Unload
  window.addEventListener('beforeunload', () => {
    endSession();
  });

  resetActivity();
}

// ============================================================================
// DATA EXPORT / CLEAR
// ============================================================================

/**
 * Exportiert alle Analytics-Daten als JSON
 */
export function exportAnalyticsData() {
  const data = getAnalyticsData();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `remaike_analytics_${new Date().toISOString().split('T')[0]}.json`;
  a.click();

  URL.revokeObjectURL(url);
}

/**
 * Löscht alle Analytics-Daten
 */
export function clearAnalyticsData() {
  Object.values(STORAGE_KEYS).forEach((key) => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });

  currentSession = null;
  videoSessions.clear();

  console.log('[Analytics] Alle Daten gelöscht');
}

/**
 * Prüft und setzt Analytics-Consent
 */
export function hasAnalyticsConsent() {
  return localStorage.getItem(STORAGE_KEYS.CONSENT) === 'true';
}

export function setAnalyticsConsent(consent) {
  localStorage.setItem(STORAGE_KEYS.CONSENT, consent ? 'true' : 'false');

  if (!consent) {
    clearAnalyticsData();
    return;
  }

  // Consent granted: initialize external analytics immediately.
  try {
    initExternalAnalytics();
  } catch {
    // ignore
  }
}

// ============================================================================
// INIT
// ============================================================================

/**
 * Initialisiert das Analytics-System
 */
export function initAnalytics() {
  // Only run analytics when explicit consent was granted.
  const consent = localStorage.getItem(STORAGE_KEYS.CONSENT);
  if (consent !== 'true') {
    console.log('[Analytics] Deaktiviert (kein Consent)');
    return;
  }

  // Session starten oder fortsetzen
  const existingSession = sessionStorage.getItem(STORAGE_KEYS.CURRENT_SESSION);

  if (existingSession) {
    currentSession = JSON.parse(existingSession);
    sessionStartTime = new Date(currentSession.startTime).getTime();
    setupActivityTracking();
    console.log('[Analytics] Session fortgesetzt:', currentSession.id);
  } else {
    startSession();
  }

  // Initial Page View
  trackPageView();

  try {
    initExternalAnalytics();
  } catch {
    // ignore
  }

  // Developer convenience: expose a debug handle when VITE_DEBUG_MODE is enabled
  try {
    if (import.meta.env.VITE_DEBUG_MODE === 'true' && typeof window !== 'undefined') {
      window.__REMAIKE_ANALYTICS__ = {
        trackVideoStart,
        trackVideoEvent,
        trackVideoEnd,
        trackPageView,
        getAnalyticsData,
      };
    }
  } catch {
    // ignore
  }
}

export default {
  initAnalytics,
  startSession,
  endSession,
  trackPageView,
  trackVideoStart,
  trackVideoEvent,
  trackVideoEnd,
  trackInteraction,
  trackClick,
  trackScrollDepth,
  trackSearch,
  trackFilter,
  getAnalyticsData,
  getDashboardReport,
  getVideoReport,
  exportAnalyticsData,
  clearAnalyticsData,
  hasAnalyticsConsent,
  setAnalyticsConsent,
};
