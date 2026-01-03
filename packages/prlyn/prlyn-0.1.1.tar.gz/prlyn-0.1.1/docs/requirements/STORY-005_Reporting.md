# STORY-005: Reporting Engine

## Description
Generate the final report and recommendations based on all metrics.

## Acceptance Criteria
- [ ] **Report Generation**:
    - [ ] Reconstructs clear text from preprocessor placeholders relative to findings.
    - [ ] Aggregates all metric scores.
    - [ ] Formats output (Markdown/JSON).
- [ ] **Recommendations**:
    - [ ] Provides specific actions for failed checks (e.g. "Move instructions from middle to start").
    - [ ] Estimates cost based on token count.

## Technical Notes
- See REQ-001 "Report + Recommendations".
