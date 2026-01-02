from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class BankAccountNumberRecognizer(PatternRecognizer):
    """Recognize Indonesian bank account numbers using regex patterns."""
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize BankAccountNumberRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Defaults to "id".
        '''
