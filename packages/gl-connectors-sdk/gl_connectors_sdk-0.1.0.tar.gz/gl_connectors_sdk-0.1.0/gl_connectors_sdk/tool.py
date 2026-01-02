"""Tool Generator Module.

This module generates gllm-agent tools based on OpenAPI schemas.

Authors:
    Fahmi Armand (fahmi.a.r.harahap@gdplabs.id)
"""

from typing import Dict, List, Literal, overload

import requests
from gllm_core.schema.tool import Tool
from langchain_core.tools import BaseTool
from requests import HTTPError
from typing_extensions import deprecated

from .helpers.tool_builder import BaseToolBuilder, GllmToolBuilder, LangchainToolBuilder


class GLConnectorToolError(Exception):
    """Base exception for GL Connectors SDK errors."""


@deprecated("Use 'GLConnectorToolError' instead; will be removed in a future version")
class BosaConnectorToolError(GLConnectorToolError):
    """Deprecated: Use GLConnectorToolError instead."""

    pass


class GLConnectorToolGenerator:
    """Tool Generator for GL Connectors SDK.

    This class generates tools based on OpenAPI schemas for various services.

    Attributes:
        api_base_url (str): The base URL for the API.
        api_key (str): The API key for authentication.
        info_path (str): The path to the API information endpoint.
        DEFAULT_TIMEOUT (int): Default timeout for API requests.
        app_name (str): The name of the application.

    Methods:
        generate_tools(): Generates tools for the specified services.
    """

    api_base_url: str
    api_key: str
    INFO_PATH: str = "connectors"
    DEFAULT_TIMEOUT: int = 30
    app_name: str

    EXCLUDED_ENDPOINTS = [
        "integrations",
        "integration-exists",
        "success-authorize-callback",
    ]

    TOOL_BUILDER_MAP: Dict[str, BaseToolBuilder] = {
        "langchain": LangchainToolBuilder(),
        "gllm": GllmToolBuilder(),
    }

    def __init__(self, api_base_url: str, api_key: str, app_name: str):
        """Initialize the tool generator with API base URL, info path, and app name.

        Args:
            api_base_url (str): The base URL for the API.
            api_key (str): The API key for authentication.
            app_name (str): The name of the application.
        """
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.app_name = app_name

    @overload
    def generate_tools(self) -> List[BaseTool]: ...

    @overload
    def generate_tools(self, tool_type: Literal["langchain"]) -> List[BaseTool]: ...

    @overload
    def generate_tools(self, tool_type: Literal["gllm"]) -> List[Tool]: ...

    def generate_tools(self, tool_type: Literal["gllm", "langchain"] = "langchain"):
        """Generate tools based on the Connector OpenAPI schemas.

        Args:
            tool_type: The type of tools to generate ("gllm" or "langchain").

        Returns:
            List of tools
        """
        response = requests.get(
            f"{self.api_base_url}/{self.INFO_PATH}/?modules={self.app_name}",
            timeout=self.DEFAULT_TIMEOUT,
        )

        if 500 < response.status_code < 600:  # noqa PLR2004
            raise HTTPError(f"Failed to fetch connector info: {response.status_code}")

        if self.app_name not in response.json():
            raise GLConnectorToolError(f"No connector found for app '{self.app_name}'")

        schemas = response.json()[self.app_name]
        schemas = {
            endpoint: schema_info
            for endpoint, schema_info in schemas.items()
            if "method" in schema_info
            and schema_info["method"] == "POST"
            and not any(endpoint.startswith(excluded) for excluded in self.EXCLUDED_ENDPOINTS)
        }

        tool_classes = {}

        tool_builder = self.TOOL_BUILDER_MAP.get(tool_type)
        if tool_builder is None:
            raise ValueError(f"Invalid tool type: {tool_type}")

        for endpoint_name, endpoint_schema in schemas.items():
            tool_class = tool_builder.create_tool(
                self.app_name,
                endpoint_name,
                endpoint_schema,
                self.api_base_url,
                self.api_key,
                self.app_name,
                self.DEFAULT_TIMEOUT,
            )
            tool_classes[f"{self.app_name}_{endpoint_name}"] = tool_class

        tool_instances = list(tool_classes.values())

        return tool_instances


@deprecated("Use 'GLConnectorToolGenerator' instead; will be removed in a future version")
class BOSAConnectorToolGenerator(GLConnectorToolGenerator):
    """Deprecated: Use GLConnectorToolGenerator instead."""

    pass
