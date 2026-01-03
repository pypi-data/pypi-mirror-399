from _typeshed import Incomplete
from spacy.language import Language

logger: Incomplete
DEFAULT_SPACY_MODEL: str
DEFAULT_SPACY_MODEL_VERSION: str
SPACY_MODEL_URL_TEMPLATE: str
MAX_LOAD_ATTEMPTS: int
RETRY_DELAY_SECONDS: float

def load_spacy_model(model_name: str = ..., model_version: str = ..., auto_install: bool = True) -> Language:
    """Load a spaCy model, optionally installing it if not found.

    Args:
        model_name: The name of the spaCy model to load.
        model_version: The version of the model to install if auto_install is True.
        auto_install: If True, automatically install the model if not found.

    Returns:
        Language: The loaded spaCy model.

    Raises:
        OSError: If the model cannot be loaded and auto_install is False.
        RuntimeError: If auto-installation fails.
    """
def ensure_spacy_model(model_name: str = ..., model_version: str = ...) -> None:
    """Ensure a spaCy model is available, installing it if necessary.

    Args:
        model_name: The name of the spaCy model.
        model_version: The version of the model to install if needed.

    Raises:
        RuntimeError: If the model cannot be installed or loaded.
    """
