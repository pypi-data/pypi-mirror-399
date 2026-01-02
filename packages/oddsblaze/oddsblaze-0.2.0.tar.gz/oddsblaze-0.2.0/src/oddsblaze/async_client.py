"""Async OddsBlaze API client."""

from typing import Any, Optional

import httpx

from .exceptions import AuthenticationError, raise_for_error_message
from .models import (
    ActiveMarketsResponse,
    ConsensusResponse,
    GraderResponse,
    HistoricalResponse,
    League,
    OddsResponse,
    PolledResponse,
    ScheduleResponse,
    Sportsbook,
)
from .settings import OddsblazeSettings, PriceFormat, get_settings


class AsyncOddsblazeClient:
    """Asynchronous client for the OddsBlaze API."""

    BASE_URL = "https://api.oddsblaze.com/v2"
    ODDS_URL = "https://odds.oddsblaze.com"
    HISTORICAL_URL = "https://historical.oddsblaze.com"
    GRADER_URL = "https://grader.oddsblaze.com"
    POLLED_URL = "https://polled.oddsblaze.com"

    def __init__(
        self,
        settings: Optional[OddsblazeSettings] = None,
        timeout: float = 30.0,
    ):
        self.settings = settings or get_settings()
        self._client = httpx.AsyncClient(timeout=timeout)

    def _require_api_key(self) -> str:
        """Get API key or raise AuthenticationError."""
        if self.settings.api_key:
            return self.settings.api_key
        raise AuthenticationError(
            "ODDSBLAZE_API_KEY is required; set it in env, .env, or ~/.oddsblaze"
        )

    def _build_params(self, require_auth: bool = True, **kwargs: Any) -> dict[str, str]:
        """Build query parameters, handling auth and filtering None values."""
        params: dict[str, str] = {}

        if require_auth:
            params["key"] = self._require_api_key()
        elif self.settings.api_key:
            params["key"] = self.settings.api_key

        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, bool):
                params[key] = "true" if value else "false"
            elif isinstance(value, list):
                params[key] = ",".join(str(v) for v in value)
            elif isinstance(value, PriceFormat):
                params[key] = value.value
            else:
                params[key] = str(value)

        return params

    async def _request(self, url: str, params: dict[str, str]) -> Any:
        """Make async GET request and handle errors."""
        response = await self._client.get(url, params=params)

        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid or expired API key. Get a new key at oddsblaze.com"
            )

        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "message" in data and len(data) == 1:
            raise_for_error_message(data["message"])

        return data

    # -------------------------------------------------------------------------
    # Odds API
    # -------------------------------------------------------------------------
    async def get_odds(
        self,
        sportsbook: str,
        league: str,
        *,
        market: Optional[str | list[str]] = None,
        market_contains: Optional[str | list[str]] = None,
        price: Optional[PriceFormat] = None,
        event: Optional[str | list[str]] = None,
        main: Optional[bool] = None,
        live: Optional[bool] = None,
    ) -> OddsResponse:
        """
        Get real-time odds for a sportsbook and league.

        Args:
            sportsbook: Sportsbook ID (e.g., "draftkings")
            league: League ID (e.g., "nfl")
            market: Market ID(s) or name(s) to filter
            market_contains: Filter markets containing these strings
            price: Price format (defaults to settings)
            event: Event ID(s) to filter
            main: True for main lines only, False for alternates only
            live: True for live events only, False for pre-match only
        """
        params = self._build_params(
            require_auth=True,
            sportsbook=sportsbook,
            league=league,
            market=market,
            market_contains=market_contains,
            price=price or self.settings.price_format,
            event=event,
            main=main,
            live=live,
        )
        data = await self._request(self.ODDS_URL, params)
        return OddsResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Historical Odds API
    # -------------------------------------------------------------------------
    async def get_historical(
        self,
        odds_id: str,
        *,
        price: Optional[PriceFormat] = None,
        time_series: bool = False,
        locked: bool = False,
    ) -> HistoricalResponse:
        """
        Get historical odds with CLV, OLV, and line movement.

        Args:
            odds_id: The odds ID from a previous odds response
            price: Price format (defaults to settings)
            time_series: Include line movement history
            locked: Include locked odds in time series
        """
        params = self._build_params(
            require_auth=True,
            id=odds_id,
            price=price or self.settings.price_format,
        )
        if time_series:
            params["time_series"] = ""
        if locked:
            params["locked"] = ""

        data = await self._request(self.HISTORICAL_URL, params)
        return HistoricalResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Consensus Odds API
    # -------------------------------------------------------------------------
    async def get_consensus(
        self,
        league: str,
        market: str,
        *,
        price: Optional[PriceFormat] = None,
        dedupe: Optional[bool] = None,
        sportsbooks: Optional[list[str]] = None,
        required_sportsbooks: Optional[list[str]] = None,
        weights: Optional[dict[str, float]] = None,
    ) -> ConsensusResponse:
        """
        Get consensus odds across sportsbooks.

        Args:
            league: League ID (e.g., "nfl")
            market: Market ID (e.g., "point-spread")
            price: Price format (defaults to settings)
            dedupe: Remove duplicate prices (default True)
            sportsbooks: Sportsbooks to include (at least one must have odds)
            required_sportsbooks: Sportsbooks that must all be present
            weights: Custom weights by sportsbook ID (e.g., {"draftkings": 1.5})
        """
        params = self._build_params(
            require_auth=True,
            price=price or self.settings.price_format,
            dedupe=dedupe,
            sportsbooks=sportsbooks,
        )

        if required_sportsbooks:
            params["required-sportsbooks"] = ",".join(required_sportsbooks)

        if weights:
            for book_id, weight in weights.items():
                params[f"weight-{book_id}"] = str(weight)

        url = f"{self.BASE_URL}/consensus/{league}/{market}.json"
        data = await self._request(url, params)
        return ConsensusResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Grader API
    # -------------------------------------------------------------------------
    async def grade_bet(
        self,
        odds_id: str,
        *,
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a bet (Win, Lose, or Push).

        Args:
            odds_id: The odds ID to grade
            live: Grade while event is still in progress
        """
        params = self._build_params(require_auth=True, id=odds_id)
        if live:
            params["live"] = ""

        data = await self._request(self.GRADER_URL, params)
        return GraderResponse.model_validate(data)

    async def grade_moneyline(
        self,
        sportsbook: str,
        event_id: str,
        team: str,
        *,
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a moneyline bet.

        Args:
            sportsbook: Sportsbook name (e.g., "FanDuel", "DraftKings")
            event_id: Event ID (UUID)
            team: Team name (e.g., "Boston Celtics")
            live: Grade while event is still in progress
        """
        odds_id = f"{sportsbook}#{event_id}#Moneyline#{team}"
        return await self.grade_bet(odds_id, live=live)

    async def grade_spread(
        self,
        sportsbook: str,
        event_id: str,
        team: str,
        line: float,
        *,
        market: str = "Point Spread",
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a point spread bet.

        Args:
            sportsbook: Sportsbook name (e.g., "FanDuel", "DraftKings")
            event_id: Event ID (UUID)
            team: Team name (e.g., "Boston Celtics")
            line: The spread line (e.g., -2.5 or +2.5)
            market: Market name (default "Point Spread", or "1st Quarter Point Spread")
            live: Grade while event is still in progress
        """
        # Format line with sign (e.g., -2.5 or +2.5)
        if line >= 0:
            name = f"{team} +{line}"
        else:
            name = f"{team} {line}"
        odds_id = f"{sportsbook}#{event_id}#{market}#{name}"
        return await self.grade_bet(odds_id, live=live)

    async def grade_total(
        self,
        sportsbook: str,
        event_id: str,
        side: str,
        line: float,
        *,
        market: str = "Total Points",
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a total points bet.

        Args:
            sportsbook: Sportsbook name (e.g., "FanDuel", "DraftKings")
            event_id: Event ID (UUID)
            side: "Over" or "Under"
            line: The total line (e.g., 229.5)
            market: Market name (default "Total Points", or "1st Quarter Total Points")
            live: Grade while event is still in progress
        """
        name = f"{side} {line}"
        odds_id = f"{sportsbook}#{event_id}#{market}#{name}"
        return await self.grade_bet(odds_id, live=live)

    async def grade_yes_no(
        self,
        sportsbook: str,
        event_id: str,
        market: str,
        selection: str,
        *,
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a Yes/No or simple selection bet.

        Args:
            sportsbook: Sportsbook name (e.g., "FanDuel", "DraftKings")
            event_id: Event ID (UUID)
            market: Market name (e.g., "Overtime?", "Total Points Odd/Even")
            selection: The selection (e.g., "Yes", "No", "Odd", "Even")
            live: Grade while event is still in progress
        """
        odds_id = f"{sportsbook}#{event_id}#{market}#{selection}"
        return await self.grade_bet(odds_id, live=live)

    async def grade_player_bet(
        self,
        sportsbook: str,
        event_id: str,
        market: str,
        player_name: str,
        player_id: str,
        side: str,
        line: float,
        *,
        live: bool = False,
    ) -> GraderResponse:
        """
        Grade a player prop bet.

        Builds the odds ID automatically from the provided components.

        Args:
            sportsbook: Sportsbook name (e.g., "FanDuel", "DraftKings")
            event_id: Event ID (UUID)
            market: Market name (e.g., "Player Points", "Player Rebounds")
            player_name: Player's name (e.g., "Jaylen Brown")
            player_id: Player's UUID (from a previous get_odds() call)
            side: Selection side ("Over" or "Under")
            line: The betting line (e.g., 22.5)
            live: Grade while event is still in progress
        """
        name = f"{player_name} {side} {line}"
        odds_id = f"{sportsbook}#{event_id}#{market}#{name}#{player_id}"
        return await self.grade_bet(odds_id, live=live)

    # -------------------------------------------------------------------------
    # Schedule API
    # -------------------------------------------------------------------------
    async def get_schedule(
        self,
        league: str,
        *,
        event_id: Optional[str | list[str]] = None,
        team: Optional[str | list[str]] = None,
        date: Optional[str | list[str]] = None,
        live: Optional[bool] = None,
    ) -> ScheduleResponse:
        """
        Get upcoming and live events.

        Args:
            league: League ID (e.g., "nfl")
            event_id: Event ID(s) to filter
            team: Team ID(s), name(s), or abbreviation(s) to filter
            date: Date(s) in YYYY-MM-DD format, or range YYYY-MM-DD-YYYY-MM-DD
            live: True for live only, False for pre-match only
        """
        params = self._build_params(
            require_auth=True,
            id=event_id,
            team=team,
            date=date,
            live=live,
        )
        url = f"{self.BASE_URL}/schedule/{league}.json"
        data = await self._request(url, params)
        return ScheduleResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Leagues API (no auth required)
    # -------------------------------------------------------------------------
    async def get_leagues(self) -> list[League]:
        """Get all available leagues."""
        params = self._build_params(require_auth=False)
        url = f"{self.BASE_URL}/leagues.json"
        data = await self._request(url, params)
        return [League.model_validate(item) for item in data]

    # -------------------------------------------------------------------------
    # Sportsbooks API (no auth required)
    # -------------------------------------------------------------------------
    async def get_sportsbooks(self) -> list[Sportsbook]:
        """Get all available sportsbooks."""
        params = self._build_params(require_auth=False)
        url = f"{self.BASE_URL}/sportsbooks.json"
        data = await self._request(url, params)
        return [Sportsbook.model_validate(item) for item in data]

    # -------------------------------------------------------------------------
    # Active Markets API (no auth required)
    # -------------------------------------------------------------------------
    async def get_active_markets(self) -> ActiveMarketsResponse:
        """Get active markets across all leagues."""
        params = self._build_params(require_auth=False)
        url = f"{self.BASE_URL}/markets/active.json"
        data = await self._request(url, params)
        return ActiveMarketsResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Last Polled API
    # -------------------------------------------------------------------------
    async def get_last_polled(
        self,
        *,
        league: Optional[str | list[str]] = None,
        sportsbook: Optional[str | list[str]] = None,
        group: bool = False,
    ) -> PolledResponse:
        """
        Get last polled timestamps for odds.

        Args:
            league: League ID(s) to filter
            sportsbook: Sportsbook ID(s) to filter
            group: Group results by sportsbook
        """
        params = self._build_params(
            require_auth=True,
            league=league,
            sportsbook=sportsbook,
        )
        if group:
            params["group"] = ""

        data = await self._request(self.POLLED_URL, params)
        return PolledResponse.model_validate(data)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncOddsblazeClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
