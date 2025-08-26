from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MedicationKB:
    """
    Medication Knowledge Base using TF-IDF + cosine similarity.
    Loads a single CSV file: 'data/med_kb/medications.csv'.
    """

    def __init__(self):
        # Use project root as base
        BASE_DIR = Path(__file__).resolve().parent.parent  # project root
        kb_file = BASE_DIR / "data/med_kb/medications.csv"

        if not kb_file.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {kb_file}")

        # Read CSV
        self.df = pd.read_csv(kb_file)
        self.docs: List[str] = []

        # Convert each row into a text document
        for _, row in self.df.iterrows():
            doc = (
                f"Generic: {row['Generic']}\n"
                f"Brand: {row['Brand']}\n"
                f"Class: {row['Class']}\n"
                f"Indication: {row['Indication']}\n"
                f"Side effects: {row['SideEffect']}\n"
                f"Monitoring: {row['Monitoring']}\n"
                f"NDC: {row['NDC']}\n"
                f"GPI: {row['GPI']}"
            )
            self.docs.append(doc)

        if self.docs:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.docs)
        else:
            self.vectorizer = None
            self.matrix = None

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant medication entries based on cosine similarity.
        """
        if not self.docs:
            return []

        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]

        # argsort() returns indices sorted ascending; [::-1] reverses to descending
        idxs = sims.argsort()[::-1][:k]

        results = []
        for i in idxs:
            results.append({
                "score": float(sims[i]),
                "doc": self.docs[i],
                "generic": self.df.iloc[i]["Generic"],
                "brand": self.df.iloc[i]["Brand"],
            })
        return results
