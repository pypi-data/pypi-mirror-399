"""The entrypoint class for GL Connectors SDK.

This class serves as the main point where implementors will instantiate
in order to use GL Connectors using this SDK. They only need to initialize
this class using the Base URL and API Key as such:

```python
# Initialize connector
connector = GLConnectors(api_base_url="https://connector.gdplabs.id", api_key="your-key")

# Create action builders for different plugins
github = connector.connect('github')
gdrive = connector.connect('google_drive') # This is just an example

# Method 1: Direct execution with raw response
data, status = connector.execute('github', 'list_pull_requests',
    owner='GDP-ADMIN',
    repo='gl-connectors',
    page=1,
    per_page=10
)

# Method 2: Direct execution with pagination
response = connector.run('github', 'list_pull_requests',
    owner='GDP-ADMIN',
    repo='gl-connectors',
    page=1,
    per_page=10
)

# Method 3: Fluent interface with raw response
data, status = github.action('list_pull_requests')\
    .params({
        'owner': 'GDP-ADMIN',
        'repo': 'gl-connectors',
        'page': 1,
        'per_page': 10
    })\
    .token('user-token')\
    .headers({'X-Custom-Header': 'value'})\
    .execute()

# Method 4: Fluent interface with pagination
response = github.action('list_pull_requests')\
    .params({
        'owner': 'GDP-ADMIN',
        'repo': 'gl-connectors',
        'page': 1,
        'per_page': 10
    })\
    .token('user-token')\
    .headers({'X-Custom-Header': 'value'})\
    .run()

# Pagination example
data = response.get_data()
while response.has_next():
    response = response.next_page()
    data = response.get_data()
```

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

import logging
from typing import Annotated, Any, Dict, List, Optional

import requests
from requests.exceptions import HTTPError
from typing_extensions import deprecated

from gl_connectors_sdk.action import Action
from gl_connectors_sdk.action_response import ActionResponse
from gl_connectors_sdk.auth import ApiKeyAuthenticator
from gl_connectors_sdk.constant import DEFAULT_API_KEY, DEFAULT_API_URL
from gl_connectors_sdk.helpers.authenticator import GLAuthenticator
from gl_connectors_sdk.helpers.integrations import GLIntegrationHelper
from gl_connectors_sdk.models.file import ConnectorFile
from gl_connectors_sdk.models.result import ActionResult
from gl_connectors_sdk.models.token import GLToken
from gl_connectors_sdk.models.user import CreateUserResponse, GLUser
from gl_connectors_sdk.module import GLConnectorError, GLConnectorModule


class GLConnectors:
    """Main connector class that manages all GL Connectors SDK modules."""

    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_ATTEMPTS = 1
    OAUTH2_FLOW_ENDPOINT = "/connectors/{name}/integrations"
    INTEGRATION_CHECK_ENDPOINT = "/connectors/{name}/integration-exists"

    _instance = None

    def __init__(self, api_base_url: str = DEFAULT_API_URL, api_key: str = DEFAULT_API_KEY):
        """Initialization."""
        if not hasattr(self, "_initialized"):
            self.api_base_url = api_base_url
            self.auth_scheme = ApiKeyAuthenticator(api_key)
            self._authenticator = GLAuthenticator(api_base_url, api_key)
            self._integration_helper = GLIntegrationHelper(api_base_url, api_key)
            self._modules: Dict[str, GLConnectorModule] = {}
            self._initialized = True

    @property
    def bosa_authenticator(self) -> GLAuthenticator:
        """Deprecated: Use _authenticator instead."""
        return self._authenticator

    @property
    def bosa_integration_helper(self) -> GLIntegrationHelper:
        """Deprecated: Use _integration_helper instead."""
        return self._integration_helper

    def get_available_modules(self) -> List[str]:
        """Scan and cache all available connector modules.

        Returns:
            List of available modules
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/{GLConnectorModule.LIST_NAME_PATH}", timeout=self.DEFAULT_TIMEOUT
            )
            if response.status_code == 200:  # noqa PLR2004
                return response.json()
            return []
        except Exception as e:
            raise GLConnectorError(f"Failed to scan available modules: {str(e)}") from e

    def create_user(self, identifier: str) -> CreateUserResponse:
        """Create a GL Connectors User in the scope of Connector.

        Args:
            identifier: Username

        Returns:
            User Data with the secret
        """
        return self._authenticator.register(identifier)

    @deprecated("Use 'create_user' instead; will be removed in a future version")
    def create_bosa_user(self, identifier: str) -> CreateUserResponse:
        """Create a User in the scope of Connector.

        .. deprecated::
            Use :meth:`create_user` instead. This method will be removed in a future version.

        Args:
            identifier: Username

        Returns:
            User Data with the secret
        """
        return self.create_user(identifier)

    def authenticate(self, identifier: str, secret: str) -> GLToken:
        """Triggers the authentication of the User in the scope of Connector.

        Args:
            identifier: Username
            secret: Password

        Returns:
            User Token
        """
        return self._authenticator.authenticate(identifier, secret)

    @deprecated("Use 'authenticate' instead; will be removed in a future version")
    def authenticate_bosa_user(self, identifier: str, secret: str) -> GLToken:
        """Triggers the authentication of the User in the scope of Connector.

        .. deprecated::
            Use :meth:`authenticate` instead. This method will be removed in a future version.

        Args:
            identifier: Username
            secret: Password

        Returns:
            User Token
        """
        return self.authenticate(identifier, secret)

    def initiate_connector_auth(self, app_name: str, token: str, callback_uri: str) -> str:
        """Triggers the OAuth2 flow for a connector for this API Key and User Token.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            callback_uri: The callback URL to be used for the integration

        Returns:
            The redirect URL to be used for the integration
        """
        return self._integration_helper.initiate_integration(app_name, token, callback_uri)

    def initiate_plugin_configuration(self, app_name: str, token: str, config: dict[str, Any]) -> ActionResult:
        """Initiates a plugin configuration for a given app/connector.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            config: The configuration for the integration

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        return self._integration_helper.initiate_plugin_configuration(app_name, token, config)

    def get_user_info(self, token: str) -> GLUser:
        """Gets the user information for a given token.

        Args:
            token: The User Token

        Returns:
            User information
        """
        return self._authenticator.get_user(token)

    def user_has_integration(self, app_name: str, token: str) -> bool:
        """Checks whether or not a user has an integration for a given app in this client.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token

        Returns:
            True if the user has an integration for the given app
        """
        return self._integration_helper.user_has_integration(app_name, token)

    def select_integration(self, app_name: str, token: str, user_identifier: str) -> ActionResult:
        """Selects a 3rd party integration for a user against a certain client.

        Args:
            token: The User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to select

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        return self._integration_helper.select_integration(app_name, token, user_identifier)

    def get_integration(self, app_name: str, token: str, user_identifier: str) -> dict:
        """Gets a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The User Token
            user_identifier: User identifier to specify which integration to get

        Returns:
            The integration data as a dictionary
        """
        return self._integration_helper.get_integration(app_name, token, user_identifier)

    def remove_integration(self, app_name: str, token: str, user_identifier: str) -> ActionResult:
        """Removes a 3rd party integration for a user against a certain client.

        Args:
            token: The User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to remove

        Returns:
            Result that contains an error message (if any), and the success status.
        """
        return self._integration_helper.remove_integration(app_name, token, user_identifier)

    def get_connector(self, app_name: str) -> GLConnectorModule:
        """Get or create an instance of a connector module.

        Args:
            app_name: The name of the app/connector to use

        Returns:
            GLConnectorModule: The connector module
        """
        try:
            if app_name not in self._modules:
                application = GLConnectorModule(app_name, self.api_base_url, GLConnectorModule.INFO_PATH)
                self._modules[app_name] = application
        except GLConnectorError as e:
            logging.warning(f"No connector found for app '{app_name}': {str(e)}")
            raise GLConnectorError(f"No connector found for app '{app_name}': {str(e)}") from e
        except HTTPError as e:
            logging.warning(f"Connector failed to initialize: {str(e)}")
            raise GLConnectorError(f"Connector failed to initialize: {str(e)}") from e
        except Exception as e:
            logging.warning(f"Failed to get connector for app '{app_name}': {str(e)}")
            raise GLConnectorError(f"Failed to get connector for app '{app_name}': {str(e)}") from e
        return self._modules[app_name]

    def refresh_connector(self, app_name: str) -> None:
        """Refresh the connector module."""
        if app_name in self._modules:
            del self._modules[app_name]

    def connect(self, app_name: str) -> Action:
        """Connect to a specific module and prepare for action execution.

        Creates an Action instance for the specified connector.

        Example:
            # Create action builders for different connectors
            github = connector.connect('github')
            gdrive = connector.connect('google_drive') # This is just an example

        Args:
            app_name: The name of the app/connector to use (eg: 'github', 'google_drive', etc)

        Returns:
            Action: A new Action instance for the specified connector
        """
        module = self.get_connector(app_name)
        return Action(module, self.auth_scheme)

    def execute(  # noqa: PLR0913
        self,
        app_name: str,
        action: str,
        *,
        identifier: Optional[str] = None,
        account: Annotated[Optional[str], deprecated("Use 'identifier' instead; will be removed")] = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        input_: Dict[str, Any] = None,
        token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> tuple[Dict[str, Any] | ConnectorFile, int]:
        """Execute an action on a specific module and return raw response.

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(app_name, action, params_dict)
        2. As keyword arguments: execute(app_name, action, param1=value1, param2=value2)

        Args:
            app_name: The name of the app/connector to use
            action: The action to execute
            input_: Optional input data for the action
            token: The User Token
            identifier: Optional user integration account identifier
            account: Optional user integration account identifier (deprecated, remove this in the future)
            headers: Optional headers to include in the request
            max_attempts: The number of times the request can be retried for. Default is 0 (does not retry). Note that
                the backoff factor is 2^(N - 1) with the basic value being 1 second (1, 2, 4, 8, 16, 32, ...).
                Maximum number of retries is 10 with a maximum of 64 seconds per retry.
            timeout: Optional timeout for the request in seconds. Default is 30 seconds.
            **kwargs: Optional keyword arguments

        Returns:
            Tuple of (response, status_code) where response is the API response and status_code is the HTTP status code
        """
        module = self.get_connector(app_name)

        # If input_ is provided, use it as params
        # Otherwise, use kwargs as params
        params = input_ if isinstance(input_, dict) else kwargs

        return module.execute(
            action,
            max_attempts=max_attempts,
            input_=params,
            token=token,
            identifier=identifier or account,  # account is deprecated, remove this in the future
            authenticator=self.auth_scheme,
            headers=headers,
            timeout=timeout,
        )

    def run(  # noqa: PLR0913
        self,
        app_name: str,
        action: str,
        *,
        identifier: Optional[str] = None,
        account: Annotated[Optional[str], deprecated("Use 'identifier' instead; will be removed")] = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        input_: Dict[str, Any] = None,
        token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> ActionResponse:
        """Execute an action on a specific module and return paginated response.

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(app_name, action, input_dict)
        2. As keyword arguments: execute(app_name, action, param1=value1, param2=value2)

        Args:
            app_name: The name of the app/connector to use
            action: The action to execute
            input_: Optional input data for the action
            token: The User Token
            identifier: Optional user identifier to use for the request
            account: Optional user identifier to use for the request (deprecated, remove this in the future)
            headers: Optional headers to include in the request
            max_attempts: The number of times the request can be retried for. Default is 0 (does not retry). Note that
                the backoff factor is 2^(N - 1) with the basic value being 1 second (1, 2, 4, 8, 16, 32, ...).
                Maximum number of retries is 10 with a maximum of 64 seconds per retry.
            timeout: Optional timeout for the request in seconds. Default is 30 seconds.
            **kwargs: Optional keyword arguments

        Returns:
            ActionResponse: Response wrapper with pagination support
        """
        # If input_ is provided, use it as params
        # Otherwise, use kwargs as params
        params = input_ if isinstance(input_, dict) else kwargs

        executor = (
            self.connect(app_name)
            .action(action)
            .token(token)
            .headers(headers)
            .identifier(identifier or account)
            .max_attempts(max_attempts)
            .params(params)
            .timeout(timeout)
        )

        return executor.run()


@deprecated("Use 'GLConnectors' instead; will be removed in a future version")
class BosaConnector(GLConnectors):
    """Deprecated: Use GLConnectors instead.

    This class is provided for backwards compatibility and will be removed in a future version.
    """

    pass
