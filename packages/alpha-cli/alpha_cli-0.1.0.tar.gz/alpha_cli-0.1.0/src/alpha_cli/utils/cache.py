"""Caching utilities with stale data fallback."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


class FetchError(Exception):
    """Raised when fetch fails and no cached data is available."""

    pass


@dataclass
class CachedValue(Generic[T]):
    """A cached value with metadata."""

    data: T
    fetched_at: datetime
    is_stale: bool = False


class StaleCacheStrategy:
    """
    Cache strategy that serves stale data when fresh fetch fails.

    Behavior:
    - On success: Update cache, return fresh data
    - On failure: Return stale cached data with warning
    - On failure + no cache: Raise error

    Example:
        cache = StaleCacheStrategy()

        async def get_congress_trades():
            result = await cache.get_or_fetch(
                key="congress_trades",
                fetcher=fetch_from_api,
                ttl=timedelta(hours=1),
            )
            if result.is_stale:
                print("Using cached data")
            return result.data
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        """
        Initialize cache strategy.

        Args:
            cache_dir: Directory for cache files. Defaults to ~/.alpha/cache
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".alpha" / "cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_or_fetch(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[T]],
        ttl: timedelta = timedelta(minutes=15),
        stale_ttl: timedelta = timedelta(hours=24),
    ) -> CachedValue[T]:
        """
        Get cached data or fetch fresh.

        Falls back to stale data if fetch fails.

        Args:
            key: Cache key (used as filename)
            fetcher: Async function to fetch fresh data
            ttl: Time-to-live for fresh data
            stale_ttl: Maximum age for stale data fallback

        Returns:
            CachedValue with data and metadata

        Raises:
            FetchError: If fetch fails and no cached data is available
        """
        cache_path = self.cache_dir / f"{key}.json"

        # Check cache
        cached = self._read_cache(cache_path)
        if cached is not None:
            is_fresh = (datetime.now() - cached.fetched_at) < ttl
            if is_fresh:
                return cached

        # Try to fetch fresh data
        try:
            fresh_data = await fetcher()
            fresh_value: CachedValue[T] = CachedValue(
                data=fresh_data,
                fetched_at=datetime.now(),
                is_stale=False,
            )
            self._write_cache(cache_path, fresh_value)
            return fresh_value

        except Exception as e:
            # Fetch failed - can we serve stale?
            if cached is not None and (datetime.now() - cached.fetched_at) < stale_ttl:
                cached.is_stale = True
                return cached

            # No usable cache
            raise FetchError(f"Failed to fetch {key} and no cached data available") from e

    def _read_cache(self, path: Path) -> CachedValue[T] | None:
        """Read cached value from file."""
        if not path.exists():
            return None
        try:
            with open(path) as f:
                raw = json.load(f)
            return CachedValue(
                data=raw["data"],
                fetched_at=datetime.fromisoformat(raw["fetched_at"]),
                is_stale=False,
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _write_cache(self, path: Path, value: CachedValue[T]) -> None:
        """Write cached value to file."""
        with open(path, "w") as f:
            json.dump(
                {
                    "data": value.data,
                    "fetched_at": value.fetched_at.isoformat(),
                },
                f,
            )

    def invalidate(self, key: str) -> None:
        """Invalidate a cached value."""
        cache_path = self.cache_dir / f"{key}.json"
        if cache_path.exists():
            cache_path.unlink()

    def clear(self) -> None:
        """Clear all cached values."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
