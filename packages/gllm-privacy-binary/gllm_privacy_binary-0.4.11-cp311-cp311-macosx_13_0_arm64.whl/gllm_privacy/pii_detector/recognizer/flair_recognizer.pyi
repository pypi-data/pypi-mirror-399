from _typeshed import Incomplete
from flair.models import SequenceTagger
from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import AnalysisExplanation, EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger: Incomplete

class FlairRecognizer(EntityRecognizer):
    """Wrapper for a flair model, if needed to be used within TextAnalyzer.

    Attributes:
        ENTITIES (list[Entities]):  List of Supported entities by this recognizer.
        DEFAULT_EXPLANATION (str): Default explanation for the recognized entities.
        DEFAULT_CHECK_LABEL_GROUPS (list[tuple[set[Entities], set[str]]]): Groups of labels to check for each entity.
        MODEL_LANGUAGES (dict[str, str]): Flair model languages.
        PRESIDIO_EQUIVALENCES (dict[str, Entities]): Equivalences between Flair and Presidio entities.
        MODEL_CACHE (dict[str, SequenceTagger]): Cache for loaded Flair models.
    """
    ENTITIES: Incomplete
    DEFAULT_EXPLANATION: str
    DEFAULT_CHECK_LABEL_GROUPS: Incomplete
    MODEL_LANGUAGES: Incomplete
    PRESIDIO_EQUIVALENCES: Incomplete
    MODEL_CACHE: Incomplete
    check_label_groups: Incomplete
    model: Incomplete
    def __init__(self, supported_language: str = 'en', supported_entities: list[str] | None = None, check_label_groups: tuple[set, set] | None = None, model: SequenceTagger = None) -> None:
        '''Initialize the FlairRecognizer.

        Args:
            supported_language (str): The supported language. Defaults to "en".
            supported_entities (list[str] | None, Optional): The supported entities. Defaults to None.
            check_label_groups (tuple[set, set] | None, Optional): The groups of labels to check for each entity.
                Defaults to None.
            model (SequenceTagger, Optional): The Flair model to use. Defaults to None.
        '''
    def load(self) -> None:
        """Load the model, not used. Model is loaded during initialization."""
    def get_supported_entities(self) -> list[str]:
        """Return supported entities by this model.

        Returns:
            list[str]: List of the supported entities.
        """
    def analyze(self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts | None = None) -> list[RecognizerResult]:
        """Analyze text using Text Analytics.

        Args:
            text (str): The text to be analyzed.
            entities (list[str]): The entities to be analyzed. (Not working properly for this recognizer).
            nlp_artifacts (NlpArtifacts, Optional): The NLP artifacts to be analyzed. (Not used by this recognizer).
                Defaults to None.

        Returns:
            list[RecognizerResult]: The list of Presidio RecognizerResult constructed from the recognized
                Flair detections.
        """
    def build_flair_explanation(self, original_score: float, explanation: str) -> AnalysisExplanation:
        """Create explanation for why this result was detected.

        Args:
            original_score (float): The score given by the recognizer.
            explanation (str): The explanation string.

        Returns:
            AnalysisExplanation: The explanation for the result.
        """
