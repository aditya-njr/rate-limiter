from app.limiters.types import RateLimitResult


class TokenBucketLimiter:
    """Token bucket (parity with server tokenBucket.ts)."""

    def __init__(self, capacity: int, refill_per_ms: float) -> None:
        self._capacity = capacity
        self._refill_per_ms = refill_per_ms
        self._tokens = float(capacity)
        self._last_refill_ms: float | None = None

    def try_acquire(self, now_ms: float) -> RateLimitResult:
        if self._last_refill_ms is None:
            self._last_refill_ms = now_ms
        else:
            elapsed = now_ms - self._last_refill_ms
            if elapsed > 0:
                self._tokens = min(
                    float(self._capacity), self._tokens + elapsed * self._refill_per_ms
                )
                self._last_refill_ms = now_ms

        if self._tokens >= 1:
            self._tokens -= 1
            return RateLimitResult(allowed=True, remaining=int(self._tokens))

        needed = 1 - self._tokens
        if self._refill_per_ms > 0:
            retry_after_ms = needed / self._refill_per_ms
        else:
            retry_after_ms = None
        return RateLimitResult(allowed=False, remaining=0, retry_after_ms=retry_after_ms)

    def reset(self) -> None:
        self._tokens = float(self._capacity)
        self._last_refill_ms = None
