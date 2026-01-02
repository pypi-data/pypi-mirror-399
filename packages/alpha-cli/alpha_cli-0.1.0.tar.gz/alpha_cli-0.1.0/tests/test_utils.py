"""Tests for utility modules."""

import asyncio
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

from alpha_cli.utils.retry import RetryConfig, with_retry
from alpha_cli.utils.circuit_breaker import CircuitBreaker, CircuitState, CircuitOpenError
from alpha_cli.utils.cache import StaleCacheStrategy, CachedValue, FetchError


class TestRetryDecorator:
    """Tests for retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self) -> None:
        """Test that successful calls don't retry."""
        call_count = 0

        @with_retry()
        async def successful_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self) -> None:
        """Test that connection errors trigger retry."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_errors(self) -> None:
        """Test that 4xx errors don't trigger retry by default."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3))
        async def client_error_func() -> str:
            nonlocal call_count
            call_count += 1
            response = httpx.Response(400, request=httpx.Request("GET", "http://test"))
            raise httpx.HTTPStatusError("Bad Request", request=response.request, response=response)

        with pytest.raises(httpx.HTTPStatusError):
            await client_error_func()

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_retry_on_5xx_errors(self) -> None:
        """Test that 5xx errors trigger retry."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def server_error_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                response = httpx.Response(503, request=httpx.Request("GET", "http://test"))
                raise httpx.HTTPStatusError("Service Unavailable", request=response.request, response=response)
            return "success"

        result = await server_error_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_attempts_exhausted(self) -> None:
        """Test that error is raised when max attempts exhausted."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise httpx.ConnectError("Always fails")

        with pytest.raises(httpx.ConnectError):
            await always_fail()

        assert call_count == 3


class TestCircuitBreaker:
    """Tests for circuit breaker."""

    @pytest.mark.asyncio
    async def test_closed_state_allows_calls(self) -> None:
        """Test that closed circuit allows calls through."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)

        async def success() -> str:
            return "ok"

        result = await breaker.call(success)
        assert result == "ok"
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self) -> None:
        """Test that circuit opens after threshold failures."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)

        async def fail() -> str:
            raise Exception("error")

        # Trigger failures
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(fail)

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self) -> None:
        """Test that open circuit rejects calls immediately."""
        breaker = CircuitBreaker(name="test", failure_threshold=1)

        async def fail() -> str:
            raise Exception("error")

        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(fail)

        # Next call should be rejected without calling function
        with pytest.raises(CircuitOpenError):
            await breaker.call(fail)

    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self) -> None:
        """Test that circuit goes half-open after recovery timeout."""
        breaker = CircuitBreaker(name="test", failure_threshold=1, recovery_timeout=0.01)

        async def fail() -> str:
            raise Exception("error")

        async def success() -> str:
            return "ok"

        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(fail)

        # Wait for recovery timeout
        await asyncio.sleep(0.02)

        # Circuit should allow one call (half-open)
        result = await breaker.call(success)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_closes_after_success_threshold(self) -> None:
        """Test that circuit closes after success threshold in half-open."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=0.01,
            success_threshold=2
        )

        async def fail() -> str:
            raise Exception("error")

        async def success() -> str:
            return "ok"

        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(fail)

        await asyncio.sleep(0.02)

        # Successful calls should close circuit
        await breaker.call(success)
        await breaker.call(success)

        assert breaker.state == CircuitState.CLOSED

    def test_reset_method(self) -> None:
        """Test manual reset of circuit breaker."""
        breaker = CircuitBreaker(name="test")
        breaker.state = CircuitState.OPEN
        breaker.failure_count = 10

        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0


class TestStaleCacheStrategy:
    """Tests for stale cache strategy."""

    @pytest.fixture
    def cache_dir(self, tmp_path: Path) -> Path:
        """Create temporary cache directory."""
        return tmp_path / "cache"

    @pytest.fixture
    def cache(self, cache_dir: Path) -> StaleCacheStrategy:
        """Create cache instance."""
        return StaleCacheStrategy(cache_dir)

    @pytest.mark.asyncio
    async def test_fetch_and_cache(self, cache: StaleCacheStrategy) -> None:
        """Test that data is fetched and cached."""
        async def fetcher() -> dict:
            return {"value": 42}

        result = await cache.get_or_fetch("test", fetcher)

        assert result.data == {"value": 42}
        assert result.is_stale is False

    @pytest.mark.asyncio
    async def test_returns_cached_when_fresh(self, cache: StaleCacheStrategy) -> None:
        """Test that cached data is returned when fresh."""
        call_count = 0

        async def fetcher() -> dict:
            nonlocal call_count
            call_count += 1
            return {"value": call_count}

        # First call - fetches
        result1 = await cache.get_or_fetch("test", fetcher, ttl=timedelta(hours=1))
        assert result1.data["value"] == 1

        # Second call - uses cache
        result2 = await cache.get_or_fetch("test", fetcher, ttl=timedelta(hours=1))
        assert result2.data["value"] == 1
        assert call_count == 1  # Only called once

    @pytest.mark.asyncio
    async def test_returns_stale_on_fetch_failure(self, cache: StaleCacheStrategy) -> None:
        """Test that stale data is returned when fetch fails."""
        call_count = 0

        async def fetcher() -> dict:
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise Exception("Fetch failed")
            return {"value": 42}

        # First call - succeeds
        await cache.get_or_fetch(
            "test", fetcher,
            ttl=timedelta(seconds=0),  # Immediately stale
            stale_ttl=timedelta(hours=1)
        )

        # Second call - fails but returns stale
        result = await cache.get_or_fetch(
            "test", fetcher,
            ttl=timedelta(seconds=0),
            stale_ttl=timedelta(hours=1)
        )

        assert result.data["value"] == 42
        assert result.is_stale is True

    @pytest.mark.asyncio
    async def test_raises_when_no_cache_and_fetch_fails(
        self, cache: StaleCacheStrategy
    ) -> None:
        """Test that error is raised when fetch fails and no cache."""
        async def failing_fetcher() -> dict:
            raise Exception("Fetch failed")

        with pytest.raises(FetchError):
            await cache.get_or_fetch("new_key", failing_fetcher)

    def test_invalidate(self, cache: StaleCacheStrategy, cache_dir: Path) -> None:
        """Test cache invalidation."""
        # Create a cache file
        cache_file = cache_dir / "test.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text('{"data": 1, "fetched_at": "2025-01-01T00:00:00"}')

        cache.invalidate("test")

        assert not cache_file.exists()

    def test_clear(self, cache: StaleCacheStrategy, cache_dir: Path) -> None:
        """Test clearing all cache."""
        # Create multiple cache files
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "test1.json").write_text("{}")
        (cache_dir / "test2.json").write_text("{}")

        cache.clear()

        assert len(list(cache_dir.glob("*.json"))) == 0
