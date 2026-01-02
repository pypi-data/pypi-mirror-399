/**
 * Rate limiting middleware using Cloudflare KV
 */

import { Context, Next } from 'hono';
import type { Env, AuthContext } from '../types';

// Rate limits by auth status
const RATE_LIMITS: Record<string, { requests: number; windowSeconds: number }> = {
  anonymous: { requests: 20, windowSeconds: 60 },    // 20 req/min
  free: { requests: 100, windowSeconds: 60 },        // 100 req/min
  premium: { requests: 1000, windowSeconds: 60 },    // 1000 req/min
  expired: { requests: 50, windowSeconds: 60 },      // 50 req/min
};

interface RateLimitState {
  count: number;
  resetAt: number;
}

/**
 * Get rate limit key for a user/IP
 */
function getRateLimitKey(c: Context, auth: AuthContext): string {
  if (auth.userId) {
    return `ratelimit:user:${auth.userId}`;
  }
  // Fall back to IP for anonymous users
  const ip = c.req.header('CF-Connecting-IP') || 'unknown';
  return `ratelimit:ip:${ip}`;
}

/**
 * Rate limiting middleware
 */
export async function rateLimitMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
  const auth = c.get('auth') as AuthContext || { status: 'anonymous' };
  const limit = RATE_LIMITS[auth.status] || RATE_LIMITS.anonymous;
  const key = getRateLimitKey(c, auth);

  // Get current state from KV
  const now = Date.now();
  let state = await c.env.CACHE.get(key, 'json') as RateLimitState | null;

  if (!state || state.resetAt < now) {
    // Start new window
    state = {
      count: 1,
      resetAt: now + (limit.windowSeconds * 1000),
    };
  } else {
    state.count++;
  }

  // Check if over limit
  if (state.count > limit.requests) {
    const retryAfter = Math.ceil((state.resetAt - now) / 1000);
    c.header('X-RateLimit-Limit', limit.requests.toString());
    c.header('X-RateLimit-Remaining', '0');
    c.header('X-RateLimit-Reset', Math.ceil(state.resetAt / 1000).toString());
    c.header('Retry-After', retryAfter.toString());

    return c.json({
      code: 'E429_RATE_LIMITED',
      message: `Rate limit exceeded. Please wait ${retryAfter} seconds.`,
      retryAfter,
    }, 429);
  }

  // Update state in KV
  await c.env.CACHE.put(key, JSON.stringify(state), {
    expirationTtl: limit.windowSeconds + 60, // Extra buffer
  });

  // Set headers
  c.header('X-RateLimit-Limit', limit.requests.toString());
  c.header('X-RateLimit-Remaining', Math.max(0, limit.requests - state.count).toString());
  c.header('X-RateLimit-Reset', Math.ceil(state.resetAt / 1000).toString());

  return next();
}
