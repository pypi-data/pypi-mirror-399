from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class BPJSNumberRecognizer(PatternRecognizer):
    """Recognize Indonesian BPJS (Social Security) numbers."""
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize BPJSRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer, default is "id".
        '''
