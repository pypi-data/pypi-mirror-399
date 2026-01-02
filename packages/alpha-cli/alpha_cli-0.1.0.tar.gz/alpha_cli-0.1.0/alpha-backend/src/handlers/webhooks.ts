/**
 * Webhook handlers for Stripe events
 */

import { Hono } from 'hono';
import type { Env } from '../types';
import Stripe from 'stripe';

const app = new Hono<{ Bindings: Env }>();

/**
 * POST /webhooks/stripe
 * Handle Stripe webhook events
 */
app.post('/stripe', async (c) => {
  const signature = c.req.header('stripe-signature');
  if (!signature) {
    return c.json({ error: 'Missing signature' }, 400);
  }

  const body = await c.req.text();

  // Initialize Stripe
  const stripe = new Stripe(c.env.STRIPE_SECRET_KEY, {
    apiVersion: '2023-10-16',
  });

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      c.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return c.json({ error: 'Invalid signature' }, 400);
  }

  // Handle the event
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      await handleCheckoutCompleted(c.env.DB, session);
      break;
    }

    case 'customer.subscription.created':
    case 'customer.subscription.updated': {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionUpdate(c.env.DB, subscription);
      break;
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionDeleted(c.env.DB, subscription);
      break;
    }

    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice;
      await handlePaymentFailed(c.env.DB, invoice);
      break;
    }

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  return c.json({ received: true });
});

/**
 * Handle checkout.session.completed event
 */
async function handleCheckoutCompleted(db: D1Database, session: Stripe.Checkout.Session) {
  const customerId = session.customer as string;
  const subscriptionId = session.subscription as string;
  const customerEmail = session.customer_email;

  if (!customerId || !subscriptionId) {
    console.error('Missing customer or subscription ID in checkout session');
    return;
  }

  // Update user with Stripe customer ID if not already set
  if (customerEmail) {
    await db.prepare(`
      UPDATE users SET stripe_customer_id = ?
      WHERE email = ? AND stripe_customer_id IS NULL
    `).bind(customerId, customerEmail).run();
  }

  console.log(`Checkout completed for customer ${customerId}, subscription ${subscriptionId}`);
}

/**
 * Handle subscription created/updated events
 */
async function handleSubscriptionUpdate(db: D1Database, subscription: Stripe.Subscription) {
  const customerId = subscription.customer as string;
  const subscriptionId = subscription.id;
  const status = subscription.status;
  const periodStart = new Date(subscription.current_period_start * 1000).toISOString();
  const periodEnd = new Date(subscription.current_period_end * 1000).toISOString();
  const cancelAtPeriodEnd = subscription.cancel_at_period_end;

  // Find user by Stripe customer ID
  const user = await db.prepare(`
    SELECT id FROM users WHERE stripe_customer_id = ?
  `).bind(customerId).first<{ id: string }>();

  if (!user) {
    console.error(`No user found for customer ${customerId}`);
    return;
  }

  // Upsert subscription
  await db.prepare(`
    INSERT INTO subscriptions (id, user_id, status, current_period_start, current_period_end, cancel_at_period_end, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
      status = excluded.status,
      current_period_start = excluded.current_period_start,
      current_period_end = excluded.current_period_end,
      cancel_at_period_end = excluded.cancel_at_period_end,
      updated_at = CURRENT_TIMESTAMP
  `).bind(
    subscriptionId,
    user.id,
    status,
    periodStart,
    periodEnd,
    cancelAtPeriodEnd ? 1 : 0
  ).run();

  console.log(`Subscription ${subscriptionId} updated: ${status}`);
}

/**
 * Handle subscription deleted event
 */
async function handleSubscriptionDeleted(db: D1Database, subscription: Stripe.Subscription) {
  const subscriptionId = subscription.id;

  await db.prepare(`
    UPDATE subscriptions SET status = 'canceled', updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `).bind(subscriptionId).run();

  console.log(`Subscription ${subscriptionId} canceled`);
}

/**
 * Handle payment failed event
 */
async function handlePaymentFailed(db: D1Database, invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string;

  if (subscriptionId) {
    await db.prepare(`
      UPDATE subscriptions SET status = 'past_due', updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).bind(subscriptionId).run();

    console.log(`Subscription ${subscriptionId} marked past_due due to payment failure`);
  }
}

export default app;
