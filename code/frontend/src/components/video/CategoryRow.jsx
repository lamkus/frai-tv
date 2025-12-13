import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../../lib/utils';
import VideoCard from './VideoCard';

/**
 * CategoryRow Component - Horizontal scrollable video row
 *
 * Features:
 * - Smooth horizontal scrolling
 * - Navigation arrows on hover
 * - Responsive card sizing
 * - Snap scrolling
 * - Touch-friendly
 * - Live video previews on card hover
 */
export default function CategoryRow({
  title,
  videos = [],
  variant = 'default',
  showAllLink,
  enableLivePreview = true, // Enable live previews by default
  className,
}) {
  const { t } = useTranslation();
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  // Check scroll position
  const checkScrollPosition = () => {
    const container = scrollRef.current;
    if (!container) return;

    setCanScrollLeft(container.scrollLeft > 0);
    setCanScrollRight(container.scrollLeft < container.scrollWidth - container.clientWidth - 10);
  };

  useEffect(() => {
    checkScrollPosition();
    const container = scrollRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollPosition, { passive: true });
      window.addEventListener('resize', checkScrollPosition);
    }
    return () => {
      container?.removeEventListener('scroll', checkScrollPosition);
      window.removeEventListener('resize', checkScrollPosition);
    };
  }, [videos]);

  // Scroll by card width
  const scroll = (direction) => {
    const container = scrollRef.current;
    if (!container) return;

    // Get first card width + gap
    const card = container.querySelector('article');
    const cardWidth = card ? card.offsetWidth + 16 : 200; // 16px gap
    const scrollAmount = cardWidth * 3; // Scroll 3 cards at a time

    container.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    });
  };

  if (!videos.length) return null;

  return (
    <section
      className={cn('category-row', className)}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Header */}
      <div className="flex items-center justify-between category-title">
        <h2 className="text-fluid-lg xs:text-fluid-xl font-semibold text-white">{title}</h2>

        {showAllLink && (
          <a
            href={showAllLink}
            className="text-fluid-xs xs:text-fluid-sm text-retro-muted hover:text-accent-cyan transition-colors min-h-[44px] flex items-center"
          >
            <span className="hidden xs:inline">{t('showAll')}</span>
            <span className="xs:hidden">{t('all')}</span>
          </a>
        )}
      </div>

      {/* Slider Container */}
      <div className="relative group">
        {/* Left Arrow - Hidden on touch devices */}
        <button
          onClick={() => scroll('left')}
          disabled={!canScrollLeft}
          className={cn(
            'absolute left-0 top-0 bottom-4 z-10 w-10 xs:w-12 sm:w-14 md:w-16',
            'hidden sm:flex items-center justify-center',
            'bg-gradient-to-r from-retro-black via-retro-black/80 to-transparent',
            'opacity-0 transition-opacity duration-200',
            canScrollLeft && isHovering && 'sm:opacity-100',
            'disabled:opacity-0 disabled:cursor-default'
          )}
          aria-label="Nach links scrollen"
        >
          <ChevronLeft
            size={28}
            className="text-white drop-shadow-lg md:w-8 md:h-8 3xl:w-10 3xl:h-10"
          />
        </button>

        {/* Scrollable Container */}
        <div ref={scrollRef} className="category-slider scrollbar-hide">
          {videos.map((video, index) => (
            <VideoCard
              key={video.id || video.ytId || index}
              video={video}
              variant={variant}
              enableLivePreview={enableLivePreview}
            />
          ))}
        </div>

        {/* Right Arrow - Hidden on touch devices */}
        <button
          onClick={() => scroll('right')}
          disabled={!canScrollRight}
          className={cn(
            'absolute right-0 top-0 bottom-4 z-10 w-10 xs:w-12 sm:w-14 md:w-16',
            'hidden sm:flex items-center justify-center',
            'bg-gradient-to-l from-retro-black via-retro-black/80 to-transparent',
            'opacity-0 transition-opacity duration-200',
            canScrollRight && isHovering && 'sm:opacity-100',
            'disabled:opacity-0 disabled:cursor-default'
          )}
          aria-label="Nach rechts scrollen"
        >
          <ChevronRight
            size={28}
            className="text-white drop-shadow-lg md:w-8 md:h-8 3xl:w-10 3xl:h-10"
          />
        </button>
      </div>
    </section>
  );
}
