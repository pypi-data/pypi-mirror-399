"""BOSA Connectors - Deprecated alias for gl_connectors_sdk.

.. deprecated::
    This module is deprecated. Use gl_connectors_sdk instead.
    All classes have been renamed:
    - BosaConnector -> GLConnectors
    - BosaAuthenticator -> GLAuthenticator
    - BosaConnectorModule -> GLConnectorModule
    - BosaConnectorError -> GLConnectorError
    - BOSAConnectorToolGenerator -> GLConnectorToolGenerator
    - BosaToken -> GLToken
    - BosaUser -> GLUser
"""

import sys
import warnings

# Emit deprecation warning when this module is imported
warnings.warn(
    "The 'bosa_connectors' package is deprecated. Use 'gl_connectors_sdk' instead. "
    "All Bosa* classes have been renamed to GL* equivalents.",
    DeprecationWarning,
    stacklevel=2,
)

from gl_connectors_sdk import (  # noqa: F401, E402
    BOSAConnectorToolGenerator,
    BosaAuthenticator,
    BosaConnector,
    BosaConnectorError,
    BosaConnectorModule,
    BosaIntegrationHelper,
    BosaToken,
    BosaUser,
)

# Import all submodules from gl_connectors_sdk
import gl_connectors_sdk.action  # noqa: E402
import gl_connectors_sdk.action_response  # noqa: E402
import gl_connectors_sdk.auth  # noqa: E402
import gl_connectors_sdk.connector  # noqa: E402
import gl_connectors_sdk.constant  # noqa: E402
import gl_connectors_sdk.helpers  # noqa: E402
import gl_connectors_sdk.models  # noqa: E402
import gl_connectors_sdk.module  # noqa: E402
import gl_connectors_sdk.tool  # noqa: E402

# Register all modules in sys.modules so they can be imported from bosa_connectors
# This allows: from bosa_connectors.module import BosaConnectorError
# Same as: from gl_connectors_sdk.module import BosaConnectorError
sys.modules["bosa_connectors.action"] = gl_connectors_sdk.action
sys.modules["bosa_connectors.action_response"] = gl_connectors_sdk.action_response
sys.modules["bosa_connectors.auth"] = gl_connectors_sdk.auth
sys.modules["bosa_connectors.auth.api_key"] = gl_connectors_sdk.auth.api_key
sys.modules["bosa_connectors.auth.base"] = gl_connectors_sdk.auth.base
sys.modules["bosa_connectors.connector"] = gl_connectors_sdk.connector
sys.modules["bosa_connectors.constant"] = gl_connectors_sdk.constant
sys.modules["bosa_connectors.helpers"] = gl_connectors_sdk.helpers
sys.modules["bosa_connectors.helpers.authenticator"] = gl_connectors_sdk.helpers.authenticator
sys.modules["bosa_connectors.helpers.integrations"] = gl_connectors_sdk.helpers.integrations
sys.modules["bosa_connectors.helpers.tool_builder"] = gl_connectors_sdk.helpers.tool_builder
sys.modules["bosa_connectors.helpers.tool_builder.base"] = gl_connectors_sdk.helpers.tool_builder.base
sys.modules["bosa_connectors.helpers.tool_builder.gllm"] = gl_connectors_sdk.helpers.tool_builder.gllm
sys.modules["bosa_connectors.helpers.tool_builder.json_schema_generator"] = (
    gl_connectors_sdk.helpers.tool_builder.json_schema_generator
)
sys.modules["bosa_connectors.helpers.tool_builder.langchain"] = gl_connectors_sdk.helpers.tool_builder.langchain
sys.modules["bosa_connectors.models"] = gl_connectors_sdk.models
sys.modules["bosa_connectors.models.action"] = gl_connectors_sdk.models.action
sys.modules["bosa_connectors.models.file"] = gl_connectors_sdk.models.file
sys.modules["bosa_connectors.models.result"] = gl_connectors_sdk.models.result
sys.modules["bosa_connectors.models.token"] = gl_connectors_sdk.models.token
sys.modules["bosa_connectors.models.user"] = gl_connectors_sdk.models.user
sys.modules["bosa_connectors.module"] = gl_connectors_sdk.module
sys.modules["bosa_connectors.tool"] = gl_connectors_sdk.tool

__all__ = [
    "BosaAuthenticator",
    "BosaConnector",
    "BosaConnectorError",
    "BosaConnectorModule",
    "BosaIntegrationHelper",
    "BosaToken",
    "BosaUser",
    "BOSAConnectorToolGenerator",
]
