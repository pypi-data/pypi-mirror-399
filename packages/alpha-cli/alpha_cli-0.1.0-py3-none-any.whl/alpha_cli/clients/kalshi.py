"""Client for Kalshi prediction market API."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx

from alpha_cli.types import KalshiMarket, KalshiOrderBook
from alpha_cli.utils.retry import RetryConfig, with_retry
from alpha_cli.utils.circuit_breaker import CircuitBreaker

# Kalshi API configuration
KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
KALSHI_DEMO_URL = "https://demo-api.kalshi.co/trade-api/v2"

# JWT token expires every 30 minutes
JWT_EXPIRY_SECONDS = 30 * 60

# Circuit breaker for Kalshi API
_kalshi_circuit = CircuitBreaker(name="kalshi", failure_threshold=5, recovery_timeout=60)


class KalshiClient:
    """
    Client for Kalshi prediction market API.

    Documentation: https://docs.kalshi.com/

    Example:
        client = KalshiClient()
        markets = await client.get_markets(limit=10)
        for market in markets:
            print(f"{market.ticker}: YES @ {market.yes_price}")

    For authenticated operations (trading):
        client = KalshiClient(api_key="your_key", private_key_path="~/.kalshi/key.pem")
    """

    def __init__(
        self,
        api_key: str | None = None,
        private_key_path: str | None = None,
        use_demo: bool = False,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the Kalshi client.

        Args:
            api_key: Kalshi API key (for authenticated operations)
            private_key_path: Path to private key for signing (for trading)
            use_demo: Use demo API instead of production
            timeout: HTTP request timeout in seconds
        """
        self.api_key = api_key
        self.private_key_path = private_key_path
        self.base_url = KALSHI_DEMO_URL if use_demo else KALSHI_BASE_URL
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None
        self._jwt_token: str | None = None
        self._jwt_expiry: float = 0

    async def _get_http(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http is None or self._http.is_closed:
            headers = {"User-Agent": "AlphaCLI/1.0 (https://alpha.dev)"}
            self._http = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._http

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers with JWT token."""
        if not self.api_key:
            return {}

        # Check if token needs refresh
        if self._jwt_token is None or time.time() > self._jwt_expiry:
            await self._refresh_token()

        if self._jwt_token:
            return {"Authorization": f"Bearer {self._jwt_token}"}
        return {}

    async def _refresh_token(self) -> None:
        """Refresh JWT token."""
        if not self.api_key:
            return

        http = await self._get_http()
        response = await http.post(
            "/login",
            json={"email": "", "password": "", "api_key": self.api_key},
        )
        if response.status_code == 200:
            data = response.json()
            self._jwt_token = data.get("token")
            # Set expiry to 25 minutes (5 minutes before actual expiry)
            self._jwt_expiry = time.time() + JWT_EXPIRY_SECONDS - 300

    def _parse_market(self, raw: dict[str, Any]) -> KalshiMarket:
        """Parse raw market data into KalshiMarket object."""
        # Parse close time
        close_time = None
        if raw.get("close_time"):
            try:
                close_time = datetime.fromisoformat(raw["close_time"].replace("Z", "+00:00"))
            except ValueError:
                pass

        # Parse expiration time
        expiration_time = None
        if raw.get("expiration_time"):
            try:
                expiration_time = datetime.fromisoformat(
                    raw["expiration_time"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        # Parse prices (Kalshi uses cents)
        yes_price = Decimal(str(raw.get("yes_price", 0))) / 100
        no_price = Decimal(str(raw.get("no_price", 0))) / 100
        yes_bid = Decimal(str(raw.get("yes_bid", 0))) / 100
        yes_ask = Decimal(str(raw.get("yes_ask", 0))) / 100
        no_bid = Decimal(str(raw.get("no_bid", 0))) / 100
        no_ask = Decimal(str(raw.get("no_ask", 0))) / 100

        return KalshiMarket(
            ticker=raw.get("ticker", ""),
            title=raw.get("title", ""),
            subtitle=raw.get("subtitle"),
            category=raw.get("category"),
            status=raw.get("status", "open"),
            yes_price=yes_price,
            no_price=no_price,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_bid=no_bid,
            no_ask=no_ask,
            volume=raw.get("volume", 0),
            open_interest=raw.get("open_interest", 0),
            close_time=close_time,
            expiration_time=expiration_time,
            result=raw.get("result"),
        )

    @with_retry(RetryConfig(max_attempts=3))
    async def get_markets(
        self,
        limit: int = 100,
        cursor: str | None = None,
        status: str | None = None,
        series_ticker: str | None = None,
        event_ticker: str | None = None,
    ) -> tuple[list[KalshiMarket], str | None]:
        """
        Get list of markets.

        Args:
            limit: Maximum number of markets to return (max 1000)
            cursor: Pagination cursor
            status: Filter by status (open, closed, settled)
            series_ticker: Filter by series ticker
            event_ticker: Filter by event ticker

        Returns:
            Tuple of (list of markets, next cursor)
        """
        http = await self._get_http()

        params: dict[str, Any] = {"limit": min(limit, 1000)}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        if series_ticker:
            params["series_ticker"] = series_ticker
        if event_ticker:
            params["event_ticker"] = event_ticker

        async def _fetch() -> httpx.Response:
            return await http.get("/markets", params=params)

        response = await _kalshi_circuit.call(_fetch)
        response.raise_for_status()
        data = response.json()

        markets = [self._parse_market(m) for m in data.get("markets", [])]
        next_cursor = data.get("cursor")

        return markets, next_cursor

    @with_retry(RetryConfig(max_attempts=3))
    async def get_market(self, ticker: str) -> KalshiMarket | None:
        """
        Get a single market by ticker.

        Args:
            ticker: Market ticker

        Returns:
            KalshiMarket or None if not found
        """
        http = await self._get_http()

        async def _fetch() -> httpx.Response:
            return await http.get(f"/markets/{ticker}")

        try:
            response = await _kalshi_circuit.call(_fetch)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return self._parse_market(data.get("market", data))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    @with_retry(RetryConfig(max_attempts=3))
    async def get_orderbook(self, ticker: str, depth: int = 10) -> KalshiOrderBook | None:
        """
        Get order book for a market.

        Args:
            ticker: Market ticker
            depth: Number of price levels to return

        Returns:
            KalshiOrderBook or None if not found
        """
        http = await self._get_http()

        async def _fetch() -> httpx.Response:
            return await http.get(f"/markets/{ticker}/orderbook", params={"depth": depth})

        try:
            response = await _kalshi_circuit.call(_fetch)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

            orderbook = data.get("orderbook", data)

            # Parse bids and asks (prices in cents)
            yes_bids: list[tuple[Decimal, int]] = []
            yes_asks: list[tuple[Decimal, int]] = []
            no_bids: list[tuple[Decimal, int]] = []
            no_asks: list[tuple[Decimal, int]] = []

            for bid in orderbook.get("yes", {}).get("bids", []):
                price = Decimal(str(bid.get("price", 0))) / 100
                qty = bid.get("quantity", 0)
                yes_bids.append((price, qty))

            for ask in orderbook.get("yes", {}).get("asks", []):
                price = Decimal(str(ask.get("price", 0))) / 100
                qty = ask.get("quantity", 0)
                yes_asks.append((price, qty))

            for bid in orderbook.get("no", {}).get("bids", []):
                price = Decimal(str(bid.get("price", 0))) / 100
                qty = bid.get("quantity", 0)
                no_bids.append((price, qty))

            for ask in orderbook.get("no", {}).get("asks", []):
                price = Decimal(str(ask.get("price", 0))) / 100
                qty = ask.get("quantity", 0)
                no_asks.append((price, qty))

            return KalshiOrderBook(
                ticker=ticker,
                yes_bids=yes_bids,
                yes_asks=yes_asks,
                no_bids=no_bids,
                no_asks=no_asks,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def search_markets(
        self, query: str, limit: int = 20
    ) -> list[KalshiMarket]:
        """
        Search markets by query string.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching markets
        """
        # Kalshi doesn't have a native search endpoint, so we fetch markets
        # and filter client-side. In a real implementation, you'd want to
        # index markets in a search-friendly data structure.
        markets, _ = await self.get_markets(limit=1000, status="open")

        query_lower = query.lower()
        matches: list[KalshiMarket] = []

        for market in markets:
            # Check if query matches ticker, title, or subtitle
            if (
                query_lower in market.ticker.lower()
                or query_lower in market.title.lower()
                or (market.subtitle and query_lower in market.subtitle.lower())
            ):
                matches.append(market)
                if len(matches) >= limit:
                    break

        return matches

    async def get_all_markets(self, status: str | None = "open") -> list[KalshiMarket]:
        """
        Get all markets (handles pagination).

        Args:
            status: Filter by status (open, closed, settled)

        Returns:
            List of all markets
        """
        all_markets: list[KalshiMarket] = []
        cursor: str | None = None

        while True:
            markets, cursor = await self.get_markets(
                limit=1000,
                cursor=cursor,
                status=status,
            )
            all_markets.extend(markets)

            if not cursor or not markets:
                break

        return all_markets
