/**
 * Market Snapshot Widget
 * Displays VIX, major indices (SPY, DIA, QQQ), and market trend
 */

'use client';

import React from 'react';
import Card from '@/components/ui/Card';

interface MarketData {
  vix_level: number;
  regime: string;
  description: string;
}

interface IndexData {
  level: number;
  change: string;
  raw_change?: number;
}

interface MarketSnapshotProps {
  vixRegime?: MarketData;
  marketContext?: {
    market_trend?: string;
    major_indices?: {
      SPY?: IndexData;
      DIA?: IndexData;
      QQQ?: IndexData;
    };
  };
}

const MarketSnapshot: React.FC<MarketSnapshotProps> = ({
  vixRegime,
  marketContext,
}) => {
  // Get color for VIX regime
  const getVixColor = (regime: string) => {
    switch (regime?.toUpperCase()) {
      case 'LOW_VOL':
        return 'text-primary'; // Green
      case 'NORMAL':
        return 'text-yellow-400'; // Yellow
      case 'ELEVATED':
        return 'text-orange-400'; // Orange
      case 'HIGH_VOL':
        return 'text-negative'; // Red
      default:
        return 'text-neutral';
    }
  };

  // Get color for index change
  const getChangeColor = (change: string | number) => {
    const changeStr = change.toString();
    if (changeStr.startsWith('+') || parseFloat(changeStr) > 0) {
      return 'text-primary';
    } else if (changeStr.startsWith('-') || parseFloat(changeStr) < 0) {
      return 'text-negative';
    }
    return 'text-neutral';
  };

  const vixLevel = vixRegime?.vix_level || 0;
  const vixRegimeText = vixRegime?.regime || 'UNKNOWN';
  const marketTrend = marketContext?.market_trend || 'neutral';
  const indices = marketContext?.major_indices || {};

  return (
    <Card className="bg-gradient-to-br from-card via-card-dark to-card">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            📊 Market Snapshot
          </h2>
          <span className="text-xs text-neutral">Live Data</span>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* VIX */}
          <div className="bg-black/30 p-4 rounded-lg text-center border border-neutral/10">
            <div className="text-xs text-neutral uppercase tracking-wide mb-1">
              VIX
            </div>
            <div className={`text-2xl font-bold ${getVixColor(vixRegimeText)}`}>
              {vixLevel.toFixed(1)}
            </div>
            <div className="text-xs text-neutral mt-1">
              {vixRegimeText.replace('_', ' ')}
            </div>
          </div>

          {/* SPY */}
          {indices.SPY && (
            <div className="bg-black/30 p-4 rounded-lg text-center border border-neutral/10">
              <div className="text-xs text-neutral uppercase tracking-wide mb-1">
                SPY
              </div>
              <div className="text-2xl font-bold text-white">
                {indices.SPY.level.toFixed(2)}
              </div>
              <div className={`text-xs mt-1 font-medium ${getChangeColor(indices.SPY.change)}`}>
                {indices.SPY.change}
              </div>
            </div>
          )}

          {/* DIA */}
          {indices.DIA && (
            <div className="bg-black/30 p-4 rounded-lg text-center border border-neutral/10">
              <div className="text-xs text-neutral uppercase tracking-wide mb-1">
                DIA
              </div>
              <div className="text-2xl font-bold text-white">
                {indices.DIA.level.toFixed(2)}
              </div>
              <div className={`text-xs mt-1 font-medium ${getChangeColor(indices.DIA.change)}`}>
                {indices.DIA.change}
              </div>
            </div>
          )}

          {/* QQQ */}
          {indices.QQQ && (
            <div className="bg-black/30 p-4 rounded-lg text-center border border-neutral/10">
              <div className="text-xs text-neutral uppercase tracking-wide mb-1">
                QQQ
              </div>
              <div className="text-2xl font-bold text-white">
                {indices.QQQ.level.toFixed(2)}
              </div>
              <div className={`text-xs mt-1 font-medium ${getChangeColor(indices.QQQ.change)}`}>
                {indices.QQQ.change}
              </div>
            </div>
          )}
        </div>

        {/* Market Trend */}
        <div className="flex items-center justify-between pt-4 border-t border-neutral/10">
          <span className="text-sm text-neutral">Market Trend:</span>
          <span className={`text-sm font-bold uppercase ${
            marketTrend === 'bullish' ? 'text-primary' :
            marketTrend === 'bearish' ? 'text-negative' :
            'text-neutral'
          }`}>
            {marketTrend}
          </span>
        </div>
      </div>
    </Card>
  );
};

export default MarketSnapshot;
