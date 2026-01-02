"""Models for GL Connectors User.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from uuid import UUID

from pydantic import BaseModel
from typing_extensions import deprecated


class ThirdPartyIntegrationAuthBasic(BaseModel):
    """Basic model for a third party integration authentication."""

    id: UUID
    client_id: UUID
    user_id: UUID
    connector: str
    user_identifier: str
    selected: bool


class GLUser(BaseModel):
    """Model for a GL Connectors User."""

    id: UUID
    client_id: UUID
    identifier: str
    secret_preview: str
    is_active: bool
    integrations: list[ThirdPartyIntegrationAuthBasic]


@deprecated("Use 'GLUser' instead; will be removed in a future version")
class BosaUser(GLUser):
    """Deprecated: Use GLUser instead."""

    pass


class CreateUserResponse(BaseModel):
    """Model for a GL Connectors User creation response."""

    id: UUID
    identifier: str
    secret: str
    secret_preview: str
    is_active: bool
