"""Models for the Odds API endpoint."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .base import League, Links, Player, Selection, Sportsbook, Teams


class Odd(BaseModel):
    """Individual odds line."""

    id: str = Field(description="Unique odds identifier")
    market: str = Field(description="Market name (e.g., 'Moneyline')")
    name: str = Field(description="Selection name (e.g., 'Celtics')")
    price: str = Field(description="Odds price in configured format")
    main: Optional[bool] = Field(
        default=None, description="Whether this is a main line"
    )
    links: Optional[Links] = Field(default=None, description="Deep links to bet slip")
    sgp: Optional[str] = Field(default=None, description="Same Game Parlay identifier")
    selection: Optional[Selection] = Field(
        default=None, description="Parsed selection details"
    )
    player: Optional[Player] = Field(default=None, description="Player info for props")
    updated: Optional[datetime] = Field(
        default=None, description="When this line was last updated"
    )


class Event(BaseModel):
    """A sporting event with associated odds."""

    id: str = Field(description="Unique event identifier")
    teams: Teams = Field(description="Participating teams")
    date: datetime = Field(description="Event start time (UTC)")
    live: bool = Field(description="Whether the event is currently live")
    odds: list[Odd] = Field(default=[], description="List of odds for this event")


class OddsResponse(BaseModel):
    """Response from the Odds API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    league: League = Field(description="League information")
    sportsbook: Sportsbook = Field(description="Sportsbook information")
    events: list[Event] = Field(default=[], description="List of events with odds")
