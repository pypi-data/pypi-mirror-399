from _typeshed import Incomplete
from enum import StrEnum
from gllm_privacy.pii_detector.recognizer.config import CAHYA_BERT_CONFIGURATION as CAHYA_BERT_CONFIGURATION
from gllm_privacy.pii_detector.utils.text_chunker import TokenAwareTextChunker as TokenAwareTextChunker
from presidio_analyzer import AnalysisExplanation, EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from transformers import TokenClassificationPipeline
from typing import TypedDict

manager: Incomplete
logger: Incomplete
PUNCTUATION_CHARS: str
TRANSFORMERS_AVAILABLE: bool
available_providers: Incomplete
OPTIMUM_ONNX_CUDA_AVAILABLE: Incomplete
OPTIMUM_ONNX_AVAILABLE: bool
BACKEND_MPS: str
BACKEND_TRANSFORMERS: str
BACKEND_ONNX: str
BACKEND_CUDA: str
DEVICE_MPS: str
DEVICE_CUDA: str
DEVICE_CPU: str
OPTIMIZATION_FP16: str
OPTIMIZATION_ONNX_OPTIMIZATION: str
OPTIMIZATION_MPS_ACCELERATION: str

class TokenizationLevel(StrEnum):
    """Tokenization granularity strategies for entity recognition."""
    SUBWORD: str
    WORD: str

class PredictionEntity(TypedDict):
    """Type definition for entity prediction dictionary.

    This represents the structure of entity predictions returned by the
    transformers pipeline and processed by the recognizer methods.

    Attributes:
        entity_group (str): The entity type/group (e.g., 'PER', 'LOC', 'ORG').
        word (str): The detected entity text.
        start (int): Start position of the entity in the text.
        end (int): End position of the entity in the text.
        score (float): Confidence score of the prediction (0.0 to 1.0)
    """
    entity_group: str
    word: str
    start: int
    end: int
    score: float

class OptimumPipelineManager:
    """Manages different pipeline backends for optimal performance.

    This class handles the creation and management of different pipeline types:
    - NVIDIA TensorRT-LLM (via optimum-nvidia) for maximum GPU performance
    - ONNX Runtime for CPU optimization
    - Standard transformers as fallback

    Attributes:
        backend (str): The current backend being used.
        pipeline: The active pipeline instance.
        config (dict): Configuration for the pipeline.
    """
    config: Incomplete
    backend: Incomplete
    pipeline: Incomplete
    def __init__(self, config: dict) -> None:
        """Initialize the pipeline manager.

        Args:
            config (dict): Configuration dictionary containing Optimum settings.
        """
    def create_pipeline(self, model_path: str, tokenizer, aggregation_strategy: str = 'simple', ignore_labels: list = None):
        """Create a pipeline with the optimal backend.

        Args:
            model_path (str): Path to the model.
            tokenizer: The tokenizer instance.
            aggregation_strategy (str): Strategy for aggregating sub-word tokens.
            ignore_labels (list): Labels to ignore during inference.
        """
    def get_pipeline(self) -> TokenClassificationPipeline:
        """Get the current pipeline instance.

        Returns:
            TokenClassificationPipeline: The current pipeline instance.
        """
    def get_backend_info(self) -> dict[str, str | int | bool]:
        """Get information about the current backend.

        Returns:
            dict[str, str | int | bool]: Information about the current backend.
        """

class TransformersRecognizer(EntityRecognizer):
    '''Wrapper for a transformers model, if needed to be used within Presidio Analyzer.

    The class loads models hosted on HuggingFace - https://huggingface.co/
    and loads the model and tokenizer into a TokenClassification pipeline.
    Samples are split into short text chunks, ideally shorter than max_length input_ids of the individual model,
    to avoid truncation by the Tokenizer and loss of information

    A configuration object should be maintained for each dataset-model combination and translate
    entities names into a standardized view. A sample of a configuration file is attached in
    the example.

    Attributes:
        model_path (str | None, optional): String referencing a HuggingFace uploaded model to be used
                for inference. Defaults to None.
        pipeline (TokenClassificationPipeline | None, optional): Instance of a TokenClassificationPipeline
                including a Tokenizer and a Model. Defaults to None.
        supported_entities (list[str] | None, optional): List of entities to run inference on. Defaults to None.
        optimum_manager (OptimumPipelineManager | None, optional): Manager for Optimum pipeline backends.

    Thread-safety:
        This recognizer supports multi-threaded reuse by serializing calls into the underlying tokenizer
        (including HuggingFace "fast" tokenizers) to avoid runtime errors such as "Already borrowed".
    '''
    model_path: Incomplete
    pipeline: Incomplete
    tokenization_level: Incomplete
    is_loaded: bool
    use_optimum: Incomplete
    aggregation_mechanism: Incomplete
    ignore_labels: Incomplete
    model_to_presidio_mapping: Incomplete
    entity_mapping: Incomplete
    default_explanation: Incomplete
    chunk_length: Incomplete
    id_entity_name: Incomplete
    id_score_reduction: Incomplete
    model: Incomplete
    tokenizer: Incomplete
    text_chunker: Incomplete
    optimum_manager: Incomplete
    def __init__(self, model_path: str | None = None, pipeline: TokenClassificationPipeline | None = None, supported_entities: list[str] | None = None, tokenization_level: TokenizationLevel = ..., use_optimum: bool | None = None, supported_language: str = 'id') -> None:
        '''Initialize the TransformersRecognizer.

        Args:
            model_path (str | None, optional): Path to the model to be used for inference. Defaults to None.
            pipeline (TokenClassificationPipeline | None, optional): Instance of a TokenClassificationPipeline
                including a Tokenizer and a Model. Defaults to None.
            supported_entities (list[str] | None, optional): List of entities to run inference on. Defaults to None.
            tokenization_level (TokenizationLevel, optional): Tokenization granularity strategy.
                SUBWORD uses standard transformers subword tokenization,
                WORD uses word-level boundary detection. Defaults to TokenizationLevel.SUBWORD.
            use_optimum (bool | None, optional): Whether to use Optimum optimizations. Defaults to None (auto-detect).
            supported_language (str, optional): The supported language for the recognizer. Defaults to "id".
        '''
    def load(self) -> None:
        """Initialize the recognizer assets if needed."""
    def load_transformer(self, **kwargs) -> None:
        '''Load external configuration parameters and set default values.

        Args:
            **kwargs: Default values for class attributes and modify pipeline behavior.
                DATASET_TO_PRESIDIO_MAPPING (dict): Defines mapping entity strings from dataset format to
                    Presidio format.
                MODEL_TO_PRESIDIO_MAPPING (dict): Defines mapping entity strings from chosen model format to
                    Presidio format.
                SUB_WORD_AGGREGATION (str): Define how to aggregate sub-word tokens into full words and spans as defined
                    in HuggingFace https://huggingface.co/transformers/v4.8.0/main_classes/pipelines.html
                CHUNK_SIZE (int): Number of characters in each chunk of text.
                LABELS_TO_IGNORE (list[str]): List of entities to skip evaluation. Defaults to ["O"].
                DEFAULT_EXPLANATION (str): String format to use for prediction explanations.
                ID_ENTITY_NAME (str): Name of the ID entity.
                ID_SCORE_REDUCTION (float): Score multiplier for ID entities.
                USE_OPTIMUM (bool): Whether to use Optimum optimizations.
                OPTIMUM_BACKEND (str): Backend to use for Optimum ("auto", BACKEND_ONNX, BACKEND_CUDA, BACKEND_MPS,
                    BACKEND_TRANSFORMERS).
                OPTIMUM_QUANTIZATION (bool): Whether to use quantization.
                OPTIMUM_DEVICE (str): Device to use for inference.
                OPTIMUM_FP8 (bool): Whether to use FP8 precision (NVIDIA Hopper/Ada-Lovelace only).
                OPTIMUM_MAX_BATCH_SIZE (int): Maximum batch size for Optimum models.
                TOKENIZATION_LEVEL(str): The tokenization level to use ("word", "subword").
        '''
    def get_supported_entities(self) -> list[str]:
        """Return supported entities by this model.

        Returns:
            list[str]: List of the supported entities.
        """
    def get_pipeline_info(self) -> dict:
        """Get information about the current pipeline and its optimizations.

        Returns:
            dict: Information about the pipeline backend, device, and optimizations.
        """
    def switch_backend(self, backend: str) -> bool:
        """Switch to a different backend if available.

        Args:
            backend (str): The backend to switch to (BACKEND_ONNX, BACKEND_CUDA, BACKEND_MPS, BACKEND_TRANSFORMERS)

        Returns:
            bool: True if the switch was successful, False otherwise
        """
    def analyze(self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts = None) -> list[RecognizerResult]:
        """Analyze text using transformers model to produce NER tagging.

        Args:
            text (str): The text for analysis.
            entities (list[str]): The list of entities this recognizer is able to detect.
            nlp_artifacts (NlpArtifacts, optional): Not used by this recognizer.

        Returns:
            list[RecognizerResult]: The list of Presidio RecognizerResult constructed from the recognized
                transformers detections.
        """
    def build_transformers_explanation(self, original_score: float, explanation: str, pattern: str) -> AnalysisExplanation:
        """Create explanation for why this result was detected.

        Args:
            original_score (float): Score given by this recognizer.
            explanation (str): Explanation string.
            pattern (str): Regex pattern used.

        Returns:
            AnalysisExplanation: Structured explanation and scores of a NER model prediction.
        """
    @staticmethod
    def split_long_text(text: str, start_pos: int, max_length: int) -> list[tuple[int, int]]:
        """Split a long text into chunks at word boundaries.

        Args:
            text (str): Text to split
            start_pos (int): Starting position in the original text
            max_length (int): Maximum length of each chunk

        Returns:
            list of (start, end) position tuples for each chunk
        """
