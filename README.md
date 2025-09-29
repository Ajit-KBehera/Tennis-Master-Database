Tennis Master Pipeline

This repository contains a reusable Python pipeline to integrate multiple public tennis datasets (ATP, WTA, Slam point-by-point, MatchCharting) into unified master CSVs.

Quick start
- Create a virtual environment and install requirements
- Run the CLI to build manifests, dimensions, and master outputs

Example
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tennis_master build --data-root "data(github)" --out-dir outputs
```

Outputs
- outputs/tennis_master_matches.csv
- outputs/dim_players.csv
- outputs/dim_tournaments.csv
- (optional) outputs/tennis_master_points.csv
- (optional) outputs/tennis_master_shots.csv
 - outputs/manifest.csv
 - outputs/player_aliases.csv
 - outputs/tournament_aliases.csv

See docs/DATA_DICTIONARY.md for field definitions.

Re-running with new data
- Place new files in the same folder structure under the data root
- Re-run the same CLI command; the pipeline rescans and rebuilds deterministically


