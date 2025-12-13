import { useEffect, useCallback, useState, useRef } from 'react';
import { X, Minimize } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn, getYouTubeEmbedUrl, formatDuration, storage } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import {
  recordVideoStart,
  recordWatchTime,
  getNextVideo,
  shouldShowStillWatching,
  markStillWatchingShown,
} from '../../lib/recommendationEngine';
import UpNextOverlay from './UpNextOverlay';

// Simple analytics stub - no-op functions that won't crash
const noopAnalytics = {
  trackPlay: () => {},
  trackPause: () => {},
  trackSeek: () => {},
  trackComplete: () => {},
  trackEnd: () => {},
};

/**
 * VideoPlayer Component - Full-featured modal video player
 *
 * Features:
 * - YouTube embed with privacy mode
 * - Custom controls overlay
 * - Progress tracking (Continue Watching)
 * - Keyboard shortcuts
 * - Responsive sizing (mobile to 4K)
 */
export default function VideoPlayer() {
  const {
    currentVideo,
    isPlayerOpen,
    closePlayer,
    minimizePlayer,
    volume,
    updateVolume,
    videos,
    openPlayer,
    updateWatchProgress,
  } = useApp();

  // Simple analytics - always safe, never crashes
  const analytics = noopAnalytics;

  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [isVideoEnded, setIsVideoEnded] = useState(false);
  const [showStillWatching, setShowStillWatching] = useState(false);
  const [showOurRecommendations, setShowOurRecommendations] = useState(false);
  const [watchStartTime, setWatchStartTime] = useState(null);
  const playerId = useRef(`yt-player-${Math.random().toString(36).slice(2)}`);

  // YouTube/privacy consent - MUST be before any conditional returns!
  const [allowYouTube, setAllowYouTube] = useState(() =>
    storage.get('remaike_allow_youtube', false)
  );

  const containerRef = useRef(null);
  const controlsTimeoutRef = useRef(null);
  const iframeRef = useRef(null);

  // Translation
  const { t } = useTranslation();

  // Video stats state (must be before early returns)
  const [videoStats, setVideoStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  }, []);

  // Hide controls after inactivity
  const resetControlsTimeout = useCallback(() => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) setShowControls(false);
    }, 3000);
  }, [isPlaying]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!isPlayerOpen) return;

    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'Escape':
          closePlayer();
          break;
        case ' ':
        case 'k':
          e.preventDefault();
          setIsPlaying((prev) => {
            if (prev) {
              analytics?.trackPause?.();
            } else {
              analytics?.trackPlay?.();
            }
            return !prev;
          });
          break;
        case 'm':
          setIsMuted((prev) => !prev);
          break;
        case 'f':
          toggleFullscreen();
          break;
        case 'ArrowRight':
          // Skip forward 10s (would need YouTube API)
          break;
        case 'ArrowLeft':
          // Skip back 10s
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPlayerOpen, closePlayer, toggleFullscreen]);

  // Reset on video change + track session
  useEffect(() => {
    if (currentVideo) {
      setCurrentTime(0);
      setIsPlaying(true);
      setIsVideoEnded(false);
      setShowOurRecommendations(false);
      setWatchStartTime(Date.now());
      resetControlsTimeout();

      // Track video start for recommendation engine
      recordVideoStart(currentVideo);

      // Analytics: Track video start
      analytics?.trackPlay?.();

      // Check if we should show "still watching?" prompt
      if (shouldShowStillWatching()) {
        setShowStillWatching(true);
      }
    }
  }, [currentVideo, resetControlsTimeout, analytics]);

  // Fallback timer-based video end detection
  // YouTube postMessage is unreliable, so also check duration
  useEffect(() => {
    if (!currentVideo || !isPlaying || !watchStartTime || isVideoEnded) return;

    const duration = currentVideo.duration || currentVideo.durationSeconds || 0;
    if (!duration || duration < 60) return; // Skip if no duration or too short

    const elapsed = Math.floor((Date.now() - watchStartTime) / 1000);
    const remaining = duration - elapsed;

    // If less than 10 seconds remain, set a timer to trigger end
    if (remaining > 0 && remaining <= 60) {
      const timeout = setTimeout(() => {
        setIsVideoEnded(true);
        setIsPlaying(false);
        analytics?.trackComplete?.();
      }, remaining * 1000);

      return () => clearTimeout(timeout);
    }
  }, [currentVideo, isPlaying, watchStartTime, isVideoEnded, analytics]);

  // Track watch time when video ends or player closes
  useEffect(() => {
    return () => {
      if (watchStartTime && currentVideo) {
        const watchedSeconds = Math.floor((Date.now() - watchStartTime) / 1000);
        if (watchedSeconds > 5) {
          recordWatchTime(watchedSeconds);
          // Analytics: Track video end with watch duration
          analytics?.trackEnd?.();
          // Update continue-watching progress in AppContext if available
          try {
            const duration = currentVideo.duration || currentVideo.durationSeconds || 0;
            if (updateWatchProgress && duration > 0) {
              const progress = Math.min(watchedSeconds, duration);
              updateWatchProgress(currentVideo.id || currentVideo.ytId, progress, duration);
            }
          } catch (e) {
            // ignore update errors
          }
        }
      }
    };
  }, [watchStartTime, currentVideo, analytics]);

  // Periodically report progress while the video is playing (so Continue Watching updates)
  useEffect(() => {
    if (!currentVideo || !isPlaying || !watchStartTime) return;

    const interval = setInterval(() => {
      try {
        const watchedSeconds = Math.floor((Date.now() - watchStartTime) / 1000);
        const duration = currentVideo.duration || currentVideo.durationSeconds || 0;
        if (updateWatchProgress && duration > 0) {
          const progress = Math.min(watchedSeconds, duration);
          updateWatchProgress(currentVideo.id || currentVideo.ytId, progress, duration);
        }
      } catch (e) {
        // noop
      }
    }, 5000); // every 5s

    return () => clearInterval(interval);
  }, [currentVideo, isPlaying, watchStartTime, updateWatchProgress]);

  // Handle autoplay next video
  const handlePlayNext = useCallback(
    (nextVideo) => {
      setIsVideoEnded(false);
      openPlayer(nextVideo);
    },
    [openPlayer]
  );

  // Handle cancel autoplay
  const handleCancelAutoplay = useCallback(() => {
    setIsVideoEnded(false);
  }, []);

  // Trigger video end - shows the UpNextOverlay
  const simulateVideoEnd = useCallback(() => {
    setIsVideoEnded(true);
    setIsPlaying(false);
    analytics?.trackComplete?.();
  }, [analytics]);

  // Detect end from YouTube IFrame API postMessage (state 0)
  const handlePlayerMessage = useCallback(
    (event) => {
      if (!event?.data || typeof event.data !== 'string') return;
      try {
        const data = JSON.parse(event.data);
        if (data?.event === 'onStateChange' && data?.info === 0) {
          simulateVideoEnd();
        }
      } catch (err) {
        // ignore non-JSON messages
      }
    },
    [simulateVideoEnd]
  );

  useEffect(() => {
    window.addEventListener('message', handlePlayerMessage);
    return () => window.removeEventListener('message', handlePlayerMessage);
  }, [handlePlayerMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
    };
  }, []);

  // Fetch video stats when video changes
  useEffect(() => {
    let mounted = true;
    const ytId = currentVideo?.ytId;
    if (!ytId) {
      setVideoStats(null);
      return;
    }
    setStatsLoading(true);
    setVideoStats(null);
    fetch(`/api/video-stats/${ytId}`)
      .then((r) => r.json())
      .then((json) => {
        if (!mounted) return;
        if (json && json.data) setVideoStats(json.data);
      })
      .catch((err) => {
        console.warn('Failed to load video stats', err);
      })
      .finally(() => {
        if (mounted) setStatsLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [currentVideo?.ytId]);

  if (!isPlayerOpen || !currentVideo) return null;

  const { title, ytId, description, duration, category, year, tags } = currentVideo;

  const embedUrl = getYouTubeEmbedUrl(ytId, {
    autoplay: true,
    params: {
      mute: isMuted ? '1' : '0',
      vq: 'hd2160',
    },
  });

  // Stats already fetched by useEffect above early return

  // (guard already above) ensure we proceed to render

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/95 backdrop-blur-xl"
      onClick={(e) => {
        if (e.target === e.currentTarget) closePlayer();
      }}
    >
      <div
        ref={containerRef}
        className={cn(
          'relative w-[95vw] max-w-7xl bg-gradient-to-br from-retro-black/98 via-retro-darker/95 to-retro-black/98',
          'rounded-2xl shadow-2xl shadow-black/80 border border-accent-gold/20',
          'backdrop-blur-2xl overflow-hidden',
          isFullscreen && 'max-w-none w-screen h-screen rounded-none border-none'
        )}
        onMouseMove={resetControlsTimeout}
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 z-30 px-6 md:px-8 py-4 bg-gradient-to-b from-black/90 via-black/60 to-transparent border-b border-accent-gold/30 backdrop-blur-md flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-gold to-accent-amber flex items-center justify-center shadow-xl shadow-accent-gold/30 ring-2 ring-accent-gold/40">
              <span className="text-sm font-display font-bold text-retro-black tracking-tight">
                rem
              </span>
            </div>
            <div className="min-w-0">
              <h3 className="text-lg md:text-xl font-display font-bold line-clamp-1 text-white tracking-wide">
                {title}
              </h3>
              <div className="flex items-center gap-3 text-xs text-retro-muted/80 mt-1.5 font-medium">
                {category && (
                  <span className="px-2 py-0.5 bg-white/5 text-accent-gold rounded">
                    {category}
                  </span>
                )}
                {duration && <span>{formatDuration(duration)}</span>}
                {statsLoading ? (
                  <span className="text-sm text-retro-muted/60">Lade Stats…</span>
                ) : videoStats ? (
                  <span className="text-sm text-retro-muted/70">
                    {Intl.NumberFormat('de-DE').format(videoStats.viewCount)} Aufrufe
                  </span>
                ) : null}
                <span>4K • 8K capable</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigator.clipboard?.writeText(window.location.href)}
              className="px-4 py-2 rounded-lg bg-white/5 border border-accent-gold/20 text-xs font-semibold text-white hover:bg-accent-gold/10 hover:border-accent-gold/40 transition-all shadow-sm"
            >
              Teilen
            </button>
            <button
              onClick={minimizePlayer}
              className="p-2.5 rounded-lg bg-black/40 hover:bg-black/60 border border-white/10 hover:border-accent-gold/30 text-white transition-all"
              aria-label="Minimieren"
            >
              <Minimize size={20} />
            </button>
            <button
              onClick={closePlayer}
              className="p-2.5 rounded-lg bg-black/40 hover:bg-black/60 border border-white/10 hover:border-accent-gold/30 text-white transition-all"
              aria-label="Schließen"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Video Container */}
        <div className="video-player-container relative">
          {/* YouTube Embed */}
          {allowYouTube ? (
            <>
              <iframe
                ref={iframeRef}
                src={embedUrl}
                title={title}
                id={playerId.current}
                className="absolute inset-0 w-full h-full rounded-lg pointer-events-auto"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                frameBorder="0"
                style={{ pointerEvents: 'auto' }}
              />
              {/* Overlay über YouTube-Empfehlungsleiste (unten ~120px) - blockiert Klicks auf YT-Videos */}
              <div
                className="absolute bottom-0 left-0 right-0 h-[120px] z-20"
                style={{ pointerEvents: 'auto' }}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Zeige unsere eigene "Weitere Videos" Liste
                  setShowOurRecommendations(true);
                }}
              >
                {/* Transparenter Overlay - verhindert Klicks auf YouTube-Empfehlungen */}
              </div>
              {/* Vollständiger Overlay wenn Video endet */}
              {isVideoEnded && (
                <div
                  className="absolute inset-0 z-20"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                />
              )}
            </>
          ) : (
            <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-retro-dark/80 text-center px-6">
              <div>
                <p className="mb-4">
                  Dieses Video wird von YouTube geladen. Es verwendet externe Inhalte
                  (youtube-nocookie.com).
                </p>
                <div className="flex items-center justify-center gap-3">
                  <button onClick={() => setAllowYouTube(true)} className="btn btn-primary">
                    Video laden
                  </button>
                  <button
                    onClick={() => {
                      setAllowYouTube(true);
                      storage.set('remaike_allow_youtube', true);
                    }}
                    className="btn btn-secondary"
                  >
                    Immer erlauben
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Video Info (below player when not fullscreen) */}
        {!isFullscreen && (
          <div className="p-6 sm:p-8 md:p-10 bg-gradient-to-b from-retro-darker/80 to-retro-black border-t border-accent-gold/10">
            <div className="flex flex-wrap items-start gap-4">
              <div className="flex-1 min-w-0">
                <h2 className="text-xl md:text-2xl font-display font-bold mb-3 line-clamp-2 text-white">
                  {title}
                </h2>
                <div className="flex flex-wrap items-center gap-3 mb-3">
                  {category && (
                    <span className="px-3 py-1 bg-accent-gold/20 text-accent-gold text-xs font-bold rounded-full border border-accent-gold/30">
                      {category}
                    </span>
                  )}
                  {year && (
                    <span className="px-3 py-1 bg-white/5 text-white/70 text-xs font-medium rounded-full">
                      {year} • vor {new Date().getFullYear() - year} Jahren
                    </span>
                  )}
                  {duration && (
                    <span className="text-sm text-retro-muted/70 font-medium">
                      {formatDuration(duration)}
                    </span>
                  )}
                </div>
                {/* YouTube Original Link */}
                <a
                  href={`https://www.youtube.com/watch?v=${ytId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-xs text-red-500 hover:text-red-400 transition-colors mb-3"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                  </svg>
                  Auf YouTube ansehen
                </a>
              </div>
            </div>

            {description && (
              <p className="text-sm md:text-base text-retro-muted/80 mt-2 leading-relaxed">
                {description}
              </p>
            )}

            {/* Tags */}
            {tags && tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {tags.slice(0, 6).map((tag) => (
                  <span key={tag} className="px-2 py-0.5 bg-white/5 text-white/50 text-xs rounded">
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Up Next Overlay (Netflix-style autoplay) */}
        {allowYouTube && (
          <UpNextOverlay
            currentVideo={currentVideo}
            allVideos={videos}
            onPlayNext={handlePlayNext}
            onCancel={handleCancelAutoplay}
            isVideoEnded={isVideoEnded}
            countdownSeconds={8}
          />
        )}

        {/* Unsere eigene "Weitere Videos" Liste - ersetzt YouTube-Empfehlungen */}
        {showOurRecommendations && !isVideoEnded && (
          <div className="absolute bottom-0 left-0 right-0 z-30 bg-gradient-to-t from-black via-black/95 to-transparent p-4 animate-fade-in">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-white">Weitere Videos</h4>
              <button
                onClick={() => setShowOurRecommendations(false)}
                className="text-white/60 hover:text-white p-1"
              >
                <X size={18} />
              </button>
            </div>
            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {(() => {
                // 2 Slots für neueste Videos + 6 weitere
                const otherVideos = videos.filter((v) => v.ytId !== currentVideo?.ytId);
                const newestVideos = otherVideos.slice(0, 2); // Erste 2 = neueste
                const relatedVideos = otherVideos
                  .filter((v) => v.category === currentVideo?.category && !newestVideos.includes(v))
                  .slice(0, 6);
                const finalList = [...newestVideos, ...relatedVideos].slice(0, 8);

                return finalList.map((video, idx) => (
                  <button
                    key={video.ytId || video.id}
                    onClick={() => {
                      setShowOurRecommendations(false);
                      openPlayer(video);
                    }}
                    className="flex-shrink-0 group relative w-32 sm:w-40"
                  >
                    <div className="relative aspect-video rounded-lg overflow-hidden ring-1 ring-white/10 group-hover:ring-accent-gold/50 transition-all">
                      <img
                        src={`https://i.ytimg.com/vi/${video.ytId}/mqdefault.jpg`}
                        alt={video.title}
                        className="w-full h-full object-cover"
                      />
                      {/* NEU Badge für die ersten 2 */}
                      {idx < 2 && (
                        <span className="absolute top-1 left-1 px-1.5 py-0.5 bg-accent-gold text-black text-[9px] font-bold rounded">
                          NEU
                        </span>
                      )}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <div className="w-10 h-10 rounded-full bg-accent-gold/90 flex items-center justify-center">
                          <svg
                            className="w-4 h-4 text-black ml-0.5"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        </div>
                      </div>
                      {/* Jahr Badge */}
                      {video.year && (
                        <span className="absolute bottom-1 right-1 px-1.5 py-0.5 bg-black/80 text-white/80 text-[9px] rounded">
                          {video.year}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-xs text-white/80 line-clamp-2 text-left group-hover:text-white transition-colors">
                      {video.title}
                    </p>
                  </button>
                ));
              })()}
            </div>
          </div>
        )}

        {/* Still Watching Prompt (after 4+ hours) */}
        {showStillWatching && (
          <div className="absolute inset-0 bg-retro-black/95 flex items-center justify-center z-40">
            <div className="text-center max-w-md p-6">
              <div className="text-6xl mb-4">😴</div>
              <h3 className="text-2xl font-semibold mb-2">{t('stillWatching')}</h3>
              <p className="text-retro-muted mb-6">{t('stillWatchingDesc')}</p>
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={() => {
                    setShowStillWatching(false);
                    markStillWatchingShown();
                  }}
                  className="btn btn-primary"
                >
                  {t('continueWatching')}
                </button>
                <button
                  onClick={() => {
                    setShowStillWatching(false);
                    closePlayer();
                  }}
                  className="btn btn-secondary"
                >
                  {t('takePause')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Debug: Manual Video End Trigger (remove in production) */}
        {process.env.NODE_ENV === 'development' && allowYouTube && !isVideoEnded && (
          <button
            onClick={simulateVideoEnd}
            className="absolute bottom-4 left-4 z-50 btn btn-ghost text-xs opacity-30 hover:opacity-100"
          >
            [DEV] Simulate End
          </button>
        )}
      </div>
    </div>
  );
}
