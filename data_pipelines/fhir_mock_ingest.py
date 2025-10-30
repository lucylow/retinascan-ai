import os
import json
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


FHIR_DEFAULT_BASE = "https://hapi.fhir.org/baseR4"


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
	return os.getenv(name, default)


def get_engine() -> Optional[Engine]:
	url = get_env("DATABASE_URL")
	if not url:
		return None
	return create_engine(url)


def fhir_search(resource_type: str, base_url: str, params: Optional[Dict[str, Any]] = None, limit: int = 200) -> List[Dict[str, Any]]:
	url = f"{base_url.rstrip('/')}/{resource_type}"
	query = params.copy() if params else {}
	query.update({"_count": 100})
	collected: List[Dict[str, Any]] = []
	while True:
		resp = requests.get(url, params=query, timeout=30)
		resp.raise_for_status()
		bundle = resp.json()
		entries = bundle.get("entry", [])
		for e in entries:
			resource = e.get("resource")
			if resource:
				collected.append(resource)
				if len(collected) >= limit:
					return collected
		# follow next link if present
		next_link = None
		for link in bundle.get("link", []):
			if link.get("relation") == "next":
				next_link = link.get("url")
				break
		if not next_link:
			break
		url = next_link
		query = None  # fully qualified next link already contains params
	return collected


def normalize(resources: List[Dict[str, Any]]) -> pd.DataFrame:
	if not resources:
		return pd.DataFrame()
	return pd.json_normalize(resources)


def write_csv(df: pd.DataFrame, name: str, data_dir: str) -> str:
	os.makedirs(data_dir, exist_ok=True)
	path = os.path.join(data_dir, f"{name}.csv")
	df.to_csv(path, index=False)
	return path


def write_db(df: pd.DataFrame, table: str, engine: Optional[Engine]) -> None:
	if engine is None or df.empty:
		return
	df.to_sql(table, engine, if_exists="append", index=False)


def main() -> None:
	base = get_env("FHIR_BASE_URL", FHIR_DEFAULT_BASE)
	data_dir = get_env("DATA_DIR", "./data")
	engine = get_engine()

	resources_to_fetch = {
		"fhir_patient": ("Patient", {"_has:Observation:subject:code": "loinc|4548-4"}),
		"fhir_observation": ("Observation", {"code": "http://loinc.org|4548-4"}),  # Example: HbA1c
		"fhir_condition": ("Condition", {"code": "http://snomed.info/sct|44054006"}),  # Diabetes mellitus
	}

	for table, (rtype, params) in resources_to_fetch.items():
		resources = fhir_search(rtype, base, params=params, limit=500)
		df = normalize(resources)
		csv_path = write_csv(df, table, data_dir)
		write_db(df, table, engine)
		print(json.dumps({"table": table, "rows": len(df), "csv": csv_path}))


if __name__ == "__main__":
	main()
