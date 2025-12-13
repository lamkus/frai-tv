import { useState, useEffect } from 'react';
import {
  Settings,
  Moon,
  Sun,
  Volume2,
  VolumeX,
  Monitor,
  Smartphone,
  Languages,
  Bell,
  Palette,
  Info,
  Shield,
  Trash2,
  Download,
  ChevronRight,
  Check,
  RefreshCw,
  MonitorSmartphone,
  Sparkles,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../lib/utils';
import { InfoPopup, QuickNotice } from '../components/ui/InfoPopup';
import { useApp } from '../context/AppContext';
import { InstallButton, InstallPrompt } from '../components/ui/InstallPrompt';

/**
 * SettingsPage - User preferences and app settings
 *
 * Sections:
 * - Appearance (Theme, Display)
 * - Playback (Autoplay, Quality)
 * - Notifications
 * - Privacy & Data
 * - About
 */
export default function SettingsPage() {
  const { t } = useTranslation();
  const { preferences, updatePreferences, clearHistory } = useApp();
  const [activeSection, setActiveSection] = useState('install');
  const [showClearDataConfirm, setShowClearDataConfirm] = useState(false);

  // Settings sections
  const sections = [
    { id: 'install', labelKey: 'settingsPage.sections.install', icon: MonitorSmartphone },
    { id: 'appearance', labelKey: 'settingsPage.sections.appearance', icon: Palette },
    { id: 'playback', labelKey: 'settingsPage.sections.playback', icon: Monitor },
    { id: 'notifications', labelKey: 'settingsPage.sections.notifications', icon: Bell },
    { id: 'privacy', labelKey: 'settingsPage.sections.privacy', icon: Shield },
    { id: 'about', labelKey: 'settingsPage.sections.about', icon: Info },
  ];

  // Toggle setting
  const toggleSetting = (key) => {
    updatePreferences({ [key]: !preferences[key] });
  };

  // Set setting value
  const setSetting = (key, value) => {
    updatePreferences({ [key]: value });
  };

  // Clear all data
  const handleClearData = () => {
    localStorage.clear();
    window.location.reload();
  };

  // Demo popup state
  const [showInfoDemo, setShowInfoDemo] = useState(false);
  const [showQuickNoticeDemo, setShowQuickNoticeDemo] = useState(false);
  const [showInstallPreview, setShowInstallPreview] = useState(false);

  // Listen for demo events to show popups
  useEffect(() => {
    const showInfo = () => setShowInfoDemo(true);
    const showQuick = () => setShowQuickNoticeDemo(true);

    window.addEventListener('remake:showInfoPopup', showInfo);
    window.addEventListener('remake:showQuickNotice', showQuick);
    return () => {
      window.removeEventListener('remake:showInfoPopup', showInfo);
      window.removeEventListener('remake:showQuickNotice', showQuick);
    };
  }, []);

  return (
    <div className="min-h-screen pt-4 pb-12">
      {/* Header */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mb-6 md:mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Settings className="text-accent-cyan" size={28} />
          <h1 className="text-fluid-3xl font-display">{t('settingsPage.title')}</h1>
        </div>
        <p className="text-fluid-base text-retro-muted">{t('settingsPage.subtitle')}</p>
      </div>

      {/* Settings Layout */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24">
        <div className="flex flex-col md:flex-row gap-6 max-w-6xl">
          {/* Navigation (Sidebar on desktop, tabs on mobile) */}
          <nav className="md:w-56 shrink-0">
            {/* Mobile: Horizontal scroll */}
            <div
              className="flex md:flex-col gap-2 overflow-x-auto pb-2 md:pb-0 
                          hide-scrollbar -mx-4 px-4 md:mx-0 md:px-0"
            >
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                      'whitespace-nowrap text-fluid-sm md:w-full',
                      activeSection === section.id
                        ? 'bg-accent-red/20 text-accent-red'
                        : 'bg-retro-dark/50 text-retro-muted hover:bg-retro-dark hover:text-white'
                    )}
                  >
                    <Icon size={18} />
                    <span>{t(section.labelKey)}</span>
                  </button>
                );
              })}
            </div>
          </nav>

          {/* Content */}
          <div className="flex-1 bg-retro-dark/30 rounded-xl border border-retro-gray/30 p-6">
            {/* Install App */}
            {activeSection === 'install' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.install.title')}
                </h2>

                <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-xl p-6 border border-purple-500/30">
                  {/* Dev UI Preview Buttons */}
                  <div className="mt-4 flex flex-col sm:flex-row gap-3">
                    <button
                      onClick={() => setShowInstallPreview((s) => !s)}
                      className="px-4 py-2 rounded-lg bg-gradient-to-br from-accent-gold to-[#b8944a] text-black font-bold hover:shadow-lg transition-all"
                    >
                      Toggle Install Prompt Preview
                    </button>
                    <button
                      onClick={() => window.dispatchEvent(new CustomEvent('remake:showInfoPopup'))}
                      className="px-4 py-2 rounded-lg bg-accent-gold text-black font-semibold hover:bg-accent-honey transition-colors"
                    >
                      UI Preview: Info Popup
                    </button>

                    <button
                      onClick={() =>
                        window.dispatchEvent(new CustomEvent('remake:showQuickNotice'))
                      }
                      className="px-4 py-2 rounded-lg bg-retro-gray/80 text-white border border-white/10 hover:border-accent-gold transition-colors"
                    >
                      UI Preview: Quick Notice
                    </button>

                    <div className="ml-auto">
                      <InstallButton />
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg">
                      <span className="text-white font-bold text-3xl">f</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {t('settingsPage.install.appName')}
                      </h3>
                      <p className="text-sm text-zinc-400 mb-4">
                        {t('settingsPage.install.appDesc')}
                      </p>
                      <InstallButton />
                    </div>
                  </div>
                </div>

                <div className="space-y-4 text-sm text-zinc-400">
                  {/* Info Popup Demo (Hidden: Dev only) */}
                  <InfoPopup
                    isOpen={showInfoDemo}
                    title="Premium UI Preview"
                    onClose={() => setShowInfoDemo(false)}
                    className="md:max-w-md"
                  >
                    <p>
                      This is a preview of the remAIke.IT premium popup styles (gold accents,
                      backdrop blur, etc.). Use the buttons above to preview.
                    </p>
                  </InfoPopup>

                  <QuickNotice
                    isOpen={showQuickNoticeDemo}
                    onClose={() => setShowQuickNoticeDemo(false)}
                    message="This is a premium quick notice."
                    variant="info"
                  />

                  {/* Install Prompt Demo */}
                  {showInstallPreview && <InstallPrompt forceOpen={true} />}

                  <h4 className="font-medium text-white">{t('settingsPage.install.benefits')}</h4>
                  <ul className="space-y-2">
                    <li className="flex items-center gap-2">
                      <Check size={16} className="text-green-500" />
                      {t('settingsPage.install.benefit1')}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check size={16} className="text-green-500" />
                      {t('settingsPage.install.benefit2')}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check size={16} className="text-green-500" />
                      {t('settingsPage.install.benefit3')}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check size={16} className="text-green-500" />
                      {t('settingsPage.install.benefit4')}
                    </li>
                  </ul>
                </div>
              </div>
            )}

            {/* Appearance */}
            {activeSection === 'appearance' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.appearance.title')}
                </h2>

                {/* Theme */}
                <SettingItem
                  icon={preferences.darkMode ? Moon : Sun}
                  label={t('settingsPage.appearance.darkMode')}
                  description={t('settingsPage.appearance.darkModeDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.darkMode !== false}
                    onChange={() => toggleSetting('darkMode')}
                  />
                </SettingItem>

                {/* Accent Color */}
                <SettingItem
                  icon={Palette}
                  label={t('settingsPage.appearance.accentColor')}
                  description={t('settingsPage.appearance.accentColorDesc')}
                >
                  <div className="flex gap-2">
                    {['red', 'cyan', 'amber', 'green', 'purple'].map((color) => (
                      <button
                        key={color}
                        onClick={() => setSetting('accentColor', color)}
                        className={cn(
                          'w-8 h-8 rounded-full transition-transform hover:scale-110',
                          color === 'red' && 'bg-accent-red',
                          color === 'cyan' && 'bg-accent-cyan',
                          color === 'amber' && 'bg-accent-amber',
                          color === 'green' && 'bg-green-500',
                          color === 'purple' && 'bg-purple-500',
                          preferences.accentColor === color &&
                            'ring-2 ring-white ring-offset-2 ring-offset-retro-dark'
                        )}
                        aria-label={t('settingsPage.appearance.colorAriaLabel', { color })}
                      >
                        {preferences.accentColor === color && (
                          <Check className="mx-auto text-white" size={16} />
                        )}
                      </button>
                    ))}
                  </div>
                </SettingItem>

                {/* Compact Mode */}
                <SettingItem
                  icon={Smartphone}
                  label={t('settingsPage.appearance.compactMode')}
                  description={t('settingsPage.appearance.compactModeDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.compactMode}
                    onChange={() => toggleSetting('compactMode')}
                  />
                </SettingItem>

                <SettingItem
                  icon={Sparkles}
                  label={t('settingsPage.appearance.premiumUI')}
                  description={t('settingsPage.appearance.premiumUIDesc')}
                >
                  <ToggleSwitch
                    checked={!!preferences.premiumUI}
                    onChange={() => updatePreferences({ premiumUI: !preferences.premiumUI })}
                  />
                </SettingItem>
              </div>
            )}

            {/* Playback */}
            {activeSection === 'playback' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.playback.title')}
                </h2>

                {/* Autoplay */}
                <SettingItem
                  icon={RefreshCw}
                  label={t('settingsPage.playback.autoplay')}
                  description={t('settingsPage.playback.autoplayDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.autoplay !== false}
                    onChange={() => toggleSetting('autoplay')}
                  />
                </SettingItem>

                {/* Default Quality */}
                <SettingItem
                  icon={Monitor}
                  label={t('settingsPage.playback.defaultQuality')}
                  description={t('settingsPage.playback.defaultQualityDesc')}
                >
                  <select
                    value={preferences.defaultQuality || 'auto'}
                    onChange={(e) => setSetting('defaultQuality', e.target.value)}
                    className="bg-retro-dark border border-retro-gray rounded-lg
                             px-3 py-2 text-fluid-sm"
                  >
                    <option value="auto">Auto</option>
                    <option value="2160p">4K (2160p)</option>
                    <option value="1080p">Full HD (1080p)</option>
                    <option value="720p">HD (720p)</option>
                    <option value="480p">SD (480p)</option>
                  </select>
                </SettingItem>

                {/* Muted Start */}
                <SettingItem
                  icon={preferences.mutedStart ? VolumeX : Volume2}
                  label={t('settingsPage.playback.mutedStart')}
                  description={t('settingsPage.playback.mutedStartDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.mutedStart}
                    onChange={() => toggleSetting('mutedStart')}
                  />
                </SettingItem>

                {/* Subtitles */}
                <SettingItem
                  icon={Languages}
                  label={t('settingsPage.playback.subtitles')}
                  description={t('settingsPage.playback.subtitlesDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.subtitles}
                    onChange={() => toggleSetting('subtitles')}
                  />
                </SettingItem>
              </div>
            )}

            {/* Notifications */}
            {activeSection === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.notifications.title')}
                </h2>

                {/* Push Notifications */}
                <SettingItem
                  icon={Bell}
                  label={t('settingsPage.notifications.push')}
                  description={t('settingsPage.notifications.pushDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.pushNotifications}
                    onChange={() => toggleSetting('pushNotifications')}
                  />
                </SettingItem>

                {/* Email Notifications */}
                <SettingItem
                  icon={Bell}
                  label={t('settingsPage.notifications.email')}
                  description={t('settingsPage.notifications.emailDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.emailNotifications}
                    onChange={() => toggleSetting('emailNotifications')}
                  />
                </SettingItem>
              </div>
            )}

            {/* Privacy */}
            {activeSection === 'privacy' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.privacy.title')}
                </h2>

                {/* Watch History */}
                <SettingItem
                  icon={Shield}
                  label={t('settingsPage.privacy.saveHistory')}
                  description={t('settingsPage.privacy.saveHistoryDesc')}
                >
                  <ToggleSwitch
                    checked={preferences.saveHistory !== false}
                    onChange={() => toggleSetting('saveHistory')}
                  />
                </SettingItem>

                {/* Clear History */}
                <SettingItem
                  icon={Trash2}
                  label={t('settingsPage.privacy.clearHistory')}
                  description={t('settingsPage.privacy.clearHistoryDesc')}
                >
                  <button
                    onClick={() => {
                      clearHistory?.();
                      alert(t('settingsPage.privacy.historyCleared'));
                    }}
                    className="btn btn-outline text-accent-red border-accent-red/50 
                             hover:bg-accent-red/10"
                  >
                    {t('settingsPage.privacy.deleteBtn')}
                  </button>
                </SettingItem>

                {/* Clear All Data */}
                <SettingItem
                  icon={Trash2}
                  label={t('settingsPage.privacy.clearAllData')}
                  description={t('settingsPage.privacy.clearAllDataDesc')}
                >
                  <button
                    onClick={() => setShowClearDataConfirm(true)}
                    className="btn btn-outline text-accent-red border-accent-red/50 
                             hover:bg-accent-red/10"
                  >
                    {t('settingsPage.privacy.resetBtn')}
                  </button>
                </SettingItem>

                {/* Export Data */}
                <SettingItem
                  icon={Download}
                  label={t('settingsPage.privacy.exportData')}
                  description={t('settingsPage.privacy.exportDataDesc')}
                >
                  <button
                    onClick={() => {
                      const data = {
                        preferences,
                        watchlist: JSON.parse(localStorage.getItem('watchlist') || '[]'),
                        history: JSON.parse(localStorage.getItem('continueWatching') || '[]'),
                      };
                      const blob = new Blob([JSON.stringify(data, null, 2)], {
                        type: 'application/json',
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'remaike-tv-data.json';
                      a.click();
                    }}
                    className="btn btn-outline"
                  >
                    {t('settingsPage.privacy.exportBtn')}
                  </button>
                </SettingItem>
              </div>
            )}

            {/* About */}
            {activeSection === 'about' && (
              <div className="space-y-6">
                <h2 className="text-fluid-xl font-semibold mb-4">
                  {t('settingsPage.about.title')}
                </h2>

                <div className="bg-retro-dark rounded-lg p-6 text-center">
                  <div className="text-4xl mb-4">📺</div>
                  <h3 className="text-fluid-lg font-display mb-2">remAIke.TV</h3>
                  <p className="text-fluid-sm text-retro-muted mb-4">
                    {t('settingsPage.about.subtitle')}
                  </p>
                  <p className="text-fluid-xs text-retro-muted">
                    {t('settingsPage.about.version')} 0.1.0 (Alpha)
                  </p>
                </div>

                <div className="space-y-3">
                  <AboutLink label={t('settingsPage.about.documentation')} href="/docs" />
                  <AboutLink
                    label={t('settingsPage.about.github')}
                    href="https://github.com/remaike/tv"
                    external
                  />
                  <AboutLink label={t('settingsPage.about.changelog')} href="/changelog" />
                  <AboutLink label={t('settingsPage.about.license')} href="/license" />
                  <AboutLink label={t('settingsPage.about.privacyPolicy')} href="/privacy" />
                  <AboutLink label={t('settingsPage.about.imprint')} href="/impressum" />
                </div>

                <div className="text-center pt-4 border-t border-retro-gray/30">
                  <p className="text-fluid-xs text-retro-muted">
                    {t('settingsPage.about.madeWith')}
                  </p>
                  <p className="text-fluid-xs text-retro-muted mt-1">
                    © {new Date().getFullYear()} {t('settingsPage.about.copyright')}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Clear Data Confirmation Modal */}
      {showClearDataConfirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4
                       bg-black/80 backdrop-blur-sm animate-fade-in"
        >
          <div
            className="bg-retro-dark border border-retro-gray rounded-xl 
                        max-w-sm w-full p-6 shadow-2xl animate-scale-in"
          >
            <h3 className="text-fluid-xl font-semibold mb-2">{t('settingsPage.reset.title')}</h3>
            <p className="text-retro-muted mb-6">{t('settingsPage.reset.message')}</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowClearDataConfirm(false)}
                className="btn btn-outline flex-1"
              >
                {t('settingsPage.reset.cancel')}
              </button>
              <button
                onClick={handleClearData}
                className="btn bg-accent-red hover:bg-accent-red/80 flex-1"
              >
                {t('settingsPage.reset.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Setting item wrapper component
function SettingItem({ icon: Icon, label, description, children }) {
  return (
    <div
      className="flex items-center justify-between gap-4 py-3 
                   border-b border-retro-gray/20 last:border-0"
    >
      <div className="flex items-start gap-3">
        {Icon && <Icon className="text-retro-muted mt-0.5 shrink-0" size={20} />}
        <div>
          <h3 className="text-fluid-base font-medium">{label}</h3>
          {description && <p className="text-fluid-sm text-retro-muted">{description}</p>}
        </div>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

// Toggle switch component
function ToggleSwitch({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className={cn(
        'relative w-12 h-6 rounded-full transition-colors',
        checked ? 'bg-accent-red' : 'bg-retro-gray'
      )}
    >
      <span
        className={cn(
          'absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform',
          checked && 'translate-x-6'
        )}
      />
    </button>
  );
}

// About link component
function AboutLink({ label, href, external }) {
  const Component = external ? 'a' : 'a';
  return (
    <Component
      href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      className="flex items-center justify-between p-3 rounded-lg
               bg-retro-dark/50 hover:bg-retro-dark transition-colors group"
    >
      <span className="text-fluid-sm">{label}</span>
      <ChevronRight
        className="text-retro-muted group-hover:text-white transition-colors"
        size={18}
      />
    </Component>
  );
}
