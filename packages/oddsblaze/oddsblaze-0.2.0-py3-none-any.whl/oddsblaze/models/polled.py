"""Models for the Last Polled API endpoint."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def _ms_to_datetime(v: int | datetime) -> datetime:
    """Convert millisecond timestamp to UTC datetime."""
    if isinstance(v, datetime):
        return v
    return datetime.fromtimestamp(v / 1000, tz=timezone.utc)


TimestampMs = Annotated[datetime, BeforeValidator(_ms_to_datetime)]


class PolledSportsbook(BaseModel):
    """A sportsbook's last polled status."""

    id: str = Field(description="Sportsbook identifier")
    name: str = Field(description="Sportsbook name")
    timestamp: TimestampMs = Field(description="Last poll timestamp")
    last: int = Field(description="Seconds elapsed since last poll")


class PolledLeague(BaseModel):
    """A league with polled sportsbooks."""

    id: str = Field(description="League identifier")
    name: str = Field(description="League name")
    sportsbooks: list[PolledSportsbook] = Field(
        default=[], description="Poll status per sportsbook"
    )


class PolledResponse(BaseModel):
    """Response from the Last Polled API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    leagues: list[PolledLeague] = Field(
        default=[], description="List of leagues and poll statuses"
    )
