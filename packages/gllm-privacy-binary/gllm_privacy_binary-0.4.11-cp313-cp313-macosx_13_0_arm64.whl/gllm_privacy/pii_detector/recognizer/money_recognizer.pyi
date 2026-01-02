from _typeshed import Incomplete
from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class MoneyRecognizer(PatternRecognizer):
    """Recognize money amounts using regex and context.

    Regex pattern to match money amounts with the following rules:
    - Must start with a currency symbol ($, €, £, ¥) or currency code (USD, EUR, GBP, JPY, Rp)
    - Matches numbers with at least 1 digit before the decimal point
    - Optionally matches comma-separated thousands
    - Optionally matches a decimal point followed by exactly two digits
    - Ensures the number is not preceded or followed by other digits
    - Excludes single zeros or numbers that are just decimal zeros (e.g., 0.00)
    """
    STRONG_CONTEXT: Incomplete
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize the MoneyRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Defaults to "id".
        '''
