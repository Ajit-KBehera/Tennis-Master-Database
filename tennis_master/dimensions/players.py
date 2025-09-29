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


def _prep_players(df: pd.DataFrame, source: str) -> pd.DataFrame:
	cols = [c for c in [
		"player_id", "name_first", "name_last", "hand", "dob", "ioc", "height", "wikidata_id"
	] if c in df.columns]
	df = df[cols].copy()
	if source == "wta" and "player_id" in df.columns:
		# ensure separation of id spaces when we later merge
		df.rename(columns={"player_id": "player_id_wta"}, inplace=True)
	elif source == "atp" and "player_id" in df.columns:
		df.rename(columns={"player_id": "player_id_atp"}, inplace=True)
	df["name_first_norm"] = df.get("name_first", "").map(lambda x: normalize_name(x) if pd.notna(x) else "")
	df["name_last_norm"] = df.get("name_last", "").map(lambda x: normalize_name(x) if pd.notna(x) else "")
	df["full_name_norm"] = (df["name_first_norm"] + " " + df["name_last_norm"]).str.strip()
	return df



def build_players(config: BuildConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
	atp_path = config.data_root / "tennis_atp" / "atp_players.csv"
	wta_path = config.data_root / "tennis_wta" / "wta_players.csv"
	atp = read_csv_safely(atp_path)
	wta = read_csv_safely(wta_path)
	atp_p = _prep_players(atp, "atp")
	wta_p = _prep_players(wta, "wta")

	# Outer merge by normalized full name and dob/ioc when available
	left_keys = ["full_name_norm", "dob", "ioc"]
	right_keys = ["full_name_norm", "dob", "ioc"]
	merged = pd.merge(
		atp_p,
		wta_p,
		how="outer",
		left_on=left_keys,
		right_on=right_keys,
		suffixes=("_atp", "_wta"),
	)

	# After merge with left_on/right_on, ensure we have aligned-length series
	def col_or_empty(name: str) -> pd.Series:
		return merged[name] if name in merged.columns else pd.Series([pd.NA] * len(merged), dtype="string")

	full_name = col_or_empty("full_name_norm_x").fillna(col_or_empty("full_name_norm_y"))
	dob = col_or_empty("dob_x").fillna(col_or_empty("dob_y"))
	ioc = col_or_empty("ioc_x").fillna(col_or_empty("ioc_y"))

	canonical_id = [
		stable_id(fn or "", d or "", i or "")
		for fn, d, i in zip(full_name.fillna(""), dob.fillna(""), ioc.fillna(""))
	]

	# Prefer ATP fields, then WTA
	def prefer(a: str, b: str) -> pd.Series:
		return col_or_empty(a).fillna(col_or_empty(b))

	dim = pd.DataFrame({
		"player_canonical_id": canonical_id,
		"full_name": full_name,
		"name_first": prefer("name_first_atp", "name_first_wta"),
		"name_last": prefer("name_last_atp", "name_last_wta"),
		"hand": prefer("hand_atp", "hand_wta"),
		"dob": dob,
		"ioc": ioc,
		"height": prefer("height_atp", "height_wta"),
		"wikidata_id": prefer("wikidata_id_atp", "wikidata_id_wta"),
		"player_id_atp": col_or_empty("player_id_atp"),
		"player_id_wta": col_or_empty("player_id_wta"),
	})

	# Alias table maps each source id to canonical id
	aliases = []
	if "player_id_atp" in dim.columns:
		aliases.append(dim[["player_canonical_id", "player_id_atp"]].dropna().assign(source="atp", source_id=lambda d: d["player_id_atp"]).loc[:, ["player_canonical_id", "source", "source_id"]])
	if "player_id_wta" in dim.columns:
		aliases.append(dim[["player_canonical_id", "player_id_wta"]].dropna().assign(source="wta", source_id=lambda d: d["player_id_wta"]).loc[:, ["player_canonical_id", "source", "source_id"]])
	alias_df = pd.concat(aliases, ignore_index=True) if aliases else pd.DataFrame(columns=["player_canonical_id", "source", "source_id"])

	return dim, alias_df


