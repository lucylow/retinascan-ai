from datetime import datetime
import requests


class FHIRIntegration:
    """FHIR-compliant EHR integration client."""

    def __init__(self, fhir_server_url: str, auth_token: str) -> None:
        self.fhir_server_url = fhir_server_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/fhir+json",
        }

    def create_diagnostic_report(self, patient_id: str, screening_results: dict) -> dict:
        resource = {
            "resourceType": "DiagnosticReport",
            "id": screening_results.get("report_id"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": "RAD",
                            "display": "Radiology",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {"system": "http://loinc.org", "code": "81204-9", "display": "Diabetic Retinopathy Screening"}
                ]
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": datetime.now().isoformat(),
            "issued": datetime.now().isoformat(),
            "conclusion": self._format_conclusion(screening_results),
            "conclusionCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": self._get_snomed_code(screening_results.get("dr_grade", "No DR")),
                            "display": screening_results.get("dr_grade", "No DR"),
                        }
                    ]
                }
            ],
        }
        return self._post_to_fhir(resource, "DiagnosticReport")

    def create_observation(self, patient_id: str, screening_results: dict) -> dict:
        resource = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "imaging",
                            "display": "Imaging",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {"system": "http://loinc.org", "code": "81204-9", "display": "Diabetic Retinopathy AI Assessment"}
                ]
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": datetime.now().isoformat(),
            "valueString": screening_results.get("dr_grade", "Unknown"),
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "POS" if screening_results.get("requires_referral") else "NEG",
                            "display": "Positive" if screening_results.get("requires_referral") else "Negative",
                        }
                    ]
                }
            ],
            "note": [
                {"text": f"AI Confidence: {screening_results.get('dr_confidence', 0.0)*100:.1f}%"}
            ],
        }
        return self._post_to_fhir(resource, "Observation")

    def create_service_request(self, patient_id: str, screening_results: dict) -> dict | None:
        if not screening_results.get("requires_referral"):
            return None

        priority = (
            "urgent" if screening_results.get("dr_grade") in ["Severe", "Proliferative DR"] else "routine"
        )
        resource = {
            "resourceType": "ServiceRequest",
            "status": "active",
            "intent": "order",
            "priority": priority,
            "code": {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "252779009", "display": "Ophthalmology consultation"}
                ]
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "authoredOn": datetime.now().isoformat(),
            "reasonCode": [{"text": f"Diabetic Retinopathy detected: {screening_results.get('dr_grade', 'Unknown')}"}],
        }
        return self._post_to_fhir(resource, "ServiceRequest")

    def _format_conclusion(self, results: dict) -> str:
        conclusion = f"AI-assisted screening detected: {results.get('dr_grade', 'Unknown')} "
        conclusion += f"(Confidence: {results.get('dr_confidence', 0.0)*100:.1f}%). "
        conclusion += (
            "Referral to ophthalmologist recommended." if results.get("requires_referral") else "Continue routine annual screening."
        )
        return conclusion

    def _get_snomed_code(self, dr_grade: str) -> str:
        mapping = {
            "No DR": "201141000119104",
            "Mild": "312903003",
            "Moderate": "399864000",
            "Severe": "399866003",
            "Proliferative DR": "59276001",
        }
        return mapping.get(dr_grade, "201141000119104")

    def _post_to_fhir(self, resource: dict, resource_type: str) -> dict:
        try:
            response = requests.post(
                f"{self.fhir_server_url}/{resource_type}", headers=self.headers, json=resource, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "resource_id": data.get("id") or data.get("entry", [{}])[0].get("id")}
        except requests.exceptions.RequestException as exc:
            return {"status": "error", "message": str(exc)}


fhir_client = FHIRIntegration(
    fhir_server_url="https://fhir.example.com/api",
    auth_token="your_oauth_token_here",
)


