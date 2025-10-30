import os
import json
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

try:
	import pydicom  # type: ignore
except Exception as e:  # pragma: no cover
	pydicom = None


IMAGE_EXTENSIONS = {".dcm"}


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
	return os.getenv(name, default)


def get_engine() -> Optional[Engine]:
	url = get_env("DATABASE_URL")
	if not url:
		return None
	return create_engine(url)


def list_files(root: str) -> List[str]:
	paths: List[str] = []
	for dirpath, _, filenames in os.walk(root):
		for fname in filenames:
			paths.append(os.path.join(dirpath, fname))
	return paths


def is_dicom(path: str) -> bool:
	_, ext = os.path.splitext(path.lower())
	return ext in IMAGE_EXTENSIONS


def extract_dicom_metadata(path: str) -> Dict[str, Any]:
	if pydicom is None:
		raise RuntimeError("pydicom is not installed")
	ds = pydicom.dcmread(path, stop_before_pixels=True, force=True)
	meta = {
		"file_path": path,
		"SOPClassUID": str(getattr(ds, "SOPClassUID", "")),
		"SOPInstanceUID": str(getattr(ds, "SOPInstanceUID", "")),
		"StudyInstanceUID": str(getattr(ds, "StudyInstanceUID", "")),
		"SeriesInstanceUID": str(getattr(ds, "SeriesInstanceUID", "")),
		"Modality": str(getattr(ds, "Modality", "")),
		"StudyDate": str(getattr(ds, "StudyDate", "")),
		"PatientID": str(getattr(ds, "PatientID", "")),
		"PatientSex": str(getattr(ds, "PatientSex", "")),
		"PatientBirthDate": str(getattr(ds, "PatientBirthDate", "")),
	}
	return meta


def gather_metadata(images_dir: str) -> List[Dict[str, Any]]:
	records: List[Dict[str, Any]] = []
	for path in list_files(images_dir):
		if not is_dicom(path):
			continue
		try:
			records.append(extract_dicom_metadata(path))
		except Exception as e:  # skip broken files in hackathon mode
			records.append({"file_path": path, "error": str(e)})
	return records


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
	images_dir = get_env("IMAGES_DIR", "./datasets/retina_images")
	data_dir = get_env("DATA_DIR", "./data")
	engine = get_engine()

	records = gather_metadata(images_dir)
	df = pd.json_normalize(records)
	csv_path = write_csv(df, "dicom_metadata", data_dir)
	write_db(df, "dicom_metadata", engine)
	print(json.dumps({"table": "dicom_metadata", "rows": len(df), "csv": csv_path}))


if __name__ == "__main__":
	main()
