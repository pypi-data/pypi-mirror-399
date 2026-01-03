from typing import List
from prlyn.models import ContradictionPair, ClassifiedSentence, SentenceLabel
from sentence_transformers import SentenceTransformer, util


class ContradictionAnalyzer:
    def __init__(self, model):
        # reuse the model from redundancy analyzer if passed, or new one
        if isinstance(model, str):
            self.model = SentenceTransformer(model)
        else:
            self.model = model

    def analyze(self, sentences: List[ClassifiedSentence]) -> List[ContradictionPair]:
        constraints_indices = [
            i
            for i, s in enumerate(sentences)
            if s.primary_label == SentenceLabel.CONSTRAINT
        ]

        if len(constraints_indices) < 2:
            return []

        texts = [sentences[i].text for i in constraints_indices]
        embeddings = self.model.encode(texts)

        # Calculate cosine similarity matrix
        # util.cos_sim returns a Tensor, convert to numpy
        cosine_scores = util.cos_sim(embeddings, embeddings).numpy()

        contradictions = []

        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = cosine_scores[i][j]

                # Check for high similarity (meaning they talk about the same thing)
                if sim > 0.60:
                    text_a = texts[i]
                    text_b = texts[j]

                    # Check for opposing polarity (Simple Heuristic)
                    # Ideally we'd use an NLI model, but for now we look for negation mismatch
                    # on similar sentences.
                    neg_a = self.has_negation(text_a)
                    neg_b = self.has_negation(text_b)

                    if neg_a != neg_b:
                        contradictions.append(
                            ContradictionPair(
                                sentence_a_index=constraints_indices[i],
                                sentence_b_index=constraints_indices[j],
                                text_a=text_a,
                                text_b=text_b,
                                similarity=float(sim),
                                reason=f"High similarity ({sim:.2f}) with opposing polarity",
                            )
                        )

        return contradictions

    def has_negation(self, text: str) -> bool:
        negs = {"not", "never", "no ", "don't", "shouldn't", "can't", "won't"}
        text_lower = text.lower()
        return any(n in text_lower for n in negs)
