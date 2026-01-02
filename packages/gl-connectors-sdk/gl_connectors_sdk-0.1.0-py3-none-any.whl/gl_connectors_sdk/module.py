"""GL Connectors SDK module.

Serves as the main connector to GL Connectors Applications. Activates by
populating the schema for a certain module. Module can be fetched through
the base URL of GL Connectors, which *must* contain the module and all possible
actions.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

import logging
import random
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Type, Union

import requests
from pydantic import BaseModel, ValidationError, create_model
from requests import HTTPError
from typing_extensions import deprecated

# TODO: use own header parser instead of cgi
try:
    import cgi  # noqa: F401
except ImportError:  # pragma: no cover
    # For Python 3.13+, use legacy-cgi package
    try:
        from legacy_cgi import cgi  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "The 'cgi' module has been removed in Python 3.13. "
            "Please install the 'legacy-cgi' package: pip install legacy-cgi"
        ) from e

from gl_connectors_sdk.auth import BaseAuthenticator
from gl_connectors_sdk.constant import DEFAULT_API_URL
from gl_connectors_sdk.models.file import ConnectorFile


class GLConnectorError(Exception):
    """Base exception for GL Connectors SDK errors."""


@deprecated("Use 'GLConnectorError' instead; will be removed in a future version")
class BosaConnectorError(GLConnectorError):
    """Deprecated: Use GLConnectorError instead."""

    pass


class GLConnectorModule:
    """Base class for all GL Connectors SDK modules."""

    app_name: str
    _actions: List[str] = []
    DEFAULT_TIMEOUT = 30
    MAX_RETRY = 10
    MAX_BACKOFF_SECONDS = 64
    INFO_PATH = "connectors"
    LIST_NAME_PATH = "connectors/names"

    EXCLUDED_ENDPOINTS = [
        "integrations",
        "integration-exists",
        "success-authorize-callback",
    ]

    @staticmethod
    def is_retryable_error(status_code: int) -> bool:
        """Check if the status code indicates a retryable error (429 or 5xx).

        Args:
            status_code: HTTP status code to check

        Returns:
            bool: True if the error is retryable
        """
        return status_code == requests.codes.too_many_requests or (500 <= status_code < 600)  # noqa PLR2004

    def __init__(
        self,
        app_name: str,
        api_base_url: str = DEFAULT_API_URL,
        info_path: str = INFO_PATH,
    ):
        """Initialize a new connector module.

        This constructor should only be called by GLConnectors.
        """
        self.app_name = app_name
        self.api_base_url = api_base_url
        self.info_path = info_path
        self._schema_cache: Dict[str, BaseModel] = {}
        self._docstrings: Dict[str, str] = {}
        self._request_url_cache: Dict[str, str] = {}
        self._init_schemas()

    def _init_schemas(self):
        """Initialize request/response schemas from the API."""
        response = requests.get(
            f"{self.api_base_url}/{self.info_path}/?modules={self.app_name}",
            timeout=self.DEFAULT_TIMEOUT,
        )

        if 500 < response.status_code < 600:  # noqa PLR2004
            raise HTTPError(f"Failed to fetch connector info: {response.status_code}")

        if self.app_name not in response.json():
            raise GLConnectorError(f"No connector found for app '{self.app_name}'")

        schemas = response.json()[self.app_name]
        schemas = {
            endpoint: schema_info
            for endpoint, schema_info in schemas.items()
            if "method" in schema_info
            and schema_info["method"] == "POST"
            and not any(endpoint.startswith(excluded) for excluded in self.EXCLUDED_ENDPOINTS)
        }
        # Store available actions
        self._actions = list(schemas.keys())
        self._docstrings = {action: schema_info["docstring"] for action, schema_info in schemas.items()}

        for endpoint, schema_info in schemas.items():
            fields = {}
            if schema_info["parameters"].get("request"):
                request_schema = schema_info["parameters"]["request"]["schema"]

                # All parameters are in request body
                for prop_name, prop_info in request_schema["properties"].items():
                    try:
                        base_type, is_optional = self._get_type_info(prop_info)
                        field_type = Optional[base_type] if is_optional else base_type
                        fields[prop_name] = (field_type, None if is_optional else ...)
                    except ValueError as e:
                        # Skip fields we can't parse
                        logging.warning(f"Skipping field {prop_name} due to error: {e}")
                        continue

            self._schema_cache[endpoint] = create_model(f"Request{endpoint.replace('/', '_')}", **fields)

            request_url = schema_info["path"]
            self._request_url_cache[endpoint] = request_url

    def _get_type_info(self, prop_info):  # noqa: PLR0912
        """Extract type information from a property info dictionary.

        Args:
            prop_info: Property info dictionary from the schema

        Returns:
            Tuple of (base_type, is_optional)
        """
        if "type" in prop_info:
            if prop_info["type"] == "object" and "properties" in prop_info:
                # Create a nested model for objects
                fields = {}
                for name, field_info in prop_info["properties"].items():
                    base_type, is_optional = self._get_type_info(field_info)
                    fields[name] = (
                        Optional[base_type] if is_optional else base_type,
                        None if is_optional else ...,
                    )
                model_name = f"Nested_{next(iter(prop_info['properties']))}"  # Use first property name
                nested_model = create_model(model_name, **fields)
                return nested_model, False
            elif prop_info["type"] == "array" and "items" in prop_info:
                # Handle array types with proper item validation
                item_type, _ = self._get_type_info(prop_info["items"])
                return List[item_type], False
            else:
                format_type = prop_info.get("format")
                return self._get_python_type(prop_info["type"], format_type), False
        elif "anyOf" in prop_info:
            base_type = None
            is_optional = False
            types = []
            for type_info in prop_info["anyOf"]:
                if type_info["type"] == "null":
                    is_optional = True
                elif "items" in type_info:
                    item_format = type_info["items"].get("format")
                    item_type = self._get_python_type(type_info["items"]["type"], item_format)
                    types.append(List[item_type])
                else:
                    format_type = type_info.get("format")
                    types.append(self._get_python_type(type_info["type"], format_type))

            # If we have multiple types, use Union
            if len(types) > 1:
                base_type = Union[tuple(types)]
            elif len(types) == 1:
                base_type = types[0]
            return base_type, is_optional
        elif "schema" in prop_info:
            # Handle case where type info is nested in schema
            return self._get_type_info(prop_info["schema"])
        else:
            raise ValueError(f"Unable to determine type for property: {prop_info}")

    def _get_python_type(self, schema_type: str, format_type: str = None) -> Type:
        """Convert schema types to Python types.

        Args:
            schema_type: The schema type (e.g., 'string', 'integer')
            format_type: Optional format specifier (e.g., 'binary' for strings)

        Returns:
            The corresponding Python type
        """
        # Handle special formats
        if schema_type == "string" and format_type == "binary":
            return bytes

        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        return type_map.get(schema_type, str)

    def get_actions(self) -> List[Tuple[str, str, str]]:
        """Return list of available actions for this module."""
        return [(action, self._request_url_cache[action], self._docstrings[action]) for action in self._actions.copy()]

    def get_action_parameters(self, action: str):
        """Get flattened parameter information for an action.

        Args:
            action: The action endpoint

        Returns:
            List of parameter info dicts with name, type, and required fields.
            Nested objects are flattened using dot notation, e.g.:
                object.attr1, object.attr2, object.attr3.attr21
        """
        schema = self._schema_cache.get(action)
        if not schema:
            return []

        parameters = []
        self._flatten_schema(schema.model_fields, "", parameters)
        return parameters

    def _flatten_schema(self, fields: Dict, prefix: str, parameters: List[Dict]):
        """Recursively flatten a schema's fields into a list of parameters.

        Args:
            fields: Dictionary of field definitions
            prefix: Current prefix for nested fields (e.g. "parent.child.")
            parameters: List to append flattened parameters to
        """
        for field_name, field in fields.items():
            full_name = f"{prefix}{field_name}" if prefix else field_name

            # Handle nested Pydantic models
            if hasattr(field.annotation, "model_fields"):
                # Add the nested field itself
                parameters.append(
                    {
                        "name": full_name,
                        "type": str(field.annotation),
                        "required": field.is_required(),
                    }
                )
                # Then add its nested fields
                self._flatten_schema(field.annotation.model_fields, f"{full_name}.", parameters)
            else:
                parameters.append(
                    {
                        "name": full_name,
                        "type": str(field.annotation),
                        "required": field.is_required(),
                    }
                )

    def validate_request(self, action: str, params: Dict[str, Any]) -> tuple[Dict[str, Any] | None, Dict[str, str]]:
        """Validate and clean request parameters.

        Args:
            action: The action endpoint
            params: Dict of parameter values

        Returns:
            Tuple of (cleaned_params, error_details) where error_details is empty if validation passed
        """
        schema = self._schema_cache.get(action)
        if not schema:
            return None, {"_schema": "No schema found for action"}
        # Clean parameters - remove empty optional fields
        cleaned = {
            k: v.strip() if isinstance(v, str) else v
            for k, v in params.items()
            if v != ""  # Skip empty values, schema validation will catch required fields
        }
        try:
            validated = schema(**cleaned)
            filtered = validated.model_dump(exclude_none=True)
            return filtered, {}
        except ValidationError as e:
            errors = {error["loc"][0]: error["msg"] for error in e.errors()}
            return None, errors

    def execute(  # noqa: PLR0912, PLR0913, D417
        self,
        action: str,
        max_attempts: int,
        input_: Dict = None,
        token: Optional[str] = None,
        account: Annotated[Optional[str], deprecated("Use 'identifier' instead; will be removed")] = None,
        identifier: Optional[str] = None,
        authenticator: Optional[BaseAuthenticator] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
    ) -> tuple[Union[Dict[str, Any], ConnectorFile], int]:
        """Execute an action with validated parameters and return typed response.

        Args:
            action: The action to execute
            max_attempts: Maximum number of attempts for failed requests (429 or 5xx errors). Must be at least 1.
                  Will be capped at MAX_RETRY (10) to prevent excessive retries.
            input_: Optional dictionary of parameters
            token: Optional User Token. If not provided, will use the default token
            account: Optional user account to use for the request (deprecated, remove this in the future)
            identifier: Optional user identifier to use for the request
            authenticator: Optional authenticator to use for the request
            headers: Optional headers to include in the request

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(action, params_dict)
        2. As keyword arguments: execute(action, param1=value1, param2=value2)

        Raises:
            ValueError: If action is invalid, parameters are invalid, or max_attempts is less than 1
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if action not in self._actions:
            raise ValueError(f"Invalid action '{action}'. Available actions: {', '.join(self._actions)}")

        params_dict = input_ or {}
        params, file_post = self._parse_param_from_files(params_dict)
        validated_params, errors = self.validate_request(action, params)
        if errors:
            raise ValueError("Invalid parameters: " + str(errors))

        path = self._request_url_cache.get(action)
        url = f"{self.api_base_url}{path}"

        headers = headers or {}
        if authenticator:
            headers.update(authenticator.authenticate())

        if token:
            headers.update({"Authorization": f"Bearer {token}"})

        if identifier:
            headers.update({"X-Bosa-Integration": identifier})
        elif account:  # account is deprecated, remove this in the future
            headers.update({"X-Bosa-Integration": account})

        attempt = 0
        retry = min(max_attempts - 1, self.MAX_RETRY)
        is_form_data = self._check_form_data_request(action)

        while True:
            try:
                logging.info(f"Running execute for {url} attempt number: {attempt}")
                response = self._request(url, validated_params, file_post, is_form_data, headers, timeout)

                # If status code is not retryable or we're out of retries, return the response
                if not self.is_retryable_error(response.status_code) or attempt >= retry:
                    return self._get_response_return(response)

                # Calculate backoff time with exponential increase and random jitter
                backoff = min(pow(2, attempt), self.MAX_BACKOFF_SECONDS) + (random.random())
                time.sleep(backoff)
                attempt += 1
            except requests.RequestException:
                # For connection errors, apply the same retry logic
                if attempt >= retry:
                    raise
                backoff = min(pow(2, attempt), self.MAX_BACKOFF_SECONDS) + (random.random())
                time.sleep(backoff)
                attempt += 1

    def _request(  # noqa PLR0913
        self,
        url: str,
        params: Dict[str, Any],
        files: Dict[str, ConnectorFile],
        is_form_data: bool,
        headers: Dict,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """Make a POST request to the API with parameters and files.

        Args:
            url: The URL to send the request to
            params: Dictionary of request data
            files: Dictionary of files to include in the request
            is_form_data: Whether to send the request as form data
            headers: Dictionary of headers to include in the request
            timeout: Optional timeout for the request

        Returns:
            Response object from the requests library
        """
        if len(files) > 0:
            data, post_files = self._prepare_form_data_request_parameters(params, files)
            return requests.post(url, data=data, files=post_files, headers=headers, timeout=timeout)
        elif is_form_data:
            return requests.post(url, data=params, headers=headers, timeout=timeout)
        else:
            return requests.post(url, json=params, headers=headers, timeout=timeout)

    def _get_response_return(self, response: requests.Response) -> tuple[Union[Dict[str, Any], ConnectorFile], int]:
        """Process the response from the API."""
        content_type = response.headers.get("content-type", None)

        if "application/json" in content_type:
            return response.json(), response.status_code

        content_disposition = response.headers.get("Content-Disposition", "")
        _, params = cgi.parse_header(content_disposition)

        return (
            ConnectorFile(
                file=response.content,
                filename=params.get("filename"),
                content_type=content_type,
                headers=response.headers,
            ),
            response.status_code,
        )

    def _check_form_data_request(self, action: str) -> bool:
        """Check if the request should be sent as form data.

        Args:
            action: The action to check

        Returns:
            bool: True if the request should be sent as form data, False otherwise
        """
        schema = self._schema_cache.get(action)
        if not schema:
            return False

        # Check if any of the parameters are ConnectorFile instances
        for field in schema.model_fields.values():
            if (
                field.annotation == Optional[bytes]
                or field.annotation is bytes
                or field.annotation is List[bytes]
                or field.annotation is Optional[List[bytes]]
            ):
                return True
        return False

    def _parse_param_from_files(self, params_dict: Dict) -> tuple[Dict[str, Any], Dict[str, ConnectorFile]]:
        """Parse parameters from a dictionary, separating files from other parameters.

        Can only detect `ConnectorFile` on the first level of the dictionary.

        Args:
            params_dict: Dictionary of parameters

        Returns:
            Tuple of (params, file_post) where params is the cleaned parameters and file_post is the file parameters
        """
        params = {}
        file_post = {}
        for key, value in params_dict.items():
            if isinstance(value, list) and len(value) > 0 and all(isinstance(item, ConnectorFile) for item in value):
                file_post[key] = value
                params[key] = [v.file for v in value]
            elif isinstance(value, ConnectorFile):
                file_post[key] = value
                params[key] = value.file
            else:
                params[key] = value
        return params, file_post

    def _prepare_form_data_request_parameters(
        self, params: Dict[str, Any], files: Dict[str, ConnectorFile]
    ) -> tuple[Dict[str, Any], Dict[str, Tuple]]:
        """Prepare parameters for the request by handling files and regular parameters.

        Args:
            params: Dictionary of validated parameters
            files: Dictionary of file parameters

        Returns:
            Tuple of (params, files)
        """
        prepared_files = self._prepare_file_parameters(files)
        params_without_files = self._remove_file_keys_from_params(params, files.keys())
        return params_without_files, prepared_files

    def _prepare_file_parameters(self, files: Dict[str, Union[ConnectorFile, List[ConnectorFile]]]) -> List[Tuple]:
        """Transform file parameters to the format required by requests.post()."""
        result: List[Tuple] = []
        for key, file in files.items():
            if isinstance(file, list):
                result.extend(
                    [
                        (
                            key,
                            self._map_connector_file_to_request_file_tuple(file_item),
                        )
                        for file_item in file
                    ]
                )
            else:
                result.append((key, self._map_connector_file_to_request_file_tuple(file)))
        return result

    def _remove_file_keys_from_params(self, params: Dict[str, Any], file_keys: list[str]) -> Dict:
        """Remove file keys from the parameters dictionary."""
        result = params.copy()
        for key in file_keys:
            result.pop(key, None)
        return result

    def _map_connector_file_to_request_file_tuple(self, file: ConnectorFile) -> tuple:
        """Map a ConnectorFile object to a request file tuple.

        Args:
            file: ConnectorFile object

        Returns:
            Tuple in format (filename, file content, content_type, headers) for requests.post()
        """
        return (file.filename, file.file, file.content_type, file.headers)


@deprecated("Use 'GLConnectorModule' instead; will be removed in a future version")
class BosaConnectorModule(GLConnectorModule):
    """Deprecated: Use GLConnectorModule instead."""

    pass
