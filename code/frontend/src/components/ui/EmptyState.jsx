import { Film, Search, Clock, Bookmark, History, Inbox, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/utils';

/**
 * EmptyState - Reusable empty state display component
 *
 * Variants:
 * - videos: No videos in category/list
 * - search: No search results
 * - watchlist: Empty watchlist
 * - history: No watch history
 * - generic: General empty state
 */
export function EmptyState({
  variant = 'generic',
  title,
  message,
  actionLabel,
  actionHref,
  onAction,
  className,
}) {
  const variants = {
    videos: {
      icon: Film,
      defaultTitle: 'Keine Videos',
      defaultMessage: 'In dieser Kategorie sind noch keine Videos verfügbar.',
      defaultAction: 'Alle Videos durchsuchen',
      defaultHref: '/',
    },
    search: {
      icon: Search,
      defaultTitle: 'Keine Ergebnisse',
      defaultMessage:
        'Für deine Suche wurden keine Videos gefunden. Versuche einen anderen Suchbegriff.',
      defaultAction: 'Zur Mediathek',
      defaultHref: '/',
    },
    watchlist: {
      icon: Bookmark,
      defaultTitle: 'Watchlist ist leer',
      defaultMessage:
        'Du hast noch keine Videos zu deiner Watchlist hinzugefügt. Stöbere in der Mediathek und speichere interessante Filme.',
      defaultAction: 'Videos entdecken',
      defaultHref: '/',
    },
    history: {
      icon: History,
      defaultTitle: 'Noch nichts angeschaut',
      defaultMessage: 'Dein Verlauf ist leer. Schau dir ein Video an und es erscheint hier.',
      defaultAction: 'Jetzt stöbern',
      defaultHref: '/',
    },
    continueWatching: {
      icon: Clock,
      defaultTitle: 'Weiterschauen',
      defaultMessage:
        'Du hast noch keine Videos angefangen. Starte ein Video und setze es später hier fort.',
      defaultAction: null,
      defaultHref: null,
    },
    generic: {
      icon: Inbox,
      defaultTitle: 'Hier ist noch nichts',
      defaultMessage: 'Dieser Bereich ist noch leer.',
      defaultAction: 'Zur Startseite',
      defaultHref: '/',
    },
  };

  const config = variants[variant] || variants.generic;
  const Icon = config.icon;

  const finalActionLabel = actionLabel ?? config.defaultAction;
  const finalActionHref = actionHref ?? config.defaultHref;

  return (
    <div
      className={cn('flex flex-col items-center justify-center py-12 px-4 text-center', className)}
    >
      {/* Icon with animated ring */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center">
          <Icon size={36} className="text-retro-muted" />
        </div>
        <div
          className="absolute inset-0 rounded-full border-2 border-dashed border-white/10 animate-spin"
          style={{ animationDuration: '20s' }}
        />
      </div>

      {/* Title */}
      <h3 className="text-lg md:text-xl font-display font-bold text-white mb-2">
        {title || config.defaultTitle}
      </h3>

      {/* Message */}
      <p className="text-retro-muted text-sm md:text-base max-w-sm mb-6">
        {message || config.defaultMessage}
      </p>

      {/* Action */}
      {finalActionLabel &&
        (finalActionHref || onAction) &&
        (onAction ? (
          <button
            onClick={onAction}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent-gold text-black font-semibold rounded-lg hover:bg-accent-amber transition-all text-sm"
          >
            <Plus size={16} />
            {finalActionLabel}
          </button>
        ) : (
          <Link
            to={finalActionHref}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent-gold text-black font-semibold rounded-lg hover:bg-accent-amber transition-all text-sm"
          >
            {finalActionLabel}
          </Link>
        ))}
    </div>
  );
}

/**
 * CompactEmptyState - Smaller empty state for inline use
 */
export function CompactEmptyState({ icon: CustomIcon, message, className }) {
  const Icon = CustomIcon || Inbox;

  return (
    <div
      className={cn('flex items-center justify-center gap-3 py-8 px-4 text-retro-muted', className)}
    >
      <Icon size={20} className="opacity-50" />
      <p className="text-sm">{message || 'Keine Inhalte verfügbar'}</p>
    </div>
  );
}

export default EmptyState;
