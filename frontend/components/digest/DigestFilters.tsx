/**
 * Digest Filters Component
 */

'use client';

import React from 'react';
import { FilterOptions } from '@/lib/types';
import Badge from '@/components/ui/Badge';

interface DigestFiltersProps {
  filters: FilterOptions;
  onChange: (filters: FilterOptions) => void;
}

const DigestFilters: React.FC<DigestFiltersProps> = ({ filters, onChange }) => {
  const categories = [
    { value: 'all', label: 'All Signals' },
    { value: 'trade_alert', label: '🔴 Trade Alerts' },
    { value: 'watch_list', label: '🟡 Watch List' },
    { value: 'market_context', label: '🟢 Market Context' },
  ];

  const priorities = [
    { value: 'all', label: 'All Priorities' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  const sortOptions = [
    { value: 'date', label: 'Date' },
    { value: 'confidence', label: 'Confidence' },
    { value: 'sentiment', label: 'Sentiment' },
  ];

  return (
    <div className="bg-card rounded-xl border border-neutral/20 p-4 space-y-4">
      {/* Category Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Category
        </label>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => onChange({ ...filters, category: cat.value as any })}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filters.category === cat.value
                  ? 'bg-primary text-black'
                  : 'bg-card-secondary text-gray-300 hover:bg-primary/10'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Priority
        </label>
        <div className="flex flex-wrap gap-2">
          {priorities.map((priority) => (
            <button
              key={priority.value}
              onClick={() => onChange({ ...filters, priority: priority.value as any })}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filters.priority === priority.value
                  ? 'bg-primary text-black'
                  : 'bg-card-secondary text-gray-300 hover:bg-primary/10'
              }`}
            >
              {priority.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sort */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Sort By
        </label>
        <div className="flex gap-2">
          {sortOptions.map((sort) => (
            <button
              key={sort.value}
              onClick={() => onChange({ ...filters, sortBy: sort.value as any })}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filters.sortBy === sort.value
                  ? 'bg-primary text-black'
                  : 'bg-card-secondary text-gray-300 hover:bg-primary/10'
              }`}
            >
              {sort.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DigestFilters;
