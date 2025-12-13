import { forwardRef } from 'react';
import { Search, X } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * Input component with variants
 */
const Input = forwardRef(({
  className,
  type = 'text',
  error,
  label,
  helperText,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  onClear,
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-fluid-sm font-medium mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {LeftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted">
            <LeftIcon size={18} />
          </div>
        )}
        <input
          ref={ref}
          type={type}
          className={cn(
            'w-full bg-retro-dark border border-retro-gray rounded-lg',
            'text-fluid-sm text-white placeholder:text-retro-muted',
            'transition-colors duration-200',
            'focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            LeftIcon ? 'pl-10' : 'pl-4',
            RightIcon || onClear ? 'pr-10' : 'pr-4',
            'py-2.5',
            error && 'border-accent-red focus:border-accent-red focus:ring-accent-red/30',
            className
          )}
          {...props}
        />
        {(RightIcon || onClear) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {onClear && props.value ? (
              <button
                type="button"
                onClick={onClear}
                className="text-retro-muted hover:text-white transition-colors"
                aria-label="Löschen"
              >
                <X size={18} />
              </button>
            ) : RightIcon ? (
              <RightIcon size={18} className="text-retro-muted" />
            ) : null}
          </div>
        )}
      </div>
      {(helperText || error) && (
        <p className={cn(
          'text-fluid-xs mt-1.5',
          error ? 'text-accent-red' : 'text-retro-muted'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

/**
 * Search input with icon
 */
const SearchInput = forwardRef(({ className, ...props }, ref) => {
  return (
    <Input
      ref={ref}
      type="search"
      leftIcon={Search}
      placeholder="Suchen..."
      className={className}
      {...props}
    />
  );
});

SearchInput.displayName = 'SearchInput';

/**
 * Textarea component
 */
const Textarea = forwardRef(({
  className,
  label,
  error,
  helperText,
  rows = 4,
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-fluid-sm font-medium mb-1.5">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={cn(
          'w-full bg-retro-dark border border-retro-gray rounded-lg',
          'px-4 py-2.5 text-fluid-sm text-white placeholder:text-retro-muted',
          'transition-colors duration-200 resize-y',
          'focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-accent-red focus:border-accent-red focus:ring-accent-red/30',
          className
        )}
        {...props}
      />
      {(helperText || error) && (
        <p className={cn(
          'text-fluid-xs mt-1.5',
          error ? 'text-accent-red' : 'text-retro-muted'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

/**
 * Select component
 */
const Select = forwardRef(({
  className,
  label,
  error,
  helperText,
  options = [],
  placeholder,
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-fluid-sm font-medium mb-1.5">
          {label}
        </label>
      )}
      <select
        ref={ref}
        className={cn(
          'w-full bg-retro-dark border border-retro-gray rounded-lg',
          'px-4 py-2.5 text-fluid-sm text-white',
          'transition-colors duration-200',
          'focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-accent-red focus:border-accent-red focus:ring-accent-red/30',
          className
        )}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
      {(helperText || error) && (
        <p className={cn(
          'text-fluid-xs mt-1.5',
          error ? 'text-accent-red' : 'text-retro-muted'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

/**
 * Checkbox component
 */
const Checkbox = forwardRef(({
  className,
  label,
  description,
  ...props
}, ref) => {
  return (
    <label className={cn('flex items-start gap-3 cursor-pointer group', className)}>
      <input
        ref={ref}
        type="checkbox"
        className={cn(
          'w-5 h-5 mt-0.5 rounded border-2 border-retro-gray',
          'bg-retro-dark text-accent-red',
          'focus:ring-2 focus:ring-accent-red/30 focus:ring-offset-0',
          'transition-colors cursor-pointer'
        )}
        {...props}
      />
      <div>
        {label && (
          <span className="text-fluid-sm font-medium group-hover:text-accent-cyan transition-colors">
            {label}
          </span>
        )}
        {description && (
          <p className="text-fluid-xs text-retro-muted mt-0.5">
            {description}
          </p>
        )}
      </div>
    </label>
  );
});

Checkbox.displayName = 'Checkbox';

export { Input, SearchInput, Textarea, Select, Checkbox };
export default Input;
