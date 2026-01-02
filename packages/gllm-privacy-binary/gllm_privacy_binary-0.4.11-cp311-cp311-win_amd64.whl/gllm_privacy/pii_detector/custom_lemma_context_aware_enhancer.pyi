from _typeshed import Incomplete
from presidio_analyzer import EntityRecognizer as EntityRecognizer, RecognizerResult
from presidio_analyzer.context_aware_enhancers import ContextAwareEnhancer
from presidio_analyzer.nlp_engine import NlpArtifacts

manager: Incomplete
logger: Incomplete

class CustomLemmaContextAwareEnhancer(ContextAwareEnhancer):
    """A class representing a lemma based context aware enhancer logic.

    Context words might enhance confidence score of a recognized entity,
    LemmaContextAwareEnhancer is an implementation of Lemma based context aware logic,
    it compares spacy lemmas of each word in context of the matched entity to given
    context and the recognizer context words,
    if matched it enhance the recognized entity confidence score by a given factor.

    Attributes:
        context_similarity_factor (float): How much to enhance confidence of match entity.
        min_score_with_context_similarity (float): Minimum confidence score.
        context_prefix_count (int): How many words before the entity to match context.
        context_suffix_count (int): How many words after the entity to match context.
        max_phrase_words (int): The maximum number of words to consider in a phrase.
    """
    max_phrase_words: Incomplete
    def __init__(self, context_similarity_factor: float = 0.35, min_score_with_context_similarity: float = 0.4, context_prefix_count: int = 5, context_suffix_count: int = 0, max_phrase_words: int = 3) -> None:
        """Initialize the LemmaContextAwareEnhancer.

        Args:
            context_similarity_factor (float, optional): How much to enhance confidence of match entity.
            min_score_with_context_similarity (float, optional): Minimum confidence score.
            context_prefix_count (int, optional): How many words before the entity to match context.
            context_suffix_count (int, optional): How many words after the entity to match context.
            max_phrase_words (int, optional): The maximum number of words to consider in a phrase.
        """
    def enhance_using_context(self, text: str, raw_results: list[RecognizerResult], nlp_artifacts: NlpArtifacts, recognizers: list[EntityRecognizer], context: list[str] | None = None) -> list[RecognizerResult]:
        """
        Update results in case the lemmas of surrounding words or input context
        words are identical to the context words.

        Using the surrounding words of the actual word matches, look
        for specific strings that if found contribute to the score
        of the result, improving the confidence that the match is
        indeed of that PII entity type

        Args:
            text (str): The actual text that was analyzed.
            raw_results (List[RecognizerResult]): Recognizer results which didn't take context into consideration.
            nlp_artifacts (NlpArtifacts): The nlp artifacts contains elements such as lemmatized tokens for better
                    accuracy of the context enhancement process.
            recognizers (List[EntityRecognizer]): the list of recognizers.
            context (Optional[List[str]], optional): List of context words. Default is None.
        """
