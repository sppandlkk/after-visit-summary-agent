from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalMedKB:
    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir
        self.docs: List[str] = []
        self.paths: List[Path] = []
        for p in sorted(kb_dir.glob("*.md")):
            txt = p.read_text(encoding="utf-8")
            self.docs.append(txt)
            self.paths.append(p)
        if self.docs:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.docs)
        else:
            self.vectorizer = None
            self.matrix = None

    def retrieve(self, query: str, k: int = 4) -> List[Dict]:
        if not self.docs:
            return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        idxs = sims.argsort()[::-1][:k]
        results = []
        for i in idxs:
            results.append({
                "path": str(self.paths[i].name),
                "score": float(sims[i]),
                "snippet": self.docs[i][:1200]
            })
        return results
