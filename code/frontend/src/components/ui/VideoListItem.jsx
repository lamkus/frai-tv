import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Clock, Eye } from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../../lib/utils';
import { useApp } from '../../context/AppContext';

/**
 * VideoListItem - Compact list item with thumbnail (frai.tv style)
 *
 * Features:
 * - Small thumbnail
 * - Title and description
 * - Duration and views
 * - AI badge
 */
export default function VideoListItem({ video, className }) {
  const { openPlayer } = useApp();
  const [imageError, setImageError] = useState(false);

  // Early return AFTER all hooks
  if (!video) return null;

  const { ytId, title, description, duration, viewCount, category, year } = video;
  const thumbnailUrl = video.thumbnailUrl || getYouTubeThumbnail(ytId, 'medium');

  return (
    <div
      className={cn(
        'group flex gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer',
        className
      )}
      onClick={() => openPlayer(video)}
    >
      {/* Thumbnail */}
      <div className="relative flex-shrink-0 w-16 sm:w-20 aspect-video rounded overflow-hidden">
        {!imageError ? (
          <img
            src={thumbnailUrl}
            alt=""
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-retro-dark flex items-center justify-center">
            <span className="text-lg">🎬</span>
          </div>
        )}

        {/* AI Badge */}
        <div className="absolute top-0.5 left-0.5">
          <span className="inline-flex items-center gap-0.5 px-1 py-0.5 rounded text-[8px] font-bold bg-accent-amber text-black">
            <Sparkles size={6} />
            AI
          </span>
        </div>
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-white truncate group-hover:text-accent-amber transition-colors">
          {title}
        </h3>
        <p className="text-xs text-retro-muted line-clamp-2 mt-0.5">{description || category}</p>
        <div className="flex items-center gap-3 mt-1 text-xs text-retro-muted">
          {duration && (
            <span className="flex items-center gap-1">
              <Clock size={10} />
              {formatDuration(duration)}
            </span>
          )}
          {viewCount && (
            <span className="flex items-center gap-1">
              <Eye size={10} />
              {formatViewCount(viewCount)}
            </span>
          )}
          {year && <span>{year}</span>}
        </div>
      </div>
    </div>
  );
}

/**
 * VideoListSection - Section with list items
 */
export function VideoListSection({ title, videos = [], columns = 3, showAllLink, className }) {
  if (videos.length === 0) return null;

  return (
    <section className={cn('mb-8 px-4 sm:px-6 lg:px-8', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        {showAllLink && (
          <Link to={showAllLink} className="text-sm text-accent-amber hover:underline">
            View All →
          </Link>
        )}
      </div>

      {/* Grid */}
      <div
        className={cn(
          'grid gap-2',
          columns === 2 && 'grid-cols-1 sm:grid-cols-2',
          columns === 3 && 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
          columns === 4 && 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
        )}
      >
        {videos.map((video) => (
          <VideoListItem key={video.id} video={video} />
        ))}
      </div>
    </section>
  );
}

/**
 * Format view count (e.g., 1.2M, 456K)
 */
function formatViewCount(count) {
  if (!count) return '';
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(0)}K`;
  }
  return count.toString();
}
