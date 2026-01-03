import re
from typing import Tuple, Dict
from prlyn.models import Placeholder, PlaceholderType


class Preprocessor:
    def __init__(self):
        # Non-greedy match for code blocks
        self.code_block_pattern = re.compile(r"```[\s\S]*?```")
        # Basic double quote pattern, handling escaped quotes
        self.quote_pattern = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"')

    def process(self, text: str) -> Tuple[str, Dict[str, Placeholder]]:
        placeholders: Dict[str, Placeholder] = {}

        # Pass 1: Code Blocks
        matches = list(self.code_block_pattern.finditer(text))
        new_text_parts = []
        last_idx = 0

        for match in matches:
            # Append text before match
            new_text_parts.append(text[last_idx : match.start()])

            # Create placeholder
            pid = f"[CODE_BLOCK_{len(placeholders)}]"
            placeholders[pid] = Placeholder(
                id=pid,
                content=match.group(0),
                type=PlaceholderType.CODE_BLOCK,
                start_index=match.start(),
                end_index=match.end(),
            )

            # Append placeholder
            new_text_parts.append(pid)
            last_idx = match.end()

        new_text_parts.append(text[last_idx:])
        intermediate_text = "".join(new_text_parts)

        # Pass 2: Quotes (on intermediate text)
        matches = list(self.quote_pattern.finditer(intermediate_text))
        final_text_parts = []
        last_idx = 0

        for match in matches:
            # Check if this looks like it's inside a placeholder (unlikely with unique IDs)
            # Append text before match
            final_text_parts.append(intermediate_text[last_idx : match.start()])

            pid = f"[QUOTED_{len(placeholders)}]"
            placeholders[pid] = Placeholder(
                id=pid,
                content=match.group(0),
                type=PlaceholderType.QUOTED_STRING,
                start_index=match.start(),  # Index in intermediate text
                end_index=match.end(),
            )

            final_text_parts.append(pid)
            last_idx = match.end()

        final_text_parts.append(intermediate_text[last_idx:])
        clean_text = "".join(final_text_parts)

        return clean_text, placeholders
