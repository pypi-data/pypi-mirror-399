from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SentenceLabel(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    CONSTRAINT = "CONSTRAINT"
    EXAMPLE = "EXAMPLE"
    FORMAT_SPEC = "FORMAT_SPEC"
    CONTEXT = "CONTEXT"
    UNKNOWN = "UNKNOWN"


class PlaceholderType(str, Enum):
    CODE_BLOCK = "CODE_BLOCK"
    QUOTED_STRING = "QUOTED_STRING"


class Placeholder(BaseModel):
    id: str
    content: str
    type: PlaceholderType
    start_index: int = Field(description="Start index in the original raw text")
    end_index: int = Field(description="End index in the original raw text")


class ClassifiedSentence(BaseModel):
    text: str
    start_char: int = Field(description="Start char index in clean text")
    end_char: int = Field(description="End char index in clean text")
    primary_label: SentenceLabel
    secondary_labels: List[SentenceLabel] = Field(default_factory=list)
    tokens: int = 0


class AmbiguityScore(BaseModel):
    vague_term_density: float
    unresolved_coref_score: float
    hedging_density: float
    vague_terms_found: List[str] = Field(default_factory=list)
    hedging_terms_found: List[str] = Field(default_factory=list)


class NegativeConstraint(BaseModel):
    sentence_index: int
    text: str
    negative_terms: List[str]
    suggestion: str


class PositionScore(BaseModel):
    start_density: float
    middle_density: float
    end_density: float
    buried_instructions: List[int] = Field(
        description="Indices of instructions in the middle zone"
    )
    score: float


class EfficiencyScore(BaseModel):
    actionable_token_ratio: float
    rating: str  # Low, Moderate, Good, High


class ReadabilityScore(BaseModel):
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_syllables_per_word: float


class VulnerabilityScore(BaseModel):
    vulnerability_zones: List[int] = Field(
        description="Sentence indices with vague/unconstrained context"
    )
    has_strong_delimiters: bool
    missing_defensive_anchors: List[str] = Field(default_factory=list)
    reflexive_leakage_risks: List[int] = Field(default_factory=list)
    score: float = Field(description="0.0 to 1.0, higher is better (more secure)")


class FlowScore(BaseModel):
    sentence_similarities: List[float] = Field(
        description="Cosine similarity between adjacent sentences"
    )
    disjointed_indices: List[int] = Field(default_factory=list)
    score: float


class StrengthScore(BaseModel):
    imperative_density: float
    weighted_strength_score: float
    weak_instructions: List[int] = Field(
        description="Indices of instructions with weak verbs (can, would)"
    )


class RedundancyCluster(BaseModel):
    label: SentenceLabel
    sentence_indices: List[int]
    representative_text: str


class RedundancyScore(BaseModel):
    clusters: List[RedundancyCluster] = Field(default_factory=list)
    redundancy_count: int


class ContradictionPair(BaseModel):
    sentence_a_index: int
    sentence_b_index: int
    text_a: str
    text_b: str
    similarity: float
    reason: str


class AnalysisResult(BaseModel):
    raw_text: str
    clean_text: str
    placeholders: Dict[str, Placeholder] = Field(default_factory=dict)
    sentences: List[ClassifiedSentence] = Field(default_factory=list)
    total_tokens: int = 0
    ambiguity_score: Optional[AmbiguityScore] = None
    negative_constraints: List[NegativeConstraint] = Field(default_factory=list)
    position_score: Optional[PositionScore] = None
    efficiency_score: Optional[EfficiencyScore] = None
    readability_score: Optional[ReadabilityScore] = None
    redundancy_score: Optional[RedundancyScore] = None
    contradictions: List[ContradictionPair] = Field(default_factory=list)
    vulnerability_score: Optional[VulnerabilityScore] = None
    flow_score: Optional[FlowScore] = None
    strength_score: Optional[StrengthScore] = None
    model_name: Optional[str] = None
