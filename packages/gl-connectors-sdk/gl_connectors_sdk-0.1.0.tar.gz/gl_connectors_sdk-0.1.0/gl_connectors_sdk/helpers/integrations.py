"""Integration helper module for GL Connectors.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from typing import Any

import requests
from typing_extensions import deprecated

from gl_connectors_sdk.auth import ApiKeyAuthenticator
from gl_connectors_sdk.constant import DEFAULT_API_KEY, DEFAULT_API_URL
from gl_connectors_sdk.models.result import ActionResult


class GLIntegrationHelper:
    """Helper class for GL Connectors integrations."""

    OAUTH2_FLOW_ENDPOINT = "/connectors/{name}/integrations"
    INTEGRATION_USER_ENDPOINT = "/connectors/{name}/integrations/{user_identifier}"
    INTEGRATION_CHECK_ENDPOINT = "/connectors/{name}/integration-exists"
    DEFAULT_TIMEOUT = 10

    def __init__(
        self, api_base_url: str = DEFAULT_API_URL, api_key: str = DEFAULT_API_KEY
    ):
        """Initializes the GLIntegrationHelper with the provided API key.

        Args:
            api_base_url (str): The base URL for GL Connectors. Defaults to DEFAULT_API_URL.
            api_key (str): The API key for authentication. Defaults to DEFAULT_API_KEY.
        """
        self.api_base_url = api_base_url
        self.auth_scheme = ApiKeyAuthenticator(api_key)

    def user_has_integration(self, app_name: str, token: str) -> bool:
        """Checks whether or not a user has an integration for a given app in this client.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token

        Returns:
            True if the user has an integration for the given app
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            f"{self.api_base_url}{self.INTEGRATION_CHECK_ENDPOINT.format(name=app_name)}",
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )
        return (
            response.status_code == 200 and response.json()["data"]["has_integration"]
        )  # noqa PLR2004

    def initiate_integration(self, app_name: str, token: str, callback_uri: str) -> str:
        """Initiates a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            callback_uri: The callback URL to be used for the integration

        Returns:
            The integration URL
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        body = {"callback_url": callback_uri}
        response = requests.post(
            f"{self.api_base_url}{self.OAUTH2_FLOW_ENDPOINT.format(name=app_name)}",
            headers=headers,
            json=body,
            timeout=self.DEFAULT_TIMEOUT,
        )
        response_json = response.json()
        if response.status_code != 200:  # noqa PLR2004
            if response_json.get("message"):
                raise ValueError(
                    f"Failed to initiate integration: {response_json['message']}"
                )
            if response_json.get("error") and response_json["error"].get("message"):
                raise ValueError(
                    f"Failed to initiate integration: {response_json['error']['message']}"
                )
            raise ValueError("Failed to initiate integration")
        return response_json["data"]["url"]

    def initiate_plugin_configuration(
        self, app_name: str, token: str, config: dict[str, Any]
    ) -> ActionResult:
        """Initiates a plugin configuration for a given app/connector.

        Used to initiate a connector that requires a plugin configuration and may not
        support the OAuth2 flow.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            config: The configuration for the integration

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        request_body = {
            "auth_type": "custom",
            "configuration": config,
        }
        response = requests.post(
            f"{self.api_base_url}{self.OAUTH2_FLOW_ENDPOINT.format(name=app_name)}",
            headers=headers,
            json=request_body,
            timeout=self.DEFAULT_TIMEOUT,
        )
        response_json = response.json()
        if response.status_code != 200:  # noqa PLR2004
            raise ValueError(
                f"Failed to initiate plugin configuration: {response_json['message']}"
            )
        return ActionResult(
            success=True, message="Plugin configuration initiated successfully."
        )

    def select_integration(
        self, app_name: str, token: str, user_identifier: str
    ) -> ActionResult:
        """Selects a 3rd party integration for a user against a certain client.

        Args:
            token: The User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to select

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        integration_endpoint = self.INTEGRATION_USER_ENDPOINT.format(
            name=app_name, user_identifier=user_identifier
        )
        response = requests.post(
            f"{self.api_base_url}{integration_endpoint}",
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )
        response_json = response.json()

        data = response_json.get("data", {})
        success = data.get("success", False)
        message = data.get("error", "success")
        return ActionResult(success=success, message=message)

    def get_integration(self, app_name: str, token: str, user_identifier: str) -> dict:
        """Gets a 3rd party integration for a user against a certain client.

        Args:
            token: The User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to get

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        integration_endpoint = self.INTEGRATION_USER_ENDPOINT.format(
            name=app_name, user_identifier=user_identifier
        )
        response = requests.get(
            f"{self.api_base_url}{integration_endpoint}",
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )
        response_json = response.json()

        data = response_json.get("data", {})
        return data

    def remove_integration(
        self, app_name: str, token: str, user_identifier: str
    ) -> ActionResult:
        """Removes a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            user_identifier: User identifier to specify which integration to remove

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        headers = {
            self.auth_scheme.API_KEY_HEADER: self.auth_scheme.api_key,
            "Authorization": f"Bearer {token}",
        }
        integration_endpoint = self.INTEGRATION_USER_ENDPOINT.format(
            name=app_name, user_identifier=user_identifier
        )
        response = requests.delete(
            f"{self.api_base_url}{integration_endpoint}",
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT,
        )
        response_json = response.json()

        data = response_json.get("data", {})
        success = data.get("success", False)
        message = data.get("error", "success")
        return ActionResult(success=success, message=message)


@deprecated("Use 'GLIntegrationHelper' instead; will be removed in a future version")
class BosaIntegrationHelper(GLIntegrationHelper):
    """Deprecated: Use GLIntegrationHelper instead."""

    pass
