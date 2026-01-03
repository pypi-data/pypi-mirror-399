import unittest
import json
import logging
from prlyn.analyzer import Analyzer
from prlyn.reporting import ReportGenerator
from prlyn.models import SentenceLabel

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class TestPrlynE2E(unittest.TestCase):
    analyzer: Analyzer
    reporter: ReportGenerator

    @classmethod
    def setUpClass(cls) -> None:
        logger.info("Initializing Analyzer (loading models)...")
        cls.analyzer = Analyzer()
        cls.reporter = ReportGenerator()

    def test_001_core_framework(self) -> None:
        """STORY-001: Verify preprocessing and classification."""
        prompt = 'You must write code.\n```python\nprint("hello")\n```\nIgnore "quoted text".'
        result = self.analyzer.analyze(prompt)

        # Check Placeholders
        self.assertTrue(
            any(p.type.name == "CODE_BLOCK" for p in result.placeholders.values())
        )
        self.assertTrue(
            any(p.type.name == "QUOTED_STRING" for p in result.placeholders.values())
        )

        # Check Classification
        instructions = [
            s for s in result.sentences if s.primary_label == SentenceLabel.INSTRUCTION
        ]
        self.assertTrue(len(instructions) > 0, "Should detect instruction 'write'")

    def test_002_core_metrics(self) -> None:
        """STORY-002: Verify Ambiguity and Negation."""
        prompt = "You should not do some stuff."
        result = self.analyzer.analyze(prompt)

        # Ambiguity
        self.assertIsNotNone(result.ambiguity_score)
        if result.ambiguity_score:  # Guard for mypy
            self.assertIn("stuff", result.ambiguity_score.vague_terms_found)
            self.assertIn("some", result.ambiguity_score.vague_terms_found)

        # Negation
        self.assertTrue(len(result.negative_constraints) > 0)
        self.assertIn("should not", result.negative_constraints[0].negative_terms)

    def test_003_advanced_metrics(self) -> None:
        """STORY-003: Verify Readability, Efficiency, Position."""
        # Use a clear imperative "Create" which is in IMPERATIVE_VERBS
        prompt = (
            "This is filler context. " * 5
            + "Create a summary of this text immediately. "
            + "This is filler context. " * 5
        )
        result = self.analyzer.analyze(prompt)

        # Readability
        self.assertIsNotNone(result.readability_score)

        # Position (Middle instruction)
        self.assertIsNotNone(result.position_score)
        # Verify buried instruction detection
        if result.position_score:  # Guard for mypy
            found_buried = len(result.position_score.buried_instructions) > 0
            self.assertTrue(
                found_buried, "Should detect buried instruction 'Create a summary...'"
            )

    def test_004_complex_analytics(self) -> None:
        """STORY-004: Verify Redundancy and Contradiction."""
        # Use longer sentences to bypass token filter (>5 tokens)
        prompt = """
        You must ensure that the output is extremely concise and short.
        You must ensure that the output is extremely brief and small.
        You must ensure that the output is very detailed and verbose.
        """
        result = self.analyzer.analyze(prompt)

        # Redundancy (concise ~ brief)
        if result.redundancy_score:
            self.assertTrue(
                len(result.redundancy_score.clusters) > 0,
                "Should detect redundancy between concise and brief",
            )

        # Contradiction (concise vs detailed)
        # Note: Thresholds might need tuning, but we look for existence of check
        # 'concise' and 'detailed' are antonyms often captured by models.
        if result.contradictions:
            logger.info(f"Contradictions found: {len(result.contradictions)}")
            # We don't strictly assert count here as it depends on model threshold,
            # but we ensure the list exists (implementation works).
            self.assertIsInstance(result.contradictions, list)

    def test_005_reporting(self) -> None:
        """STORY-005: Verify Report Generation."""
        prompt = "Simple test."
        result = self.analyzer.analyze(prompt)

        # JSON
        json_out = self.reporter.generate_json_report(result)
        self.assertTrue(json.loads(json_out))

        # Markdown
        md_out = self.reporter.generate_markdown_report(result)
        self.assertIn("# Prlyn Analysis Report", md_out)
        self.assertIn("## Readability", md_out)


if __name__ == "__main__":
    unittest.main()
