import { useState } from 'react';
import { X, Play, Plus, Check, Calendar, Clock, Eye, Share2 } from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { CATEGORIES } from '../../data/remaikeData';
import { ShareModal } from '../ui';
import { useVideoI18n } from '../../lib/useVideoI18n';

/**
 * VideoInfoModal - FRai.TV Style Video Detail Popup
 *
 * Zeigt detaillierte Informationen zu einem Video an.
 * Inspiriert vom Netflix "More Info" Dialog.
 *
 * Features:
 * - Großes Thumbnail mit Play-Button
 * - Video-Metadaten (Jahr, Dauer, Kategorie)
 * - Beschreibung
 * - Zur Watchlist hinzufügen
 * - Teilen-Funktion
 * - YouTube-Link
 */
export default function VideoInfoModal({ video, isOpen, onClose }) {
  const { openPlayer, addToWatchlist, removeFromWatchlist, isInWatchlist } = useApp();
  const [isShareOpen, setIsShareOpen] = useState(false);

  // i18n für mehrsprachige Titel/Beschreibungen
  const { getVideoText } = useVideoI18n();

  if (!isOpen || !video) return null;

  const { id, ytId, duration, category, year, viewCount, thumbnailUrl } = video;
  // Lokalisierte Texte
  const { title, description } = getVideoText(video);

  const inWatchlist = isInWatchlist(id);
  const thumbnail = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');

  // Get category info
  const categoryData = CATEGORIES.find((c) => c.id === category || c.label === category);
  const categoryColor = categoryData?.hex || '#d4af37';

  const handlePlay = () => {
    onClose();
    openPlayer(video);
  };

  const handleWatchlist = () => {
    if (inWatchlist) {
      removeFromWatchlist(id);
    } else {
      addToWatchlist(id);
    }
  };

  const handleShare = () => {
    setIsShareOpen(true);
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4 animate-fade-in"
      style={{
        background: 'linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(10,10,20,0.98) 100%)',
        backdropFilter: 'blur(12px)',
      }}
      onClick={handleBackdropClick}
    >
      <div
        className="relative w-full max-w-2xl rounded-2xl overflow-hidden animate-scale-in"
        style={{
          background: 'linear-gradient(180deg, rgba(26,26,36,0.98) 0%, rgba(18,18,26,0.99) 100%)',
          border: '1px solid rgba(212, 175, 55, 0.2)',
          boxShadow:
            '0 0 0 1px rgba(255,255,255,0.05), 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 100px -20px rgba(212, 175, 55, 0.2)',
        }}
      >
        {/* Gold/Red accent line */}
        <div
          className="absolute top-0 left-0 right-0 h-1"
          style={{
            background: `linear-gradient(90deg, #e50914 0%, ${categoryColor} 50%, #e50914 100%)`,
          }}
        />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-black/60 hover:bg-black/80 text-white transition-colors"
          aria-label="Schließen"
        >
          <X size={20} />
        </button>

        {/* Thumbnail with Play Button */}
        <div className="relative aspect-video">
          <img src={thumbnail} alt={title} className="w-full h-full object-cover" />

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

          {/* Category Badge */}
          {categoryData && (
            <div
              className="absolute top-4 left-4 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5"
              style={{
                backgroundColor: `${categoryColor}20`,
                color: categoryColor,
                border: `1px solid ${categoryColor}50`,
              }}
            >
              <span>{categoryData.icon}</span>
              <span>{categoryData.label}</span>
            </div>
          )}

          {/* Play Button */}
          <button
            onClick={handlePlay}
            className="absolute inset-0 flex items-center justify-center group"
          >
            <div className="w-20 h-20 rounded-full bg-accent-gold flex items-center justify-center transform group-hover:scale-110 transition-all shadow-2xl ring-1 ring-accent-gold/30">
              <Play size={36} className="text-black ml-1" fill="currentColor" />
            </div>
          </button>

          {/* Bottom Info Overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 drop-shadow-lg">
              {title}
            </h2>

            {/* Meta Info */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-300">
              {year && (
                <span className="flex items-center gap-1">
                  <Calendar size={14} />
                  {year}
                </span>
              )}
              {duration && (
                <span className="flex items-center gap-1">
                  <Clock size={14} />
                  {formatDuration(duration)}
                </span>
              )}
              {viewCount && (
                <span className="flex items-center gap-1">
                  <Eye size={14} />
                  {viewCount.toLocaleString('de-DE')} Views
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Content Section */}
        <div className="p-6">
          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 mb-6">
            <button
              onClick={handlePlay}
              className="flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-accent-gold to-accent-amber hover:from-accent-amber hover:to-accent-gold text-retro-black font-semibold transition-all shadow-lg shadow-accent-gold/30 border border-accent-gold/30"
            >
              <Play size={18} fill="currentColor" />
              Abspielen
            </button>

            <button
              onClick={handleWatchlist}
              className={cn(
                'flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-all border',
                inWatchlist
                  ? 'bg-accent-gold/20 border-accent-gold/50 text-accent-gold'
                  : 'bg-retro-gray/30 border-retro-gray/50 text-white hover:border-accent-gold/50'
              )}
            >
              {inWatchlist ? <Check size={18} /> : <Plus size={18} />}
              {inWatchlist ? 'Auf Merkliste' : 'Merken'}
            </button>

            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-4 py-3 rounded-lg bg-retro-gray/30 border border-retro-gray/50 text-white hover:border-accent-cyan/50 font-medium transition-all"
            >
              <Share2 size={18} />
              Teilen
            </button>
          </div>

          {/* Description */}
          {description && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-retro-muted mb-2 uppercase tracking-wider">
                Beschreibung
              </h3>
              <p className="text-gray-300 leading-relaxed">{description}</p>
            </div>
          )}
        </div>
      </div>

      {/* Share Modal */}
      <ShareModal isOpen={isShareOpen} onClose={() => setIsShareOpen(false)} video={video} />
    </div>
  );
}
