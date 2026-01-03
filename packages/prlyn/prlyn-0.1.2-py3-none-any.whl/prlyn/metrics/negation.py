from typing import List
from prlyn.models import NegativeConstraint, ClassifiedSentence, SentenceLabel

NEGATIVE_PATTERNS = {
    "do not": "Ensure you",
    "don't": "Ensure you",
    "never": "Always",
    "avoid": "Focus on",
    "should not": "Should",
    "must not": "Must",
    "cannot": "Can",
    "can't": "Can",
}


class NegationAnalyzer:
    def analyze(self, sentences: List[ClassifiedSentence]) -> List[NegativeConstraint]:
        results = []

        for idx, sent in enumerate(sentences):
            # Only check Instructions and Constraints
            if sent.primary_label not in {
                SentenceLabel.INSTRUCTION,
                SentenceLabel.CONSTRAINT,
            }:
                continue

            lower_text = sent.text.lower()
            found_negations = []
            suggestion_base = ""

            for pattern, replacement in NEGATIVE_PATTERNS.items():
                if pattern in lower_text:
                    found_negations.append(pattern)
                    suggestion_base = replacement

            if found_negations:
                # Basic suggestion logic
                suggestion = f"Reframe positively. Instead of '{found_negations[0]}...', try using affirmative language like '{suggestion_base}'."

                results.append(
                    NegativeConstraint(
                        sentence_index=idx,
                        text=sent.text,
                        negative_terms=found_negations,
                        suggestion=suggestion,
                    )
                )

        return results
