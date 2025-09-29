from __future__ import annotations

from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from typing import List

from ..staging.manifest import build_manifest
from ..dimensions.players import build_players
from ..dimensions.tournaments import build_tournaments
from ..integrations.matches import integrate_atp_wta, enrich_match_fields, normalize_tourney_level
from ..integrations.slam_mcp_flags import flag_slam_points, flag_mcp_shots, union_slam_matches, build_points_outputs


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def build_all(data_root: Path, out_dir: Path) -> None:
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

	# 3) Integrate ATP+WTA matches
	matches = integrate_atp_wta(config)
	matches = flag_slam_points(config, matches)
	matches = flag_mcp_shots(config, matches)
	# union Slam singles matches as base rows
	slam_rows = union_slam_matches(config)
	if not slam_rows.empty:
		matches = pd.concat([matches, slam_rows], ignore_index=True)
	matches = enrich_match_fields(matches)
	matches = normalize_tourney_level(matches)
	matches.to_csv(out_dir / "tennis_master_matches.csv", index=False)

	# build points and shots outputs
	build_points_outputs(config, out_dir)


