from _typeshed import Incomplete
from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class ProjectNameRecognizer(PatternRecognizer):
    '''Recognize Project name using regex pattern.

    Project name start with "Project" or contain specific terms like GDP Labs, Catapa, GLAIR, KASKUS, Project E, BOSA,
    SWISS.
    '''
    PATTERNS: Incomplete
    def __init__(self, supported_language: str = 'id', additional_project_names: list[str] | None = None) -> None:
        '''Initialize ProjectNameRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default is "id".
            additional_project_names (list[str], optional): List of additional project names to be recognized.
                    Default is None.
        '''
