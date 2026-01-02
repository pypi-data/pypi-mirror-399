from _typeshed import Incomplete
from dataclasses import dataclass, field
from presidio_analyzer import RecognizerResult as RecognizerResult
from presidio_anonymizer.entities import EngineResult
from typing import Any

MappingDataType = dict[str, dict[str, str]]

def format_duplicated_operator(operator_name: str, count: int) -> str:
    """Format the operator name with the count.

    Args:
        operator_name (str): The operator name.
        count (int): The count of the operator.
    """

@dataclass
class DeanonymizerMapping:
    """Class to store the deanonymizer mapping.

    The mapping is used to replace anonymized entities with their original values.

    Attributes:
        mapping (MappingDataType): The deanonymizer mapping.
        data (MappingDataType): The current deanonymizer mapping.
        skip_format_duplicates (bool): Whether to skip formatting duplicated operators.
    """
    mapping: MappingDataType = field(default_factory=Incomplete)
    skip_format_duplicates: bool = ...
    @property
    def data(self) -> MappingDataType:
        """Return the deanonymizer mapping.

        Returns:
            MappingDataType: The current deanonymizer mapping.
        """
    def update(self, new_mapping: MappingDataType) -> None:
        """Update the deanonymizer mapping with new values.

        Duplicated values will not be added. If there are multiple entities of the same type, the mapping will
        include a count to differentiate them. For example, if there are two names in the input text, the mapping
        will include NAME_1 and NAME_2.

        Args:
            new_mapping (MappingDataType): The new mapping to be added to the existing deanonymizer mapping.
        """

def create_anonymizer_mapping(original_text: str, analyzer_results: list[RecognizerResult], anonymizer_results: EngineResult, is_reversed: bool = False, skip_format_duplicates: bool = False) -> MappingDataType:
    '''Create or update the mapping used to anonymize and/or deanonymize a text.

    This method exploits the results returned by the analysis and anonymization processes and ensures
    case-insensitive matching during mapping creation.

    Args:
        original_text (str): The original text to be anonymized or deanonymized.
        analyzer_results (list[RecognizerResult]): The results from the text analysis.
        anonymizer_results (EngineResult): The results from the text anonymization.
        is_reversed (bool, optional): If True, constructs a mapping from each original entity to its anonymized value.
            If False, constructs a mapping from each anonymized entity back to its original text value.
            Defaults to False.
        skip_format_duplicates (bool, optional): If True, skip formatting duplicated operators.
            Defaults to False.

    Returns:
        MappingDataType: The mapping used to anonymize and/or deanonymize the text. This mapping is constructed with
            case-insensitive checks but preserves the original case in the stored values.

    Example:
        {
            "PERSON": {
                "<original>": "<anonymized>",
                "John Doe": "Slim Shady"
            },
            "PHONE_NUMBER": {
                "111-111-1111": "555-555-5555"
            }
            ...
        }
    '''
def get_dict_diff(first_mapping: MappingDataType, second_mapping: MappingDataType) -> list[dict[str, Any]]:
    '''Compare two dictionaries and generate the differences.

    This function compares two nested dictionaries and identifies the differences between them. If a key-value pair
    in `first_mapping` is different from `second_mapping`, the function records the difference and stores it as a
    dictionary containing the PII type, anonymized value, and the corresponding PII value.

    Args:
        first_mapping (MappingDataType): The original dictionary to compare.
        second_mapping (MappingDataType): The new dictionary to compare against the original.

    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the differences, with keys "pii_type",
            "anonymized_value", and "pii_value".
    '''
