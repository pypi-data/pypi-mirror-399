/**
 * Type definitions for Alpha CLI Backend
 */

// Environment bindings
export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
  WEBHOOK_QUEUE: Queue;
  STRIPE_SECRET_KEY: string;
  STRIPE_WEBHOOK_SECRET: string;
  ANTHROPIC_API_KEY: string;
  OPENAI_API_KEY: string;
  ENVIRONMENT: string;
  API_VERSION: string;
}

// Auth types
export type AuthStatus = 'anonymous' | 'free' | 'premium' | 'expired' | 'invalid';

export interface AuthContext {
  status: AuthStatus;
  userId?: string;
  email?: string;
  subscriptionEnd?: string;
}

export interface User {
  id: string;
  email: string;
  createdAt: string;
  stripeCustomerId?: string;
}

export interface ApiKey {
  id: string;
  userId: string;
  keyHash: string;
  keyPrefix: string;
  environment: 'live' | 'test';
  createdAt: string;
  lastUsedAt?: string;
  revokedAt?: string;
}

export interface Subscription {
  id: string;
  userId: string;
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  createdAt: string;
  updatedAt: string;
}

// Congress trading types
export interface CongressTrade {
  transactionDate: string;
  disclosureDate: string;
  ticker: string;
  assetDescription: string;
  assetType: string;
  tradeType: 'purchase' | 'sale' | 'exchange';
  amount: string;
  representative: string;
  district?: string;
  state?: string;
  party?: 'R' | 'D' | 'I';
  chamber?: 'house' | 'senate';
}

// Market types
export interface KalshiMarket {
  ticker: string;
  title: string;
  subtitle?: string;
  category?: string;
  status: string;
  yesPrice: number;
  noPrice: number;
  volume: number;
  closeTime?: string;
}

export interface RelatedMarket {
  platform: 'kalshi' | 'polymarket';
  ticker: string;
  title: string;
  yesPrice: number;
  noPrice: number;
  volume: number;
  closeDate?: string;
  relevanceScore: number;
  relevanceType: 'direct' | 'sector' | 'macro';
}

export interface CrossReference {
  congressTrade: CongressTrade;
  relatedMarkets: RelatedMarket[];
}

export interface ScanResponse {
  crossReferences: CrossReference[];
  generatedAt: string;
  cacheTtl: number;
  isStale: boolean;
}

// API types
export interface ApiError {
  code: string;
  message: string;
  retryAfter?: number;
}

// Alert types
export interface Alert {
  id: string;
  userId: string;
  alertType: 'congress_ticker' | 'market_move' | 'arb_opportunity';
  config: Record<string, unknown>;
  webhookUrl: string;
  enabled: boolean;
  lastTriggeredAt?: string;
  cooldownMinutes: number;
  createdAt: string;
}

// Webhook message types
export interface WebhookMessage {
  alertId: string;
  userId: string;
  webhookUrl: string;
  payload: Record<string, unknown>;
  attempt: number;
}
