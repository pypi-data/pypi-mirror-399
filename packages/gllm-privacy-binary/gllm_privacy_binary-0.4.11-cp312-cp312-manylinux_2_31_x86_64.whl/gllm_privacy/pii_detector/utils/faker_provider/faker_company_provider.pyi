from faker.providers import BaseProvider

class CompanyProvider(BaseProvider):
    """Custom provider for generating company names with specific formats."""
    def custom_company(self) -> str:
        """Generate a custom company name with a specific format.

        The format can be one of the following:
        - PT <company_name>
        - CV <company_name>
        - PT <company_name> Tbk

        Returns:
            str: A custom company name in the selected format.
        """
