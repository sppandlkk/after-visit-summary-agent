from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from .llm import LLMClient
from .rag import MedicationKB


def _fmt_date(dt: str) -> str:
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M"
        )
    except Exception:
        return dt


def build_avs(
    patient: Dict[str, Any],
    encounter: Dict[str, Any],
    conditions: List[Dict[str, Any]],
    med_requests: List[Dict[str, Any]],
    med_statements: List[Dict[str, Any]],
    transcript_text: str,
    kb: MedicationKB,
    k: int = 3,
) -> Dict[str, Any]:
    provenance = {
        "patient": [],
        "visit": [],
        "history": [],
        "diagnoses_and_issues": [],
        "treatment_plan": [],
        "follow_up": [],
    }

    # Patient
    name = "unknown"
    if patient.get("name"):
        n = patient["name"][0]
        given = " ".join(n.get("given", []))
        name = (given + " " + n.get("family", "")).strip() or "unknown"
        provenance["patient"].append("FHIR:Patient")
    birth = patient.get("birthDate", "unknown")
    if birth != "unknown":
        provenance["patient"].append("FHIR:Patient.birthDate")
    gender = patient.get("gender", "unknown")
    if gender != "unknown":
        provenance["patient"].append("FHIR:Patient.gender")

    # Visit info from encounter
    visit_date = "unknown"
    visit_time = "unknown"
    if encounter.get("period", {}).get("start"):
        dt = encounter["period"]["start"]
        iso = _fmt_date(dt)
        if len(iso.split()) == 2:
            visit_date, visit_time = iso.split()
        else:
            visit_date = iso
        provenance["visit"].append("FHIR:Encounter.period.start")

    # History from conditions and med statements
    cond_summ = []
    for c in conditions:
        if isinstance(c, dict):
            code = c.get("code", {})
            cond_summ.append(code.get("text", "") if code else "")
        else:
            r = c.get("resource", {})
            cond_summ.append(r.get("code", {}).get("text", ""))
    med_hist = []
    for m in med_statements:
        if isinstance(m, dict):
            med_hist.append(m.get("medicationCodeableConcept", {}).get("text", ""))
        else:
            r = m.get("resource", {})
            med_hist.append(r.get("medicationCodeableConcept", {}).get("text", ""))
    history_text = ""
    if cond_summ:
        history_text += "Conditions: " + "; ".join(
            sorted(set([x for x in cond_summ if x]))
        )
    if med_hist:
        if history_text:
            history_text += " | "
        history_text += "Medications: " + "; ".join(
            sorted(set([x for x in med_hist if x]))
        )
    if history_text:
        provenance["history"].extend(["FHIR:Condition", "FHIR:MedicationStatement"])

    # RAG context from med requests
    meds_now = []
    for r in med_requests:
        if isinstance(r, dict):
            meds_now.append(r.get("medicationCodeableConcept", {}).get("text", ""))
        else:
            meds_now.append(
                r.get("resource", {})
                .get("medicationCodeableConcept", {})
                .get("text", "")
            )
    rag_context = []
    for med in meds_now:
        if not med:
            continue
        for res in kb.retrieve(med, k=k):
            rag_context.append(
                f"# Generic: {res['generic']} | Brand: {res['brand']}\n"
                f"{res['doc']}"
            )
    logging.info(f"{k} RAG docs retrieved for medications: {meds_now}")

    # LLM generation
    llm = LLMClient()
    llm_output = llm.generate_summary(transcript_text, rag_context)
    diag_text = llm_output.get("diagnoses_and_issues", "unknown")
    plan_text = llm_output.get("treatment_plan", "unknown")
    provenance["diagnoses_and_issues"].append("LLM+Transcript")
    provenance["treatment_plan"].append("LLM+Transcript+KB")

    # Follow-up
    follow = "If symptoms worsen, please return or call the clinic."
    for line in transcript_text.splitlines():
        low = line.lower()
        if (
            "follow-up" in low
            or "follow up" in low
            or "see you in" in low
            or "return in" in low
        ):
            follow = line.strip()
            provenance["follow_up"].append("Transcript")
            break

    md = f"""# After Visit Summary

**Patient**  
Name: {name}  
DOB: {birth}  
Sex: {gender}  

**Visit Information**  
Date: {visit_date}  
Time: {visit_time}  

**History**  
{history_text or "unknown"}

**Diagnoses & Issues**  
{diag_text}

**Treatment Plan**  
{plan_text}

**Follow-up**  
{follow}

---  
*Sources:* patient={provenance["patient"]}; visit={provenance["visit"]}; history={provenance["history"]}; dx/issues={provenance["diagnoses_and_issues"]}; plan={provenance["treatment_plan"]}; follow-up={provenance["follow_up"]}
"""

    return {"avs_markdown": md, "provenance": provenance}
