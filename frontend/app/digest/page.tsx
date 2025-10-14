/**
 * Digest Page - Main Intelligence Feed
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { digestApi } from '@/lib/api';
import { DigestResponse, DigestItem, FilterOptions } from '@/lib/types';
import DigestCard from '@/components/digest/DigestCard';
import DigestFilters from '@/components/digest/DigestFilters';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

export default function DigestPage() {
  const router = useRouter();
  const [digest, setDigest] = useState<DigestResponse | null>(null);
  const [filteredItems, setFilteredItems] = useState<DigestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    category: 'all',
    priority: 'all',
    sortBy: 'date',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    fetchDigest();
  }, [router]);

  useEffect(() => {
    if (digest) {
      applyFilters();
    }
  }, [filters, digest]);

  const fetchDigest = async () => {
    try {
      setError('');
      const data = await digestApi.getDailyDigest({
        max_items: 20,
        hours_lookback: 24,
        enable_ml: true,
      });
      setDigest(data);
      setFilteredItems(data.items);
    } catch (err: any) {
      console.error('Failed to fetch digest:', err);
      setError(err.response?.data?.detail || 'Failed to load digest');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDigest();
    setRefreshing(false);
  };

  const applyFilters = () => {
    if (!digest) return;

    let filtered = [...digest.items];

    // Filter by category
    if (filters.category && filters.category !== 'all') {
      filtered = filtered.filter((item) => item.category === filters.category);
    }

    // Filter by priority
    if (filters.priority && filters.priority !== 'all') {
      filtered = filtered.filter((item) => item.priority === filters.priority);
    }

    // Sort
    if (filters.sortBy === 'confidence') {
      filtered.sort((a, b) => (b.confidence_score || 0) - (a.confidence_score || 0));
    } else if (filters.sortBy === 'sentiment') {
      filtered.sort((a, b) => Math.abs(b.sentiment_score || 0) - Math.abs(a.sentiment_score || 0));
    } else {
      // Sort by date (default)
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }

    setFilteredItems(filtered);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-300">Loading your intelligence digest...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Daily Market Digest
            </h1>
            <p className="text-gray-300">
              {digest?.generated_at && (
                <>Generated {new Date(digest.generated_at).toLocaleString()}</>
              )}
            </p>
          </div>
          <Button
            variant="secondary"
            onClick={handleRefresh}
            loading={refreshing}
            disabled={refreshing}
          >
            <ArrowPathIcon className="w-5 h-5 mr-2" />
            Refresh
          </Button>
        </div>

        {/* VIX Regime (if available) */}
        {digest?.vix_regime && (
          <div className="bg-card rounded-xl border border-primary/20 p-4 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">
                  Market Regime: {digest.vix_regime.regime}
                </h3>
                <p className="text-gray-300">{digest.vix_regime.description}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Current VIX</p>
                <p className="text-3xl font-bold text-primary">
                  {digest.vix_regime.current_vix}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-card rounded-xl border border-neutral/20 p-4">
            <p className="text-gray-400 text-sm mb-1">Total Signals</p>
            <p className="text-3xl font-bold text-white">{digest?.total_items || 0}</p>
          </div>
          <div className="bg-card rounded-xl border border-neutral/20 p-4">
            <p className="text-gray-400 text-sm mb-1">Filtered</p>
            <p className="text-3xl font-bold text-primary">{filteredItems.length}</p>
          </div>
          <div className="bg-card rounded-xl border border-neutral/20 p-4">
            <p className="text-gray-400 text-sm mb-1">Trade Alerts</p>
            <p className="text-3xl font-bold text-negative">
              {digest?.items.filter((i) => i.category === 'trade_alert').length || 0}
            </p>
          </div>
          <div className="bg-card rounded-xl border border-neutral/20 p-4">
            <p className="text-gray-400 text-sm mb-1">Watch List</p>
            <p className="text-3xl font-bold text-yellow-400">
              {digest?.items.filter((i) => i.category === 'watch_list').length || 0}
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-negative/10 border border-negative/20 rounded-xl p-4 mb-8">
            <p className="text-negative">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <DigestFilters filters={filters} onChange={setFilters} />
          </div>

          {/* Digest Items */}
          <div className="lg:col-span-3 space-y-6">
            {filteredItems.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-400 text-lg">
                  No signals match your filters
                </p>
              </div>
            ) : (
              filteredItems.map((item, index) => (
                <DigestCard key={item.id || index} item={item} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
