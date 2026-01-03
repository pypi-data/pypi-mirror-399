from _typeshed import Incomplete
from enum import StrEnum
from presidio_analyzer import RecognizerResult as PresidioRecognizerResult

RecognizerResult = PresidioRecognizerResult

class Entities(StrEnum):
    """Supported entities for PII detection."""
    KTP: str
    NPWP: str
    PROJECT: str
    ORGANIZATION_NAME: str
    EMPLOYEE_ID: str
    FAMILY_CARD_NUMBER: str
    FACEBOOK_ACCOUNT: str
    LINKEDIN_ACCOUNT: str
    BANK_ACCOUNT: str
    ID_BPJS_NUMBER: str
    EMAIL_ADDRESS: str
    PERSON: str
    PHONE_NUMBER: str
    IBAN_CODE: str
    CREDIT_CARD: str
    CRYPTO: str
    IP_ADDRESS: str
    LOCATION: str
    DATE_TIME: str
    NRP: str
    MEDICAL_LICENSE: str
    URL: str
    MONEY: str
    US_BANK_NUMBER: str
    US_DRIVER_LICENSE: str
    US_ITIN: str
    US_PASSPORT: str
    US_SSN: str
    OTHER_NAME: str
    GOD: str
    FACILITY: str
    PRODUCT: str
    EVENT: str
    TIME: str
    NUMBER: str
    MEASUREMENT: str

GLLM_PRIVACY_ENTITIES: Incomplete

class ProsaNERConstant:
    """Defines constants used in the Prosa NER integration.

    This class encapsulates various constants that are utilized throughout the Prosa Named Entity Recognition (NER)
    integration process. These include API headers, API payload keys and values, entity recognition response keys,
    and default values for entity recognition processing.

    Attributes:
        HEADER_CONTENT_TYPE_KEY (str): Key for the content type header.
        HEADER_CONTENT_TYPE_VAL (str): Value for the 'Content-Type' header, typically 'application/json'.
        HEADER_USER_AGENT (str): Key for the user agent header.
        HEADER_USER_AGENT_VAL (str): Value for User-Agent HTTP header for request.
        ID_LANGUAGE (str): Language code for Indonesian language, used in language-specific operations.
        VERSION_CUSTOM_NER (str): Version identifier for the custom NER being used.
        PAYLOAD_VERSION_KEY (str): Key for specifying the version in the API payload.
        PAYLOAD_VERSION_VAL (str): Value for the API version, typically 'v1'.
        PAYLOAD_TEXT_KEY (str): Key for the text to be analyzed in the API payload.
        RESPONSE_TIMEOUT (int): Timeout value for the API response, in seconds.
        ENTITY_TYPE_KEY (str): Key for the entity type in entity dictionaries.
        START_KEY (str): Key for the start index of an entity in the text.
        START_IDX_KEY (str): Key for the start index of an entity in the text returned by Prosa.
        END_KEY (str): Key for the end index of an entity in the text.
        SCORE_KEY (str): Key for the confidence score of the entity recognition.
        DEFAULT_SCORE (float): Default score assigned to recognized entities if not provided.
        RECOGNITION_METADATA_KEY (str): Key for additional metadata associated with recognized entities.
        NAME_KEY (str): Key for the entity's name within the recognition metadata.
        ENTITY_KEY (str): Key for accessing entity string from the API response.
    """
    HEADER_CONTENT_TYPE_KEY: str
    HEADER_CONTENT_TYPE_VAL: str
    HEADER_X_API_KEY_KEY: str
    HEADER_USER_AGENT: str
    HEADER_USER_AGENT_VAL: str
    ID_LANGUAGE: str
    VERSION_CUSTOM_NER: str
    PAYLOAD_VERSION_KEY: str
    PAYLOAD_VERSION_VAL: str
    PAYLOAD_TEXT_KEY: str
    RESPONSE_TIMEOUT: int
    ENTITY_TYPE_KEY: str
    START_KEY: str
    START_IDX_KEY: str
    END_KEY: str
    LENGTH_KEY: str
    SCORE_KEY: str
    DEFAULT_SCORE: float
    RECOGNITION_METADATA_KEY: str
    NAME_KEY: str
    ENTITY_KEY: str

PROSA_ENTITY_MAP: Incomplete
DEFAULT_PROSA_SUPPORTED_PII_ENTITIES: Incomplete
