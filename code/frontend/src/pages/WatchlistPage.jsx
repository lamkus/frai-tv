import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Bookmark,
  BookmarkCheck,
  Trash2,
  Grid,
  List,
  SortAsc,
  Clock,
  Calendar,
  Play,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn, formatRelativeTime, formatDuration } from '../lib/utils';
import { useApp } from '../context/AppContext';
import { VideoCard } from '../components/video';
import { EmptyState } from '../components/ui';

/**
 * WatchlistPage - User's saved videos (favorites/watchlist)
 *
 * Features:
 * - List/Grid view toggle
 * - Sort options
 * - Bulk actions (remove all)
 * - Progress tracking for partially watched
 */
export default function WatchlistPage() {
  const { t } = useTranslation();
  const { watchlist, removeFromWatchlist, openPlayer, videos } = useApp();
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('added');

  // Get full video data for watchlist items
  const watchlistVideos = useMemo(() => {
    const videoMap = new Map(videos.map((v) => [v.id || v.ytId, v]));

    return watchlist
      .map((item) => {
        const video = videoMap.get(item.id);
        return video ? { ...video, addedAt: item.addedAt } : null;
      })
      .filter(Boolean);
  }, [watchlist, videos]);

  // Sort watchlist
  const sortedVideos = useMemo(() => {
    const sorted = [...watchlistVideos];

    switch (sortBy) {
      case 'added':
        sorted.sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));
        break;
      case 'title':
        sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
        break;
      case 'duration':
        sorted.sort((a, b) => (b.duration || 0) - (a.duration || 0));
        break;
      case 'newest':
        sorted.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));
        break;
      default:
        break;
    }

    return sorted;
  }, [watchlistVideos, sortBy]);

  // Remove all from watchlist
  const handleClearAll = () => {
    if (window.confirm(t('confirmRemoveAll'))) {
      watchlist.forEach((item) => removeFromWatchlist(item.id));
    }
  };

  // Empty state
  if (watchlistVideos.length === 0) {
    return <EmptyState variant="EmptyWatchlist" />;
  }

  return (
    <div className="min-h-screen pt-4 pb-12">
      {/* Header */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mb-6 md:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <BookmarkCheck className="text-accent-cyan" size={28} />
              <h1 className="text-fluid-3xl font-display">{t('watchlist')}</h1>
            </div>
            <p className="text-fluid-base text-retro-muted">
              {watchlistVideos.length} {watchlistVideos.length === 1 ? 'Video' : 'Videos'}{' '}
              {t('saved')}
            </p>
          </div>

          {/* Quick Play All Button */}
          {watchlistVideos.length > 0 && (
            <button onClick={() => openPlayer(watchlistVideos[0])} className="btn btn-primary">
              <Play size={18} />
              {t('playAll')}
            </button>
          )}
        </div>
      </div>

      {/* Toolbar */}
      <div
        className="sticky top-14 sm:top-16 md:top-18 lg:top-20 z-30 
                      bg-retro-black/95 backdrop-blur-md border-b border-retro-gray
                      px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 py-3"
      >
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {/* Sort */}
            <div className="flex items-center gap-2">
              <SortAsc size={16} className="text-retro-muted hidden sm:block" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-retro-dark border border-retro-gray rounded-lg
                         px-3 py-2 text-fluid-sm focus:outline-none focus:border-accent-cyan"
              >
                <option value="added">{t('sortRecentlyAdded')}</option>
                <option value="title">{t('sortTitle')}</option>
                <option value="duration">{t('sortLongest')}</option>
                <option value="newest">{t('sortNewest')}</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Clear All */}
            <button onClick={handleClearAll} className="btn btn-ghost text-accent-red text-sm">
              <Trash2 size={16} />
              <span className="hidden sm:inline">{t('removeAll')}</span>
            </button>

            {/* View Mode Toggle */}
            <div className="flex items-center border border-retro-gray rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 transition-colors',
                  viewMode === 'grid'
                    ? 'bg-accent-red text-white'
                    : 'text-retro-muted hover:text-white'
                )}
                aria-label={t('gridView')}
              >
                <Grid size={18} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-2 transition-colors',
                  viewMode === 'list'
                    ? 'bg-accent-red text-white'
                    : 'text-retro-muted hover:text-white'
                )}
                aria-label={t('listView')}
              >
                <List size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Video Grid/List */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mt-6">
        {viewMode === 'grid' ? (
          <div
            className="grid grid-cols-video-mobile sm:grid-cols-video-tablet md:grid-cols-video-desktop 
                         lg:grid-cols-video-hd 3xl:grid-cols-video-fhd 5k:grid-cols-video-4k gap-4"
          >
            {sortedVideos.map((video) => (
              <VideoCard key={video.id || video.ytId} video={video} showBookmark />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {sortedVideos.map((video) => (
              <WatchlistListItem
                key={video.id || video.ytId}
                video={video}
                onPlay={() => openPlayer(video)}
                onRemove={() => removeFromWatchlist(video.id || video.ytId)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// List view item component
function WatchlistListItem({ video, onPlay, onRemove }) {
  const { t } = useTranslation();
  return (
    <div
      className="group flex items-center gap-4 p-3 bg-retro-dark/50 
                   rounded-lg border border-transparent hover:border-retro-gray
                   transition-all"
    >
      {/* Thumbnail */}
      <button
        onClick={onPlay}
        className="relative w-40 sm:w-48 aspect-video rounded-lg overflow-hidden shrink-0
                  group/thumb"
      >
        <img
          src={video.thumbnailUrl || `https://img.youtube.com/vi/${video.ytId}/mqdefault.jpg`}
          alt={video.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <div
          className="absolute inset-0 bg-black/60 opacity-0 group-hover/thumb:opacity-100
                      flex items-center justify-center transition-opacity"
        >
          <Play className="text-white" size={32} />
        </div>
        {video.duration && (
          <span
            className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 
                         bg-black/80 rounded text-xs font-medium"
          >
            {formatDuration(video.duration)}
          </span>
        )}
      </button>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3
          className="font-semibold text-fluid-base line-clamp-2 mb-1 cursor-pointer
                   hover:text-accent-cyan transition-colors"
          onClick={onPlay}
        >
          {video.title}
        </h3>
        <p className="text-fluid-sm text-retro-muted">{video.channelName}</p>
        <div className="flex items-center gap-3 mt-2 text-xs text-retro-muted">
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {formatDuration(video.duration)}
          </span>
          <span className="flex items-center gap-1">
            <Calendar size={12} />
            {formatRelativeTime(video.addedAt)} hinzugefügt
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={onPlay} className="btn btn-primary btn-sm">
          <Play size={16} />
          <span className="hidden md:inline">{t('play')}</span>
        </button>
        <button
          onClick={onRemove}
          className="p-2 text-retro-muted hover:text-accent-red transition-colors"
          aria-label={t('removeFromWatchlist')}
        >
          <Trash2 size={18} />
        </button>
      </div>
    </div>
  );
}
