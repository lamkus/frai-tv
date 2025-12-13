import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Play,
  Film,
  Settings,
  Clock,
  TrendingUp,
  Bookmark,
  Sparkles,
  ChevronRight,
  Eye,
  Star,
  Zap,
  Info,
} from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { CATEGORIES } from '../../data/remaikeData';
import useVideoI18n from '../../lib/useVideoI18n';

// Helper: Get category color from ID or label
function getCategoryColor(category) {
  if (!category) return '#d4af37'; // Default gold
  const cat = CATEGORIES.find((c) => c.id === category || c.label === category);
  return cat?.hex || '#d4af37';
}

/**
 * DashboardGrid - TV Mediathek DELUXE Style
 *
 * Features:
 * - Glass-morphism cards with real video thumbnails
 * - Gold accent highlights with neon glow
 * - Animated hover effects with scale & glow
 * - Click ripple effects
 * - Category corner effects
 * - Responsive grid layout
 */
export default function DashboardGrid({ featuredVideo, recentVideos = [], categories = [] }) {
  const { videos, openPlayer, openInfoModal } = useApp();

  // Get actual videos for the grid
  const gridVideos = videos?.slice(0, 12) || [];
  const heroVideo = featuredVideo || gridVideos[0];
  const sideVideos = recentVideos.length > 0 ? recentVideos : gridVideos.slice(1, 6);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Hero Section - Featured Video */}
      {heroVideo && (
        <section className="mb-8">
          <HeroCard video={heroVideo} onPlay={() => openPlayer(heroVideo)} />
        </section>
      )}

      {/* Video Grid - Echte Videos */}
      <section>
        <SectionHeader icon={TrendingUp} title="Neueste Videos" link="/browse" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {sideVideos.map((video, index) => (
            <VideoCard
              key={video?.id || video?.ytId || index}
              video={video}
              index={index}
              onPlay={() => video && openPlayer(video)}
              onInfo={() => video && openInfoModal(video)}
            />
          ))}
        </div>
      </section>

      {/* Quick Actions Grid */}
      <section>
        <SectionHeader icon={Zap} title="Schnellzugriff" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <QuickActionCard
            title="Alle Videos"
            icon={Film}
            link="/browse"
            color="gold"
            count={videos?.length || 0}
          />
          <QuickActionCard title="Weiterschauen" icon={Clock} link="/history" color="purple" />
          <QuickActionCard title="Watchlist" icon={Bookmark} link="/watchlist" color="cyan" />
          <QuickActionCard title="Einstellungen" icon={Settings} link="/settings" color="gray" />
        </div>
      </section>

      {/* Categories with Icons */}
      {categories.length > 0 && (
        <section>
          <SectionHeader icon={Sparkles} title="Kategorien" link="/browse" />
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {categories.slice(0, 7).map((cat, index) => (
              <CategoryCard key={cat.id || cat.name || index} category={cat} />
            ))}
          </div>
        </section>
      )}

      {/* More Videos Row */}
      {gridVideos.length > 6 && (
        <section>
          <SectionHeader icon={Star} title="Empfohlen" link="/browse?sort=popular" />
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {gridVideos.slice(6, 12).map((video, index) => (
              <VideoCard
                key={video?.id || video?.ytId || `more-${index}`}
                video={video}
                index={index + 6}
                variant="compact"
                onPlay={() => video && openPlayer(video)}
                onInfo={() => video && openInfoModal(video)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

/**
 * Section Header Component
 */
function SectionHeader({ icon: Icon, title, link }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-xl font-display text-white flex items-center gap-2">
        {Icon && <Icon size={20} className="text-accent-gold" />}
        <span>{title}</span>
      </h2>
      {link && (
        <Link
          to={link}
          className="text-sm text-retro-muted hover:text-accent-gold transition-colors flex items-center gap-1 group"
        >
          Alle anzeigen
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      )}
    </div>
  );
}

/**
 * Hero Card - Large Featured Video
 */
function HeroCard({ video, onPlay }) {
  const [isHovered, setIsHovered] = useState(false);
  const { getVideoText } = useVideoI18n();

  // Early return AFTER all hooks
  if (!video) return null;

  const { title, description } = getVideoText(video);
  const thumbnail = video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'maxres');

  return (
    <div
      className={cn(
        'relative rounded-3xl overflow-hidden cursor-pointer group',
        'border border-white/10 hover:border-accent-gold/50',
        'transition-all duration-500 ease-out',
        'hover:shadow-2xl hover:shadow-accent-gold/20',
        'transform hover:scale-[1.01]'
      )}
      onClick={onPlay}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background Thumbnail */}
      <div className="relative aspect-[21/9] sm:aspect-[21/7]">
        <img
          src={thumbnail}
          alt={title}
          className={cn(
            'w-full h-full object-cover transition-all duration-700',
            isHovered ? 'scale-105 brightness-75' : 'scale-100 brightness-50'
          )}
        />

        {/* Gradient Overlays */}
        <div className="absolute inset-0 bg-gradient-to-r from-retro-black via-retro-black/60 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-transparent to-transparent" />

        {/* Animated Border Glow */}
        <div
          className={cn(
            'absolute inset-0 rounded-3xl transition-opacity duration-500',
            'bg-gradient-to-r from-accent-gold/20 via-transparent to-accent-gold/20',
            isHovered ? 'opacity-100' : 'opacity-0'
          )}
        />
      </div>

      {/* Content */}
      <div className="absolute inset-0 p-6 sm:p-8 flex flex-col justify-end">
        {/* Badge */}
        <div className="flex items-center gap-2 mb-3">
          <span className="px-3 py-1 bg-accent-gold/90 text-retro-black text-xs font-bold rounded-full flex items-center gap-1">
            <Sparkles size={12} />
            FEATURED
          </span>
          {video.duration && (
            <span className="px-2 py-1 bg-retro-black/60 text-white text-xs rounded-full">
              {formatDuration(video.duration)}
            </span>
          )}
        </div>

        {/* Title */}
        <h2
          className={cn(
            'text-2xl sm:text-3xl lg:text-4xl font-display text-white mb-2',
            'line-clamp-2 transition-colors duration-300',
            isHovered && 'text-accent-gold'
          )}
        >
          {title}
        </h2>

        {/* Description */}
        {description && (
          <p className="text-retro-muted text-sm sm:text-base line-clamp-2 max-w-2xl mb-4">
            {description}
          </p>
        )}

        {/* Stats & Play Button */}
        <div className="flex items-center gap-4">
          <button
            className={cn(
              'flex items-center gap-2 px-6 py-3 rounded-full',
              'bg-accent-gold text-retro-black font-bold',
              'hover:bg-accent-amber transition-all duration-300',
              'transform hover:scale-105 active:scale-95',
              'shadow-lg shadow-accent-gold/30'
            )}
          >
            <Play size={20} fill="currentColor" />
            Jetzt ansehen
          </button>

          {video.viewCount && (
            <span className="flex items-center gap-1 text-retro-muted text-sm">
              <Eye size={14} />
              {Number(video.viewCount).toLocaleString('de-DE')} Views
            </span>
          )}
        </div>
      </div>

      {/* Play Icon Overlay */}
      <div
        className={cn(
          'absolute inset-0 flex items-center justify-center pointer-events-none',
          'transition-opacity duration-300',
          isHovered ? 'opacity-100' : 'opacity-0'
        )}
      >
        <div className="w-20 h-20 rounded-full bg-accent-gold/90 flex items-center justify-center animate-pulse">
          <Play size={36} fill="white" className="text-white ml-1" />
        </div>
      </div>
    </div>
  );
}

/**
 * Video Card - Individual Video Thumbnail
 */
function VideoCard({ video, index, variant = 'default', onPlay, onInfo }) {
  const [isHovered, setIsHovered] = useState(false);
  const [ripple, setRipple] = useState(null);
  const cardRef = useRef(null);
  const { getVideoText } = useVideoI18n();

  // Early return AFTER all hooks
  if (!video) return null;

  const { title } = getVideoText(video);
  const thumbnail = video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'high');
  const categoryColor = getCategoryColor(video.category);

  // Click ripple effect
  const handleClick = (e) => {
    const rect = cardRef.current?.getBoundingClientRect();
    if (rect) {
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setRipple({ x, y });
      setTimeout(() => setRipple(null), 600);
    }
    onPlay?.();
  };

  return (
    <div
      ref={cardRef}
      className={cn(
        'relative rounded-xl overflow-hidden cursor-pointer group',
        'border border-white/5 hover:border-accent-gold/40',
        'transition-all duration-300 ease-out',
        'hover:shadow-xl hover:shadow-accent-gold/10',
        'transform hover:scale-[1.03] hover:-translate-y-1',
        variant === 'compact' ? 'aspect-video' : 'aspect-[16/10]'
      )}
      style={{
        animationDelay: `${index * 50}ms`,
      }}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Thumbnail */}
      <img
        src={thumbnail}
        alt={title}
        className={cn(
          'w-full h-full object-cover transition-all duration-500',
          isHovered ? 'scale-110 brightness-75' : 'scale-100'
        )}
        loading="lazy"
      />

      {/* Category Corner Effect */}
      <div
        className="absolute top-0 right-0 w-0 h-0 transition-all duration-300"
        style={{
          borderLeft: '24px solid transparent',
          borderTop: `24px solid ${categoryColor}`,
          opacity: isHovered ? 1 : 0.7,
        }}
      />

      {/* Gradient Overlay */}
      <div
        className={cn(
          'absolute inset-0 transition-opacity duration-300',
          'bg-gradient-to-t from-retro-black via-retro-black/40 to-transparent',
          isHovered ? 'opacity-90' : 'opacity-70'
        )}
      />

      {/* Duration Badge */}
      {video.duration && (
        <span className="absolute top-2 left-2 px-2 py-0.5 bg-retro-black/80 text-white text-xs rounded font-mono">
          {formatDuration(video.duration)}
        </span>
      )}

      {/* Content */}
      <div className="absolute bottom-0 left-0 right-0 p-3">
        <h3
          className={cn(
            'text-sm font-medium text-white line-clamp-2 transition-colors',
            isHovered && 'text-accent-gold'
          )}
        >
          {title}
        </h3>

        {variant !== 'compact' && video.viewCount && (
          <div className="flex items-center gap-2 mt-1 text-xs text-retro-muted">
            <Eye size={12} />
            <span>{Number(video.viewCount).toLocaleString('de-DE')}</span>
          </div>
        )}
      </div>

      {/* Play Icon */}
      <div
        className={cn(
          'absolute inset-0 flex items-center justify-center gap-3',
          'transition-all duration-300',
          isHovered ? 'opacity-100' : 'opacity-0'
        )}
      >
        {/* Info Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onInfo?.();
          }}
          className={cn(
            'w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center',
            'hover:bg-white/40 transition-all duration-300',
            'transform',
            isHovered ? 'scale-100' : 'scale-75'
          )}
          aria-label="Mehr Infos"
        >
          <Info size={16} className="text-white" />
        </button>

        {/* Play Button */}
        <div
          className={cn(
            'w-12 h-12 rounded-full bg-accent-gold/90 flex items-center justify-center',
            'transform transition-transform duration-300',
            isHovered ? 'scale-100' : 'scale-75'
          )}
        >
          <Play size={20} fill="white" className="text-white ml-0.5" />
        </div>
      </div>

      {/* Click Ripple */}
      {ripple && (
        <span
          className="absolute rounded-full bg-white/30 animate-ripple pointer-events-none"
          style={{
            left: ripple.x - 50,
            top: ripple.y - 50,
            width: 100,
            height: 100,
          }}
        />
      )}

      {/* Hover Glow Border */}
      <div
        className={cn(
          'absolute inset-0 rounded-xl pointer-events-none transition-opacity duration-300',
          'ring-2 ring-inset ring-accent-gold/0',
          isHovered && 'ring-accent-gold/50'
        )}
      />
    </div>
  );
}

/**
 * Quick Action Card
 */
function QuickActionCard({ title, icon: Icon, link, color = 'gold', count }) {
  const [isHovered, setIsHovered] = useState(false);

  const colorClasses = {
    gold: 'from-accent-gold/20 to-accent-gold/5 hover:border-accent-gold/50 hover:shadow-accent-gold/20',
    purple:
      'from-accent-purple/20 to-accent-purple/5 hover:border-accent-purple/50 hover:shadow-accent-purple/20',
    cyan: 'from-accent-cyan/20 to-accent-cyan/5 hover:border-accent-cyan/50 hover:shadow-accent-cyan/20',
    gray: 'from-retro-gray/20 to-retro-gray/5 hover:border-retro-light/50 hover:shadow-retro-light/20',
  };

  const iconColors = {
    gold: 'text-accent-gold',
    purple: 'text-accent-purple',
    cyan: 'text-accent-cyan',
    gray: 'text-retro-light',
  };

  return (
    <Link
      to={link}
      className={cn(
        'relative p-5 rounded-2xl overflow-hidden group',
        'bg-gradient-to-br border border-white/5',
        'transition-all duration-300 ease-out',
        'hover:shadow-xl transform hover:scale-[1.02]',
        colorClasses[color]
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background Glow */}
      <div
        className={cn(
          'absolute inset-0 opacity-0 transition-opacity duration-300',
          'bg-gradient-to-br from-white/5 to-transparent',
          isHovered && 'opacity-100'
        )}
      />

      {/* Content */}
      <div className="relative z-10">
        <Icon
          size={28}
          className={cn(
            'mb-3 transition-transform duration-300',
            iconColors[color],
            isHovered && 'scale-110'
          )}
        />
        <h3 className="text-white font-medium">{title}</h3>
        {count !== undefined && <p className="text-retro-muted text-sm mt-1">{count} Videos</p>}
      </div>

      {/* Arrow */}
      <ChevronRight
        size={18}
        className={cn(
          'absolute bottom-4 right-4 text-retro-muted transition-all duration-300',
          isHovered && 'text-white translate-x-1'
        )}
      />
    </Link>
  );
}

/**
 * Category Card
 */
function CategoryCard({ category }) {
  const [isHovered, setIsHovered] = useState(false);
  const categoryColor = category.hex || getCategoryColor(category.id || category.label);

  return (
    <Link
      to={`/browse?category=${encodeURIComponent(category.name || category.label)}`}
      className={cn(
        'relative p-4 rounded-xl text-center overflow-hidden group',
        'bg-gradient-to-br from-retro-dark/80 to-retro-darker/60',
        'border border-white/5 hover:border-accent-gold/30',
        'transition-all duration-300',
        'hover:shadow-lg transform hover:scale-[1.03]'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Category Color Accent */}
      <div
        className="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
        style={{
          backgroundColor: categoryColor,
          opacity: isHovered ? 1 : 0.5,
        }}
      />

      <span className="text-2xl mb-2 block">{category.icon || '📁'}</span>
      <span className={cn('text-sm text-retro-muted transition-colors', isHovered && 'text-white')}>
        {category.label || category.name}
      </span>

      {category.videos?.length > 0 && (
        <span className="block text-xs text-retro-muted/60 mt-1">
          {category.videos.length} Videos
        </span>
      )}
    </Link>
  );
}

export { VideoCard, HeroCard, QuickActionCard, CategoryCard };
