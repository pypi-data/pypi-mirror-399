"""GLLM tool builder module.

This module contains the GLLM tool builder implementation.

Authors:
    Hans Sean Nathanael (hans.s.nathanael@gdplabs.id)
"""

from gllm_core.schema.tool import Tool

from gl_connectors_sdk.helpers.tool_builder.base import BaseToolBuilder
from gl_connectors_sdk.helpers.tool_builder.json_schema_generator import (
    create_input_json_schema,
)


class GllmToolBuilder(BaseToolBuilder):
    """Tool builder for GLLM tools."""

    def create_tool(  # noqa: PLR0913
        self,
        service_name: str,
        endpoint_name: str,
        schema: dict,
        api_base_url: str,
        api_key: str,
        app_name: str,
        default_timeout: int,
    ) -> Tool:
        """Create a GLLM tool for a given endpoint.

        Args:
            service_name (str): The name of the service.
            endpoint_name (str): The name of the endpoint.
            schema (dict): The schema definition for the endpoint.
            api_base_url (str): The base URL for the API.
            api_key (str): The API key for authentication.
            app_name (str): The name of the application.
            default_timeout (int): Default timeout in seconds for BosaConnector.

        Returns:
            Tool: The generated GLLM Core Tool object.
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

        # Create the _run method with specific parameters
        run_method = self._create_run_method(
            api_base_url, api_key, app_name, endpoint_name
        )

        return Tool(
            name=tool_name,
            title=tool_name,
            input_schema=request_schema,
            description=docstring,
            func=run_method,
            is_async=False,
        )
