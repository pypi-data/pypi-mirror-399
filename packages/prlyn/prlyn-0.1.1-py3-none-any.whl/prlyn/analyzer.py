"""
Core analyzer module for the Plint package.
"""
from typing import Optional
from prlyn.models import AnalysisResult
from prlyn.preprocessor import Preprocessor
from prlyn.tokenizer import Tokenizer
from prlyn.classifier import Classifier
from prlyn.metrics.ambiguity import AmbiguityAnalyzer
from prlyn.metrics.negation import NegationAnalyzer
from prlyn.metrics.readability import ReadabilityAnalyzer
from prlyn.metrics.efficiency import EfficiencyAnalyzer
from prlyn.metrics.position import PositionAnalyzer
from prlyn.metrics.redundancy import RedundancyAnalyzer
from prlyn.metrics.contradiction import ContradictionAnalyzer
from prlyn.metrics.vulnerability import VulnerabilityAnalyzer
from prlyn.metrics.flow import FlowAnalyzer
from prlyn.metrics.strength import StrengthAnalyzer
from prlyn.awareness import apply_model_awareness
from prlyn.reporting import ReportGenerator


class Analyzer:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.tokenizer = Tokenizer()
        self.classifier = Classifier(self.tokenizer)
        self.report_generator = ReportGenerator()
        self.ambiguity_analyzer = AmbiguityAnalyzer(self.tokenizer)
        self.negation_analyzer = NegationAnalyzer()
        self.readability_analyzer = ReadabilityAnalyzer(self.tokenizer)
        self.efficiency_analyzer = EfficiencyAnalyzer()
        self.position_analyzer = PositionAnalyzer()
        self.vulnerability_analyzer = VulnerabilityAnalyzer()
        self.flow_analyzer = None  # Late binding for model
        self.strength_analyzer = StrengthAnalyzer()

        # Initialize heavy models once
        # Using a shared model for both to save memory
        try:
            self.redundancy_analyzer = RedundancyAnalyzer()  # Loads model
            self.contradiction_analyzer = ContradictionAnalyzer(
                self.redundancy_analyzer.model
            )
            self.flow_analyzer = FlowAnalyzer(self.redundancy_analyzer.model)
        except (ImportError, RuntimeError, ValueError) as e:
            # Log as warning but allow initialization to proceed without heavy models
            # In a production library, we might want to use a proper logger here
            import structlog

            logger = structlog.get_logger()
            logger.warning("failed_to_load_embeddings_model", error=str(e))
            self.redundancy_analyzer = None
            self.contradiction_analyzer = None

    def analyze(
        self, raw_text: str, model_name: Optional[str] = None
    ) -> AnalysisResult:
        """
        Main analysis pipeline for the input text.
        """
        # 1. Preprocess: Extract code/quotes
        clean_text, placeholders = self.preprocessor.process(raw_text)

        # 2. Tokenize: Count tokens (on clean text for now)
        total_tokens = self.tokenizer.count_tokens(clean_text)

        # 3. Classify: Identify sentence types
        sentences = self.classifier.classify(clean_text)

        # 4. Metrics
        ambiguity_score = self.ambiguity_analyzer.analyze(clean_text)
        negative_constraints = self.negation_analyzer.analyze(sentences)
        readability_score = self.readability_analyzer.analyze(
            clean_text, total_sentences=len(sentences)
        )
        efficiency_score = self.efficiency_analyzer.analyze(sentences, total_tokens)
        position_score = self.position_analyzer.analyze(sentences, len(clean_text))

        redundancy_score = None
        contradictions = []
        if self.redundancy_analyzer:
            redundancy_score = self.redundancy_analyzer.analyze(sentences)
        if self.contradiction_analyzer:
            contradictions = self.contradiction_analyzer.analyze(sentences)

        vulnerability_score = self.vulnerability_analyzer.analyze(sentences, clean_text)

        flow_score = None
        if self.flow_analyzer:
            flow_score = self.flow_analyzer.analyze(sentences)

        strength_score = self.strength_analyzer.analyze(sentences)

        # 5. Construct Result
        result = AnalysisResult(
            raw_text=raw_text,
            clean_text=clean_text,
            placeholders=placeholders,
            sentences=sentences,
            total_tokens=total_tokens,
            ambiguity_score=ambiguity_score,
            negative_constraints=negative_constraints,
            position_score=position_score,
            efficiency_score=efficiency_score,
            readability_score=readability_score,
            redundancy_score=redundancy_score,
            contradictions=contradictions,
            vulnerability_score=vulnerability_score,
            flow_score=flow_score,
            strength_score=strength_score,
            model_name=model_name,
        )

        # 6. Apply Model Awareness
        return apply_model_awareness(result, model_name)
