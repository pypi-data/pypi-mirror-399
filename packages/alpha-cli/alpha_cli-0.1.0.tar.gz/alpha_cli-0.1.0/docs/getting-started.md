# Getting Started with Alpha CLI

Alpha CLI is a command-line tool for cross-referencing congressional stock trades with prediction markets.

## Installation

### Using pip

```bash
pip install alpha-cli
```

### Using uv (recommended)

```bash
uv pip install alpha-cli
```

### From source

```bash
git clone https://github.com/alpha-cli/alpha-cli.git
cd alpha-cli
pip install -e .
```

## Quick Start

### View Kalshi Markets

```bash
# List open markets
alpha kalshi markets

# Get details for a specific market
alpha kalshi market KXBTC-150K

# View order book
alpha kalshi orderbook KXBTC-150K

# Search for markets
alpha kalshi find "fed rate"
```

### View Congressional Trades

```bash
# Recent trades (last 30 days)
alpha congress trades

# Filter by ticker
alpha congress trades --ticker NVDA

# Filter by party
alpha congress trades --party D

# Get trades for a specific member
alpha congress member "Nancy Pelosi"

# Get trades for a specific ticker
alpha congress ticker NVDA

# Most traded tickers
alpha congress top
```

### Cross-Reference Scan (Premium)

```bash
# Scan for congressional trades with related markets
alpha scan

# Filter options
alpha scan --days 30 --ticker NVDA --party R

# Output as JSON (for AI agents)
alpha scan --format json
```

## Output Formats

All commands support multiple output formats:

```bash
# Table (default)
alpha congress trades

# JSON
alpha congress trades --format json

# CSV
alpha congress trades --format csv
```

## Authentication

For premium features, you need to authenticate:

```bash
# Login (opens browser)
alpha login

# Check status
alpha status

# Logout
alpha logout
```

## Configuration

### Configure Kalshi credentials

```bash
alpha config kalshi
```

### View current config

```bash
alpha config show
```

### Clear credentials

```bash
alpha config clear
```

## Environment Variables

For CI/automation, use environment variables:

```bash
export ALPHA_API_KEY="alpha_live_xxx"
export KALSHI_API_KEY="your_kalshi_key"
export KALSHI_PRIVATE_KEY_PATH="/path/to/key.pem"
```

## Examples

### Find what Congress is trading

```bash
# See top traded tickers
alpha congress top --days 7

# Look at recent trades
alpha congress trades --days 7 --limit 20
```

### Research a specific ticker

```bash
# Who in Congress is trading NVDA?
alpha congress ticker NVDA

# Are there related prediction markets?
alpha scan --ticker NVDA
```

### Monitor a member's activity

```bash
# Get all trades for a member
alpha congress member "Tommy Tuberville" --days 365
```

### Export for analysis

```bash
# Export to CSV for spreadsheets
alpha congress trades --days 90 --format csv > trades.csv

# Export to JSON for processing
alpha congress trades --format json > trades.json
```

## Free vs Premium Features

### Free Features

- View Kalshi markets, details, and order books
- Search Kalshi markets
- View congressional trades
- Filter by ticker, party, member
- Export to JSON/CSV
- No account required

### Premium Features ($20/month)

- Cross-reference scan (`alpha scan`)
- AI-powered market matching
- Higher accuracy relevance scores
- Priority support

## Troubleshooting

### "Command not found"

Make sure alpha-cli is installed and in your PATH:

```bash
pip install alpha-cli
which alpha
```

### API errors

If you see errors fetching data, check:

1. Internet connection
2. API status at status.alpha.dev
3. Try again (transient errors are retried automatically)

### Rate limiting

If you hit rate limits:

```bash
# Wait for the retry-after period
# Or authenticate for higher limits
alpha login
```

## Getting Help

```bash
# General help
alpha --help

# Command-specific help
alpha kalshi --help
alpha congress trades --help
```
