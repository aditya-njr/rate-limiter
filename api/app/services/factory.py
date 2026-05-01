from typing import Any

from app.limiters import (
    FixedWindowLimiter,
    LeakyBucketLimiter,
    SlidingWindowLogLimiter,
    TokenBucketLimiter,
)


def create_limiter(algorithm: str, config: dict[str, Any]):
    if algorithm == "fixedWindow":
        return FixedWindowLimiter(int(config["windowMs"]), int(config["maxRequests"]))
    if algorithm == "slidingWindow":
        return SlidingWindowLogLimiter(int(config["windowMs"]), int(config["maxRequests"]))
    if algorithm == "tokenBucket":
        c = int(config["capacity"])
        refill_per_second = float(config["refillPerSecond"])
        return TokenBucketLimiter(c, refill_per_second / 1000.0)
    if algorithm == "leakyBucket":
        c = int(config["capacity"])
        leak_per_second = float(config["leakPerSecond"])
        return LeakyBucketLimiter(c, leak_per_second / 1000.0)
    raise ValueError(f"Unknown algorithm: {algorithm}")
