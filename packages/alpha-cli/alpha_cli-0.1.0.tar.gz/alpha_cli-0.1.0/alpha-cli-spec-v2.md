# Alpha CLI: Technical Specification v2.0

> Improved specification addressing gaps, outdated information, and architectural traps from v1.0.
> Last updated: December 29, 2025

---

## Changelog from v1.0

| Issue | v1.0 | v2.0 |
|-------|------|------|
| Ticker-to-market matching | Undefined | Full algorithm design with embeddings |
| Congress data source | Capitol Trades scraping (fragile) | House/Senate Stock Watcher APIs |
| Lobbying data | OpenSecrets API | Senate LDA API (OpenSecrets discontinued April 2025) |
| Authentication flow | Undefined | Complete signup → API key → subscription flow |
| Alert architecture | Basic Workers (won't work) | Cron Triggers + Queues + D1 |
| Credential storage | Plaintext config | OS keyring integration |
| MVP scope | 9 premium features | 3 features (kalshi, congress, scan) |
| Polymarket integration | "Simple API" | Full CLOB documentation |
| Arbitrage calculations | Gross profit only | Net profit after fees/slippage |
| Error handling | 4 error codes | Retry logic, circuit breakers, graceful degradation |
| Open source strategy | Vague | Explicit licensing per component |

---

## Table of Contents

1. [Critical Path: Ticker-to-Market Matching](#1-critical-path-ticker-to-market-matching)
2. [Data Sources (Updated)](#2-data-sources-updated)
3. [Authentication & Subscription Flow](#3-authentication--subscription-flow)
4. [Secure Credential Storage](#4-secure-credential-storage)
5. [Backend Architecture (Revised)](#5-backend-architecture-revised)
6. [Polymarket CLOB Integration](#6-polymarket-clob-integration)
7. [Arbitrage Fee Modeling](#7-arbitrage-fee-modeling)
8. [Error Handling & Resilience](#8-error-handling--resilience)
9. [Reduced MVP Scope](#9-reduced-mvp-scope)
10. [Open Source Strategy](#10-open-source-strategy)
11. [Revised Development Roadmap](#11-revised-development-roadmap)
12. [API Specification (OpenAPI)](#12-api-specification-openapi)

---

## 1. Critical Path: Ticker-to-Market Matching

### The Problem

The `alpha scan` feature requires matching stock tickers (e.g., `NVDA`) to relevant prediction markets (e.g., `KXNVIDIA-Q4-EARNINGS`). This is **the core technical challenge** and determines whether the product delivers value.

### Why This Is Hard

1. **No direct mapping exists** — Kalshi doesn't tag markets with stock tickers
2. **Semantic ambiguity** — When Pelosi buys GOOGL, is `KXGOOG-ANTITRUST` or `KXAI-REGULATION` more relevant?
3. **False positives destroy trust** — Bad matches make the product useless
4. **Scale** — Must work across ~500 traded tickers × ~1000 active markets

### Solution: Hybrid Matching System

We use a **three-tier matching system** combining exact matching, semantic embeddings, and LLM validation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TICKER-TO-MARKET MATCHING PIPELINE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Input: Congressional Trade                                                 │
│  ├── Ticker: NVDA                                                          │
│  ├── Company: NVIDIA Corporation                                           │
│  ├── Trade Type: Purchase                                                  │
│  └── Amount: $50,001 - $100,000                                            │
│                                                                             │
│                              ▼                                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TIER 1: Exact Matching (Fast, High Precision)                      │   │
│  │                                                                      │   │
│  │  • Check curated ticker → market mapping table                      │   │
│  │  • Covers top 100 most-traded congressional tickers                 │   │
│  │  • Human-verified mappings, updated weekly                          │   │
│  │  • Example: NVDA → [KXNVDA-*, KXNVIDIA-*]                          │   │
│  │                                                                      │   │
│  │  Hit? → Return matches with relevance_score = 1.0                   │   │
│  │  Miss? → Continue to Tier 2                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TIER 2: Semantic Embedding Search (Medium Speed, Good Recall)      │   │
│  │                                                                      │   │
│  │  Pre-computed (daily):                                              │   │
│  │  • Embed all Kalshi market titles + descriptions                    │   │
│  │  • Store in vector index (Cloudflare Vectorize or Pinecone)         │   │
│  │                                                                      │   │
│  │  At query time:                                                     │   │
│  │  • Build query: "{Company} {Ticker} {Sector} stock price"           │   │
│  │  • Example: "NVIDIA Corporation NVDA semiconductor stock price"     │   │
│  │  • Embed query with same model                                      │   │
│  │  • Cosine similarity search, top-10 candidates                      │   │
│  │  • Filter: similarity > 0.7                                         │   │
│  │                                                                      │   │
│  │  Embedding Model: voyage-finance-2 (if budget allows)               │   │
│  │                   or text-embedding-3-small (OpenAI, cheaper)       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TIER 3: LLM Validation (Slow, High Quality)                        │   │
│  │                                                                      │   │
│  │  For each candidate from Tier 2:                                    │   │
│  │  • Prompt Claude Haiku with:                                        │   │
│  │    "Is the prediction market '{market_title}' directly relevant     │   │
│  │     to the stock {ticker} ({company})? Answer YES/NO with           │   │
│  │     confidence 0-100 and one-sentence explanation."                 │   │
│  │                                                                      │   │
│  │  • Filter: confidence >= 70 AND answer == YES                       │   │
│  │  • Cost: ~$0.001 per validation (Haiku pricing)                     │   │
│  │  • Cache results for 24 hours                                       │   │
│  │                                                                      │   │
│  │  Output: Validated matches with relevance scores                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                              │
│  Output: Ranked list of relevant markets                                   │
│  ├── KXNVIDIA-Q4-EARNINGS    relevance: 0.95                              │
│  ├── KXAICHIP-EXPORT-BAN     relevance: 0.82                              │
│  └── KXNVDA-1000             relevance: 0.78                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Curated Mapping Table Schema

```sql
-- Stored in Cloudflare D1
CREATE TABLE ticker_market_mappings (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,           -- e.g., "NVDA"
    company_name TEXT NOT NULL,     -- e.g., "NVIDIA Corporation"
    sector TEXT,                    -- e.g., "Technology"
    market_pattern TEXT NOT NULL,   -- e.g., "KXNVDA%" or "KXNVIDIA%"
    relevance_type TEXT NOT NULL,   -- "direct" | "sector" | "macro"
    verified_at DATETIME,
    verified_by TEXT,               -- "human" | "llm" | "auto"
    UNIQUE(ticker, market_pattern)
);

-- Index for fast lookups
CREATE INDEX idx_ticker ON ticker_market_mappings(ticker);
```

### Initial Curated List (Top 50 Congressional Tickers)

Based on 2024-2025 congressional trading data:

```
NVDA  → KXNVDA%, KXNVIDIA%, KXAICHIP%
AAPL  → KXAAPL%, KXAPPLE%
MSFT  → KXMSFT%, KXMICROSOFT%
GOOGL → KXGOOG%, KXGOOGLE%, KXALPHABET%
AMZN  → KXAMZN%, KXAMAZON%
META  → KXMETA%, KXFACEBOOK%
TSLA  → KXTSLA%, KXTESLA%
AMD   → KXAMD%
INTC  → KXINTC%, KXINTEL%
...
```

### Embedding Infrastructure

**Option A: Cloudflare Vectorize (Recommended)**
- Native integration with Workers
- 5M vectors on free tier
- ~$0.01/1000 queries on paid tier

**Option B: Pinecone**
- More mature, better tooling
- Free tier: 1 index, 100K vectors
- Serverless: ~$0.08/1M queries

**Embedding Model Costs**

| Model | Cost per 1M tokens | Quality | Latency |
|-------|-------------------|---------|---------|
| voyage-finance-2 | $0.12 | Best for finance | 100ms |
| text-embedding-3-small | $0.02 | Good general | 50ms |
| text-embedding-3-large | $0.13 | Better general | 80ms |

**Recommendation**: Start with `text-embedding-3-small` for cost efficiency. Upgrade to `voyage-finance-2` if matching quality is insufficient.

### Validation Requirements

Before shipping `alpha scan`:

1. **Build test set**: 100 manual ticker → market mappings
2. **Measure precision**: % of returned matches that are actually relevant
3. **Measure recall**: % of relevant markets that are returned
4. **Target**: Precision > 85%, Recall > 70%
5. **User feedback loop**: Allow users to flag bad matches

### Cost Estimate (Premium User)

Per `alpha scan` call:
- Tier 1 lookup: Free (D1 query)
- Tier 2 embedding: ~$0.0001 (one query embedding)
- Tier 3 LLM validation: ~$0.005 (5 candidates × $0.001)
- **Total: ~$0.005 per call**

At 100 calls/user/month: $0.50/user/month (well under $20 price point)

---

## 2. Data Sources (Updated)

### Congress Trading Data

**Primary: House Stock Watcher API**
- URL: `https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json`
- Format: JSON array of all transactions
- Update frequency: Daily
- Auth: None required
- Rate limit: Standard S3 (effectively unlimited for reads)
- Source: [housestockwatcher.com/api](https://housestockwatcher.com/api)

**Primary: Senate Stock Watcher API**
- URL: `https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json`
- Format: JSON array of all transactions
- Update frequency: Daily
- Auth: None required
- Source: [senatestockwatcher.com/api](https://senatestockwatcher.com/api)

**Fallback: Quiver Quantitative API**
- URL: `https://api.quiverquant.com/beta/historical/congresstrading`
- Auth: API key required
- Cost: $25/month
- When to use: If Stock Watcher data is stale or unavailable

**Data Schema (House/Senate Stock Watcher)**
```json
{
  "transaction_date": "2025-12-15",
  "disclosure_date": "2025-12-18",
  "owner": "joint",
  "ticker": "NVDA",
  "asset_description": "NVIDIA Corporation",
  "asset_type": "Stock",
  "type": "purchase",
  "amount": "$50,001 - $100,000",
  "representative": "Tommy Tuberville",
  "district": "AL07",
  "ptr_link": "https://...",
  "cap_gains_over_200_usd": false
}
```

**Note**: Stock Watcher data does NOT include party affiliation. Merge with a members dataset:
- Source: [github.com/unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)

### Prediction Markets

**Kalshi API**
- Docs: [docs.kalshi.com](https://docs.kalshi.com/welcome)
- Base URL: `https://api.elections.kalshi.com/trade-api/v2`
- Auth: JWT Bearer token (expires every 30 minutes, must refresh)
- Rate limit: Generous (undocumented, ~100 req/sec observed)
- Key endpoints:
  - `GET /markets` — List all markets
  - `GET /markets/{ticker}` — Market details
  - `GET /markets/{ticker}/orderbook` — Order book
  - `GET /portfolio/positions` — User positions (auth required)

**Polymarket CLOB API** (See Section 6 for full details)
- Docs: [docs.polymarket.com](https://docs.polymarket.com/)
- Base URL: `https://clob.polymarket.com`
- Auth: L1 (wallet) or L2 (API key via HMAC-SHA256)
- Complexity: Higher than Kalshi — requires understanding CLOB model

### SEC Form 4 (Insider Trading)

**Primary: SEC EDGAR API**
- Base URL: `https://data.sec.gov`
- Filings: `https://data.sec.gov/submissions/CIK{cik}.json`
- Rate limit: **10 requests/second per IP**
- **Required**: User-Agent header with contact email
  ```
  User-Agent: AlphaCLI/1.0 (contact@alpha.dev)
  ```
- Blocked for: Missing User-Agent, bot-like behavior
- Source: [sec.gov/developer](https://www.sec.gov/developer)

**Fallback: sec-api.io**
- Cost: $49/month
- Benefit: Pre-parsed data, faster queries
- When to use: If EDGAR parsing is too slow or rate-limited

### Lobbying Data

**Primary: Senate LDA API** (OpenSecrets API discontinued April 2025)
- Docs: [lda.senate.gov/api/redoc/v1](https://lda.senate.gov/api/redoc/v1/)
- Base URL: `https://lda.senate.gov/api/v1`
- Auth: Optional API key (anonymous access is rate-limited)
- Endpoints:
  - `/filings/` — Search registrations and reports
  - `/registrants/` — Lobbying organizations
  - `/lobbyists/` — Individual lobbyists
  - `/clients/` — Lobbying clients
- Filing types:
  - LD-1: Registrations
  - LD-2: Quarterly activity reports
  - LD-203: Contribution reports

### Federal Contracts

**Primary: USAspending API**
- Docs: [api.usaspending.gov](https://api.usaspending.gov/)
- Base URL: `https://api.usaspending.gov/api/v2`
- Auth: None required
- Rate limit: Generous (undocumented)
- Key endpoints:
  - `POST /search/spending_by_award/` — Search contracts
  - `GET /awards/{award_id}/` — Award details
  - `POST /search/spending_by_geography/` — Geographic breakdown
- Data freshness: 3-5 business days after award
- Source: [GitHub - usaspending-api](https://github.com/fedspendingtransparency/usaspending-api)

### Economic Calendar

**Primary: FRED API (St. Louis Fed)**
- Docs: [fred.stlouisfed.org/docs/api](https://fred.stlouisfed.org/docs/api/fred/)
- Base URL: `https://api.stlouisfed.org/fred`
- Auth: Free API key required
- Rate limit: 120 requests/minute
- Endpoints:
  - `/releases` — List economic releases
  - `/release/dates` — Release schedule
  - `/series/observations` — Historical data
- Coverage: CPI, GDP, unemployment, Fed funds rate, etc.

**Fallback: Trading Economics API**
- Cost: $49/month
- Benefit: Global coverage, more granular events
- When to use: Need non-US data or more event types

### Data Source Summary

| Data | Primary Source | Auth | Rate Limit | Fallback |
|------|---------------|------|------------|----------|
| Congress trades | House/Senate Stock Watcher | None | Unlimited | Quiver ($25/mo) |
| Kalshi markets | Kalshi API | JWT | ~100/sec | None |
| Polymarket | CLOB API | HMAC | Undocumented | None |
| SEC Form 4 | EDGAR API | User-Agent | 10/sec | sec-api.io ($49/mo) |
| Lobbying | Senate LDA API | Optional key | Throttled | None |
| Contracts | USAspending API | None | Generous | FPDS.gov |
| Econ calendar | FRED API | API key | 120/min | Trading Economics |

---

## 3. Authentication & Subscription Flow

### Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION & SUBSCRIPTION FLOW                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NEW USER JOURNEY                                                           │
│  ════════════════                                                           │
│                                                                             │
│  1. Install CLI                                                             │
│     $ pip install alpha-cli                                                 │
│     $ brew install alpha-cli                                                │
│                                                                             │
│  2. Use free features (no account needed)                                   │
│     $ alpha kalshi markets                    ✓ Works immediately          │
│     $ alpha congress trades                   ✓ Works immediately          │
│                                                                             │
│  3. Try premium feature (blocked)                                           │
│     $ alpha scan                                                            │
│     ╭──────────────────────────────────────────────────────────────────╮   │
│     │ ⚠️  Premium feature requires authentication                       │   │
│     │                                                                   │   │
│     │ Run `alpha login` to sign in or create an account.               │   │
│     │ Premium features are $20/month. Free 7-day trial available.      │   │
│     ╰──────────────────────────────────────────────────────────────────╯   │
│                                                                             │
│  4. Create account                                                          │
│     $ alpha login                                                           │
│     ╭──────────────────────────────────────────────────────────────────╮   │
│     │ Opening browser to complete authentication...                     │   │
│     │                                                                   │   │
│     │ If browser doesn't open, visit:                                  │   │
│     │ https://alpha.dev/auth/cli?code=ABC123                           │   │
│     │                                                                   │   │
│     │ Waiting for authentication...                                    │   │
│     ╰──────────────────────────────────────────────────────────────────╯   │
│                                                                             │
│  5. Browser flow                                                            │
│     ┌─────────────────────────────────────────┐                            │
│     │  alpha.dev/auth/cli                     │                            │
│     ├─────────────────────────────────────────┤                            │
│     │                                         │                            │
│     │  Sign in to Alpha CLI                   │                            │
│     │                                         │                            │
│     │  [Email address: _____________ ]        │                            │
│     │                                         │                            │
│     │  [ Continue with Email ]                │                            │
│     │  [ Continue with GitHub ]               │                            │
│     │  [ Continue with Google ]               │                            │
│     │                                         │                            │
│     └─────────────────────────────────────────┘                            │
│                                                                             │
│  6. Email magic link / OAuth completes                                      │
│     → Backend generates API key                                            │
│     → Redirects to alpha.dev/auth/success?token=xxx                        │
│     → Page displays: "Authentication complete! Return to terminal."        │
│     → CLI polls backend, receives API key                                  │
│                                                                             │
│  7. CLI stores credentials securely                                         │
│     $ alpha login                                                           │
│     ╭──────────────────────────────────────────────────────────────────╮   │
│     │ ✓ Authenticated as user@example.com                              │   │
│     │                                                                   │   │
│     │ Account status: Free tier                                        │   │
│     │ To unlock premium features, run `alpha upgrade`                  │   │
│     ╰──────────────────────────────────────────────────────────────────╯   │
│                                                                             │
│  8. Upgrade to premium                                                      │
│     $ alpha upgrade                                                         │
│     → Opens Stripe Checkout in browser                                     │
│     → User completes payment                                               │
│     → Stripe webhook updates subscription status                           │
│     → Next CLI call sees premium status                                    │
│                                                                             │
│  9. Use premium features                                                    │
│     $ alpha scan                              ✓ Works!                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### API Key Generation

```python
# Backend: Generate API key on successful authentication
import secrets
import hashlib

def generate_api_key(user_id: str, environment: str = "live") -> tuple[str, str]:
    """
    Returns (display_key, key_hash)
    - display_key: Shown to user once, stored in their keyring
    - key_hash: Stored in our database for validation
    """
    # Generate 32 random bytes = 256 bits of entropy
    random_part = secrets.token_urlsafe(32)

    # Prefix for identification (following Stripe's pattern)
    prefix = f"alpha_{environment}_"

    # Full key shown to user
    display_key = f"{prefix}{random_part}"

    # Hash for storage (never store raw key)
    key_hash = hashlib.sha256(display_key.encode()).hexdigest()

    return display_key, key_hash

# Example output:
# display_key: alpha_live_x7Kj9mNpQrStUvWxYz1234567890abcdefghij
# key_hash: 8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b
```

### Backend Database Schema

```sql
-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,              -- UUID
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    stripe_customer_id TEXT UNIQUE
);

-- API keys table
CREATE TABLE api_keys (
    id TEXT PRIMARY KEY,              -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    key_hash TEXT UNIQUE NOT NULL,    -- SHA-256 of full key
    key_prefix TEXT NOT NULL,         -- First 12 chars for identification
    environment TEXT NOT NULL,         -- "live" or "test"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    revoked_at DATETIME,
    UNIQUE(user_id, environment)       -- One active key per environment
);

-- Subscriptions table (synced from Stripe webhooks)
CREATE TABLE subscriptions (
    id TEXT PRIMARY KEY,              -- Stripe subscription ID
    user_id TEXT NOT NULL REFERENCES users(id),
    status TEXT NOT NULL,             -- "active", "canceled", "past_due", "trialing"
    current_period_start DATETIME,
    current_period_end DATETIME,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
```

### CLI Authentication State Machine

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class AuthState(Enum):
    ANONYMOUS = "anonymous"           # No API key stored
    AUTHENTICATED_FREE = "free"       # Valid API key, no subscription
    AUTHENTICATED_PREMIUM = "premium" # Valid API key + active subscription
    AUTHENTICATED_EXPIRED = "expired" # Valid API key, subscription lapsed
    INVALID = "invalid"               # API key rejected by backend

@dataclass
class AuthContext:
    state: AuthState
    user_email: str | None = None
    subscription_end: datetime | None = None

    def can_use_premium(self) -> bool:
        return self.state == AuthState.AUTHENTICATED_PREMIUM

# Auth check on CLI startup (cached for 5 minutes)
async def get_auth_context() -> AuthContext:
    api_key = get_stored_api_key()  # From keyring

    if not api_key:
        return AuthContext(state=AuthState.ANONYMOUS)

    # Check cache first
    cached = get_cached_auth_context()
    if cached and cached.is_fresh():
        return cached.context

    # Validate with backend
    response = await backend_client.post("/auth/validate", {
        "api_key": api_key
    })

    if response.status == 401:
        return AuthContext(state=AuthState.INVALID)

    data = response.json()
    context = AuthContext(
        state=AuthState(data["status"]),
        user_email=data.get("email"),
        subscription_end=data.get("subscription_end")
    )

    cache_auth_context(context, ttl_seconds=300)
    return context
```

### Stripe Integration

**Webhook Events to Handle**

```typescript
// Backend: Stripe webhook handler
app.post('/webhooks/stripe', async (c) => {
  const sig = c.req.header('stripe-signature');
  const body = await c.req.text();

  const event = stripe.webhooks.constructEvent(
    body,
    sig,
    c.env.STRIPE_WEBHOOK_SECRET
  );

  switch (event.type) {
    case 'checkout.session.completed':
      // New subscription created
      await handleNewSubscription(event.data.object);
      break;

    case 'customer.subscription.updated':
      // Subscription changed (upgrade, downgrade, renewal)
      await handleSubscriptionUpdate(event.data.object);
      break;

    case 'customer.subscription.deleted':
      // Subscription canceled
      await handleSubscriptionCanceled(event.data.object);
      break;

    case 'invoice.payment_failed':
      // Payment failed - mark as past_due
      await handlePaymentFailed(event.data.object);
      break;
  }

  return c.json({ received: true });
});
```

---

## 4. Secure Credential Storage

### Problem with v1.0

```toml
# ~/.alpha/config.toml (INSECURE - v1.0)
[auth]
api_key = "alpha_live_xxxxxxxxxxxxxxxxxxxxxxxx"

[kalshi]
api_key = "your-kalshi-api-key"
private_key_path = "~/.kalshi/private.pem"
```

Issues:
1. Plaintext API keys readable by any process
2. If config is accidentally committed to git, credentials are exposed
3. Kalshi private key path stored alongside Alpha credentials

### Solution: OS Keyring Integration

Use the [Python keyring library](https://keyring.readthedocs.io/) which integrates with:
- **macOS**: Keychain
- **Windows**: Credential Locker
- **Linux**: Secret Service (GNOME Keyring, KWallet)

```python
# src/alpha_cli/credentials.py
import keyring
import json
from dataclasses import dataclass
from typing import Optional

SERVICE_NAME = "alpha-cli"

@dataclass
class AlphaCredentials:
    api_key: str
    user_email: Optional[str] = None

@dataclass
class KalshiCredentials:
    api_key: str
    private_key_path: Optional[str] = None

def store_alpha_credentials(creds: AlphaCredentials) -> None:
    """Store Alpha CLI credentials in OS keyring."""
    keyring.set_password(
        SERVICE_NAME,
        "alpha_credentials",
        json.dumps({
            "api_key": creds.api_key,
            "user_email": creds.user_email
        })
    )

def get_alpha_credentials() -> Optional[AlphaCredentials]:
    """Retrieve Alpha CLI credentials from OS keyring."""
    data = keyring.get_password(SERVICE_NAME, "alpha_credentials")
    if not data:
        return None
    parsed = json.loads(data)
    return AlphaCredentials(**parsed)

def delete_alpha_credentials() -> None:
    """Remove Alpha CLI credentials from OS keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "alpha_credentials")
    except keyring.errors.PasswordDeleteError:
        pass  # Already deleted

def store_kalshi_credentials(creds: KalshiCredentials) -> None:
    """Store Kalshi credentials separately."""
    keyring.set_password(
        SERVICE_NAME,
        "kalshi_credentials",
        json.dumps({
            "api_key": creds.api_key,
            "private_key_path": creds.private_key_path
        })
    )

def get_kalshi_credentials() -> Optional[KalshiCredentials]:
    """Retrieve Kalshi credentials."""
    data = keyring.get_password(SERVICE_NAME, "kalshi_credentials")
    if not data:
        return None
    parsed = json.loads(data)
    return KalshiCredentials(**parsed)
```

### Config File (Non-Sensitive Settings Only)

```toml
# ~/.alpha/config.toml (v2.0 - no secrets)
[display]
format = "table"      # table, json, csv
color = true
timezone = "America/New_York"

[cache]
enabled = true
ttl_minutes = 15

[alerts]
# Webhook URL stored in keyring, not here
enabled = true
```

### CLI Credential Commands

```bash
# Store Alpha credentials (interactive, uses keyring)
$ alpha login
Opening browser for authentication...
✓ Authenticated as user@example.com
✓ API key stored securely in system keyring

# Store Kalshi credentials (interactive)
$ alpha config kalshi
Enter Kalshi API Key: ********
Enter path to private key [~/.kalshi/private.pem]:
✓ Kalshi credentials stored securely in system keyring

# View what's stored (masked)
$ alpha config show
Alpha CLI:
  Email: user@example.com
  API Key: alpha_live_x7Kj...ghij

Kalshi:
  API Key: kalshi_...
  Private Key: ~/.kalshi/private.pem

# Clear all credentials
$ alpha logout
✓ Removed Alpha credentials
✓ Removed Kalshi credentials
```

### Fallback for Headless/CI Environments

```bash
# Environment variables take precedence (for CI/automation)
export ALPHA_API_KEY="alpha_live_xxx"
export KALSHI_API_KEY="xxx"
export KALSHI_PRIVATE_KEY_PATH="/path/to/key.pem"

# CLI checks in order:
# 1. Environment variables
# 2. OS keyring
# 3. (Legacy) config file (with deprecation warning)
```

---

## 5. Backend Architecture (Revised)

### Alert System Architecture

The v1.0 spec mentioned alerts but didn't address that Cloudflare Workers are stateless and can't run background jobs. Here's the correct architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ALERT SYSTEM ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CRON TRIGGER (Every 5 minutes)                                     │   │
│  │  wrangler.toml: crons = ["*/5 * * * *"]                            │   │
│  │                                                                      │   │
│  │  • Triggered by Cloudflare on schedule                              │   │
│  │  • CPU limit: 30 seconds (since interval >= 1 hour... wait no)     │   │
│  │  • Actually for <1hr interval: 30 second CPU limit                  │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ALERT PROCESSOR WORKER                                             │   │
│  │                                                                      │   │
│  │  scheduled() handler:                                               │   │
│  │  1. Fetch all active alerts from D1                                 │   │
│  │  2. Group by data source (congress, kalshi, polymarket)            │   │
│  │  3. Batch fetch current data (one API call per source)             │   │
│  │  4. Check each alert against current data                          │   │
│  │  5. For triggered alerts, enqueue webhook delivery                 │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CLOUDFLARE QUEUE: alert-webhooks                                   │   │
│  │                                                                      │   │
│  │  Message schema:                                                    │   │
│  │  {                                                                  │   │
│  │    "alert_id": "abc123",                                           │   │
│  │    "user_id": "user_456",                                          │   │
│  │    "webhook_url": "https://discord.com/api/webhooks/...",          │   │
│  │    "payload": { ... alert data ... },                              │   │
│  │    "attempt": 1                                                    │   │
│  │  }                                                                  │   │
│  │                                                                      │   │
│  │  Benefits:                                                          │   │
│  │  • Automatic retries with backoff                                  │   │
│  │  • Dead letter queue for failures                                  │   │
│  │  • No CPU time limit on queue consumers                            │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WEBHOOK DELIVERY WORKER (Queue Consumer)                           │   │
│  │                                                                      │   │
│  │  queue() handler:                                                   │   │
│  │  1. Extract webhook_url and payload from message                   │   │
│  │  2. POST to webhook_url with payload                               │   │
│  │  3. If success (2xx): ack message, log delivery                    │   │
│  │  4. If failure: retry (up to 3 attempts) or move to DLQ            │   │
│  │  5. Update alert.last_triggered_at in D1                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  D1 DATABASE: Alert State                                           │   │
│  │                                                                      │   │
│  │  CREATE TABLE alerts (                                              │   │
│  │    id TEXT PRIMARY KEY,                                            │   │
│  │    user_id TEXT NOT NULL,                                          │   │
│  │    alert_type TEXT NOT NULL,  -- 'congress_ticker', 'market_move' │   │
│  │    config JSON NOT NULL,       -- type-specific configuration      │   │
│  │    webhook_url TEXT NOT NULL,                                      │   │
│  │    enabled BOOLEAN DEFAULT TRUE,                                   │   │
│  │    last_triggered_at DATETIME,                                     │   │
│  │    cooldown_minutes INTEGER DEFAULT 60,                            │   │
│  │    created_at DATETIME DEFAULT CURRENT_TIMESTAMP                   │   │
│  │  );                                                                 │   │
│  │                                                                      │   │
│  │  -- Example configs:                                                │   │
│  │  -- congress_ticker: {"ticker": "NVDA"}                            │   │
│  │  -- market_move: {"market": "KXFED-RATE", "threshold_cents": 5}   │   │
│  │  -- arb_opportunity: {"min_profit_pct": 2.0}                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### wrangler.toml Configuration

```toml
name = "alpha-backend"
main = "src/index.ts"
compatibility_date = "2024-12-01"

# Cron triggers for scheduled tasks
[triggers]
crons = ["*/5 * * * *"]  # Every 5 minutes

# D1 Database binding
[[d1_databases]]
binding = "DB"
database_name = "alpha-db"
database_id = "xxxxx"

# KV namespace for caching
[[kv_namespaces]]
binding = "CACHE"
id = "xxxxx"

# Queue for webhook delivery
[[queues.producers]]
binding = "WEBHOOK_QUEUE"
queue = "alert-webhooks"

[[queues.consumers]]
queue = "alert-webhooks"
max_batch_size = 10
max_retries = 3
dead_letter_queue = "alert-webhooks-dlq"

# Environment variables (secrets set via wrangler secret)
[vars]
ENVIRONMENT = "production"
```

### Revised Backend Structure

```
alpha-backend/
├── src/
│   ├── index.ts                 # Main router (Hono)
│   ├── scheduled.ts             # Cron trigger handler
│   ├── queue.ts                 # Queue consumer handler
│   ├── middleware/
│   │   ├── auth.ts              # API key validation
│   │   ├── rateLimit.ts         # Per-user rate limiting
│   │   └── cache.ts             # Response caching
│   ├── handlers/
│   │   ├── auth.ts              # /auth/* endpoints
│   │   ├── scan.ts              # /scan endpoint
│   │   ├── arb.ts               # /arb endpoint
│   │   ├── alerts.ts            # /alerts/* endpoints
│   │   └── webhooks.ts          # /webhooks/stripe
│   ├── services/
│   │   ├── congress.ts          # Congress data fetching
│   │   ├── kalshi.ts            # Kalshi API client
│   │   ├── polymarket.ts        # Polymarket CLOB client
│   │   ├── matching.ts          # Ticker-to-market matching
│   │   └── embedding.ts         # Vector embedding operations
│   ├── db/
│   │   ├── schema.sql           # D1 schema
│   │   ├── users.ts             # User operations
│   │   ├── alerts.ts            # Alert operations
│   │   └── subscriptions.ts     # Subscription operations
│   └── types/
│       └── index.ts             # Shared type definitions
├── wrangler.toml
├── package.json
└── tsconfig.json
```

### CPU Time Management

Cloudflare Workers have strict CPU limits. Here's how to stay within them:

```typescript
// Problem: Complex cross-reference might exceed 30ms CPU
// Solution: Split into multiple requests or use caching aggressively

// BAD: Do everything in one request
app.post('/scan', async (c) => {
  const congressTrades = await fetchCongressTrades();     // 5ms
  const markets = await fetchKalshiMarkets();             // 5ms
  const matches = await matchTickersToMarkets(trades);    // 50ms+ (TOO SLOW)
  return c.json({ matches });
});

// GOOD: Pre-compute matches, serve from cache
app.post('/scan', async (c) => {
  const { days, ticker } = await c.req.json();

  // Check cache first (KV lookup is fast)
  const cacheKey = `scan:${days}:${ticker || 'all'}`;
  const cached = await c.env.CACHE.get(cacheKey, 'json');
  if (cached) {
    return c.json(cached);
  }

  // If not cached, trigger background refresh and return stale
  await c.env.REFRESH_QUEUE.send({ type: 'scan', params: { days, ticker } });

  // Return last known good data (or empty if first request)
  const stale = await c.env.CACHE.get(`scan:${days}:${ticker || 'all'}:stale`, 'json');
  return c.json(stale || { matches: [], stale: true });
});

// Background worker pre-computes scan results every 15 minutes
// This runs in scheduled() handler with 30-second CPU limit
async function refreshScanCache(env: Env) {
  const congressTrades = await fetchCongressTrades(30);  // Last 30 days
  const markets = await fetchKalshiMarkets();

  // Match in batches to avoid CPU timeout
  const matches = [];
  for (const trade of congressTrades) {
    const tradeMatches = await matchSingleTrade(trade, markets, env);
    matches.push({ trade, markets: tradeMatches });

    // Yield to avoid CPU timeout (check every 10 trades)
    if (matches.length % 10 === 0) {
      await scheduler.wait(1); // 1ms yield
    }
  }

  // Cache results
  await env.CACHE.put('scan:30:all', JSON.stringify({ matches }), {
    expirationTtl: 900  // 15 minutes
  });
  await env.CACHE.put('scan:30:all:stale', JSON.stringify({ matches }), {
    expirationTtl: 86400  // 24 hours (fallback)
  });
}
```

---

## 6. Polymarket CLOB Integration

### Understanding the CLOB Model

Polymarket uses a **Central Limit Order Book (CLOB)** that is fundamentally different from Kalshi's simpler API:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    POLYMARKET vs KALSHI: KEY DIFFERENCES                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KALSHI                              POLYMARKET                             │
│  ══════                              ══════════                             │
│                                                                             │
│  • Centralized exchange              • Hybrid decentralized (CLOB)         │
│  • Traditional REST API              • REST + WebSocket + Blockchain       │
│  • Bearer token auth (JWT)           • L1 (wallet) or L2 (API key/HMAC)   │
│  • Simple market tickers             • Token IDs (condition IDs)           │
│  • USD balances                      • USDC on Polygon                     │
│  • Fees: 0% (currently)              • Fees: Variable + gas                │
│  • US-only (regulated)               • Non-US (regulatory gray area)       │
│                                                                             │
│  API Complexity                                                             │
│  ══════════════                                                             │
│                                                                             │
│  Kalshi: "Get price for KXFED-RATE"                                        │
│  GET /markets/KXFED-RATE → { yes_price: 0.65, no_price: 0.36 }            │
│                                                                             │
│  Polymarket: "Get price for Fed rate cut market"                           │
│  1. Find market by slug or search                                          │
│  2. Get condition_id from market                                           │
│  3. Get token_ids for YES and NO outcomes                                  │
│  4. Query order book for each token                                        │
│  5. Calculate mid price from best bid/ask                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Polymarket API Client

```python
# src/alpha_cli/clients/polymarket.py
import httpx
from dataclasses import dataclass
from typing import Optional
import hashlib
import hmac
import time
import base64

CLOB_BASE_URL = "https://clob.polymarket.com"
GAMMA_BASE_URL = "https://gamma-api.polymarket.com"

@dataclass
class PolymarketMarket:
    condition_id: str
    question: str
    slug: str
    yes_token_id: str
    no_token_id: str
    volume: float
    liquidity: float
    end_date: str

@dataclass
class PolymarketPrice:
    market: PolymarketMarket
    yes_price: float
    no_price: float
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    spread: float

class PolymarketClient:
    """
    Client for Polymarket CLOB API.

    Authentication levels:
    - None: Public data (markets, prices, order books)
    - L2: API key for trading (requires wallet signature to generate)

    For alpha-cli, we only need public data access.
    """

    def __init__(self):
        self.http = httpx.AsyncClient(
            base_url=CLOB_BASE_URL,
            timeout=30.0,
            headers={"User-Agent": "AlphaCLI/1.0"}
        )
        self.gamma = httpx.AsyncClient(
            base_url=GAMMA_BASE_URL,
            timeout=30.0,
            headers={"User-Agent": "AlphaCLI/1.0"}
        )

    async def get_markets(self, limit: int = 100, active: bool = True) -> list[PolymarketMarket]:
        """Fetch markets from Gamma API (better for discovery)."""
        response = await self.gamma.get("/markets", params={
            "limit": limit,
            "active": active,
            "closed": False
        })
        response.raise_for_status()

        markets = []
        for m in response.json():
            # Each market can have multiple outcomes (YES/NO tokens)
            tokens = m.get("tokens", [])
            yes_token = next((t for t in tokens if t.get("outcome") == "Yes"), None)
            no_token = next((t for t in tokens if t.get("outcome") == "No"), None)

            if yes_token and no_token:
                markets.append(PolymarketMarket(
                    condition_id=m["conditionId"],
                    question=m["question"],
                    slug=m["slug"],
                    yes_token_id=yes_token["token_id"],
                    no_token_id=no_token["token_id"],
                    volume=float(m.get("volume", 0)),
                    liquidity=float(m.get("liquidity", 0)),
                    end_date=m.get("endDate")
                ))

        return markets

    async def get_price(self, market: PolymarketMarket) -> PolymarketPrice:
        """Get current price from order book."""
        # Fetch order books for both tokens
        yes_book = await self._get_order_book(market.yes_token_id)
        no_book = await self._get_order_book(market.no_token_id)

        # Calculate prices from order book
        yes_bid = float(yes_book["bids"][0]["price"]) if yes_book["bids"] else 0
        yes_ask = float(yes_book["asks"][0]["price"]) if yes_book["asks"] else 1
        no_bid = float(no_book["bids"][0]["price"]) if no_book["bids"] else 0
        no_ask = float(no_book["asks"][0]["price"]) if no_book["asks"] else 1

        # Mid prices
        yes_price = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else yes_ask
        no_price = (no_bid + no_ask) / 2 if no_bid and no_ask else no_ask

        return PolymarketPrice(
            market=market,
            yes_price=yes_price,
            no_price=no_price,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_bid=no_bid,
            no_ask=no_ask,
            spread=yes_ask - yes_bid
        )

    async def _get_order_book(self, token_id: str) -> dict:
        """Fetch order book for a specific token."""
        response = await self.http.get(f"/book", params={
            "token_id": token_id
        })
        response.raise_for_status()
        return response.json()

    async def search_markets(self, query: str) -> list[PolymarketMarket]:
        """Search markets by query string."""
        response = await self.gamma.get("/markets", params={
            "tag": query,  # or use full-text search if available
            "active": True
        })
        response.raise_for_status()
        # ... parse response similar to get_markets
```

### Mapping Between Platforms

For arbitrage detection, we need to match equivalent markets across Kalshi and Polymarket:

```python
# Pre-computed mappings for common markets
CROSS_PLATFORM_MAPPINGS = {
    # Fed rate decisions
    "KXFED-RATE-JAN-2026": {
        "polymarket_slug": "will-the-fed-cut-rates-january-2026",
        "match_type": "exact",
        "resolution_alignment": True
    },
    # Bitcoin price targets
    "KXBTC-150K-Q1": {
        "polymarket_slug": "bitcoin-150k-march-2026",
        "match_type": "approximate",  # Resolution dates may differ slightly
        "resolution_alignment": False
    },
    # ... more mappings
}

async def find_equivalent_market(
    kalshi_ticker: str,
    polymarket_client: PolymarketClient
) -> Optional[PolymarketMarket]:
    """Find equivalent Polymarket market for a Kalshi ticker."""

    # Check pre-computed mappings first
    if kalshi_ticker in CROSS_PLATFORM_MAPPINGS:
        mapping = CROSS_PLATFORM_MAPPINGS[kalshi_ticker]
        markets = await polymarket_client.search_markets(mapping["polymarket_slug"])
        if markets:
            return markets[0]

    # Fall back to semantic search (more expensive)
    kalshi_market = await kalshi_client.get_market(kalshi_ticker)
    query = kalshi_market.title  # e.g., "Will the Fed cut rates in January 2026?"

    candidates = await polymarket_client.search_markets(query)

    # Use embedding similarity to find best match
    # (implementation depends on embedding service)

    return best_match if similarity > 0.9 else None
```

---

## 7. Arbitrage Fee Modeling

### The Problem with v1.0

```
# v1.0 output (MISLEADING)
Cross-platform arb:
Buy YES on Polymarket @ 31¢ + Buy NO on Kalshi @ 68¢ = 99¢
Guaranteed profit: 1¢ per contract (1.0% ROI)
After fees: ~0.3% net profit
```

This is misleading because:
1. **Kalshi fees are higher than implied** (up to 10% of winnings)
2. **Polymarket has gas fees** on Polygon
3. **Spread/slippage** eats into profit on thin order books
4. **Capital lockup** isn't accounted for

### Accurate Fee Model

```python
# src/alpha_cli/services/arb.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

@dataclass
class ArbitrageOpportunity:
    kalshi_market: str
    polymarket_market: str
    description: str

    # Prices
    kalshi_yes: Decimal
    kalshi_no: Decimal
    polymarket_yes: Decimal
    polymarket_no: Decimal

    # Best execution
    buy_yes_platform: Literal["kalshi", "polymarket"]
    buy_no_platform: Literal["kalshi", "polymarket"]
    buy_yes_price: Decimal
    buy_no_price: Decimal

    # Profit analysis
    gross_cost: Decimal           # Cost to enter position
    gross_payout: Decimal         # Guaranteed payout ($1.00)
    gross_profit: Decimal         # Before fees
    gross_roi_pct: Decimal

    # Fee breakdown
    kalshi_fee: Decimal           # Fee on winning side
    polymarket_gas: Decimal       # Polygon gas estimate
    polymarket_spread: Decimal    # Bid-ask spread cost
    total_fees: Decimal

    # Net profit
    net_profit: Decimal
    net_roi_pct: Decimal

    # Time value
    days_to_resolution: int
    annualized_roi_pct: Decimal

    # Liquidity
    max_size_usd: Decimal         # Max position before moving market

    # Risk factors
    resolution_risk: bool         # Do markets resolve identically?
    counterparty_risk: str        # Platform risk assessment

@dataclass
class FeeStructure:
    """Current fee structures as of Dec 2025."""

    # Kalshi fees (tiered based on winnings)
    # Source: https://kalshi.com/docs/fees
    kalshi_fee_rate: Decimal = Decimal("0.07")  # 7% of profit (simplified)
    kalshi_min_fee: Decimal = Decimal("0.00")   # No minimum

    # Polymarket fees
    # Trading fee: 0% (currently waived)
    # Gas: Variable based on Polygon network
    polymarket_trading_fee: Decimal = Decimal("0.00")
    polymarket_avg_gas_usd: Decimal = Decimal("0.02")  # ~$0.02 per tx

    # Spread cost (estimated)
    avg_spread_pct: Decimal = Decimal("0.02")  # 2% of position

def calculate_arbitrage(
    kalshi_yes: Decimal,
    kalshi_no: Decimal,
    poly_yes: Decimal,
    poly_no: Decimal,
    fees: FeeStructure = FeeStructure()
) -> ArbitrageOpportunity | None:
    """
    Calculate if an arbitrage opportunity exists after fees.

    Arbitrage exists when:
    - Buy YES on platform A + Buy NO on platform B < $1.00 - fees

    Returns None if no profitable opportunity exists.
    """

    # Option 1: YES on Kalshi, NO on Polymarket
    cost_1 = kalshi_yes + poly_no

    # Option 2: YES on Polymarket, NO on Kalshi
    cost_2 = poly_yes + kalshi_no

    # Find cheaper option
    if cost_1 < cost_2:
        buy_yes_platform = "kalshi"
        buy_no_platform = "polymarket"
        buy_yes_price = kalshi_yes
        buy_no_price = poly_no
        gross_cost = cost_1
    else:
        buy_yes_platform = "polymarket"
        buy_no_platform = "kalshi"
        buy_yes_price = poly_yes
        buy_no_price = kalshi_no
        gross_cost = cost_2

    # Gross profit (before fees)
    gross_payout = Decimal("1.00")
    gross_profit = gross_payout - gross_cost

    if gross_profit <= 0:
        return None

    gross_roi_pct = (gross_profit / gross_cost) * 100

    # Calculate fees
    # Kalshi fee applies to the winning side's profit
    # Worst case: we pay on the larger side
    kalshi_position = kalshi_yes if buy_yes_platform == "kalshi" else kalshi_no
    kalshi_profit_if_win = gross_payout - kalshi_position
    kalshi_fee = kalshi_profit_if_win * fees.kalshi_fee_rate

    # Polymarket fees
    polymarket_gas = fees.polymarket_avg_gas_usd * 2  # Entry + exit
    polymarket_spread = gross_cost * fees.avg_spread_pct

    total_fees = kalshi_fee + polymarket_gas + polymarket_spread

    # Net profit
    net_profit = gross_profit - total_fees

    if net_profit <= 0:
        return None

    net_roi_pct = (net_profit / gross_cost) * 100

    return ArbitrageOpportunity(
        # ... fill in all fields
        gross_profit=gross_profit,
        gross_roi_pct=gross_roi_pct,
        kalshi_fee=kalshi_fee,
        polymarket_gas=polymarket_gas,
        polymarket_spread=polymarket_spread,
        total_fees=total_fees,
        net_profit=net_profit,
        net_roi_pct=net_roi_pct,
        # ...
    )
```

### Improved Output

```bash
$ alpha arb --min-net-profit 3

┌─────────────────────────────────────────────────────────────────────────────┐
│ ARBITRAGE OPPORTUNITIES (Net profit > 3%)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ "Will BTC exceed $150k by March 31, 2026?"                                  │
│                                                                             │
│   Kalshi (KXBTC-150K-Q1):     YES @ 34¢  /  NO @ 68¢                       │
│   Polymarket:                  YES @ 29¢  /  NO @ 73¢                       │
│                                                                             │
│   Best execution:                                                           │
│   ├── Buy YES on Polymarket @ 29¢                                          │
│   └── Buy NO on Kalshi @ 68¢                                               │
│                                                                             │
│   Cost breakdown:                                                           │
│   ├── Position cost:     97¢                                               │
│   ├── Kalshi fee (7%):   -2.2¢  (on 32¢ profit if NO wins)                │
│   ├── Polygon gas:       -0.04¢ (2 transactions)                           │
│   └── Spread slippage:   -1.9¢  (estimated 2%)                             │
│                                                                             │
│   Guaranteed payout:     $1.00                                              │
│   Net profit:            -1.1¢  ❌ NOT PROFITABLE                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ "Fed rate cut in March 2026?"                                               │
│                                                                             │
│   Kalshi (KXFED-RATE-MAR):    YES @ 42¢  /  NO @ 60¢                       │
│   Polymarket:                  YES @ 38¢  /  NO @ 64¢                       │
│                                                                             │
│   Best execution:                                                           │
│   ├── Buy YES on Polymarket @ 38¢                                          │
│   └── Buy NO on Kalshi @ 60¢                                               │
│                                                                             │
│   Cost breakdown:                                                           │
│   ├── Position cost:     98¢                                               │
│   ├── Kalshi fee (7%):   -2.8¢                                             │
│   ├── Polygon gas:       -0.04¢                                            │
│   └── Spread slippage:   -2.0¢                                             │
│                                                                             │
│   Guaranteed payout:     $1.00                                              │
│   Net profit:            -2.8¢  ❌ NOT PROFITABLE                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚠️  No arbitrage opportunities found with net profit > 3%                  │
│                                                                             │
│  Markets are generally efficient. True arbitrage is rare and fleeting.     │
│  Consider using `alpha arb --watch` to monitor for opportunities.          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Honest Disclaimer

```
$ alpha arb --help

IMPORTANT: Arbitrage Limitations
════════════════════════════════
• True arbitrage opportunities are rare and typically last seconds
• Fee structures change; verify current rates before trading
• Liquidity is often insufficient for meaningful position sizes
• Resolution rules may differ between platforms (basis risk)
• This tool shows ESTIMATED profits; actual results may vary
• Past opportunities do not guarantee future availability

This feature is for EDUCATIONAL and RESEARCH purposes.
Not financial advice. Do your own due diligence.
```

---

## 8. Error Handling & Resilience

### Retry Logic with Exponential Backoff

```python
# src/alpha_cli/utils/retry.py
import asyncio
import random
from functools import wraps
from typing import TypeVar, Callable, Awaitable
import httpx

T = TypeVar('T')

class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True

    # Retryable status codes
    retryable_status_codes: set[int] = {408, 429, 500, 502, 503, 504}

def with_retry(config: RetryConfig = RetryConfig()):
    """Decorator for async functions that should be retried on failure."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code not in config.retryable_status_codes:
                        raise  # Non-retryable error
                    last_exception = e

                except (httpx.ConnectError, httpx.ReadTimeout) as e:
                    last_exception = e

                # Calculate delay with exponential backoff
                if attempt < config.max_attempts:
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        delay = delay * (0.5 + random.random())

                    await asyncio.sleep(delay)

            # All attempts exhausted
            raise last_exception

        return wrapper
    return decorator

# Usage
@with_retry(RetryConfig(max_attempts=3))
async def fetch_congress_trades() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
        )
        response.raise_for_status()
        return response.json()
```

### Circuit Breaker Pattern

```python
# src/alpha_cli/utils/circuit_breaker.py
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Awaitable, TypeVar

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    - CLOSED: Requests pass through normally
    - OPEN: Requests fail immediately (service is down)
    - HALF_OPEN: Allow one request to test recovery
    """
    name: str
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: float = 30.0      # Seconds before trying again
    success_threshold: int = 2          # Successes to close from half-open

    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: datetime | None = field(default=None)

    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitOpenError(Exception):
    pass

# Usage
kalshi_circuit = CircuitBreaker(name="kalshi", failure_threshold=5, recovery_timeout=60)
congress_circuit = CircuitBreaker(name="congress", failure_threshold=3, recovery_timeout=30)

async def fetch_kalshi_markets():
    return await kalshi_circuit.call(_fetch_kalshi_markets_impl)
```

### Graceful Degradation with Stale Data

```python
# src/alpha_cli/utils/cache.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Awaitable

T = TypeVar('T')

@dataclass
class CachedValue(Generic[T]):
    data: T
    fetched_at: datetime
    is_stale: bool = False

class StaleCacheStrategy:
    """
    Cache strategy that serves stale data when fresh fetch fails.

    - On success: Update cache, return fresh data
    - On failure: Return stale cached data with warning
    - On failure + no cache: Raise error
    """

    def __init__(self, cache_dir: Path = Path.home() / ".alpha" / "cache"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_or_fetch(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[T]],
        ttl: timedelta = timedelta(minutes=15),
        stale_ttl: timedelta = timedelta(hours=24)
    ) -> CachedValue[T]:
        """
        Get cached data or fetch fresh.
        Falls back to stale data if fetch fails.
        """
        cache_path = self.cache_dir / f"{key}.json"

        # Check cache
        cached = self._read_cache(cache_path)
        is_fresh = cached and (datetime.now() - cached.fetched_at) < ttl

        if is_fresh:
            return cached

        # Try to fetch fresh data
        try:
            fresh_data = await fetcher()
            fresh_value = CachedValue(
                data=fresh_data,
                fetched_at=datetime.now(),
                is_stale=False
            )
            self._write_cache(cache_path, fresh_value)
            return fresh_value

        except Exception as e:
            # Fetch failed - can we serve stale?
            if cached and (datetime.now() - cached.fetched_at) < stale_ttl:
                cached.is_stale = True
                return cached

            # No usable cache
            raise FetchError(f"Failed to fetch {key} and no cached data available") from e

    def _read_cache(self, path: Path) -> CachedValue | None:
        if not path.exists():
            return None
        try:
            with open(path) as f:
                raw = json.load(f)
            return CachedValue(
                data=raw["data"],
                fetched_at=datetime.fromisoformat(raw["fetched_at"]),
                is_stale=False
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def _write_cache(self, path: Path, value: CachedValue):
        with open(path, 'w') as f:
            json.dump({
                "data": value.data,
                "fetched_at": value.fetched_at.isoformat()
            }, f)

class FetchError(Exception):
    pass

# Usage in CLI
cache = StaleCacheStrategy()

async def get_congress_trades():
    result = await cache.get_or_fetch(
        key="congress_trades",
        fetcher=fetch_congress_trades_from_api,
        ttl=timedelta(hours=1),
        stale_ttl=timedelta(hours=24)
    )

    if result.is_stale:
        console.print(f"[yellow]⚠️  Using cached data from {result.fetched_at:%Y-%m-%d %H:%M}[/yellow]")

    return result.data
```

### Extended Error Codes

```python
# src/alpha_cli/errors.py
from enum import Enum
from dataclasses import dataclass

class ErrorCode(Enum):
    # Authentication errors (4xx)
    INVALID_API_KEY = "E401_INVALID_KEY"
    EXPIRED_API_KEY = "E401_EXPIRED_KEY"
    PREMIUM_REQUIRED = "E403_PREMIUM_REQUIRED"
    RATE_LIMITED = "E429_RATE_LIMITED"

    # Data source errors (5xx)
    KALSHI_UNAVAILABLE = "E503_KALSHI"
    POLYMARKET_UNAVAILABLE = "E503_POLYMARKET"
    CONGRESS_DATA_UNAVAILABLE = "E503_CONGRESS"
    SEC_UNAVAILABLE = "E503_SEC"

    # Client errors
    INVALID_TICKER = "E400_INVALID_TICKER"
    INVALID_MARKET = "E400_INVALID_MARKET"
    INVALID_DATE_RANGE = "E400_INVALID_DATES"

    # Internal errors
    MATCHING_FAILED = "E500_MATCHING"
    CACHE_CORRUPTED = "E500_CACHE"

@dataclass
class AlphaError(Exception):
    code: ErrorCode
    message: str
    details: dict | None = None
    retry_after: int | None = None  # Seconds until retry (for rate limits)

    def __str__(self):
        return f"[{self.code.value}] {self.message}"

# User-friendly error messages
ERROR_MESSAGES = {
    ErrorCode.INVALID_API_KEY:
        "Invalid API key. Run `alpha login` to authenticate.",
    ErrorCode.EXPIRED_API_KEY:
        "Your API key has expired. Run `alpha login` to get a new one.",
    ErrorCode.PREMIUM_REQUIRED:
        "This feature requires a premium subscription. Run `alpha upgrade`.",
    ErrorCode.RATE_LIMITED:
        "Rate limit exceeded. Please wait {retry_after} seconds.",
    ErrorCode.KALSHI_UNAVAILABLE:
        "Kalshi API is currently unavailable. Try again later or use cached data.",
    ErrorCode.CONGRESS_DATA_UNAVAILABLE:
        "Congressional trading data is temporarily unavailable.",
}
```

---

## 9. Reduced MVP Scope

### v1.0 Scope (Too Ambitious)

```
Week 1-4:   CLI skeleton + kalshi + congress + auth + stripe + alpha scan
Week 5-8:   alpha arb + alpha events + alpha insider
Week 9-12:  alpha lobbying + alpha contracts + alpha patterns
Week 13-16: alpha alerts + alpha calibrate + polish + launch
```

**Problem**: 9 premium features in 16 weeks = 1.7 weeks per feature. Not enough time for quality.

### v2.0 Scope (Focused)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MVP FEATURE SET                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FREE TIER                           PREMIUM ($20/month)                    │
│  ═════════                           ═══════════════════                    │
│                                                                             │
│  ✓ alpha kalshi markets              ✓ Everything in Free                  │
│  ✓ alpha kalshi market <TICKER>      ✓ alpha scan                          │
│  ✓ alpha kalshi orderbook <TICKER>   ✓ alpha scan --json (for AI agents)   │
│  ✓ alpha kalshi find <QUERY>                                                │
│  ✓ alpha congress trades                                                    │
│  ✓ alpha congress member <NAME>      FUTURE (v1.1+)                        │
│  ✓ alpha congress ticker <TICKER>    ─────────────────                     │
│  ✓ JSON/CSV output                   • alpha arb                           │
│  ✓ Unlimited usage                   • alpha insider                       │
│                                      • alpha events                         │
│                                      • alpha alerts                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rationale for Single Premium Feature

1. **`alpha scan` is the killer feature** — It's the unique value prop (cross-reference congress ↔ markets)
2. **Ship faster, learn faster** — Get to market in 6 weeks, not 16
3. **Validate before expanding** — See if users actually pay for cross-referencing
4. **One thing done well** — Better than nine things done poorly

### Revised Development Roadmap

```
PHASE 1: FOUNDATION (Weeks 1-2)
════════════════════════════════
├── Day 1-3: Project setup
│   ├── Python project with uv, pyproject.toml
│   ├── CLI skeleton with Typer
│   ├── Rich output formatting
│   └── Basic --json and --csv output
│
├── Day 4-7: Kalshi integration
│   ├── Kalshi API client (with JWT refresh)
│   ├── alpha kalshi markets
│   ├── alpha kalshi market <TICKER>
│   ├── alpha kalshi orderbook <TICKER>
│   └── alpha kalshi find <QUERY>
│
├── Day 8-10: Congress integration
│   ├── House/Senate Stock Watcher client
│   ├── Party affiliation data merge
│   ├── alpha congress trades
│   ├── alpha congress member <NAME>
│   └── alpha congress ticker <TICKER>
│
└── Day 11-14: Testing & polish
    ├── Unit tests for all clients
    ├── Integration tests with mocked APIs
    ├── Error handling (retry, circuit breaker)
    └── Local caching with stale fallback

PHASE 2: AUTHENTICATION (Weeks 3-4)
═══════════════════════════════════
├── Day 15-17: Backend skeleton
│   ├── Cloudflare Workers + Hono setup
│   ├── D1 database schema
│   ├── KV namespace for caching
│   └── Basic health check endpoint
│
├── Day 18-21: Auth system
│   ├── User signup (email magic link or OAuth)
│   ├── API key generation
│   ├── /auth/validate endpoint
│   └── CLI: alpha login / alpha logout
│
├── Day 22-25: Stripe integration
│   ├── Stripe Checkout session creation
│   ├── Webhook handler for subscription events
│   ├── Subscription status in D1
│   └── CLI: alpha upgrade / alpha status
│
└── Day 26-28: Credential storage
    ├── Python keyring integration
    ├── Environment variable fallback
    └── Secure config file (non-sensitive only)

PHASE 3: CORE PREMIUM FEATURE (Weeks 5-6)
═════════════════════════════════════════
├── Day 29-32: Matching system
│   ├── Curated ticker → market mapping table
│   ├── Embedding infrastructure (OpenAI or Vectorize)
│   ├── Semantic search for Tier 2 matching
│   └── LLM validation for Tier 3 (Claude Haiku)
│
├── Day 33-36: alpha scan implementation
│   ├── Cross-reference congress trades ↔ Kalshi markets
│   ├── Beautiful Rich table output
│   ├── JSON output for AI agents
│   └── Filtering: --days, --ticker, --party
│
├── Day 37-40: Testing & validation
│   ├── 100-case test set for matching accuracy
│   ├── Measure precision/recall
│   ├── Performance optimization (caching)
│   └── Cost tracking (embedding + LLM calls)
│
└── Day 41-42: Polish
    ├── Error messages
    ├── Help text
    └── Loading states

PHASE 4: LAUNCH (Week 7-8)
══════════════════════════
├── Day 43-45: Documentation
│   ├── README with quickstart
│   ├── --help for all commands
│   └── Website landing page
│
├── Day 46-48: Distribution
│   ├── PyPI package
│   ├── Homebrew formula
│   └── GitHub releases
│
├── Day 49-50: Launch prep
│   ├── HN post draft
│   ├── Twitter thread
│   ├── Demo video
│   └── Discord server setup
│
└── Day 51-56: Launch & iterate
    ├── HN, Reddit, Twitter launch
    ├── Monitor errors (Sentry)
    ├── Respond to feedback
    └── Hotfixes as needed
```

### Post-MVP Roadmap

```
v1.1 (Month 3): Arbitrage
─────────────────────────
• Polymarket CLOB integration
• alpha arb with accurate fee modeling
• Cross-platform market matching

v1.2 (Month 4): Insider Data
────────────────────────────
• SEC Form 4 integration
• alpha insider <TICKER>
• Congress vs insider pattern detection

v1.3 (Month 5): Events
──────────────────────
• Economic calendar integration (FRED)
• alpha events --days 7
• Market linking to economic events

v1.4 (Month 6): Alerts
──────────────────────
• Webhook alerts infrastructure
• alpha alerts add / list / remove
• Cron-based monitoring

v2.0 (Month 9): Platform
────────────────────────
• API tier for developers
• Team plans
• Mobile companion app
```

---

## 10. Open Source Strategy

### Component Licensing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OPEN SOURCE STRATEGY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  COMPONENT                    LICENSE         VISIBILITY                    │
│  ═════════                    ═══════         ══════════                    │
│                                                                             │
│  alpha-cli (full repo)        MIT             Public on GitHub              │
│  ├── Free commands            MIT             ✓ Open source                 │
│  ├── Premium command stubs    MIT             ✓ Open source                 │
│  ├── API clients              MIT             ✓ Open source                 │
│  └── Utilities                MIT             ✓ Open source                 │
│                                                                             │
│  alpha-backend                Proprietary     Private repo                  │
│  ├── Auth system              Proprietary     ✗ Closed source               │
│  ├── Matching algorithm       Proprietary     ✗ Closed source               │
│  ├── Cross-reference engine   Proprietary     ✗ Closed source               │
│  └── Database schema          Proprietary     ✗ Closed source               │
│                                                                             │
│  Documentation                CC-BY-4.0       Public                        │
│  ├── User guides              CC-BY-4.0       ✓ Open                        │
│  ├── API reference            CC-BY-4.0       ✓ Open                        │
│  └── Blog posts               CC-BY-4.0       ✓ Open                        │
│                                                                             │
│  Curated mappings             Proprietary     Private                       │
│  └── Ticker → Market table    Proprietary     ✗ Closed (competitive moat)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why This Split?

**Open (MIT):**
- CLI code — builds trust, allows contributions, enables forks
- API clients — useful to community even without our backend
- Utilities — generic code that others can use

**Closed (Proprietary):**
- Matching algorithm — core competitive advantage
- Curated mappings — labor-intensive to create, easy to copy
- Backend logic — contains business logic and user data handling

### Contributor License Agreement (CLA)

For open source components:

```markdown
# Contributor License Agreement

By contributing to alpha-cli, you agree that:

1. You have the right to submit the contribution
2. Your contribution is licensed under MIT
3. We may use your contribution in both open source and commercial products
4. We are not obligated to use your contribution
```

### Community Guidelines

```markdown
# Contributing to Alpha CLI

## What We Accept
- Bug fixes for CLI functionality
- New free commands (subject to approval)
- Documentation improvements
- Performance optimizations
- Test coverage improvements

## What We Don't Accept
- Changes to premium feature logic
- Attempts to bypass premium checks
- Features that compete with premium offerings

## How to Contribute
1. Open an issue first to discuss
2. Fork the repo
3. Create a branch
4. Submit a PR with tests
5. Sign the CLA
```

---

## 11. Revised Development Roadmap

See Section 9 for the week-by-week breakdown. Summary:

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Foundation | 2 weeks | Kalshi + Congress commands, CLI skeleton |
| Authentication | 2 weeks | Backend, auth, Stripe, credentials |
| Core Premium | 2 weeks | `alpha scan` with matching system |
| Launch | 2 weeks | Docs, distribution, marketing |
| **Total** | **8 weeks** | **Working MVP** |

---

## 12. API Specification (OpenAPI)

```yaml
openapi: 3.0.3
info:
  title: Alpha CLI Backend API
  version: 1.0.0
  description: Backend API for Alpha CLI premium features

servers:
  - url: https://api.alpha.dev/v1
    description: Production

security:
  - ApiKeyAuth: []

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: "Format: alpha_live_xxx or alpha_test_xxx"

  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          example: "E403_PREMIUM_REQUIRED"
        message:
          type: string
          example: "This feature requires a premium subscription."
        retry_after:
          type: integer
          description: Seconds until retry (for rate limits)

    AuthStatus:
      type: object
      properties:
        status:
          type: string
          enum: [anonymous, free, premium, expired, invalid]
        email:
          type: string
          format: email
        subscription_end:
          type: string
          format: date-time

    CongressTrade:
      type: object
      properties:
        member:
          type: string
        party:
          type: string
          enum: [R, D, I]
        state:
          type: string
        ticker:
          type: string
        type:
          type: string
          enum: [purchase, sale, exchange]
        amount_range:
          type: string
        trade_date:
          type: string
          format: date
        disclosure_date:
          type: string
          format: date

    RelatedMarket:
      type: object
      properties:
        platform:
          type: string
          enum: [kalshi, polymarket]
        ticker:
          type: string
        title:
          type: string
        yes_price:
          type: number
        no_price:
          type: number
        volume:
          type: integer
        close_date:
          type: string
          format: date
        relevance_score:
          type: number
          minimum: 0
          maximum: 1

    CrossReference:
      type: object
      properties:
        congress_trade:
          $ref: '#/components/schemas/CongressTrade'
        related_markets:
          type: array
          items:
            $ref: '#/components/schemas/RelatedMarket'

    ScanResponse:
      type: object
      properties:
        cross_references:
          type: array
          items:
            $ref: '#/components/schemas/CrossReference'
        generated_at:
          type: string
          format: date-time
        cache_ttl:
          type: integer
          description: Seconds until data is stale
        is_stale:
          type: boolean
          description: True if serving cached data due to fetch failure

paths:
  /auth/validate:
    post:
      summary: Validate API key and get subscription status
      tags: [Auth]
      security:
        - ApiKeyAuth: []
      responses:
        '200':
          description: Valid API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthStatus'
        '401':
          description: Invalid or expired API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /scan:
    post:
      summary: Cross-reference congress trades with prediction markets
      tags: [Premium]
      security:
        - ApiKeyAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                days:
                  type: integer
                  default: 30
                  minimum: 1
                  maximum: 365
                ticker:
                  type: string
                  description: Filter by stock ticker
                party:
                  type: string
                  enum: [R, D]
                  description: Filter by party
      responses:
        '200':
          description: Cross-reference results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScanResponse'
        '403':
          description: Premium subscription required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '429':
          description: Rate limited
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

---

## Summary of Changes

### Critical Fixes
1. ✅ Designed ticker-to-market matching system (hybrid embeddings + LLM)
2. ✅ Replaced Capitol Trades scraping with House/Senate Stock Watcher APIs
3. ✅ Updated lobbying source to Senate LDA API (OpenSecrets discontinued)
4. ✅ Designed complete authentication flow with secure credential storage
5. ✅ Redesigned alert architecture with Cron Triggers + Queues

### Scope Reduction
6. ✅ Cut MVP from 9 premium features to 1 (`alpha scan`)
7. ✅ Reduced timeline from 16 weeks to 8 weeks

### Improved Accuracy
8. ✅ Documented Polymarket CLOB complexity
9. ✅ Added accurate arbitrage fee modeling
10. ✅ Added error handling patterns (retry, circuit breaker, stale cache)

### Clarifications
11. ✅ Defined explicit open source strategy (MIT for CLI, proprietary for backend)
12. ✅ Added OpenAPI specification

---

## References

### Data Sources
- [House Stock Watcher API](https://housestockwatcher.com/api)
- [Senate Stock Watcher API](https://senatestockwatcher.com/api)
- [Kalshi API Docs](https://docs.kalshi.com/welcome)
- [Polymarket CLOB Docs](https://docs.polymarket.com/)
- [SEC EDGAR Access](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- [Senate LDA API](https://lda.senate.gov/api/redoc/v1/)
- [USAspending API](https://api.usaspending.gov/)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)

### Infrastructure
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Cloudflare Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/)
- [Cloudflare Queues](https://developers.cloudflare.com/queues/)
- [Hono Framework](https://hono.dev/)
- [Python Keyring](https://keyring.readthedocs.io/)

### Frameworks
- [Typer CLI](https://typer.tiangolo.com/)
- [Rich Console](https://rich.readthedocs.io/)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/build-subscriptions)

---

## Implementation Status

### Completed (Phase 1 - Foundation)

| Component | Status | Location |
|-----------|--------|----------|
| Python project structure | ✅ Complete | `pyproject.toml`, `src/alpha_cli/` |
| CLI skeleton (Typer + Rich) | ✅ Complete | `src/alpha_cli/main.py` |
| Kalshi API client | ✅ Complete | `src/alpha_cli/clients/kalshi.py` |
| Congress data client | ✅ Complete | `src/alpha_cli/clients/congress.py` |
| Secure credential storage | ✅ Complete | `src/alpha_cli/credentials.py` |
| Retry with backoff | ✅ Complete | `src/alpha_cli/utils/retry.py` |
| Circuit breaker | ✅ Complete | `src/alpha_cli/utils/circuit_breaker.py` |
| Stale cache strategy | ✅ Complete | `src/alpha_cli/utils/cache.py` |

### Completed (Phase 2 - Core Features)

| Component | Status | Location |
|-----------|--------|----------|
| Kalshi commands (markets, orderbook, find) | ✅ Complete | `src/alpha_cli/commands/kalshi.py` |
| Congress commands (trades, member, ticker, top) | ✅ Complete | `src/alpha_cli/commands/congress.py` |
| Config commands | ✅ Complete | `src/alpha_cli/commands/config.py` |
| Tier 1 matching (curated mappings) | ✅ Complete | `src/alpha_cli/services/matching.py` |
| Scan command | ✅ Complete | `src/alpha_cli/commands/scan.py` |
| Login/logout/status | ✅ Complete | `src/alpha_cli/main.py` |

### Completed (Phase 3 - Backend)

| Component | Status | Location |
|-----------|--------|----------|
| Cloudflare Workers setup | ✅ Complete | `alpha-backend/` |
| D1 database schema | ✅ Complete | `alpha-backend/src/db/schema.sql` |
| Auth middleware | ✅ Complete | `alpha-backend/src/middleware/auth.ts` |
| Rate limiting | ✅ Complete | `alpha-backend/src/middleware/rateLimit.ts` |
| Stripe webhooks | ✅ Complete | `alpha-backend/src/handlers/webhooks.ts` |
| Scan endpoint | ✅ Complete | `alpha-backend/src/handlers/scan.ts` |

### Requires Operator Setup

See `operator-todo.md` for items requiring external accounts:
- Cloudflare account + D1 database
- Stripe account + webhook configuration
- Domain configuration
- API keys for enhanced features (OpenAI/Anthropic)

### Future Features (Post-MVP)

| Feature | Spec Section | Priority |
|---------|--------------|----------|
| Tier 2 matching (embeddings) | Section 1 | High |
| Tier 3 matching (LLM) | Section 1 | High |
| Polymarket integration | Section 6 | Medium |
| Arbitrage detection | Section 7 | Medium |
| Alerts system | Section 5 | Low |
| SEC Form 4 integration | Section 2 | Low |

---

*Document version: 2.0*
*Last updated: December 29, 2025*
*Changelog: Major revision addressing 10 critical issues from v1.0*
*Implementation status: MVP complete, requires operator setup for deployment*
