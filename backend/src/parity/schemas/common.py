"""Shared strict value objects for the public API."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, StringConstraints, model_validator

DecimalString = Annotated[
    str,
    StringConstraints(pattern=r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$"),
]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]


class StrictModel(BaseModel):
    """Reject undeclared fields at every external boundary."""

    model_config = ConfigDict(extra="forbid")


class Classification(StrEnum):
    OBSERVED = "observed"
    MODEL_ESTIMATED = "model_estimated"
    SIMULATED = "simulated"
    USER_PROVIDED = "user_provided"
    ADJUSTED = "adjusted"
    UNAVAILABLE = "unavailable"


class Unit(StrEnum):
    PROBABILITY = "probability"
    USD_PER_CONTRACT = "usd_per_contract"
    USD_TOTAL = "usd_total"


class SourceKind(StrEnum):
    USER_INPUT = "user_input"
    PUBLIC_API = "public_api"
    OFFICIAL_DOCUMENT = "official_document"
    DETERMINISTIC_FIXTURE = "deterministic_fixture"
    MODEL = "model"


class Source(StrictModel):
    source_id: Annotated[str, Field(min_length=1, max_length=80)]
    source_name: Annotated[str, Field(min_length=1, max_length=160)]
    source_kind: SourceKind
    source_url: AnyUrl | None = None
    observed_at: datetime | None = None
    retrieved_at: datetime | None = None
    effective_at: datetime | None = None
    classification: Classification
    fixture_version: str | None = None
    content_sha256: Sha256 | None = None
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provenance(self) -> Source:
        for name in ("observed_at", "retrieved_at", "effective_at"):
            value = getattr(self, name)
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.classification is Classification.SIMULATED and not self.fixture_version:
            raise ValueError("simulated sources require fixture_version")
        if self.source_kind is SourceKind.DETERMINISTIC_FIXTURE and not self.fixture_version:
            raise ValueError("deterministic fixtures require fixture_version")
        if self.source_url is not None:
            parsed = urlsplit(str(self.source_url))
            if parsed.query or parsed.fragment:
                raise ValueError("source_url must be a fixed public URL without query or fragment")
        return self
