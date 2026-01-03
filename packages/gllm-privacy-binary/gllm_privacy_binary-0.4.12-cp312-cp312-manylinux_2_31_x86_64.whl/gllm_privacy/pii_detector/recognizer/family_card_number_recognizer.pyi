from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class FamilyCardNumberRecognizer(PatternRecognizer):
    """Recognize Indonesian family card (Kartu Keluarga) numbers."""
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize FamilyCardNumberRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer, default is "id".
        '''
