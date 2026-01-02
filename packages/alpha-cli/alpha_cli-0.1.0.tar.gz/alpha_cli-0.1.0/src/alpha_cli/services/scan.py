"""Scan service for cross-referencing congress trades with prediction markets."""

from datetime import datetime, timedelta
from typing import Literal

from alpha_cli.clients.congress import CongressClient
from alpha_cli.clients.kalshi import KalshiClient
from alpha_cli.services.matching import TickerMatcher
from alpha_cli.types import (
    AuthContext,
    AuthState,
    CongressTrade,
    CrossReference,
    RelatedMarket,
    ScanResult,
)
from alpha_cli.utils.cache import StaleCacheStrategy


class ScanService:
    """
    Service for cross-referencing congressional trades with prediction markets.

    This is the core premium feature of Alpha CLI. It:
    1. Fetches recent congressional trades
    2. Matches tickers to relevant Kalshi markets
    3. Returns cross-references with relevance scores

    The basic scan (Tier 1 matching) is available to all users.
    Premium users get enhanced matching via the backend API.
    """

    def __init__(
        self,
        congress_client: CongressClient | None = None,
        kalshi_client: KalshiClient | None = None,
        cache: StaleCacheStrategy | None = None,
    ) -> None:
        """
        Initialize the scan service.

        Args:
            congress_client: Client for congressional data
            kalshi_client: Client for Kalshi markets
            cache: Cache strategy for data
        """
        self.congress_client = congress_client or CongressClient()
        self.kalshi_client = kalshi_client or KalshiClient()
        self.matcher = TickerMatcher()
        self.cache = cache or StaleCacheStrategy()
        self._owns_clients = congress_client is None or kalshi_client is None

    async def close(self) -> None:
        """Close underlying clients if we created them."""
        if self._owns_clients:
            await self.congress_client.close()
            await self.kalshi_client.close()

    async def scan(
        self,
        days: int = 30,
        ticker: str | None = None,
        party: Literal["R", "D"] | None = None,
        min_relevance: float = 0.5,
        auth_context: AuthContext | None = None,
    ) -> ScanResult:
        """
        Scan for congressional trades with relevant prediction markets.

        Args:
            days: Number of days to look back
            ticker: Filter by stock ticker
            party: Filter by party
            min_relevance: Minimum relevance score (0-1)
            auth_context: User authentication context

        Returns:
            ScanResult with cross-references
        """
        # Determine if user has premium access
        is_premium = auth_context and auth_context.can_use_premium()

        # Fetch congressional trades
        trades = await self.congress_client.get_trades(
            days=days,
            ticker=ticker,
            party=party,
        )

        # Fetch Kalshi markets (use cache)
        markets_result = await self.cache.get_or_fetch(
            key="kalshi_markets",
            fetcher=lambda: self.kalshi_client.get_all_markets(status="open"),
            ttl=timedelta(minutes=15),
            stale_ttl=timedelta(hours=24),
        )
        markets = markets_result.data

        # Build cross-references
        cross_references: list[CrossReference] = []
        seen_tickers: set[str] = set()

        for trade in trades:
            # Skip if we've already processed this ticker
            if trade.ticker in seen_tickers:
                # Find existing cross-reference and add trade
                for cr in cross_references:
                    if cr.congress_trade.ticker == trade.ticker:
                        # We're grouping by ticker, so skip duplicate trades
                        # In a more sophisticated version, we'd aggregate trades
                        break
                continue

            seen_tickers.add(trade.ticker)

            # Match ticker to markets
            # For premium users, we'd call the backend for Tier 2/3 matching
            # For now, just use Tier 1
            match_results = self.matcher.match(
                ticker=trade.ticker,
                markets=markets,
                include_tier2=is_premium,
                include_tier3=is_premium,
            )

            # Filter by minimum relevance
            related_markets: list[RelatedMarket] = []
            for result in match_results:
                if result.relevance_score >= min_relevance:
                    related_markets.append(self.matcher.to_related_market(result))

            # Only include if we found related markets
            if related_markets:
                cross_references.append(
                    CrossReference(
                        congress_trade=trade,
                        related_markets=related_markets,
                    )
                )

        return ScanResult(
            cross_references=cross_references,
            generated_at=datetime.now(),
            cache_ttl=900,  # 15 minutes
            is_stale=markets_result.is_stale,
        )

    async def scan_single_ticker(
        self,
        ticker: str,
        days: int = 30,
        auth_context: AuthContext | None = None,
    ) -> CrossReference | None:
        """
        Scan for a single ticker's trades and related markets.

        Args:
            ticker: Stock ticker
            days: Number of days to look back
            auth_context: User authentication context

        Returns:
            CrossReference or None if no trades/markets found
        """
        result = await self.scan(
            days=days,
            ticker=ticker,
            auth_context=auth_context,
        )

        if result.cross_references:
            return result.cross_references[0]
        return None
