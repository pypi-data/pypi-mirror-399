"""Models for GL Connector SDK File Request and Response."""

from typing import Dict, Optional

from pydantic import BaseModel


class ConnectorFile(BaseModel):
    """Model for a file in a GL Connector SDK request or response."""

    file: bytes
    filename: Optional[str] = None
    content_type: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
