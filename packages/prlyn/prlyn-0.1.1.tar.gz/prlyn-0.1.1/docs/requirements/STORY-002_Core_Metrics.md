# STORY-002: Core Metrics (Ambiguity & Negation)

## Description
Implement the decomposition of the Ambiguity Score and the scoped Negative Instruction analysis.

## Acceptance Criteria
- [ ] **Ambiguity Analysis**:
    - [ ] Vague Term density calculation.
    - [ ] Unresolved Coreference score (pronouns without antecedents).
    - [ ] Hedging Language density.
- [ ] **Negative Instruction Analysis**:
    - [ ] Scans ONLY sentences labeled INSTRUCTION/CONSTRAINT.
    - [ ] Detects negative patterns (don't, do not, never, etc.).
    - [ ] Suggests positive reframes.

## Technical Notes
- See REQ-001 Change 3 & 5.
- Targets: Vague < 0.02, Coref < 0.10, Hedge < 0.05.
