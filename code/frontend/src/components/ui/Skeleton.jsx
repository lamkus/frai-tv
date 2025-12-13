import { cn } from '../../lib/utils';

/**
 * Skeleton loading components
 * 
 * Used for content placeholders while loading.
 * Includes shimmer animation.
 */

/**
 * Base skeleton element
 */
export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn(
        'skeleton-shimmer rounded bg-retro-gray/30',
        className
      )}
      {...props}
    />
  );
}

/**
 * Video card skeleton
 */
export function VideoCardSkeleton({ variant = 'default' }) {
  if (variant === 'compact') {
    return (
      <div className="flex gap-3">
        <Skeleton className="w-28 sm:w-36 aspect-video rounded-lg shrink-0" />
        <div className="flex-1 space-y-2 py-1">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    );
  }

  if (variant === 'large') {
    return (
      <div className="space-y-3">
        <Skeleton className="aspect-video rounded-xl" />
        <div className="flex gap-3">
          <Skeleton className="w-10 h-10 rounded-full shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-2/3" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Skeleton className="aspect-video rounded-lg" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  );
}

/**
 * Video grid skeleton
 */
export function VideoGridSkeleton({ count = 12, variant = 'default' }) {
  return (
    <div className="grid grid-cols-video-mobile sm:grid-cols-video-tablet md:grid-cols-video-desktop 
                   lg:grid-cols-video-hd 3xl:grid-cols-video-fhd 5k:grid-cols-video-4k gap-4">
      {[...Array(count)].map((_, i) => (
        <VideoCardSkeleton key={i} variant={variant} />
      ))}
    </div>
  );
}

/**
 * Category row skeleton
 */
export function CategoryRowSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-7 w-40" />
        <Skeleton className="h-5 w-20" />
      </div>
      <div className="flex gap-4 overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="w-[280px] shrink-0">
            <VideoCardSkeleton />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Hero section skeleton
 */
export function HeroSkeleton() {
  return (
    <div className="relative aspect-[21/9] sm:aspect-[21/7] md:aspect-[21/6] rounded-xl overflow-hidden">
      <Skeleton className="absolute inset-0" />
      <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8 md:p-12">
        <Skeleton className="h-10 w-2/3 mb-4" />
        <Skeleton className="h-5 w-1/2 mb-2" />
        <Skeleton className="h-5 w-1/3 mb-6" />
        <div className="flex gap-3">
          <Skeleton className="h-12 w-32 rounded-lg" />
          <Skeleton className="h-12 w-32 rounded-lg" />
        </div>
      </div>
    </div>
  );
}

/**
 * Text skeleton
 */
export function TextSkeleton({ lines = 3, className }) {
  return (
    <div className={cn('space-y-2', className)}>
      {[...Array(lines)].map((_, i) => (
        <Skeleton
          key={i}
          className="h-4"
          style={{ width: `${100 - (i === lines - 1 ? 30 : 0)}%` }}
        />
      ))}
    </div>
  );
}

/**
 * Avatar skeleton
 */
export function AvatarSkeleton({ size = 'md' }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  return <Skeleton className={cn('rounded-full', sizes[size])} />;
}

/**
 * Page skeleton - Full page loading state
 */
export function PageSkeleton() {
  return (
    <div className="min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 py-8 space-y-8">
      <HeroSkeleton />
      <CategoryRowSkeleton />
      <CategoryRowSkeleton />
      <CategoryRowSkeleton />
    </div>
  );
}

export default Skeleton;
