from abc import ABC, abstractmethod
from enum import StrEnum
from gllm_core.schema import Component
from presidio_anonymizer import ConflictResolutionStrategy

class Operation(StrEnum):
    """Enum represent the valid operation for the anonymizer."""
    ANONYMIZE: str
    DEANONYMIZE: str

class BaseTextAnonymizer(Component, ABC):
    """Anonymizer class to anonymize the text."""
    @abstractmethod
    def anonymize(self, text: str, entities: list[str] | None = None, language: str = 'id', conflict_resolution: ConflictResolutionStrategy | None = None, analyzer_score_threshold: float = 0.46) -> str:
        '''Anonymize the text.

        Args:
            text (str): The text to be anonymized.
            entities (list[str] | None, optional): The list of entities to be anonymized. Default is None.
            language (str, optional): The language of the text to be analyzed. Default is "id".
            conflict_resolution (ConflictResolutionStrategy | None, optional): The conflict resolution strategy.
                Default is None.
            analyzer_score_threshold (float, optional): The score threshold for the analyzer, default is 0.46.

        Returns:
            str: The anonymized text
        '''
    @abstractmethod
    def deanonymize(self, text: str) -> str:
        """Deanonymize the text.

        Args:
            text (str): The text to be deanonymized

        Returns:
            str: The deanonymized text
        """
