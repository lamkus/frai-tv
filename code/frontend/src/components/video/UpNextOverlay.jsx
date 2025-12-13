import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Play, X, SkipForward, Pause } from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../../lib/utils';
import { getUpNextQueue } from '../../lib/recommendationEngine';

/**
 * UpNextOverlay - Netflix-style "Up Next" countdown overlay
 *
 * Shows when current video is about to end (or has ended).
 * Displays countdown timer and allows user to:
 * - Let it auto-play next video
 * - Cancel autoplay
 * - Skip to next immediately
 * - Choose from queue
 */
export default function UpNextOverlay({
  currentVideo,
  allVideos,
  onPlayNext,
  onCancel,
  isVideoEnded = false,
  countdownSeconds = 8,
  className,
}) {
  const { t } = useTranslation();
  const [countdown, setCountdown] = useState(countdownSeconds);
  const [isPaused, setIsPaused] = useState(false);
  const [upNextQueue, setUpNextQueue] = useState([]);
  const [showQueue, setShowQueue] = useState(false);
  const countdownRef = useRef(null);

  // Generate up next queue
  useEffect(() => {
    if (currentVideo && allVideos.length > 0) {
      const queue = getUpNextQueue(currentVideo, allVideos, 5);
      setUpNextQueue(queue);
    }
  }, [currentVideo, allVideos]);

  // Countdown timer
  useEffect(() => {
    if (!isVideoEnded || isPaused || countdown <= 0) return;

    countdownRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          // Auto-play next video
          if (upNextQueue.length > 0) {
            onPlayNext(upNextQueue[0]);
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
      }
    };
  }, [isVideoEnded, isPaused, countdown, upNextQueue, onPlayNext]);

  // Reset countdown when video ends
  useEffect(() => {
    if (isVideoEnded) {
      setCountdown(countdownSeconds);
      setIsPaused(false);
    }
  }, [isVideoEnded, countdownSeconds]);

  const handlePlayNow = useCallback(
    (video) => {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
      }
      onPlayNext(video);
    },
    [onPlayNext]
  );

  const handleCancel = useCallback(() => {
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
    }
    setIsPaused(true);
    onCancel?.();
  }, [onCancel]);

  const togglePause = useCallback(() => {
    setIsPaused((prev) => !prev);
  }, []);

  if (!isVideoEnded || upNextQueue.length === 0) return null;

  const nextVideo = upNextQueue[0];

  return (
    <div
      className={cn(
        'absolute inset-0 bg-retro-black/90 flex items-center justify-center z-30',
        'animate-fade-in',
        className
      )}
    >
      <div className="w-full max-w-2xl p-6">
        {/* Main Up Next Card */}
        <div className="relative bg-retro-darker rounded-xl overflow-hidden shadow-2xl">
          {/* Thumbnail */}
          <div className="relative aspect-video">
            <img
              src={getYouTubeThumbnail(nextVideo.ytId, 'maxres')}
              alt={nextVideo.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = getYouTubeThumbnail(nextVideo.ytId, 'hq');
              }}
            />

            {/* Countdown Circle Overlay */}
            <div className="absolute inset-0 flex items-center justify-center bg-black/50">
              <div className="relative">
                {/* Circular Progress */}
                <svg className="w-24 h-24 -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="44"
                    fill="none"
                    stroke="rgba(255,255,255,0.2)"
                    strokeWidth="4"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="44"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                    className="text-accent-red"
                    strokeDasharray={`${2 * Math.PI * 44}`}
                    strokeDashoffset={`${2 * Math.PI * 44 * (1 - countdown / countdownSeconds)}`}
                    style={{ transition: 'stroke-dashoffset 1s linear' }}
                  />
                </svg>

                {/* Countdown Number / Play Button */}
                <button
                  onClick={() => handlePlayNow(nextVideo)}
                  className="absolute inset-0 flex flex-col items-center justify-center 
                           hover:scale-110 transition-transform"
                >
                  {isPaused ? (
                    <Play size={32} className="text-white" fill="currentColor" />
                  ) : (
                    <>
                      <span className="text-3xl font-bold text-white">{countdown}</span>
                      <span className="text-xs text-white/70">{t('seconds')}</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Duration Badge */}
            {nextVideo.duration && (
              <span className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                {formatDuration(nextVideo.duration)}
              </span>
            )}
          </div>

          {/* Info Section */}
          <div className="p-4">
            <p className="text-sm text-accent-cyan font-medium mb-1">{t('upNext')}</p>
            <h3 className="text-lg font-semibold line-clamp-2 mb-2">{nextVideo.title}</h3>
            {nextVideo.category && (
              <span className="badge badge-year text-xs">{nextVideo.category}</span>
            )}

            {/* Action Buttons */}
            <div className="flex items-center gap-2 mt-4">
              <button
                onClick={() => handlePlayNow(nextVideo)}
                className="btn btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <Play size={16} fill="currentColor" />
                {t('playNow')}
              </button>

              <button
                onClick={togglePause}
                className="btn btn-secondary btn-icon"
                aria-label={isPaused ? t('resume') : t('pause')}
              >
                {isPaused ? <Play size={18} /> : <Pause size={18} />}
              </button>

              <button
                onClick={handleCancel}
                className="btn btn-ghost btn-icon"
                aria-label={t('cancel')}
              >
                <X size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Queue Preview */}
        {upNextQueue.length > 1 && (
          <div className="mt-4">
            <button
              onClick={() => setShowQueue(!showQueue)}
              className="flex items-center gap-2 text-sm text-retro-muted hover:text-white transition-colors mb-2"
            >
              <SkipForward size={16} />
              {showQueue ? t('hideQueue') : `${upNextQueue.length - 1} ${t('moreVideos')}`}
            </button>

            {showQueue && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 animate-fade-in">
                {upNextQueue.slice(1, 5).map((video) => (
                  <button
                    key={video.ytId || video.id}
                    onClick={() => handlePlayNow(video)}
                    className="group relative aspect-video rounded-lg overflow-hidden
                             hover:ring-2 hover:ring-accent-cyan transition-all"
                  >
                    <img
                      src={getYouTubeThumbnail(video.ytId, 'mq')}
                      alt={video.title}
                      className="w-full h-full object-cover"
                    />
                    <div
                      className="absolute inset-0 bg-black/60 flex items-center justify-center
                                  opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Play size={20} className="text-white" fill="currentColor" />
                    </div>
                    <span
                      className="absolute bottom-1 left-1 right-1 text-[10px] text-white 
                                   line-clamp-1 bg-black/70 px-1 rounded"
                    >
                      {video.title}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
