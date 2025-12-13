import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Tv,
  Clock,
  Heart,
  Settings,
  X,
  Star,
  ChevronDown,
  ChevronRight,
  Trophy,
  Zap,
  History,
  Radio,
  Smartphone,
  Library,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { DECADES, CATEGORIES, MILESTONE_TYPES } from '../../data/remaikeData';
import { useTranslation } from 'react-i18next';

// Navigation keys for i18n
const mainNavKeys = [
  { href: '/', labelKey: 'sidebar.start', icon: Home },
  { href: '/browse', labelKey: 'sidebar.allVideos', icon: Tv },
  { href: '/series', labelKey: 'sidebar.series', icon: Library },
  { href: '/shorts', labelKey: 'sidebar.shorts', icon: Smartphone },
  { href: '/timeline', labelKey: 'sidebar.timeline', icon: History },
  { href: '/sender', labelKey: 'sidebar.sender', icon: Radio },
];

const collectionsKeys = [
  { href: '/watchlist', labelKey: 'sidebar.myList', icon: Heart },
  { href: '/history', labelKey: 'sidebar.watchHistory', icon: Clock },
];

const quickFiltersKeys = [
  { href: '/browse?filter=world-firsts', labelKey: 'sidebar.worldFirsts', icon: Trophy },
  { href: '/browse?filter=iconic', labelKey: 'sidebar.iconicMoments', icon: Star },
  { href: '/browse?filter=new', labelKey: 'sidebar.newlyAdded', icon: Zap },
];

// Category ID to i18n key mapping
const categoryI18nKeys = {
  'classic-films': 'categories.classicFilms',
  cartoons: 'categories.cartoonsAnimation',
  documentaries: 'categories.documentaries',
  propaganda: 'categories.propaganda',
  comedy: 'categories.comedySketches',
  christmas: 'categories.christmasSpecials',
  commercials: 'categories.commercials',
};

// Milestone ID to i18n key mapping
const milestoneI18nKeys = {
  'world-first': 'milestones.worldFirsts',
  'iconic-moment': 'milestones.iconicMoments',
  documentary: 'milestones.documentaries',
};

/**
 * Internal Content Component to avoid duplication
 */
function SidebarContent({ onClose, expandedSections, toggleSection, isActive }) {
  const { t } = useTranslation();

  return (
    <nav className="space-y-6">
      {/* Main Navigation */}
      <div className="px-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          {t('sidebar.navigation')}
        </h3>
        <ul className="space-y-1">
          {mainNavKeys.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                onClick={onClose}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg',
                  'text-fluid-sm font-medium transition-all duration-200',
                  isActive(item.href)
                    ? 'bg-accent-gold/10 text-accent-gold border-l-2 border-accent-gold'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                )}
              >
                <item.icon size={20} />
                {t(item.labelKey)}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* Quick Filters */}
      <div className="px-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          {t('sidebar.highlights')}
        </h3>
        <ul className="space-y-1">
          {quickFiltersKeys.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                onClick={onClose}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg
                         text-fluid-sm text-gray-400 hover:bg-white/5 hover:text-white transition-colors"
              >
                <item.icon size={18} className="text-accent-gold" />
                {t(item.labelKey)}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* Decades - Expandable */}
      <div className="px-4">
        <button
          onClick={() => toggleSection('decades')}
          className="flex items-center justify-between w-full text-left mb-2 hover:text-white transition-colors"
        >
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            {t('sidebar.byDecade')}
          </h3>
          {expandedSections.decades ? (
            <ChevronDown size={16} className="text-gray-500" />
          ) : (
            <ChevronRight size={16} className="text-gray-500" />
          )}
        </button>
        {expandedSections.decades && (
          <ul className="space-y-1 animate-in slide-in-from-top-2 duration-200 pl-2 border-l border-white/10 ml-2">
            {DECADES.map((decade) => (
              <li key={decade.id}>
                <Link
                  to={`/browse?decade=${decade.id}`}
                  onClick={onClose}
                  className="flex items-center justify-between px-3 py-2 rounded-lg
                           text-fluid-sm text-gray-400 hover:bg-white/5 hover:text-white transition-colors group"
                >
                  <span className="flex items-center gap-2">
                    <span>{decade.icon}</span>
                    <span>{decade.label}</span>
                  </span>
                  <span className="text-xs text-gray-600 group-hover:text-white">
                    {decade.range[0]}–{decade.range[1]}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Categories - Expandable */}
      <div className="px-4">
        <button
          onClick={() => toggleSection('categories')}
          className="flex items-center justify-between w-full text-left mb-2 hover:text-white transition-colors"
        >
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            {t('sidebar.byCategory')}
          </h3>
          {expandedSections.categories ? (
            <ChevronDown size={16} className="text-gray-500" />
          ) : (
            <ChevronRight size={16} className="text-gray-500" />
          )}
        </button>
        {expandedSections.categories && (
          <ul className="space-y-1 animate-in slide-in-from-top-2 duration-200 pl-2 border-l border-white/10 ml-2">
            {CATEGORIES.map((category) => {
              const labelKey = categoryI18nKeys[category.id];
              return (
                <li key={category.id}>
                  <Link
                    to={`/browse?category=${category.id}`}
                    onClick={onClose}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg
                             text-fluid-sm text-gray-400 hover:bg-white/5 hover:text-white transition-colors"
                  >
                    <span>{category.icon}</span>
                    <span>{labelKey ? t(labelKey) : category.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Milestones - Expandable */}
      <div className="px-4">
        <button
          onClick={() => toggleSection('milestones')}
          className="flex items-center justify-between w-full text-left mb-2 hover:text-white transition-colors"
        >
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            {t('sidebar.milestones')}
          </h3>
          {expandedSections.milestones ? (
            <ChevronDown size={16} className="text-gray-500" />
          ) : (
            <ChevronRight size={16} className="text-gray-500" />
          )}
        </button>
        {expandedSections.milestones && (
          <ul className="space-y-1 animate-in slide-in-from-top-2 duration-200 pl-2 border-l border-white/10 ml-2">
            {MILESTONE_TYPES.map((milestone) => {
              const labelKey = milestoneI18nKeys[milestone.id];
              return (
                <li key={milestone.id}>
                  <Link
                    to={`/browse?milestone=${milestone.id}`}
                    onClick={onClose}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg
                             text-fluid-sm text-gray-400 hover:bg-white/5 hover:text-white transition-colors"
                  >
                    <span>{milestone.icon}</span>
                    <span>{labelKey ? t(labelKey) : milestone.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Collections */}
      <div className="px-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          {t('sidebar.myCollection')}
        </h3>
        <ul className="space-y-1">
          {collectionsKeys.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                onClick={onClose}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg',
                  'text-fluid-sm transition-all duration-200',
                  isActive(item.href)
                    ? 'bg-accent-gold/10 text-accent-gold border-l-2 border-accent-gold'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                )}
              >
                <item.icon size={18} />
                {t(item.labelKey)}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* Footer Links */}
      <div className="px-4 pt-4 border-t border-white/10">
        <Link
          to="/settings"
          onClick={onClose}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg
                   text-fluid-sm text-gray-500 hover:text-white hover:bg-white/5 transition-colors"
        >
          <Settings size={18} />
          {t('sidebar.settings')}
        </Link>
      </div>
    </nav>
  );
}

/**
 * Sidebar Component - Handles both Mobile Drawer and Desktop Sidebar
 *
 * @param {Object} props
 * @param {'mobile' | 'desktop'} props.variant - Display mode
 */
export default function Sidebar({ variant = 'mobile' }) {
  const location = useLocation();
  const { isSidebarOpen, setIsSidebarOpen } = useApp();

  // Expandable sections state
  const [expandedSections, setExpandedSections] = useState({
    decades: false,
    categories: false,
    milestones: false,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname === href || location.pathname.startsWith(href.split('?')[0]);
  };

  const closeSidebar = () => setIsSidebarOpen(false);

  // Desktop Variant
  if (variant === 'desktop') {
    return (
      <aside className="hidden lg:flex flex-col w-64 h-[calc(100vh-4.5rem)] sticky top-[4.5rem] border-r border-white/10 bg-black/50 backdrop-blur-sm overflow-y-auto custom-scrollbar">
        <div className="py-6">
          <SidebarContent
            onClose={undefined}
            expandedSections={expandedSections}
            toggleSection={toggleSection}
            isActive={isActive}
          />
        </div>
      </aside>
    );
  }

  // Mobile Variant (Drawer)
  return (
    <>
      {/* Overlay */}
      <div
        onClick={closeSidebar}
        className={cn(
          'fixed inset-0 z-40 bg-black/80 backdrop-blur-sm transition-opacity duration-300 lg:hidden',
          isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
      />

      {/* Sidebar Drawer */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-72 sm:w-80',
          'bg-[#0a0a0b] border-r border-white/10',
          'transform transition-transform duration-300 ease-out',
          'flex flex-col',
          'lg:hidden', // Hide on desktop
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <Link to="/" onClick={closeSidebar} className="font-display text-2xl text-accent-gold">
            remAIke.TV
          </Link>
          <button
            onClick={closeSidebar}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Menü schließen"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-4">
          <SidebarContent
            onClose={closeSidebar}
            expandedSections={expandedSections}
            toggleSection={toggleSection}
            isActive={isActive}
          />
        </div>
      </aside>
    </>
  );
}
