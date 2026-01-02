# Alpha CLI

Cross-reference congressional stock trades with prediction markets.

## Features

**Free Features:**
- View Kalshi prediction markets, order books, and search
- View congressional stock trades from House and Senate
- Filter by ticker, party, member
- Export to JSON/CSV

**Premium Features ($20/month):**
- Cross-reference scan - find prediction markets related to congressional trades
- AI-powered market matching

## Installation

```bash
pip install alpha-cli
```

## Quick Start

```bash
# View recent congressional trades
alpha congress trades

# Search for Kalshi markets
alpha kalshi find "bitcoin"

# Cross-reference trades with markets
alpha scan
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```

## License

MIT License - see LICENSE for details.

The CLI is open source. Premium features require a backend subscription.
