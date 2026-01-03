# STORY-001: Core Framework (Preprocessor + Classifier)

## Description
Implement the foundational pipeline for Prompt Analyzer v2. This includes the preprocessor to handle code blocks and quotes, the tokenizer using tiktoken/spaCy, and the dependency-based classifier.

## Acceptance Criteria
- [ ] **Preprocessor**: correctly extracts code blocks (```...```) and quoted strings into a separate store, replacing them with placeholders.
- [ ] **Tokenizer**: integrates `tiktoken` (cl100k_base) and `spaCy` (en_core_web_sm/trf).
- [ ] **Classifier**: implements `classify_sentence` using dependency parsing.
    - [ ] Identifying INSTRUCTION (imperative root).
    - [ ] Identifying CONSTRAINT (modal subject pattern).
    - [ ] Identifying EXAMPLE/FORMAT_SPEC/CONTEXT.
- [ ] **Multi-label**: supports primary and secondary labels.

## Technical Notes
- See REQ-001 Change 1 & 2.
- Input: raw prompt text.
- Output: Structured object with clean text, placeholders, and classified sentences.
