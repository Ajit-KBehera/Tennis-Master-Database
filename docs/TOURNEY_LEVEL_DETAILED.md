# Tournament Level Codes - Detailed Documentation

## Overview
The `tourney_level` field categorizes tournaments by their importance, prize money, and tour hierarchy. The coding system differs between ATP and WTA tours, with some overlap.

## ATP Tournament Levels

### Main Tour Levels
- **G** (Grand Slams): 38,513 matches
  - The four major tournaments: Australian Open, French Open, Wimbledon, US Open
  - Highest prize money and ranking points

- **M** (Masters 1000): 28,061 matches  
  - ATP Masters 1000 series (formerly ATP Masters Series)
  - 9 mandatory tournaments for top players
  - High prize money and ranking points

- **A** (ATP Tour): 143,379 matches
  - Regular ATP Tour events (250, 500 level tournaments)
  - ATP 250, ATP 500 series events
  - Mid-tier prize money and ranking points

- **C** (Challengers): 192,692 matches
  - ATP Challenger Tour events
  - Lower prize money, important for players ranking 100-300
  - Development circuit for up-and-coming players

### Special Events
- **D** (Davis Cup): 14,790 matches
  - International team competition
  - National team events

- **F** (Tour Finals): 594 matches
  - Season-ending championships
  - ATP Finals, Next Gen ATP Finals

- **O** (Other): 64 matches
  - Miscellaneous or unclassified events

## WTA Tournament Levels

### Main Tour Levels
- **G** (Grand Slams): 40,033 matches
  - Same four majors as ATP
  - Highest prize money and ranking points

- **P** (Premier): 17,067 matches
  - WTA Premier events
  - High-tier tournaments with significant prize money

- **PM** (Premier Mandatory): 5,984 matches
  - WTA Premier Mandatory events
  - Most important non-Grand Slam tournaments
  - Mandatory for top players

- **I** (International): 24,377 matches
  - WTA International events
  - Mid-tier tournaments

- **C** (Challengers): 76,405 matches
  - WTA Challenger events
  - Development circuit

### ITF Prize Money Levels (in thousands of dollars)
- **10**: 152,232 matches (ITF $10,000 events)
- **15**: 96,110 matches (ITF $15,000 events)  
- **25**: 120,926 matches (ITF $25,000 events)
- **35**: 10,350 matches (ITF $35,000 events)
- **40**: 2,741 matches (ITF $40,000 events)
- **50**: 25,684 matches (ITF $50,000 events)
- **60**: 15,129 matches (ITF $60,000 events)
- **75**: 10,408 matches (ITF $75,000 events)
- **80**: 3,098 matches (ITF $80,000 events)
- **100**: 9,622 matches (ITF $100,000 events)

### Historical WTA Tier System
- **T1** (Tier I): 7,273 matches
- **T2** (Tier II): 8,091 matches  
- **T3** (Tier III): 7,982 matches
- **T4** (Tier IV): 5,311 matches
- **T5** (Tier V): 1,728 matches

### Special Events
- **W** (WTA Finals): 94,623 matches
  - Season-ending championships
  - WTA Finals, WTA Elite Trophy

- **D** (Fed Cup/Billie Jean King Cup): 26,964 matches
  - International team competition
  - National team events

- **E** (Exhibition): 283 matches
  - Non-sanctioned events
  - Exhibition matches

- **J** (Juniors): 6 matches
  - Junior tournaments

- **CC** (Challenger Circuit): 1,913 matches
  - Additional challenger events

## Data Coverage by Source

### ATP (418,093 matches)
- Dominated by Challengers (46%) and ATP Tour events (34%)
- Strong representation of Grand Slams (9%) and Masters 1000 (7%)
- Significant Davis Cup presence (4%)

### WTA (751,977 matches)  
- Heavy ITF circuit representation (various prize money levels)
- Strong WTA Finals presence (13%)
- Good Grand Slam coverage (5%)
- Historical tier system well represented

### Slam Point-by-Point (13,154 matches)
- All Grand Slam events
- No tourney_level values (all null/empty)

## Key Insights

1. **ITF Circuit Dominance**: The WTA dataset includes extensive ITF circuit coverage, explaining the high number of low-prize-money events.

2. **Challenger Circuit**: Both tours have significant Challenger representation, crucial for player development.

3. **Historical Evolution**: The WTA tier system (T1-T5) represents older tournament classifications, while current system uses Premier/International designations.

4. **Team Events**: Both tours include significant team competition data (Davis Cup, Fed Cup).

5. **Prize Money Progression**: ITF levels show clear progression from $10K to $100K events, representing the development pathway for professional tennis.

## Usage Notes
- When analyzing tournament importance, consider the hierarchy: G > M/PM > A/P > I > C > ITF levels
- ITF prize money levels are cumulative (higher numbers = more important)
- Historical tier system (T1-T5) should be considered alongside current Premier/International system
- Team events (D) represent different competition format than individual tournaments
