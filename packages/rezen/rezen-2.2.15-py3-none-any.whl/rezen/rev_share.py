"""Revenue share (revshare) client for the ReZEN Arrakis API."""

from datetime import date
from typing import Any, Dict, Optional

from .base_client import BaseClient


class RevShareClient(BaseClient):
    """Client for revenue share (revshare) endpoints."""

    def _get_text(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Perform a GET request and return the raw text response.

        This is used for endpoints that return CSV/text payloads instead of JSON.

        Args:
            endpoint: API endpoint path (relative to base_url).
            params: Optional query parameters.

        Returns:
            Response text body.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout_seconds)

        if response.status_code in (200, 201):
            return response.text

        # Delegate error handling to the shared response handler (raises on error).
        self._handle_response(response)
        return ""

    def get_payments_for_agent(
        self,
        yenta_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get all revshare payments for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            page_number: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            Revshare payments response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        endpoint = f"revshares/{yenta_id}/payments"
        return self.get(endpoint, params=params if params else None)

    def get_payment_by_id(
        self,
        yenta_id: str,
        outgoing_payment_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get details for a particular revshare payment.

        Args:
            yenta_id: Agent Yenta ID.
            outgoing_payment_id: Outgoing payment ID.
            page_number: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            Revshare payment response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        endpoint = f"revshares/{yenta_id}/payments/{outgoing_payment_id}"
        return self.get(endpoint, params=params if params else None)

    def get_payment_export_for_agent(
        self, yenta_id: str, outgoing_payment_id: str
    ) -> str:
        """Return a CSV file of all revshare contributions for a payment.

        Args:
            yenta_id: Agent Yenta ID.
            outgoing_payment_id: Outgoing payment ID.

        Returns:
            CSV content as a string.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/{outgoing_payment_id}/export"
        return self._get_text(endpoint)

    def get_pending_payment_for_agent(
        self,
        yenta_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get all pending revshare payments for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            page_number: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            Pending revshare payment response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        endpoint = f"revshares/{yenta_id}/payments/pending"
        return self.get(endpoint, params=params if params else None)

    def get_pending_payment_export_for_agent(self, yenta_id: str) -> str:
        """Return a CSV file for all pending revshare payments for an agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            CSV content as a string.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/pending/export"
        return self._get_text(endpoint)

    def get_pending_payment_preview_for_agent(self, yenta_id: str) -> Dict[str, Any]:
        """Get pending revshare payments overview for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            Pending payment overview payload.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/pending-overview"
        return self.get(endpoint)

    def get_contributors_by_tier(
        self,
        yenta_id: str,
        tier: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_number: int = 0,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Get revshare contributors by tier.

        Args:
            yenta_id: Agent Yenta ID.
            tier: Tier number to fetch contributors for.
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_number: Page number for pagination.
            page_size: Page size for pagination.

        Returns:
            Contributors response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()

        endpoint = f"revshares/{yenta_id}/contributors/{tier}"
        return self.get(endpoint, params=params)

    def get_contributions_by_tier(
        self,
        yenta_id: str,
        tier: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_number: int = 0,
        page_size: int = 20,
        missed: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get agent-wise revshare contributions by tier.

        Args:
            yenta_id: Agent Yenta ID.
            tier: Tier number to fetch contributions for.
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_number: Page number for pagination.
            page_size: Page size for pagination.
            missed: Optional flag to filter for missed contributions.

        Returns:
            Contributions-by-tier response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        if missed is not None:
            params["missed"] = missed

        endpoint = f"revshares/{yenta_id}/contributions/{tier}"
        return self.get(endpoint, params=params)

    def get_by_tier(
        self,
        yenta_id: str,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get revshare by tier for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.

        Returns:
            Revshare-by-tier response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()

        endpoint = f"revshares/{yenta_id}/by-tier"
        return self.get(endpoint, params=params if params else None)

    def get_history(
        self, agent_yenta_id: str, *, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get an agent's revshare history.

        Args:
            agent_yenta_id: Agent Yenta ID.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).

        Returns:
            Revshare history response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        endpoint = f"revshares/{agent_yenta_id}/history"
        return self.get(endpoint, params=params)

    def get_monthly_performance(
        self, yenta_id: str, month: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get revshare performance for a particular month for an agent.

        Args:
            yenta_id: Agent Yenta ID.
            month: Month selector. If omitted, the API defaults to "current".

        Returns:
            Monthly performance response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if month is not None:
            params["month"] = month

        endpoint = f"revshares/performance/{yenta_id}/revenue-share"
        return self.get(endpoint, params=params if params else None)

    def get_current_performance(self, yenta_id: str) -> Dict[str, Any]:
        """Get the current revshare performance overview for an agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            Current performance overview payload.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/performance/{yenta_id}/revenue-share/current"
        return self.get(endpoint)
