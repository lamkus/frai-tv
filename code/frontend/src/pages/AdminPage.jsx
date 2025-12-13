import { useState, useMemo } from 'react';
import {
  Settings,
  Video,
  FolderOpen,
  Plus,
  Trash2,
  Edit2,
  RefreshCw,
  Upload,
  Search,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Lock,
  Eye,
  EyeOff,
  BarChart3,
  Image as ImageIcon,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useApp } from '../context/AppContext';
import AnalyticsDashboard from '../components/admin/AnalyticsDashboard';
import ThumbnailGenerator from '../components/admin/ThumbnailGenerator';

/**
 * AdminPage - Admin panel for managing videos and categories
 *
 * Features:
 * - Video management (CRUD)
 * - Category management
 * - YouTube channel import trigger
 * - Basic stats
 *
 * Note: In production, this should be protected by authentication!
 */
export default function AdminPage() {
  const { videos, categories } = useApp();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [authError, setAuthError] = useState('');

  // Simple password protection (in production use proper auth!)
  const ADMIN_PASSWORD = 'remaike2024'; // Change this!

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === ADMIN_PASSWORD) {
      setIsAuthenticated(true);
      setAuthError('');
      sessionStorage.setItem('admin_auth', 'true');
    } else {
      setAuthError('Falsches Passwort');
    }
  };

  // Check session on mount
  useState(() => {
    if (sessionStorage.getItem('admin_auth') === 'true') {
      setIsAuthenticated(true);
    }
  });

  // Login Screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-red/20 flex items-center justify-center">
                <Lock className="text-accent-red" size={32} />
              </div>
              <h1 className="text-fluid-2xl font-display">Admin-Bereich</h1>
              <p className="text-retro-muted mt-2">Bitte Passwort eingeben</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Passwort"
                  className="w-full px-4 py-3 bg-retro-darker border border-retro-gray/50 rounded-lg
                           text-white placeholder:text-retro-muted
                           focus:outline-none focus:border-accent-red"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-retro-muted hover:text-white"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {authError && (
                <p className="text-red-400 text-sm flex items-center gap-2">
                  <AlertCircle size={14} />
                  {authError}
                </p>
              )}

              <button type="submit" className="btn btn-primary w-full">
                Anmelden
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Settings },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'thumbnails', label: 'Thumbnails', icon: ImageIcon },
    { id: 'videos', label: 'Videos', icon: Video },
    { id: 'categories', label: 'Kategorien', icon: FolderOpen },
    { id: 'import', label: 'Import', icon: Upload },
  ];

  return (
    <div className="min-h-screen pt-4 pb-12">
      {/* Header */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="text-accent-red" size={28} />
            <h1 className="text-fluid-3xl font-display">Admin Panel</h1>
          </div>
          <button
            onClick={() => {
              sessionStorage.removeItem('admin_auth');
              setIsAuthenticated(false);
            }}
            className="btn btn-ghost text-sm"
          >
            Abmelden
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 mb-6">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap',
                  activeTab === tab.id
                    ? 'bg-accent-red text-white'
                    : 'bg-retro-dark text-retro-muted hover:text-white'
                )}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12">
        {activeTab === 'dashboard' && <DashboardTab videos={videos} categories={categories} />}
        {activeTab === 'analytics' && <AnalyticsDashboard />}
        {activeTab === 'thumbnails' && <ThumbnailGenerator videos={videos} />}
        {activeTab === 'videos' && <VideosTab videos={videos} />}
        {activeTab === 'categories' && <CategoriesTab categories={categories} />}
        {activeTab === 'import' && <ImportTab />}
      </div>
    </div>
  );
}

// Dashboard Tab
function DashboardTab({ videos, categories }) {
  const stats = [
    { label: 'Videos', value: videos.length, icon: Video },
    { label: 'Kategorien', value: categories.length, icon: FolderOpen },
    { label: 'Gesamtdauer', value: formatTotalDuration(videos), icon: RefreshCw },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6"
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-accent-red/20 rounded-lg">
                  <Icon className="text-accent-red" size={24} />
                </div>
                <div>
                  <p className="text-retro-muted text-sm">{stat.label}</p>
                  <p className="text-fluid-2xl font-display">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Videos */}
      <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
        <h3 className="text-fluid-lg font-semibold mb-4">Neueste Videos</h3>
        <div className="space-y-3">
          {videos.slice(0, 5).map((video) => (
            <div
              key={video.id || video.ytId}
              className="flex items-center gap-4 p-3 bg-retro-darker rounded-lg"
            >
              <img
                src={video.thumbnailUrl || `https://i.ytimg.com/vi/${video.ytId}/mqdefault.jpg`}
                alt=""
                className="w-24 h-14 object-cover rounded"
              />
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{video.title}</p>
                <p className="text-sm text-retro-muted">{video.category || 'Keine Kategorie'}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Videos Tab
function VideosTab({ videos }) {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [editingVideo, setEditingVideo] = useState(null);
  const [editForm, setEditForm] = useState({});

  const filteredVideos = useMemo(() => {
    return videos.filter((v) => {
      const matchesSearch = !search || v.title?.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = !selectedCategory || v.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [videos, search, selectedCategory]);

  const uniqueCategories = [...new Set(videos.map((v) => v.category).filter(Boolean))];

  const handleEdit = (video) => {
    setEditingVideo(video);
    setEditForm({
      title: video.title || '',
      category: video.category || '',
      description: video.description || '',
      year: video.year || '',
      tags: video.tags?.join(', ') || '',
    });
  };

  const handleSave = async () => {
    if (!editingVideo) return;

    try {
      // Try to save to backend API
      const response = await fetch(`/api/videos/${editingVideo.id || editingVideo.ytId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...editForm,
          tags: editForm.tags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
        }),
      });

      if (response.ok) {
        alert('Video gespeichert!');
        setEditingVideo(null);
        // Refresh page to show changes
        window.location.reload();
      } else {
        // Fallback: Save to localStorage for local override
        const localOverrides = JSON.parse(localStorage.getItem('remaike_video_overrides') || '{}');
        localOverrides[editingVideo.id || editingVideo.ytId] = {
          ...editForm,
          tags: editForm.tags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
        };
        localStorage.setItem('remaike_video_overrides', JSON.stringify(localOverrides));
        alert('Video lokal gespeichert (Backend nicht erreichbar)');
        setEditingVideo(null);
      }
    } catch (err) {
      // Fallback to localStorage
      const localOverrides = JSON.parse(localStorage.getItem('remaike_video_overrides') || '{}');
      localOverrides[editingVideo.id || editingVideo.ytId] = {
        ...editForm,
        tags: editForm.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
      };
      localStorage.setItem('remaike_video_overrides', JSON.stringify(localOverrides));
      alert('Video lokal gespeichert (Backend nicht erreichbar)');
      setEditingVideo(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted" size={18} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Videos durchsuchen..."
            className="w-full pl-10 pr-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                     text-white placeholder:text-retro-muted
                     focus:outline-none focus:border-accent-cyan"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                   text-white focus:outline-none focus:border-accent-cyan"
        >
          <option value="">Alle Kategorien</option>
          {uniqueCategories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Videos Table */}
      <div className="bg-retro-dark rounded-xl border border-retro-gray/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-retro-darker">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-retro-muted">Video</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-retro-muted">
                  Kategorie
                </th>
                <th className="text-left px-4 py-3 text-sm font-medium text-retro-muted">Datum</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-retro-muted">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-retro-gray/20">
              {filteredVideos.map((video) => (
                <tr key={video.id || video.ytId} className="hover:bg-retro-darker/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={
                          video.thumbnailUrl || `https://i.ytimg.com/vi/${video.ytId}/default.jpg`
                        }
                        alt=""
                        className="w-16 h-9 object-cover rounded"
                      />
                      <span className="font-medium truncate max-w-xs">{video.title}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-retro-muted">{video.category || '-'}</td>
                  <td className="px-4 py-3 text-retro-muted text-sm">
                    {video.publishDate
                      ? new Date(video.publishDate).toLocaleDateString('de-DE')
                      : '-'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleEdit(video)}
                        className="p-2 hover:bg-retro-gray/30 rounded"
                        title="Bearbeiten"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        className="p-2 hover:bg-red-500/20 text-red-400 rounded"
                        title="Löschen"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredVideos.length === 0 && (
          <div className="text-center py-8 text-retro-muted">Keine Videos gefunden</div>
        )}
      </div>

      <p className="text-sm text-retro-muted">
        {filteredVideos.length} von {videos.length} Videos
      </p>

      {/* Edit Video Modal */}
      {editingVideo && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={(e) => e.target === e.currentTarget && setEditingVideo(null)}
        >
          <div className="w-full max-w-2xl mx-4 bg-retro-darker border border-retro-gray/30 rounded-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-retro-gray/20">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Edit2 className="text-accent-gold" size={20} />
                Video bearbeiten
              </h3>
              <button
                onClick={() => setEditingVideo(null)}
                className="p-2 hover:bg-retro-gray/30 rounded-full"
              >
                <span className="sr-only">Schließen</span>×
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              {/* Thumbnail Preview */}
              <div className="flex gap-4">
                <img
                  src={
                    editingVideo.thumbnailUrl ||
                    `https://i.ytimg.com/vi/${editingVideo.ytId}/mqdefault.jpg`
                  }
                  alt=""
                  className="w-40 h-24 object-cover rounded-lg"
                />
                <div className="flex-1">
                  <p className="text-xs text-retro-muted mb-1">YouTube ID</p>
                  <p className="font-mono text-sm">{editingVideo.ytId}</p>
                </div>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-retro-muted mb-1">Titel</label>
                <input
                  type="text"
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  className="w-full px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                           text-white focus:outline-none focus:border-accent-gold"
                />
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-retro-muted mb-1">Kategorie</label>
                <select
                  value={editForm.category}
                  onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                  className="w-full px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                           text-white focus:outline-none focus:border-accent-gold"
                >
                  <option value="">Keine Kategorie</option>
                  {uniqueCategories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                  <option value="Weihnachten">Weihnachten</option>
                  <option value="Cartoons">Cartoons</option>
                  <option value="Comedy">Comedy</option>
                  <option value="Klassische Filme">Klassische Filme</option>
                  <option value="Propaganda">Propaganda</option>
                  <option value="Werbung">Werbung</option>
                  <option value="Musik">Musik</option>
                  <option value="Dokumentation">Dokumentation</option>
                </select>
              </div>

              {/* Year */}
              <div>
                <label className="block text-sm font-medium text-retro-muted mb-1">Jahr</label>
                <input
                  type="text"
                  value={editForm.year}
                  onChange={(e) => setEditForm({ ...editForm, year: e.target.value })}
                  placeholder="z.B. 1950"
                  className="w-full px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                           text-white focus:outline-none focus:border-accent-gold"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-retro-muted mb-1">
                  Tags (kommagetrennt)
                </label>
                <input
                  type="text"
                  value={editForm.tags}
                  onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })}
                  placeholder="z.B. christmas, classic, animated"
                  className="w-full px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                           text-white focus:outline-none focus:border-accent-gold"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-retro-muted mb-1">
                  Beschreibung
                </label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 bg-retro-dark border border-retro-gray/50 rounded-lg
                           text-white focus:outline-none focus:border-accent-gold resize-none"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-4 border-t border-retro-gray/20">
              <button
                onClick={() => setEditingVideo(null)}
                className="px-4 py-2 text-retro-muted hover:text-white transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-accent-gold text-black font-semibold rounded-lg hover:bg-accent-gold/90"
              >
                Speichern
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Categories Tab
function CategoriesTab({ categories }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-fluid-lg font-semibold">Kategorien verwalten</h3>
        <button className="btn btn-primary text-sm">
          <Plus size={16} />
          Neue Kategorie
        </button>
      </div>

      <div className="grid gap-4">
        {categories.map((category) => (
          <div
            key={category.name}
            className="bg-retro-dark rounded-xl border border-retro-gray/30 p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FolderOpen className="text-accent-cyan" size={20} />
                <div>
                  <p className="font-medium">{category.name}</p>
                  <p className="text-sm text-retro-muted">{category.videos?.length || 0} Videos</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 hover:bg-retro-gray/30 rounded" title="Bearbeiten">
                  <Edit2 size={16} />
                </button>
                <button className="p-2 hover:bg-red-500/20 text-red-400 rounded" title="Löschen">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}

        {categories.length === 0 && (
          <div className="text-center py-8 text-retro-muted bg-retro-dark rounded-xl">
            Noch keine Kategorien vorhanden
          </div>
        )}
      </div>
    </div>
  );
}

// Import Tab
function ImportTab() {
  const [channelId, setChannelId] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [maxResults, setMaxResults] = useState('500');
  const [importResult, setImportResult] = useState(null);

  const handleImport = async () => {
    if (!channelId.trim()) return;

    setIsImporting(true);
    setImportResult(null);

    try {
      const response = await fetch('/api/refresh-channel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channelId: channelId.trim(),
          maxResults: parseInt(maxResults, 10) || 50,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setImportResult({ success: true, message: `${data.imported} Videos importiert!` });
      } else {
        setImportResult({ success: false, message: data.error || 'Import fehlgeschlagen' });
      }
    } catch (err) {
      setImportResult({ success: false, message: 'Netzwerkfehler beim Import' });
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
        <h3 className="text-fluid-lg font-semibold mb-4 flex items-center gap-2">
          <Upload className="text-accent-cyan" size={20} />
          YouTube-Kanal importieren
        </h3>

        <p className="text-retro-muted mb-4">
          Gib die YouTube Channel-ID ein, um alle Videos des Kanals zu importieren. Die Channel-ID
          findest du in der URL des YouTube-Kanals.
        </p>

        <div className="flex gap-3">
          <input
            type="text"
            value={channelId}
            onChange={(e) => setChannelId(e.target.value)}
            placeholder="UC... (YouTube Channel ID)"
            className="flex-1 px-4 py-2 bg-retro-darker border border-retro-gray/50 rounded-lg
                     text-white placeholder:text-retro-muted
                     focus:outline-none focus:border-accent-cyan"
          />
          <button
            onClick={handleImport}
            disabled={isImporting || !channelId.trim()}
            className="btn btn-primary"
          >
            {isImporting ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Importiere...
              </>
            ) : (
              <>
                <Upload size={16} />
                Importieren
              </>
            )}
          </button>
          <div className="flex items-center gap-2 ml-2">
            <label className="text-xs text-retro-muted">Max results</label>
            <select
              value={maxResults}
              onChange={(e) => setMaxResults(e.target.value)}
              className="bg-retro-darker border border-retro-gray rounded px-3 py-2 text-sm"
            >
              <option value="50">50</option>
              <option value="200">200</option>
              <option value="500">500</option>
              <option value="1000">1000</option>
              <option value="5000">5000</option>
            </select>
          </div>
        </div>

        {importResult && (
          <div
            className={cn(
              'mt-4 p-3 rounded-lg flex items-center gap-2',
              importResult.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            )}
          >
            {importResult.success ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
            {importResult.message}
          </div>
        )}
      </div>

      <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6">
        <h3 className="text-fluid-lg font-semibold mb-4">Hinweise</h3>
        <ul className="space-y-2 text-retro-muted text-sm">
          <li className="flex items-start gap-2">
            <ChevronRight size={16} className="mt-0.5 shrink-0" />
            Der Import nutzt die YouTube Data API mit Quota-Limits
          </li>
          <li className="flex items-start gap-2">
            <ChevronRight size={16} className="mt-0.5 shrink-0" />
            Maximal 50 Videos pro Import (API-Limit)
          </li>
          <li className="flex items-start gap-2">
            <ChevronRight size={16} className="mt-0.5 shrink-0" />
            Bei Quota-Überschreitung wird aus dem Cache geladen
          </li>
        </ul>
      </div>
    </div>
  );
}

// Helper function
function formatTotalDuration(videos) {
  const totalSeconds = videos.reduce((acc, v) => acc + (v.duration || 0), 0);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}
