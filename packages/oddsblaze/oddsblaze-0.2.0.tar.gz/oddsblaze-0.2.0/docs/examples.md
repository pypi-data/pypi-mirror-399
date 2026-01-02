# Examples

## Get Odds

### Basic Usage

```python
from oddsblaze import OddsblazeClient

client = OddsblazeClient()

# Get all NFL odds from DraftKings
odds = client.get_odds("draftkings", "nfl")

print(f"Updated: {odds.updated}")
print(f"League: {odds.league.name}")
print(f"Sportsbook: {odds.sportsbook.name}")

for event in odds.events:
    print(f"\n{event.teams.away.name} @ {event.teams.home.name}")
    print(f"  Date: {event.date}")
    print(f"  Live: {event.live}")
```

### Filter by Market

```python
# Single market
odds = client.get_odds("draftkings", "nfl", market="moneyline")

# Multiple markets
odds = client.get_odds("draftkings", "nfl", market=["moneyline", "point-spread"])

# Markets containing a string
odds = client.get_odds("draftkings", "nfl", market_contains="Player")
```

### Filter by Event Type

```python
# Only live events
odds = client.get_odds("draftkings", "nfl", live=True)

# Only pre-match events
odds = client.get_odds("draftkings", "nfl", live=False)

# Only main lines (no alternates)
odds = client.get_odds("draftkings", "nfl", main=True)
```

---

## Get Consensus Odds

```python
# Get consensus point spreads for NFL
consensus = client.get_consensus("nfl", "point-spread")

for event in consensus.events:
    print(f"\n{event.teams.away.name} @ {event.teams.home.name}")
    for odd in event.odds:
        print(f"  {odd.name}: {odd.price}")
        print(f"    Sportsbooks: {len(odd.sportsbooks)}")
        for sb in odd.sportsbooks:
            print(f"      {sb.name}: {sb.price}")
```

### Custom Weights

```python
# Weight Circa higher
consensus = client.get_consensus(
    "nfl",
    "point-spread",
    sportsbooks=["draftkings", "circa", "caesars"],
    weights={"circa": 1.5, "draftkings": 1.0}
)
```

---

## Get Schedule

```python
# Get NFL schedule
schedule = client.get_schedule("nfl")

for event in schedule.events:
    print(f"{event.teams.away.name} @ {event.teams.home.name} - {event.date}")
```

### Filter by Date

```python
# Single date
schedule = client.get_schedule("nfl", date="2025-01-05")

# Date range
schedule = client.get_schedule("nfl", date="2025-01-01-2025-01-31")
```

### Filter by Team

```python
schedule = client.get_schedule("nfl", team="Kansas City Chiefs")
# or by abbreviation
schedule = client.get_schedule("nfl", team="KC")
```

---

## Grade a Bet

Grade completed bets to determine Win, Lose, or Push outcomes.

### Moneyline

```python
result = client.grade_moneyline(
    sportsbook="FanDuel",
    event_id="4d0ff2ce-e788-5cef-887e-b22fba888282",  # Celtics @ Pacers
    team="Boston Celtics",
)
print(f"Result: {result.result}")  # Win
# Final: Celtics 140 - Pacers 122
```

### Point Spread

```python
result = client.grade_spread(
    sportsbook="FanDuel",
    event_id="4d0ff2ce-e788-5cef-887e-b22fba888282",
    team="Boston Celtics",
    line=-2.5,
)
print(f"Result: {result.result}")  # Win (won by 18)

# 1st Quarter Spread
result = client.grade_spread(
    sportsbook="FanDuel",
    event_id="...",
    team="Boston Celtics",
    line=-1.5,
    market="1st Quarter Point Spread",
)
```

### Total Points

```python
# Game Total
result = client.grade_total(
    sportsbook="FanDuel",
    event_id="4d0ff2ce-e788-5cef-887e-b22fba888282",
    side="Over",
    line=229.5,
)
print(f"Result: {result.result}")  # Win (total: 262)

# 1st Quarter Total
result = client.grade_total(
    sportsbook="FanDuel",
    event_id="4d0ff2ce-e788-5cef-887e-b22fba888282",
    side="Over",
    line=54.5,
    market="1st Quarter Total Points",
)
print(f"Result: {result.result}")  # Win (1Q total: 67)
```


### Player Props

```python
# Main line
result = client.grade_player_bet(
    sportsbook="FanDuel",
    event_id="4d0ff2ce-e788-5cef-887e-b22fba888282",
    market="Player Points",
    player_name="Jaylen Brown",
    player_id="58088eea-8ff7-5a7d-933f-dcd558fcde37",
    side="Over",
    line=22.5,
)
print(f"Result: {result.result}")  # Win
print(f"Actual Points: {result.player.score}")  # 30

# Alternate line
result = client.grade_player_bet(
    sportsbook="FanDuel",
    event_id="...",
    market="Player Points",
    player_name="Jaylen Brown",
    player_id="58088eea-8ff7-5a7d-933f-dcd558fcde37",
    side="Over",
    line=29.5,  # Alt line
)

# Other player stats
result = client.grade_player_bet(
    sportsbook="FanDuel",
    event_id="...",
    market="Player Rebounds",
    player_name="Jayson Tatum",
    player_id="...",
    side="Over",
    line=7.5,
)
```

### GraderResponse Fields

```python
result.result          # "Win", "Lose", or "Push"
result.event.status    # "Final"
result.event.teams.away.score  # Score for the relevant period
result.event.teams.home.score
result.selection.side  # "Over" or "Under" (for totals)
result.selection.line  # The line value
result.selection.name  # Team name (for spreads/moneylines)

# For player props only:
result.player.id       # Player UUID
result.player.score    # Actual stat value
```

### Live Grading

```python
# Grade while event is still in progress
result = client.grade_team_bet(..., live=True)
result = client.grade_player_bet(..., live=True)
```

---

## Get Historical Odds

```python
# Get CLV and OLV
historical = client.get_historical(odds_id)

print(f"OLV (Opening): {historical.olv.price}")
print(f"CLV (Closing): {historical.clv.price}")
```

### With Line Movement

```python
historical = client.get_historical(odds_id, time_series=True)

for entry in historical.entries:
    if entry.locked:
        print(f"  LOCKED at {entry.timestamp}")
    else:
        print(f"  {entry.price} at {entry.timestamp}")
```

---

## Metadata Endpoints

### Get Leagues

```python
leagues = client.get_leagues()

for league in leagues:
    print(f"{league.name} ({league.sport})")
```

### Get Sportsbooks

```python
sportsbooks = client.get_sportsbooks()

for sb in sportsbooks:
    print(f"{sb.name} - SGP: {sb.sgp}")
```

### Get Active Markets

```python
markets = client.get_active_markets()

for league in markets.leagues:
    print(f"\n{league.name}:")
    for market in league.markets:
        print(f"  {market.name}: {len(market.sportsbooks)} sportsbooks")
```

### Get Last Polled

```python
polled = client.get_last_polled(league=["nfl", "nba"])

for league in polled.leagues:
    print(f"\n{league.name}:")
    for sb in league.sportsbooks:
        print(f"  {sb.name}: {sb.last}s ago")
```
