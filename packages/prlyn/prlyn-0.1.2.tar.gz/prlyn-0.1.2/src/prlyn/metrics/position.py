from prlyn.models import PositionScore, ClassifiedSentence, SentenceLabel
from typing import List


class PositionAnalyzer:
    def analyze(
        self, sentences: List[ClassifiedSentence], text_length: int
    ) -> PositionScore:
        if text_length == 0:
            return PositionScore(
                start_density=0,
                middle_density=0,
                end_density=0,
                buried_instructions=[],
                score=0,
            )

        start_bound = text_length * 0.25
        end_bound = text_length * 0.75

        zone_counts = {"start": 0, "middle": 0, "end": 0}
        buried_indices = []

        for i, sent in enumerate(sentences):
            # Determine zone by midpoint of sentence
            midpoint = (sent.start_char + sent.end_char) / 2

            zone = "middle"
            if midpoint < start_bound:
                zone = "start"
            elif midpoint > end_bound:
                zone = "end"

            is_critical = sent.primary_label in {
                SentenceLabel.INSTRUCTION,
                SentenceLabel.CONSTRAINT,
            }

            if is_critical:
                zone_counts[zone] += 1
                if zone == "middle":
                    buried_indices.append(i)

        total_critical = sum(zone_counts.values())
        if total_critical == 0:
            return PositionScore(
                start_density=0,
                middle_density=0,
                end_density=0,
                buried_instructions=[],
                score=1.0,
            )

        # Simple density: fraction of criticals in that zone (normalized by zone size?)
        # Let's simple use count ratio for now
        s_d = zone_counts["start"] / total_critical
        m_d = zone_counts["middle"] / total_critical
        e_d = zone_counts["end"] / total_critical

        # Penalize middle instructions. Score starts at 1.0, minus middle density
        score = max(0.0, 1.0 - m_d)

        return PositionScore(
            start_density=round(s_d, 2),
            middle_density=round(m_d, 2),
            end_density=round(e_d, 2),
            buried_instructions=buried_indices,
            score=round(score, 2),
        )
