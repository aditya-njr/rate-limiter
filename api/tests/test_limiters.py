from app.limiters import (
    FixedWindowLimiter,
    LeakyBucketLimiter,
    SlidingWindowLogLimiter,
    TokenBucketLimiter,
)


def test_fixed_window_allows_then_blocks_and_resets():
    l = FixedWindowLimiter(1000, 2)
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(1).remaining == 0
    assert l.try_acquire(2).allowed is False
    assert l.try_acquire(2).retry_after_ms is not None

    l2 = FixedWindowLimiter(1000, 1)
    assert l2.try_acquire(0).allowed is True
    assert l2.try_acquire(500).allowed is False
    assert l2.try_acquire(1000).allowed is True

    l3 = FixedWindowLimiter(1000, 1)
    l3.try_acquire(0)
    l3.reset()
    assert l3.try_acquire(0).allowed is True


def test_sliding_window():
    l = SlidingWindowLogLimiter(1000, 2)
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(100).allowed is True
    assert l.try_acquire(200).allowed is False

    l2 = SlidingWindowLogLimiter(1000, 2)
    l2.try_acquire(0)
    l2.try_acquire(100)
    assert l2.try_acquire(200).allowed is False
    assert l2.try_acquire(1001).allowed is True

    l3 = SlidingWindowLogLimiter(100, 1)
    l3.try_acquire(0)
    l3.reset()
    assert l3.try_acquire(0).allowed is True


def test_token_bucket():
    l = TokenBucketLimiter(2, 1 / 1000)
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(0).allowed is False
    r = l.try_acquire(1000)
    assert r.allowed is True

    l2 = TokenBucketLimiter(1, 0.001)
    l2.try_acquire(0)
    r2 = l2.try_acquire(0)
    assert r2.allowed is False
    assert (r2.retry_after_ms or 0) > 0

    l3 = TokenBucketLimiter(1, 1)
    l3.try_acquire(0)
    l3.reset()
    assert l3.try_acquire(0).allowed is True


def test_leaky_bucket():
    l = LeakyBucketLimiter(2, 0)
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(0).allowed is True
    assert l.try_acquire(0).allowed is False

    l2 = LeakyBucketLimiter(1, 0.001)
    assert l2.try_acquire(0).allowed is True
    assert l2.try_acquire(0).allowed is False
    assert l2.try_acquire(2000).allowed is True

    l3 = LeakyBucketLimiter(1, 0)
    l3.try_acquire(0)
    l3.reset()
    assert l3.try_acquire(0).allowed is True
