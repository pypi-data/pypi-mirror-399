"""Models for GL Connector SDKs.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from pydantic import BaseModel


class ActionResult(BaseModel):
    """Model for an action result."""

    success: bool
    message: str
