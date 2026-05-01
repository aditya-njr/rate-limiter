import json
from typing import Any

from app.services.factory import create_limiter


def _registry_key(algorithm: str, client_id: str, config: dict[str, Any]) -> str:
    payload = {"algorithm": algorithm, "clientId": client_id, "config": config}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class LimiterRegistry:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get_or_create(self, algorithm: str, client_id: str, config: dict[str, Any]):
        key = _registry_key(algorithm, client_id, config)
        if key not in self._store:
            self._store[key] = create_limiter(algorithm, config)
        return self._store[key]

    def reset(self, client_id: str, algorithm: str | None = None) -> int:
        removed = 0
        for key in list(self._store.keys()):
            parsed = json.loads(key)
            if parsed["clientId"] == client_id and (
                algorithm is None or parsed["algorithm"] == algorithm
            ):
                del self._store[key]
                removed += 1
        return removed
