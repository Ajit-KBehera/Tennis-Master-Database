from __future__ import annotations

from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from typing import List

# Import from main tennis_master package
import sys
sys.path.append('/Users/ajitbehera/Codes/Tennis-Master-Project')
from tennis_master.staging.manifest import build_manifest
from tennis_master.dimensions.players import build_players
from tennis_master.dimensions.tournaments import build_tournaments
from tennis_master.integrations.matches import integrate_atp_wta, enrich_match_fields, normalize_tourney_level
from tennis_master.integrations.slam_mcp_flags import flag_slam_points, flag_mcp_shots, union_slam_matches, build_points_outputs

# Import futures-specific modules
from ..integrations.matches import integrate_atp_futures, enrich_futures_match_fields, normalize_futures_tourney_level


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def build_all_with_futures(data_root: Path, out_dir: Path) -> None:
	"""Build all outputs including ATP futures matches."""
	config = BuildConfig(data_root=data_root, out_dir=out_dir)
	out_dir.mkdir(parents=True, exist_ok=True)
	
	# 1) Inventory datasets
	manifest_df = build_manifest(config)
	manifest_path = out_dir / "manifest.csv"
	manifest_df.to_csv(manifest_path, index=False)
	
	# 2) Dimensions
	players_dim, player_aliases = build_players(config)
	players_dim.to_csv(out_dir / "dim_players.csv", index=False)
	player_aliases.to_csv(out_dir / "player_aliases.csv", index=False)

	tourneys_dim, tourney_aliases = build_tournaments(config)
	tourneys_dim.to_csv(out_dir / "dim_tournaments.csv", index=False)
	tourney_aliases.to_csv(out_dir / "tournament_aliases.csv", index=False)

	# 3) Integrate ATP+WTA matches (existing logic)
	matches = integrate_atp_wta(config)
	matches = flag_slam_points(config, matches)
	matches = flag_mcp_shots(config, matches)
	
	# union Slam singles matches as base rows
	slam_rows = union_slam_matches(config)
	if not slam_rows.empty:
		matches = pd.concat([matches, slam_rows], ignore_index=True)
	
	# 4) Integrate ATP Futures matches
	futures_matches = integrate_atp_futures(config)
	futures_matches = enrich_futures_match_fields(futures_matches)
	futures_matches = normalize_futures_tourney_level(futures_matches)
	
	# 5) Combine all matches
	all_matches = pd.concat([matches, futures_matches], ignore_index=True)
	all_matches = enrich_match_fields(all_matches)
	all_matches = normalize_tourney_level(all_matches)
	
	# 6) Save the combined matches with futures
	all_matches.to_csv(out_dir / "tennis_master_matches_futures_included.csv", index=False)
	
	# 7) Also save the original matches without futures for comparison
	matches = enrich_match_fields(matches)
	matches = normalize_tourney_level(matches)
	matches.to_csv(out_dir / "tennis_master_matches.csv", index=False)

	# 8) build points and shots outputs
	build_points_outputs(config, out_dir)


def build_futures_only(data_root: Path, out_dir: Path) -> None:
	"""Build only futures matches for testing."""
	config = BuildConfig(data_root=data_root, out_dir=out_dir)
	out_dir.mkdir(parents=True, exist_ok=True)
	
	# Integrate only ATP Futures matches
	futures_matches = integrate_atp_futures(config)
	futures_matches = enrich_futures_match_fields(futures_matches)
	futures_matches = normalize_futures_tourney_level(futures_matches)
	
	# Save futures matches
	futures_matches.to_csv(out_dir / "tennis_master_matches_futures_only.csv", index=False)
	
	print(f"Futures matches saved: {len(futures_matches)} matches")
	print(f"Years covered: {futures_matches['event_year'].unique() if 'event_year' in futures_matches.columns else 'N/A'}")
	print(f"Tournament levels: {futures_matches['tourney_level'].unique() if 'tourney_level' in futures_matches.columns else 'N/A'}")
