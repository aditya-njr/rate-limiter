from dataclasses import dataclass


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_ms: float | None = None
    remaining: int | None = None
