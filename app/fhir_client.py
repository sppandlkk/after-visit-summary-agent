from __future__ import annotations
import os
import requests
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "mock_fhir"

class FhirClient:
    """Client that queries a real FHIR server when configured, otherwise falls back to local mock files.
    It expects the following env vars:
      - FHIR_BASE_URL (e.g. https://epic.example.com/api/FHIR/R4)
      - FHIR_API_KEY (optional, for authorization header)
    """
    def __init__(self):
        self.base_url = os.getenv("FHIR_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("FHIR_API_KEY", "")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Accept": "application/fhir+json"})

    def _use_remote(self) -> bool:
        return bool(self.base_url)

    def get_patient(self, patient_fhir_id: str) -> Dict[str, Any]:
        if self._use_remote():
            url = f"{self.base_url}/Patient/{patient_fhir_id}"
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        # local mock path: data/mock_fhir/{patient_fhir_id}/Patient_{id}.json or Patient.json
        folder = DATA_DIR / patient_fhir_id
        p = folder / "Patient.json"
        if p.exists():
            return json_load(p)
        return {}

    def list_conditions(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        if self._use_remote():
            url = f"{self.base_url}/Condition"
            params = {"patient": patient_fhir_id}
            r = self.session.get(url, params=params, timeout=10)
            r.raise_for_status()
            bundle = r.json()
            return bundle.get("entry", [])
        folder = DATA_DIR / patient_fhir_id
        p = folder / "Condition.json"
        if p.exists():
            return json_load(p)
        return []

    def list_medication_requests(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        if self._use_remote():
            url = f"{self.base_url}/MedicationRequest"
            params = {"patient": patient_fhir_id}
            r = self.session.get(url, params=params, timeout=10)
            r.raise_for_status()
            bundle = r.json()
            return bundle.get("entry", [])
        folder = DATA_DIR / patient_fhir_id
        p = folder / "MedicationRequest.json"
        if p.exists():
            return json_load(p)
        return []

    def list_medication_statements(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        if self._use_remote():
            url = f"{self.base_url}/MedicationStatement"
            params = {"patient": patient_fhir_id}
            r = self.session.get(url, params=params, timeout=10)
            r.raise_for_status()
            bundle = r.json()
            return bundle.get("entry", [])
        folder = DATA_DIR / patient_fhir_id
        p = folder / "MedicationStatement.json"
        if p.exists():
            return json_load(p)
        return []

    def get_latest_encounter(self, patient_fhir_id: str) -> Dict[str, Any]:
        if self._use_remote():
            url = f"{self.base_url}/Encounter"
            params = {"patient": patient_fhir_id, "_sort": "-period", "_count": 1}
            r = self.session.get(url, params=params, timeout=10)
            r.raise_for_status()
            bundle = r.json()
            entries = bundle.get("entry", [])
            if entries:
                return entries[0].get("resource", {})
            return {}
        folder = DATA_DIR / patient_fhir_id
        p = folder / "Encounter.json"
        if p.exists():
            return json_load(p)
        return {}

def json_load(path: Path):
    import json
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
