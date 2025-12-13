import { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Users,
  Play,
  Clock,
  Eye,
  Monitor,
  Globe,
  Download,
  Trash2,
  RefreshCw,
  ChevronDown,
  Video,
  FileText,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import {
  getDashboardReport,
  getVideoReport,
  exportAnalyticsData,
  clearAnalyticsData,
  getAnalyticsData,
} from '../../lib/analytics';

/**
 * Analytics Dashboard - YouTube Studio Style
 *
 * Zeigt:
 * - Übersichts-Metriken
 * - Video-Performance
 * - Audience-Insights
 * - Traffic-Quellen
 * - Echtzeit-Daten
 */
export default function AnalyticsDashboard() {
  const [period, setPeriod] = useState(7);
  const [report, setReport] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoReport, setVideoReport] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);

  // Report laden
  useEffect(() => {
    setIsLoading(true);
    const data = getDashboardReport(period);
    setReport(data);
    setIsLoading(false);
  }, [period]);

  // Video-Report laden
  useEffect(() => {
    if (selectedVideo) {
      const data = getVideoReport(selectedVideo);
      setVideoReport(data);
    } else {
      setVideoReport(null);
    }
  }, [selectedVideo]);

  const tabs = [
    { id: 'overview', label: 'Übersicht', icon: BarChart3 },
    { id: 'content', label: 'Content', icon: Video },
    { id: 'audience', label: 'Audience', icon: Users },
    { id: 'realtime', label: 'Echtzeit', icon: TrendingUp },
  ];

  if (isLoading || !report) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-accent-amber" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="text-accent-amber" />
          Analytics Dashboard
        </h2>

        <div className="flex items-center gap-3">
          {/* Zeitraum-Auswahl */}
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="bg-retro-dark border border-retro-gray/50 rounded-lg px-4 py-2 text-sm text-white"
          >
            <option value={7}>Letzte 7 Tage</option>
            <option value={14}>Letzte 14 Tage</option>
            <option value={30}>Letzte 30 Tage</option>
            <option value={90}>Letzte 90 Tage</option>
          </select>

          {/* Export */}
          <button
            onClick={exportAnalyticsData}
            className="flex items-center gap-2 px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg text-sm hover:bg-retro-gray transition-colors"
          >
            <Download size={16} />
            Export
          </button>

          {/* Daten löschen */}
          <button
            onClick={() => {
              if (confirm('Alle Analytics-Daten unwiderruflich löschen?')) {
                clearAnalyticsData();
                setReport(getDashboardReport(period));
              }
            }}
            className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-lg text-sm text-red-400 hover:bg-red-500/30 transition-colors"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-retro-gray/30 pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors',
              activeTab === tab.id
                ? 'bg-accent-amber text-black font-medium'
                : 'text-retro-muted hover:text-white hover:bg-retro-dark'
            )}
          >
            <tab.icon size={18} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KPICard
              icon={Users}
              label="Besucher"
              value={report.overview.uniqueVisitors}
              subtext={`${report.overview.totalSessions} Sessions`}
              color="cyan"
            />
            <KPICard
              icon={Eye}
              label="Seitenaufrufe"
              value={report.overview.totalPageViews}
              subtext={`${(
                report.overview.totalPageViews / Math.max(report.overview.totalSessions, 1)
              ).toFixed(1)} pro Session`}
              color="amber"
            />
            <KPICard
              icon={Play}
              label="Video Views"
              value={report.overview.totalVideoViews}
              subtext={formatDuration(report.overview.totalWatchTime)}
              color="green"
            />
            <KPICard
              icon={Clock}
              label="Ø Session-Dauer"
              value={formatDuration(report.overview.avgSessionDuration)}
              subtext={`${report.overview.totalInteractions} Interaktionen`}
              color="purple"
            />
          </div>

          {/* Trend Chart */}
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Trend</h3>
            <TrendChart data={report.dailyStats} />
          </div>

          {/* Top Content */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Top Videos */}
            <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Video size={20} className="text-accent-amber" />
                Top Videos
              </h3>
              <div className="space-y-3">
                {report.topVideos.length === 0 ? (
                  <p className="text-retro-muted text-sm">Noch keine Video-Daten</p>
                ) : (
                  report.topVideos.map((video, i) => (
                    <div
                      key={video.videoId}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-retro-darker cursor-pointer"
                      onClick={() => setSelectedVideo(video.videoId)}
                    >
                      <span className="text-retro-muted text-sm w-6">{i + 1}.</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm truncate">
                          {video.title || video.videoId}
                        </p>
                        <p className="text-retro-muted text-xs">
                          {video.views} Views • {formatDuration(video.totalWatchTime)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-accent-green text-sm">
                          {Math.round(video.avgCompletion)}%
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Top Pages */}
            <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <FileText size={20} className="text-accent-cyan" />
                Top Seiten
              </h3>
              <div className="space-y-3">
                {report.topPages.length === 0 ? (
                  <p className="text-retro-muted text-sm">Noch keine Seitendaten</p>
                ) : (
                  report.topPages.map((page, i) => (
                    <div
                      key={page.path}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-retro-darker"
                    >
                      <span className="text-retro-muted text-sm w-6">{i + 1}.</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm truncate">{page.path}</p>
                        <p className="text-retro-muted text-xs">
                          Ø {formatDuration(Math.round(page.totalTime / Math.max(page.views, 1)))}{' '}
                          pro Aufruf
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-accent-amber text-sm">{page.views}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Tab */}
      {activeTab === 'content' && (
        <div className="space-y-6">
          {selectedVideo && videoReport ? (
            <VideoDetailReport report={videoReport} onClose={() => setSelectedVideo(null)} />
          ) : (
            <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Video Performance</h3>
              <div className="space-y-2">
                {report.topVideos.length === 0 ? (
                  <p className="text-retro-muted">
                    Noch keine Video-Analytics vorhanden. Schaue dir ein Video an!
                  </p>
                ) : (
                  report.topVideos.map((video) => (
                    <div
                      key={video.videoId}
                      className="flex items-center gap-4 p-4 rounded-lg bg-retro-darker hover:bg-retro-gray/30 cursor-pointer transition-colors"
                      onClick={() => setSelectedVideo(video.videoId)}
                    >
                      <div className="w-24 h-14 rounded bg-retro-gray/50 flex items-center justify-center">
                        <Play size={20} className="text-retro-muted" />
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium">{video.title || video.videoId}</p>
                        <div className="flex items-center gap-4 text-sm text-retro-muted mt-1">
                          <span>{video.views} Views</span>
                          <span>{formatDuration(video.totalWatchTime)} Watchtime</span>
                          <span>{Math.round(video.avgCompletion)}% Completion</span>
                        </div>
                      </div>
                      <ChevronDown className="text-retro-muted rotate-[-90deg]" size={20} />
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Audience Tab */}
      {activeTab === 'audience' && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Geräte */}
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Monitor size={20} className="text-accent-cyan" />
              Geräte
            </h3>
            <DistributionChart data={report.deviceDistribution} />
          </div>

          {/* Browser */}
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Globe size={20} className="text-accent-amber" />
              Browser
            </h3>
            <DistributionChart data={report.browserDistribution} />
          </div>

          {/* Traffic-Quellen */}
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp size={20} className="text-accent-green" />
              Traffic-Quellen
            </h3>
            <DistributionChart data={report.trafficSources} />
          </div>
        </div>
      )}

      {/* Realtime Tab */}
      {activeTab === 'realtime' && <RealtimeView />}
    </div>
  );
}

// ============================================================================
// Sub-Components
// ============================================================================

function KPICard({ icon: Icon, label, value, subtext, color }) {
  const colorClasses = {
    cyan: 'text-accent-cyan bg-accent-cyan/20',
    amber: 'text-accent-amber bg-accent-amber/20',
    green: 'text-accent-green bg-accent-green/20',
    purple: 'text-accent-purple bg-accent-purple/20',
  };

  return (
    <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-retro-muted text-sm">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          <p className="text-retro-muted text-xs mt-1">{subtext}</p>
        </div>
        <div className={cn('p-2 rounded-lg', colorClasses[color])}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  );
}

function TrendChart({ data }) {
  const maxValue = Math.max(...data.map((d) => Math.max(d.sessions, d.pageViews, d.videoViews)), 1);

  return (
    <div className="h-48 flex items-end gap-1">
      {data.map((day) => (
        <div key={day.date} className="flex-1 flex flex-col items-center gap-1">
          <div className="w-full flex flex-col gap-0.5">
            <div
              className="w-full bg-accent-cyan rounded-t"
              style={{ height: `${(day.pageViews / maxValue) * 150}px` }}
              title={`${day.pageViews} Seitenaufrufe`}
            />
            <div
              className="w-full bg-accent-amber rounded-t"
              style={{ height: `${(day.videoViews / maxValue) * 150}px` }}
              title={`${day.videoViews} Video Views`}
            />
          </div>
          <span className="text-retro-muted text-xs">{day.date.slice(5)}</span>
        </div>
      ))}
    </div>
  );
}

function DistributionChart({ data }) {
  const total = Object.values(data).reduce((sum, v) => sum + v, 0);
  const colors = [
    'bg-accent-cyan',
    'bg-accent-amber',
    'bg-accent-green',
    'bg-accent-purple',
    'bg-accent-red',
  ];

  if (total === 0) {
    return <p className="text-retro-muted text-sm">Keine Daten</p>;
  }

  return (
    <div className="space-y-3">
      {Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([key, value], i) => (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-white capitalize">{key}</span>
              <span className="text-retro-muted">{Math.round((value / total) * 100)}%</span>
            </div>
            <div className="h-2 bg-retro-darker rounded-full overflow-hidden">
              <div
                className={cn('h-full rounded-full', colors[i % colors.length])}
                style={{ width: `${(value / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
    </div>
  );
}

function VideoDetailReport({ report, onClose }) {
  return (
    <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white">{report.title || report.videoId}</h3>
        <button onClick={onClose} className="text-retro-muted hover:text-white">
          ✕
        </button>
      </div>

      {/* Metriken */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Views</p>
          <p className="text-2xl font-bold text-white">{report.metrics.totalViews}</p>
        </div>
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Watchtime</p>
          <p className="text-2xl font-bold text-white">
            {formatDuration(report.metrics.totalWatchTime)}
          </p>
        </div>
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Ø Completion</p>
          <p className="text-2xl font-bold text-white">{report.metrics.avgCompletion}%</p>
        </div>
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Replay Rate</p>
          <p className="text-2xl font-bold text-white">{Math.round(report.metrics.replayRate)}%</p>
        </div>
      </div>

      {/* Segment Heatmap */}
      <div className="mb-6">
        <h4 className="text-white font-medium mb-3">Retention Heatmap</h4>
        <div className="flex gap-1">
          {report.engagement.segmentViews.map((views, i) => {
            const maxViews = Math.max(...report.engagement.segmentViews, 1);
            const intensity = views / maxViews;
            return (
              <div
                key={i}
                className="flex-1 h-8 rounded"
                style={{
                  backgroundColor: `rgba(255, 193, 7, ${0.2 + intensity * 0.8})`,
                }}
                title={`${i * 10}-${(i + 1) * 10}%: ${views} Views`}
              />
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-retro-muted mt-1">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Engagement Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Ø Seeks pro View</p>
          <p className="text-xl font-bold text-white">
            {report.engagement.avgSeeksPerView.toFixed(1)}
          </p>
        </div>
        <div className="bg-retro-darker rounded-lg p-4">
          <p className="text-retro-muted text-sm">Ø Pausen pro View</p>
          <p className="text-xl font-bold text-white">
            {report.engagement.avgPausesPerView.toFixed(1)}
          </p>
        </div>
      </div>
    </div>
  );
}

function RealtimeView() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const update = () => {
      const analytics = getAnalyticsData();
      setData({
        activeSessions: analytics.currentSession ? 1 : 0,
        recentPageViews: analytics.pageViews.slice(-10).reverse(),
        recentInteractions: analytics.interactions.slice(-10).reverse(),
      });
    };

    update();
    const interval = setInterval(update, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Live Counter */}
      <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="w-3 h-3 bg-accent-green rounded-full animate-pulse" />
          <span className="text-retro-muted">Aktive Nutzer</span>
        </div>
        <p className="text-6xl font-bold text-white">{data.activeSessions}</p>
      </div>

      {/* Recent Activity */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Letzte Seitenaufrufe</h3>
          <div className="space-y-2">
            {data.recentPageViews.map((pv, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="text-white truncate">{pv.path}</span>
                <span className="text-retro-muted">
                  {new Date(pv.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Letzte Interaktionen</h3>
          <div className="space-y-2">
            {data.recentInteractions.map((int, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="text-white">
                  {int.type}: {int.target}
                </span>
                <span className="text-retro-muted">
                  {new Date(int.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Helpers
// ============================================================================

function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '0s';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
}
