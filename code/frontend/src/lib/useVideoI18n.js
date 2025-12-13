/**
 * Video i18n Hook - Mehrsprachige Video-Metadaten
 *
 * Holt Titel und Beschreibung aus dem i18n-System.
 * Fallback auf den im Video hinterlegten Text (Deutsch).
 */

import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import { remaikeVideos } from '../data/remaikeData';

// Cache für ytId -> id Mapping
const ytIdToIdMap = new Map();
remaikeVideos.forEach((v) => {
  if (v.ytId && v.id) {
    ytIdToIdMap.set(v.ytId, v.id);
  }
});

/**
 * Hook für mehrsprachige Video-Daten
 * @returns {Object} { getVideoText, localizeVideos, localizeVideo, currentLanguage }
 */
export function useVideoI18n() {
  const { t, i18n } = useTranslation();

  /**
   * Holt lokalisierten Titel und Beschreibung für ein Video
   * @param {Object} video - Video-Objekt aus remaikeData.js oder YouTube API
   * @returns {Object} { title, description } - Lokalisierte Texte
   */
  const getVideoText = (video) => {
    if (!video) return { title: '', description: '' };

    // Finde die richtige Video-ID für Übersetzungen
    // 1. Wenn video.id ein Slug ist (z.B. "rudolph-1948"), nutze es direkt
    // 2. Wenn video.id eine YouTube-ID ist, schaue nach dem Mapping via ytId
    let translationId = video.id;

    // Prüfe ob video.id wie eine YouTube-ID aussieht (11 Zeichen, alphanumerisch)
    const looksLikeYouTubeId = video.id && /^[A-Za-z0-9_-]{11}$/.test(video.id);

    if (looksLikeYouTubeId && video.ytId) {
      // video.id ist wahrscheinlich YouTube-ID, suche den richtigen Slug
      translationId = ytIdToIdMap.get(video.ytId) || video.id;
    } else if (!video.id && video.ytId) {
      // Kein id aber ytId vorhanden
      translationId = ytIdToIdMap.get(video.ytId);
    }

    if (!translationId) {
      return { title: video.title || '', description: video.description || '' };
    }

    // Versuche i18n Keys zu laden
    const titleKey = `videos.${translationId}.title`;
    const descKey = `videos.${translationId}.description`;

    // Prüfe ob Übersetzung existiert (safe check für Production)
    const hasTitle = typeof i18n.exists === 'function' ? i18n.exists(titleKey) : false;
    const hasDesc = typeof i18n.exists === 'function' ? i18n.exists(descKey) : false;

    return {
      title: hasTitle ? t(titleKey) : video.title || '',
      description: hasDesc ? t(descKey) : video.description || '',
    };
  };

  /**
   * Lokalisiert ein einzelnes Video
   * @param {Object} video - Video-Objekt
   * @returns {Object} Video mit lokalisierten Texten
   */
  const localizeVideo = (video) => {
    if (!video) return null;
    const { title, description } = getVideoText(video);
    return {
      ...video,
      title,
      description,
    };
  };

  /**
   * Lokalisiert ein ganzes Video-Array
   * @param {Array} videos - Array von Video-Objekten
   * @returns {Array} Videos mit lokalisierten Texten
   */
  const localizeVideos = (videos) => {
    if (!videos || !Array.isArray(videos)) return [];
    return videos.map(localizeVideo);
  };

  return {
    getVideoText,
    localizeVideo,
    localizeVideos,
    currentLanguage: i18n.language,
  };
}

/**
 * HOC zum Lokalisieren einer Video-Liste
 * @param {Array} videos - Video-Array
 * @returns {Array} Lokalisierte Videos (memoized)
 */
export function useLocalizedVideos(videos) {
  const { localizeVideos, currentLanguage } = useVideoI18n();

  return useMemo(() => {
    return localizeVideos(videos);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videos, currentLanguage]);
}

export default useVideoI18n;
