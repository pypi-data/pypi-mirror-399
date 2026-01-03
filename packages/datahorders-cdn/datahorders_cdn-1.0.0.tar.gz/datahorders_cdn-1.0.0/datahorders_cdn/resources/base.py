"""Base resource class for API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datahorders_cdn.client import DataHordersCDN


class BaseResource:
    """Base class for all API resources.

    Provides common functionality for making API requests.
    """

    def __init__(self, client: DataHordersCDN) -> None:
        """Initialize the resource.

        Args:
            client: The DataHorders CDN client instance.
        """
        self._client = client

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response data.
        """
        return self._client._request("GET", path, params=params)

    async def _get_async(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._request_async("GET", path, params=params)

    def _post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a POST request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return self._client._request("POST", path, json=data, params=params)

    async def _post_async(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async POST request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._request_async("POST", path, json=data, params=params)

    def _put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a PUT request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return self._client._request("PUT", path, json=data, params=params)

    async def _put_async(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async PUT request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._request_async("PUT", path, json=data, params=params)

    def _patch(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a PATCH request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return self._client._request("PATCH", path, json=data, params=params)

    async def _patch_async(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async PATCH request.

        Args:
            path: API endpoint path.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._request_async(
            "PATCH", path, json=data, params=params
        )

    def _delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a DELETE request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response data.
        """
        return self._client._request("DELETE", path, params=params)

    async def _delete_async(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async DELETE request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._request_async("DELETE", path, params=params)

    def _get_raw(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make a GET request and return raw bytes.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Raw response bytes.
        """
        return self._client._request_raw("GET", path, params=params)

    async def _get_raw_async(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make an async GET request and return raw bytes.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Raw response bytes.
        """
        return await self._client._request_raw_async("GET", path, params=params)
