import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
  Play,
  Volume2,
  VolumeX,
  MessageCircle,
  Share2,
  ChevronUp,
  ChevronDown,
  ThumbsUp,
  Repeat,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn, getYouTubeEmbedUrl } from '../lib/utils';
import useMeta from '../lib/useMeta';
import { fetchYouTubeShorts } from '../data/youtubeService';
import { CHANNEL_CONFIG, remaikeVideos } from '../data/remaikeData';
import ShareModal from '../components/ui/ShareModal';
import { useVideoI18n } from '../lib/useVideoI18n';

/**
 * ShortsPage - YouTube Shorts-style Vertical Video Feed
 *
 * Loads curated Shorts from remaikeData.js with YouTube API stats
 */

// Kuratierte Shorts aus remaikeData.js
const curatedShortsRaw = remaikeVideos.filter((v) => v.isShort === true);

export default function ShortsPage() {
  const { t } = useTranslation();

  useMeta({
    title: 'Shorts - remAIke.TV',
    description: t('curatedShorts'),
  });

  // i18n für mehrsprachige Titel/Beschreibungen
  const { localizeVideos } = useVideoI18n();
  const curatedShorts = useMemo(() => localizeVideos(curatedShortsRaw), [localizeVideos]);

  const [apiStats, setApiStats] = useState({});
  const [loading, setLoading] = useState(true);

  // Load API stats for curated shorts
  useEffect(() => {
    async function loadStats() {
      setLoading(true);
      try {
        // Fetch stats from YouTube API
        const apiShorts = await fetchYouTubeShorts(CHANNEL_CONFIG.channelId, 30);
        // Create map of ytId -> stats
        const statsMap = {};
        apiShorts.forEach((s) => {
          statsMap[s.ytId] = {
            viewCount: s.viewCount || 0,
            likeCount: s.likeCount || 0,
            commentCount: s.commentCount || 0,
          };
        });
        setApiStats(statsMap);
      } catch (err) {
        console.error('Failed to load stats:', err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  // Merge curated data with API stats
  const shortsVideos = useMemo(() => {
    return curatedShorts.map((short) => ({
      ...short,
      viewCount: apiStats[short.ytId]?.viewCount || 0,
      likeCount: apiStats[short.ytId]?.likeCount || 0,
      commentCount: apiStats[short.ytId]?.commentCount || 0,
      thumbnailUrl: `https://img.youtube.com/vi/${short.ytId}/maxresdefault.jpg`,
    }));
  }, [apiStats, curatedShorts]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [userConsent, setUserConsent] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [liked, setLiked] = useState({});

  // Swipe state
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState(0);
  const startY = useRef(0);
  const containerRef = useRef(null);

  const currentShort = shortsVideos[currentIndex];
  const totalShorts = shortsVideos.length;

  // Navigate to next/previous short
  const goToShort = useCallback(
    (index) => {
      if (index >= 0 && index < totalShorts) {
        setCurrentIndex(index);
        setIsPlaying(true);
      }
    },
    [totalShorts]
  );

  const goNext = useCallback(() => {
    if (currentIndex < totalShorts - 1) {
      goToShort(currentIndex + 1);
    }
  }, [currentIndex, totalShorts, goToShort]);

  const goPrev = useCallback(() => {
    if (currentIndex > 0) {
      goToShort(currentIndex - 1);
    }
  }, [currentIndex, goToShort]);

  // Touch/Mouse handlers for swipe
  const handleTouchStart = (e) => {
    const touch = e.touches ? e.touches[0] : e;
    startY.current = touch.clientY;
    setIsDragging(true);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const touch = e.touches ? e.touches[0] : e;
    const deltaY = touch.clientY - startY.current;
    setDragOffset(deltaY);
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    const threshold = window.innerHeight * 0.2;
    if (dragOffset < -threshold) {
      goNext();
    } else if (dragOffset > threshold) {
      goPrev();
    }
    setIsDragging(false);
    setDragOffset(0);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowDown' || e.key === 'j') {
        e.preventDefault();
        goNext();
      } else if (e.key === 'ArrowUp' || e.key === 'k') {
        e.preventDefault();
        goPrev();
      } else if (e.key === ' ') {
        e.preventDefault();
        setIsPlaying((p) => !p);
      } else if (e.key === 'm') {
        setIsMuted((m) => !m);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goNext, goPrev]);

  const handleConsent = () => {
    setUserConsent(true);
    setIsPlaying(true);
    setIsMuted(false);
  };

  const toggleLike = (shortId) => {
    setLiked((prev) => ({ ...prev, [shortId]: !prev[shortId] }));
  };

  const formatCount = (num) => {
    const n = num || 0;
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return n.toString();
  };

  // No shorts available
  if (loading) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
        <div className="text-center p-8">
          <Loader2 className="w-16 h-16 text-accent-amber mx-auto mb-4 animate-spin" />
          <h1 className="text-xl font-bold text-white">{t('loading')}</h1>
        </div>
      </div>
    );
  }

  if (shortsVideos.length === 0) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
        <div className="text-center p-8 max-w-md">
          <AlertCircle className="w-16 h-16 text-accent-amber mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">{t('noResults')}</h1>
          <p className="text-retro-muted mb-6">{t('noShortsAvailable')}</p>
          <a
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent-amber text-black rounded-lg font-medium hover:bg-amber-400 transition-colors"
          >
            {t('library')}
          </a>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 bg-black z-50 overflow-hidden select-none"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      onMouseDown={handleTouchStart}
      onMouseMove={isDragging ? handleTouchMove : undefined}
      onMouseUp={handleTouchEnd}
      onMouseLeave={handleTouchEnd}
    >
      {/* Video Container */}
      <div
        className={cn(
          'absolute inset-0 flex flex-col',
          !isDragging && 'transition-transform duration-300 ease-out'
        )}
        style={{
          transform: `translateY(${
            -currentIndex * 100 + (dragOffset / window.innerHeight) * 100
          }%)`,
          height: `${totalShorts * 100}%`,
        }}
      >
        {shortsVideos.map((short, index) => (
          <div
            key={short.id}
            className="relative w-full flex-shrink-0"
            style={{ height: `${100 / totalShorts}%` }}
          >
            {/* Video Player */}
            {userConsent ? (
              <iframe
                src={getYouTubeEmbedUrl(short.ytId, {
                  autoplay: index === currentIndex && isPlaying,
                  params: {
                    mute: isMuted ? '1' : '0',
                    loop: '1',
                    playlist: short.ytId,
                    controls: '0',
                    showinfo: '0',
                    rel: '0',
                    playsinline: '1',
                  },
                })}
                title={short.title}
                className="absolute inset-0 w-full h-full object-cover"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                style={{ pointerEvents: 'none' }}
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <img
                  src={`https://i.ytimg.com/vi/${short.ytId}/maxresdefault.jpg`}
                  alt=""
                  className="absolute inset-0 w-full h-full object-cover"
                  onError={(e) => {
                    e.target.src = `https://i.ytimg.com/vi/${short.ytId}/hqdefault.jpg`;
                  }}
                />
                <div className="absolute inset-0 bg-black/50" />
                <button
                  onClick={handleConsent}
                  className="relative z-10 flex flex-col items-center gap-4 p-8"
                >
                  <div className="w-24 h-24 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:scale-110 transition-transform">
                    <Play size={48} className="text-white ml-2" fill="white" />
                  </div>
                  <p className="text-white font-semibold">{t('tapToStart')}</p>
                  <p className="text-white/70 text-sm flex items-center gap-1">
                    <Volume2 size={14} />
                    {t('playWithSound')}
                  </p>
                </button>
              </div>
            )}

            {/* Gradient overlays */}
            <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />
            <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/80 to-transparent pointer-events-none" />

            {/* Right side actions */}
            <div className="absolute right-4 bottom-32 flex flex-col items-center gap-6">
              <button
                onClick={() => toggleLike(short.id)}
                className="flex flex-col items-center gap-1"
              >
                <div
                  className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center transition-colors',
                    liked[short.id]
                      ? 'bg-red-500 text-white'
                      : 'bg-white/10 backdrop-blur-sm text-white hover:bg-white/20'
                  )}
                >
                  <ThumbsUp size={24} fill={liked[short.id] ? 'currentColor' : 'none'} />
                </div>
                <span className="text-white text-xs font-medium">
                  {formatCount((short.likeCount || 0) + (liked[short.id] ? 1 : 0))}
                </span>
              </button>

              <button className="flex flex-col items-center gap-1">
                <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/20 transition-colors">
                  <MessageCircle size={24} />
                </div>
                <span className="text-white text-xs font-medium">
                  {formatCount(short.commentCount)}
                </span>
              </button>

              <button
                onClick={() => setShowShareModal(true)}
                className="flex flex-col items-center gap-1"
              >
                <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/20 transition-colors">
                  <Share2 size={24} />
                </div>
                <span className="text-white text-xs font-medium">
                  {formatCount(short.viewCount)}
                </span>
              </button>

              <div className="flex flex-col items-center gap-1">
                <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center text-white">
                  <Repeat size={20} />
                </div>
              </div>

              <button className="relative">
                <img
                  src={short.channelAvatar}
                  alt={short.channel}
                  className="w-12 h-12 rounded-full border-2 border-white object-cover"
                />
                <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  +
                </div>
              </button>
            </div>

            {/* Bottom info */}
            <div className="absolute left-4 right-20 bottom-8">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-white font-semibold">@{short.channel.replace(' ', '')}</span>
              </div>
              <p className="text-white text-sm line-clamp-2 mb-2">{short.title}</p>
              <p className="text-white/70 text-xs line-clamp-1">{short.description || ''}</p>
            </div>

            {/* Mute button */}
            {userConsent && (
              <button
                onClick={() => setIsMuted((m) => !m)}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/20 transition-colors"
              >
                {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            )}

            {/* Progress indicator */}
            <div className="absolute top-4 left-16 flex gap-1">
              {shortsVideos.map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    'h-1 rounded-full transition-all',
                    i === currentIndex ? 'w-8 bg-white' : 'w-2 bg-white/40'
                  )}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Navigation hints */}
      {currentIndex > 0 && (
        <button
          onClick={goPrev}
          className="absolute top-1/4 left-1/2 -translate-x-1/2 text-white/50 hover:text-white transition-colors animate-bounce"
        >
          <ChevronUp size={32} />
        </button>
      )}
      {currentIndex < totalShorts - 1 && (
        <button
          onClick={goNext}
          className="absolute bottom-1/4 left-1/2 -translate-x-1/2 text-white/50 hover:text-white transition-colors animate-bounce"
        >
          <ChevronDown size={32} />
        </button>
      )}

      {/* Back button */}
      <a
        href="/"
        className="absolute top-4 left-4 z-20 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-white text-sm font-medium hover:bg-white/20 transition-colors"
      >
        ← Zurück
      </a>

      {/* Share Modal */}
      {showShareModal && currentShort && (
        <ShareModal
          video={{ ...currentShort, id: currentShort.ytId }}
          isOpen={showShareModal}
          onClose={() => setShowShareModal(false)}
        />
      )}

      {/* Keyboard hints */}
      <div className="hidden md:block absolute bottom-4 left-4 text-white/40 text-xs">
        <p>↑↓ Navigation • Space Play/Pause • M Mute</p>
      </div>
    </div>
  );
}
