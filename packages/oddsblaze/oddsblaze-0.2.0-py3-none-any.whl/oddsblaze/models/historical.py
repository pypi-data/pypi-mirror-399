"""Models for the Historical Odds API endpoint."""

from datetime import datetime, timezone
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

from .base import Selection


def _ms_to_datetime(v: int | datetime) -> datetime:
    """Convert millisecond timestamp to UTC datetime."""
    if isinstance(v, datetime):
        return v
    return datetime.fromtimestamp(v / 1000, tz=timezone.utc)


# Type alias for millisecond timestamps that become datetimes
TimestampMs = Annotated[datetime, BeforeValidator(_ms_to_datetime)]


class PricePoint(BaseModel):
    """A price at a specific timestamp (CLV/OLV)."""

    price: str = Field(description="The odds price")
    timestamp: TimestampMs = Field(description="Timestamp of the price")


class TimeSeriesEntry(BaseModel):
    """An entry in the line movement history."""

    price: Optional[str] = Field(
        default=None, description="The odds price at this time"
    )
    locked: bool = Field(description="Whether the odds were locked/suspended")
    timestamp: TimestampMs = Field(description="Timestamp of the update")


class HistoricalResponse(BaseModel):
    """Response from the Historical Odds API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    id: str = Field(description="The odds ID")
    market: str = Field(description="Market name")
    name: str = Field(description="Selection name")
    selection: Optional[Selection] = Field(
        default=None, description="Parsed selection details"
    )
    olv: Optional[PricePoint] = Field(default=None, description="Opening Line Value")
    clv: Optional[PricePoint] = Field(default=None, description="Closing Line Value")
    entries: list[TimeSeriesEntry] = Field(
        default=[], description="Line movement history"
    )
