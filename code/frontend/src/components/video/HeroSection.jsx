import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Play, Info, Volume2, VolumeX, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn, getYouTubeThumbnail, truncateText } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import useVideoI18n from '../../lib/useVideoI18n';

/**
 * HeroSection Component - Featured video banner
 *
 * Features:
 * - Full-width background image/video
 * - Auto-rotation (optional)
 * - Responsive text sizing
 * - Call-to-action buttons
 * - Mobile-optimized layout
 */
export default function HeroSection({ videos = [], autoPlay = true, interval = 8000 }) {
  const { t } = useTranslation();
  const { openPlayer, featuredVideo } = useApp();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const { getVideoText } = useVideoI18n();

  // Use provided videos or featured video
  const heroVideos = videos.length > 0 ? videos : featuredVideo ? [featuredVideo] : [];
  const currentVideo = heroVideos[currentIndex];

  const goToNext = useCallback(() => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % heroVideos.length);
      setIsTransitioning(false);
    }, 300);
  }, [heroVideos.length]);

  const goToPrev = useCallback(() => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev - 1 + heroVideos.length) % heroVideos.length);
      setIsTransitioning(false);
    }, 300);
  }, [heroVideos.length]);

  // Auto-rotate
  useEffect(() => {
    if (!autoPlay || heroVideos.length <= 1) return;

    const timer = setInterval(() => {
      goToNext();
    }, interval);

    return () => clearInterval(timer);
  }, [autoPlay, interval, heroVideos.length, currentIndex, goToNext]);

  const goToIndex = (index) => {
    if (index === currentIndex) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentIndex(index);
      setIsTransitioning(false);
    }, 300);
  };

  if (!currentVideo) {
    return (
      <section className="hero-section bg-retro-darker flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-fluid-3xl font-display text-retro-muted">{t('homePage.welcome')}</h2>
          <p className="text-fluid-lg text-retro-muted mt-4">{t('homePage.loadVideos')}</p>
        </div>
      </section>
    );
  }

  const { ytId, category, thumbnailUrl } = currentVideo;
  const { title, description } = getVideoText(currentVideo);
  const backgroundImage = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');

  return (
    <section className="hero-section">
      {/* Background Image */}
      <div
        className={cn(
          'absolute inset-0 transition-opacity duration-500',
          isTransitioning ? 'opacity-0' : 'opacity-100'
        )}
      >
        <img src={backgroundImage} alt="" className="hero-background" aria-hidden="true" />

        {/* Gradients */}
        <div className="hero-gradient" />
        <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-transparent to-retro-black/30" />
      </div>

      {/* Content */}
      <div
        className={cn(
          'hero-content transition-all duration-500',
          isTransitioning ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'
        )}
      >
        {/* Category Badge */}
        {category && <span className="badge badge-year mb-2 xs:mb-3 sm:mb-4">{category}</span>}

        {/* Title */}
        <h1
          className="font-display text-fluid-2xl xs:text-fluid-3xl sm:text-fluid-hero leading-tight mb-2 xs:mb-3 sm:mb-4 md:mb-6
                       text-white drop-shadow-lg"
        >
          {title}
        </h1>

        {/* Description */}
        {description && (
          <p
            className="text-fluid-sm xs:text-fluid-base text-retro-white/90 max-w-xl xs:max-w-2xl 3xl:max-w-3xl
                       line-clamp-2 sm:line-clamp-3 mb-3 xs:mb-4 sm:mb-6 md:mb-8
                       drop-shadow"
          >
            {truncateText(description, 200)}
          </p>
        )}

        {/* Actions */}
        <div className="flex flex-wrap items-center gap-2 xs:gap-3 sm:gap-4">
          <button
            onClick={() => openPlayer(currentVideo)}
            className="btn btn-primary text-fluid-sm xs:text-fluid-base
                     px-4 xs:px-6 py-2.5 xs:py-3 sm:px-8 sm:py-4 3xl:px-10 3xl:py-5"
          >
            <Play size={18} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" fill="currentColor" />
            <span className="hidden xs:inline">{t('play')}</span>
            <span className="xs:hidden">{t('playShort')}</span>
          </button>

          <button
            onClick={() => {
              /* Open detail modal */
            }}
            className="btn btn-secondary text-fluid-sm xs:text-fluid-base
                     px-4 xs:px-6 py-2.5 xs:py-3 sm:px-8 sm:py-4 3xl:px-10 3xl:py-5"
          >
            <Info size={18} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" />
            <span className="hidden xs:inline">{t('moreInfo')}</span>
            <span className="xs:hidden">{t('moreInfoShort')}</span>
          </button>

          {/* Mute Toggle */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="btn btn-ghost btn-icon ml-auto"
            aria-label={isMuted ? 'Ton an' : 'Ton aus'}
          >
            {isMuted ? (
              <VolumeX size={20} className="xs:w-6 xs:h-6" />
            ) : (
              <Volume2 size={20} className="xs:w-6 xs:h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation Arrows (Desktop) */}
      {heroVideos.length > 1 && (
        <>
          <button
            onClick={goToPrev}
            className="absolute left-2 xs:left-4 top-1/2 -translate-y-1/2 z-20
                     btn btn-ghost btn-icon hidden sm:flex
                     bg-black/30 hover:bg-black/50"
            aria-label="Vorheriges Video"
          >
            <ChevronLeft size={28} className="md:w-8 md:h-8" />
          </button>

          <button
            onClick={goToNext}
            className="absolute right-2 xs:right-4 top-1/2 -translate-y-1/2 z-20
                     btn btn-ghost btn-icon hidden sm:flex
                     bg-black/30 hover:bg-black/50"
            aria-label="Nächstes Video"
          >
            <ChevronRight size={28} className="md:w-8 md:h-8" />
          </button>
        </>
      )}

      {/* Pagination Dots */}
      {heroVideos.length > 1 && (
        <div
          className="absolute bottom-3 xs:bottom-4 sm:bottom-6 md:bottom-8 left-1/2 -translate-x-1/2 z-20
                       flex items-center gap-1.5 xs:gap-2"
        >
          {heroVideos.map((_, index) => (
            <button
              key={index}
              onClick={() => goToIndex(index)}
              className={cn(
                'h-2 xs:h-2.5 rounded-full transition-all duration-300 min-w-[8px]',
                index === currentIndex
                  ? 'bg-white w-5 xs:w-6 sm:w-8'
                  : 'bg-white/40 hover:bg-white/60 w-2 xs:w-2.5'
              )}
              aria-label={`Video ${index + 1} anzeigen`}
              aria-current={index === currentIndex}
            />
          ))}
        </div>
      )}
    </section>
  );
}
