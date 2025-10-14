/**
 * Reusable Badge component for labels and tags
 */

import React from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
}

const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', size = 'sm' }) => {
  const variants = {
    success: 'bg-primary/10 text-primary border-primary/20',
    warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    error: 'bg-negative/10 text-negative border-negative/20',
    info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    neutral: 'bg-neutral/10 text-neutral border-neutral/20',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium border',
        variants[variant],
        sizes[size]
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
