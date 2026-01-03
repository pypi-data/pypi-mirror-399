from prlyn.models import ReadabilityScore
from prlyn.tokenizer import Tokenizer
import re


class ReadabilityAnalyzer:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def count_syllables(self, word: str) -> int:
        word = word.lower()
        if len(word) <= 3:
            return 1

        # Heuristic syllable counting
        word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
        word = re.sub(r"^y", "", word)
        syllables = len(re.findall(r"[aeiouy]{1,2}", word))
        return max(1, syllables)

    def analyze(self, text: str, total_sentences: int) -> ReadabilityScore:
        if not text.strip() or total_sentences == 0:
            return ReadabilityScore(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
            )

        doc = self.tokenizer.get_spacy_doc(text)
        words = [t.text for t in doc if not t.is_punct and not t.is_space]
        total_words = len(words)

        if total_words == 0:
            return ReadabilityScore(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
            )

        total_syllables = sum(self.count_syllables(w) for w in words)

        asl = total_words / total_sentences
        asw = total_syllables / total_words

        # Flesch Reading Ease
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)

        # Flesch-Kincaid Grade
        fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59

        return ReadabilityScore(
            flesch_reading_ease=round(fre, 2),
            flesch_kincaid_grade=round(fk_grade, 2),
            avg_sentence_length=round(asl, 2),
            avg_syllables_per_word=round(asw, 2),
        )
