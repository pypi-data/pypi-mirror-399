"""GL Connectors SDK Module."""

from gl_connectors_sdk.helpers.authenticator import BosaAuthenticator, GLAuthenticator
from gl_connectors_sdk.helpers.integrations import BosaIntegrationHelper, GLIntegrationHelper
from gl_connectors_sdk.models.token import BosaToken, GLToken
from gl_connectors_sdk.models.user import BosaUser, GLUser

from .connector import BosaConnector, GLConnectors
from .module import BosaConnectorError, BosaConnectorModule, GLConnectorError, GLConnectorModule
from .tool import BOSAConnectorToolGenerator, GLConnectorToolGenerator

__all__ = [
    # New names (preferred)
    "GLAuthenticator",
    "GLConnectors",
    "GLConnectorError",
    "GLConnectorModule",
    "GLConnectorToolGenerator",
    "GLIntegrationHelper",
    "GLToken",
    "GLUser",
    # Deprecated aliases (backwards compatibility)
    "BosaAuthenticator",
    "BosaConnector",
    "BosaConnectorError",
    "BosaConnectorModule",
    "BosaIntegrationHelper",
    "BosaToken",
    "BosaUser",
    "BOSAConnectorToolGenerator",
]
