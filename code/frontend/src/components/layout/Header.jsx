import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Menu,
  X,
  Search,
  Home,
  Tv,
  Clock,
  Heart,
  Settings,
  ChevronDown,
  User,
  Radio,
  Youtube,
  Instagram,
  ExternalLink,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useApp } from '../../context/AppContext';

/**
 * Header Component - Responsive navigation for remAIke.TV
 *
 * Features:
 * - Sticky header with blur on scroll
 * - Responsive navigation (hamburger on mobile)
 * - Search integration
 * - User menu
 */
export default function Header() {
  const location = useLocation();
  const { setSearchQuery, setIsSidebarOpen, isSidebarOpen, user, promptGoogleSignIn, signOut } =
    useApp();

  const [isScrolled, setIsScrolled] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [ytSubscribers, setYtSubscribers] = useState(null);

  // Fetch YouTube subscriber count (using public API or mock)
  useEffect(() => {
    // TODO: Replace with actual YouTube API call when API key is available
    // For now, simulate a realistic subscriber count
    const fetchSubscribers = async () => {
      try {
        // Mock data - replace with actual API call:
        // const response = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=statistics&id=CHANNEL_ID&key=API_KEY`);
        // const data = await response.json();
        // setYtSubscribers(data.items[0].statistics.subscriberCount);

        // Demo value (simulate ~12.3k subscribers)
        setYtSubscribers(12347);
      } catch (error) {
        console.warn('Could not fetch YouTube subscribers:', error);
      }
    };
    fetchSubscribers();
  }, []);

  // Handle scroll for header transparency
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Navigation items
  const navItems = [
    { href: '/', label: 'Start', icon: Home },
    { href: '/browse', label: 'Durchsuchen', icon: Tv },
    { href: '/live', label: 'Live', icon: Radio, badge: 'LIVE' },
    { href: '/watchlist', label: 'Merkliste', icon: Heart },
    { href: '/history', label: 'Verlauf', icon: Clock },
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchValue.trim()) {
      setSearchQuery(searchValue);
      // Navigate to search results if not already there
    }
  };

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        isScrolled
          ? 'bg-retro-black/95 backdrop-blur-md shadow-lg'
          : 'bg-gradient-to-b from-retro-black/80 to-transparent'
      )}
    >
      <div className="safe-top" />

      <nav
        className="flex items-center justify-between h-14 sm:h-16 md:h-18 lg:h-20 
                      px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24"
      >
        {/* Left: Logo & Mobile Menu */}
        <div className="flex items-center gap-4 md:gap-6">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="btn-ghost btn-icon md:hidden"
            aria-label="Menü öffnen"
          >
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <span
              className="font-display text-xl sm:text-2xl md:text-3xl 3xl:text-4xl
                           text-accent-red tracking-wider
                           group-hover:text-white transition-colors"
            >
              FRai.TV
            </span>
          </Link>

          {/* Social Media Buttons - remAIke.IT Clean Style */}
          <div className="hidden sm:flex items-center gap-1.5 ml-3">
            {/* YouTube with Live Follower Count */}
            <a
              href="https://www.youtube.com/@FRai_TV"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                         bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20
                         transition-all duration-200 group"
              title="FRai.TV auf YouTube"
            >
              <Youtube
                size={16}
                className="text-white/70 group-hover:text-red-500 transition-colors"
              />
              {ytSubscribers && (
                <span className="text-xs font-medium text-white/70 group-hover:text-white transition-colors">
                  {ytSubscribers >= 1000 ? `${(ytSubscribers / 1000).toFixed(1)}K` : ytSubscribers}
                </span>
              )}
            </a>

            {/* Instagram */}
            <a
              href="https://www.instagram.com/frai.tv"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-8 h-8 rounded-lg
                         bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20
                         transition-all duration-200 group"
              title="FRai.TV auf Instagram"
            >
              <Instagram
                size={16}
                className="text-white/70 group-hover:text-pink-400 transition-colors"
              />
            </a>

            {/* TikTok */}
            <a
              href="https://www.tiktok.com/@frai.tv"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-8 h-8 rounded-lg
                         bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20
                         transition-all duration-200 group"
              title="FRai.TV auf TikTok"
            >
              <svg
                viewBox="0 0 24 24"
                className="w-4 h-4 fill-white/70 group-hover:fill-white transition-colors"
              >
                <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
              </svg>
            </a>

            {/* X/Twitter */}
            <a
              href="https://x.com/FRai_TV"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-8 h-8 rounded-lg
                         bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20
                         transition-all duration-200 group"
              title="FRai.TV auf X"
            >
              <svg
                viewBox="0 0 24 24"
                className="w-4 h-4 fill-white/70 group-hover:fill-white transition-colors"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
          </div>

          {/* Desktop Navigation */}
          <ul className="hidden md:flex items-center gap-1 lg:gap-2 ml-4 lg:ml-8">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  to={item.href}
                  className={cn(
                    'nav-link flex items-center gap-2 px-3 py-2 text-fluid-sm font-medium',
                    isActive(item.href) && 'nav-link-active'
                  )}
                >
                  <item.icon size={18} className="3xl:w-5 3xl:h-5" />
                  <span className="hidden lg:inline">{item.label}</span>
                  {item.badge && (
                    <span className="badge badge-live text-[10px] 3xl:text-xs">{item.badge}</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Right: Search & User */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Search */}
          <div
            className={cn(
              'flex items-center transition-all duration-300',
              isSearchOpen ? 'w-48 sm:w-64 md:w-80 lg:w-96' : 'w-auto'
            )}
          >
            {isSearchOpen ? (
              <form onSubmit={handleSearch} className="relative w-full">
                <input
                  type="search"
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  placeholder="Videos suchen..."
                  autoFocus
                  className="w-full bg-retro-dark/80 border border-retro-gray rounded-full
                           px-4 py-2 pr-10 text-fluid-sm
                           focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan
                           placeholder:text-retro-muted"
                />
                <button
                  type="button"
                  onClick={() => {
                    setIsSearchOpen(false);
                    setSearchValue('');
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-retro-muted hover:text-white"
                >
                  <X size={18} />
                </button>
              </form>
            ) : (
              <button
                onClick={() => setIsSearchOpen(true)}
                className="btn-ghost btn-icon"
                aria-label="Suche öffnen"
              >
                <Search size={20} className="3xl:w-6 3xl:h-6" />
              </button>
            )}
          </div>

          {/* User Menu */}
          <div className="relative group">
            <button className="btn-ghost btn-icon flex items-center gap-2">
              <div
                className="w-8 h-8 sm:w-9 sm:h-9 3xl:w-10 3xl:h-10 
                            rounded-full bg-accent-red flex items-center justify-center overflow-hidden"
              >
                {user?.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name || user.email}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User size={18} className="3xl:w-5 3xl:h-5" />
                )}
              </div>
              <ChevronDown
                size={16}
                className="hidden sm:block text-retro-muted group-hover:text-white"
              />
            </button>

            {/* Dropdown */}
            <div
              className="absolute right-0 top-full mt-2 w-48 py-2
                          bg-retro-dark rounded-lg shadow-xl border border-retro-gray
                          opacity-0 invisible group-hover:opacity-100 group-hover:visible
                          transition-all duration-200 transform origin-top-right
                          scale-95 group-hover:scale-100"
            >
              {user ? (
                <div>
                  <Link
                    to="/profile"
                    className="flex items-center gap-3 px-4 py-2 hover:bg-retro-gray/50 text-fluid-sm"
                  >
                    <User size={16} />
                    Mein Profil
                  </Link>
                  <Link
                    to="/history"
                    className="flex items-center gap-3 px-4 py-2 hover:bg-retro-gray/50 text-fluid-sm"
                  >
                    <Clock size={16} />
                    Verlauf
                  </Link>
                  <button
                    onClick={() => signOut()}
                    className="w-full text-left px-4 py-2 hover:bg-retro-gray/50 text-fluid-sm"
                  >
                    Abmelden
                  </button>
                </div>
              ) : (
                <div>
                  <button
                    onClick={() => promptGoogleSignIn()}
                    className="flex items-center gap-3 px-4 py-2 hover:bg-retro-gray/50 text-fluid-sm w-full text-left"
                  >
                    <img
                      src="/google-icon.svg"
                      alt="Google"
                      className="w-4 h-4 inline-block mr-2"
                    />
                    Mit Google anmelden
                  </button>
                  <Link
                    to="/settings"
                    className="flex items-center gap-3 px-4 py-2 hover:bg-retro-gray/50 text-fluid-sm"
                  >
                    <Settings size={16} />
                    Einstellungen
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
}
