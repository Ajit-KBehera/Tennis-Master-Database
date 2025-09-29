from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd


@dataclass
class BuildConfig:
	data_root: Path
	out_dir: Path


def _iter_csvs(root: Path) -> Iterable[Path]:
	for p in root.rglob("*.csv"):
		# skip outputs if user writes inside data root by mistake
		if any(part.lower() == "outputs" for part in p.parts):
			continue
		yield p


def _classify_dataset(path: Path) -> Tuple[str, str, str]:
	# returns (source, domain, kind)
	parts = [part.lower() for part in path.parts]
	if "tennis_atp" in parts:
		source = "atp"
	elif "tennis_wta" in parts:
		source = "wta"
	elif "tennis_slam_pointbypoint" in parts:
		source = "slam_pbp"
	elif "tennis_matchchartingproject" in parts:
		source = "mcp"
	else:
		source = "unknown"

	name = path.name.lower()
	if "points" in name:
		kind = "points"
	elif "matches" in name:
		kind = "matches"
	elif "players" in name:
		kind = "players"
	elif "rankings" in name:
		kind = "rankings"
	else:
		kind = "other"

	if source in {"atp", "wta"}:
		domain = "tour"
	elif source == "slam_pbp":
		domain = "grand_slam"
	elif source == "mcp":
		domain = "charting"
	else:
		domain = "unknown"
	return source, domain, kind


def build_manifest(config: BuildConfig) -> pd.DataFrame:
	rows = []
	root = config.data_root
	for csv in _iter_csvs(root):
		source, domain, kind = _classify_dataset(csv)
		rows.append({
			"source": source,
			"domain": domain,
			"kind": kind,
			"rel_path": str(csv.relative_to(root)),
			"abs_path": str(csv.resolve()),
			"file_name": csv.name,
			"size_bytes": csv.stat().st_size,
		})
	manifest = pd.DataFrame(rows).sort_values(["source", "kind", "file_name"]).reset_index(drop=True)
	return manifest


