Tennis Master Pipeline

This repository contains a reusable Python pipeline to integrate multiple public tennis datasets (ATP, WTA, Slam point-by-point, MatchCharting) into unified master CSVs.

## Quick start
- Create a virtual environment and install requirements
- Run the CLI to build manifests, dimensions, and master outputs

### Standard Build (ATP/WTA + Slam data)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tennis_master build --data-root "data(github)" --out-dir outputs
```

### Build with ATP Futures Included
```bash
python -m tennis_master_futures_included build --data-root "data(github)" --out-dir outputs
```

### Futures-Only Build (for testing)
```bash
python -m tennis_master_futures_included futures-only --data-root "data(github)" --out-dir outputs
```

## Outputs

### Standard Outputs
- `outputs/tennis_master_matches.csv` - Main matches dataset (ATP/WTA + Slam)
- `outputs/dim_players.csv` - Player dimension table
- `outputs/dim_tournaments.csv` - Tournament dimension table
- `outputs/manifest.csv` - Dataset inventory
- `outputs/player_aliases.csv` - Player name aliases
- `outputs/tournament_aliases.csv` - Tournament name aliases
- `outputs/tennis_master_points.csv` - (optional) Point-by-point data
- `outputs/tennis_master_shots.csv` - (optional) Shot-level data

### Futures Integration Outputs
- `outputs/tennis_master_matches_futures_included.csv` - Complete matches dataset including ATP Futures (1991-2024)
- `outputs/tennis_master_matches_futures_only.csv` - ATP Futures matches only (for testing)

## ATP Futures Integration

The project now includes comprehensive ATP Futures integration covering:
- **Years**: 1991-2024 (35 years of data)
- **Matches**: ~498,555 futures matches
- **Tournament Levels**: 
  - Futures (standard)
  - Futures $15K (prize money tournaments)
  - Futures $25K (prize money tournaments)

The futures integration maintains the same data structure and processing logic as the main tennis_master system, ensuring consistency across all tournament levels.

## Data Structure

See `docs/DATA_DICTIONARY.md` for field definitions.

## Re-running with new data
- Place new files in the same folder structure under the data root
- Re-run the same CLI command; the pipeline rescans and rebuilds deterministically


