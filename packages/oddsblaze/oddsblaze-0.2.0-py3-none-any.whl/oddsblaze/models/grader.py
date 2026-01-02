"""Models for the Grader API endpoint."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .base import Selection


class GradedTeam(BaseModel):
    """A team with score in a graded event."""

    name: str = Field(description="Team name")
    score: int = Field(description="Final score")


class GradedTeams(BaseModel):
    """Away and home teams with scores."""

    away: GradedTeam = Field(description="Away team score info")
    home: GradedTeam = Field(description="Home team score info")


class GradedEvent(BaseModel):
    """Event information for bet grading."""

    id: str = Field(description="Event identifier")
    teams: GradedTeams = Field(description="Teams and scores")
    status: str = Field(description="Event status (e.g., 'Final')")


class GradedPlayer(BaseModel):
    """Player information for bet grading."""

    id: str = Field(description="Player identifier")
    score: Optional[int] = Field(
        default=None, description="Player's stat score if applicable"
    )


class GraderResponse(BaseModel):
    """Response from the Grader API endpoint."""

    id: str = Field(description="The graded odds ID")
    event: GradedEvent = Field(description="Event information")
    market: str = Field(description="Market name")
    name: str = Field(description="Selection name")
    selection: Optional[Selection] = Field(
        default=None, description="Parsed selection details"
    )
    player: Optional[GradedPlayer] = Field(
        default=None, description="Player score info for prop bets"
    )
    result: Literal["Win", "Lose", "Push"] = Field(description="Bet result")
