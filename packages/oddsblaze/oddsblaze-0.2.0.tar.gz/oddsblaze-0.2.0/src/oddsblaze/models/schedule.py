"""Models for the Schedule API endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import League, Teams


class ScheduleEvent(BaseModel):
    """A scheduled sporting event."""

    id: str = Field(description="Unique event identifier")
    teams: Teams = Field(description="Participating teams")
    date: datetime = Field(description="Event start time (UTC)")
    live: bool = Field(description="Whether the event is currently live")


class ScheduleResponse(BaseModel):
    """Response from the Schedule API endpoint."""

    updated: datetime = Field(description="Response generation timestamp")
    league: League = Field(description="League information")
    events: list[ScheduleEvent] = Field(
        default=[], description="List of scheduled events"
    )
