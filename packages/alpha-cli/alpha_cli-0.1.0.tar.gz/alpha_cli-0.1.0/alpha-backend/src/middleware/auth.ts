/**
 * Authentication middleware for API key validation
 */

import { Context, Next } from 'hono';
import type { Env, AuthContext, AuthStatus } from '../types';

// Cache for auth context (5 minute TTL)
const AUTH_CACHE_TTL = 300;

/**
 * Hash an API key for comparison
 */
async function hashApiKey(key: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(key);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Extract API key from request headers
 */
function extractApiKey(c: Context): string | null {
  // Check X-API-Key header
  const headerKey = c.req.header('X-API-Key');
  if (headerKey) return headerKey;

  // Check Authorization header (Bearer token)
  const authHeader = c.req.header('Authorization');
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.slice(7);
  }

  return null;
}

/**
 * Validate API key and get user context
 */
async function validateApiKey(
  db: D1Database,
  cache: KVNamespace,
  apiKey: string
): Promise<AuthContext> {
  // Check cache first
  const cacheKey = `auth:${apiKey.slice(0, 16)}`;
  const cached = await cache.get(cacheKey, 'json') as AuthContext | null;
  if (cached) {
    return cached;
  }

  // Hash the key for DB lookup
  const keyHash = await hashApiKey(apiKey);

  // Look up the API key
  const keyResult = await db.prepare(`
    SELECT ak.*, u.email
    FROM api_keys ak
    JOIN users u ON ak.user_id = u.id
    WHERE ak.key_hash = ? AND ak.revoked_at IS NULL
  `).bind(keyHash).first<{
    id: string;
    user_id: string;
    email: string;
    environment: string;
  }>();

  if (!keyResult) {
    return { status: 'invalid' };
  }

  // Update last_used_at
  await db.prepare(`
    UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP WHERE id = ?
  `).bind(keyResult.id).run();

  // Check subscription status
  const subResult = await db.prepare(`
    SELECT * FROM subscriptions
    WHERE user_id = ? AND status IN ('active', 'trialing')
    ORDER BY current_period_end DESC
    LIMIT 1
  `).bind(keyResult.user_id).first<{
    status: string;
    current_period_end: string;
  }>();

  let authStatus: AuthStatus = 'free';
  let subscriptionEnd: string | undefined;

  if (subResult) {
    const periodEnd = new Date(subResult.current_period_end);
    if (periodEnd > new Date()) {
      authStatus = 'premium';
      subscriptionEnd = subResult.current_period_end;
    } else {
      authStatus = 'expired';
      subscriptionEnd = subResult.current_period_end;
    }
  }

  const context: AuthContext = {
    status: authStatus,
    userId: keyResult.user_id,
    email: keyResult.email,
    subscriptionEnd,
  };

  // Cache the result
  await cache.put(cacheKey, JSON.stringify(context), {
    expirationTtl: AUTH_CACHE_TTL,
  });

  return context;
}

/**
 * Authentication middleware
 *
 * Sets c.set('auth', AuthContext) for downstream handlers
 */
export async function authMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
  const apiKey = extractApiKey(c);

  if (!apiKey) {
    c.set('auth', { status: 'anonymous' } as AuthContext);
    return next();
  }

  const context = await validateApiKey(c.env.DB, c.env.CACHE, apiKey);
  c.set('auth', context);

  return next();
}

/**
 * Require authentication middleware
 * Returns 401 if not authenticated
 */
export async function requireAuth(c: Context<{ Bindings: Env }>, next: Next) {
  const auth = c.get('auth') as AuthContext;

  if (!auth || auth.status === 'anonymous' || auth.status === 'invalid') {
    return c.json({
      code: 'E401_INVALID_KEY',
      message: 'Invalid or missing API key. Run `alpha login` to authenticate.',
    }, 401);
  }

  return next();
}

/**
 * Require premium subscription middleware
 * Returns 403 if not premium
 */
export async function requirePremium(c: Context<{ Bindings: Env }>, next: Next) {
  const auth = c.get('auth') as AuthContext;

  if (auth.status !== 'premium') {
    return c.json({
      code: 'E403_PREMIUM_REQUIRED',
      message: 'This feature requires a premium subscription. Run `alpha upgrade`.',
    }, 403);
  }

  return next();
}
