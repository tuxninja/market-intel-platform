/**
 * Reusable Input component
 */

import React from 'react';
import clsx from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            'w-full px-4 py-2.5 bg-card border rounded-lg transition-colors',
            'text-white placeholder-neutral',
            'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary',
            error ? 'border-negative' : 'border-neutral/30',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-sm text-negative">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-neutral">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
