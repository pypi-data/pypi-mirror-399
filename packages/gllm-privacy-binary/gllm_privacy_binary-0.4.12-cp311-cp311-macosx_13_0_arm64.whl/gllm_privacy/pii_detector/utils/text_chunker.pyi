from _typeshed import Incomplete
from typing import Any

DEFAULT_SAFE_MAX_LENGTH: int
MAX_REASONABLE_LENGTH: int
CHUNK_SIZE_RATIO: float
SENTENCE_SPLIT_PATTERN: Incomplete

class TokenAwareTextChunker:
    """Token-aware text chunker for NER processing.

    Handles splitting long text into chunks that respect tokenizer limits
    while preserving sentence and word boundaries for better entity detection.
    """
    tokenizer: Incomplete
    def __init__(self, tokenizer: Any, max_tokens: int | None = None) -> None:
        """Initialize the text chunker.

        Args:
            tokenizer: The tokenizer to use for token counting.
            max_tokens (int | None, optional): Maximum tokens per chunk override. Defaults to None.
        """
    def get_max_chunk_tokens(self) -> int:
        """Get maximum tokens per chunk with user override support and safe fallbacks.

        Handles cases where model_max_length is None or unrealistic (like 1000000000000).

        Returns:
            int: Maximum tokens per chunk.
        """
    def should_chunk(self, text: str) -> bool:
        """Determine if text needs chunking based on actual token count.

        Args:
            text (str): Input text to check.

        Returns:
            bool: True if text should be chunked, False if it fits in model limits.
        """
    def split_text(self, text: str) -> list[tuple[int, int]]:
        """Split text into chunks that respect token limits and boundaries.

        Uses sentence boundaries first, then word boundaries as fallback.
        Each chunk is guaranteed to fit within token limits.

        Args:
            text (str): Input text to split.

        Returns:
            list[tuple[int, int]]: List of (start_pos, end_pos) for each chunk.
        """
    def split_by_sentences(self, text: str, max_tokens: int) -> list[tuple[int, int]]:
        """Split text by sentence boundaries while respecting token limits.

        Args:
            text (str): Input text to split.
            max_tokens (int): Maximum tokens per chunk.

        Returns:
            list[tuple[int, int]]: List of chunks, empty if sentences too long.
        """
    def split_by_words(self, text: str, max_tokens: int) -> list[tuple[int, int]]:
        """Split text by word boundaries while respecting token limits.

        Args:
            text (str): Input text to split.
            max_tokens (int): Maximum tokens per chunk.

        Returns:
            list[tuple[int, int]]: List of chunks.
        """
