import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { History, Trash2, Play, Clock, X, Search } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { formatRelativeTime, formatDuration } from '../lib/utils';
import { useApp } from '../context/AppContext';
import { EmptyState } from '../components/ui';

/**
 * HistoryPage - Watch history with time groupings
 *
 * Features:
 * - Grouped by time (Today, Yesterday, This Week, etc.)
 * - Search within history
 * - Clear individual or all history
 * - Resume playback option
 */
export default function HistoryPage() {
  const { t } = useTranslation();
  const { continueWatching, clearHistory, openPlayer, videos } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  // Build history from continueWatching and videos
  const historyItems = useMemo(() => {
    const videoMap = new Map(videos.map((v) => [v.id || v.ytId, v]));

    return continueWatching
      .map((item) => {
        const video = videoMap.get(item.id);
        if (!video) return null;
        return {
          ...video,
          watchedAt: item.watchedAt,
          progress: item.progress,
          completed: item.progress >= 0.9,
        };
      })
      .filter(Boolean)
      .sort((a, b) => new Date(b.watchedAt) - new Date(a.watchedAt));
  }, [continueWatching, videos]);

  // Filter by search
  const filteredHistory = useMemo(() => {
    if (!searchTerm.trim()) return historyItems;

    const query = searchTerm.toLowerCase();
    return historyItems.filter(
      (v) => v.title?.toLowerCase().includes(query) || v.channelName?.toLowerCase().includes(query)
    );
  }, [historyItems, searchTerm]);

  // Group by time period
  const groupedHistory = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const thisWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thisMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const groups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      thisMonth: [],
      older: [],
    };

    filteredHistory.forEach((item) => {
      const watchDate = new Date(item.watchedAt);

      if (watchDate >= today) {
        groups.today.push(item);
      } else if (watchDate >= yesterday) {
        groups.yesterday.push(item);
      } else if (watchDate >= thisWeek) {
        groups.thisWeek.push(item);
      } else if (watchDate >= thisMonth) {
        groups.thisMonth.push(item);
      } else {
        groups.older.push(item);
      }
    });

    return groups;
  }, [filteredHistory]);

  const groupLabels = {
    today: t('historyGroups.today'),
    yesterday: t('historyGroups.yesterday'),
    thisWeek: t('historyGroups.thisWeek'),
    thisMonth: t('historyGroups.thisMonth'),
    older: t('historyGroups.older'),
  };

  // Clear all history
  const handleClearAll = () => {
    clearHistory();
    setShowClearConfirm(false);
  };

  // Empty state
  if (historyItems.length === 0) {
    return <EmptyState variant="EmptyHistory" />;
  }

  return (
    <div className="min-h-screen pt-4 pb-12">
      {/* Header */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mb-6 md:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <History className="text-accent-amber" size={28} />
              <h1 className="text-fluid-3xl font-display">{t('history')}</h1>
            </div>
            <p className="text-fluid-base text-retro-muted">
              {historyItems.length} {historyItems.length === 1 ? 'Video' : 'Videos'}{' '}
              {t('historyGroups.watched')}
            </p>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div
        className="sticky top-14 sm:top-16 md:top-18 lg:top-20 z-30 
                      bg-retro-black/95 backdrop-blur-md border-b border-retro-gray
                      px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 py-3"
      >
        <div className="flex items-center justify-between gap-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted"
              size={18}
            />
            <input
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={t('searchInHistory')}
              className="w-full bg-retro-dark border border-retro-gray rounded-lg
                       pl-10 pr-4 py-2 text-fluid-sm
                       focus:outline-none focus:border-accent-cyan"
            />
          </div>

          {/* Clear History */}
          <button
            onClick={() => setShowClearConfirm(true)}
            className="btn btn-ghost text-accent-red text-sm"
          >
            <Trash2 size={16} />
            <span className="hidden sm:inline">{t('clearHistory')}</span>
          </button>
        </div>
      </div>

      {/* History Groups */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mt-6">
        {/* No Results */}
        {filteredHistory.length === 0 && searchTerm && (
          <div className="text-center py-12">
            <p className="text-retro-muted">{t('noResults')}</p>
          </div>
        )}

        {/* Grouped History */}
        <div className="space-y-8">
          {Object.entries(groupedHistory).map(([key, items]) => {
            if (items.length === 0) return null;

            return (
              <section key={key}>
                <h2 className="text-fluid-lg font-semibold mb-4 text-retro-muted">
                  {groupLabels[key]}
                </h2>
                <div className="space-y-3">
                  {items.map((video) => (
                    <HistoryItem
                      key={`${video.id || video.ytId}-${video.watchedAt}`}
                      video={video}
                      onPlay={() => openPlayer(video)}
                      onRemove={() => {
                        /* Remove from history */
                      }}
                    />
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </div>

      {/* Clear Confirmation Modal */}
      {showClearConfirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4
                       bg-black/80 backdrop-blur-sm animate-fade-in"
        >
          <div
            className="bg-retro-dark border border-retro-gray rounded-xl 
                        max-w-sm w-full p-6 shadow-2xl animate-scale-in"
          >
            <h3 className="text-fluid-xl font-semibold mb-2">{t('historyGroups.clearConfirm')}</h3>
            <p className="text-retro-muted mb-6">{t('historyGroups.clearWarning')}</p>
            <div className="flex gap-3">
              <button onClick={() => setShowClearConfirm(false)} className="btn btn-outline flex-1">
                {t('cancel')}
              </button>
              <button
                onClick={handleClearAll}
                className="btn bg-accent-red hover:bg-accent-red/80 flex-1"
              >
                {t('historyGroups.delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// History item component
function HistoryItem({ video, onPlay, onRemove }) {
  const { t } = useTranslation();
  const progressPercent = Math.round((video.progress || 0) * 100);

  return (
    <div
      className="group flex items-center gap-4 p-3 bg-retro-dark/30 
                   rounded-lg hover:bg-retro-dark/60 transition-all"
    >
      {/* Thumbnail with Progress */}
      <button
        onClick={onPlay}
        className="relative w-36 sm:w-44 aspect-video rounded-lg overflow-hidden shrink-0"
      >
        <img
          src={video.thumbnailUrl || `https://img.youtube.com/vi/${video.ytId}/mqdefault.jpg`}
          alt={video.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />

        {/* Play overlay */}
        <div
          className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100
                      flex items-center justify-center transition-opacity"
        >
          <Play className="text-white" size={28} />
        </div>

        {/* Duration badge */}
        {video.duration && (
          <span
            className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 
                         bg-black/80 rounded text-xs font-medium"
          >
            {formatDuration(video.duration)}
          </span>
        )}

        {/* Progress bar */}
        {video.progress > 0 && video.progress < 0.95 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-retro-gray/50">
            <div className="h-full bg-accent-red" style={{ width: `${progressPercent}%` }} />
          </div>
        )}

        {/* Completed badge */}
        {video.completed && (
          <div
            className="absolute top-1.5 left-1.5 px-1.5 py-0.5 
                        bg-green-500/90 rounded text-xs font-medium"
          >
            ✓ {t('historyGroups.seen')}
          </div>
        )}
      </button>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3
          className="font-medium text-fluid-sm line-clamp-2 mb-1 cursor-pointer
                   hover:text-accent-cyan transition-colors"
          onClick={onPlay}
        >
          {video.title}
        </h3>
        <p className="text-fluid-xs text-retro-muted">{video.channelName}</p>

        <div className="flex items-center gap-3 mt-1.5 text-xs text-retro-muted">
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {formatRelativeTime(video.watchedAt)}
          </span>
          {video.progress > 0 && video.progress < 0.95 && (
            <span className="text-accent-amber">
              {t('historyGroups.percentWatched', { percent: progressPercent })}
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        {video.progress > 0 && video.progress < 0.95 ? (
          <button onClick={onPlay} className="btn btn-primary btn-sm whitespace-nowrap">
            <Play size={14} />
            {t('historyGroups.continueWatching')}
          </button>
        ) : (
          <button onClick={onPlay} className="btn btn-secondary btn-sm">
            <Play size={14} />
          </button>
        )}
        <button
          onClick={onRemove}
          className="p-2 text-retro-muted hover:text-accent-red transition-colors"
          aria-label={t('historyGroups.removeFromHistory')}
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
