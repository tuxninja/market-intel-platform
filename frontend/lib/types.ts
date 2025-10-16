/**
 * TypeScript type definitions for Market Intelligence Platform
 */

// User Types
export interface User {
  id: number;
  email: string;
  subscription_tier: 'free' | 'pro' | 'premium' | 'elite';
  is_active: boolean;
  is_verified: boolean;
  full_name?: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Digest Types
export interface NewsArticle {
  title: string;
  summary: string;
  url: string;
  sentiment_score: number;
  source: string;
  published: string;
}

export interface DigestItem {
  id?: number;
  symbol?: string;
  title: string;
  summary: string;
  explanation?: string;
  how_to_trade?: string;
  sentiment_score?: number;
  confidence_score?: number;
  priority: 'high' | 'medium' | 'low';
  category: 'trade_alert' | 'watch_list' | 'market_context';
  source?: string;
  news_articles?: NewsArticle[];
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DigestResponse {
  generated_at: string;
  items: DigestItem[];
  total_items: number;
  market_context?: Record<string, any>;
  vix_regime?: {
    current_vix: number;
    regime: string;
    description: string;
  };
}

export interface DigestRequest {
  max_items?: number;
  hours_lookback?: number;
  enable_ml?: boolean;
  categories?: string[];
}

// API Error Types
export interface ApiError {
  detail: string;
  status?: number;
}

// Component Props Types
export interface AuthFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export interface DigestCardProps {
  item: DigestItem;
}

export interface FilterOptions {
  category?: 'all' | 'trade_alert' | 'watch_list' | 'market_context';
  priority?: 'all' | 'high' | 'medium' | 'low';
  sortBy?: 'date' | 'confidence' | 'sentiment';
}
