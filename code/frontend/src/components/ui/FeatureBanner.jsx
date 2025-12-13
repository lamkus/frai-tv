import { Link } from 'react-router-dom';
import { Play, Sparkles } from 'lucide-react';
import { cn, getYouTubeThumbnail } from '../../lib/utils';

/**
 * FeatureBanner - Large promotional banner (frai.tv style)
 *
 * Features:
 * - Full-width gradient background
 * - CTA button
 * - Featured content preview
 */
export default function FeatureBanner({
  title = 'Retro Tech History Archive',
  subtitle = 'DIE GESCHICHTE DER TECHNIK NEU ERLEBEN',
  ctaText = 'JETZT ENTDECKEN',
  ctaLink = '/browse',
  featuredVideo = null,
  className,
}) {
  const backgroundImage =
    featuredVideo?.thumbnailUrl ||
    (featuredVideo?.ytId ? getYouTubeThumbnail(featuredVideo.ytId, 'maxres') : null);

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-xl mx-4 sm:mx-6 lg:mx-8 mb-8',
        'bg-gradient-to-r from-retro-darker via-retro-dark to-retro-darker',
        'border border-retro-gray/30',
        className
      )}
    >
      {/* Background Image */}
      {backgroundImage && (
        <div className="absolute right-0 top-0 w-1/2 h-full">
          <img src={backgroundImage} alt="" className="w-full h-full object-cover opacity-60" />
          <div className="absolute inset-0 bg-gradient-to-r from-retro-darker via-retro-darker/80 to-transparent" />
        </div>
      )}

      {/* Content */}
      <div className="relative z-10 flex items-center justify-between p-6 sm:p-8 lg:p-12">
        <div className="max-w-md">
          <p className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-2">{subtitle}</p>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">
            <span className="text-accent-amber">rem</span>
            <span className="text-accent-cyan">AI</span>
            <span className="text-accent-amber">ke</span>
            <span className="text-white">.TV</span>
            <span className="text-retro-muted text-lg sm:text-xl ml-2">– {title}</span>
          </h2>

          <Link
            to={ctaLink}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg
                     bg-accent-amber hover:bg-amber-500 
                     text-black font-bold text-sm
                     transition-all shadow-lg hover:shadow-amber-500/30"
          >
            <Play size={18} fill="black" />
            {ctaText}
          </Link>
        </div>

        {/* Decorative Elements */}
        <div className="hidden lg:flex items-center gap-4">
          <div className="text-accent-amber">
            <Sparkles size={48} />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * FeaturedCarousel - Horizontal scrolling featured videos
 */
export function FeaturedCarousel({ videos = [], className }) {
  // Import useApp locally to avoid unused import in main component
  const { useApp } = require('../../context/AppContext');
  const { openPlayer } = useApp();

  if (videos.length === 0) return null;

  return (
    <section className={cn('mb-8', className)}>
      <div className="px-4 sm:px-6 lg:px-8 mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <Sparkles size={20} className="text-accent-amber" />
          Featured
        </h2>
      </div>

      <div className="flex gap-4 overflow-x-auto scrollbar-thin pb-4 px-4 sm:px-6 lg:px-8">
        {videos.slice(0, 6).map((video) => (
          <div
            key={video.id}
            className="relative flex-shrink-0 w-64 sm:w-72 lg:w-80 aspect-video rounded-xl overflow-hidden group cursor-pointer"
            onClick={() => openPlayer(video)}
          >
            <img
              src={video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'maxres')}
              alt={video.title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />

            {/* Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />

            {/* Play Button */}
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center shadow-xl">
                <Play size={28} className="text-black ml-1" fill="black" />
              </div>
            </div>

            {/* Title */}
            <div className="absolute bottom-0 left-0 right-0 p-4">
              <h3 className="text-white font-semibold truncate">{video.title}</h3>
              {video.category && <p className="text-sm text-retro-muted">{video.category}</p>}
            </div>

            {/* Play indicator */}
            <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                <Play size={20} className="text-black ml-0.5" fill="black" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
