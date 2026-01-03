"""
Reporting module for generating analysis reports in various formats.
"""
from prlyn.models import AnalysisResult


class ReportGenerator:
    def generate_json_report(self, result: AnalysisResult) -> str:
        return result.model_dump_json(indent=2)

    def generate_markdown_report(self, result: AnalysisResult) -> str:
        lines = []
        lines.append("# Plint Analysis Report")
        lines.append(f"**Tokens**: {result.total_tokens}")

        # 1. Overall Score (Mockup composite)
        # Assuming we want a single health score? Not explicitly in requirements but good for summary.
        # Let's focused on detailed sections.

        # 2. Readability
        if result.readability_score:
            r = result.readability_score
            lines.append("## Readability")
            lines.append(
                f"- **Flesch Reading Ease**: {r.flesch_reading_ease} (Target: >60)"
            )
            lines.append(f"- **Grade Level**: {r.flesch_kincaid_grade} (Target: <8)")

        # 3. Efficiency & Position
        if result.efficiency_score:
            e = result.efficiency_score
            lines.append("## Efficiency")
            lines.append(f"- **Rating**: {e.rating}")
            lines.append(f"- **Actionable Ratio**: {e.actionable_token_ratio:.2f}")

        if result.position_score:
            p = result.position_score
            lines.append("## Structure")
            lines.append(f"- **Position Score**: {p.score:.2f}")
            if p.buried_instructions:
                lines.append(
                    f"- **Warning**: {len(p.buried_instructions)} instructions found in the middle zone (buried)."
                )

        # 4. Security & Vulnerability
        if result.vulnerability_score:
            v = result.vulnerability_score
            lines.append("## Security (Design-time)")
            lines.append(f"- **Vulnerability Score**: {v.score:.2f}")
            lines.append(
                f"- **Strong Delimiters**: {'✅' if v.has_strong_delimiters else '❌'}"
            )
            if v.missing_defensive_anchors:
                lines.append(
                    f"- **Missing Anchors**: {', '.join(v.missing_defensive_anchors)}"
                )
            if v.vulnerability_zones:
                lines.append(
                    f"- **Warning**: Found {len(v.vulnerability_zones)} vulnerable zones regarding user input handling."
                )

        # 5. Advanced Linguistics
        if result.flow_score:
            f = result.flow_score
            lines.append("## Advanced Linguistics")
            lines.append(f"- **Flow Cohesion**: {f.score:.2f}")
            if f.disjointed_indices:
                lines.append(
                    f"- **Warning**: Logic jumps detected between sentences {f.disjointed_indices}."
                )

        if result.strength_score:
            s = result.strength_score
            lines.append(
                f"- **Instructional Strength**: {s.weighted_strength_score:.2f}"
            )
            if s.weak_instructions:
                lines.append(
                    f"- **Warning**: {len(s.weak_instructions)} instructions use weak verbs (e.g., 'can', 'try')."
                )

        # 4. Critical Issues
        issues = []

        # Negations
        for nc in result.negative_constraints:
            issues.append(f'- **Negative Constraint**: "{nc.text}". {nc.suggestion}')

        # Contradictions
        for c in result.contradictions:
            issues.append(
                f'- **Contradiction**: "{c.text_a}" vs "{c.text_b}". Reason: {c.reason}'
            )

        # Redundancy
        if result.redundancy_score and result.redundancy_score.clusters:
            for cluster in result.redundancy_score.clusters:
                issues.append(
                    f'- **Redundancy**: {len(cluster.sentence_indices)} sentences similar to "{cluster.representative_text}".'
                )

        # Ambiguity
        if result.ambiguity_score:
            a = result.ambiguity_score
            if a.vague_terms_found:
                issues.append(
                    f"- **Vague Terms**: Found {', '.join(a.vague_terms_found)}."
                )
            if a.hedging_terms_found:
                issues.append(
                    f"- **Hedging**: Found {', '.join(a.hedging_terms_found)}."
                )

        if issues:
            lines.append("## Critical Issues & Recommendations")
            for issue in issues:
                lines.append(issue)
        else:
            lines.append("## Critical Issues")
            lines.append("No critical issues found.")

        return "\n".join(lines)

    def generate_table_report(self, result: AnalysisResult) -> str:
        lines = []
        lines.append("# Plint Summary Report")
        lines.append("")
        lines.append("| Metric | Value | Reference | Status |")
        lines.append("| :--- | :--- | :--- | :--- |")

        # Readability
        if result.readability_score:
            r = result.readability_score
            lines.append(
                f"| Flesch Reading Ease | {r.flesch_reading_ease} | >60 | {'✅' if r.flesch_reading_ease > 60 else '⚠️'} |"
            )
            lines.append(
                f"| Grade Level | {r.flesch_kincaid_grade} | <8 | {'✅' if r.flesch_kincaid_grade < 8 else '⚠️'} |"
            )

        # Efficiency
        if result.efficiency_score:
            e = result.efficiency_score
            lines.append(
                f"| Actionable Ratio | {e.actionable_token_ratio:.2f} | >0.7 | {'✅' if e.actionable_token_ratio > 0.7 else '⚠️'} |"
            )

        # Position
        if result.position_score:
            p = result.position_score
            lines.append(
                f"| Position Score | {p.score:.2f} | >0.8 | {'✅' if p.score > 0.8 else '⚠️'} |"
            )

        # New Metrics Summary
        if result.vulnerability_score:
            v = result.vulnerability_score
            lines.append(
                f"| Security Score | {v.score:.2f} | >0.7 | {'✅' if v.score > 0.7 else '⚠️'} |"
            )

        if result.flow_score:
            f = result.flow_score
            lines.append(
                f"| Flow Cohesion | {f.score:.2f} | >0.6 | {'✅' if f.score > 0.6 else '⚠️'} |"
            )

        if result.strength_score:
            s = result.strength_score
            lines.append(
                f"| Instruction Strength | {s.weighted_strength_score:.2f} | >0.7 | {'✅' if s.weighted_strength_score > 0.7 else '⚠️'} |"
            )

        lines.append("")

        # Critical Issues Summary
        issues_count = (
            len(result.negative_constraints)
            + len(result.contradictions)
            + (1 if result.redundancy_score and result.redundancy_score.clusters else 0)
            + (
                1
                if result.ambiguity_score
                and (
                    result.ambiguity_score.vague_terms_found
                    or result.ambiguity_score.hedging_terms_found
                )
                else 0
            )
        )

        if issues_count > 0:
            lines.append("## Issues & Recommendations")
            for nc in result.negative_constraints:
                lines.append(f'- **Negation**: "{nc.text}" (Try positive reframe)')
            if result.ambiguity_score and result.ambiguity_score.vague_terms_found:
                lines.append(
                    f"- **Vague Terms**: {', '.join(result.ambiguity_score.vague_terms_found)}"
                )
            if result.ambiguity_score and result.ambiguity_score.hedging_terms_found:
                lines.append(
                    f"- **Hedging**: {', '.join(result.ambiguity_score.hedging_terms_found)}"
                )
            for c in result.contradictions:
                lines.append(f"- **Contradiction**: {c.reason}")
        else:
            lines.append("## Status: Clean")
            lines.append("No critical issues detected.")

        lines.append("")
        lines.append("---")
        lines.append("### How to Read this Report")
        lines.append("| Metric | Scale | Better | Definition |")
        lines.append("| :--- | :--- | :--- | :--- |")
        lines.append(
            "| **Reading Ease** | 0 - 100 | High | Accessibility of the text. (>60 is standard) |"
        )
        lines.append(
            "| **Grade Level** | 1 - 16+ | Low | US Grade level required to read. (<8 is standard) |"
        )
        lines.append(
            "| **Actionable Ratio** | 0.0 - 1.0 | High | Ratio of instruction words to filler words. |"
        )
        lines.append(
            "| **Position Score** | 0.0 - 1.0 | High | Instructional density at start/end. (>0.8 avoids 'buried' instructions) |"
        )

        return "\n".join(lines)
