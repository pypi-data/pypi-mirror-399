# Operator TODO

Items requiring external account setup or operator action before the system is fully operational.

## Required for MVP Launch

### 1. Cloudflare Account Setup

- [x] Create Cloudflare account (if not existing)
- [x] Create D1 database named `alpha-db` (ID: `e531d6c6-167b-4f26-a05f-84be637612ef`)
- [x] Update `wrangler.toml` with real database_id
- [x] Create KV namespace for caching (ID: `6553af8806bf4ae5940c651e87f61527`)
- [x] Update `wrangler.toml` with real KV namespace id
- [x] Initialize D1 database schema: `wrangler d1 execute alpha-db --remote --file=src/db/schema.sql`
- [x] Deploy worker: `cd alpha-backend && wrangler deploy`
- [x] Worker deployed at: `https://alpha-backend.austinkk24.workers.dev`

**Note:** Queue `alert-webhooks` requires Workers Paid plan. Deferred to post-MVP (alerts feature).

### 2. Stripe Account Setup

- [x] Create Stripe account
- [x] Create product "Alpha Premium" ($20/month)
- [x] Set environment secrets:
  ```bash
  cd alpha-backend && wrangler secret put STRIPE_SECRET_KEY
  cd alpha-backend && wrangler secret put STRIPE_WEBHOOK_SECRET
  ```
- [x] Configure webhook endpoint in Stripe dashboard:
  - URL: `https://alpha-backend.austinkk24.workers.dev/webhooks/stripe`
  - Events: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`

### 3. Landing Page

- [x] Created landing page at `/landing/index.html`
- [x] Deployed to Cloudflare Pages: `https://alpha-cli.pages.dev`
- [ ] (Optional) Register custom domain and connect to Pages

### 4. Domain Configuration (Optional)

- [ ] Register domain (e.g., `alphacli.dev` ~$12/yr on Cloudflare)
- [ ] Configure DNS for:
  - `api.alphacli.dev` → Cloudflare Worker (`alpha-backend.austinkk24.workers.dev`)
  - `alphacli.dev` → Cloudflare Pages (`alpha-cli.pages.dev`)
- [ ] Set up SSL certificates (Cloudflare handles automatically)

### 5. API Keys for Enhanced Features

#### For Tier 2 Matching (Embeddings)

- [ ] OpenAI API key for `text-embedding-3-small`
  OR
- [ ] Voyage AI key for `voyage-finance-2`

Set with:
```bash
cd alpha-backend && wrangler secret put OPENAI_API_KEY
```

#### For Tier 3 Matching (LLM Validation)

- [ ] Anthropic API key for Claude Haiku
```bash
cd alpha-backend && wrangler secret put ANTHROPIC_API_KEY
```

### 6. Kalshi Partnership (Optional)

- [ ] Apply for Kalshi API partnership for higher rate limits
- [ ] Get production API credentials

## Required for Distribution

### 7. PyPI Publishing

- [ ] Create PyPI account
- [ ] Configure trusted publishing or API token
- [ ] Publish: `uv build && uv publish`

### 8. Homebrew Formula

- [ ] Create homebrew-alpha-cli tap repository
- [ ] Add formula pointing to PyPI package

## Post-Launch

### 9. Monitoring

- [ ] Set up Sentry for error tracking
- [ ] Configure uptime monitoring
- [ ] Set up Cloudflare analytics

### 10. OAuth Providers (for `alpha login`)

- [ ] Configure Google OAuth
- [ ] Configure GitHub OAuth
- [ ] Set up email provider for magic links

## Notes

- The CLI works without backend for free features (Kalshi, Congress)
- Premium features require backend + Stripe + API keys
- Start with minimal setup, add enhanced features over time
