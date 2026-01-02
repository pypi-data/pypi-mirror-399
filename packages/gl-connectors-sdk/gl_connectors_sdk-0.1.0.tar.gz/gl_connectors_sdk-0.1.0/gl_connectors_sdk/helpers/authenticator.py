"""Authenticator module for GL Connectors.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

import requests
from typing_extensions import deprecated

from gl_connectors_sdk.auth import ApiKeyAuthenticator
from gl_connectors_sdk.constant import DEFAULT_API_KEY, DEFAULT_API_URL
from gl_connectors_sdk.models.token import GLToken
from gl_connectors_sdk.models.user import CreateUserResponse, GLUser


class GLAuthenticator:
    """Authenticator for GL Connectors."""

    DEFAULT_TIMEOUT = 10

    def __init__(
        self, api_base_url: str = DEFAULT_API_URL, api_key: str = DEFAULT_API_KEY
    ):
        """Initialize the GLAuthenticator with the provided API key.

        Args:
            api_base_url (str): The base URL for GL Connectors. Defaults to DEFAULT_API_URL.
            api_key (str): The API key for authentication. Defaults to DEFAULT_API_KEY.
        """
        self.api_base_url = api_base_url
        self.auth_scheme = ApiKeyAuthenticator(api_key)

    def register(self, identifier: str) -> CreateUserResponse:
        """Register a User in the scope of GL Connectors.

        Args:
            identifier: Username

        Returns:
            User Data with the secret
        """
        headers = {self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key}
        response = requests.post(
            f"{self.api_base_url}/users",
            json={"identifier": identifier},
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:  # noqa PLR2004
            raise ValueError(f"Failed to register user: {response.json()}")

        data = response.json()["data"]
        return CreateUserResponse.model_validate(data)

    def authenticate(self, identifier: str, secret: str) -> GLToken:
        """Authenticate a User in the scope of GL Connectors.

        Args:
            identifier: Username
            secret: Password

        Returns:
            User Token
        """
        headers = {self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key}
        response = requests.post(
            f"{self.api_base_url}/auth/tokens",
            json={"identifier": identifier, "secret": secret},
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:  # noqa PLR2004
            raise ValueError(f"Failed to authenticate user: {response.json()}")

        data = response.json()["data"]
        return GLToken.model_validate(data)

    def get_user(self, token: str) -> GLUser:
        """Get the current user from GL Connectors.

        Args:
            token: The User Token

        Returns:
            User information
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            f"{self.api_base_url}/users/me",
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:  # noqa PLR2004
            raise ValueError(f"Failed to receive user. {str(response.json())}")

        data = response.json()["data"]
        return GLUser.model_validate(data)


@deprecated("Use 'GLAuthenticator' instead; will be removed in a future version")
class BosaAuthenticator(GLAuthenticator):
    """Deprecated: Use GLAuthenticator instead."""

    pass
