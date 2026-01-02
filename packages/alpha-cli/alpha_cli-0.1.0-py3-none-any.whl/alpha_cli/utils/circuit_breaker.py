"""Circuit breaker pattern for external service calls."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


class CircuitState(Enum):
    """State of the circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitOpenError(Exception):
    """Raised when the circuit is open and requests are rejected."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Circuit {name} is OPEN")


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    States:
    - CLOSED: Requests pass through normally
    - OPEN: Requests fail immediately (service is down)
    - HALF_OPEN: Allow one request to test recovery

    Example:
        kalshi_circuit = CircuitBreaker(name="kalshi", failure_threshold=5)

        async def fetch_markets():
            return await kalshi_circuit.call(_fetch_markets_impl)
    """

    name: str
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before trying again
    success_threshold: int = 2  # Successes to close from half-open

    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: datetime | None = field(default=None)

    async def call(self, func: Callable[..., Awaitable[T]], *args: object, **kwargs: object) -> T:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            CircuitOpenError: If circuit is open
            Exception: Any exception from func
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(self.name)

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
