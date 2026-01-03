from gllm_privacy.pii_detector.constants import Entities as Entities
from presidio_analyzer import PatternRecognizer

class NPWPRecognizer(PatternRecognizer):
    """Recognize NPWP (Nomor Pokok Wajib Pajak) using regex pattern.

    NPWP has 15 digits without accounting separator: {2}.{3}.{3}-{1}.{3}.{3}
    - 2 digits of Tax Identities
    - 3 digits of Registration Number - first part
    - 3 digits of Registration Number - second part
    - 1 digit of Security Number
    - 3 digits of KPP code
    - 3 digits of Tax Status (000 => Pajak Pusat; 001 => Pajak Cabang)
    """
    def __init__(self, supported_language: str = 'id') -> None:
        '''Initialize NPWPRecognizer.

        Args:
            supported_language (str, optional): The supported language for the recognizer. Default to "id".
        '''
