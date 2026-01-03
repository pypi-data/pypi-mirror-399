from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from prlyn.models import FlowScore, ClassifiedSentence


class FlowAnalyzer:
    def __init__(self, model: Optional[SentenceTransformer] = None):
        self.model = model

    def analyze(self, sentences: List[ClassifiedSentence]) -> FlowScore:
        if not self.model or len(sentences) < 2:
            return FlowScore(sentence_similarities=[], disjointed_indices=[], score=1.0)

        texts = [s.text for s in sentences]
        embeddings = self.model.encode(texts)

        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / np.where(norms == 0, 1, norms)

        similarities = []
        disjointed_indices = []

        for i in range(len(embeddings) - 1):
            sim = float(np.dot(embeddings[i], embeddings[i + 1]))
            similarities.append(sim)
            # Threshold for logical jump
            if sim < 0.3:
                disjointed_indices.append(i)

        avg_sim = sum(similarities) / len(similarities) if similarities else 1.0

        return FlowScore(
            sentence_similarities=similarities,
            disjointed_indices=disjointed_indices,
            score=max(0.0, min(1.0, avg_sim)),
        )
