import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ExternalLink, Radio, RefreshCw, Clock, Play } from 'lucide-react';
import useMeta from '../lib/useMeta';

export default function SenderPage() {
  const { t } = useTranslation();

  useMeta({
    title: t('senderPage.metaTitle'),
    description: t('senderPage.metaDescription'),
  });

  const [liveStreams, setLiveStreams] = useState([]);
  const [upcomingStreams, setUpcomingStreams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const resp = await fetch('/api/livestreams');
        if (!resp.ok) {
          setLiveStreams([]);
          setUpcomingStreams([]);
          return;
        }
        const data = await resp.json();
        setLiveStreams(data.live || []);
        setUpcomingStreams(data.upcoming || []);
      } catch {
        setLiveStreams([]);
        setUpcomingStreams([]);
      } finally {
        setLoading(false);
      }
    };

    load();
    const interval = setInterval(load, 60000);
    return () => clearInterval(interval);
  }, []);

  const primaryLive = liveStreams?.[0] || null;

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="px-4 sm:px-6 lg:px-8 pt-6 pb-4 border-b border-retro-gray/20">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-fluid-2xl font-display">{t('senderPage.title')}</h1>
              <p className="text-retro-muted mt-2 max-w-2xl">{t('senderPage.subtitle')}</p>
            </div>

            <a
              href="https://www.youtube.com/@remAIkeIT?sub_confirmation=1"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary hidden sm:flex items-center gap-2"
            >
              <ExternalLink size={16} />
              {t('senderPage.subscribeYoutube')}
            </a>
          </div>

          {/* On Air / Next */}
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 bg-retro-dark rounded-xl border border-retro-gray/30 overflow-hidden">
              <div className="p-4 md:p-5 flex items-center justify-between gap-3 border-b border-retro-gray/20">
                <div className="flex items-center gap-2 font-semibold">
                  <Radio className="text-red-500" size={18} />
                  {primaryLive ? t('senderPage.onAir') : t('senderPage.offAir')}
                </div>
                {loading && <RefreshCw className="animate-spin text-accent-gold" size={18} />}
              </div>

              <div className="p-4 md:p-5">
                {primaryLive ? (
                  <>
                    <p className="text-lg font-semibold text-white">{primaryLive.title}</p>
                    {primaryLive.viewerCount ? (
                      <p className="text-sm text-retro-muted mt-1">
                        {t('senderPage.viewersNow', { count: primaryLive.viewerCount })}
                      </p>
                    ) : null}

                    <div className="mt-4 flex flex-col sm:flex-row gap-3">
                      <Link to="/live" className="btn btn-primary flex items-center gap-2">
                        <Play size={16} />
                        {t('senderPage.watchLive')}
                      </Link>
                      <Link to="/" className="btn btn-secondary">
                        {t('senderPage.openMediathek')}
                      </Link>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="text-white font-semibold">{t('senderPage.noLiveTitle')}</p>
                    <p className="text-retro-muted text-sm mt-2">{t('senderPage.noLiveDesc')}</p>
                    <div className="mt-4 flex flex-col sm:flex-row gap-3">
                      <Link to="/" className="btn btn-primary">
                        {t('senderPage.openMediathek')}
                      </Link>
                      <a
                        href="https://www.youtube.com/@remAIkeIT"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary flex items-center gap-2"
                      >
                        <ExternalLink size={16} />
                        {t('senderPage.openChannel')}
                      </a>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="bg-retro-dark rounded-xl border border-retro-gray/30 overflow-hidden">
              <div className="p-4 md:p-5 flex items-center gap-2 font-semibold border-b border-retro-gray/20">
                <Clock className="text-accent-gold" size={18} />
                {t('senderPage.nextUp')}
              </div>
              <div className="p-4 md:p-5 space-y-3">
                {upcomingStreams && upcomingStreams.length > 0 ? (
                  upcomingStreams.slice(0, 3).map((s) => (
                    <div
                      key={s.ytId}
                      className="p-3 rounded-lg bg-retro-darker border border-retro-gray/20"
                    >
                      <p className="text-sm font-semibold text-white line-clamp-2">{s.title}</p>
                      {s.scheduledStartTime ? (
                        <p className="text-xs text-retro-muted mt-1">
                          {new Date(s.scheduledStartTime).toLocaleString()}
                        </p>
                      ) : null}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-retro-muted">{t('senderPage.noUpcoming')}</p>
                )}

                <Link to="/live" className="btn btn-secondary w-full text-center">
                  {t('senderPage.openLiveCenter')}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust / compliance note */}
      <section className="px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-4 md:p-5">
            <p className="text-sm text-retro-muted">{t('senderPage.privacyNote')}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
