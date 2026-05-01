"""Allowed browser origins (parity with server/src/config/cors.ts)."""

from app.config import settings


def get_allowed_origins() -> list[str]:
    from_env = [s.strip() for s in (settings.client_origin or "").split(",") if s.strip()]

    dev_defaults: list[str] = []
    if settings.environment == "production":
        dev_defaults = []
    else:
        dev_defaults = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://[::1]:5173",
        ]

    merged = list(dict.fromkeys([*from_env, *dev_defaults]))
    return merged


def is_origin_allowed(origin: str | None, allowed: list[str]) -> bool:
    if not origin:
        return True
    return origin in allowed
