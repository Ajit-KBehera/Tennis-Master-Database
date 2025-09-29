Tennis Master Outputs: Data Dictionary

Files
- outputs/manifest.csv: Inventory of discovered CSVs under the data root
- outputs/dim_players.csv: Canonical players dimension
- outputs/player_aliases.csv: Mapping from source player ids to canonical ids
- outputs/dim_tournaments.csv: Canonical tournaments dimension derived from tour data
- outputs/tournament_aliases.csv: Tournament alias hints from tour/Slam/MCP
- outputs/tennis_master_matches.csv: Integrated ATP+WTA match-level dataset with enrichment flags

dim_players.csv
- player_canonical_id: Stable id generated from normalized full name, dob, and ioc
- full_name: Normalized full name
- name_first, name_last: Given/surname when available
- hand: R/L/U from sources
- dob: YYYYMMDD when available (string as in sources)
- ioc: Three-letter country code per source
- height: Height in centimeters if present
- wikidata_id: Wikidata identifier when provided
- player_id_atp, player_id_wta: Source ids (may be null for one side)

player_aliases.csv
- player_canonical_id: Canonical player id
- source: atp|wta
- source_id: Player id within that source

dim_tournaments.csv
- tourney_id: Source tourney identifier (ATP/WTA space)
- tourney_name: Tournament name
- surface: Hard/Clay/Grass/Carpet when known
- tourney_level: G/M/A/I/… per source
- draw_size: Numeric where available
- tourney_date: YYYYMMDD integer-like date for event start

tournament_aliases.csv
- tourney_id: May be null when alias originates from non-tour sources
- alias: Normalized alias string
- source: tour|slam_pbp|mcp (origin of alias)

tennis_master_matches.csv
- match_id: Canonical stable id from tourney_id, date, round, and ordered player ids
- source: atp|wta (base record origin)
- tourney_id, tourney_name, surface, draw_size, tourney_level, tourney_date: Event metadata
- match_num: Source match number when present
- winner_id, winner_seed, winner_entry, winner_name, winner_hand, winner_ht, winner_ioc, winner_age: Winner fields
- loser_id, loser_seed, loser_entry, loser_name, loser_hand, loser_ht, loser_ioc, loser_age: Loser fields
- score: Raw score string from source
- best_of: 3 or 5
- round: Standardized round code per source
- minutes: Match duration when available
- w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_SvGms, w_bpSaved, w_bpFaced: Winner serve stats
- l_ace, l_df, l_svpt, l_1stIn, l_1stWon, l_2ndWon, l_SvGms, l_bpSaved, l_bpFaced: Loser serve stats
- winner_rank, winner_rank_points, loser_rank, loser_rank_points: Rankings metadata when present
- gender: M for ATP, W for WTA
- discipline: singles (default for this integration)
- has_points: Y/N flag indicating potential Slam point-by-point coverage exists
- has_shots: Y/N flag indicating potential MatchCharting shot-level coverage exists

Notes
- Canonical ids are deterministic hashes; the same inputs will yield the same ids on re-runs.
- Normalization uses ASCII folding and whitespace cleanup for name fields; originals are preserved in source datasets.
- Future enhancements can join Slam/MCP rows exactly to expose point or shot keys per match.


