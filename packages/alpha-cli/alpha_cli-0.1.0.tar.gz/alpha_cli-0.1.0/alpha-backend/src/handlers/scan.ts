/**
 * Scan handler for cross-referencing congress trades with markets
 */

import { Hono } from 'hono';
import type { Env, AuthContext, ScanResponse, CrossReference, CongressTrade, RelatedMarket } from '../types';

const app = new Hono<{ Bindings: Env }>();

// Congress data URLs
const HOUSE_URL = 'https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json';
const SENATE_URL = 'https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json';

// Kalshi API URL
const KALSHI_URL = 'https://api.elections.kalshi.com/trade-api/v2';

/**
 * Fetch congress trades with caching
 */
async function fetchCongressTrades(
  cache: KVNamespace,
  days: number
): Promise<CongressTrade[]> {
  const cacheKey = 'congress_trades';
  const cached = await cache.get(cacheKey, 'json') as CongressTrade[] | null;

  // Use cache if fresh (15 min TTL)
  if (cached) {
    return cached;
  }

  // Fetch from both sources
  const [houseRes, senateRes] = await Promise.allSettled([
    fetch(HOUSE_URL),
    fetch(SENATE_URL),
  ]);

  const trades: CongressTrade[] = [];
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  // Parse house trades
  if (houseRes.status === 'fulfilled' && houseRes.value.ok) {
    const houseData = await houseRes.value.json() as any[];
    for (const raw of houseData) {
      const trade = parseCongressTrade(raw, 'house');
      if (trade && new Date(trade.transactionDate) >= cutoffDate) {
        trades.push(trade);
      }
    }
  }

  // Parse senate trades
  if (senateRes.status === 'fulfilled' && senateRes.value.ok) {
    const senateData = await senateRes.value.json() as any[];
    for (const raw of senateData) {
      const trade = parseCongressTrade(raw, 'senate');
      if (trade && new Date(trade.transactionDate) >= cutoffDate) {
        trades.push(trade);
      }
    }
  }

  // Sort by date descending
  trades.sort((a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime());

  // Cache for 15 minutes
  await cache.put(cacheKey, JSON.stringify(trades), { expirationTtl: 900 });

  return trades;
}

/**
 * Parse raw congress trade data
 */
function parseCongressTrade(raw: any, chamber: 'house' | 'senate'): CongressTrade | null {
  const ticker = raw.ticker?.trim();
  if (!ticker || ticker === '--') return null;

  let tradeType: 'purchase' | 'sale' | 'exchange' = 'purchase';
  const rawType = (raw.type || '').toLowerCase();
  if (rawType.includes('sale')) tradeType = 'sale';
  else if (rawType.includes('exchange')) tradeType = 'exchange';

  return {
    transactionDate: raw.transaction_date || '',
    disclosureDate: raw.disclosure_date || '',
    ticker: ticker.toUpperCase(),
    assetDescription: raw.asset_description || '',
    assetType: raw.asset_type || 'Stock',
    tradeType,
    amount: raw.amount || '',
    representative: raw.representative || raw.senator || '',
    district: raw.district,
    state: raw.district?.slice(0, 2),
    chamber,
  };
}

/**
 * Fetch Kalshi markets with caching
 */
async function fetchKalshiMarkets(cache: KVNamespace): Promise<any[]> {
  const cacheKey = 'kalshi_markets';
  const cached = await cache.get(cacheKey, 'json') as any[] | null;

  if (cached) {
    return cached;
  }

  const response = await fetch(`${KALSHI_URL}/markets?limit=1000&status=open`);
  if (!response.ok) {
    throw new Error('Failed to fetch Kalshi markets');
  }

  const data = await response.json() as { markets: any[] };
  const markets = data.markets || [];

  // Cache for 15 minutes
  await cache.put(cacheKey, JSON.stringify(markets), { expirationTtl: 900 });

  return markets;
}

/**
 * Match ticker to markets using database mappings
 */
async function matchTickerToMarkets(
  db: D1Database,
  ticker: string,
  markets: any[]
): Promise<RelatedMarket[]> {
  // Get mappings from database
  const mappings = await db.prepare(`
    SELECT market_pattern, relevance_type
    FROM ticker_market_mappings
    WHERE ticker = ?
  `).bind(ticker.toUpperCase()).all<{
    market_pattern: string;
    relevance_type: string;
  }>();

  if (!mappings.results?.length) {
    return [];
  }

  const results: RelatedMarket[] = [];

  for (const market of markets) {
    for (const mapping of mappings.results) {
      // Check if market ticker matches pattern (SQL LIKE)
      const pattern = mapping.market_pattern.replace('%', '.*');
      const regex = new RegExp(`^${pattern}`, 'i');

      if (regex.test(market.ticker)) {
        results.push({
          platform: 'kalshi',
          ticker: market.ticker,
          title: market.title,
          yesPrice: (market.yes_price || 0) / 100,
          noPrice: (market.no_price || 0) / 100,
          volume: market.volume || 0,
          closeDate: market.close_time,
          relevanceScore: mapping.relevance_type === 'direct' ? 1.0 : 0.7,
          relevanceType: mapping.relevance_type as 'direct' | 'sector' | 'macro',
        });
        break; // Don't match same market twice
      }
    }
  }

  // Sort by relevance
  results.sort((a, b) => b.relevanceScore - a.relevanceScore);

  return results;
}

/**
 * POST /scan
 * Cross-reference congress trades with prediction markets
 */
app.post('/', async (c) => {
  const auth = c.get('auth') as AuthContext;
  const body = await c.req.json<{
    days?: number;
    ticker?: string;
    party?: 'R' | 'D';
  }>();

  const days = Math.min(body.days || 30, 365);
  const ticker = body.ticker?.toUpperCase();
  const party = body.party;

  try {
    // Fetch data
    const [trades, markets] = await Promise.all([
      fetchCongressTrades(c.env.CACHE, days),
      fetchKalshiMarkets(c.env.CACHE),
    ]);

    // Filter trades
    let filteredTrades = trades;
    if (ticker) {
      filteredTrades = filteredTrades.filter(t => t.ticker === ticker);
    }
    if (party) {
      filteredTrades = filteredTrades.filter(t => t.party === party);
    }

    // Build cross-references
    const crossRefs: CrossReference[] = [];
    const seenTickers = new Set<string>();

    for (const trade of filteredTrades.slice(0, 100)) { // Limit to 100 trades
      if (seenTickers.has(trade.ticker)) continue;
      seenTickers.add(trade.ticker);

      const relatedMarkets = await matchTickerToMarkets(c.env.DB, trade.ticker, markets);

      if (relatedMarkets.length > 0) {
        crossRefs.push({
          congressTrade: trade,
          relatedMarkets: relatedMarkets.slice(0, 5), // Top 5 markets per trade
        });
      }
    }

    const response: ScanResponse = {
      crossReferences: crossRefs.slice(0, 50), // Limit response size
      generatedAt: new Date().toISOString(),
      cacheTtl: 900,
      isStale: false,
    };

    return c.json(response);

  } catch (error) {
    console.error('Scan error:', error);
    return c.json({
      code: 'E500_SCAN_ERROR',
      message: 'Failed to perform scan. Please try again.',
    }, 500);
  }
});

export default app;
