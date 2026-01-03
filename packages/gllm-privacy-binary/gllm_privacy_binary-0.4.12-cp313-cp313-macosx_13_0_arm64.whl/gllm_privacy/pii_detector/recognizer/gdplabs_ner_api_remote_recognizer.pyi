from _typeshed import Incomplete
from gllm_privacy.pii_detector.constants import GLLM_PRIVACY_ENTITIES as GLLM_PRIVACY_ENTITIES, RecognizerResult as RecognizerResult
from presidio_analyzer import RemoteRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

manager: Incomplete
logger: Incomplete

class GDPLabsNerApiRemoteRecognizer(RemoteRecognizer):
    '''Remote NER Recognizer that calls an external NER API.

    Attributes:
        api_endpoint (str): Full URL of the NER API endpoint
        api_headers (dict): Optional headers to send with the API request. Defaults to None.
        api_timeout (int): Timeout for API request in seconds. Defaults to 60.
        supported_entities (list[str]): List of entity types supported by the recognizer. Defaults to None.
        supported_language (str): Language supported by the recognizer. Defaults to "en".
        DEFAULT_EXPLANATION (str): Default explanation format for the analysis results.
    '''
    DEFAULT_EXPLANATION: str
    api_endpoint: Incomplete
    api_headers: Incomplete
    api_timeout: Incomplete
    def __init__(self, api_url: str, supported_entities: list[str] = None, api_headers: dict | None = None, api_timeout: int = 60, supported_language: str | None = 'en') -> None:
        '''Initialize a Remote NER Recognizer that calls an external NER API.

        Args:
            api_url (str): Full URL of the NER API endpoint
            supported_entities (list[str], optional): List of entity types supported by the recognizer.
                Defaults to None.
            api_headers (dict | None, optional): Optional headers to send with the API request. Defaults to None.
            api_timeout (int, optional): Timeout for API request in seconds. Defaults to 60.
            supported_language (str | None, optional): Language supported by the recognizer. Defaults to "en".
        '''
    def analyze(self, text: str, entities: list[str] = None, nlp_artifacts: NlpArtifacts = None) -> list[RecognizerResult]:
        """Analyze text using the remote NER API and convert results to Presidio RecognizerResults.

        Args:
            text (str): Input text to analyze
            entities (list[str], optional): Optional list of specific entity types to recognize. Defaults to None.
            nlp_artifacts (NlpArtifacts, optional): Optional NLP artifacts. Defaults to None.

        Returns:
            list[RecognizerResult]: List of RecognizerResults containing the recognized entities
        """
    def get_supported_entities(self) -> list[str]:
        """Get the list of supported entities for the recognizer.

        Returns:
            list[str]: List of supported entity types
        """
