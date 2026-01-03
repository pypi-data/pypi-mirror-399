from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class FacebookAccountRecognizer(PatternRecognizer):
    """Recognize Facebook account."""
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize FacebookAccountRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default is "id".
        '''
