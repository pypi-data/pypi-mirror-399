"""Models for GL Connectors Token.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from pydantic import BaseModel
from typing_extensions import deprecated


class GLToken(BaseModel):
    """Model for a GL Connectors Token."""

    token: str
    token_type: str
    expires_at: str
    is_revoked: bool
    user_id: str
    client_id: str


@deprecated("Use 'GLToken' instead; will be removed in a future version")
class BosaToken(GLToken):
    """Deprecated: Use GLToken instead."""

    pass
