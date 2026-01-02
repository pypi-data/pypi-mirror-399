/**
 * Alpha CLI Backend - Cloudflare Workers
 *
 * Main entry point for the API.
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { prettyJSON } from 'hono/pretty-json';
import type { Env } from './types';
import { authMiddleware, requireAuth, requirePremium } from './middleware/auth';
import { rateLimitMiddleware } from './middleware/rateLimit';
import authHandlers from './handlers/auth';
import scanHandlers from './handlers/scan';
import webhookHandlers from './handlers/webhooks';

const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use('*', logger());
app.use('*', prettyJSON());
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'X-API-Key', 'Authorization'],
}));

// Health check (no auth required)
app.get('/', (c) => {
  return c.json({
    name: 'Alpha CLI Backend',
    version: c.env.API_VERSION,
    status: 'healthy',
  });
});

app.get('/health', (c) => {
  return c.json({ status: 'ok' });
});

// Auth middleware for all API routes
app.use('/v1/*', authMiddleware);
app.use('/v1/*', rateLimitMiddleware);

// Public routes (auth optional)
app.route('/v1/auth', authHandlers);

// Webhook routes (no auth - uses Stripe signature)
app.route('/webhooks', webhookHandlers);

// Premium routes (require auth + premium)
app.use('/v1/scan', requireAuth);
// Note: scan is available to free users with basic matching
// Premium users get enhanced matching
app.route('/v1/scan', scanHandlers);

// 404 handler
app.notFound((c) => {
  return c.json({
    code: 'E404_NOT_FOUND',
    message: 'Endpoint not found',
  }, 404);
});

// Error handler
app.onError((err, c) => {
  console.error('Unhandled error:', err);
  return c.json({
    code: 'E500_INTERNAL',
    message: 'Internal server error',
  }, 500);
});

// Export for Cloudflare Workers
export default {
  fetch: app.fetch,

  // Scheduled handler for cron triggers
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    console.log(`Cron triggered at ${new Date().toISOString()}`);

    // This would handle:
    // 1. Refreshing cached data
    // 2. Processing alerts
    // 3. Cleanup tasks

    // For now, just log
    console.log('Scheduled task completed');
  },

  // Queue handler for webhook delivery
  async queue(batch: MessageBatch<unknown>, env: Env) {
    for (const message of batch.messages) {
      try {
        const data = message.body as {
          alertId: string;
          webhookUrl: string;
          payload: unknown;
          attempt: number;
        };

        // Deliver webhook
        const response = await fetch(data.webhookUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data.payload),
        });

        if (response.ok) {
          // Update alert last_triggered_at
          await env.DB.prepare(`
            UPDATE alerts SET last_triggered_at = CURRENT_TIMESTAMP
            WHERE id = ?
          `).bind(data.alertId).run();

          message.ack();
        } else if (data.attempt < 3) {
          // Retry
          message.retry({ delaySeconds: Math.pow(2, data.attempt) * 60 });
        } else {
          // Give up after 3 attempts
          console.error(`Webhook delivery failed after 3 attempts: ${data.alertId}`);
          message.ack();
        }
      } catch (error) {
        console.error('Queue message processing error:', error);
        message.retry();
      }
    }
  },
};
