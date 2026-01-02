from _typeshed import Incomplete
from presidio_analyzer.nlp_engine import NlpArtifacts as NlpArtifacts
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer as BaseCreditCardRecognizer

CREDIT_CARD_BASE_SCORE: float

class CreditCardRecognizer(BaseCreditCardRecognizer):
    """Credit card recognizer that normalizes context terms and caps base scores."""
    DEFAULT_CONTEXT: list[str]
    context: Incomplete
    def __init__(self, supported_language: str = 'id', **kwargs) -> None:
        """Initialize recognizer with merged context and softened base scores.

        Args:
            supported_language: Language code passed through to the base recognizer.
            **kwargs: Extra parameters (e.g., `context`) forwarded for compatibility with Presidio loader.
        """
    def analyze(self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts | None = None, regex_flags: int | None = None):
        """Run base analysis then cap raw scores; context boosting is handled by Presidio.

        Args:
            text: Text to analyze.
            entities: Entity types this recognizer can emit.
            nlp_artifacts: Optional NLP artifacts supplied by Presidio.
            regex_flags: Optional regex flags for pattern matching.

        Returns:
            List of recognizer results with scores capped to the base score.
        """
