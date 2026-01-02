"""Action builder for GL Connectors.

This module provides the Action class for building and executing
API requests against GL Connectors.

"""

from typing import Annotated, Any, Dict, Optional, Tuple, Union

from typing_extensions import deprecated

from gl_connectors_sdk.action_response import ActionResponse
from gl_connectors_sdk.auth import BaseAuthenticator
from gl_connectors_sdk.models.file import ConnectorFile
from gl_connectors_sdk.module import GLConnectorModule


# pylint: disable=R0902
class ActionExecutor:
    """Represents a specific action execution for a service.

    Example:
        # Direct execution with raw response
        data, status = github.action('list_pull_requests')\
            .params({'owner': 'GDP-ADMIN', 'repo': 'gl-connectors'})\
            .execute()

        # Or with pagination support
        response = github.action('list_pull_requests')\
            .params({'owner': 'GDP-ADMIN', 'repo': 'gl-connectors'})\
            .run()

        # Get data and handle pagination
        data = response.get_data()
        while response.has_next():
            response = response.next_page()
            data = response.get_data()
    """

    DEFAULT_MAX_ATTEMPTS = 1
    DEFAULT_TIMEOUT = 10

    def __init__(
        self, module: GLConnectorModule, authenticator: BaseAuthenticator, action: str
    ):
        """Initialize the action executor.

        Args:
            module: The connector module to execute against
            authenticator: The authenticator to use for requests
            action: The action name to execute
        """
        self._module = module
        self._authenticator = authenticator
        self._action = action
        self._account: Annotated[
            Optional[str], deprecated("Use 'identifier' instead; will be removed")
        ] = None
        self._identifier: Optional[str] = None
        self._params: Dict[str, Any] = {}
        self._headers: Optional[Dict[str, str]] = None
        self._max_attempts: int = self.DEFAULT_MAX_ATTEMPTS
        self._token: Optional[str] = None
        self._timeout: Optional[int] = None

    def params(self, params: Dict[str, Any]) -> "ActionExecutor":
        """Set additional parameters."""
        self._params = params
        return self

    @deprecated("Use 'identifier' instead; will be removed")
    def account(
        self,
        account: Annotated[
            Optional[str], deprecated("Use 'identifier' instead; will be removed")
        ],
    ) -> "ActionExecutor":
        """Set the user account for the action.

        deprecated:: future version
            The `account` method is deprecated and will be removed in future version.
            Use `identifier()` instead.
        """
        self._account = account
        return self

    def identifier(self, identifier: Optional[str] = None) -> "ActionExecutor":
        """Set the user identifier for the action."""
        self._identifier = identifier
        return self

    def headers(self, headers: Dict[str, str]) -> "ActionExecutor":
        """Set request headers."""
        self._headers = headers
        return self

    def max_attempts(self, attempts: int) -> "ActionExecutor":
        """Set maximum retry attempts."""
        self._max_attempts = attempts
        return self

    def token(self, token: Optional[str]) -> "ActionExecutor":
        """Set the user token for this action."""
        self._token = token
        return self

    def timeout(self, timeout: Optional[int]) -> "ActionExecutor":
        """Set the timeout for the request."""
        self._timeout = timeout
        return self

    def execute(self) -> Tuple[Union[Dict[str, Any], ConnectorFile], int]:
        """Execute request and return raw response.

        Returns:
            Tuple of (response_data, status_code)
        """
        return self._execute()

    def run(self) -> "ActionResponse":
        """Execute request and return paginated response.

        Returns an ActionResponse that supports pagination for list responses.
        For single item responses, pagination methods will return the same item.

        Returns:
            ActionResponse with pagination support
        """
        data, status = self._execute()

        # Define response creator function
        def create_new_response(  # noqa: PLR0913
            params: Dict[str, Any],
            headers: Dict[str, str],
            max_attempts: int,
            token: Optional[str],
            account: Annotated[
                Optional[str], deprecated("Use 'identifier' instead; will be removed")
            ],
            identifier: Optional[str],
            timeout: Optional[int],
        ) -> "ActionResponse":
            executor = ActionExecutor(self._module, self._authenticator, self._action)
            executor.params(params).headers(headers).max_attempts(max_attempts).token(
                token
            ).timeout(timeout).account(account).identifier(identifier)

            return executor.run()

        return ActionResponse(
            response_data=data,
            status=status,
            response_creator=create_new_response,
            initial_executor_request={
                "params": self._params,
                "headers": self._headers,
                "max_attempts": self._max_attempts,
                "token": self._token,
                "account": self._account,  # account is deprecated, remove this in the future
                "identifier": self._identifier,
                "timeout": self._timeout,
            },
        )

    def _execute(self) -> Tuple[Union[Dict[str, Any], ConnectorFile], int]:
        """Execute the action and return raw response.

        Returns:
            Tuple of (response_data, status_code)
        """
        data, status = self._module.execute(
            self._action,
            max_attempts=self._max_attempts,
            input_=self._params,
            token=self._token,
            account=self._account,  # account is deprecated, remove this in the future
            identifier=self._identifier,
            authenticator=self._authenticator,
            headers=self._headers,
            timeout=self._timeout,
        )
        return data, status


class Action:
    """Base class for plugins to prepare action execution.

    Example:
        # Create a GitHub connector
        github = connector.connect('github')

        # Execute with raw response
        data, status = github.action('list_pull_requests')\
            .params({'owner': 'GDP-ADMIN', 'repo': 'gl-connectors'})\
            .execute()

        # Or with pagination support
        response = github.action('list_pull_requests')\
            .params({'owner': 'GDP-ADMIN', 'repo': 'gl-connectors'})\
            .run()
    """

    def __init__(self, module: GLConnectorModule, authenticator: BaseAuthenticator):
        """Initialize the action builder.

        Args:
            module: The connector module to use
            authenticator: The authenticator to use for requests
        """
        self._module = module
        self._authenticator = authenticator

    def action(self, action: str) -> "ActionExecutor":
        """Create a new action executor for a service."""
        return ActionExecutor(self._module, self._authenticator, action)
