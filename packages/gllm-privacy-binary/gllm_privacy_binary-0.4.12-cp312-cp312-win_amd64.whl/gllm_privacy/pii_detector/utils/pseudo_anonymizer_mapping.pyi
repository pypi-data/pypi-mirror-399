from gllm_privacy.pii_detector.utils.faker_provider import CompanyProvider as CompanyProvider, KTPProvider as KTPProvider
from typing import Callable

def get_pseudoanonymizer_mapping(seed: int | None = None) -> dict[str, Callable]:
    """Get a mapping of entities to pseudo anonymize them.

    Args:
        seed (int | None, optional): An optional seed for the random number generator to ensure reproducibility.

    Returns:
        dict[str, Callable]: A dictionary where keys are entity types and values are functions that generate
            pseudo-anonymized data.

    Raises:
        ImportError: If the `faker` library is not installed.
    """
