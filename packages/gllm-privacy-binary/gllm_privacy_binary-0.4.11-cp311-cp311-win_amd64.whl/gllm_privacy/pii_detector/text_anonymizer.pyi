from _typeshed import Incomplete
from gllm_privacy.pii_detector.analyzer import BaseTextAnalyzer as BaseTextAnalyzer
from gllm_privacy.pii_detector.anonymizer import BaseTextAnonymizer as BaseTextAnonymizer
from gllm_privacy.pii_detector.utils.deanonymizer_mapping import DeanonymizerMapping as DeanonymizerMapping, MappingDataType as MappingDataType, create_anonymizer_mapping as create_anonymizer_mapping
from gllm_privacy.pii_detector.utils.pseudo_anonymizer_mapping import get_pseudoanonymizer_mapping as get_pseudoanonymizer_mapping
from presidio_anonymizer import AnonymizerEngine, ConflictResolutionStrategy
from presidio_anonymizer.entities import OperatorConfig
from typing import Any

class TextAnonymizer(BaseTextAnonymizer):
    """TextAnonymizer class to anonymize the text based on the analyzer results.

    Implemented using presidio pii library [1].

    Attributes:
        anonymizer (AnonymizerEngine): The anonymizer engine used in the anonymization process.
        operators (dict[str, OperatorConfig]): The operators used in the anonymization process.
        anonymizer_mapping (MappingDataType): The anonymizer mapping.
        deanonymizer_mapping (MappingDataType): The deanonymizer mapping.
    """
    anonymizer: Incomplete
    skip_format_duplicates: Incomplete
    operators: Incomplete
    def __init__(self, text_analyzer: BaseTextAnalyzer, operators: dict[str, OperatorConfig] | None = None, add_default_faker_operators: bool = False, faker_seed: int | None = 42, anonymizer_engine: AnonymizerEngine | None = None, deanonymizer_mapping: DeanonymizerMapping | None = None, skip_format_duplicates: bool | None = False) -> None:
        """Initialize the TextAnonymizer class.

        Args:
            text_analyzer (BaseTextAnalyzer): The analyzer engine used in the anonymization process
            operators (dic[str, OperatorConfig] | None, optional): The operators used in the anonymization process
                    see https://microsoft.github.io/presidio/anonymizer/#built-in-operators
            add_default_faker_operators (bool, optional): Whether to add default faker operators. Defaults to False.
            faker_seed (int | None, optional): The seed used for faker. Defaults to 42.
            anonymizer_engine (AnonymizerEngine, optional): The anonymizer engine used in the anonymization process.
                    Defaults to None.
            deanonymizer_mapping (DeanonymizerMapping, optional): The deanonymizer mapping used to record mapping
                    between anonymized and original text. Defaults to None.
            skip_format_duplicates (bool, optional): Whether to skip formatting duplicated operators. Defaults to False.
        """
    @property
    def deanonymizer_mapping(self) -> MappingDataType:
        """Return the deanonymizer mapping.

        Returns:
            MappingDataType: The deanonymizer mapping.
        """
    @property
    def anonymizer_mapping(self) -> MappingDataType:
        """Return the anonymizer mapping.

        Returns:
            MappingDataType: The anonymizer mapping.
        """
    def anonymize(self, text: str, entities: list[str] | None = None, language: str = 'id', conflict_resolution: ConflictResolutionStrategy | None = None, analyzer_score_threshold: float = 0.46, allow_list: list[str] | None = None, allow_list_match: str | None = 'exact', regex_flags: int | None = ..., **kwargs: Any) -> str:
        '''Anonymize the text based on the analyzer results.

        Args:
            text (str): The text to be anonymized
            entities (list[str] | None, optional): The list of entities to be anonymized. Defaults to None.
            language (str, optional): The language of the text to be analyzed, Defaults to "id".
            conflict_resolution (ConflictResolutionStrategy | None, optional): The conflict resolution strategy.
                Defaults to None.
            analyzer_score_threshold (float, optional): The score threshold for the analyzer. Defaults to 0.46.
            allow_list (list | None, optional): List of words that the user defines as being allowed to keep in
                the text. Defaults to None.
            allow_list_match (str | None, optional): The matching strategy for the allow list. Defaults to "exact".
            regex_flags (int | None, optional): The regex flags for the text analysis.
            **kwargs (Any): Additional keyword arguments that may be needed for the text analysis process.

        Returns:
            str: The anonymized text.
        '''
    def deanonymize(self, text: str) -> str:
        """Deanonymize the text based on the anonymizer mapping.

        Args:
            text (str): The text to be deanonymized.

        Returns:
            str: The deanonymized text or the original text if no mapping is found or the mapping is empty.
        """
    def reset_deanonymizer_mapping(self) -> None:
        """Reset the deanonymizer mapping."""
    def add_operators(self, operators: dict[str, OperatorConfig]) -> None:
        """Add operators to the anonymizer.

        Args:
            operators (dict[str, OperatorConfig]): Operators to add to the anonymizer.
        """
    def remove_all_operators(self) -> None:
        """Remove all operators from the anonymizer."""
