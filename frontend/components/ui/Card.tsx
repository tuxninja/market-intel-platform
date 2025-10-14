/**
 * Reusable Card component
 */

import React from 'react';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({ children, className, hover = false, onClick }) => {
  return (
    <div
      className={clsx(
        'bg-card rounded-xl border border-neutral/20 p-6',
        hover && 'transition-all duration-200 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;
