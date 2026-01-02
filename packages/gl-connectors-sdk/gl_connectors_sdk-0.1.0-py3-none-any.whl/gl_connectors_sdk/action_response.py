"""Response wrapper for action execution results."""

from typing import Any, Callable, Dict, List, Optional, Union

from gl_connectors_sdk.models.action import ActionResponseData, InitialExecutorRequest
from gl_connectors_sdk.models.file import ConnectorFile


class ActionResponse:
    """Represents the response from an action execution.

    Currently supports 2 pagination modes:
    1. Page-based pagination: Using page numbers (page=1, page=2, etc.)
    2. Cursor-based pagination: Using cursor tokens for forwards and backwards navigation

    The class automatically detects which pagination mode to use based on the response metadata:
    - If "forwards_cursor" and "backwards_cursor" are present, cursor-based pagination is used
    - Otherwise, it falls back to page-based pagination using "page" parameter

    Common pagination attributes:
    - total: Total number of items
    - total_page: Total number of pages
    - has_next: Whether there is a next page
    - has_prev: Whether there is a previous page

    Followed by optional attributes
    Cursor-based pagination attributes:
    - forwards_cursor: Cursor for next page
    - backwards_cursor: Cursor for previous page

    Page-based pagination attributes:
    - page: Current page number
    - limit: Number of items per page

    If the response is ConnectorFile, it will not support pagination and will return the file directly.
    """

    def __init__(
        self,
        response_data: Optional[Union[Dict[str, Any], ConnectorFile]],
        status: int,
        response_creator: Callable[..., "ActionResponse"],
        initial_executor_request: Dict[str, Any],
    ):
        """Initialize response wrapper.

        Args:
            response_data: Response data which could be:
                 - List response: {"data": [...], "meta": {...}}
                 - Single item response: {"data": {...}, "meta": {...}}
            status: HTTP status code
            response_creator: Callable to create a new ActionResponse
            initial_executor_request: Initial action request attributes as dict
        """
        if response_data is None:
            response_data = {}
        if isinstance(response_data, ConnectorFile):
            response_data = {"data": response_data}

        self._response_data = ActionResponseData(
            data=response_data.get("data", response_data),
            meta=response_data.get("meta", {}),
        )
        self._status = status
        self._initial_executor_request = InitialExecutorRequest(
            headers=initial_executor_request.get("headers", {}),
            params=initial_executor_request.get("params", {}),
            max_attempts=initial_executor_request.get("max_attempts"),
            token=initial_executor_request.get("token"),
            account=initial_executor_request.get(
                "account"
            ),  # account is deprecated, remove this in the future
            identifier=initial_executor_request.get("identifier"),
            timeout=initial_executor_request.get("timeout"),
        )

        self._response_creator = response_creator

    def get_data(self) -> Union[List[Dict[str, Any]], Dict[str, Any], ConnectorFile]:
        """Get the current page data.

        Returns:
            List of objects for paginated responses, or
            Single object for single item responses
        """
        return getattr(self._response_data, "data", {})

    def get_meta(self) -> Dict[str, Any]:
        """Get the meta data."""
        meta = getattr(self._response_data, "meta", {})

        if meta is None:
            return {}

        return meta

    def get_status(self) -> int:
        """Get the HTTP status code."""
        return self._status

    def is_list(self) -> bool:
        """Check if the response data is a list."""
        return isinstance(self.get_data(), list)

    def has_next(self) -> bool:
        """Check if there is a next page.

        Returns False if this is a single item response.
        """
        if not self.is_list():
            return False

        meta = self.get_meta()
        return meta.get("has_next")

    def has_prev(self) -> bool:
        """Check if there is a previous page.

        Returns False if this is a single item response.
        """
        if not self.is_list():
            return False

        meta = self.get_meta()
        return meta.get("has_prev")

    def next_page(self) -> "ActionResponse":
        """Move to the next page and get the response.

        Supports both page-based and cursor-based navigation:
        1. If forwards_cursor is available, uses cursor-based navigation
        2. Otherwise, falls back to page-based navigation

        Returns self if this is a single item response or there is no next page.
        """
        if not self.has_next():
            return self

        meta = self.get_meta()

        updated_params = dict(self._initial_executor_request.params)

        # Handle cursor-based pagination if available
        if meta.get("forwards_cursor"):
            updated_params["cursor"] = meta["forwards_cursor"]
        # Fall back to page-based pagination
        elif meta.get("page"):
            current_page = meta.get("page", 1)
            updated_params["page"] = current_page + 1

        new_response = self._response_creator(
            headers=self._initial_executor_request.headers,
            params=updated_params,
            max_attempts=self._initial_executor_request.max_attempts,
            token=self._initial_executor_request.token,
            account=self._initial_executor_request.account,  # account is deprecated, remove this in the future
            identifier=self._initial_executor_request.identifier,
            timeout=self._initial_executor_request.timeout,
        )

        return new_response

    def prev_page(self) -> "ActionResponse":
        """Move to the previous page and get the response.

        Supports both page-based and cursor-based navigation:
        1. If backwards_cursor is available, uses cursor-based navigation
        2. Otherwise, falls back to page-based navigation

        Returns self if this is a single item data or there is no previous page.
        """
        if not self.has_prev():
            return self

        meta = self.get_meta()

        updated_params = dict(self._initial_executor_request.params)

        # Handle cursor-based pagination if available
        if meta.get("backwards_cursor"):
            updated_params["cursor"] = meta["backwards_cursor"]
        # Fall back to page-based pagination
        elif meta.get("page"):
            current_page = meta.get("page", 1)
            updated_params["page"] = current_page - 1

        new_response = self._response_creator(
            headers=self._initial_executor_request.headers,
            params=updated_params,
            max_attempts=self._initial_executor_request.max_attempts,
            token=self._initial_executor_request.token,
            account=self._initial_executor_request.account,  # account is deprecated, remove this in the future
            identifier=self._initial_executor_request.identifier,
            timeout=self._initial_executor_request.timeout,
        )

        return new_response

    def get_all_items(self) -> List[Any]:
        """Get all items from all pages."""
        current_data = self.get_data()
        current_meta = self.get_meta()

        # If single item, return as list
        if not self.is_list():
            return [{"data": current_data, "meta": current_meta}]

        items = []
        response = self

        while True:
            items.append({"data": response.get_data(), "meta": response.get_meta()})

            # Check if there are more pages
            if not response.has_next():
                break

            # Move to next page
            response = response.next_page()

        return items
