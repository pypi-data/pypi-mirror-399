from typing import List
from prlyn.models import StrengthScore, ClassifiedSentence, SentenceLabel

STRONG_VERBS = {"must", "shall", "always", "never", "ensure", "require"}
MODERATE_VERBS = {"should", "please", "expect", "need"}
WEAK_VERBS = {
    "can",
    "may",
    "might",
    "could",
    "try",
    "possibly",
    "optionally",
    "probably",
}


class StrengthAnalyzer:
    def analyze(self, sentences: List[ClassifiedSentence]) -> StrengthScore:
        instructions = [
            s for s in sentences if s.primary_label == SentenceLabel.INSTRUCTION
        ]
        if not instructions:
            return StrengthScore(
                imperative_density=0.0,
                weighted_strength_score=0.0,
                weak_instructions=[],
            )

        weak_indices = []
        weighted_sum = 0.0

        for i, s in enumerate(sentences):
            if s.primary_label != SentenceLabel.INSTRUCTION:
                continue

            text_lower = s.text.lower()

            # Simple keyword check for weight assignment
            if any(v in text_lower for v in STRONG_VERBS):
                weighted_sum += 1.0
            elif any(v in text_lower for v in MODERATE_VERBS):
                weighted_sum += 0.7
            elif any(v in text_lower for v in WEAK_VERBS):
                weighted_sum += 0.3
                weak_indices.append(i)
            else:
                # Default to moderate
                weighted_sum += 0.6

        avg_strength = weighted_sum / len(instructions)
        density = len(instructions) / len(sentences) if sentences else 0.0

        return StrengthScore(
            imperative_density=density,
            weighted_strength_score=avg_strength,
            weak_instructions=weak_indices,
        )
