"""Shared type definitions for Alpha CLI."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal


class AuthState(Enum):
    """Authentication state for CLI users."""

    ANONYMOUS = "anonymous"  # No API key stored
    AUTHENTICATED_FREE = "free"  # Valid API key, no subscription
    AUTHENTICATED_PREMIUM = "premium"  # Valid API key + active subscription
    AUTHENTICATED_EXPIRED = "expired"  # Valid API key, subscription lapsed
    INVALID = "invalid"  # API key rejected by backend


@dataclass
class AuthContext:
    """Authentication context containing user state."""

    state: AuthState
    user_email: str | None = None
    subscription_end: datetime | None = None

    def can_use_premium(self) -> bool:
        """Check if user can access premium features."""
        return self.state == AuthState.AUTHENTICATED_PREMIUM


@dataclass
class AlphaCredentials:
    """Credentials for Alpha CLI backend."""

    api_key: str
    user_email: str | None = None


@dataclass
class KalshiCredentials:
    """Credentials for Kalshi API."""

    api_key: str
    private_key_path: str | None = None


# Congress Trading Types


@dataclass
class CongressTrade:
    """A congressional stock trade."""

    transaction_date: str
    disclosure_date: str
    ticker: str
    asset_description: str
    asset_type: str
    trade_type: Literal["purchase", "sale", "exchange"]
    amount: str
    representative: str
    district: str | None = None
    state: str | None = None
    party: Literal["R", "D", "I"] | None = None
    owner: str | None = None
    ptr_link: str | None = None
    chamber: Literal["house", "senate"] | None = None


# Kalshi Market Types


@dataclass
class KalshiMarket:
    """A Kalshi prediction market."""

    ticker: str
    title: str
    subtitle: str | None = None
    category: str | None = None
    status: str = "open"
    yes_price: Decimal = Decimal("0")
    no_price: Decimal = Decimal("0")
    yes_bid: Decimal = Decimal("0")
    yes_ask: Decimal = Decimal("0")
    no_bid: Decimal = Decimal("0")
    no_ask: Decimal = Decimal("0")
    volume: int = 0
    open_interest: int = 0
    close_time: datetime | None = None
    expiration_time: datetime | None = None
    result: str | None = None


@dataclass
class KalshiOrderBook:
    """Order book for a Kalshi market."""

    ticker: str
    yes_bids: list[tuple[Decimal, int]] = field(default_factory=list)  # (price, quantity)
    yes_asks: list[tuple[Decimal, int]] = field(default_factory=list)
    no_bids: list[tuple[Decimal, int]] = field(default_factory=list)
    no_asks: list[tuple[Decimal, int]] = field(default_factory=list)


# Matching Types


@dataclass
class RelatedMarket:
    """A market related to a ticker/trade."""

    platform: Literal["kalshi", "polymarket"]
    ticker: str
    title: str
    yes_price: Decimal
    no_price: Decimal
    volume: int
    close_date: str | None = None
    relevance_score: float = 0.0
    relevance_type: Literal["direct", "sector", "macro"] = "direct"


@dataclass
class CrossReference:
    """Cross-reference between a congress trade and related markets."""

    congress_trade: CongressTrade
    related_markets: list[RelatedMarket] = field(default_factory=list)


@dataclass
class ScanResult:
    """Result of alpha scan command."""

    cross_references: list[CrossReference]
    generated_at: datetime
    cache_ttl: int = 900  # 15 minutes
    is_stale: bool = False


# Error Types


class ErrorCode(Enum):
    """Error codes for Alpha CLI."""

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
    """Custom exception for Alpha CLI errors."""

    code: ErrorCode
    message: str
    details: dict | None = None
    retry_after: int | None = None  # Seconds until retry (for rate limits)

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"


# User-friendly error messages
ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_API_KEY: "Invalid API key. Run `alpha login` to authenticate.",
    ErrorCode.EXPIRED_API_KEY: "Your API key has expired. Run `alpha login` to get a new one.",
    ErrorCode.PREMIUM_REQUIRED: "This feature requires a premium subscription. Run `alpha upgrade`.",
    ErrorCode.RATE_LIMITED: "Rate limit exceeded. Please wait {retry_after} seconds.",
    ErrorCode.KALSHI_UNAVAILABLE: (
        "Kalshi API is currently unavailable. Try again later or use cached data."
    ),
    ErrorCode.CONGRESS_DATA_UNAVAILABLE: "Congressional trading data is temporarily unavailable.",
    ErrorCode.INVALID_TICKER: "Invalid ticker symbol provided.",
    ErrorCode.INVALID_MARKET: "Invalid market ticker provided.",
}
