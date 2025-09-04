import json
import pytest
from unittest.mock import MagicMock, patch

from app.fhir_client import FhirClient


@pytest.fixture
def client():
    c = FhirClient()
    # Patch internals directly
    c.base_url = "http://fake-fhir"
    c.session = MagicMock()
    return c


def test_get_patient_remote(client):
    """Test that remote fetch returns JSON when _use_remote is True."""
    patient_json = {"resourceType": "Patient", "id": "123"}
    client._use_remote = MagicMock(return_value=True)
    mock_response = MagicMock()
    mock_response.json.return_value = patient_json
    # mock_response.raise_for_status.return_value = None
    client.session.get.return_value = mock_response
    result = client.get_patient("123")

    client.session.get.assert_called_once_with("http://fake-fhir/Patient/123", timeout=10)
    assert result == patient_json


def test_get_patient_local(tmp_path, client):
    """Test that local mock path loads Patient.json when present."""
    client._use_remote = MagicMock(return_value=False)

    # Create mock folder and Patient.json
    folder = tmp_path / "123"
    folder.mkdir()
    patient_file = folder / "Patient.json"
    patient_data = {"resourceType": "Patient", "id": "123"}
    patient_file.write_text(json.dumps(patient_data))

    # Patch DATA_DIR inside the module
    with patch("app.fhir_client.DATA_DIR", tmp_path):
        result = client.get_patient("123")

    assert result == patient_data