from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from unidecode import unidecode


def normalize_name(name: str) -> str:
	if name is None:
		return ""
	return " ".join(unidecode(str(name)).strip().replace("_", " ").split()).title()


def stable_id(*parts: Optional[str]) -> str:
	joined = "|".join([(p or "").strip() for p in parts])
	return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]


def read_csv_safely(path: Path, **kwargs) -> pd.DataFrame:
	kwargs.setdefault("dtype", "string")
	kwargs.setdefault("na_filter", True)
	kwargs.setdefault("keep_default_na", True)
	try:
		return pd.read_csv(path, **kwargs)
	except UnicodeDecodeError:
		return pd.read_csv(path, encoding="latin1", **kwargs)


