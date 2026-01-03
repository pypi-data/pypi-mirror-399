import typing
from prlyn.models import ClassifiedSentence, SentenceLabel, EfficiencyScore


class EfficiencyAnalyzer:
    def analyze(
        self, sentences: typing.List[ClassifiedSentence], total_tokens: int
    ) -> EfficiencyScore:
        if total_tokens == 0:
            return EfficiencyScore(actionable_token_ratio=0.0, rating="Low")

        actionable_tokens = 0
        for sent in sentences:
            if sent.primary_label in {
                SentenceLabel.INSTRUCTION,
                SentenceLabel.CONSTRAINT,
                SentenceLabel.FORMAT_SPEC,
            }:
                actionable_tokens += sent.tokens

        ratio = actionable_tokens / total_tokens

        rating = "Low"
        if ratio > 0.7:
            rating = "High"
        elif ratio > 0.4:
            rating = "Good"
        elif ratio > 0.2:
            rating = "Moderate"

        return EfficiencyScore(actionable_token_ratio=round(ratio, 2), rating=rating)
