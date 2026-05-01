from app.limiters.types import RateLimitResult


class LeakyBucketLimiter:
    """Leaky bucket (parity with server leakyBucket.ts)."""

    def __init__(self, capacity: int, leak_per_ms: float) -> None:
        self._capacity = capacity
        self._leak_per_ms = leak_per_ms
        self._depth = 0.0
        self._last_update_ms: float | None = None

    def try_acquire(self, now_ms: float) -> RateLimitResult:
        if self._last_update_ms is None:
            self._last_update_ms = now_ms
        else:
            elapsed = now_ms - self._last_update_ms
            if elapsed > 0:
                leaked = elapsed * self._leak_per_ms
                self._depth = max(0.0, self._depth - leaked)
                self._last_update_ms = now_ms

        if self._depth < self._capacity:
            self._depth += 1
            return RateLimitResult(
                allowed=True, remaining=int(self._capacity - self._depth)
            )

        excess = self._depth - self._capacity + 1
        if self._leak_per_ms > 0:
            retry_after_ms = excess / self._leak_per_ms
        else:
            # JS JSON.stringify(Infinity) -> null; no meaningful retry when leak rate is zero.
            retry_after_ms = None
        return RateLimitResult(allowed=False, remaining=0, retry_after_ms=retry_after_ms)

    def reset(self) -> None:
        self._depth = 0.0
        self._last_update_ms = None
