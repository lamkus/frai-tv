import { memo, useState, useRef, useCallback } from 'react';
import { Play, Plus, Info, Check, Volume2, VolumeX } from 'lucide-react';
import { cn, formatDuration, getYouTubeThumbnail, getYouTubeEmbedUrl } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { CATEGORIES } from '../../data/remaikeData';
import { useVideoI18n } from '../../lib/useVideoI18n';

/**
 * VideoCard Component - Responsive video thumbnail card with LIVE PREVIEW
 *
 * Features:
 * - Live thumbnail preview on hover (actual video plays muted)
 * - Animated thumbnail strip on hover (YouTube-style)
 * - Smooth zoom transitions
 * - Progress tracking overlay
 * - Info button opens VideoInfoModal
 *
 * Variants:
 * - default: Standard card for grids
 * - featured: Larger card for hero sections
 * - compact: Smaller card for continue watching
 * - poster: Portrait orientation (2:3 aspect ratio)
 */
function VideoCard({
  video,
  variant = 'default',
  showProgress = false,
  progress = 0,
  className,
  onPlay,
  onInfo,
  enableLivePreview = false, // DISABLED - causes double player bug and excessive API usage
}) {
  const {
    openPlayer,
    continueWatching,
    openInfoModal,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
  } = useApp();

  // Live preview state
  const [isHovering, setIsHovering] = useState(false);
  const [showLivePreview, setShowLivePreview] = useState(false);
  const [previewMuted, setPreviewMuted] = useState(true);
  const hoverTimeoutRef = useRef(null);

  // i18n für mehrsprachige Titel/Beschreibungen
  const { getVideoText } = useVideoI18n();

  // Handle hover for live preview - must be before early return
  const handleMouseEnter = useCallback(() => {
    if (!video) return;
    setIsHovering(true);

    // Show live video preview after 1.5s hover (like Netflix)
    if (enableLivePreview && video.ytId) {
      hoverTimeoutRef.current = setTimeout(() => {
        setShowLivePreview(true);
      }, 1500);
    }
  }, [enableLivePreview, video]);

  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
    setShowLivePreview(false);

    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
  }, []);

  if (!video) return null;

  const { id, ytId, duration, category, thumbnailUrl } = video;
  // Lokalisierte Texte
  const { title, description } = getVideoText(video);

  // Get multiple thumbnail qualities for animated preview
  // Use maxres as default if available, fallback to hq
  const mainThumbnail = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');

  // Fallback image if thumbnail fails to load
  const handleImageError = (e) => {
    e.target.src = getYouTubeThumbnail(ytId, 'hq'); // Try lower quality if maxres fails
    e.target.onerror = null; // Prevent infinite loop
  };

  // Check if in watchlist
  const inWatchlist = isInWatchlist(id || ytId);

  // Check continue watching progress
  const watchProgress = continueWatching.find((w) => w.videoId === id || w.videoId === ytId);
  const progressPercent = watchProgress?.percentage || progress;

  // Get category color
  const categoryData = CATEGORIES.find((c) => c.label === category || c.id === category);
  const categoryColor = categoryData?.hex;

  const handlePlay = (e) => {
    e.stopPropagation();
    if (onPlay) {
      onPlay(video);
    } else {
      openPlayer(video);
    }
  };

  const handleInfo = (e) => {
    e.stopPropagation();
    if (onInfo) {
      onInfo(video);
    } else {
      // Default: open the global VideoInfoModal
      openInfoModal(video);
    }
  };

  const togglePreviewMute = (e) => {
    e.stopPropagation();
    setPreviewMuted(!previewMuted);
  };

  // Size classes based on variant - optimiert für alle Geräte
  const sizeClasses = {
    default: 'w-32 xs:w-36 sm:w-44 md:w-48 lg:w-52 xl:w-56 3xl:w-64 4k:w-72',
    featured: 'w-40 xs:w-48 sm:w-56 md:w-64 lg:w-72 xl:w-80 3xl:w-96 4k:w-112',
    compact: 'w-28 xs:w-32 sm:w-36 md:w-40 lg:w-44 3xl:w-52',
    poster: 'w-24 xs:w-28 sm:w-32 md:w-36 lg:w-40 xl:w-44 3xl:w-52 4k:w-60',
    responsive: 'w-full', // Full width in grid
  };

  const aspectClasses = {
    default: 'aspect-video',
    featured: 'aspect-video',
    compact: 'aspect-video',
    poster: 'aspect-poster',
  };

  // Generate live preview embed URL
  const previewEmbedUrl = ytId
    ? getYouTubeEmbedUrl(ytId, {
        autoplay: true,
        params: {
          mute: previewMuted ? '1' : '0',
          controls: '0',
          start: Math.floor(Math.random() * 30), // Start at random point for variety
        },
      })
    : '';

  return (
    <article
      onClick={handlePlay}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handlePlay(e);
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`${title} abspielen${duration ? ` - ${formatDuration(duration)}` : ''}`}
      className={cn(
        'video-card group flex-shrink-0 snap-start cursor-pointer',
        'transform transition-all duration-300',
        'focus:outline-none focus:ring-2 focus:ring-accent-gold focus:ring-offset-2 focus:ring-offset-retro-black',
        isHovering && 'scale-105 z-20',
        sizeClasses[variant],
        className
      )}
    >
      {/* Thumbnail Container */}
      <div
        className={cn(
          'relative overflow-hidden rounded-lg shadow-lg bg-retro-gray',
          isHovering && 'shadow-2xl shadow-accent-red/20',
          aspectClasses[variant]
        )}
      >
        {/* Category Corner Effect */}
        {categoryColor && (
          <div
            className="absolute top-0 right-0 w-0 h-0 border-t-[32px] border-l-[32px] border-l-transparent z-20 pointer-events-none opacity-90 shadow-sm"
            style={{ borderTopColor: categoryColor }}
          />
        )}

        {/* Main Thumbnail */}
        <img
          src={mainThumbnail}
          alt={title}
          onError={handleImageError}
          loading="lazy"
          className={cn(
            'w-full h-full object-cover transition-transform duration-500',
            isHovering && !showLivePreview && 'scale-110'
          )}
        />

        {/* Live Video Preview (Netflix-style) */}
        {showLivePreview && previewEmbedUrl && (
          <div className="absolute inset-0 z-10 rounded-lg overflow-hidden border border-accent-gold/20 shadow-xl">
            <iframe
              src={previewEmbedUrl}
              title={`Preview: ${title}`}
              className="w-full h-full"
              allow="autoplay; encrypted-media"
              loading="lazy"
              frameBorder="0"
            />
            {/* Mute toggle for preview */}
            <button
              onClick={togglePreviewMute}
              className="absolute bottom-2 left-2 p-1.5 rounded-full bg-accent-gold/90 hover:bg-accent-gold text-black transition-colors z-20 ring-1 ring-accent-gold/20"
              aria-label={previewMuted ? 'Ton einschalten' : 'Ton ausschalten'}
            >
              {previewMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
            </button>
          </div>
        )}

        {/* Gradient Overlay */}
        <div
          className={cn('video-card-overlay transition-opacity', showLivePreview && 'opacity-30')}
        />

        {/* Duration Badge */}
        {duration && (
          <span className="absolute bottom-2 right-2 badge badge-duration text-[10px] sm:text-xs">
            {formatDuration(duration)}
          </span>
        )}

        {/* Category Badge */}
        {category && variant !== 'compact' && (
          <span className="absolute top-2 left-2 badge badge-year text-[10px] sm:text-xs opacity-0 group-hover:opacity-100 transition-opacity">
            {category}
          </span>
        )}

        {/* Play Button Overlay - hidden during live preview */}
        {!showLivePreview && (
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <button
              onClick={handlePlay}
              className="w-12 h-12 sm:w-14 sm:h-14 3xl:w-16 3xl:h-16 
                       rounded-full bg-accent-gold hover:bg-accent-gold/90 
                       flex items-center justify-center
                       transform scale-75 group-hover:scale-100 transition-all duration-300
                       shadow-lg shadow-accent-gold/30 ring-1 ring-accent-gold/20"
              aria-label={`${title} abspielen`}
            >
              <Play
                className="w-5 h-5 sm:w-6 sm:h-6 3xl:w-7 3xl:h-7 text-black ml-1"
                fill="currentColor"
              />
            </button>
          </div>
        )}

        {/* "Now Playing" indicator during live preview */}
        {showLivePreview && (
          <div className="absolute top-2 right-2 z-20 flex items-center gap-1.5 px-2 py-1 bg-accent-red rounded text-white text-xs font-medium">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
            Preview
          </div>
        )}

        {/* Progress Bar (Continue Watching) */}
        {(showProgress || progressPercent > 0) && progressPercent < 95 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-retro-gray/50">
            <div
              className="h-full bg-accent-red transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>

      {/* Info Section */}
      <div className="video-card-info p-2 sm:p-3">
        {/* Quick Actions */}
        <div className="flex items-center gap-1 mb-2">
          <button
            onClick={handlePlay}
            className="btn btn-primary btn-icon !p-1.5 sm:!p-2 bg-accent-gold text-black border border-accent-gold/40 hover:bg-accent-amber shadow-accent-gold/20"
            aria-label="Abspielen"
          >
            <Play size={14} className="sm:w-4 sm:h-4" fill="currentColor" />
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              if (inWatchlist) removeFromWatchlist(id || ytId);
              else addToWatchlist(id || ytId);
            }}
            className="btn btn-secondary btn-icon !p-1.5 sm:!p-2"
            aria-label={inWatchlist ? 'Von Liste entfernen' : 'Zur Liste hinzufügen'}
          >
            {inWatchlist ? (
              <Check size={14} className="sm:w-4 sm:h-4" />
            ) : (
              <Plus size={14} className="sm:w-4 sm:h-4" />
            )}
          </button>

          {/* Info Button - always visible */}
          <button
            onClick={handleInfo}
            className="btn btn-secondary btn-icon !p-1.5 sm:!p-2 ml-auto"
            aria-label="Mehr Infos"
          >
            <Info size={14} className="sm:w-4 sm:h-4" />
          </button>
        </div>

        {/* Title */}
        <h3 className="text-fluid-sm font-display font-semibold line-clamp-1 text-white group-hover:text-accent-gold transition-colors">
          {title}
        </h3>

        {/* Description (only on larger variants) */}
        {variant === 'featured' && description && (
          <p className="text-fluid-xs text-retro-muted line-clamp-2 mt-1">{description}</p>
        )}
      </div>
    </article>
  );
}

// Memoize to prevent unnecessary re-renders in lists
export default memo(VideoCard);
