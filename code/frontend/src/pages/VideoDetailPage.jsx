import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Play,
  Share2,
  Clock,
  Calendar,
  Tag,
  ChevronLeft,
  ThumbsUp,
  Eye,
  Bookmark,
  BookmarkCheck,
} from 'lucide-react';
import useMeta from '../lib/useMeta';
import { cn, formatDuration, formatRelativeTime, getYouTubeThumbnail } from '../lib/utils';
import { useApp } from '../context/AppContext';
import { CategoryRow } from '../components/video';
import { ErrorState } from '../components/ui';

/**
 * VideoDetailPage - Full video detail view
 *
 * Features:
 * - Large hero with video thumbnail/preview
 * - Video metadata (title, description, date, duration)
 * - Play button, watchlist toggle
 * - Related videos
 * - Share functionality
 */
export default function VideoDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { videos, openPlayer, addToWatchlist, removeFromWatchlist, watchlist } = useApp();
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

  // Find the video
  const video = videos.find((v) => v.id === parseInt(id, 10) || v.id === id || v.ytId === id);

  // Set page meta
  useMeta({
    title: video?.title || 'Video nicht gefunden',
    description: video?.description?.slice(0, 160) || 'Video Details auf frai.tv',
  });

  // Check if in watchlist
  const isInWatchlist = watchlist.some((w) => w.id === video?.id || w.id === video?.ytId);

  // Get related videos (same category or random)
  const relatedVideos = videos
    .filter((v) => v.id !== video?.id && v.ytId !== video?.ytId)
    .filter((v) => v.category === video?.category || Math.random() > 0.7)
    .slice(0, 12);

  // Get more from same category
  const moreLikeThis = videos
    .filter((v) => v.category === video?.category && v.id !== video?.id)
    .slice(0, 12);

  const handlePlay = () => {
    if (video) openPlayer(video);
  };

  const handleWatchlistToggle = () => {
    if (!video) return;
    const videoId = video.id || video.ytId;
    if (isInWatchlist) {
      removeFromWatchlist(videoId);
    } else {
      addToWatchlist(videoId);
    }
  };

  const handleShare = async () => {
    if (!video) return;

    const shareData = {
      title: video.title,
      text: `Schau dir "${video.title}" auf frai.tv an!`,
      url: window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(window.location.href);
        alert('Link in Zwischenablage kopiert!');
      }
    } catch (err) {
      console.error('Share failed:', err);
    }
  };

  // 404 state
  if (!video) {
    return <ErrorState variant="NotFound" />;
  }

  const {
    title,
    description,
    ytId,
    category,
    duration,
    publishDate,
    thumbnailUrl,
    viewCount,
    likeCount,
    channelName,
  } = video;

  const thumbnail = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');

  return (
    <div className="min-h-screen pb-12 safe-bottom">
      {/* Hero Section */}
      <section className="relative">
        {/* Background Image */}
        <div className="absolute inset-0 h-[50vh] xs:h-[55vh] sm:h-[60vh] md:h-[70vh]">
          <img src={thumbnail} alt="" className="w-full h-full object-cover" aria-hidden="true" />
          <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-retro-black/60 to-retro-black/30" />
          <div className="absolute inset-0 bg-gradient-to-r from-retro-black/80 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 min-h-[50vh] xs:min-h-[55vh] sm:min-h-[60vh] md:min-h-[70vh] flex flex-col justify-end">
          {/* Back Button */}
          <button
            onClick={() => navigate(-1)}
            className="absolute top-3 left-3 xs:top-4 xs:left-4 sm:top-6 sm:left-6 btn btn-ghost min-h-[44px] safe-top"
          >
            <ChevronLeft size={20} />
            <span className="hidden xs:inline">Zurück</span>
          </button>

          {/* Video Info */}
          <div className="px-3 xs:px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 pb-6 xs:pb-8 md:pb-12">
            <div className="max-w-3xl">
              {/* Category Badge */}
              {category && (
                <span className="badge badge-year mb-2 xs:mb-3">
                  <Tag size={12} className="mr-1" />
                  {category}
                </span>
              )}

              {/* Title */}
              <h1 className="text-fluid-2xl xs:text-fluid-3xl sm:text-fluid-hero font-display mb-3 xs:mb-4 leading-tight">
                {title}
              </h1>

              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-2 xs:gap-3 sm:gap-4 text-fluid-xs xs:text-fluid-sm text-retro-muted mb-4 xs:mb-6">
                {publishDate && (
                  <span className="flex items-center gap-1 xs:gap-1.5">
                    <Calendar size={14} />
                    {formatRelativeTime(publishDate)}
                  </span>
                )}
                {duration && (
                  <span className="flex items-center gap-1 xs:gap-1.5">
                    <Clock size={14} />
                    {formatDuration(duration)}
                  </span>
                )}
                {viewCount && (
                  <span className="flex items-center gap-1 xs:gap-1.5">
                    <Eye size={14} />
                    <span className="hidden xs:inline">
                      {viewCount.toLocaleString('de-DE')} Aufrufe
                    </span>
                    <span className="xs:hidden">{(viewCount / 1000).toFixed(0)}K</span>
                  </span>
                )}
                {likeCount && (
                  <span className="flex items-center gap-1 xs:gap-1.5">
                    <ThumbsUp size={14} />
                    {likeCount.toLocaleString('de-DE')}
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-wrap items-center gap-2 xs:gap-3">
                <button
                  onClick={handlePlay}
                  className="btn btn-primary text-fluid-sm xs:text-fluid-base px-4 xs:px-6 py-2.5 xs:py-3 sm:px-8 sm:py-4"
                >
                  <Play size={18} className="xs:w-5 xs:h-5" fill="currentColor" />
                  <span className="hidden xs:inline">Abspielen</span>
                  <span className="xs:hidden">Play</span>
                </button>

                <button
                  onClick={handleWatchlistToggle}
                  className={cn(
                    'btn text-fluid-sm xs:text-fluid-base px-3 xs:px-5 py-2.5 xs:py-3',
                    isInWatchlist ? 'btn-primary' : 'btn-secondary'
                  )}
                >
                  {isInWatchlist ? (
                    <>
                      <BookmarkCheck size={18} />
                      <span className="hidden sm:inline">Auf Watchlist</span>
                    </>
                  ) : (
                    <>
                      <Bookmark size={18} />
                      <span className="hidden sm:inline">Watchlist</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleShare}
                  className="btn btn-secondary btn-icon"
                  aria-label="Teilen"
                >
                  <Share2 size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Description Section */}
      <section className="px-3 xs:px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 py-6 xs:py-8 md:py-12">
        <div className="max-w-4xl">
          <h2 className="text-fluid-lg xs:text-fluid-xl font-semibold mb-3 xs:mb-4">
            Beschreibung
          </h2>

          {description ? (
            <div className="relative">
              <p
                className={cn(
                  'text-fluid-sm xs:text-fluid-base text-retro-muted whitespace-pre-wrap leading-relaxed',
                  !isDescriptionExpanded && 'line-clamp-3 xs:line-clamp-4'
                )}
              >
                {description}
              </p>

              {description.length > 200 && (
                <button
                  onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                  className="mt-2 text-accent-cyan hover:underline text-fluid-sm min-h-[44px] flex items-center"
                >
                  {isDescriptionExpanded ? 'Weniger anzeigen' : 'Mehr anzeigen'}
                </button>
              )}
            </div>
          ) : (
            <p className="text-fluid-sm xs:text-fluid-base text-retro-muted italic">
              Keine Beschreibung verfügbar.
            </p>
          )}

          {/* Channel Info */}
          {channelName && (
            <div className="mt-4 xs:mt-6 pt-4 xs:pt-6 border-t border-retro-gray/30">
              <p className="text-fluid-xs xs:text-fluid-sm text-retro-muted">
                Kanal: <span className="text-white font-medium">{channelName}</span>
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Related Videos */}
      {moreLikeThis.length > 0 && (
        <CategoryRow
          title={`Mehr aus ${category}`}
          videos={moreLikeThis}
          showAllLink={`/browse?category=${encodeURIComponent(category)}`}
        />
      )}

      {relatedVideos.length > 0 && <CategoryRow title="Ähnliche Videos" videos={relatedVideos} />}
    </div>
  );
}
