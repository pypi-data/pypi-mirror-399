# REQ-001: Prompt Analyzer v2 - Revised Algorithm

## Overview
A revised algorithm for the Prompt Analyzer to address fragility in classifier heuristics and missing metrics (contradiction, token value, position scoring).

## Phase 1: Core (Ship First)
Goal: Strip to essentials. Get working. Iterate.

### Architecture
1. Preprocessor (code block isolation)
2. Tokenizer (tiktoken + spaCy)
3. Classifier (dependency-based)
4. Metrics Engine (6 core metrics + Readability)
5. Report + Recommendations
6. Deployment (MCP Server via uvx)

## Detailed Changes

### Change 1: Preprocessor Layer
**Problem**: Code blocks corrupt POS tagging.
**Solution**: Extract before analysis, restore for reporting.
- Extract code blocks (```) -> store separately.
- Replace with [CODE_BLOCK_N].
- Extract quoted strings -> store separately.
- Replace with [QUOTED_N].

### Change 2: Classifier — Dependency Parsing
**Problem**: POS-only misses embedded instructions.
**Solution**: Use dependency tree root verbs.
- `root.lemma` in IMPERATIVE_VERBS -> INSTRUCTION.
- `has_modal_subject_pattern` -> CONSTRAINT.
- `is_example_block` -> EXAMPLE.
- `has_format_specification` -> FORMAT_SPEC.
- `is_descriptive` -> CONTEXT.
- Multi-label handling.

### Change 3: Ambiguity Score — Decomposed
**Problem**: Combined formula with arbitrary weights.
**Solution**: Separate sub-scores.
- Vague Terms Detection.
- Unresolved Coreference.
- Hedging Language.

### Change 4: Instruction Position Scoring
**Problem**: Lost in the middle.
**Solution**: Score instruction placement (Start/Middle/End zones).

### Change 5: Negative Instruction — Scoped
**Problem**: False positives.
**Solution**: Only check labeled instructions/constraints for negations.

### Change 6: Redundancy — Label-Gated + Clustered
**Problem**: O(n^2) cost.
**Solution**: Only compare same-label sentences. Use clustering.
- Group by label.
- Filter short sentences.
- Agglomerative clustering.

### Change 7: Contradiction Detection
**Problem**: Conflicting constraints.
**Solution**: Detect semantic opposition within constraints (similarity > 0.60 + opposing polarity).

### Change 8: Token Efficiency
**Problem**: Token count without value.
**Solution**: Ratio of actionable tokens to total.

### Change 9: Readability Metrics
**Problem**: Prompts too complex or hard to read.
**Solution**: Calculate standard readability scores.
- Flesch-Kincaid Grade Level.
- Flesch Reading Ease.

 ### Change 10: Deployment — MCP Server with uvx
 **Problem**: Missing integration standard and ease of distribution.
 **Solution**: Deploy as an MCP Server executable via `uvx`.
 - Expose reports and metrics via MCP resources/tools.
 - Support `uvx` for zero-install execution (`uvx plint`).

## Implementation Priority
- Week 1: Preprocessor + Tokenizer + Basic Classifier (STORY-01)
- Week 2: Core Metrics (STORY-02)
- Week 3: Position Scoring + Token Efficiency (STORY-03)
- Week 4: Redundancy + Contradiction (STORY-04)
- Week 5: Reporting (STORY-05)
