from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd

from ..utils import normalize_name, read_csv_safely, stable_id


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def _collect_tourneys_from_matches(matches: pd.DataFrame) -> pd.DataFrame:
	cols = [c for c in ["tourney_id", "tourney_name", "surface", "tourney_level", "draw_size", "tourney_date"] if c in matches.columns]
	return matches[cols].drop_duplicates()


def build_tournaments(config: BuildConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
	# Load representative ATP/WTA matches to derive tournament dimension
	atp_matches = []
	wta_matches = []
	for year in range(1968, 2025):
		p = config.data_root / "tennis_atp" / f"atp_matches_{year}.csv"
		if p.exists():
			atp_matches.append(read_csv_safely(p, nrows=10000))
		p2 = config.data_root / "tennis_wta" / f"wta_matches_{year}.csv"
		if p2.exists():
			wta_matches.append(read_csv_safely(p2, nrows=10000))
	atp_df = pd.concat(atp_matches, ignore_index=True) if atp_matches else pd.DataFrame()
	wta_df = pd.concat(wta_matches, ignore_index=True) if wta_matches else pd.DataFrame()

	base = pd.concat([
		_collect_tourneys_from_matches(atp_df) if not atp_df.empty else pd.DataFrame(),
		_collect_tourneys_from_matches(wta_df) if not wta_df.empty else pd.DataFrame(),
	], ignore_index=True)
	if base.empty:
		return pd.DataFrame(columns=["tourney_id","tourney_name","surface","tourney_level","draw_size","tourney_date"]), pd.DataFrame(columns=["tourney_id","alias","source"]) 

	base["tourney_name_norm"] = base["tourney_name"].map(lambda x: normalize_name(x) if pd.notna(x) else "")
	base = base.drop_duplicates(["tourney_id"]).reset_index(drop=True)

	aliases = base[["tourney_id", "tourney_name_norm"]].drop_duplicates().rename(columns={"tourney_name_norm": "alias"})
	aliases["source"] = "tour"

	# Slam and MCP aliases derived from filenames only
	slam_aliases = []
	for p in (config.data_root / "tennis_slam_pointbypoint").glob("*.csv"):
		name = p.stem
		if "-matches" in name or "-points" in name:
			slam_aliases.append({"tourney_id": None, "alias": normalize_name(name.split("-")[1]), "source": "slam_pbp"})
	mcp_aliases = []
	for p in (config.data_root / "tennis_MatchChartingProject").glob("charting-*-matches.csv"):
		mcp_aliases.append({"tourney_id": None, "alias": "", "source": "mcp"})
	alias_df = pd.concat([aliases, pd.DataFrame(slam_aliases), pd.DataFrame(mcp_aliases)], ignore_index=True)
	return base.drop(columns=["tourney_name_norm"], errors="ignore"), alias_df


