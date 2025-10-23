/**
 * Digest Item Card Component
 */

'use client';

import React, { useState } from 'react';
import { DigestItem } from '@/lib/types';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

interface DigestCardProps {
  item: DigestItem;
}

const DigestCard: React.FC<DigestCardProps> = ({ item }) => {
  const [expanded, setExpanded] = useState(false);

  // Get category badge variant and label
  const getCategoryInfo = (category: string) => {
    switch (category) {
      case 'trade_alert':
        return { variant: 'error' as const, label: 'TRADE ALERT', icon: '🔴' };
      case 'watch_list':
        return { variant: 'warning' as const, label: 'WATCH LIST', icon: '🟡' };
      case 'market_context':
        return { variant: 'info' as const, label: 'MARKET CONTEXT', icon: '🟢' };
      default:
        return { variant: 'neutral' as const, label: category.toUpperCase(), icon: '⚪' };
    }
  };

  const categoryInfo = getCategoryInfo(item.category);

  // Get priority badge
  const getPriorityVariant = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  // Format sentiment score
  const getSentimentColor = (score?: number) => {
    if (score === undefined) return 'text-neutral';
    if (score > 0.3) return 'text-primary';
    if (score < -0.3) return 'text-negative';
    return 'text-neutral';
  };

  return (
    <Card hover className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={categoryInfo.variant} size="md">
              {categoryInfo.icon} {categoryInfo.label}
            </Badge>
            {item.priority && (
              <Badge variant={getPriorityVariant(item.priority)} size="sm">
                {item.priority.toUpperCase()}
              </Badge>
            )}
          </div>
          <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
          {item.symbol && (
            <p className="text-primary font-mono text-lg">${item.symbol}</p>
          )}
        </div>

        {/* Scores */}
        <div className="text-right space-y-1">
          {item.confidence_score !== undefined && (
            <div className="text-sm">
              <span className="text-neutral">Confidence: </span>
              <span className="text-primary font-bold">
                {(item.confidence_score * 100).toFixed(1)}%
              </span>
            </div>
          )}
          {item.sentiment_score !== undefined && (
            <div className="text-sm">
              <span className="text-neutral">Sentiment: </span>
              <span className={getSentimentColor(item.sentiment_score)}>
                {item.sentiment_score > 0 ? '+' : ''}
                {item.sentiment_score.toFixed(2)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      <p className="text-gray-300 leading-relaxed">{item.summary}</p>

      {/* Expandable Details */}
      {(item.explanation || item.how_to_trade) && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-primary hover:text-primary-light transition-colors"
          >
            <span className="font-medium">
              {expanded ? 'Hide Details' : 'Show Analysis & Trading Strategy'}
            </span>
            {expanded ? (
              <ChevronUpIcon className="w-5 h-5" />
            ) : (
              <ChevronDownIcon className="w-5 h-5" />
            )}
          </button>

          {expanded && (
            <div className="mt-4 space-y-4 pt-4 border-t border-neutral/20">
              {item.explanation && (
                <div>
                  <h4 className="text-primary font-bold mb-2">💡 WHY THIS MATTERS</h4>
                  <p className="text-gray-300 leading-relaxed">{item.explanation}</p>
                </div>
              )}

              {/* News Articles Section */}
              {item.news_articles && item.news_articles.length > 0 && (
                <div className="bg-card-dark p-4 rounded-lg border-l-4 border-primary/30">
                  <h4 className="text-primary font-bold mb-3 flex items-center gap-2">
                    📰 RELATED NEWS
                  </h4>
                  <div className="space-y-3">
                    {item.news_articles.slice(0, 3).map((article, idx) => {
                      const sentimentEmoji = article.sentiment_score > 0.2
                        ? '📈'
                        : article.sentiment_score < -0.2
                        ? '📉'
                        : '📊';

                      return (
                        <div
                          key={idx}
                          className="pb-3 border-b border-neutral/10 last:border-b-0 last:pb-0"
                        >
                          <div className="flex items-center gap-2 mb-1 text-xs">
                            <span className="text-neutral font-mono uppercase">
                              {article.source}
                            </span>
                            <span>{sentimentEmoji}</span>
                          </div>
                          <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-white hover:text-primary transition-colors text-sm leading-snug block"
                          >
                            {article.title.length > 100
                              ? `${article.title.substring(0, 100)}...`
                              : article.title}
                          </a>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {item.how_to_trade && (
                <div>
                  <h4 className="text-primary font-bold mb-2">🎯 HOW TO TRADE</h4>
                  <p className="text-gray-300 leading-relaxed whitespace-pre-line">
                    {item.how_to_trade}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-neutral pt-2 border-t border-neutral/20">
        <span>{item.source || 'TradeTheHype'}</span>
        <span>{new Date(item.created_at).toLocaleString()}</span>
      </div>
    </Card>
  );
};

export default DigestCard;
