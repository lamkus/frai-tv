import { useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  initAnalytics,
  trackPageView,
  trackVideoStart,
  trackVideoEvent,
  trackVideoEnd,
  trackInteraction,
  trackSearch,
  trackFilter,
  trackScrollDepth,
} from './analytics';

/**
 * Hook für automatisches Page-View-Tracking
 */
export function usePageTracking() {
  const location = useLocation();

  useEffect(() => {
    trackPageView(location.pathname + location.search, document.title);
  }, [location]);
}

/**
 * Hook für Video-Analytics
 */
export function useVideoAnalytics(videoId, videoTitle) {
  const hasStarted = useRef(false);
  const lastProgress = useRef(0);

  // Video starten
  const onVideoStart = useCallback(
    (startPosition = 0) => {
      if (!hasStarted.current) {
        trackVideoStart(videoId, videoTitle, startPosition);
        hasStarted.current = true;
      }
    },
    [videoId, videoTitle]
  );

  // Play
  const onPlay = useCallback(
    (position) => {
      trackVideoEvent(videoId, 'play', { position });
    },
    [videoId]
  );

  // Pause
  const onPause = useCallback(
    (position) => {
      trackVideoEvent(videoId, 'pause', { position });
    },
    [videoId]
  );

  // Seek
  const onSeek = useCallback(
    (from, to) => {
      trackVideoEvent(videoId, 'seek', { from, to });
    },
    [videoId]
  );

  // Progress (rufe alle 10% auf)
  const onProgress = useCallback(
    (position, duration) => {
      const progressPercent = Math.floor((position / duration) * 10) * 10;

      if (progressPercent > lastProgress.current) {
        trackVideoEvent(videoId, 'progress', { position, duration });
        lastProgress.current = progressPercent;
      }
    },
    [videoId]
  );

  // Qualitätsänderung
  const onQualityChange = useCallback(
    (from, to) => {
      trackVideoEvent(videoId, 'quality_change', { from, to });
    },
    [videoId]
  );

  // Video zu Ende
  const onComplete = useCallback(() => {
    trackVideoEvent(videoId, 'complete', {});
  }, [videoId]);

  // Replay
  const onReplay = useCallback(() => {
    trackVideoEvent(videoId, 'replay', {});
  }, [videoId]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (hasStarted.current) {
        trackVideoEnd(videoId);
        hasStarted.current = false;
        lastProgress.current = 0;
      }
    };
  }, [videoId]);

  // Track End (cleanup / video ended)
  const onEnd = useCallback(() => {
    if (hasStarted.current) {
      trackVideoEnd(videoId);
    }
  }, [videoId]);

  return {
    // Original naming
    onVideoStart,
    onPlay,
    onPause,
    onSeek,
    onProgress,
    onQualityChange,
    onComplete,
    onReplay,
    onEnd,
    // Alternative naming (for compatibility with VideoPlayer)
    trackPlay: onPlay,
    trackPause: onPause,
    trackSeek: onSeek,
    trackComplete: onComplete,
    trackEnd: onEnd,
  };
}

/**
 * Hook für Scroll-Tracking
 */
export function useScrollTracking() {
  const maxScrollDepth = useRef(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = Math.round((scrollTop / docHeight) * 100);

      // Nur tracken wenn neuer Maximalwert erreicht
      const threshold = Math.floor(scrollPercent / 25) * 25; // 0, 25, 50, 75, 100
      if (threshold > maxScrollDepth.current) {
        maxScrollDepth.current = threshold;
        trackScrollDepth(threshold);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      maxScrollDepth.current = 0;
    };
  }, []);
}

/**
 * Hook für Such-Tracking
 */
export function useSearchTracking() {
  const trackSearchQuery = useCallback((query, resultsCount) => {
    trackSearch(query, resultsCount);
  }, []);

  return trackSearchQuery;
}

/**
 * Hook für Filter-Tracking
 */
export function useFilterTracking() {
  const trackFilterChange = useCallback((filterType, filterValue) => {
    trackFilter(filterType, filterValue);
  }, []);

  return trackFilterChange;
}

/**
 * Hook für allgemeine Interaktions-Tracking
 */
export function useInteractionTracking() {
  const track = useCallback((type, target, data = {}) => {
    trackInteraction(type, target, data);
  }, []);

  return track;
}

/**
 * Analytics Provider - initialisiert das System
 */
export function AnalyticsProvider({ children }) {
  useEffect(() => {
    initAnalytics();
  }, []);

  return children;
}

export default {
  usePageTracking,
  useVideoAnalytics,
  useScrollTracking,
  useSearchTracking,
  useFilterTracking,
  useInteractionTracking,
  AnalyticsProvider,
};
