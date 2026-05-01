from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WindowConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    window_ms: int = Field(alias="windowMs", ge=1, le=86_400_000)
    max_requests: int = Field(alias="maxRequests", ge=1, le=1_000_000)


class TokenBucketConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    capacity: int = Field(ge=1, le=1_000_000)
    refill_per_second: float = Field(alias="refillPerSecond", gt=0, le=1_000_000)


class LeakyBucketConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    capacity: int = Field(ge=1, le=1_000_000)
    leak_per_second: float = Field(alias="leakPerSecond", gt=0, le=1_000_000)


class SimulateFixedWindow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["fixedWindow"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    request_count: int = Field(alias="requestCount", ge=1, le=10_000)
    interval_ms: int | None = Field(default=None, alias="intervalMs")
    config: WindowConfig

    @field_validator("interval_ms")
    @classmethod
    def interval_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 0 or v > 60_000:
            raise ValueError("intervalMs must be between 0 and 60000")
        return v


class SimulateSlidingWindow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["slidingWindow"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    request_count: int = Field(alias="requestCount", ge=1, le=10_000)
    interval_ms: int | None = Field(default=None, alias="intervalMs")
    config: WindowConfig

    @field_validator("interval_ms")
    @classmethod
    def interval_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 0 or v > 60_000:
            raise ValueError("intervalMs must be between 0 and 60000")
        return v


class SimulateTokenBucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["tokenBucket"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    request_count: int = Field(alias="requestCount", ge=1, le=10_000)
    interval_ms: int | None = Field(default=None, alias="intervalMs")
    config: TokenBucketConfig

    @field_validator("interval_ms")
    @classmethod
    def interval_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 0 or v > 60_000:
            raise ValueError("intervalMs must be between 0 and 60000")
        return v


class SimulateLeakyBucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["leakyBucket"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    request_count: int = Field(alias="requestCount", ge=1, le=10_000)
    interval_ms: int | None = Field(default=None, alias="intervalMs")
    config: LeakyBucketConfig

    @field_validator("interval_ms")
    @classmethod
    def interval_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 0 or v > 60_000:
            raise ValueError("intervalMs must be between 0 and 60000")
        return v


SimulateBody = Annotated[
    Union[
        SimulateFixedWindow,
        SimulateSlidingWindow,
        SimulateTokenBucket,
        SimulateLeakyBucket,
    ],
    Field(discriminator="algorithm"),
]


class TryFixedWindow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["fixedWindow"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    now_ms: float | None = Field(default=None, alias="nowMs")
    config: WindowConfig

    @field_validator("now_ms")
    @classmethod
    def now_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("nowMs must be non-negative")
        return v


class TrySlidingWindow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["slidingWindow"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    now_ms: float | None = Field(default=None, alias="nowMs")
    config: WindowConfig

    @field_validator("now_ms")
    @classmethod
    def now_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("nowMs must be non-negative")
        return v


class TryTokenBucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["tokenBucket"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    now_ms: float | None = Field(default=None, alias="nowMs")
    config: TokenBucketConfig

    @field_validator("now_ms")
    @classmethod
    def now_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("nowMs must be non-negative")
        return v


class TryLeakyBucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    algorithm: Literal["leakyBucket"]
    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    now_ms: float | None = Field(default=None, alias="nowMs")
    config: LeakyBucketConfig

    @field_validator("now_ms")
    @classmethod
    def now_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("nowMs must be non-negative")
        return v


TryBody = Annotated[
    Union[TryFixedWindow, TrySlidingWindow, TryTokenBucket, TryLeakyBucket],
    Field(discriminator="algorithm"),
]


class ResetBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    client_id: str = Field(alias="clientId", min_length=1, max_length=256)
    algorithm: (
        Literal["fixedWindow", "slidingWindow", "tokenBucket", "leakyBucket"] | None
    ) = None
