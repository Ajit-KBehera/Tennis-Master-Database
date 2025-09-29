# Tennis Master Matches - Column Documentation

This document describes all columns in `tennis_master_matches.csv`, the unified master dataset combining ATP, WTA, Slam, and MatchCharting data.

## Match Identification
- **match_id**: Canonical stable identifier for the match (deterministic hash)
- **source**: Origin of the match record (`atp`, `wta`, `slam_pbp`, `mcp`)
- **tourney_id**: Tournament identifier from source data
- **tourney_name**: Tournament name
- **match_num**: Match number within the tournament

## Tournament Information
- **surface**: Court surface (`Hard`, `Clay`, `Grass`, `Carpet`, `Unknown`)
- **draw_size**: Number of players in the draw (often rounded to nearest power of 2)
- **tourney_level**: Tournament level code
  - **ATP**: `G`=Grand Slams, `M`=Masters 1000, `A`=ATP Tour, `C`=Challengers, `S`=ITF/Satellites, `F`=Tour Finals, `D`=Davis Cup
  - **WTA**: `G`=Grand Slams, `P`=Premier, `PM`=Premier Mandatory, `I`=International, `D`=Fed Cup, plus ITF prize money levels (e.g., `15`=ITF $15,000)
  - **Other**: `E`=Exhibition, `J`=Juniors, `T`=Team Tennis

## Event Timing
- **event_year**: Year of the tournament (YYYY)
- **event_month**: Month of the tournament (MM)
- **event_date**: Full date in ISO format (YYYY-MM-DD)

## Player Information - Winner
- **winner_id**: Player identifier from source data
- **winner_seed**: Seeding position (1-32, typically)
- **winner_entry**: Entry method (`WC`=Wild Card, `Q`=Qualifier, `LL`=Lucky Loser, `PR`=Protected Ranking, `ITF`=ITF Entry)
- **winner_name**: Player's full name
- **winner_hand**: Playing hand (`R`=Right, `L`=Left, `U`=Unknown) - for ambidextrous players, this is their serving hand
- **winner_ht**: Height in centimeters
- **winner_ioc**: Three-character country code (IOC format)
- **winner_age**: Age in years as of the tournament date

## Player Information - Loser
- **loser_id**: Player identifier from source data
- **loser_seed**: Seeding position
- **loser_entry**: Entry method
- **loser_name**: Player's full name
- **loser_hand**: Playing hand
- **loser_ht**: Height in centimeters
- **loser_ioc**: Three-character country code
- **loser_age**: Age in years as of the tournament date

## Match Results
- **set1**: Score of first set (e.g., `6-4`, `7-6(5)`)
- **set2**: Score of second set
- **set3**: Score of third set
- **set4**: Score of fourth set (if applicable)
- **set5**: Score of fifth set (if applicable)
- **best_of**: Number of sets in the match (`3` or `5`)
- **round**: Tournament round (`F`=Final, `SF`=Semifinal, `QF`=Quarterfinal, `R16`=Round of 16, `R32`=Round of 32, `R64`=Round of 64, `R128`=Round of 128, `RR`=Round Robin, `Q1`-`Q3`=Qualifying rounds)

## Match Duration
- **minutes**: Match length in minutes (where available)

## Serve Statistics - Winner (w_*)
- **w_ace**: Winner's number of aces
- **w_df**: Winner's number of double faults
- **w_svpt**: Winner's total serve points
- **w_1stIn**: Winner's first serves in
- **w_1stWon**: Winner's first-serve points won
- **w_2ndWon**: Winner's second-serve points won
- **w_SvGms**: Winner's service games
- **w_bpSaved**: Winner's break points saved
- **w_bpFaced**: Winner's break points faced

## Serve Statistics - Loser (l_*)
- **l_ace**: Loser's number of aces
- **l_df**: Loser's number of double faults
- **l_svpt**: Loser's total serve points
- **l_1stIn**: Loser's first serves in
- **l_1stWon**: Loser's first-serve points won
- **l_2ndWon**: Loser's second-serve points won
- **l_SvGms**: Loser's service games
- **l_bpSaved**: Loser's break points saved
- **l_bpFaced**: Loser's break points faced

## Rankings
- **winner_rank**: Winner's ATP/WTA ranking as of tournament date
- **winner_rank_points**: Winner's ranking points
- **loser_rank**: Loser's ATP/WTA ranking as of tournament date
- **loser_rank_points**: Loser's ranking points

## Match Classification
- **gender**: Player gender (`M`=Men, `W`=Women)
- **discipline**: Match type (`singles`, `doubles`, `mixed`)

## Data Availability Flags
- **has_points**: Indicates if point-by-point data is available (`Y`/`N`)
- **has_shots**: Indicates if shot-level data is available (`Y`/`N`)

## Data Sources and Coverage
- **ATP**: Tour-level matches from 1968-2024, including qualifying and challengers
- **WTA**: Tour-level matches from 1968-2024, including qualifying and ITF events
- **Slam**: Grand Slam matches with point-by-point data (2011-2024)
- **MatchCharting**: Manually charted matches with detailed shot data

## Notes
- All statistics are integer totals (not percentages)
- Age and rankings are calculated as of the tournament date
- Some historical matches may have missing statistics
- Davis Cup/Fed Cup matches are included but may lack detailed stats
- The dataset prioritizes ATP/WTA as the primary source, with Slam and MatchCharting data used for enrichment

## Related Files
- `tennis_master_points.csv`: Point-by-point data for Slam matches
- `tennis_master_shots.csv`: Shot-level data from MatchCharting
- `dim_players.csv`: Canonical player dimension
- `dim_tournaments.csv`: Tournament dimension
