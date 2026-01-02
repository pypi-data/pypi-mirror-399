"""Models for the Active Markets API endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field


class Market(BaseModel):
    """An active market."""

    id: str = Field(description="Market identifier (e.g., 'Moneyline')")
    name: str = Field(description="Display name")
    sportsbooks: list[str] = Field(
        default=[], description="List of sportsbook IDs supporting this market"
    )


class LeagueMarkets(BaseModel):
    """A league with its active markets."""

    id: str = Field(description="League identifier")
    name: str = Field(description="League name")
    sport: str = Field(description="Sport name")
    markets: list[Market] = Field(
        default=[], description="Active markets in this league"
    )


class ActiveMarketsResponse(BaseModel):
    """Response from the Active Markets API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    leagues: list[LeagueMarkets] = Field(
        default=[], description="List of leagues and their markets"
    )
