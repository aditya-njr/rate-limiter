from app.limiters.types import RateLimitResult


class SlidingWindowLogLimiter:
    """Sliding window log (parity with server slidingWindow.ts)."""

    def __init__(self, window_ms: int, max_requests: int) -> None:
        self._window_ms = window_ms
        self._max_requests = max_requests
        self._timestamps: list[float] = []

    def try_acquire(self, now_ms: float) -> RateLimitResult:
        window_start = now_ms - self._window_ms
        while self._timestamps and self._timestamps[0] < window_start:
            self._timestamps.pop(0)

        if len(self._timestamps) < self._max_requests:
            self._timestamps.append(now_ms)
            return RateLimitResult(allowed=True, remaining=self._max_requests - len(self._timestamps))

        oldest = self._timestamps[0]
        retry_after_ms = max(0.0, oldest + self._window_ms - now_ms)
        return RateLimitResult(allowed=False, remaining=0, retry_after_ms=retry_after_ms)

    def reset(self) -> None:
        self._timestamps.clear()
