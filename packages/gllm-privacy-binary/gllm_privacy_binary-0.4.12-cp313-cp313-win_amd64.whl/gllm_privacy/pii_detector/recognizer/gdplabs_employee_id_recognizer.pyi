from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class GDPLabsEmployeeIdRecognizer(PatternRecognizer):
    """Recognize GDP Labs Employee ID using regex pattern.

    GDP Labs Employee ID contains 8 digits of numeric characters.
    """
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize GDPLabsEmployeeIdRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default to "id".
        '''
