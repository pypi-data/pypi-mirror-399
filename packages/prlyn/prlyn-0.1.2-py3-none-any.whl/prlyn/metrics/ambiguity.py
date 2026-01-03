from prlyn.models import AmbiguityScore
from prlyn.tokenizer import Tokenizer

VAGUE_TERMS = {
    "some",
    "few",
    "many",
    "several",
    "things",
    "stuff",
    "various",
    "certain",
    "kind of",
    "sort of",
    "roughly",
    "about",
    "approximately",
    "something",
}

HEDGING_TERMS = {
    "might",
    "may",
    "could",
    "can",
    "possibly",
    "probably",
    "likely",
    "usually",
    "often",
    "sometimes",
    "generally",
    "seem",
    "appear",
    "suggest",
    "think",
    "believe",
    "assume",
}


class AmbiguityAnalyzer:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def analyze(self, text: str) -> AmbiguityScore:
        doc = self.tokenizer.get_spacy_doc(text)
        tokens = [token.text.lower() for token in doc]
        total_tokens = len(tokens) if tokens else 1

        # 1. Vague Terms
        found_vague = [t for t in tokens if t in VAGUE_TERMS]
        vague_density = len(found_vague) / total_tokens

        # 2. Hedging
        found_hedging = [t for t in tokens if t in HEDGING_TERMS]
        hedging_density = len(found_hedging) / total_tokens

        # 3. Unresolved Coreference (Naive Implementation)
        # Check for pronouns without clear antecedents in previous sentences.
        # This is hard to do perfectly without a coref model, so we'll use a heuristic:
        # High density of pronouns vs nouns.
        pronouns = [t for t in doc if t.pos_ == "PRON"]
        nouns = [t for t in doc if t.pos_ in {"NOUN", "PROPN"}]

        coref_score = 0.0
        if pronouns and not nouns:
            coref_score = 1.0  # All pronouns, no context
        elif pronouns:
            # Ratio of pronouns to nouns+pronouns
            coref_score = len(pronouns) / (len(nouns) + len(pronouns))

        return AmbiguityScore(
            vague_term_density=vague_density,
            unresolved_coref_score=coref_score,
            hedging_density=hedging_density,
            vague_terms_found=list(set(found_vague)),
            hedging_terms_found=list(set(found_hedging)),
        )
