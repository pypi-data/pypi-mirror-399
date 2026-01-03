# STORY-003: Advanced Metrics (Position, Efficiency, Readability)

## Description
Implement Position Scoring to detect "buried" instructions and Token Efficiency analysis.

## Acceptance Criteria
- [ ] **Position Analysis**:
    - [ ] Splits text into Start (25%), Middle (50%), End (25%).
    - [ ] Counts critical labels (INSTRUCTION, CONSTRAINT) in each zone.
    - [ ] Calculates score based on reduced middle-zone density.
- [ ] **Token Efficiency**:
    - [ ] Calculates ratio of actionable tokens (INSTRUCTION/CONSTRAINT/FORMAT) to total tokens.
    - [ ] Categorizes efficiency (Low/Moderate/Good/High).
- [ ] **Readability Metrics**:
    - [ ] Calculates Flesch-Kincaid Grade Level.
    - [ ] Calculates Flesch Reading Ease score.
    - [ ] Includes scores in the JSON report.

## Technical Notes
- See REQ-001 Change 4, 8, & 9.
