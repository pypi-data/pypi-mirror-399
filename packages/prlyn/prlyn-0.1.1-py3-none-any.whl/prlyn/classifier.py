from typing import List
from prlyn.models import ClassifiedSentence, SentenceLabel
from prlyn.tokenizer import Tokenizer

IMPERATIVE_VERBS = {
    "write",
    "create",
    "generate",
    "make",
    "build",
    "implement",
    "code",
    "explain",
    "describe",
    "summarize",
    "translate",
    "list",
    "compare",
    "analyze",
    "fix",
    "update",
    "add",
    "remove",
    "delete",
    "use",
    "act",
    "ignore",
    "return",
    "provide",
    "output",
    "ensure",
    "check",
    "verify",
}

MODALS = {"must", "should", "shall", "need", "require", "have to", "ought"}


class Classifier:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def classify(self, text: str) -> List[ClassifiedSentence]:
        doc = self.tokenizer.get_spacy_doc(text)
        classified_sentences = []

        lines = text.splitlines()
        if len(lines) > 50:
            return []
        # 1. Instruction Detection (Root Verb + List)
        for sent in doc.sents:
            labels = []

            root = sent.root
            # Imperatives are usually ROOT and VERB.
            # Sometimes Spacy misclassifies, checking lemma in list is a strong heuristic.
            is_imperative = (
                root.pos_ == "VERB" and root.lemma_.lower() in IMPERATIVE_VERBS
            )

            if is_imperative:
                labels.append(SentenceLabel.INSTRUCTION)

            # 2. Constraint Detection (Modals)
            # Scan for modals or constraint keywords
            has_constraint = False
            for token in sent:
                if token.tag_ == "MD" or token.lemma_.lower() in MODALS:
                    has_constraint = True
                    break

            # Negative constraints often use "do not", "never"
            if "not" in sent.text.lower() or "never" in sent.text.lower():
                # If it's attached to a verb, might be a constraint
                has_constraint = True

            if has_constraint:
                labels.append(SentenceLabel.CONSTRAINT)

            # 3. Example Detection
            if "example" in sent.text.lower() or "e.g." in sent.text.lower():
                labels.append(SentenceLabel.EXAMPLE)

            # 4. Format Spec Detection
            format_keywords = [
                "json",
                "csv",
                "markdown",
                "xml",
                "format",
                "output",
                "structure",
            ]
            if any(w in sent.text.lower() for w in format_keywords):
                labels.append(SentenceLabel.FORMAT_SPEC)

            # 5. Context (Default if no other strong signal)
            if not labels:
                labels.append(SentenceLabel.CONTEXT)

            # Determine Primary
            # Priority: INSTRUCTION > CONSTRAINT > FORMAT > EXAMPLE > CONTEXT
            primary = SentenceLabel.CONTEXT
            if SentenceLabel.INSTRUCTION in labels:
                primary = SentenceLabel.INSTRUCTION
            elif SentenceLabel.CONSTRAINT in labels:
                primary = SentenceLabel.CONSTRAINT
            elif SentenceLabel.FORMAT_SPEC in labels:
                primary = SentenceLabel.FORMAT_SPEC
            elif SentenceLabel.EXAMPLE in labels:
                primary = SentenceLabel.EXAMPLE

            secondary = [lbl for lbl in labels if lbl != primary]

            classified_sentences.append(
                ClassifiedSentence(
                    text=sent.text.strip(),
                    start_char=sent.start_char,
                    end_char=sent.end_char,
                    primary_label=primary,
                    secondary_labels=secondary,
                    tokens=len(sent),
                )
            )

        return classified_sentences
