"""Tests for ticker-to-market matching system."""

import pytest
from decimal import Decimal

from alpha_cli.services.matching import TickerMatcher, TICKER_MARKET_MAPPINGS
from alpha_cli.types import KalshiMarket


@pytest.fixture
def matcher() -> TickerMatcher:
    """Create a matcher instance."""
    return TickerMatcher()


@pytest.fixture
def sample_markets() -> list[KalshiMarket]:
    """Create sample markets for testing."""
    return [
        KalshiMarket(
            ticker="KXNVDA-Q4-EARNINGS",
            title="Will NVIDIA beat Q4 earnings?",
            yes_price=Decimal("0.65"),
            no_price=Decimal("0.36"),
            volume=50000,
        ),
        KalshiMarket(
            ticker="KXNVIDIA-1000",
            title="Will NVIDIA hit $1000 by March?",
            yes_price=Decimal("0.45"),
            no_price=Decimal("0.56"),
            volume=25000,
        ),
        KalshiMarket(
            ticker="KXAICHIP-EXPORT-BAN",
            title="Will US expand AI chip export bans?",
            yes_price=Decimal("0.72"),
            no_price=Decimal("0.29"),
            volume=15000,
        ),
        KalshiMarket(
            ticker="KXBTC-150K",
            title="Will Bitcoin hit $150K?",
            yes_price=Decimal("0.32"),
            no_price=Decimal("0.69"),
            volume=100000,
        ),
        KalshiMarket(
            ticker="KXFED-RATE-JAN",
            title="Will Fed cut rates in January?",
            yes_price=Decimal("0.55"),
            no_price=Decimal("0.46"),
            volume=75000,
        ),
    ]


class TestTickerMatcher:
    """Tests for TickerMatcher class."""

    def test_ticker_mappings_exist(self) -> None:
        """Verify that curated mappings exist for top tickers."""
        top_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA"]
        for ticker in top_tickers:
            assert ticker in TICKER_MARKET_MAPPINGS, f"Missing mapping for {ticker}"

    def test_match_nvda_direct(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test direct NVDA matches."""
        results = matcher.match_tier1("NVDA", sample_markets)

        assert len(results) >= 2, "Should match at least 2 NVDA-related markets"

        # Check direct matches
        tickers = [r.market.ticker for r in results]
        assert "KXNVDA-Q4-EARNINGS" in tickers
        assert "KXNVIDIA-1000" in tickers

    def test_match_nvda_sector(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test sector-level NVDA matches."""
        results = matcher.match_tier1("NVDA", sample_markets)

        # Should include AI chip sector market
        tickers = [r.market.ticker for r in results]
        assert "KXAICHIP-EXPORT-BAN" in tickers

        # Sector matches should have lower relevance
        for result in results:
            if result.market.ticker == "KXAICHIP-EXPORT-BAN":
                assert result.relevance_type == "sector"
                assert result.relevance_score < 1.0

    def test_match_case_insensitive(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test that matching is case-insensitive."""
        results_upper = matcher.match_tier1("NVDA", sample_markets)
        results_lower = matcher.match_tier1("nvda", sample_markets)

        assert len(results_upper) == len(results_lower)

    def test_no_match_unknown_ticker(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test that unknown tickers return no matches."""
        results = matcher.match_tier1("UNKNOWN123", sample_markets)
        assert len(results) == 0

    def test_results_sorted_by_relevance(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test that results are sorted by relevance score descending."""
        results = matcher.match_tier1("NVDA", sample_markets)

        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i + 1].relevance_score

    def test_no_duplicate_markets(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test that the same market isn't returned multiple times."""
        results = matcher.match_tier1("NVDA", sample_markets)
        tickers = [r.market.ticker for r in results]
        assert len(tickers) == len(set(tickers)), "Duplicate markets in results"

    def test_to_related_market_conversion(
        self, matcher: TickerMatcher, sample_markets: list[KalshiMarket]
    ) -> None:
        """Test conversion from MatchResult to RelatedMarket."""
        results = matcher.match_tier1("NVDA", sample_markets)

        if results:
            related = matcher.to_related_market(results[0])
            assert related.platform == "kalshi"
            assert related.ticker == results[0].market.ticker
            assert related.title == results[0].market.title
            assert related.relevance_score == results[0].relevance_score


class TestMatchingPatterns:
    """Tests for specific matching patterns."""

    def test_technology_tickers(self, matcher: TickerMatcher) -> None:
        """Test that technology tickers have mappings."""
        tech_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMD", "INTC"]
        for ticker in tech_tickers:
            assert ticker in TICKER_MARKET_MAPPINGS
            patterns = TICKER_MARKET_MAPPINGS[ticker]
            assert len(patterns) > 0, f"No patterns for {ticker}"

    def test_finance_tickers(self, matcher: TickerMatcher) -> None:
        """Test that finance tickers have mappings."""
        finance_tickers = ["JPM"]
        for ticker in finance_tickers:
            assert ticker in TICKER_MARKET_MAPPINGS

    def test_crypto_related_tickers(self, matcher: TickerMatcher) -> None:
        """Test that crypto-related tickers have sector mappings."""
        assert "COIN" in TICKER_MARKET_MAPPINGS
        coin_patterns = TICKER_MARKET_MAPPINGS["COIN"]

        # Should have sector-level crypto mappings
        has_crypto_sector = any(
            p["type"] == "sector" for p in coin_patterns
        )
        assert has_crypto_sector, "COIN should have crypto sector mappings"
