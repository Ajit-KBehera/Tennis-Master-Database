from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..utils import read_csv_safely, normalize_name, stable_id


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def flag_slam_points(config: BuildConfig, matches_df: pd.DataFrame) -> pd.DataFrame:
	# Use slam file presence to flag has_points; matching by coarse keys (tourney name, year)
	if matches_df.empty:
		return matches_df
	flags = []
	slam_dir = config.data_root / "tennis_slam_pointbypoint"
	for p in slam_dir.glob("*-points*.csv"):
		flags.append(p)
	if not flags:
		matches_df["has_points"] = matches_df.get("has_points", "N")
		return matches_df
	# heuristic: mark slams by tourney level if available or by name contains Grand Slam names
	mask = matches_df.get("tourney_level").fillna("").isin(["G"]) | matches_df.get("tourney_name").fillna("").str.contains("Australian Open|Roland Garros|French Open|Wimbledon|US Open", case=False, regex=True)
	matches_df.loc[mask, "has_points"] = "Y"
	return matches_df


def flag_mcp_shots(config: BuildConfig, matches_df: pd.DataFrame) -> pd.DataFrame:
	mcp_dir = config.data_root / "tennis_MatchChartingProject"
	mcp_points = list(mcp_dir.glob("charting-*-points-*.csv"))
	if not mcp_points or matches_df.empty:
		matches_df["has_shots"] = matches_df.get("has_shots", "N")
		return matches_df
	# broad flag: any match potentially in MCP data
	matches_df["has_shots"] = "Y"
	return matches_df


def union_slam_matches(config: BuildConfig) -> pd.DataFrame:
	rows = []
	slam_dir = config.data_root / "tennis_slam_pointbypoint"
	for p in slam_dir.glob("*-matches*.csv"):
		df = read_csv_safely(p)
		if df.empty:
			continue
		keep = pd.DataFrame({
			"source": "slam_pbp",
			"tourney_name": df.get("slam", pd.Series(dtype="string")).map(lambda x: normalize_name(x) if pd.notna(x) else ""),
			"tourney_id": df.get("slam", pd.Series(dtype="string")),
			"tourney_date": df.get("year", pd.Series(dtype="string")),
			"match_num": df.get("match_num", pd.Series(dtype="string")),
			"winner_name": df.get("winner", pd.Series(dtype="string")),
			"loser_name": pd.Series([pd.NA] * len(df), dtype="string"),
			"round": df.get("round", pd.Series(dtype="string")),
			"best_of": pd.Series([pd.NA] * len(df), dtype="string"),
			"gender": pd.Series([pd.NA] * len(df), dtype="string"),
			"discipline": pd.Series(["singles"] * len(df), dtype="string"),
		})
		keep["match_id"] = [
			stable_id(str(r.get("tourney_id", "")), str(r.get("tourney_date", "")), str(r.get("round", "")), str(i))
			for i, r in keep.iterrows()
		]
		rows.append(keep)
	return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_points_outputs(config: BuildConfig, out_dir: Path) -> None:
	# Concatenate Slam points and MCP points into separate outputs
	slam_points = []
	for p in (config.data_root / "tennis_slam_pointbypoint").glob("*-points*.csv"):
		df = read_csv_safely(p)
		if not df.empty:
			df.insert(0, "source", "slam_pbp")
			slam_points.append(df)
	if slam_points:
		pd.concat(slam_points, ignore_index=True).to_csv(out_dir / "tennis_master_points.csv", index=False)

	mcp_points = []
	for p in (config.data_root / "tennis_MatchChartingProject").glob("charting-*-points-*.csv"):
		df = read_csv_safely(p)
		if not df.empty:
			df.insert(0, "source", "mcp")
			mcp_points.append(df)
	if mcp_points:
		pd.concat(mcp_points, ignore_index=True).to_csv(out_dir / "tennis_master_shots.csv", index=False)


