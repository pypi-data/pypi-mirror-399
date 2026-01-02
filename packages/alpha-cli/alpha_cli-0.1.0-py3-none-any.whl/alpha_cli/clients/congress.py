"""Client for congressional trading data from House/Senate Stock Watcher APIs."""

from datetime import datetime, timedelta
from typing import Literal

import httpx

from alpha_cli.types import CongressTrade
from alpha_cli.utils.retry import RetryConfig, with_retry
from alpha_cli.utils.circuit_breaker import CircuitBreaker

# API URLs
HOUSE_STOCK_WATCHER_URL = (
    "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
)
SENATE_STOCK_WATCHER_URL = (
    "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
)

# Party affiliation lookup (subset - would be expanded with full congress-legislators data)
# Source: https://github.com/unitedstates/congress-legislators
MEMBER_PARTIES: dict[str, Literal["R", "D", "I"]] = {
    # House members (sample - real implementation would load from congress-legislators)
    "Nancy Pelosi": "D",
    "Kevin McCarthy": "R",
    "Tommy Tuberville": "R",
    "Michael McCaul": "R",
    "Ro Khanna": "D",
    "Dan Crenshaw": "R",
    "Alexandria Ocasio-Cortez": "D",
    "Josh Gottheimer": "D",
    "Marjorie Taylor Greene": "R",
    "John Curtis": "R",
    # Add more as needed
}

# Circuit breakers for each data source
_house_circuit = CircuitBreaker(name="house_stock_watcher", failure_threshold=3, recovery_timeout=60)
_senate_circuit = CircuitBreaker(
    name="senate_stock_watcher", failure_threshold=3, recovery_timeout=60
)


class CongressClient:
    """
    Client for fetching congressional trading data.

    Data sources:
    - House Stock Watcher: https://housestockwatcher.com/api
    - Senate Stock Watcher: https://senatestockwatcher.com/api

    Example:
        client = CongressClient()
        trades = await client.get_trades(days=30)
        for trade in trades:
            print(f"{trade.representative} {trade.trade_type} {trade.ticker}")
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """
        Initialize the Congress client.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": "AlphaCLI/1.0 (https://alpha.dev)"},
            )
        return self._http

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    @with_retry(RetryConfig(max_attempts=3))
    async def _fetch_house_trades(self) -> list[dict]:
        """Fetch raw house trades data."""
        http = await self._get_http()

        async def _fetch() -> list[dict]:
            response = await http.get(HOUSE_STOCK_WATCHER_URL)
            response.raise_for_status()
            return response.json()

        return await _house_circuit.call(_fetch)

    @with_retry(RetryConfig(max_attempts=3))
    async def _fetch_senate_trades(self) -> list[dict]:
        """Fetch raw senate trades data."""
        http = await self._get_http()

        async def _fetch() -> list[dict]:
            response = await http.get(SENATE_STOCK_WATCHER_URL)
            response.raise_for_status()
            return response.json()

        return await _senate_circuit.call(_fetch)

    def _parse_trade(
        self, raw: dict, chamber: Literal["house", "senate"]
    ) -> CongressTrade | None:
        """Parse raw trade data into CongressTrade object."""
        try:
            # Get ticker - skip if missing
            ticker = raw.get("ticker", "").strip()
            if not ticker or ticker == "--":
                return None

            # Normalize trade type
            raw_type = raw.get("type", "").lower()
            if "purchase" in raw_type:
                trade_type: Literal["purchase", "sale", "exchange"] = "purchase"
            elif "sale" in raw_type:
                trade_type = "sale"
            elif "exchange" in raw_type:
                trade_type = "exchange"
            else:
                trade_type = "purchase"  # Default

            # Get member name
            representative = raw.get("representative", "") or raw.get("senator", "")
            representative = representative.strip()

            # Look up party affiliation
            party = MEMBER_PARTIES.get(representative)

            # Extract state from district if available
            district = raw.get("district", "")
            state = district[:2] if district and len(district) >= 2 else None

            return CongressTrade(
                transaction_date=raw.get("transaction_date", ""),
                disclosure_date=raw.get("disclosure_date", ""),
                ticker=ticker.upper(),
                asset_description=raw.get("asset_description", ""),
                asset_type=raw.get("asset_type", "Stock"),
                trade_type=trade_type,
                amount=raw.get("amount", ""),
                representative=representative,
                district=district,
                state=state,
                party=party,
                owner=raw.get("owner"),
                ptr_link=raw.get("ptr_link"),
                chamber=chamber,
            )
        except Exception:
            return None

    async def get_trades(
        self,
        days: int = 30,
        ticker: str | None = None,
        party: Literal["R", "D"] | None = None,
        member: str | None = None,
        chamber: Literal["house", "senate", "all"] = "all",
    ) -> list[CongressTrade]:
        """
        Get congressional trades with optional filters.

        Args:
            days: Number of days to look back
            ticker: Filter by stock ticker
            party: Filter by party (R or D)
            member: Filter by member name (partial match)
            chamber: Filter by chamber (house, senate, or all)

        Returns:
            List of CongressTrade objects
        """
        trades: list[CongressTrade] = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # Fetch data based on chamber filter
        if chamber in ("house", "all"):
            try:
                house_raw = await self._fetch_house_trades()
                for raw in house_raw:
                    trade = self._parse_trade(raw, "house")
                    if trade is not None:
                        trades.append(trade)
            except Exception:
                pass  # Continue with senate data if house fails

        if chamber in ("senate", "all"):
            try:
                senate_raw = await self._fetch_senate_trades()
                for raw in senate_raw:
                    trade = self._parse_trade(raw, "senate")
                    if trade is not None:
                        trades.append(trade)
            except Exception:
                pass  # Continue with house data if senate fails

        # Apply filters
        filtered: list[CongressTrade] = []
        for trade in trades:
            # Date filter
            try:
                trade_date = datetime.strptime(trade.transaction_date, "%Y-%m-%d")
                if trade_date < cutoff_date:
                    continue
            except ValueError:
                continue

            # Ticker filter
            if ticker and trade.ticker.upper() != ticker.upper():
                continue

            # Party filter
            if party and trade.party != party:
                continue

            # Member filter (partial match)
            if member and member.lower() not in trade.representative.lower():
                continue

            filtered.append(trade)

        # Sort by transaction date descending
        filtered.sort(key=lambda t: t.transaction_date, reverse=True)

        return filtered

    async def get_member_trades(self, member: str, days: int = 365) -> list[CongressTrade]:
        """
        Get all trades for a specific member.

        Args:
            member: Member name (partial match)
            days: Number of days to look back

        Returns:
            List of trades for the member
        """
        return await self.get_trades(days=days, member=member)

    async def get_ticker_trades(self, ticker: str, days: int = 365) -> list[CongressTrade]:
        """
        Get all trades for a specific ticker.

        Args:
            ticker: Stock ticker
            days: Number of days to look back

        Returns:
            List of trades for the ticker
        """
        return await self.get_trades(days=days, ticker=ticker)

    async def get_top_traded_tickers(self, days: int = 30, limit: int = 20) -> list[tuple[str, int]]:
        """
        Get the most traded tickers.

        Args:
            days: Number of days to look back
            limit: Maximum number of tickers to return

        Returns:
            List of (ticker, count) tuples sorted by count descending
        """
        trades = await self.get_trades(days=days)
        ticker_counts: dict[str, int] = {}

        for trade in trades:
            ticker_counts[trade.ticker] = ticker_counts.get(trade.ticker, 0) + 1

        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tickers[:limit]
