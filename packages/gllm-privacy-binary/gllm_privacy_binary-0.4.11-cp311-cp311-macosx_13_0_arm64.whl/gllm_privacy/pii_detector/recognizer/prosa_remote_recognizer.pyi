from _typeshed import Incomplete
from gllm_privacy.pii_detector.constants import DEFAULT_PROSA_SUPPORTED_PII_ENTITIES as DEFAULT_PROSA_SUPPORTED_PII_ENTITIES, PROSA_ENTITY_MAP as PROSA_ENTITY_MAP, ProsaNERConstant as ProsaNERConstant, RecognizerResult as RecognizerResult
from presidio_analyzer import RemoteRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

manager: Incomplete
logger: Incomplete

class ProsaRemoteRecognizer(RemoteRecognizer):
    """Initializes a remote recognizer for interfacing with the Prosa API.

    This class extends RemoteRecognizer to provide specific functionality for interacting with the Prosa API for entity
    recognition.
    It includes methods for sending data to the Prosa API, processing the response, and adapting the recognized
    entities to a format compatible with the parent class. The class supports initialization with API credentials,
    a list of supported entities, and an optional whitelist for further filtering recognized entities.

    Attributes:
        headers (dict): Headers to be sent with each request to the Prosa API, including the Content-Type and API key.
        __post_processing_fn (list[Callable[[list[RecognizerResult]], RecognizerResult]]): List of post-processing
            functions to be applied to raw recognizer result.
        prosa_api_url (str): The URL for the Prosa API endpoint.
        prosa_api_key (str): The API key for authenticating with the Prosa API.
        supported_entities_list (list[str]): A list of entity types that the recognizer is capable of identifying.
    """
    prosa_api_url: Incomplete
    prosa_api_key: Incomplete
    supported_entities_list: Incomplete
    headers: Incomplete
    def __init__(self, prosa_api_url: str, prosa_api_key: str, supported_entities_list: list[str] = ...) -> None:
        """Initializes the ProsaRemoteRecognizer instance with API credentials and configuration.

        This constructor sets up a new ProsaRemoteRecognizer by configuring the API endpoint, API key, supported
        entities list, and an optional whitelist of entities. It also prepares the headers required for API requests
        and invokes the constructor of the parent class with specific parameters.

        Args:
            prosa_api_url (str): The URL of the Prosa API to which the recognition requests will be sent.
            prosa_api_key (str): The API key for authenticating with the Prosa API.
            supported_entities_list (list[str]): A list of entity types that the recognizer is capable of identifying.
        """
    def analyze(self, text: str, entities: list[str] = None, nlp_artifacts: NlpArtifacts = None) -> list[RecognizerResult]:
        """Analyzes text for entity recognition using the Prosa API.

        Sends a request to the Prosa API with the provided text and optional whitelist of entities, then processes
        the response to fit the expected format of RecognizerResult objects.

        Args:
            text (str): The text to be analyzed.
            entities (list[str]): A list of entities to look for in the text.
            nlp_artifacts (NlpArtifacts): Additional NLP artifacts that may be required for analysis, depending on
                the implementation.

        Returns:
            list[RecognizerResult]: A list of RecognizerResult objects representing the recognized entities.
        """
    def get_supported_entities(self) -> list[str]:
        """Returns a list of entity types that this recognizer can identify.

        Returns:
            list[str]: The list of supported entity types.
        """
