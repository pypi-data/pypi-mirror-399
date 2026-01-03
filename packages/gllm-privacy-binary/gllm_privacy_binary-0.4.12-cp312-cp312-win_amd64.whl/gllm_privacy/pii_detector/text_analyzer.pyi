from _typeshed import Incomplete
from gllm_privacy.pii_detector.analyzer import BaseTextAnalyzer as BaseTextAnalyzer
from gllm_privacy.pii_detector.constants import RecognizerResult as RecognizerResult
from gllm_privacy.pii_detector.custom_lemma_context_aware_enhancer import CustomLemmaContextAwareEnhancer as CustomLemmaContextAwareEnhancer
from gllm_privacy.pii_detector.recognizer import BPJSNumberRecognizer as BPJSNumberRecognizer, BankAccountNumberRecognizer as BankAccountNumberRecognizer, CreditCardRecognizer as CreditCardRecognizer, FacebookAccountRecognizer as FacebookAccountRecognizer, FamilyCardNumberRecognizer as FamilyCardNumberRecognizer, GDPLabsEmployeeIdRecognizer as GDPLabsEmployeeIdRecognizer, IndonesianPhoneNumberRecognizer as IndonesianPhoneNumberRecognizer, KTPRecognizer as KTPRecognizer, LinkedinAccountRecognizer as LinkedinAccountRecognizer, MoneyRecognizer as MoneyRecognizer, NPWPRecognizer as NPWPRecognizer, OrganizationNameRecognizer as OrganizationNameRecognizer, ProjectNameRecognizer as ProjectNameRecognizer
from gllm_privacy.pii_detector.utils.spacy_model_loader import ensure_spacy_model as ensure_spacy_model
from presidio_analyzer import EntityRecognizer as EntityRecognizer
from typing import Any

DEFAULT_NLP_CONFIGURATION: Incomplete
MAX_PII_TEXT_LENGTH: int

class TextAnalyzer(BaseTextAnalyzer):
    """TextAnalyzer class to analyze the text and extract the PII entities.

    Implemented using presidio pii library.

    Attributes:
        analyzer (AnalyzerEngine): The analyzer engine to analyze the text and extract the PII entities.
    """
    analyzer: Incomplete
    def __init__(self, additional_recognizers: list[EntityRecognizer] | None = None, nlp_configuration: dict[str, Any] | None = None) -> None:
        """Initialize the TextAnalyzer class and add custom recognizer.

        The predefined recognizers are BankAccountNumberRecognizer, BPJSNumberRecognizer,
        IndonesianPhoneNumberRecognizer, GDPLabsEmployeeIdRecognizer, FacebookAccountRecognizer,
        FamilyCardNumberRecognizer, KTPRecognizer, LinkedinAccountRecognizer, MoneyRecognizer, NPWPRecognizer,
        OrganizationNameRecognizer, and ProjectNameRecognizer.
        We also add Presidio EmailRecognizer and PhoneRecognizer for Indonesian language.

        Args:
            additional_recognizers (list[EntityRecognizer] | None, optional): The list of additional recognizers
                    to be added. Default is None.
            nlp_configuration (dict[str, Any] | None, optional): The configuration for the NLP engine
                    see https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/. Default is None.
        """
    def analyze(self, text: str, language: str = 'id', entities: list[str] | None = None, score_threshold: float | None = 0.46, allow_list: list[str] | None = None, allow_list_match: str | None = 'exact', regex_flags: int | None = ..., **kwargs: Any) -> list[RecognizerResult]:
        '''Analyze the text and extract the PII entities.

        Args:
            text (str): The text to be analyzed.
            language (str, optional): The language of the text to be analyzed. Default is "id".
            entities (list[str]|None, optional): The list of entities to be extracted. If you need to extract
                other entities, add the recognizer in the constructor. Default is None.
            score_threshold (float|None, optional): The minimum score threshold for the extracted entities.
                Default is 0.46.
            allow_list (list | None, optional): List of words that the user defines as being allowed to keep in
                the text. Default is None.
            allow_list_match (str | None, optional): The matching strategy for the allow list. Default is "exact".
            regex_flags (int | None, optional): The regex flags for the text analysis.
            **kwargs (Any): Additional keyword arguments that may be needed for the text analysis process.

        Returns:
            list[RecognizerResult]: The list of extracted entities
        '''
