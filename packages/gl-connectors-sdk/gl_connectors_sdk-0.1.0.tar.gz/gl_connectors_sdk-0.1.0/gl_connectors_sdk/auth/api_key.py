"""API Key Authentication for Connector.

Utilizes `X-API-Key` header for authenticating against
Connector.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from gl_connectors_sdk.auth.base import BaseAuthenticator


class ApiKeyAuthenticator(BaseAuthenticator):
    """Injects API Key Headers to Connector for Authentication."""

    API_KEY_HEADER = "X-API-Key"

    def __init__(self, api_key: str):
        """Initializes the ApiKeyAuthenticator with the provided API key.

        Args:
            api_key (str): The API key for authentication.
        """
        self.api_key = api_key

    def authenticate(self):
        """Authenticates the request.

        Raises:
            AuthenticationError: If authentication fails.
        """
        return {self.API_KEY_HEADER: self.api_key}
