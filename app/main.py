from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import Body, FastAPI
from pydantic import BaseModel

from .fhir_client import FhirClient
from .rag import MedicationKB
from .summarizer import build_avs

app = FastAPI(title="AVS Agent Demo (FHIR)")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GenerateAVSRequest(BaseModel):
    patient_fhir_id: str
    transcript_path: Optional[str] = None
    transcript_text: Optional[str] = None
    k: int = 4


@app.post("/generate_avs")
def generate_avs(req: GenerateAVSRequest = Body(...)):
    fhir = FhirClient()
    patient = fhir.get_patient(req.patient_fhir_id)
    encounter = fhir.get_latest_encounter(req.patient_fhir_id)
    conds = fhir.list_conditions(req.patient_fhir_id)
    med_reqs = fhir.list_medication_requests(req.patient_fhir_id)
    med_stmts = fhir.list_medication_statements(req.patient_fhir_id)

    BASE_DIR = Path(__file__).resolve().parent.parent  # project root
    transcript_path = BASE_DIR / req.transcript_path

    transcript = None

    if req.transcript_path and transcript_path.exists():
        with open(transcript_path, "r") as f:
            transcript = f.read()
    elif req.transcript_text:
        transcript = req.transcript_text
    else:
        # Better: raise error, so you know transcript is missing
        raise FileNotFoundError(
            f"No transcript found. Path checked: {transcript_path}, and no transcript_text provided."
        )

    logging.info(f"Loaded transcript for patient {req.patient_fhir_id} (length={len(transcript) if transcript else 0})")

    # initialize RAG Knowledge Base
    kb = MedicationKB()
    result = build_avs(
        patient, encounter, conds, med_reqs, med_stmts, transcript, kb, k=req.k
    )

    # Save output markdown to local Path
    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    out_path = outputs / f"AVS_{req.patient_fhir_id}.md"
    out_path.write_text(result["avs_markdown"], encoding="utf-8")

    return {"ok": True, "output_markdown_path": str(out_path), **result}
