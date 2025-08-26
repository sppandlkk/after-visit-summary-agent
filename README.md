# After Visit Summary (AVS) AI Agent

This project is a demo AI agent that generates **After Visit Summaries (AVS)** for patients by combining **FHIR patient data**, **doctor-patient transcripts**, and optional **RAG knowledge base** context. It supports **OpenAI** and **Google Gemini** models.

---

## Features

* Connects to a FHIR server (or mock data) to extract the following FHIR resources:
  * Patient
  * Conditions
  * Medications
  * Encounters
* Generates AVS JSON containing:

  * `diagnoses_and_issues`
  * `treatment_plan` (integrates medications and RAG context in free text)
* Configurable LLM provider: OpenAI or Gemini
* Supports **mock FHIR data** for local testing

---

## Requirements

* Python 3.12+
* [uv](https://uv.run/) for environment management

---

## Setup

1. Clone the repo:

```bash
git clone <repo-url>
cd after-visit-summary-agent
```

2. Install dependencies with `uv`:

```bash
uv sync
```

3. Copy `.env.sample` to `.env` and fill in your API keys:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
FHIR_BASE_URL=http://your-fhir-server.com
```

---

## Running the API

Start the FastAPI server:

```bash
uv run uvicorn app.main:app --env-file=.env --reload --log-level debug
```

Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

---

## Mock Data

You can use the included mock FHIR data for testing:

```
data/mock_fhir/demo-patient-1/
data/mock_fhir/demo-patient-2/
```

Transcripts:

```
data/transcripts/visit1_raw.txt  # demo-patient-1
data/transcripts/visit2_raw.txt  # demo-patient-2
```

---

## Example API Call

### Patient 1

```bash
curl -X POST http://127.0.0.1:8000/generate_avs \
  -H "Content-Type: application/json" \
  -d '{
    "patient_fhir_id": "demo-patient-1",
    "transcript_path": "data/transcripts/visit1_raw.txt",
    "k": 4
  }'
```

### Patient 2

```bash
curl -X POST http://127.0.0.1:8000/generate_avs \
  -H "Content-Type: application/json" \
  -d '{
    "patient_fhir_id": "demo-patient-2",
    "transcript_path": "data/transcripts/visit2_raw.txt",
    "k": 4
  }'
```

**Response Example:**

```json
{
  "diagnoses_and_issues": "Type 2 diabetes mellitus with elevated blood pressure...",
  "treatment_plan": "Increased metformin to 500 mg twice daily with meals. Start Lisinopril 10 mg daily. Monitor blood pressure and kidney function. Lifestyle: low sodium diet, regular exercise, glucose log. Follow-up in 3-4 weeks..."
}
```

---

## Notes

* If using RAG knowledge base, place reference documents in your workflow and pass them in `rag_docs` parameter; the LLM will attempt to integrate them into the treatment plan.
* `transcript_path` must be relative to project root or an absolute path.
* If transcript is missing, you can alternatively pass `transcript_text` in the request.
