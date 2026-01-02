from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class KTPRecognizer(PatternRecognizer):
    """Recognize KTP (Kartu Tanda Penduduk) using regex patterns.

    KTP has 16 digits with the following format: {6}{2}{2}{2}{4}.
    - 6 digits of province, city, and sub-district code
    - 2 digits of birthdate. 01-31 for men and 41-71 for women
    - 2 digits of birth month. 01-12
    - 2 digits of birth year. 00-99
    - 4 digits of sequence number
    """
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize KTPRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default to "id".
        '''
