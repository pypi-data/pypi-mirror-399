# STORY-004: Complex Analytics (Redundancy & Contradiction)

## Description
Implement computationally intensive checks: Redundancy clustering and Contradiction detection.

## Acceptance Criteria
- [ ] **Redundancy Analysis**:
    - [ ] Groups by label first.
    - [ ] Filters short sentences (<8 tokens).
    - [ ] Uses agglomerative clustering on embeddings (threshold 0.25).
- [ ] **Contradiction Analysis**:
    - [ ] Compares CONSTRAINT pairs.
    - [ ] Trigger: Similarity > 0.60 AND Opposing Polarity.
    - [ ] Polarity extraction (Positive/Negative/Neutral markers).

## Technical Notes
- See REQ-001 Change 6 & 7.
- requires embedding model (e.g., all-MiniLM-L6-v2).
