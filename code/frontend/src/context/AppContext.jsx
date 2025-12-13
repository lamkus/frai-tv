import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { storage } from '../lib/utils';
import { enrichVideoMetadata } from '../data/youtubeService';
import { CHANNEL_CONFIG } from '../data/remaikeData';
import { mockVideos, mockCategories, mockContinueWatching, mockWatchlist } from '../data/mockData';

/**
 * App Context - Global state management for remAIke.TV
 * Handles: videos, search, player state, UI preferences
 * Static Mode: Lädt Daten direkt aus gebündelten JS-Dateien - kein Backend nötig!
 */

const AppContext = createContext(null);

// Storage keys
const STORAGE_KEYS = {
  CONTINUE_WATCHING: 'remaike_continue_watching',
  WATCHLIST: 'remaike_watchlist',
  PREFERENCES: 'remaike_preferences',
  THEME: 'remaike_theme',
  VOLUME: 'remaike_volume',
  LANGUAGE: 'remaike_language',
};

export function AppProvider({ children }) {
  // ─────────────────────────────────────────────────────────────────────────
  // Video State
  // ─────────────────────────────────────────────────────────────────────────
  const [videos, setVideos] = useState([]);
  const [categories, setCategories] = useState([]);
  const [featuredVideo, setFeaturedVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ─────────────────────────────────────────────────────────────────────────
  // Search State
  // ─────────────────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // ─────────────────────────────────────────────────────────────────────────
  // Player State
  // ─────────────────────────────────────────────────────────────────────────
  const [currentVideo, setCurrentVideo] = useState(null);
  const [isPlayerOpen, setIsPlayerOpen] = useState(false);
  const [isMiniPlayerOpen, setIsMiniPlayerOpen] = useState(false);
  const [volume, setVolume] = useState(() => storage.get(STORAGE_KEYS.VOLUME, 80));

  // ─────────────────────────────────────────────────────────────────────────
  // Video Info Modal State
  // ─────────────────────────────────────────────────────────────────────────
  const [infoVideo, setInfoVideo] = useState(null);
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);

  // ─────────────────────────────────────────────────────────────────────────
  // Continue Watching
  // ─────────────────────────────────────────────────────────────────────────
  const [continueWatching, setContinueWatching] = useState(() =>
    storage.get(STORAGE_KEYS.CONTINUE_WATCHING, mockContinueWatching)
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Watchlist
  // ─────────────────────────────────────────────────────────────────────────
  const [watchlist, setWatchlist] = useState(() =>
    storage.get(STORAGE_KEYS.WATCHLIST, mockWatchlist)
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Preferences
  // ─────────────────────────────────────────────────────────────────────────
  const [preferences, setPreferences] = useState(() =>
    storage.get(STORAGE_KEYS.PREFERENCES, {
      darkMode: true,
      autoplay: true,
      defaultQuality: 'auto',
      saveHistory: true,
      compactMode: false,
      accentColor: 'amber',
      premiumUI: true,
    })
  );

  // ─────────────────────────────────────────────────────────────────────────
  // UI State
  // ─────────────────────────────────────────────────────────────────────────
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(() => storage.get(STORAGE_KEYS.THEME, 'dark'));
  const [language, setLanguage] = useState(() => storage.get(STORAGE_KEYS.LANGUAGE, 'de'));
  // Authentication (optional)
  const [user, setUser] = useState(() => storage.get('remaike_user', null));

  // ─────────────────────────────────────────────────────────────────────────
  // Data Fetching
  // ─────────────────────────────────────────────────────────────────────────
  const fetchVideos = useCallback(async () => {
    setLoading(true);
    setError(null);

    // Static Mode: Nutze lokale Daten direkt - kein Backend nötig!
    try {
      // Lade direkt aus remaikeData.js (bundled) + mockData fallback
      const { remaikeVideos, CATEGORIES } = await import('../data/remaikeData');

      // Kombiniere echte remAIke Videos mit Thumbnails
      const enrichedVideos = remaikeVideos.map((video) => ({
        ...video,
        thumbnailUrl: `https://img.youtube.com/vi/${video.ytId}/maxresdefault.jpg`,
        channelName: CHANNEL_CONFIG.channelName,
        channelId: CHANNEL_CONFIG.channelId,
        publishDate: video.publishDate || `${video.year}-01-01T00:00:00Z`,
        viewCount: video.viewCount || Math.floor(Math.random() * 100000) + 1000,
        likeCount: video.likeCount || Math.floor(Math.random() * 5000) + 100,
      }));

      setVideos(enrichedVideos);

      // Set featured video (neuestes oder zufällig)
      if (enrichedVideos.length > 0) {
        const featured =
          enrichedVideos.find((v) => v.category === 'christmas') || enrichedVideos[0];
        setFeaturedVideo(featured);
      }

      // Gruppiere nach Kategorien aus CATEGORIES
      const categoryMap = {};
      enrichedVideos.forEach((video) => {
        const catId = video.category || 'classic-films';
        const catInfo = CATEGORIES.find((c) => c.id === catId) || {
          id: catId,
          label: catId,
          icon: '🎬',
        };
        if (!categoryMap[catId]) {
          categoryMap[catId] = {
            name: catInfo.label,
            icon: catInfo.icon,
            videos: [],
          };
        }
        categoryMap[catId].videos.push(video);
      });
      setCategories(Object.values(categoryMap));

      console.log(`✅ Loaded ${enrichedVideos.length} videos from static data`);
    } catch (err) {
      console.error('Static data failed:', err.message);
      // Fallback auf mockVideos
      const fallback = mockVideos.map(enrichVideoMetadata);
      setVideos(fallback);
      setFeaturedVideo(fallback.length > 0 ? fallback[0] : null);
      setCategories(mockCategories);
      setError('Lokale Inhalte werden angezeigt.');
    } finally {
      setLoading(false);
    }
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Authentication helpers (Static Mode - local storage only)
  // ─────────────────────────────────────────────────────────────────────────
  async function signInWithIdToken(_idToken) {
    try {
      // Static Mode: Speichere User lokal (kein Server-Verify)
      storage.set('remaike_user', { email: 'guest@remaike.tv', name: 'Guest' });
      setUser({ email: 'guest@remaike.tv', name: 'Guest' });
      return { email: 'guest@remaike.tv', name: 'Guest' };
    } catch (e) {
      return null;
    }
  }

  function signOut() {
    storage.remove('remaike_user');
    setUser(null);
  }

  function promptGoogleSignIn() {
    try {
      if (window.google?.accounts?.id) {
        window.google.accounts.id.prompt();
      }
    } catch (e) {
      // ignore
    }
  }

  const fetchCategories = useCallback(async () => {
    // Backend API disabled for static/serverless deployment
    // try {
    //   const response = await fetch('/api/categories');
    //   if (response.ok) {
    //     await response.json();
    //   }
    // } catch (err) {
    //   console.warn('Categories API not available:', err);
    // }
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Search (Static Mode - local only)
  // ─────────────────────────────────────────────────────────────────────────
  const search = useCallback(
    async (query) => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        // Static Mode: Nur lokale Suche
        const lowerQuery = query.toLowerCase();
        const results = videos.filter(
          (v) =>
            v.title?.toLowerCase().includes(lowerQuery) ||
            v.description?.toLowerCase().includes(lowerQuery) ||
            v.category?.toLowerCase().includes(lowerQuery) ||
            v.tags?.some((t) => t.toLowerCase().includes(lowerQuery))
        );
        setSearchResults(results);
      } finally {
        setIsSearching(false);
      }
    },
    [videos]
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Player Actions
  // ─────────────────────────────────────────────────────────────────────────
  const openPlayer = useCallback((video) => {
    setCurrentVideo(video);
    setIsPlayerOpen(true);
    setIsMiniPlayerOpen(false);
    document.body.style.overflow = 'hidden';
  }, []);

  const closePlayer = useCallback(() => {
    setIsPlayerOpen(false);
    setIsMiniPlayerOpen(false);
    document.body.style.overflow = '';
    // Don't clear currentVideo immediately for transition
    setTimeout(() => setCurrentVideo(null), 300);
  }, []);

  const minimizePlayer = useCallback(() => {
    setIsPlayerOpen(false);
    setIsMiniPlayerOpen(true);
    document.body.style.overflow = '';
  }, []);

  const restorePlayer = useCallback(() => {
    setIsPlayerOpen(true);
    setIsMiniPlayerOpen(false);
    document.body.style.overflow = 'hidden';
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Video Info Modal Actions
  // ─────────────────────────────────────────────────────────────────────────
  const openInfoModal = useCallback((video) => {
    setInfoVideo(video);
    setIsInfoModalOpen(true);
    document.body.style.overflow = 'hidden';
  }, []);

  const closeInfoModal = useCallback(() => {
    setIsInfoModalOpen(false);
    document.body.style.overflow = '';
    setTimeout(() => setInfoVideo(null), 300);
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Continue Watching Management
  // ─────────────────────────────────────────────────────────────────────────
  const updateWatchProgress = useCallback(
    (videoId, progress, duration) => {
      setContinueWatching((prev) => {
        const existing = prev.find((w) => w.videoId === videoId);
        const video = videos.find((v) => v.id === videoId || v.ytId === videoId);

        const watchItem = {
          videoId,
          progress,
          duration,
          percentage: (progress / duration) * 100,
          timestamp: Date.now(),
          title: video?.title,
          thumbnail: video?.thumbnailUrl,
        };

        let updated;
        if (existing) {
          updated = prev.map((w) => (w.videoId === videoId ? watchItem : w));
        } else {
          updated = [watchItem, ...prev].slice(0, 20); // Keep last 20
        }

        // Remove if completed (>95%)
        if (watchItem.percentage > 95) {
          updated = updated.filter((w) => w.videoId !== videoId);
        }

        storage.set(STORAGE_KEYS.CONTINUE_WATCHING, updated);
        // Try to persist progress server-side (non-blocking)
        (async () => {
          try {
            const payload = {
              userId: user?.sub || user?.id || user?.email || null,
              ytId: videoId,
              progress,
              duration,
            };
            await fetch('/api/watch-progress', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload),
            });
          } catch (e) {
            // non-blocking — ignore errors
          }
        })();
        return updated;
      });
    },
    [videos]
  );

  const removeFromContinueWatching = useCallback((videoId) => {
    setContinueWatching((prev) => {
      const updated = prev.filter((w) => w.videoId !== videoId);
      storage.set(STORAGE_KEYS.CONTINUE_WATCHING, updated);
      return updated;
    });
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Volume Management
  // ─────────────────────────────────────────────────────────────────────────
  const updateVolume = useCallback((newVolume) => {
    setVolume(newVolume);
    storage.set(STORAGE_KEYS.VOLUME, newVolume);
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Language Management (simple flag-based selector)
  // ─────────────────────────────────────────────────────────────────────────
  const changeLanguage = useCallback((newLanguage) => {
    setLanguage(newLanguage);
    storage.set(STORAGE_KEYS.LANGUAGE, newLanguage);
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Initial Load
  // ─────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    fetchVideos();
    fetchCategories();
  }, [fetchVideos, fetchCategories]);

  // Toggle premium UI body class and trigger demo popups in non-production
  useEffect(() => {
    try {
      document.body.classList.toggle('premium-ui', !!preferences?.premiumUI);
    } catch (e) {
      // ignore (server-side rendering / tests)
    }

    if (preferences?.premiumUI && import.meta.env.MODE !== 'production') {
      // Softly trigger global demo popups so QA can see the style
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('remake:showInfoPopup'));
        window.dispatchEvent(new CustomEvent('remake:showQuickNotice'));
        window.dispatchEvent(new CustomEvent('remake:showInstallPrompt'));
      }, 900);
    }
  }, [preferences?.premiumUI]);

  // Initialize Google Identity Services (client-side) if configured
  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId || typeof window === 'undefined') return;

    // Load client if available
    try {
      // global `google` is available from the script tag in index.html
      // initialize only once
      if (window.google?.accounts?.id && !window.__remaike_gsi_init) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: async (res) => {
            // res.credential is the id_token
            if (res?.credential) {
              await signInWithIdToken(res.credential);
            }
          },
        });
        window.__remaike_gsi_init = true;
      }
    } catch (e) {
      // noop if GIS not available
    }
  }, []);

  // Sync continue-watching from backend when user signs in
  useEffect(() => {
    if (!user) return;
    (async () => {
      try {
        const resp = await fetch(
          `/api/watch-progress?userId=${encodeURIComponent(
            user?.sub || user?.id || user?.email || ''
          )}`
        );
        if (resp.ok) {
          const json = await resp.json();
          const serverItems = json.data || [];
          if (serverItems && serverItems.length > 0) {
            // Merge server items into continueWatching (server is authoritative)
            setContinueWatching((prev) => {
              // Map server items to watchItem shape used by app
              const mapped = serverItems.map((s) => ({
                videoId: s.ytId,
                progress: s.progress,
                duration: s.duration,
                percentage: s.percentage || (s.duration ? (s.progress / s.duration) * 100 : 0),
                timestamp: Date.now(),
                title: null,
                thumbnail: null,
              }));
              // Keep local items not present on server
              const keep = prev.filter((p) => !mapped.some((m) => m.videoId === p.videoId));
              const combined = [...mapped, ...keep].slice(0, 20);
              storage.set(STORAGE_KEYS.CONTINUE_WATCHING, combined);
              return combined;
            });
          }
        }
      } catch (e) {
        // ignore
      }
    })();
  }, [user]);

  // ─────────────────────────────────────────────────────────────────────────
  // Context Value
  // ─────────────────────────────────────────────────────────────────────────
  const value = {
    // Data
    videos,
    categories,
    featuredVideo,
    loading,
    error,

    // Search
    searchQuery,
    setSearchQuery,
    searchResults,
    isSearching,
    search,

    // Player
    currentVideo,
    isPlayerOpen,
    isMiniPlayerOpen,
    volume,
    openPlayer,
    closePlayer,
    minimizePlayer,
    restorePlayer,
    updateVolume,

    // Continue Watching
    continueWatching,
    updateWatchProgress,
    removeFromContinueWatching,

    // Watchlist
    watchlist,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,

    // Preferences
    preferences,
    updatePreferences,

    // History
    clearHistory,

    // UI
    isSidebarOpen,
    setIsSidebarOpen,
    theme,
    setTheme,
    language,
    setLanguage: changeLanguage,

    // Info Modal
    infoVideo,
    isInfoModalOpen,
    openInfoModal,
    closeInfoModal,

    // Actions
    refetchVideos: fetchVideos,
    // Auth
    user,
    signInWithIdToken,
    signOut,
    promptGoogleSignIn,
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Watchlist Management
  // ─────────────────────────────────────────────────────────────────────────
  function addToWatchlist(videoId) {
    setWatchlist((prev) => {
      if (prev.some((w) => w.id === videoId)) return prev;
      const updated = [{ id: videoId, addedAt: new Date().toISOString() }, ...prev];
      storage.set(STORAGE_KEYS.WATCHLIST, updated);
      return updated;
    });
  }

  function removeFromWatchlist(videoId) {
    setWatchlist((prev) => {
      const updated = prev.filter((w) => w.id !== videoId);
      storage.set(STORAGE_KEYS.WATCHLIST, updated);
      return updated;
    });
  }

  function isInWatchlist(videoId) {
    return watchlist.some((w) => w.id === videoId);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Preferences Management
  // ─────────────────────────────────────────────────────────────────────────
  function updatePreferences(newPrefs) {
    setPreferences((prev) => {
      const updated = { ...prev, ...newPrefs };
      storage.set(STORAGE_KEYS.PREFERENCES, updated);
      return updated;
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // History Management
  // ─────────────────────────────────────────────────────────────────────────
  function clearHistory() {
    setContinueWatching([]);
    storage.set(STORAGE_KEYS.CONTINUE_WATCHING, []);
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

export default AppContext;
