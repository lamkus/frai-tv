import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

/**
 * Button component with variants
 * 
 * Variants:
 * - primary: Accent red background
 * - secondary: Dark background with border
 * - outline: Transparent with border
 * - ghost: No background, subtle hover
 * 
 * Sizes: sm, md, lg
 */
const Button = forwardRef(({
  className,
  variant = 'primary',
  size = 'md',
  disabled,
  loading,
  children,
  ...props
}, ref) => {
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    font-medium rounded-lg transition-all
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-retro-black
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const variants = {
    primary: 'bg-accent-red hover:bg-accent-red/80 text-white focus:ring-accent-red',
    secondary: 'bg-retro-dark hover:bg-retro-gray border border-retro-gray text-white focus:ring-retro-gray',
    outline: 'border border-retro-gray hover:bg-retro-gray/20 text-white focus:ring-retro-gray',
    ghost: 'hover:bg-retro-gray/20 text-retro-muted hover:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    cyan: 'bg-accent-cyan hover:bg-accent-cyan/80 text-retro-black focus:ring-accent-cyan',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg',
    icon: 'p-2',
    'icon-sm': 'p-1.5',
    'icon-lg': 'p-3',
  };

  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        loading && 'relative text-transparent hover:text-transparent',
        className
      )}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <LoadingSpinner size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
        </div>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

/**
 * Loading spinner
 */
function LoadingSpinner({ size = 16, className }) {
  return (
    <svg
      className={cn('animate-spin text-current', className)}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export { Button, LoadingSpinner };
export default Button;
