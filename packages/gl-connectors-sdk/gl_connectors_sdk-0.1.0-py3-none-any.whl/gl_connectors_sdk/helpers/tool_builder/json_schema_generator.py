"""JSON Schema Generator.

This module generates JSON schemas for LLM tools.

Authors:
    Fahmi Armand (fahmi.a.r.harahap@gdplabs.id)
    Hans Sean Nathanael (hans.s.nathanael@gdplabs.id)
"""

from typing import Any, Dict

from gl_connectors_sdk.constant import DEFAULT_SERVICE_PREFIX


def create_input_json_schema(
    endpoint_name: str,
    schema: dict,
    default_timeout: int,
    service_prefix: str = DEFAULT_SERVICE_PREFIX,
) -> Dict[str, Any]:
    """Create a Pydantic model for the request schema.

    Args:
        endpoint_name (str): The name of the endpoint.
        schema (dict): The schema definition for the endpoint.
        default_timeout (int): Default timeout in seconds
        service_prefix (str, optional): The prefix for the service. Defaults to DEFAULT_SERVICE_PREFIX.

    Returns:
        Type[BaseModel]: The generated Pydantic model.
    """
    normalized_endpoint = _normalize_name(endpoint_name)
    model_name = f"{service_prefix}{_camel_case(normalized_endpoint)}Request"

    request_schema = schema.get("request_body", {})
    defs = request_schema.pop("$defs", {})
    properties = {
        "token": {
            "type": "string",
            "title": "Token",
            "description": "The authentication token.",
        },
        "identifier": {
            "anyOf": [
                {
                    "type": "string",
                },
                {
                    "type": "null",
                },
            ],
            "default": None,
            "title": "Identifier",
            "description": "The identifier.",
        },
        "timeout": {
            "type": "integer",
            "default": default_timeout,
            "title": "Timeout",
            "description": "The GL Connector SDK timeout in seconds.",
        },
    }
    required = ["token", "identifier", "timeout"]

    if request_schema:
        schema_title = request_schema["title"]
        defs[schema_title] = request_schema

        properties["request"] = {
            "$ref": f"#/$defs/{schema_title}",
        }
        required.append("request")

    result = {
        "title": model_name,
        "properties": properties,
        "required": required,
        "type": "object",
    }
    if defs:
        result["$defs"] = defs

    return result


def _normalize_name(name: str) -> str:
    """Normalize a name by replacing hyphens with underscores.

    Args:
        name (str): The name to normalize.

    Returns:
        str: The normalized name.
    """
    return name.replace("-", "_")


def _camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase.

    Args:
        snake_str (str): The snake_case string to convert.

    Returns:
        str: The converted CamelCase string.
    """
    if not snake_str:
        return ""

    # Replace hyphens with underscores, split, and handle each non-empty component
    # Preserve existing uppercase letters (already camelCase) but ensure first letter is uppercase
    return "".join(
        component[0].upper() + component[1:] if any(c.isupper() for c in component) else component.capitalize()
        for component in snake_str.replace("-", "_").split("_")
        if component
    )
