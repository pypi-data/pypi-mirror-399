"""Base tool builder module.

This module contains the abstract base class for tool builders.

Authors:
    Hans Sean Nathanael (hans.s.nathanael@gdplabs.id)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from gl_connectors_sdk.connector import GLConnectors


class BaseToolBuilder(ABC):
    """Abstract base class for tool builders."""

    @abstractmethod
    def create_tool(  # noqa: PLR0913
        self,
        service_name: str,
        endpoint_name: str,
        schema: dict,
        api_base_url: str,
        api_key: str,
        app_name: str,
        default_timeout: int,
    ) -> Any:
        """Create a tool for a given endpoint.

        Args:
            service_name (str): The name of the service.
            endpoint_name (str): The name of the endpoint.
            schema (dict): The schema definition for the endpoint.
            api_base_url (str): The base URL for the API.
            api_key (str): The API key for authentication.
            app_name (str): The name of the application.
            default_timeout (int): Default timeout in seconds for BosaConnector.

        Returns:
            The generated tool object.
        """
        pass

    def _create_run_method(
        self, api_base_url: str, default_api_key: str, app_name: str, endpoint_name: str
    ):
        """Create a unified run method for all tools.

        Args:
            api_base_url: The base URL of Connector.
            default_api_key: The default API key for authentication.
            app_name: The name of the BOSA Plugin.
            endpoint_name: The name of the BOSA Plugin action.

        Returns:
            The unified run method.
        """

        def _run(
            *,
            api_key: Optional[str] = None,
            token: Optional[str] = None,
            identifier: Optional[str] = None,
            timeout: Optional[int] = None,
            request: Dict[str, Any] | None = None,
        ):
            """Uses the tool."""
            # Create input dictionary from kwargs
            input_ = request.copy() if request else None

            api_key = api_key or default_api_key

            # Call execute with the correct parameters
            connector = GLConnectors(
                api_base_url=api_base_url,
                api_key=api_key,
            )

            # Prepare execute parameters
            execute_params = {
                "app_name": app_name,
                "action": endpoint_name,
                "input_": input_,
            }

            # Only add token if it's not None
            if token is not None:
                execute_params["token"] = token

            # Only add identifier if it's not None (account is deprecated)
            if identifier is not None:
                execute_params["identifier"] = identifier

            if timeout is not None:
                execute_params["timeout"] = timeout

            data = connector.execute(**execute_params)
            return data

        return _run

    def _clean_docstring(self, docstring: str) -> str:
        """Clean up docstring by removing unnecessary whitespace and formatting.

        Args:
            docstring (str): The docstring to clean.

        Returns:
            str: The cleaned docstring.
        """
        lines = docstring.split("\n")
        # Get the first line as the main description
        main_desc = lines[0].strip()
        return main_desc
