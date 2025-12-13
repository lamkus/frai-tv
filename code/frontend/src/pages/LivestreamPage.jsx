import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Radio,
  Users,
  Clock,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  Play,
  Volume2,
} from 'lucide-react';
import { getYouTubeEmbedUrl } from '../lib/utils';
import useMeta from '../lib/useMeta';

/**
 * LivestreamPage - YouTube Live Stream Integration
 *
 * Features:
 * - Show currently live streams from channel
 * - Upcoming scheduled streams
 * - Live viewer count
 * - Chat integration option
 * - Click-to-play with sound (browser autoplay policy)
 */
export default function LivestreamPage() {
  const { t } = useTranslation();
  useMeta({
    title: t('livestreamPage.metaTitle'),
    description: t('livestreamPage.metaDescription'),
  });

  const [liveStreams, setLiveStreams] = useState([]);
  const [upcomingStreams, setUpcomingStreams] = useState([]);
  const [selectedStream, setSelectedStream] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(true);
  // Browser blockiert autoplay MIT Ton - User muss erst klicken
  const [userConsent, setUserConsent] = useState(false);

  // Fetch live streams from API
  useEffect(() => {
    const fetchStreams = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/livestreams');
        if (response.ok) {
          const data = await response.json();
          setLiveStreams(data.live || []);
          setUpcomingStreams(data.upcoming || []);
          if (data.live?.length > 0) {
            setSelectedStream(data.live[0]);
          }
        } else {
          // Mock data for demo
          setLiveStreams([]);
          setUpcomingStreams([]);
        }
      } catch (err) {
        console.error('Failed to fetch streams:', err);
        setError(t('livestreamPage.errorLoading'));
      } finally {
        setLoading(false);
      }
    };

    fetchStreams();
    // Refresh every 60 seconds
    const interval = setInterval(fetchStreams, 60000);
    return () => clearInterval(interval);
  }, []);

  // No live streams - show placeholder
  if (!loading && liveStreams.length === 0 && upcomingStreams.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-retro-dark flex items-center justify-center">
            <Radio className="text-retro-muted" size={48} />
          </div>
          <h1 className="text-fluid-2xl font-display mb-3">{t('livestreamPage.noActiveStream')}</h1>
          <p className="text-fluid-base text-retro-muted mb-6">
            {t('livestreamPage.noActiveStreamDesc')}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a href="/" className="btn btn-primary">
              {t('livestreamPage.discoverVideos')}
            </a>
            <a
              href="https://www.youtube.com/@remAIkeIT?sub_confirmation=1"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary flex items-center gap-2"
            >
              <ExternalLink size={16} />
              {t('livestreamPage.subscribeYoutube')}
            </a>
          </div>

          {/* Schedule Info */}
          <div className="mt-12 p-6 bg-retro-dark rounded-xl border border-retro-gray/30">
            <h3 className="font-semibold mb-3 flex items-center gap-2 justify-center">
              <Clock size={18} className="text-accent-gold" />
              {t('livestreamPage.upcomingStreams')}
            </h3>
            <p className="text-retro-muted text-sm">{t('livestreamPage.subscribeDesc')}</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="animate-spin text-accent-gold" size={48} />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Live Banner */}
      {liveStreams.length > 0 && (
        <div className="bg-red-600 text-white py-2 px-4 flex items-center justify-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
          </span>
          <span className="font-semibold">{t('livestreamPage.live')}</span>
          <span className="text-white/80">
            {t('livestreamPage.streamsActive', { count: liveStreams.length })}
          </span>
        </div>
      )}

      <div className="flex flex-col lg:flex-row">
        {/* Main Player Area */}
        <div className="flex-1">
          {selectedStream ? (
            <div className="aspect-video bg-black relative">
              {!userConsent ? (
                // Click-to-play overlay - Browser blockiert autoplay MIT Ton
                <div className="absolute inset-0 z-10">
                  <img
                    src={`https://i.ytimg.com/vi/${selectedStream.ytId}/maxresdefault.jpg`}
                    alt={selectedStream.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = `https://i.ytimg.com/vi/${selectedStream.ytId}/hqdefault.jpg`;
                    }}
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                    <button
                      onClick={() => setUserConsent(true)}
                      className="group flex flex-col items-center gap-4 p-8 rounded-2xl bg-black/60 hover:bg-black/80 transition-all"
                    >
                      <div className="w-20 h-20 rounded-full bg-red-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Play size={40} className="text-white ml-1" fill="currentColor" />
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-white">
                          {t('livestreamPage.startStream')}
                        </p>
                        <p className="text-sm text-white/70 flex items-center gap-1 mt-1">
                          <Volume2 size={14} />
                          {t('livestreamPage.playWithSound')}
                        </p>
                      </div>
                    </button>
                  </div>
                  {/* Live Badge */}
                  <div className="absolute top-4 left-4 bg-red-600 text-white text-sm font-bold px-3 py-1 rounded flex items-center gap-2">
                    <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    {t('livestreamPage.live')}
                  </div>
                </div>
              ) : (
                <iframe
                  src={getYouTubeEmbedUrl(selectedStream.ytId, {
                    autoplay: true,
                    params: {
                      mute: '0',
                      rel: '0',
                    },
                  })}
                  title={selectedStream.title}
                  className="w-full h-full"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              )}
            </div>
          ) : (
            <div className="aspect-video bg-retro-darker flex items-center justify-center">
              <p className="text-retro-muted">{t('livestreamPage.selectStream')}</p>
            </div>
          )}

          {/* Stream Info */}
          {selectedStream && (
            <div className="p-4 md:p-6 bg-retro-dark border-b border-retro-gray/20">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h1 className="text-fluid-xl font-semibold mb-2">{selectedStream.title}</h1>
                  <div className="flex items-center gap-4 text-sm text-retro-muted">
                    {selectedStream.viewerCount && (
                      <span className="flex items-center gap-1">
                        <Users size={16} />
                        {selectedStream.viewerCount.toLocaleString()} {t('livestreamPage.viewers')}
                      </span>
                    )}
                    <span className="flex items-center gap-1 text-red-400">
                      <Radio size={16} />
                      {t('livestreamPage.live')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowChat(!showChat)}
                  className="hidden lg:flex btn btn-secondary text-sm"
                >
                  {showChat ? t('livestreamPage.hideChat') : t('livestreamPage.showChat')}
                </button>
              </div>

              {selectedStream.description && (
                <p className="mt-4 text-retro-muted text-sm line-clamp-3">
                  {selectedStream.description}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Chat Sidebar (Desktop) */}
        {showChat && selectedStream && (
          <div className="hidden lg:block w-96 border-l border-retro-gray/20">
            <div className="h-full flex flex-col">
              <div className="p-3 border-b border-retro-gray/20 font-semibold">
                {t('livestreamPage.liveChat')}
              </div>
              <iframe
                src={`https://www.youtube.com/live_chat?v=${selectedStream.ytId}&embed_domain=${window.location.hostname}`}
                title="Live Chat"
                className="flex-1 w-full"
              />
            </div>
          </div>
        )}
      </div>

      {/* Stream List */}
      {(liveStreams.length > 1 || upcomingStreams.length > 0) && (
        <div className="p-4 md:p-6 space-y-6">
          {/* Live Streams */}
          {liveStreams.length > 1 && (
            <div>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Radio className="text-red-500" size={20} />
                {t('livestreamPage.moreLiveStreams')}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {liveStreams
                  .filter((s) => s.ytId !== selectedStream?.ytId)
                  .map((stream) => (
                    <button
                      key={stream.ytId}
                      onClick={() => setSelectedStream(stream)}
                      className="text-left bg-retro-dark rounded-xl overflow-hidden border border-retro-gray/30 hover:border-red-500/50 transition-colors"
                    >
                      <div className="relative aspect-video">
                        <img
                          src={`https://i.ytimg.com/vi/${stream.ytId}/mqdefault.jpg`}
                          alt={stream.title}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-2 py-0.5 rounded flex items-center gap-1">
                          <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                          {t('livestreamPage.live')}
                        </div>
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 bg-black/50 transition-opacity">
                          <Play size={48} className="text-white" fill="currentColor" />
                        </div>
                      </div>
                      <div className="p-3">
                        <h3 className="font-medium line-clamp-2">{stream.title}</h3>
                        {stream.viewerCount && (
                          <p className="text-sm text-retro-muted mt-1">
                            {stream.viewerCount.toLocaleString()} {t('livestreamPage.viewers')}
                          </p>
                        )}
                      </div>
                    </button>
                  ))}
              </div>
            </div>
          )}

          {/* Upcoming Streams */}
          {upcomingStreams.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Clock className="text-accent-gold" size={20} />
                Geplante Streams
              </h2>
              <div className="space-y-3">
                {upcomingStreams.map((stream) => (
                  <div
                    key={stream.ytId}
                    className="flex items-center gap-4 p-4 bg-retro-dark rounded-xl border border-retro-gray/30"
                  >
                    <img
                      src={`https://i.ytimg.com/vi/${stream.ytId}/default.jpg`}
                      alt={stream.title}
                      className="w-24 h-14 object-cover rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium truncate">{stream.title}</h3>
                      <p className="text-sm text-retro-muted">
                        {stream.scheduledStart
                          ? new Date(stream.scheduledStart).toLocaleString('de-DE')
                          : 'Zeitpunkt wird bekannt gegeben'}
                      </p>
                    </div>
                    <a
                      href={`https://www.youtube.com/watch?v=${stream.ytId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary text-sm flex items-center gap-1"
                    >
                      <ExternalLink size={14} />
                      Reminder
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-2 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          {error}
        </div>
      )}
    </div>
  );
}
