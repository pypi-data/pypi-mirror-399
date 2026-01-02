"""Langchain tool builder module.

This module contains the Langchain tool builder implementation.

Authors:
    Hans Sean Nathanael (hans.s.nathanael@gdplabs.id)
"""

from functools import wraps
from typing import Callable, Dict

from langchain_core.tools import BaseTool

from gl_connectors_sdk.helpers.tool_builder.base import BaseToolBuilder
from gl_connectors_sdk.helpers.tool_builder.json_schema_generator import (
    create_input_json_schema,
)


class LangchainToolBuilder(BaseToolBuilder):
    """Tool builder for Langchain tools."""

    def create_tool(  # noqa: PLR0913
        self,
        service_name: str,
        endpoint_name: str,
        schema: dict,
        api_base_url: str,
        api_key: str,
        app_name: str,
        default_timeout: int,
    ) -> BaseTool:
        """Create a Langchain tool for a given endpoint.

        Args:
            service_name (str): The name of the service.
            endpoint_name (str): The name of the endpoint.
            schema (dict): The schema definition for the endpoint.
            api_base_url (str): The base URL for the API.
            api_key (str): The API key for authentication.
            app_name (str): The name of the application.
            default_timeout (int): Default timeout in seconds for BosaConnector.

        Returns:
            BaseTool: The generated Langchain tool object.
        """
        # Get the docstring from the schema
        docstring = self._clean_docstring(schema.get("docstring", "").strip())

        # Create the tool name in snake_case
        tool_name = f"{service_name}_{endpoint_name.replace('-', '_')}_tool"

        # Get the request model with proper service prefix
        service_prefix = "".join(word.capitalize() for word in service_name.split("_"))

        # Create the request model with auth handling built-in
        request_schema = create_input_json_schema(
            endpoint_name, schema, default_timeout, service_prefix
        )

        run_method = self._create_run_method(
            api_base_url, api_key, app_name, endpoint_name
        )
        run_method = self._wrap_run_method(run_method)

        # Create the class
        class ToolClass(BaseTool):
            """Tool class for interacting with the endpoint.

            This class is generated dynamically based on the OpenAPI schema.

            Attributes:
                name (str): The name of the tool.
                description (str): The description of the tool.
                args_schema (Type[BaseModel]): The Pydantic model for request validation.
                app_name (ClassVar[str]): The name of the application.
                api_base_url (ClassVar[str]): The base URL for the API.
                api_key (ClassVar[str]): The API key for authentication.
            """

            name: str = tool_name
            description: str = docstring
            args_schema: Dict = request_schema
            _run = run_method

            async def _arun(self, **kwargs):
                """Async implementation of the tool."""
                return self._run(**kwargs)

        # Set the class name
        endpoint_suffix = self._normalize_endpoint_name(endpoint_name)
        ToolClass.__name__ = f"{service_prefix}{endpoint_suffix}Tool"
        ToolClass.__qualname__ = ToolClass.__name__

        return ToolClass()

    def _normalize_endpoint_name(self, endpoint_name: str) -> str:
        """Normalize endpoint name by removing special characters and converting to camel case.

        Args:
            endpoint_name (str): The name of the endpoint.

        Returns:
            str: The normalized endpoint name in camel case.
        """
        # Replace hyphens and underscores with spaces
        name = endpoint_name.replace("-", " ").replace("_", " ")
        # Convert to camel case
        return "".join(word.capitalize() for word in name.split())

    def _wrap_run_method(self, run_method: Callable) -> Callable:
        """Wrap the run method to convert the request model to a dictionary.

        Args:
            run_method: The run method to wrap.

        Returns:
            Callable: The wrapped run method.
        """

        @wraps(run_method)
        def wrapped_run_method(self, **kwargs):
            return run_method(**kwargs)

        return wrapped_run_method
