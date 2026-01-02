from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class OrganizationNameRecognizer(PatternRecognizer):
    '''Recognize organization name using regex pattern.

    Organization names started with PT, CV followed by a space and capitalized words.

    The organization name identified with a pattern which consists of three parts:
    1.\tMatches either "PT" or "CV" followed by a space.
    2.\tMatches either a title-cased word or an all-uppercase word.
    3.\tMatches additional words that could be title-cased or all-uppercase.
    '''
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize OrganizationNameRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default to "id".
        '''
