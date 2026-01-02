# Alpha CLI Architecture

This document describes the technical architecture of Alpha CLI, a tool for cross-referencing congressional trades with prediction markets.

## Overview

Alpha CLI consists of two main components:

1. **CLI Application** (Python) - The open-source command-line interface
2. **Backend API** (Cloudflare Workers) - The premium features backend

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ALPHA CLI ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐      ┌─────────────────────┐                  │
│  │    CLI (Python)     │      │  Backend (Workers)   │                  │
│  │                     │      │                      │                  │
│  │  • alpha kalshi     │      │  • /v1/auth         │                  │
│  │  • alpha congress   │◄────►│  • /v1/scan         │                  │
│  │  • alpha scan       │      │  • /webhooks        │                  │
│  │  • alpha config     │      │                      │                  │
│  └─────────┬───────────┘      └──────────┬──────────┘                  │
│            │                             │                              │
│            ▼                             ▼                              │
│  ┌─────────────────────┐      ┌─────────────────────┐                  │
│  │   External APIs     │      │   Infrastructure    │                  │
│  │                     │      │                      │                  │
│  │  • Kalshi API       │      │  • Cloudflare D1    │                  │
│  │  • Stock Watcher    │      │  • Cloudflare KV    │                  │
│  │  • (Polymarket)     │      │  • Cloudflare Queue │                  │
│  │  • (SEC EDGAR)      │      │  • Stripe           │                  │
│  └─────────────────────┘      └─────────────────────┘                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## CLI Application

### Directory Structure

```
src/alpha_cli/
├── __init__.py           # Version info
├── main.py               # CLI entry point
├── types.py              # Shared type definitions
├── credentials.py        # Secure credential storage
├── output.py             # Output formatting (table, JSON, CSV)
├── clients/              # External API clients
│   ├── kalshi.py         # Kalshi prediction markets
│   ├── congress.py       # Congressional trading data
│   └── polymarket.py     # Polymarket (future)
├── services/             # Business logic
│   ├── matching.py       # Ticker-to-market matching
│   └── scan.py           # Cross-reference scanning
├── commands/             # CLI commands
│   ├── kalshi.py         # Kalshi subcommands
│   ├── congress.py       # Congress subcommands
│   ├── config.py         # Config subcommands
│   └── scan.py           # Scan command
└── utils/                # Utilities
    ├── retry.py          # Retry with exponential backoff
    ├── circuit_breaker.py # Circuit breaker pattern
    └── cache.py          # Stale cache fallback
```

### Key Components

#### API Clients

- **KalshiClient**: Interacts with Kalshi's prediction market API
  - JWT authentication with auto-refresh
  - Market listing, details, and order book
  - Circuit breaker for resilience

- **CongressClient**: Fetches congressional trading data
  - House and Senate Stock Watcher APIs
  - Party affiliation lookup
  - Filtering by ticker, party, member

#### Credential Storage

Credentials are stored securely using the OS keyring:
- macOS: Keychain
- Windows: Credential Locker
- Linux: Secret Service (GNOME Keyring, KWallet)

Environment variables take precedence for CI/automation:
- `ALPHA_API_KEY`
- `KALSHI_API_KEY`
- `KALSHI_PRIVATE_KEY_PATH`

#### Error Handling

Three-layer resilience:

1. **Retry with Backoff**: Automatic retry for transient failures
2. **Circuit Breaker**: Fail fast when services are down
3. **Stale Cache**: Serve cached data when fetch fails

## Backend API

### Cloudflare Workers Stack

- **Runtime**: Cloudflare Workers (JavaScript/TypeScript)
- **Framework**: Hono (lightweight web framework)
- **Database**: Cloudflare D1 (SQLite)
- **Cache**: Cloudflare KV
- **Queue**: Cloudflare Queues (for webhooks)
- **Payments**: Stripe

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | None | Health check |
| `/v1/auth/validate` | POST | API Key | Validate key, get status |
| `/v1/scan` | POST | API Key | Cross-reference scan |
| `/webhooks/stripe` | POST | Signature | Stripe webhooks |

### Database Schema

```sql
-- Users and authentication
users (id, email, stripe_customer_id)
api_keys (id, user_id, key_hash, environment)
subscriptions (id, user_id, status, period_end)

-- Matching
ticker_market_mappings (ticker, market_pattern, relevance_type)
match_cache (ticker, market_ticker, is_relevant, confidence)

-- Future: Alerts
alerts (id, user_id, alert_type, config, webhook_url)
```

## Ticker-to-Market Matching

The core feature: matching stock tickers to relevant prediction markets.

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TICKER-TO-MARKET MATCHING PIPELINE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1: Exact Matching (All Users)                                     │
│  ───────────────────────────────────                                    │
│  • Curated lookup table of ticker → market patterns                     │
│  • Covers top 50+ congressional tickers                                 │
│  • Fast, high precision                                                 │
│                                                                         │
│  TIER 2: Semantic Embedding Search (Premium)                            │
│  ───────────────────────────────────────────                            │
│  • Vector embeddings of market titles/descriptions                      │
│  • Similarity search for relevant markets                               │
│  • Catches matches not in curated list                                  │
│                                                                         │
│  TIER 3: LLM Validation (Premium)                                       │
│  ───────────────────────────────────                                    │
│  • Claude Haiku validates candidate matches                             │
│  • Filters false positives                                              │
│  • Returns confidence scores                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Example Mapping

```python
# NVDA → Related Kalshi markets
TICKER_MARKET_MAPPINGS = {
    "NVDA": [
        {"pattern": "KXNVDA%", "type": "direct"},    # Direct NVDA markets
        {"pattern": "KXNVIDIA%", "type": "direct"},  # NVIDIA markets
        {"pattern": "KXAICHIP%", "type": "sector"},  # AI chip sector
    ],
}
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. User runs `alpha login`                                             │
│  2. CLI opens browser to auth.alpha.dev                                 │
│  3. User signs in (email magic link or OAuth)                           │
│  4. Backend generates API key                                           │
│  5. CLI receives key and stores in keyring                              │
│  6. API key sent with all premium requests                              │
│                                                                         │
│  Key Format: alpha_{env}_{random}                                       │
│  Example: alpha_live_x7Kj9mNpQrStUvWxYz1234...                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Subscription Management

Stripe handles all billing:

1. User runs `alpha upgrade`
2. Opens Stripe Checkout session
3. User completes payment
4. Stripe webhook updates subscription status
5. Next API call sees premium status

## Future Features

- **Arbitrage Detection**: Cross-platform price comparison
- **SEC Insider Trading**: Form 4 integration
- **Economic Calendar**: Event-market linking
- **Alerts**: Webhook notifications for triggers
