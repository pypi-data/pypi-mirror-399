from prlyn.models import (
    AnalysisResult,
    SentenceLabel,
    ClassifiedSentence,
    PositionScore,
    AmbiguityScore,
    StrengthScore,
    VulnerabilityScore,
)
from prlyn.template_generator import generate_improvement_template


def test_generate_template_basic():
    # Mock minimal analysis
    analysis = AnalysisResult(
        raw_text="Try to do stuff.",
        clean_text="Try to do stuff.",
        sentences=[
            ClassifiedSentence(
                text="Try to do stuff.",
                start_char=0,
                end_char=16,
                primary_label=SentenceLabel.INSTRUCTION,
            )
        ],
    )

    template = generate_improvement_template(analysis)
    assert "## Original Prompt" in template
    assert "Try to do stuff." in template
    assert "## Your Task" in template


def test_generate_template_with_issues():
    # Mock analysis with specific issues
    analysis = AnalysisResult(
        raw_text="Try to do stuff.",
        clean_text="Try to do stuff.",
        sentences=[
            ClassifiedSentence(
                text="Try to do stuff.",
                start_char=0,
                end_char=16,
                primary_label=SentenceLabel.INSTRUCTION,
            )
        ],
        ambiguity_score=AmbiguityScore(
            vague_term_density=0.1,
            unresolved_coref_score=0,
            hedging_density=0.1,
            vague_terms_found=["stuff"],
            hedging_terms_found=["try to"],
        ),
        position_score=PositionScore(
            start_density=0,
            middle_density=1,
            end_density=0,
            score=0.5,
            buried_instructions=[0],
        ),
        strength_score=StrengthScore(
            imperative_density=0, weighted_strength_score=0, weak_instructions=[0]
        ),
        vulnerability_score=VulnerabilityScore(
            vulnerability_zones=[], has_strong_delimiters=False, score=0.5
        ),
    )

    template = generate_improvement_template(analysis)

    # Check for specific actionable instructions
    assert "Buried Instructions" in template
    assert "Move to START or END" in template

    assert "Vague Terms" in template
    assert 'Replace "stuff"' in template

    assert "Hedging Terms" in template
    assert 'Remove or strengthen "try to"' in template

    assert "Weak Verbs" in template
    assert "Use 'must', 'always', or 'ensure'" in template

    assert "Missing Delimiters" in template
