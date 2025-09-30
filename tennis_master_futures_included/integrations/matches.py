from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

# Import utilities from the main tennis_master package
import sys
sys.path.append('/Users/ajitbehera/Codes/Tennis-Master-Project')
from tennis_master.utils import normalize_name, read_csv_safely, stable_id


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def _load_atp_futures_matches(root: Path) -> pd.DataFrame:
    """Load ATP futures matches from all available years."""
    frames: List[pd.DataFrame] = []
    base_dir = root / "tennis_atp"
    
    # Load futures matches from 1991 to 2024
    for year in range(1991, 2025):
        futures_file = base_dir / f"atp_matches_futures_{year}.csv"
        if futures_file.exists():
            df = read_csv_safely(futures_file)
            df["discipline"] = "singles"
            df["source"] = "atp_futures"
            frames.append(df)
    
    if not frames:
        return pd.DataFrame()
    
    df = pd.concat(frames, ignore_index=True)
    return df


def _canonicalize_futures_matches(df: pd.DataFrame, gender: str) -> pd.DataFrame:
	"""Canonicalize futures matches data similar to main matches."""
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


def integrate_atp_futures(config: BuildConfig) -> pd.DataFrame:
	"""Integrate ATP futures matches with the same structure as main matches."""
	futures = _canonicalize_futures_matches(_load_atp_futures_matches(config.data_root), gender="M")
	
	# Use the same column structure as the main integration
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
	
	base = futures[[c for c in cols if c in futures.columns]]
	base["has_points"] = "N"
	base["has_shots"] = "N"
	return base


def enrich_futures_match_fields(df: pd.DataFrame) -> pd.DataFrame:
	"""Enrich futures match fields similar to main matches."""
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


def normalize_futures_tourney_level(df: pd.DataFrame) -> pd.DataFrame:
	"""Normalize tourney_level values for futures matches."""
	if df.empty or "tourney_level" not in df.columns:
		return df
	
	out = df.copy()
	
	# Define mapping rules for futures
	def map_level(level: str, source: str) -> str:
		if pd.isna(level) or level == "":
			return "Unknown"
		
		level = str(level).strip()
		
		# ATP Futures mappings
		if source == "atp_futures":
			# Futures levels are typically numeric (prize money in thousands)
			if level.isdigit():
				prize_money = int(level)
				if prize_money >= 100:
					return f"Futures ${prize_money}K"
				elif prize_money >= 25:
					return f"Futures ${prize_money}K"
				elif prize_money >= 15:
					return f"Futures ${prize_money}K"
				else:
					return f"Futures ${prize_money}K"
			else:
				return "Futures"
		
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
