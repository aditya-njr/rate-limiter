import json
import time
from typing import Any

from fastapi import APIRouter, Request, Response, status

from app.limiters.types import RateLimitResult
from app.models.schemas import ResetBody, SimulateBody, TryBody
from app.services.factory import create_limiter

router = APIRouter()


def _result_row(index: int, now_ms: float, r: RateLimitResult) -> dict[str, Any]:
    row: dict[str, Any] = {"index": index, "nowMs": now_ms, "allowed": r.allowed}
    if r.retry_after_ms is not None:
        row["retryAfterMs"] = r.retry_after_ms
    if r.remaining is not None:
        row["remaining"] = r.remaining
    return row


def _config_dict(body: SimulateBody | TryBody) -> dict[str, Any]:
    return body.config.model_dump(mode="json", by_alias=True)


@router.post("/simulate")
def simulate(request: Request, body: SimulateBody) -> dict[str, Any]:
    limiter = create_limiter(body.algorithm, _config_dict(body))
    interval = 0 if body.interval_ms is None else body.interval_ms
    results: list[dict[str, Any]] = []
    for i in range(body.request_count):
        now_ms = float(i * interval)
        r = limiter.try_acquire(now_ms)
        results.append(_result_row(i, now_ms, r))

    allowed = sum(1 for x in results if x["allowed"])
    return {
        "algorithm": body.algorithm,
        "clientId": body.client_id,
        "summary": {
            "total": len(results),
            "allowed": allowed,
            "rejected": len(results) - allowed,
        },
        "results": results,
    }


@router.post("/try")
def try_acquire(request: Request, body: TryBody) -> Response:
    registry = request.app.state.registry
    limiter = registry.get_or_create(
        body.algorithm, body.client_id, _config_dict(body)
    )
    now_ms = time.time() * 1000.0 if body.now_ms is None else float(body.now_ms)
    r = limiter.try_acquire(now_ms)
    payload = {
        "allowed": r.allowed,
        "algorithm": body.algorithm,
        "clientId": body.client_id,
    }
    if r.retry_after_ms is not None:
        payload["retryAfterMs"] = r.retry_after_ms
    if r.remaining is not None:
        payload["remaining"] = r.remaining
    code = status.HTTP_200_OK if r.allowed else status.HTTP_429_TOO_MANY_REQUESTS
    return Response(
        content=json.dumps(payload),
        media_type="application/json",
        status_code=code,
    )


@router.post("/reset")
def reset(request: Request, body: ResetBody) -> dict[str, int]:
    registry = request.app.state.registry
    removed = registry.reset(body.client_id, body.algorithm)
    return {"removed": removed}
