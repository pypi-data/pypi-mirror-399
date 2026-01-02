# Alpha CLI

A CLI tool for cross-referencing congressional stock trades with prediction markets.

## Project Overview

Alpha CLI helps traders identify potential alpha by connecting two data sources:
1. **Congressional trading data** - What stocks are members of Congress buying/selling?
2. **Prediction markets** - What markets on Kalshi might be affected?

## Quick Start

```bash
# Install dependencies
pip install -e .

# View congressional trades
alpha congress trades

# View Kalshi markets
alpha kalshi markets

# Cross-reference (the killer feature)
alpha scan
```

## Documentation

Detailed documentation is in the `docs/` directory:

| Document | Description | When to Read |
|----------|-------------|--------------|
| [getting-started.md](docs/getting-started.md) | Installation and basic usage | New to the project |
| [architecture.md](docs/architecture.md) | System design and component overview | Understanding the codebase |
| [api-reference.md](docs/api-reference.md) | Backend API documentation | Working on backend/integration |

## Code Structure

```
src/alpha_cli/          # Python CLI application
├── main.py             # CLI entry point
├── clients/            # External API clients (Kalshi, Congress)
├── services/           # Business logic (matching, scanning)
├── commands/           # CLI command implementations
└── utils/              # Utilities (retry, cache, circuit breaker)

alpha-backend/          # Cloudflare Workers backend
├── src/
│   ├── index.ts        # Main router
│   ├── handlers/       # API endpoint handlers
│   ├── middleware/     # Auth, rate limiting
│   └── db/             # Database schema
└── wrangler.toml       # Cloudflare config

docs/                   # Documentation
tests/                  # Test suite
```

## Key Concepts

### Ticker-to-Market Matching

The core feature is matching stock tickers (e.g., `NVDA`) to relevant prediction markets (e.g., `KXNVDA-Q4-EARNINGS`). See `src/alpha_cli/services/matching.py`.

Three-tier system:
- **Tier 1**: Curated lookup table (all users)
- **Tier 2**: Semantic embeddings (premium)
- **Tier 3**: LLM validation (premium)

### Data Sources

- **Congress trades**: House/Senate Stock Watcher APIs (free, daily updates)
- **Kalshi markets**: Official Kalshi API (free tier available)
- See spec for additional sources: SEC EDGAR, Senate LDA, etc.

### Authentication

- Credentials stored in OS keyring (not plaintext files)
- Environment variables for CI: `ALPHA_API_KEY`, `KALSHI_API_KEY`
- Premium features require authentication

## Development

```bash
# Run tests
pytest tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Spec Reference

The full specification is in `alpha-cli-spec-v2.md`. Key sections:

- Section 1: Ticker-to-market matching algorithm
- Section 2: Data source APIs and rate limits
- Section 3: Authentication flow
- Section 5: Backend architecture
- Section 9: MVP scope (reduced to 1 premium feature)

## What's Implemented

- [x] CLI structure with Typer/Rich
- [x] Kalshi client (markets, orderbook, search)
- [x] Congress client (trades, member, ticker)
- [x] Credential storage (keyring)
- [x] Error handling (retry, circuit breaker, cache)
- [x] Tier 1 matching (curated mappings)
- [x] Scan command (cross-reference)
- [x] Backend skeleton (Cloudflare Workers)
- [x] Database schema (D1)
- [x] Auth middleware

## What Needs Operator Setup

See `operator-todo.md` for items requiring external account setup.
