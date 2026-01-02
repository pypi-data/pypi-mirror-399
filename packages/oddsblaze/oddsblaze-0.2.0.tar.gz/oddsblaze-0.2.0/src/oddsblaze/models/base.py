"""Base Pydantic models shared across multiple endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class League(BaseModel):
    """A sports league."""

    id: str = Field(description="Unique identifier (e.g., 'nba', 'nfl')")
    name: str = Field(description="Full league name")
    sport: str = Field(description="Sport name (e.g., 'Basketball')")


class Sportsbook(BaseModel):
    """A sportsbook."""

    id: str = Field(description="Unique identifier (e.g., 'draftkings')")
    name: str = Field(description="Display name")
    sgp: Optional[bool] = Field(
        default=None, description="Whether Same Game Parlay is supported"
    )


class Team(BaseModel):
    """A team."""

    id: str = Field(description="Unique team identifier")
    name: str = Field(description="Full team name")
    abbreviation: Optional[str] = Field(
        default=None, description="Team abbreviation (e.g., 'BOS')"
    )


class Teams(BaseModel):
    """Away and home teams for an event."""

    away: Team = Field(description="Away team")
    home: Team = Field(description="Home team")


class Player(BaseModel):
    """A player with team information."""

    id: str = Field(description="Unique player identifier")
    name: str = Field(description="Full player name")
    position: Optional[str] = Field(default=None, description="Player position")
    number: Optional[str] = Field(default=None, description="Jersey number")
    team: Optional[Team] = Field(default=None, description="Player's team")


class Selection(BaseModel):
    """Betting selection details."""

    name: Optional[str] = Field(
        default=None, description="Selection name (e.g., 'Over', 'Lakers')"
    )
    side: Optional[str] = Field(
        default=None, description="Selection side ('Over', 'Under', 'Home', 'Away')"
    )
    line: Optional[float] = Field(default=None, description="Handicap or total line")


class Links(BaseModel):
    """Deep links to sportsbook betting slip."""

    desktop: Optional[str] = Field(default=None, description="Desktop web deep link")
    mobile: Optional[str] = Field(default=None, description="Mobile app deep link")
