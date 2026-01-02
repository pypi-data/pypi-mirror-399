"""Ticker-to-market matching system.

This implements the three-tier matching system from the spec:
1. Exact matching via curated lookup table
2. Semantic embedding search (requires API key)
3. LLM validation (requires API key)

For the open-source CLI, only Tier 1 (exact matching) is available.
Premium users get Tier 2 and 3 via the backend API.
"""

from dataclasses import dataclass
from typing import Literal

from alpha_cli.types import KalshiMarket, RelatedMarket


# Curated ticker -> market pattern mappings
# Based on top congressional tickers and known Kalshi markets
TICKER_MARKET_MAPPINGS: dict[str, list[dict]] = {
    # Technology
    "NVDA": [
        {"pattern": "NVDA", "type": "direct", "keywords": ["nvidia", "ai chip", "gpu"]},
        {"pattern": "AICHIP", "type": "sector", "keywords": ["ai", "semiconductor", "chip"]},
    ],
    "AAPL": [
        {"pattern": "AAPL", "type": "direct", "keywords": ["apple", "iphone"]},
        {"pattern": "APPLE", "type": "direct", "keywords": ["apple"]},
    ],
    "MSFT": [
        {"pattern": "MSFT", "type": "direct", "keywords": ["microsoft", "azure", "openai"]},
        {"pattern": "MICROSOFT", "type": "direct", "keywords": ["microsoft"]},
    ],
    "GOOGL": [
        {"pattern": "GOOG", "type": "direct", "keywords": ["google", "alphabet", "search"]},
        {"pattern": "GOOGLE", "type": "direct", "keywords": ["google"]},
        {"pattern": "ALPHABET", "type": "direct", "keywords": ["alphabet"]},
    ],
    "GOOG": [
        {"pattern": "GOOG", "type": "direct", "keywords": ["google", "alphabet", "search"]},
        {"pattern": "GOOGLE", "type": "direct", "keywords": ["google"]},
    ],
    "META": [
        {"pattern": "META", "type": "direct", "keywords": ["meta", "facebook", "instagram"]},
        {"pattern": "FACEBOOK", "type": "direct", "keywords": ["facebook"]},
    ],
    "AMZN": [
        {"pattern": "AMZN", "type": "direct", "keywords": ["amazon", "aws", "ecommerce"]},
        {"pattern": "AMAZON", "type": "direct", "keywords": ["amazon"]},
    ],
    "TSLA": [
        {"pattern": "TSLA", "type": "direct", "keywords": ["tesla", "elon", "ev"]},
        {"pattern": "TESLA", "type": "direct", "keywords": ["tesla"]},
    ],
    "AMD": [
        {"pattern": "AMD", "type": "direct", "keywords": ["amd", "chip", "semiconductor"]},
    ],
    "INTC": [
        {"pattern": "INTC", "type": "direct", "keywords": ["intel", "chip", "semiconductor"]},
        {"pattern": "INTEL", "type": "direct", "keywords": ["intel"]},
    ],
    # Finance
    "JPM": [
        {"pattern": "JPM", "type": "direct", "keywords": ["jpmorgan", "chase", "bank"]},
        {"pattern": "JPMORGAN", "type": "direct", "keywords": ["jpmorgan"]},
    ],
    "BAC": [
        {"pattern": "BAC", "type": "direct", "keywords": ["bank of america", "bofa"]},
    ],
    "GS": [
        {"pattern": "GOLDMAN", "type": "direct", "keywords": ["goldman", "sachs"]},
    ],
    # Energy
    "XOM": [
        {"pattern": "EXXON", "type": "direct", "keywords": ["exxon", "oil", "energy"]},
        {"pattern": "OIL", "type": "sector", "keywords": ["oil", "crude", "energy"]},
    ],
    "CVX": [
        {"pattern": "CHEVRON", "type": "direct", "keywords": ["chevron", "oil"]},
        {"pattern": "OIL", "type": "sector", "keywords": ["oil", "crude"]},
    ],
    # Defense
    "LMT": [
        {"pattern": "LOCKHEED", "type": "direct", "keywords": ["lockheed", "defense"]},
        {"pattern": "DEFENSE", "type": "sector", "keywords": ["defense", "military"]},
    ],
    "RTX": [
        {"pattern": "RAYTHEON", "type": "direct", "keywords": ["raytheon", "defense"]},
        {"pattern": "DEFENSE", "type": "sector", "keywords": ["defense", "military"]},
    ],
    "BA": [
        {"pattern": "BOEING", "type": "direct", "keywords": ["boeing", "aerospace"]},
    ],
    # Healthcare
    "JNJ": [
        {"pattern": "JOHNSON", "type": "direct", "keywords": ["johnson", "pharma"]},
    ],
    "PFE": [
        {"pattern": "PFIZER", "type": "direct", "keywords": ["pfizer", "vaccine", "pharma"]},
    ],
    "MRNA": [
        {"pattern": "MODERNA", "type": "direct", "keywords": ["moderna", "vaccine", "mrna"]},
    ],
    # Crypto-related
    "COIN": [
        {"pattern": "COINBASE", "type": "direct", "keywords": ["coinbase", "crypto"]},
        {"pattern": "BTC", "type": "sector", "keywords": ["bitcoin", "crypto"]},
        {"pattern": "CRYPTO", "type": "sector", "keywords": ["crypto", "bitcoin"]},
    ],
    "MSTR": [
        {"pattern": "MICROSTRATEGY", "type": "direct", "keywords": ["microstrategy"]},
        {"pattern": "BTC", "type": "sector", "keywords": ["bitcoin"]},
    ],
}

# Company name to ticker mapping for keyword matching
COMPANY_TICKERS: dict[str, str] = {
    "nvidia": "NVDA",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "meta": "META",
    "facebook": "META",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "intel": "INTC",
    "jpmorgan": "JPM",
    "exxon": "XOM",
    "chevron": "CVX",
    "lockheed": "LMT",
    "boeing": "BA",
    "pfizer": "PFE",
    "moderna": "MRNA",
    "coinbase": "COIN",
}


@dataclass
class MatchResult:
    """Result of ticker-to-market matching."""

    ticker: str
    market: KalshiMarket
    relevance_score: float
    relevance_type: Literal["direct", "sector", "macro"]
    match_tier: int  # 1, 2, or 3


class TickerMatcher:
    """
    Matches stock tickers to relevant prediction markets.

    This is the core matching system that powers `alpha scan`.
    The open-source version only supports Tier 1 (exact matching).
    Premium users get Tier 2 (embeddings) and Tier 3 (LLM) via backend.
    """

    def __init__(self) -> None:
        """Initialize the matcher."""
        pass

    def match_tier1(
        self, ticker: str, markets: list[KalshiMarket]
    ) -> list[MatchResult]:
        """
        Tier 1: Exact matching via curated lookup table.

        Fast, high precision. Covers top 50-100 most-traded congressional tickers.

        Args:
            ticker: Stock ticker to match
            markets: List of available markets

        Returns:
            List of matched markets with scores
        """
        ticker_upper = ticker.upper()
        results: list[MatchResult] = []

        # Get patterns for this ticker
        patterns = TICKER_MARKET_MAPPINGS.get(ticker_upper, [])

        if not patterns:
            return results

        for market in markets:
            market_ticker_upper = market.ticker.upper()
            market_title_lower = market.title.lower()

            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                relevance_type = pattern_info["type"]
                keywords = pattern_info.get("keywords", [])

                # Check ticker pattern match
                if pattern in market_ticker_upper:
                    results.append(
                        MatchResult(
                            ticker=ticker_upper,
                            market=market,
                            relevance_score=1.0 if relevance_type == "direct" else 0.7,
                            relevance_type=relevance_type,
                            match_tier=1,
                        )
                    )
                    break  # Don't match same market twice

                # Check keyword match in title
                for keyword in keywords:
                    if keyword.lower() in market_title_lower:
                        results.append(
                            MatchResult(
                                ticker=ticker_upper,
                                market=market,
                                relevance_score=0.8 if relevance_type == "direct" else 0.5,
                                relevance_type=relevance_type,
                                match_tier=1,
                            )
                        )
                        break

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Deduplicate (keep highest score for each market)
        seen_tickers: set[str] = set()
        unique_results: list[MatchResult] = []
        for result in results:
            if result.market.ticker not in seen_tickers:
                seen_tickers.add(result.market.ticker)
                unique_results.append(result)

        return unique_results

    def match(
        self,
        ticker: str,
        markets: list[KalshiMarket],
        include_tier2: bool = False,
        include_tier3: bool = False,
    ) -> list[MatchResult]:
        """
        Match a ticker to relevant markets.

        For the open-source CLI, only Tier 1 is available.
        Tier 2 and 3 require premium backend access.

        Args:
            ticker: Stock ticker to match
            markets: List of available markets
            include_tier2: Include semantic embedding search (premium)
            include_tier3: Include LLM validation (premium)

        Returns:
            List of matched markets sorted by relevance
        """
        # Start with Tier 1
        results = self.match_tier1(ticker, markets)

        # Tier 2 and 3 would be called here for premium users
        # These would make API calls to the backend

        return results

    def to_related_market(self, result: MatchResult) -> RelatedMarket:
        """Convert a MatchResult to a RelatedMarket."""
        return RelatedMarket(
            platform="kalshi",
            ticker=result.market.ticker,
            title=result.market.title,
            yes_price=result.market.yes_price,
            no_price=result.market.no_price,
            volume=result.market.volume,
            close_date=result.market.close_time.isoformat() if result.market.close_time else None,
            relevance_score=result.relevance_score,
            relevance_type=result.relevance_type,
        )
