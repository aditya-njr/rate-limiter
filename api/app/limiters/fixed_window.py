from app.limiters.types import RateLimitResult


class FixedWindowLimiter:
    """Aligned fixed window counter (parity with server fixedWindow.ts)."""

    def __init__(self, window_ms: int, max_requests: int) -> None:
        self._window_ms = window_ms
        self._max_requests = max_requests
        self._window_index = -1
        self._count = 0

    def try_acquire(self, now_ms: float) -> RateLimitResult:
        idx = int(now_ms // self._window_ms)
        if idx != self._window_index:
            self._window_index = idx
            self._count = 0

        if self._count < self._max_requests:
            self._count += 1
            return RateLimitResult(allowed=True, remaining=self._max_requests - self._count)

        next_window_start = (idx + 1) * self._window_ms
        return RateLimitResult(
            allowed=False,
            remaining=0,
            retry_after_ms=max(0.0, next_window_start - now_ms),
        )

    def reset(self) -> None:
        self._window_index = -1
        self._count = 0
