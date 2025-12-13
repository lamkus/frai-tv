import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Play, ExternalLink, Youtube, Shield, Eye } from 'lucide-react';
import { cn, getYouTubeEmbedUrl, getYouTubeThumbnail, storage } from '../../lib/utils';
import { getSpotlightVideo } from '../../lib/recommendationEngine';
import { useApp } from '../../context/AppContext';

/**
 * AmbientPlayer - Featured Video with YouTube Disclaimer
 *
 * NO muted autoplay - shows a thumbnail with disclaimer first.
 * User clicks to start video WITH SOUND → generates real YouTube watchtime!
 *
 * Features:
 * - Thumbnail preview with overlay
 * - DSGVO/GDPR compliant disclaimer
 * - Video starts WITH SOUND after consent click
 * - Full YouTube controls enabled
 * - Generates real watchtime for channel
 */
export default function AmbientPlayer({ className }) {
  const { t } = useTranslation();
  const { videos, openPlayer } = useApp();
  const [currentVideo, setCurrentVideo] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasConsent, setHasConsent] = useState(() => storage.get('remaike_allow_youtube', false));

  const containerRef = useRef(null);

  // Select initial spotlight video
  useEffect(() => {
    if (videos.length > 0 && !currentVideo) {
      const spotlight = getSpotlightVideo(videos);
      setCurrentVideo(spotlight);
    }
  }, [videos, currentVideo]);

  // Start video with sound (generates watchtime!)
  const handlePlayClick = () => {
    setHasConsent(true);
    setIsPlaying(true);
    storage.set('remaike_allow_youtube', true);
  };

  // Open in modal player
  const handleOpenModal = () => {
    if (currentVideo) {
      openPlayer(currentVideo);
    }
  };

  // Watch on YouTube directly
  const handleWatchOnYouTube = () => {
    if (currentVideo?.ytId) {
      window.open(`https://www.youtube.com/watch?v=${currentVideo.ytId}`, '_blank');
    }
  };

  if (!currentVideo) return null;

  // Embed URL - NO MUTE, with controls, autoplay only after consent
  const embedUrl = getYouTubeEmbedUrl(currentVideo.ytId, {
    autoplay: true,
    params: {
      mute: '0', // MIT TON für echte Watchtime!
      controls: '1', // YouTube Controls an
      rel: '0',
      modestbranding: '1',
      enablejsapi: '1',
      origin: window.location.origin,
    },
  });

  const thumbnailUrl = getYouTubeThumbnail(currentVideo.ytId, 'maxres');

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative w-full aspect-video bg-retro-darker overflow-hidden rounded-xl',
        'border border-white/10 shadow-2xl shadow-black/50',
        className
      )}
    >
      {isPlaying && hasConsent ? (
        /* YouTube Player - MIT SOUND */
        <iframe
          src={embedUrl}
          title={currentVideo.title}
          className="absolute inset-0 w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          frameBorder="0"
        />
      ) : (
        /* Disclaimer + Thumbnail Preview */
        <>
          {/* Thumbnail Background */}
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${thumbnailUrl})` }}
          />

          {/* Dark Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-black/40" />

          {/* Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
            {/* YouTube Logo & Shield */}
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-red-600 flex items-center justify-center">
                <Youtube size={28} className="text-white" />
              </div>
              <div className="w-12 h-12 rounded-xl bg-green-600/80 flex items-center justify-center">
                <Shield size={24} className="text-white" />
              </div>
            </div>

            {/* Video Title */}
            <h3 className="text-xl sm:text-2xl md:text-3xl font-bold mb-3 line-clamp-2 max-w-2xl">
              {currentVideo.title}
            </h3>

            {/* Category Badge */}
            {currentVideo.category && (
              <span className="px-3 py-1 bg-accent-gold/20 text-accent-gold rounded-full text-sm font-medium mb-4">
                {currentVideo.category}
              </span>
            )}

            {/* GDPR Disclaimer Box - remAIke.IT Premium Gold Style */}
            <div
              className="rounded-xl p-5 max-w-lg mb-5"
              style={{
                background: 'linear-gradient(145deg, #1a1a1c 0%, #0d0d0e 100%)',
                border: '2px solid #c9a962',
                boxShadow: '0 0 40px rgba(201, 169, 98, 0.25), 0 10px 30px rgba(0, 0, 0, 0.5)',
              }}
            >
              {/* Gold Accent Bar */}
              <div
                className="absolute top-0 left-0 right-0 h-1 rounded-t-xl"
                style={{
                  background: 'linear-gradient(90deg, #c9a962 0%, #a8893f 50%, #c9a962 100%)',
                }}
              />

              <p className="text-sm sm:text-base leading-relaxed" style={{ color: '#cccccc' }}>
                <strong style={{ color: '#c9a962' }}>🔒 {t('privacyNotice')}:</strong>{' '}
                {t('youtubeConsentText')}{' '}
                <a
                  href="https://policies.google.com/privacy"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#c9a962', textDecoration: 'underline' }}
                >
                  {t('googlePrivacyPolicy')}
                </a>
                .
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-3">
              {/* Main Play Button */}
              <button
                onClick={handlePlayClick}
                className="group flex items-center gap-3 px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl transition-all transform hover:scale-105 shadow-lg shadow-red-600/30"
              >
                <Play
                  size={24}
                  fill="currentColor"
                  className="group-hover:scale-110 transition-transform"
                />
                <span className="text-lg">{t('startVideo')}</span>
              </button>

              {/* Secondary Options */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleOpenModal}
                  className="flex items-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all border border-white/20"
                  title={t('inPlayer')}
                >
                  <Eye size={18} />
                  <span className="hidden sm:inline">{t('inPlayer')}</span>
                </button>

                <button
                  onClick={handleWatchOnYouTube}
                  className="flex items-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all border border-white/20"
                  title={t('openYouTube')}
                >
                  <ExternalLink size={18} />
                  <span className="hidden sm:inline">{t('openYouTube')}</span>
                </button>
              </div>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center gap-4 mt-5 text-xs text-gray-400">
              <span className="flex items-center gap-1">
                <Shield size={12} className="text-green-500" />
                {t('gdprCompliant')}
              </span>
              <span>•</span>
              <span>youtube-nocookie.com</span>
              <span>•</span>
              <span>{t('noTracking')}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
