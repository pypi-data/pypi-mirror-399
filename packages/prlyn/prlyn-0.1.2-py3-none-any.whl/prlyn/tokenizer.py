"""
Tokenizer module for counting tokens and loading linguistic models.
"""
import tiktoken
import spacy
from typing import Any


class Tokenizer:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Downloading Spacy model '{model_name}'...")
            from spacy.cli import download

            download(model_name)
            self.nlp = spacy.load(model_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def get_spacy_doc(self, text: str) -> Any:
        return self.nlp(text)
