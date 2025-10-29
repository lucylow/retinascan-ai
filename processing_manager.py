import os
import json
from datetime import datetime

from image_quality_assessment import quality_checker
from report_generator import report_gen
from retinopathy_model import retina_ai


class ProcessingManager:
    """
    Flexible cloud/edge processing manager.
    Supports both online and offline modes.
    """

    def __init__(self, mode: str = "cloud") -> None:
        self.mode = mode  # 'cloud' or 'edge'
        self.offline_queue = []

    def process_image(self, image, patient_data: dict) -> dict:
        if self.mode == "cloud" and self._check_connectivity():
            return self._cloud_process(image, patient_data)
        return self._edge_process(image, patient_data)

    def _check_connectivity(self) -> bool:
        try:
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _cloud_process(self, image, patient_data: dict) -> dict:
        quality_result = quality_checker.assess_quality(image)
        if quality_result["should_retake"]:
            return {"status": "quality_failed", "message": quality_result["feedback"], "retry": True}

        ai_result = retina_ai.predict_with_confidence(image)
        report = report_gen.generate_report(patient_data, ai_result)
        self._save_to_cloud(report)
        return {"status": "success", "report": report, "processing_mode": "cloud"}

    def _edge_process(self, image, patient_data: dict) -> dict:
        quality_result = quality_checker.assess_quality(image)
        if quality_result["should_retake"]:
            return {"status": "quality_failed", "message": quality_result["feedback"], "retry": True}

        ai_result = retina_ai.predict_with_confidence(image)
        report = report_gen.generate_report(patient_data, ai_result)

        self.offline_queue.append({"report": report, "timestamp": datetime.now().isoformat()})
        self._save_locally(report)
        return {"status": "success", "report": report, "processing_mode": "edge", "sync_pending": True}

    def sync_offline_data(self) -> dict:
        if not self._check_connectivity():
            return {"status": "offline", "message": "No connectivity"}

        synced = 0
        for item in self.offline_queue:
            try:
                self._save_to_cloud(item["report"])
                synced += 1
            except Exception as exc:  # noqa: BLE001 - log and continue
                print(f"Sync error: {exc}")

        self.offline_queue = []
        return {"status": "synced", "count": synced}

    def _save_to_cloud(self, report: dict) -> None:
        # Replace with real cloud storage (e.g., S3, Firestore).
        print(f"Saving to cloud: {report['report_id']}")

    def _save_locally(self, report: dict) -> None:
        os.makedirs("offline_reports", exist_ok=True)
        filename = f"offline_reports/{report['report_id']}.json"
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)


processor = ProcessingManager(mode="cloud")


