from faker.providers import BaseProvider

class KTPProvider(BaseProvider):
    """Custom provider for generating KTP (Indonesian identity card) numbers.

    The generated KTP number follows the format: {6}{2}{2}{2}{4}
    - 6 digits of province, city, and sub-district code
    - 2 digits of birthdate. 01-31 for men and 41-71 for women
    - 2 digits of birth month. 01-12
    - 2 digits of birth year. 00-99
    - 4 digits of sequence number
    """
    def ktp(self, gender: str = 'male') -> str:
        '''Generate a KTP number based on the specified gender.

        Args:
            gender (str, optional): The gender of the person ("male" or "female"). Defaults to "male".

        Returns:
            str: A randomly generated KTP number.
        '''
