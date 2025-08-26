import json
import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.model = os.getenv("AI_MODEL", "gemini-1.5-flash")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")

    def build_prompt(self, transcript: str, rag_docs: List[str]) -> str:
        kb_text = "\n\n---\n".join(rag_docs) if rag_docs else "No medication knowledge available."
        prompt = f"""You are a clinical AI assistant generating **After Visit Summary** sections.

            Step 1: Summarize the transcript into diagnoses_and_issues and treatment_plan.
            Step 2: In treatment_plan, if any medication is prescribed, identify any relevant information in the Medication knowledge that supplements or changes the transcript.
            Step 3: Put the relevant medication information into treatment_plan, right after the medication is mentioned.
            Step 4: Merge the two into final JSON.

            Rules:
            - Use ONLY the transcript and medication knowledge provided.
            - If info is missing, write "unknown". Do not fabricate.
            - Be professional, patient-friendly, and clinically accurate.
            - Output **strict JSON** with two fields:
            {{
            "diagnoses_and_issues": "string",
            "treatment_plan": "string"
            }}

            Transcript (doctor-patient dialogue):
            {transcript}

            Medication knowledge (retrieved snippets):
            {kb_text}

            Return JSON only, no extra commentary.
            """
        return prompt

    def parse_llm_response(self, raw_text: str) -> Dict:
        logging.debug(f"Raw LLM response: {raw_text}")

        # Remove markdown code fences if present
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.DOTALL)

        try:
            parsed = json.loads(cleaned)
            if "diagnoses_and_issues" not in parsed:
                parsed["diagnoses_and_issues"] = "unknown"
            if "treatment_plan" not in parsed:
                parsed["treatment_plan"] = "unknown"
            return parsed
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {e}\nCleaned text: {cleaned}")
            return {
                "diagnoses_and_issues": "unknown",
                "treatment_plan": "unknown",
            }

    def generate_summary(self, transcript: str, rag_docs: List[str]) -> Dict:
        prompt = self.build_prompt(transcript, rag_docs)
        logging.debug(f"Provider: {self.provider}")

        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            response = model.generate_content(prompt)
            raw_text = response.text
        elif self.provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4.0-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            raw_text = response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return self.parse_llm_response(raw_text)