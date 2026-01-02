"""Authenticator base class for Connector.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
"""

from abc import ABC, abstractmethod


class BaseAuthenticator(ABC):
    """Base authenticator for Connector."""

    @abstractmethod
    def authenticate(self):
        """Authenticates the request.

        Raises:
            AuthenticationError: If authentication fails.
        """
