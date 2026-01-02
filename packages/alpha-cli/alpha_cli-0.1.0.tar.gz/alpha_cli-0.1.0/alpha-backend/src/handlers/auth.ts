/**
 * Authentication handlers
 */

import { Hono } from 'hono';
import type { Env, AuthContext } from '../types';

const app = new Hono<{ Bindings: Env }>();

/**
 * Validate API key and return auth status
 * POST /auth/validate
 */
app.post('/validate', async (c) => {
  const auth = c.get('auth') as AuthContext;

  return c.json({
    status: auth.status,
    email: auth.email,
    subscriptionEnd: auth.subscriptionEnd,
  });
});

/**
 * Generate a new API key
 * POST /auth/keys
 */
app.post('/keys', async (c) => {
  const auth = c.get('auth') as AuthContext;

  // This would be called after OAuth flow completes
  // For now, return a placeholder response

  return c.json({
    message: 'API key generation requires authentication flow',
    hint: 'Complete OAuth at /auth/login first',
  }, 501);
});

/**
 * Revoke an API key
 * DELETE /auth/keys/:keyId
 */
app.delete('/keys/:keyId', async (c) => {
  const auth = c.get('auth') as AuthContext;
  const keyId = c.req.param('keyId');

  if (!auth.userId) {
    return c.json({ code: 'E401_INVALID_KEY', message: 'Unauthorized' }, 401);
  }

  // Revoke the key
  const result = await c.env.DB.prepare(`
    UPDATE api_keys
    SET revoked_at = CURRENT_TIMESTAMP
    WHERE id = ? AND user_id = ?
  `).bind(keyId, auth.userId).run();

  if (result.changes === 0) {
    return c.json({ code: 'E404_NOT_FOUND', message: 'API key not found' }, 404);
  }

  return c.json({ success: true });
});

export default app;
