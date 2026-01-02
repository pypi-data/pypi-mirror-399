"""Interfaces and protocols for GL Connector SDKs.

This module defines all protocols/interfaces used across the GL Connector SDKs
to provide clear contracts.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import BaseModel
from typing_extensions import deprecated

from gl_connectors_sdk.models.file import ConnectorFile


class ActionResponseData(BaseModel):
    """Response data model with data and meta information."""

    data: Union[List[Any], Dict[str, Any], ConnectorFile]
    meta: Optional[Dict[str, Any]] = None


class InitialExecutorRequest(BaseModel):
    """Initial executor request model."""

    params: Dict[str, Any] = {}
    headers: Optional[Dict[str, str]] = None
    max_attempts: Optional[int] = None
    token: Optional[str] = None
    account: Annotated[Optional[str], deprecated("Use 'identifier' instead; will be removed")] = None
    identifier: Optional[str] = None
    timeout: Optional[int] = None
