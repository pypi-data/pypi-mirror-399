"""
Template generator for actionable prompt improvement instructions.

This module generates data-driven, actionable rewrite templates
that AI coding assistants can use to improve prompts.
"""
from prlyn.models import AnalysisResult


def generate_improvement_template(analysis: AnalysisResult) -> str:
    """
    Generate an actionable rewrite template from analysis results.

    Args:
        analysis: The AnalysisResult from analyzing a prompt.

    Returns:
        A populated meta-prompt with specific improvement instructions.
    """
    sections = []

    # Header
    sections.append("## Prompt Rewrite Instructions\n")
    sections.append("You are given an original prompt and a detailed analysis.")
    sections.append("Rewrite the prompt by applying the following SPECIFIC fixes.\n")

    # 1. Buried Instructions
    if analysis.position_score and analysis.position_score.buried_instructions:
        sections.append("### 1. Buried Instructions (Move to Start or End)\n")
        sections.append(
            "The following instructions are buried in the middle of the prompt."
        )
        sections.append(
            "Move them to the START (for critical setup) or END (for final reminders):\n"
        )
        for idx in analysis.position_score.buried_instructions:
            if idx < len(analysis.sentences):
                sent = analysis.sentences[idx]
                sections.append(
                    f'- **Sentence {idx + 1}**: "{sent.text[:80]}..." → Move to START or END.'
                )
        sections.append("")

    # 2. Vague Terms
    if analysis.ambiguity_score and analysis.ambiguity_score.vague_terms_found:
        sections.append("### 2. Vague Terms (Replace with Precise Alternatives)\n")
        sections.append(
            "Replace the following vague terms with specific, concrete alternatives:\n"
        )
        for term in analysis.ambiguity_score.vague_terms_found:
            sections.append(f'- Replace "{term}" with a specific noun or quantity.')
        sections.append("")

    # 3. Hedging Terms
    if analysis.ambiguity_score and analysis.ambiguity_score.hedging_terms_found:
        sections.append("### 3. Hedging Terms (Strengthen or Remove)\n")
        sections.append("Remove hedging language to make instructions more direct:\n")
        for term in analysis.ambiguity_score.hedging_terms_found:
            sections.append(
                f"- Remove or strengthen \"{term}\" (e.g., 'maybe' → remove, 'try to' → 'always')."
            )
        sections.append("")

    # 4. Weak Instructions
    if analysis.strength_score and analysis.strength_score.weak_instructions:
        sections.append("### 4. Weak Verbs (Strengthen)\n")
        sections.append("The following instructions use weak verbs. Strengthen them:\n")
        for idx in analysis.strength_score.weak_instructions:
            if idx < len(analysis.sentences):
                sent = analysis.sentences[idx]
                sections.append(
                    f"- **Sentence {idx + 1}**: \"{sent.text[:80]}...\" → Use 'must', 'always', or 'ensure'."
                )
        sections.append("")

    # 5. Missing Delimiters
    if (
        analysis.vulnerability_score
        and not analysis.vulnerability_score.has_strong_delimiters
    ):
        sections.append("### 5. Missing Delimiters (Add Separation)\n")
        sections.append(
            "Add clear delimiters (e.g., ```xml, <user_input>, ---) to separate:\n"
        )
        sections.append("- System instructions from user-provided content.")
        sections.append("- Different logical sections of the prompt.\n")

    # 6. Flow Issues
    if analysis.flow_score and analysis.flow_score.disjointed_indices:
        sections.append("### 6. Flow Issues (Improve Transitions)\n")
        sections.append(
            "The following sentences have low semantic connection to their neighbors.\n"
        )
        sections.append(
            "Add transitional phrases or reorder for better logical flow:\n"
        )
        for idx in analysis.flow_score.disjointed_indices:
            if idx < len(analysis.sentences):
                sent = analysis.sentences[idx]
                sections.append(f'- **Sentence {idx + 1}**: "{sent.text[:60]}..."')
        sections.append("")

    # 7. Contradictions
    if analysis.contradictions:
        sections.append("### 7. Contradictions (Resolve)\n")
        sections.append(
            "The following sentence pairs may contradict each other. Resolve or clarify:\n"
        )
        for pair in analysis.contradictions[:3]:  # Limit to 3
            sections.append(
                f"- **Sentence {pair.sentence_a_index + 1}** vs **Sentence {pair.sentence_b_index + 1}**:"
            )
            sections.append(f'  - "{pair.text_a[:50]}..."')
            sections.append(f'  - "{pair.text_b[:50]}..."')
            sections.append(f"  - Reason: {pair.reason}")
        sections.append("")

    # Original Prompt Section
    sections.append("---\n")
    sections.append("## Original Prompt\n")
    sections.append("```")
    sections.append(analysis.raw_text)
    sections.append("```\n")

    # Task
    sections.append("---\n")
    sections.append("## Your Task\n")
    sections.append("Rewrite the prompt above, applying ALL the fixes listed.")
    sections.append("Preserve the original intent and meaning.")
    sections.append("Output ONLY the rewritten prompt, no explanations.")

    return "\n".join(sections)
