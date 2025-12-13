import { useMemo, useRef, useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Play,
  ChevronLeft,
  ChevronRight,
  Youtube,
  Instagram,
  Mail,
  ExternalLink,
  TrendingUp,
  Clock,
  Zap,
  Calendar,
  Star,
  Info,
} from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../lib/utils';
import useMeta from '../lib/useMeta';
import { useApp } from '../context/AppContext';
import { CATEGORIES } from '../data/remaikeData';
import { ErrorState } from '../components/ui';
import {
  getHybridRecommendations,
  explainRecommendation,
  RECOMMENDATION_CONFIG,
} from '../lib/recommendationEngine';

// Clean video title - remove quality tags (4K/8K is our standard)
const cleanTitle = (title) => {
  if (!title) return '';
  return title
    .replace(/\s*\|\s*(4K|8K|HD|4k|8k|hd)\s*/gi, '')
    .replace(/\s*\((4K|8K|HD|4k|8k|hd)\)\s*/gi, '')
    .replace(/\s*(4K|8K|HD|4k|8k|hd)$/gi, '')
    .replace(/\s+\|\s*$/g, '')
    .trim();
};

// Deduplicate videos by ytId
const dedupeVideos = (videos) => {
  const seen = new Set();
  return videos.filter((v) => {
    const id = v.ytId || v.id;
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
};

// Get category info by id
const getCategoryInfo = (categoryId) => {
  return CATEGORIES.find((c) => c.id === categoryId) || null;
};

/**
 * MediathekPage - Professional Streaming Layout
 *
 * Inspired by: ARD Mediathek, ZDF, waipu.tv
 *
 * Architecture:
 * - Hero: Featured content (40vh with gradient)
 * - Sidebar: Category navigation (sticky, 260px)
 * - Main: Content sections with horizontal carousels
 * - Footer: remAIke.IT branding
 */
export default function MediathekPage() {
  const { t } = useTranslation();
  const { videos, loading, error, openPlayer, continueWatching, refetchVideos } = useApp();

  useMeta({
    title: t('metaTitle'),
    description: t('metaDescription'),
  });

  // Featured videos (Top 5)
  const featuredVideos = useMemo(() => {
    return videos && videos.length > 0 ? videos.slice(0, 5) : [];
  }, [videos]);

  // Hybrid AI Recommendations - deduplicated
  const personalizedVideos = useMemo(() => {
    if (!videos || videos.length === 0) return [];
    const recs = getHybridRecommendations(videos, {
      count: 25,
      exploreMode: false,
      excludeWatched: true,
    });
    return dedupeVideos(recs).slice(0, 20);
  }, [videos]);

  // Continue Watching
  const continueWatchingVideos = useMemo(() => {
    return continueWatching
      .map((cw) => {
        const video = videos.find((v) => v.id === cw.videoId || v.ytId === cw.videoId);
        return video ? { ...video, progress: cw.percentage } : null;
      })
      .filter(Boolean)
      .slice(0, 12);
  }, [videos, continueWatching]);

  // Group by category
  const videosByCategory = useMemo(() => {
    const grouped = {};
    CATEGORIES.forEach((cat) => {
      grouped[cat.id] = videos.filter((v) => v.category === cat.id);
    });
    return grouped;
  }, [videos]);

  // Trending (by views) - deduplicated
  const trendingVideos = useMemo(() => {
    const sorted = [...videos].sort((a, b) => (b.views || 0) - (a.views || 0));
    return dedupeVideos(sorted).slice(0, 15);
  }, [videos]);

  // Recent videos - deduplicated
  const recentVideos = useMemo(() => {
    const sorted = [...videos].sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));
    return dedupeVideos(sorted).slice(0, 15);
  }, [videos]);

  const [selectedCategory, setSelectedCategory] = useState(null);

  // Error State
  if (error) {
    return <ErrorState variant="NetworkError" message={error} onRetry={() => refetchVideos()} />;
  }

  if (loading) {
    return <MediathekSkeleton />;
  }

  return (
    <div className="min-h-screen bg-retro-black text-white">
      {/* HERO SECTION - Featured Content */}
      {featuredVideos.length > 0 && (
        <HeroCarousel videos={featuredVideos} onPlay={openPlayer} t={t} />
      )}

      {/* MAIN LAYOUT - Content Only */}
      <div className="flex flex-col gap-0">
        {/* CONTENT - Sections with Carousels */}
        <main className="flex-1 px-4 md:px-8 py-8 space-y-12">
          {/* Horizontal Category Filter */}
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0 sticky top-16 z-30 bg-retro-black/95 backdrop-blur py-4 border-b border-white/5">
            <button
              onClick={() => setSelectedCategory(null)}
              className={cn(
                'whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border',
                selectedCategory === null
                  ? 'bg-accent-gold text-black border-accent-gold'
                  : 'bg-retro-dark border-retro-gray text-retro-muted hover:text-white hover:border-white/50'
              )}
            >
              {t('allCategories')}
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={cn(
                  'whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border flex items-center gap-2',
                  selectedCategory === cat.id
                    ? 'bg-accent-gold text-black border-accent-gold'
                    : 'bg-retro-dark border-retro-gray text-retro-muted hover:text-white hover:border-white/50'
                )}
              >
                {cat.icon && <span>{cat.icon}</span>}
                {t(`categories.${cat.id}`) || cat.label}
              </button>
            ))}
          </div>

          {/* Algorithm Info */}
          <div className="bg-gradient-to-r from-accent-gold/10 via-accent-amber/5 to-transparent border border-accent-gold/20 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3 text-xs">
              <span className="text-accent-gold font-semibold">🧠 HYBRID AI</span>
              <span className="text-retro-muted">
                {RECOMMENDATION_CONFIG.EPSILON * 100}% Exploration •
                {(1 - RECOMMENDATION_CONFIG.EPSILON) * 100}% Personalization
              </span>
            </div>
          </div>

          {/* Continue Watching */}
          {continueWatchingVideos.length > 0 && (
            <section>
              <SectionHeader
                title="Weiterschauen"
                icon={<Clock size={20} />}
                count={continueWatchingVideos.length}
              />
              <ContentRow
                videos={continueWatchingVideos}
                onPlay={openPlayer}
                showProgress={true}
                cardSize="large"
              />
            </section>
          )}

          {/* Trending */}
          <section>
            <SectionHeader
              title="Trend – Beliebt"
              icon={<TrendingUp size={20} />}
              count={trendingVideos.length}
            />
            <ContentRow videos={trendingVideos} onPlay={openPlayer} cardSize="medium" />
          </section>

          {/* Personalized */}
          {personalizedVideos.length > 0 && (
            <section>
              <SectionHeader
                title="Für Dich empfohlen"
                icon={<Zap size={20} />}
                count={personalizedVideos.length}
              />
              <ContentRow
                videos={personalizedVideos}
                onPlay={openPlayer}
                showExplanation={true}
                explainer={explainRecommendation}
                cardSize="medium"
              />
            </section>
          )}

          {/* Recent */}
          <section>
            <SectionHeader
              title={t('newAdded')}
              icon={<Calendar size={20} />}
              count={recentVideos.length}
            />
            <ContentRow videos={recentVideos} onPlay={openPlayer} cardSize="medium" />
          </section>

          {/* Categories */}
          {CATEGORIES.filter((cat) => videosByCategory[cat.id]?.length > 0)
            .filter((cat) => !selectedCategory || cat.id === selectedCategory)
            .map((category) => (
              <section key={category.id}>
                <SectionHeader
                  title={category.label}
                  icon={
                    typeof category.icon === 'string' ? <span>{category.icon}</span> : category.icon
                  }
                  count={videosByCategory[category.id].length}
                />
                <ContentRow
                  videos={videosByCategory[category.id]}
                  onPlay={openPlayer}
                  cardSize="medium"
                />
              </section>
            ))}
        </main>
      </div>

      {/* FOOTER */}
      <FooterSection />
    </div>
  );
}

/* ========== SKELETON LOADERS ========== */
function SkeletonPulse({ className }) {
  return <div className={cn('animate-pulse bg-white/5 rounded', className)} />;
}

function HeroSkeleton() {
  return (
    <div className="relative w-full h-[70vh] md:h-[75vh] lg:h-[80vh] bg-retro-darker">
      {/* Background shimmer */}
      <div className="absolute inset-0 bg-gradient-to-r from-retro-black via-retro-darker to-retro-black" />

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-r from-retro-black via-retro-black/60 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-transparent to-transparent" />

      {/* Content skeleton */}
      <div className="absolute inset-0 flex items-center">
        <div className="w-full max-w-2xl px-8 md:px-12 lg:px-16">
          {/* Badge skeleton */}
          <SkeletonPulse className="w-24 h-8 rounded-full mb-4" />

          {/* Title skeleton */}
          <SkeletonPulse className="w-3/4 h-12 md:h-16 mb-4" />
          <SkeletonPulse className="w-1/2 h-12 md:h-16 mb-6" />

          {/* Meta skeleton */}
          <div className="flex gap-4 mb-6">
            <SkeletonPulse className="w-16 h-6" />
            <SkeletonPulse className="w-20 h-6" />
            <SkeletonPulse className="w-24 h-6" />
          </div>

          {/* Buttons skeleton */}
          <div className="flex gap-4">
            <SkeletonPulse className="w-36 h-14 rounded-lg" />
            <SkeletonPulse className="w-32 h-14 rounded-lg" />
          </div>
        </div>
      </div>

      {/* Progress bar skeleton */}
      <div className="absolute bottom-8 left-8 md:left-12 flex gap-2">
        {[...Array(5)].map((_, i) => (
          <SkeletonPulse key={i} className="w-8 h-1.5 rounded-full" />
        ))}
      </div>
    </div>
  );
}

function VideoCardSkeleton() {
  return (
    <div className="flex-shrink-0 w-[200px] md:w-[240px] lg:w-[280px]">
      <SkeletonPulse className="aspect-video rounded-lg mb-2" />
      <SkeletonPulse className="w-3/4 h-4 mb-1" />
      <SkeletonPulse className="w-1/2 h-3" />
    </div>
  );
}

function ContentRowSkeleton() {
  return (
    <div className="mb-10">
      {/* Section header */}
      <div className="flex items-center gap-3 mb-5 pb-3 border-b border-accent-gold/10">
        <SkeletonPulse className="w-6 h-6 rounded" />
        <SkeletonPulse className="w-40 h-6" />
      </div>

      {/* Cards row */}
      <div className="flex gap-4 overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <VideoCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

function CategoryFilterSkeleton() {
  return (
    <div className="flex gap-2 overflow-hidden py-4 border-b border-white/5">
      {[...Array(8)].map((_, i) => (
        <SkeletonPulse key={i} className="w-32 h-10 rounded-full flex-shrink-0" />
      ))}
    </div>
  );
}

function MediathekSkeleton() {
  return (
    <div className="min-h-screen bg-retro-black text-white">
      {/* Hero Skeleton */}
      <HeroSkeleton />

      {/* Main Content */}
      <div className="px-4 md:px-8 py-8 space-y-12">
        {/* Category Filter Skeleton */}
        <CategoryFilterSkeleton />

        {/* Hybrid AI Row */}
        <ContentRowSkeleton />

        {/* Continue Watching Row */}
        <ContentRowSkeleton />

        {/* Recent Row */}
        <ContentRowSkeleton />

        {/* Category Rows */}
        <ContentRowSkeleton />
        <ContentRowSkeleton />
      </div>
    </div>
  );
}

/* ========== HERO BILLBOARD - Netflix/Disney+ Cinematic Style ========== */
function HeroCarousel({ videos, onPlay, t }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const timeoutRef = useRef(null);

  const goToSlide = useCallback(
    (index) => {
      if (isTransitioning) return;
      setIsTransitioning(true);
      setCurrentIndex(index);
      setTimeout(() => setIsTransitioning(false), 600);
    },
    [isTransitioning]
  );

  const nextSlide = useCallback(() => {
    goToSlide((currentIndex + 1) % videos.length);
  }, [currentIndex, videos.length, goToSlide]);

  const prevSlide = useCallback(() => {
    goToSlide((currentIndex - 1 + videos.length) % videos.length);
  }, [currentIndex, videos.length, goToSlide]);

  // Auto-rotate every 8 seconds
  useEffect(() => {
    if (!isAutoPlaying) return;
    timeoutRef.current = setTimeout(nextSlide, 8000);
    return () => clearTimeout(timeoutRef.current);
  }, [currentIndex, isAutoPlaying, nextSlide]);

  const currentVideo = videos[currentIndex];

  // Get display title (custom or cleaned YouTube)
  const getDisplayTitle = (video) => {
    return video.customTitle || cleanTitle(video.title);
  };

  return (
    <section
      className="relative w-full h-[70vh] md:h-[75vh] lg:h-[80vh] overflow-hidden"
      onMouseEnter={() => setIsAutoPlaying(false)}
      onMouseLeave={() => setIsAutoPlaying(true)}
    >
      {/* Full-Bleed Background Image */}
      <div className="absolute inset-0">
        <img
          key={currentVideo.id || currentVideo.ytId}
          src={
            currentVideo.customThumbnail ||
            currentVideo.thumbnailUrl ||
            `https://img.youtube.com/vi/${currentVideo.ytId}/maxresdefault.jpg`
          }
          alt=""
          className={cn(
            'w-full h-full object-cover transition-all duration-700',
            isTransitioning ? 'scale-105 opacity-80' : 'scale-100 opacity-100'
          )}
        />
      </div>

      {/* Cinematic Gradient Overlays */}
      <div className="absolute inset-0 bg-gradient-to-r from-retro-black via-retro-black/60 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-retro-black/20 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-b from-retro-black/40 via-transparent to-transparent" />

      {/* Content - Left Aligned */}
      <div className="absolute inset-0 flex items-center">
        <div className="w-full max-w-2xl px-8 md:px-12 lg:px-16">
          {/* Featured Badge */}
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-accent-gold/20 backdrop-blur-sm rounded-full border border-accent-gold/30">
              <Star size={14} className="text-accent-gold" fill="currentColor" />
              <span className="text-accent-gold font-semibold text-xs uppercase tracking-wider">
                Top {currentIndex + 1}
              </span>
            </div>
            {/* 8K Badge entfernt - alles ist 8K Standard */}
          </div>

          {/* Title - Large & Cinematic */}
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-display font-bold text-white mb-4 leading-tight drop-shadow-2xl">
            {getDisplayTitle(currentVideo)}
          </h1>

          {/* Meta Row */}
          <div className="flex flex-wrap items-center gap-3 md:gap-4 mb-6 text-sm md:text-base">
            {currentVideo.year && (
              <span className="text-accent-gold font-semibold">{currentVideo.year}</span>
            )}
            {currentVideo.duration && (
              <span className="text-white/80 flex items-center gap-1.5">
                <Clock size={14} />
                {formatDuration(currentVideo.duration)}
              </span>
            )}
            {currentVideo.category && (
              <span className="text-white/60 uppercase tracking-wider text-xs">
                {getCategoryInfo(currentVideo.category)?.label}
              </span>
            )}
          </div>

          {/* Description (if available) */}
          {currentVideo.description && (
            <p className="text-white/70 text-sm md:text-base mb-6 line-clamp-2 max-w-xl">
              {currentVideo.customDescription || currentVideo.description}
            </p>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => onPlay(currentVideo)}
              className="inline-flex items-center gap-3 px-8 py-4 bg-white text-black font-bold rounded-lg hover:bg-white/90 transition-all transform hover:scale-105 shadow-2xl"
            >
              <Play size={22} fill="currentColor" />
              <span className="text-lg">{t('play')}</span>
            </button>
            <button className="inline-flex items-center gap-2 px-6 py-4 bg-white/20 backdrop-blur-sm text-white font-semibold rounded-lg hover:bg-white/30 transition-all border border-white/20">
              <Info size={20} />
              <span className="hidden md:inline">{t('moreInfo') || 'Mehr Info'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Arrows - Edge Positioned */}
      <button
        onClick={prevSlide}
        className="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 p-3 md:p-4 rounded-full bg-black/40 text-white hover:bg-white hover:text-black transition-all backdrop-blur-sm opacity-0 hover:opacity-100 focus:opacity-100 group-hover:opacity-100"
        style={{ opacity: 0.7 }}
      >
        <ChevronLeft size={28} />
      </button>
      <button
        onClick={nextSlide}
        className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2 p-3 md:p-4 rounded-full bg-black/40 text-white hover:bg-white hover:text-black transition-all backdrop-blur-sm opacity-0 hover:opacity-100 focus:opacity-100 group-hover:opacity-100"
        style={{ opacity: 0.7 }}
      >
        <ChevronRight size={28} />
      </button>

      {/* Bottom Bar - Progress Indicators */}
      <div className="absolute bottom-8 left-8 md:left-12 lg:left-16 right-8 md:right-12">
        <div className="flex items-center gap-6">
          {/* Thumbnail Pills */}
          <div className="flex gap-2">
            {videos.map((video, index) => (
              <button
                key={video.id || video.ytId}
                onClick={() => goToSlide(index)}
                className={cn(
                  'relative h-1 rounded-full transition-all duration-500 overflow-hidden',
                  index === currentIndex ? 'w-12 bg-white' : 'w-6 bg-white/30 hover:bg-white/50'
                )}
              >
                {index === currentIndex && isAutoPlaying && (
                  <div
                    className="absolute inset-0 bg-accent-gold origin-left"
                    style={{
                      animation: 'progress 8s linear',
                    }}
                  />
                )}
              </button>
            ))}
          </div>

          {/* Video Counter */}
          <span className="text-white/50 text-sm font-mono">
            {String(currentIndex + 1).padStart(2, '0')} / {String(videos.length).padStart(2, '0')}
          </span>
        </div>
      </div>

      {/* Animated Progress Bar Keyframes */}
      <style>{`
        @keyframes progress {
          from { transform: scaleX(0); }
          to { transform: scaleX(1); }
        }
      `}</style>
    </section>
  );
}

/* ========== SECTION HEADER ========== */
function SectionHeader({ title, icon, count }) {
  return (
    <div className="flex items-center gap-3 mb-5 pb-3 border-b border-accent-gold/10">
      {icon && <div className="text-accent-gold">{icon}</div>}
      <h2 className="text-xl font-bold text-white flex-1">{title}</h2>
      {count !== undefined && <span className="text-sm text-retro-muted/60">{count} Videos</span>}
    </div>
  );
}

/* ========== CONTENT ROW - Carousel ========== */
function ContentRow({
  videos,
  onPlay,
  showProgress = false,
  showExplanation = false,
  explainer,
  cardSize = 'medium',
}) {
  const rowRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const scroll = (dir) => {
    if (!rowRef.current) return;
    const amount = rowRef.current.clientWidth * 0.75;
    rowRef.current.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' });
  };

  const checkScroll = () => {
    if (!rowRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = rowRef.current;
    setCanScrollLeft(scrollLeft > 10);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
  };

  if (!videos?.length) return null;

  return (
    <div className="group/row">
      {/* Carousel Container */}
      <div className="relative">
        {/* Left Arrow */}
        <button
          onClick={() => scroll('left')}
          className={cn(
            'absolute left-0 top-0 bottom-0 z-20 w-12 flex items-center justify-center',
            'bg-gradient-to-r from-retro-black to-transparent',
            'opacity-0 group-hover/row:opacity-100 transition-opacity',
            'hover:text-accent-gold text-white',
            !canScrollLeft && 'hidden'
          )}
          aria-label="Zurück"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>

        {/* Right Arrow */}
        <button
          onClick={() => scroll('right')}
          className={cn(
            'absolute right-0 top-0 bottom-0 z-20 w-12 flex items-center justify-center',
            'bg-gradient-to-l from-retro-black to-transparent',
            'opacity-0 group-hover/row:opacity-100 transition-opacity',
            'hover:text-accent-gold text-white',
            !canScrollRight && 'hidden'
          )}
          aria-label="Vorwärts"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Scrollable Row */}
        <div
          ref={rowRef}
          onScroll={checkScroll}
          className="flex gap-3 md:gap-4 overflow-x-auto pb-4 scroll-smooth scrollbar-hide"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {videos.slice(0, 20).map((video) => (
            <VideoCard
              key={video.id || video.ytId}
              video={video}
              onPlay={onPlay}
              showProgress={showProgress}
              showExplanation={showExplanation}
              explainer={explainer}
              size={cardSize}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ========== VIDEO CARD ========== */
function VideoCard({
  video,
  onPlay,
  showProgress = false,
  showExplanation = false,
  explainer,
  size = 'medium',
}) {
  const [hovered, setHovered] = useState(false);
  const explanation = showExplanation && explainer ? explainer(video) : null;

  const sizeClasses = {
    small: 'w-[140px] md:w-[160px] aspect-video',
    medium: 'w-[160px] md:w-[200px] lg:w-[240px] aspect-video',
    large: 'w-[200px] md:w-[280px] lg:w-[360px] aspect-video',
  };

  return (
    <button
      onClick={() => onPlay(video)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={cn(
        'flex-shrink-0',
        sizeClasses[size],
        'rounded-lg overflow-hidden bg-retro-dark relative',
        'transition-all duration-300 ease-out',
        'border-2 border-transparent',
        hovered && 'border-accent-gold shadow-lg shadow-accent-gold/20 scale-105 z-10',
        'focus:outline-none focus:border-accent-gold'
      )}
    >
      {/* Thumbnail */}
      <img
        src={video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'medium')}
        alt={cleanTitle(video.title)}
        className="w-full h-full object-cover"
        loading="lazy"
      />

      {/* Category Badge - Top Left */}
      {video.category &&
        (() => {
          const cat = getCategoryInfo(video.category);
          return cat ? (
            <div
              className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide shadow-md"
              style={{
                backgroundColor: cat.hex || '#d4af37',
                color: cat.hex === '#ffd600' ? '#000' : '#fff',
              }}
            >
              {cat.icon} {cat.label.split(' ')[0]}
            </div>
          ) : null;
        })()}

      {/* Progress Bar */}
      {showProgress && video.progress > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/50">
          <div className="h-full bg-accent-gold" style={{ width: `${video.progress}%` }} />
        </div>
      )}

      {/* Hover Overlay */}
      <div
        className={cn(
          'absolute inset-0 flex flex-col justify-end p-3',
          'bg-gradient-to-t from-black/95 via-black/50 to-transparent',
          'transition-opacity duration-200',
          hovered ? 'opacity-100' : 'opacity-0'
        )}
      >
        {/* Play Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 md:w-14 md:h-14 rounded-full bg-accent-gold flex items-center justify-center shadow-xl shadow-accent-gold/30 transform transition-transform hover:scale-110">
            <Play className="w-6 h-6 md:w-7 md:h-7 text-black ml-1" fill="black" />
          </div>
        </div>

        {/* Metadata */}
        <div className="relative z-10 space-y-1">
          <p className="text-xs md:text-sm font-medium line-clamp-2 text-white">
            {cleanTitle(video.title)}
          </p>
          <div className="text-[10px] text-accent-gold/80 flex gap-2">
            {video.year && <span>{video.year}</span>}
            {video.duration && <span>{formatDuration(video.duration)}</span>}
          </div>
          {explanation && (
            <div className="text-[9px] text-accent-amber/90 line-clamp-1 mt-1">{explanation}</div>
          )}
        </div>
      </div>

      {/* Quality Badge entfernt - alles ist 8K, daher kein Spam-Badge nötig */}
    </button>
  );
}

/* ========== FOOTER SECTION ========== */
function FooterSection() {
  return null; // Use global site footer only
}
