# Async Examples

For concurrent requests across multiple sportsbooks, use `AsyncOddsblazeClient`.

## Basic Usage

```python
import asyncio
from oddsblaze import AsyncOddsblazeClient


async def main():
    async with AsyncOddsblazeClient() as client:
        # All methods are async
        odds = await client.get_odds("draftkings", "nba")
        schedule = await client.get_schedule("nfl")
        consensus = await client.get_consensus("nba", "moneyline")


asyncio.run(main())
```

---

## Concurrent Requests

### Multiple Leagues

```python
import asyncio
from oddsblaze import AsyncOddsblazeClient


async def main():
    async with AsyncOddsblazeClient() as client:
        # Fetch multiple leagues concurrently
        nba, nfl, nhl = await asyncio.gather(
            client.get_odds("draftkings", "nba"),
            client.get_odds("draftkings", "nfl"),
            client.get_odds("draftkings", "nhl"),
        )
        
        print(f"NBA events: {len(nba.events)}")
        print(f"NFL events: {len(nfl.events)}")
        print(f"NHL events: {len(nhl.events)}")


asyncio.run(main())
```

---

## Query All Sportsbooks

Get odds from every sportsbook concurrently - useful for finding the best price:

```python
import asyncio
from oddsblaze import AsyncOddsblazeClient, OddsblazeClient


async def get_q1_totals_all_books():
    """Get 1st Quarter Total Points from all sportsbooks concurrently."""
    
    # Use sync client for initial setup
    sync_client = OddsblazeClient()
    schedule = sync_client.get_schedule("nba", live=False)
    sportsbooks = sync_client.get_sportsbooks()
    sync_client.close()
    
    if not schedule.events:
        print("No upcoming games")
        return
    
    game = schedule.events[0]
    print(f"Game: {game.teams.away.name} @ {game.teams.home.name}")
    
    async with AsyncOddsblazeClient() as client:
        async def fetch_odds(sb):
            try:
                odds = await client.get_odds(
                    sb.id,
                    "nba",
                    event=game.id,
                    market="1st Quarter Total Points",
                    main=True,
                )
                if odds.events and odds.events[0].odds:
                    return (sb.name, odds.events[0].odds)
            except Exception:
                pass
            return None
        
        # Run all requests concurrently
        results = await asyncio.gather(*[fetch_odds(sb) for sb in sportsbooks])
        
        for result in results:
            if result:
                name, odds = result
                print(f"\n{name}:")
                for odd in odds:
                    print(f"  {odd.name}: {odd.price}")


asyncio.run(get_q1_totals_all_books())
```

**Sample output:**

```
Game: Golden State Warriors @ Toronto Raptors

Bally Bet:
  Over 55.5: -107
  Under 55.5: -122

bet365:
  Over 54.5: -110
  Under 54.5: -110

DraftKings:
  Over 55.5: -110
  Under 55.5: -110

FanDuel:
  Over 55.5: -106
  Under 55.5: -120

Pinnacle:
  Over 55.5: -114
  Under 55.5: -104
```
