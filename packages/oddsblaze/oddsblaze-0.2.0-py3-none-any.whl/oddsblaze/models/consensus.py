"""Models for the Consensus Odds API endpoint."""

from datetime import datetime, timezone
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

from .base import League, Player, Selection, Sportsbook, Teams


def _ms_to_datetime(v: int | datetime) -> datetime:
    """Convert millisecond timestamp to UTC datetime."""
    if isinstance(v, datetime):
        return v
    return datetime.fromtimestamp(v / 1000, tz=timezone.utc)


TimestampMs = Annotated[datetime, BeforeValidator(_ms_to_datetime)]


class SportsbookPrice(BaseModel):
    """A sportsbook's price for consensus odds."""

    name: str = Field(description="Sportsbook name")
    price: str = Field(description="Odds price")
    timestamp: TimestampMs = Field(description="Last update timestamp")


class ConsensusOdd(BaseModel):
    """Individual consensus odds line with sportsbook breakdown."""

    id: str = Field(description="Consensus odds ID")
    market: str = Field(description="Market name")
    name: str = Field(description="Selection name")
    price: str = Field(description="Consensus price (average or best available)")
    selection: Optional[Selection] = Field(
        default=None, description="Parsed selection details"
    )
    player: Optional[Player] = Field(default=None, description="Player details")
    sportsbooks: list[SportsbookPrice] = Field(
        default=[], description="Prices from individual sportsbooks"
    )


class ConsensusEvent(BaseModel):
    """A sporting event with consensus odds."""

    id: str = Field(description="Event identifier")
    teams: Teams = Field(description="Participating teams")
    date: datetime = Field(description="Event start time (UTC)")
    live: bool = Field(description="Whether event is live")
    odds: list[ConsensusOdd] = Field(default=[], description="List of consensus odds")


class ConsensusResponse(BaseModel):
    """Response from the Consensus Odds API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    league: League = Field(description="League information")
    sportsbook: Sportsbook = Field(description="Sportsbook information (Consensus)")
    events: list[ConsensusEvent] = Field(default=[], description="List of events")
