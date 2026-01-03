"""Analytics resource for the DataHorders CDN SDK."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from datahorders_cdn.models import CdnNode, UsageMetrics
from datahorders_cdn.resources.base import BaseResource


class AnalyticsResource(BaseResource):
    """Resource for accessing traffic metrics and analytics data."""

    def get_usage(
        self,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> UsageMetrics:
        """Get bandwidth and traffic usage.

        Args:
            start_date: Start date (ISO 8601 format or date object).
            end_date: End date (ISO 8601 format or date object).

        Returns:
            Usage metrics for all domains.

        Note:
            If no date range is provided, returns data for the current
            billing period.
        """
        params: dict[str, Any] = {}
        if start_date:
            if isinstance(start_date, (date, datetime)):
                params["start_date"] = start_date.isoformat()
            else:
                params["start_date"] = start_date
        if end_date:
            if isinstance(end_date, (date, datetime)):
                params["end_date"] = end_date.isoformat()
            else:
                params["end_date"] = end_date

        response = self._get("/usage", params=params if params else None)
        return UsageMetrics.model_validate(response)

    async def get_usage_async(
        self,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> UsageMetrics:
        """Get bandwidth and traffic usage asynchronously.

        Args:
            start_date: Start date.
            end_date: End date.

        Returns:
            Usage metrics for all domains.
        """
        params: dict[str, Any] = {}
        if start_date:
            if isinstance(start_date, (date, datetime)):
                params["start_date"] = start_date.isoformat()
            else:
                params["start_date"] = start_date
        if end_date:
            if isinstance(end_date, (date, datetime)):
                params["end_date"] = end_date.isoformat()
            else:
                params["end_date"] = end_date

        response = await self._get_async("/usage", params=params if params else None)
        return UsageMetrics.model_validate(response)

    def get_cdn_nodes(self) -> list[CdnNode]:
        """Get CDN edge node status.

        Returns:
            List of CDN nodes with their status.
        """
        response = self._get("/cdn-nodes")
        # Response is a list, not wrapped in data
        if isinstance(response, list):
            return [CdnNode.model_validate(n) for n in response]
        return [CdnNode.model_validate(n) for n in response.get("data", response)]

    async def get_cdn_nodes_async(self) -> list[CdnNode]:
        """Get CDN edge node status asynchronously.

        Returns:
            List of CDN nodes with their status.
        """
        response = await self._get_async("/cdn-nodes")
        if isinstance(response, list):
            return [CdnNode.model_validate(n) for n in response]
        return [CdnNode.model_validate(n) for n in response.get("data", response)]
