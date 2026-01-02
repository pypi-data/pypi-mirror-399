from abc import ABC, abstractmethod
from gllm_core.schema import Component
from gllm_privacy.pii_detector.constants import RecognizerResult as RecognizerResult
from typing import Any

class BaseTextAnalyzer(Component, ABC):
    """Analyzer class to analyze the text and extract the PII entities."""
    @abstractmethod
    def analyze(self, text: str, language: str, entities: list[str] | None = None, score_threshold: float | None = None, allow_list: list[str] | None = None, allow_list_match: str | None = 'exact', regex_flags: int | None = ..., **kwargs: Any) -> list[RecognizerResult]:
        '''Analyze the text and extract the PII entities.

        Args:
            text (str): The text to be analyzed
            language (str): The language of the text
            entities (list | None, optional): The list of entities to be extracted. Default is None.
            score_threshold (float | None, optional): The threshold score for the extracted entities. Default is None.
            allow_list (list | None, optional): List of words that the user defines as being allowed to keep in
                the text. Default is None.
            allow_list_match (str | None, optional): The matching strategy for the allow list. Default is "exact".
            regex_flags (int | None, optional): The regex flags for the text analysis.
            **kwargs (Any): Additional keyword arguments that may be needed for the text analysis process.

        Returns:
            list[RecognizerResult]: The list of extracted entities
        '''
