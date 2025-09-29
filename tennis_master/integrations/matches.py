from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from ..utils import normalize_name, read_csv_safely, stable_id


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def _load_tour_matches(root: Path, tour: str) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    base_dir = root / ("tennis_atp" if tour == "atp" else "tennis_wta")
    for year in range(1968, 2026):
        # main draw singles
        p_main = base_dir / f"{tour}_matches_{year}.csv"
        if p_main.exists():
            dfm = read_csv_safely(p_main)
            dfm["discipline"] = "singles"
            frames.append(dfm)
        # qualifying (ATP qualifiers/challengers, WTA qual/ITF)
        if tour == "atp":
            p_qual = base_dir / f"{tour}_matches_qual_chall_{year}.csv"
            if p_qual.exists():
                dfq = read_csv_safely(p_qual)
                dfq["discipline"] = "singles"
                frames.append(dfq)
        else:
            p_qual = base_dir / f"{tour}_matches_qual_itf_{year}.csv"
            if p_qual.exists():
                dfq = read_csv_safely(p_qual)
                dfq["discipline"] = "singles"
                frames.append(dfq)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["source"] = tour
    return df


def _canonicalize_matches(df: pd.DataFrame, gender: str) -> pd.DataFrame:
	if df.empty:
		return df
	# Normalize key string columns
	for col in ["tourney_name", "winner_name", "loser_name", "surface", "round"]:
		if col in df.columns:
			df[col] = df[col].astype("string")
			df[col + "_norm"] = df[col].map(lambda x: normalize_name(x) if pd.notna(x) else "")

	# Construct canonical match id
	def make_id(r):
		tid = str(r.get("tourney_id", ""))
		date = str(r.get("tourney_date", ""))
		round = r.get("round", "")
		w = r.get("winner_id", "")
		l = r.get("loser_id", "")
		return stable_id(tid, date, str(round), str(min(w, l)), str(max(w, l)))

	df["match_id"] = df.apply(make_id, axis=1)
	df["gender"] = gender
	df["discipline"] = "singles"
	return df


def integrate_atp_wta(config: BuildConfig) -> pd.DataFrame:
	atp = _canonicalize_matches(_load_tour_matches(config.data_root, "atp"), gender="M")
	wta = _canonicalize_matches(_load_tour_matches(config.data_root, "wta"), gender="W")
	cols = [
		"match_id","source","tourney_id","tourney_name","surface","draw_size","tourney_level","tourney_date","match_num",
		"winner_id","winner_seed","winner_entry","winner_name","winner_hand","winner_ht","winner_ioc","winner_age",
		"loser_id","loser_seed","loser_entry","loser_name","loser_hand","loser_ht","loser_ioc","loser_age",
		"score","best_of","round","minutes",
		"w_ace","w_df","w_svpt","w_1stIn","w_1stWon","w_2ndWon","w_SvGms","w_bpSaved","w_bpFaced",
		"l_ace","l_df","l_svpt","l_1stIn","l_1stWon","l_2ndWon","l_SvGms","l_bpSaved","l_bpFaced",
		"winner_rank","winner_rank_points","loser_rank","loser_rank_points",
		"gender","discipline"
	]
	base = pd.concat([atp, wta], ignore_index=True)
	base = base[[c for c in cols if c in base.columns]]
	base["has_points"] = "N"
	base["has_shots"] = "N"
	return base


def enrich_match_fields(df: pd.DataFrame) -> pd.DataFrame:
	if df.empty:
		return df
	out = df.copy()
	# event_year, event_month, event_date (ISO)
	def _year(s: str) -> str:
		return s[:4] if isinstance(s, str) and len(s) >= 4 else ""
	def _month(s: str) -> str:
		return s[4:6] if isinstance(s, str) and len(s) >= 6 else ""
	def _iso(s: str) -> str:
		if isinstance(s, str) and len(s) >= 8:
			return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
		elif isinstance(s, str) and len(s) == 4:
			return f"{s}-01-01"
		return ""
	if "tourney_date" in out.columns:
		out["event_year"] = out["tourney_date"].astype("string").map(_year)
		out["event_month"] = out["tourney_date"].astype("string").map(_month)
		out["event_date"] = out["tourney_date"].astype("string").map(_iso)
		# insert after tourney_date
		cols = list(out.columns)
		td_idx = cols.index("tourney_date") if "tourney_date" in cols else len(cols)
		for name in ["event_year", "event_month", "event_date"]:
			cols.remove(name)
		cols[td_idx+1:td_idx+1] = ["event_year", "event_month", "event_date"]
		out = out[cols]
		# drop tourney_date as requested
		out = out.drop(columns=["tourney_date"], errors="ignore")
	# Replace score with set1..set5 at same position
	set_cols = ["set1","set2","set3","set4","set5"]
	def _sets(score: str) -> List[str]:
		if not isinstance(score, str):
			return ["", "", "", "", ""]
		parts = [p for p in score.strip().split() if p]
		# keep only first 5 tokens
		vals = parts[:5]
		# pad
		while len(vals) < 5:
			vals.append("")
		return vals
	if "score" in out.columns:
		sets = out["score"].astype("string").map(_sets)
		for i, name in enumerate(set_cols):
			out[name] = sets.map(lambda v, i=i: v[i])
		cols = list(out.columns)
		score_idx = cols.index("score")
		# remove newly added set cols to re-insert
		for name in set_cols:
			cols.remove(name)
		# replace score with set cols
		cols.pop(score_idx)
		for j, name in enumerate(set_cols):
			cols.insert(score_idx + j, name)
		out = out[cols]
	return out


def normalize_tourney_level(df: pd.DataFrame) -> pd.DataFrame:
	"""Normalize tourney_level values to human-readable names."""
	if df.empty or "tourney_level" not in df.columns:
		return df
	
	out = df.copy()
	
	# Define mapping rules
	def map_level(level: str, source: str) -> str:
		if pd.isna(level) or level == "":
			return "Unknown"
		
		level = str(level).strip()
		
		# ATP mappings
		if source == "atp":
			if level == "G": return "Grand Slam"
			elif level == "M": return "ATP Tour"
			elif level == "A": return "ATP Tour"
			elif level == "S": return "Futures"
			elif level == "C": return "Challengers"
			elif level == "D": return "Davis Cup"
			elif level == "F": return "Tour Finals"
			elif level == "O": return "Other"
			elif level == "E": return "Exhibition"
			elif level == "J": return "Juniors"
			elif level == "CC": return "Challengers"
		
		# WTA mappings
		elif source == "wta":
			if level == "G": return "Grand Slam"
			elif level == "P": return "WTA Tour"
			elif level == "PM": return "WTA Tour"
			elif level == "I": return "International"
			elif level == "C": return "Challengers"
			elif level == "D": return "BJK Cup"
			elif level == "W": return "Tour Finals"
			elif level == "E": return "Exhibition"
			elif level == "J": return "Juniors"
			elif level == "CC": return "Challengers"
			elif level in ["T1", "T2", "T3", "T4", "T5"]: return "WTA Tour"
			# ITF prize money levels
			elif level.isdigit() and int(level) >= 10: return f"ITF ${level}K"
		
		# Slam and MCP mappings (keep as is or map to generic)
		elif source in ["slam_pbp", "mcp"]:
			if level == "G": return "Grand Slam"
			else: return "Unknown"
		
		# Default fallback
		return level
	
	# Apply mapping
	if "source" in out.columns:
		out["tourney_level"] = out.apply(
			lambda row: map_level(row.get("tourney_level", ""), row.get("source", "")), 
			axis=1
		)
	else:
		out["tourney_level"] = out["tourney_level"].map(lambda x: map_level(x, ""))
	
	return out


