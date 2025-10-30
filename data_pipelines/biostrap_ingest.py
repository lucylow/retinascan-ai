import os
import json
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
	value = os.getenv(name, default)
	return value


def get_engine() -> Optional[Engine]:
	url = get_env("DATABASE_URL")
	if not url:
		return None
	return create_engine(url)


def fetch_biostrap(endpoint: str, api_key: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
	base_url = "https://api.biostrap.com/v1"
	url = f"{base_url}/{endpoint.lstrip('/')}"
	headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
	resp = requests.get(url, headers=headers, params=params, timeout=30)
	resp.raise_for_status()
	data = resp.json()
	if isinstance(data, dict) and "data" in data:
		return data["data"]  # common pattern
	if isinstance(data, list):
		return data
	return [data]


def write_csv(df: pd.DataFrame, name: str, data_dir: str) -> str:
	os.makedirs(data_dir, exist_ok=True)
	path = os.path.join(data_dir, f"{name}.csv")
	df.to_csv(path, index=False)
	return path


def write_db(df: pd.DataFrame, table: str, engine: Optional[Engine]) -> None:
	if engine is None or df.empty:
		return
	df.to_sql(table, engine, if_exists="append", index=False)


def normalize_records(records: List[Dict[str, Any]]) -> pd.DataFrame:
	if not records:
		return pd.DataFrame()
	# pandas.json_normalize handles nested objects reasonably for hackathon speed
	return pd.json_normalize(records)


def main() -> None:
	api_key = get_env("BIOSTRAP_API_KEY")
	if not api_key:
		raise RuntimeError("BIOSTRAP_API_KEY is not set")

	data_dir = get_env("DATA_DIR", "./data")
	engine = get_engine()

	# Example endpoints: adjust as needed based on available data in your Biostrap account
	endpoints = {
		"biostrap_heart_rate": {"endpoint": "heart_rate", "params": None},
		"biostrap_respiration": {"endpoint": "respiration_rate", "params": None},
	}

	for table, spec in endpoints.items():
		records = fetch_biostrap(spec["endpoint"], api_key, spec.get("params"))
		df = normalize_records(records)
		csv_path = write_csv(df, table, data_dir)
		write_db(df, table, engine)
		print(json.dumps({"table": table, "rows": len(df), "csv": csv_path}))


if __name__ == "__main__":
	main()
