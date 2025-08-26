# After Visit Summary

        **Patient**  
        Name: Jane Doe  
        DOB: 1975-04-12  
        Sex: female  

        **Visit Information**  
        Date: 2025-08-25  
        Time: 09:30  

        **History**  
        Conditions: Hypertension, type 2 diabetes mellitus | Medications: Atorvastatin 20 mg tablet

        **Diagnoses & Issues**  
        Elevated blood pressure (150/95), mild kidney function decline, slightly high cholesterol, and type 2 diabetes mellitus.

        **Treatment Plan**  
        The patient was started on Lisinopril 10mg once daily for hypertension. Lisinopril is an ACE inhibitor indicated for hypertension, heart failure, and post-MI. Common side effects include cough, dizziness, and hyperkalemia. Serious risks include angioedema (requiring emergency care) and renal function changes.  The patient should rise slowly to avoid dizziness and report any facial/lip swelling immediately. Blood pressure, serum creatinine, and potassium should be monitored 1-2 weeks after dose changes.  The patient should continue taking Metformin for diabetes as prescribed. Metformin is a biguanide indicated for type 2 diabetes mellitus. Common side effects include GI upset (nausea, diarrhea), and metallic taste. Serious risks include rare lactic acidosis (avoid in severe renal impairment).  The patient should take Metformin with meals and contact the clinic if persistent GI side effects occur.  A1c should be monitored every 3 months until stable, and renal function (eGFR) at baseline and periodically.  Lifestyle modifications including a low-sodium diet, regular exercise (at least 30 minutes daily), and weight monitoring were recommended.  The patient will have a follow-up appointment in 4 weeks to review blood pressure, labs, and potentially adjust the Lisinopril dosage.

        **Follow-up**  
        Patient: Should I schedule follow-up?

        ---  
        *Sources:* patient=['FHIR:Patient', 'FHIR:Patient.birthDate', 'FHIR:Patient.gender']; visit=['FHIR:Encounter.period.start']; history=['FHIR:Condition', 'FHIR:MedicationStatement']; dx/issues=['LLM+Transcript']; plan=['LLM+Transcript+KB']; follow-up=['Transcript']
    