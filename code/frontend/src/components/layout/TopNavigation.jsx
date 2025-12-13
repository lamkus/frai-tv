import { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Search,
  Bell,
  Settings,
  User,
  Zap,
  Play,
  Clock,
  ChevronDown,
  Home,
  Film,
  List,
  History,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { SocialIconsDesktop, SocialIconsMobile } from '../ui/SocialButtons';
import { youtubeService } from '../../data/youtubeService';

/**
 * TopNavigation - Netflix/Disney+ style navigation
 *
 * DESIGN RESEARCH (NNGroup, Netflix, Disney+):
 * - Desktop: Horizontal top bar, Logo left, Nav center-left, Actions right
 * - Mobile: Hamburger menu OR bottom tab bar (we use bottom tabs for discoverability)
 * - Mega menus: 0.5s hover delay, show all options at once
 * - Touch targets: minimum 44px for accessibility
 */
export default function TopNavigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, setSearchQuery, language, setLanguage } = useApp();
  const [searchValue, setSearchValue] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [latestUploads, setLatestUploads] = useState([]);
  const notificationRef = useRef(null);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  // Fetch latest 3 videos from YouTube API
  useEffect(() => {
    async function fetchLatestVideos() {
      try {
        const videos = await youtubeService.getLatestVideos(3);
        setLatestUploads(videos);
      } catch (err) {
        console.warn('Could not load latest uploads:', err);
      }
    }
    fetchLatestVideos();
  }, []);

  // Close notification dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Feature flags for experimental/admin features
  const SHOW_EXPERIMENTAL = import.meta.env.VITE_EXPERIMENTAL_FEATURES === 'true';
  const SHOW_ADMIN = import.meta.env.VITE_ENABLE_ADMIN === 'true';

  // Main navigation categories - FRai.TV specific (Home removed, Mediathek is now /)
  const navCategories = [
    { href: '/', label: 'Mediathek' },
    { href: '/sender', label: 'Sender' },
    { href: '/browse', label: 'Videos' },
    // Explore only in experimental mode
    ...(SHOW_EXPERIMENTAL ? [{ href: '/explore', label: 'Explore', experimental: true }] : []),
    { href: '/timeline', label: 'Timeline' },
    { href: '/watchlist', label: 'Watchlist' },
    // Admin only when enabled
    ...(SHOW_ADMIN ? [{ href: '/admin', label: 'Admin' }] : []),
  ];

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/' && !location.search;
    return location.pathname + location.search === href;
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchValue.trim()) {
      setSearchQuery(searchValue);
      navigate(`/search?q=${encodeURIComponent(searchValue)}`);
    }
  };

  const languages = [
    { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'fr', label: 'Français', flag: '🇫🇷' },
  ];

  const currentLang = languages.find((l) => l.code === language) || languages[0];

  return (
    <header className="sticky top-0 z-50 bg-retro-black/95 backdrop-blur-md border-b border-retro-gray/30 safe-top">
      <div className="flex items-center justify-between h-14 sm:h-16 lg:h-18 px-3 sm:px-4 lg:px-6 xl:px-8">
        {/* Left: Logo */}
        <div className="flex items-center gap-4 lg:gap-8">
          <Link
            to="/"
            className="flex items-center gap-2 group"
            tabIndex={0}
            aria-label="frai.tv Home"
          >
            {/* Lightning Logo */}
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-gradient-to-br from-accent-amber to-orange-600 flex items-center justify-center shadow-lg group-hover:shadow-amber-500/30 transition-shadow">
              <Zap size={20} className="text-black sm:hidden" fill="black" />
              <Zap size={24} className="text-black hidden sm:block" fill="black" />
            </div>
            <div className="hidden xs:block">
              <span className="text-xl sm:text-2xl font-bold">
                <span className="text-accent-amber">FRAI</span>
                <span className="text-white">.TV</span>
              </span>
              <p className="text-[10px] text-retro-muted -mt-1">FREE AI Enhanced TV</p>
            </div>
          </Link>

          {/* Navigation Tabs */}
          <nav
            className="hidden lg:flex items-center gap-1"
            role="navigation"
            aria-label="Hauptnavigation"
          >
            {navCategories.map((item, index) => (
              <Link
                key={item.href}
                to={item.href}
                tabIndex={0}
                data-nav-index={index}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-accent-amber focus:ring-offset-2 focus:ring-offset-retro-black',
                  isActive(item.href)
                    ? 'text-accent-amber bg-accent-amber/10'
                    : 'text-retro-muted hover:text-white hover:bg-white/5'
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Right: Search & User */}
        <div className="flex items-center gap-4">
          {/* Social Media Icons (Desktop) */}
          <div className="hidden md:flex items-center gap-3 mr-2">
            <div
              className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full animate-pulse"
              style={{
                background: 'linear-gradient(135deg, #ff0033 0%, #cc0028 50%, #990020 100%)',
                color: '#fff',
                fontSize: '11px',
                fontWeight: '800',
                letterSpacing: '1px',
                textTransform: 'uppercase',
                border: '1px solid rgba(255,0,51,0.6)',
                boxShadow:
                  '0 0 20px rgba(255,0,51,0.5), 0 0 40px rgba(255,0,51,0.25), 0 4px 15px rgba(0,0,0,0.4)',
              }}
            >
              <span
                className="w-2 h-2 bg-white rounded-full animate-ping"
                style={{ animationDuration: '1.5s' }}
              />
              <span>OPEN BETA</span>
            </div>
          </div>
          <SocialIconsDesktop />

          {/* Language Switcher */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowLanguageMenu((prev) => !prev)}
              className="flex items-center gap-2 px-3 py-2 rounded-full bg-retro-dark border border-retro-gray/50 text-xs text-white hover:border-accent-amber hover:text-accent-amber transition-colors"
              aria-label="Sprache wechseln"
            >
              <span className="text-lg leading-none">{currentLang.flag}</span>
              <span className="font-semibold hidden sm:inline">
                {currentLang.code.toUpperCase()}
              </span>
              <ChevronDown size={14} className="text-retro-muted" />
            </button>

            {showLanguageMenu && (
              <div className="absolute right-0 mt-2 w-32 bg-retro-dark border border-retro-gray/60 rounded-lg shadow-xl z-50 overflow-hidden">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setShowLanguageMenu(false);
                    }}
                    className={cn(
                      'w-full text-left px-3 py-2 text-sm hover:bg-white/5 transition-colors flex items-center',
                      language === lang.code ? 'text-accent-amber' : 'text-white'
                    )}
                  >
                    <span className="mr-2 text-lg">{lang.flag}</span>
                    {lang.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Search */}
          <form onSubmit={handleSearch} className="hidden sm:block">
            <div className="relative">
              <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted"
              />
              <input
                type="search"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Search for movies, series, and more..."
                className="w-64 lg:w-80 bg-retro-dark border border-retro-gray/50 rounded-full
                         pl-10 pr-4 py-2 text-sm text-white
                         placeholder:text-retro-muted
                         focus:outline-none focus:border-accent-amber focus:ring-1 focus:ring-accent-amber"
              />
            </div>
          </form>

          {/* Mobile Search */}
          <button className="sm:hidden p-2 text-retro-muted hover:text-white">
            <Search size={20} />
          </button>

          {/* Mobile SocialIcons (subscribe pill & round icons for small screens) */}
          <div className="sm:hidden flex items-center gap-2">
            <span
              className="open-beta-badge sm:hidden inline-flex items-center gap-2 px-2 py-1 rounded-full text-xs font-semibold bg-red-600 text-white"
              style={{
                background: 'linear-gradient(135deg,#ff0033 0%,#cc0028 50%,#990020 100%)',
                paddingLeft: '8px',
                paddingRight: '8px',
              }}
            >
              <span
                className="dot"
                style={{ width: 8, height: 8, background: '#fff', borderRadius: 8 }}
              />
              OPEN BETA
            </span>
            <SocialIconsMobile />
          </div>

          {/* Notifications Dropdown */}
          <div className="relative" ref={notificationRef}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-retro-muted hover:text-white transition-colors"
            >
              <Bell size={20} />
              {latestUploads.length > 0 && (
                <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-accent-amber rounded-full animate-pulse shadow-lg shadow-accent-amber/50" />
              )}
            </button>

            {/* Notification Dropdown Panel */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-retro-dark border border-retro-gray/50 rounded-xl shadow-2xl shadow-black/50 overflow-hidden z-50">
                <div className="px-4 py-3 bg-gradient-to-r from-accent-gold/10 to-accent-amber/5 border-b border-retro-gray/30">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Clock size={14} className="text-accent-amber" />
                    Neue Uploads
                  </h3>
                </div>
                <div className="divide-y divide-retro-gray/20">
                  {latestUploads.length > 0 ? (
                    latestUploads.map((video) => (
                      <Link
                        key={video.ytId || video.id}
                        to={`/video/${video.ytId || video.id}`}
                        onClick={() => setShowNotifications(false)}
                        className="flex items-start gap-3 p-3 hover:bg-white/5 transition-colors group"
                      >
                        {/* Thumbnail */}
                        <div className="relative w-24 h-14 rounded-lg overflow-hidden flex-shrink-0 bg-retro-gray/30">
                          <img
                            src={
                              video.thumbnail ||
                              `https://img.youtube.com/vi/${video.ytId || video.id}/mqdefault.jpg`
                            }
                            alt={video.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                          />
                          <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Play size={16} className="text-white" fill="white" />
                          </div>
                        </div>
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-white font-medium line-clamp-2 leading-snug">
                            {video.title}
                          </p>
                          <p className="text-[10px] text-retro-muted mt-1">
                            {video.publishedAt
                              ? new Date(video.publishedAt).toLocaleDateString('de-DE')
                              : 'Neu'}
                          </p>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="p-6 text-center text-retro-muted text-sm">
                      Keine neuen Videos verfügbar
                    </div>
                  )}
                </div>
                <Link
                  to="/browse"
                  onClick={() => setShowNotifications(false)}
                  className="block px-4 py-3 text-center text-xs text-accent-amber hover:bg-accent-amber/10 transition-colors border-t border-retro-gray/30"
                >
                  Alle Videos ansehen →
                </Link>
              </div>
            )}
          </div>

          {/* User Avatar */}
          <Link
            to="/settings"
            className="flex items-center gap-2"
            aria-label="Benutzereinstellungen"
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-accent-amber to-orange-600 flex items-center justify-center overflow-hidden ring-2 ring-transparent hover:ring-accent-amber transition-all">
              {user?.picture ? (
                <img
                  src={user.picture}
                  alt="Benutzer Avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <User size={18} className="text-black" />
              )}
            </div>
          </Link>

          {/* Settings */}
          <Link
            to="/settings"
            className="hidden sm:block p-2 text-retro-muted hover:text-white"
            aria-label="Einstellungen"
          >
            <Settings size={20} />
          </Link>
        </div>
      </div>

      {/* Mobile: Hamburger Menu Overlay */}
      {showMobileMenu && (
        <div className="lg:hidden fixed inset-0 z-50 bg-retro-black/98 backdrop-blur-xl">
          <div className="flex flex-col h-full">
            {/* Close Button */}
            <div className="flex justify-between items-center p-4 border-b border-retro-gray/20">
              <Link
                to="/"
                className="flex items-center gap-2"
                onClick={() => setShowMobileMenu(false)}
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-amber to-orange-600 flex items-center justify-center">
                  <Zap size={18} className="text-black" fill="black" />
                </div>
                <span className="text-xl font-bold">
                  <span className="text-accent-amber">frai</span>
                  <span className="text-white">.tv</span>
                </span>
              </Link>
              <button
                onClick={() => setShowMobileMenu(false)}
                className="p-2 text-retro-muted hover:text-white"
              >
                <X size={24} />
              </button>
            </div>

            {/* Menu Items */}
            <nav className="flex-1 overflow-y-auto py-4">
              {navCategories.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setShowMobileMenu(false)}
                  className={cn(
                    'flex items-center gap-4 px-6 py-4 text-lg font-medium transition-colors',
                    isActive(item.href)
                      ? 'text-accent-amber bg-accent-amber/10 border-l-4 border-accent-amber'
                      : 'text-white hover:bg-white/5'
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* Language & Settings */}
            <div className="p-4 border-t border-retro-gray/20">
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => setLanguage(lang.code)}
                      className={cn(
                        'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                        language === lang.code
                          ? 'bg-accent-amber text-black'
                          : 'bg-retro-dark text-white'
                      )}
                    >
                      {lang.label}
                    </button>
                  ))}
                </div>
                <Link
                  to="/settings"
                  onClick={() => setShowMobileMenu(false)}
                  className="p-2 text-retro-muted hover:text-white"
                >
                  <Settings size={24} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

/**
 * MobileBottomNav - Fixed bottom navigation for mobile
 *
 * Best Practice (Disney+, TikTok, Instagram):
 * - 4-5 main items max
 * - Icons + Labels
 * - Active state clearly visible
 * - Fixed at bottom for thumb accessibility
 */
export function MobileBottomNav() {
  const location = useLocation();

  const navItems = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/browse', label: 'Videos', icon: Film },
    { href: '/timeline', label: 'Timeline', icon: History },
    { href: '/watchlist', label: 'Liste', icon: List },
    { href: '/settings', label: 'Mehr', icon: Menu },
  ];

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    if (href === '/settings') {
      return ['/settings', '/history', '/admin'].some((p) => location.pathname.startsWith(p));
    }
    return location.pathname.startsWith(href);
  };

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-retro-black/95 backdrop-blur-md border-t border-retro-gray/30 safe-bottom">
      <div className="flex items-center justify-around h-16 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex flex-col items-center justify-center gap-1 flex-1 py-2 min-h-[56px] transition-colors',
                active ? 'text-accent-amber' : 'text-retro-muted'
              )}
            >
              <Icon size={22} className={active ? 'text-accent-amber' : ''} />
              <span
                className={cn(
                  'text-[10px] font-medium',
                  active ? 'text-accent-amber' : 'text-retro-muted'
                )}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
