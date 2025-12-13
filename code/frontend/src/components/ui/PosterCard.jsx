import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, Plus, Check, Sparkles, Eye, ThumbsUp } from 'lucide-react';
import { cn, getYouTubeThumbnail } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { CATEGORIES } from '../../data/remaikeData';
import { useVideoI18n } from '../../lib/useVideoI18n';

/**
 * Format view/like count (e.g., 1.2M, 456K)
 */
function formatCount(count) {
  if (!count) return null;
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${Math.round(count / 1000)}K`;
  }
  return count.toString();
}

/**
 * PosterCard - Netflix/frai.tv style poster card
 *
 * Features:
 * - Poster aspect ratio (2:3)
 * - AI badge
 * - Play button overlay
 * - Hover effects
 * - Add to list functionality
 */
export default function PosterCard({
  video,
  size = 'md',
  showAiBadge = true,
  showTitle = true,
  className,
}) {
  const { openPlayer, addToWatchlist, removeFromWatchlist, isInWatchlist } = useApp();
  const [imageError, setImageError] = useState(false);

  // i18n für mehrsprachige Titel
  const { getVideoText } = useVideoI18n();

  // Early return AFTER all hooks
  if (!video) return null;

  const { id, ytId, thumbnailUrl, category, year } = video;
  // Lokalisierter Titel
  const { title } = getVideoText(video);

  // Use poster-style thumbnail or fallback to maxres
  const posterUrl = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');
  const inWatchlist = isInWatchlist(id);

  // Get category color
  const categoryData = CATEGORIES.find((c) => c.label === category || c.id === category);
  const categoryColor = categoryData?.hex;

  const sizeClasses = {
    sm: 'w-24 xs:w-28 sm:w-32',
    md: 'w-28 xs:w-32 sm:w-36 md:w-40 lg:w-44',
    lg: 'w-36 xs:w-40 sm:w-44 md:w-48 lg:w-56',
    responsive: 'w-full', // Full width in grid, controlled by parent
  };

  const handlePlay = (e) => {
    e.preventDefault();
    e.stopPropagation();
    openPlayer(video);
  };

  const handleWatchlist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (inWatchlist) {
      removeFromWatchlist(id);
    } else {
      addToWatchlist(id);
    }
  };

  return (
    <div className={cn('poster-card group relative flex-shrink-0', sizeClasses[size], className)}>
      <Link to={`/video/${id}`} className="block">
        {/* Poster Image */}
        <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-retro-dark">
          {!imageError ? (
            <img
              src={posterUrl}
              alt={title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              onError={() => setImageError(true)}
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-retro-dark to-retro-darker">
              <span className="text-4xl">🎬</span>
            </div>
          )}

          {/* AI Badge */}
          {showAiBadge && (
            <div className="absolute top-2 left-2 z-10">
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-accent-amber text-black">
                <Sparkles size={10} />
                AI
              </span>
            </div>
          )}

          {/* Category Corner Effect */}
          {categoryColor && (
            <div
              className="absolute top-0 right-0 w-0 h-0 border-t-[32px] border-l-[32px] border-l-transparent z-20 pointer-events-none opacity-90 shadow-sm"
              style={{ borderTopColor: categoryColor }}
            />
          )}

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          {/* Play Button - Larger touch target on mobile */}
          <button
            onClick={handlePlay}
            className={cn(
              'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
              'w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/90 hover:bg-white active:scale-95',
              'flex items-center justify-center',
              'transform scale-0 group-hover:scale-100 transition-all duration-300',
              'shadow-lg hover:shadow-xl',
              'focus:outline-none focus:ring-2 focus:ring-accent-amber'
            )}
            tabIndex={0}
            aria-label={`${title} abspielen`}
          >
            <Play size={18} className="text-black ml-0.5 sm:ml-1" fill="black" />
          </button>

          {/* Watchlist Button - Better touch target */}
          <button
            onClick={handleWatchlist}
            className={cn(
              'absolute top-2 right-2',
              'w-8 h-8 sm:w-9 sm:h-9 rounded-full',
              'flex items-center justify-center',
              'transform scale-0 group-hover:scale-100 transition-all duration-300 delay-75',
              'focus:outline-none focus:ring-2 focus:ring-accent-amber',
              'active:scale-95',
              inWatchlist
                ? 'bg-accent-amber text-black'
                : 'bg-black/60 text-white hover:bg-black/80'
            )}
            tabIndex={0}
            aria-label={inWatchlist ? 'Von Watchlist entfernen' : 'Zur Watchlist hinzufügen'}
          >
            {inWatchlist ? (
              <Check size={14} className="sm:w-4 sm:h-4" />
            ) : (
              <Plus size={14} className="sm:w-4 sm:h-4" />
            )}
          </button>

          {/* Year Badge */}
          {year && (
            <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-black/70 text-white">
                {year}
              </span>
            </div>
          )}
        </div>

        {/* Title & Stats */}
        {showTitle && (
          <div className="mt-2 px-1">
            <h3 className="text-sm font-medium text-white truncate group-hover:text-accent-amber transition-colors">
              {title}
            </h3>
            <div className="flex items-center gap-2 text-xs text-retro-muted mt-0.5">
              {video.viewCount > 0 && (
                <span className="flex items-center gap-1">
                  <Eye size={10} />
                  {formatCount(video.viewCount)}
                </span>
              )}
              {video.likeCount > 0 && (
                <span className="flex items-center gap-1">
                  <ThumbsUp size={10} />
                  {formatCount(video.likeCount)}
                </span>
              )}
              {!video.viewCount && !video.likeCount && category && (
                <span className="truncate">{category}</span>
              )}
            </div>
          </div>
        )}
      </Link>
    </div>
  );
}

/**
 * PosterRow - Horizontal scrolling row of poster cards
 */
export function PosterRow({ title, videos = [], showAllLink, size = 'md', className }) {
  if (videos.length === 0) return null;

  return (
    <section className={cn('mb-8', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-4 sm:px-6 md:px-8">
        <h2 className="text-xl sm:text-2xl font-semibold text-white">{title}</h2>
        {showAllLink && (
          <Link to={showAllLink} className="text-sm text-accent-amber hover:underline">
            Alle anzeigen →
          </Link>
        )}
      </div>

      {/* Scrolling Container */}
      <div className="relative">
        <div
          className="flex gap-3 sm:gap-4 overflow-x-auto scrollbar-thin pb-4 px-4 sm:px-6 md:px-8"
          style={{ scrollSnapType: 'x mandatory' }}
        >
          {videos.map((video) => (
            <div key={video.id} style={{ scrollSnapAlign: 'start' }}>
              <PosterCard video={video} size={size} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
