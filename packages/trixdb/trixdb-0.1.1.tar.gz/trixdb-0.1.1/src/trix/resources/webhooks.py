"""Webhooks resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    Webhook,
    WebhookCreate,
    WebhookDelivery,
    WebhookDeliveryList,
    WebhookEvent,
    WebhookEventTypeInfo,
    WebhookFilter,
    WebhookList,
    WebhookStats,
    WebhookUpdate,
)
from ..utils.security import validate_id, validate_webhook_url


class WebhooksResource:
    """Resource for managing webhooks."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize webhooks resource with client."""
        self._client = client

    def create(
        self,
        name: str,
        url: str,
        events: List[WebhookEvent],
        space_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        filters: Optional[WebhookFilter] = None,
    ) -> Webhook:
        """
        Create a new webhook.

        Args:
            name: Webhook name
            url: Webhook URL endpoint
            events: List of events to subscribe to
            space_id: Optional space filter
            headers: Custom headers to send with webhook
            filters: Event filters

        Returns:
            Created webhook object

        Example:
            >>> webhook = client.webhooks.create(
            ...     name="Memory Updates",
            ...     url="https://example.com/webhook",
            ...     events=[WebhookEvent.MEMORY_CREATED, WebhookEvent.MEMORY_UPDATED]
            ... )
        """
        # Validate webhook URL to prevent SSRF attacks
        validate_webhook_url(url)
        data = WebhookCreate(
            name=name,
            url=url,
            events=events,
            space_id=space_id,
            headers=headers,
            filters=filters,
        )
        response = self._client._request(
            "POST", "/webhooks", json=data.model_dump(exclude_none=True)
        )
        return Webhook.model_validate(response)

    def list(self) -> WebhookList:
        """
        List all webhooks.

        Returns:
            List of webhooks

        Example:
            >>> webhooks = client.webhooks.list()
        """
        response = self._client._request("GET", "/webhooks")
        return WebhookList.model_validate(response)

    def get(self, id: str) -> Webhook:
        """
        Get a webhook by ID.

        Args:
            id: Webhook ID

        Returns:
            Webhook object

        Example:
            >>> webhook = client.webhooks.get("webhook_123")
        """
        validate_id(id, "webhook")
        response = self._client._request("GET", f"/webhooks/{id}")
        return Webhook.model_validate(response)

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        headers: Optional[Dict[str, str]] = None,
        filters: Optional[WebhookFilter] = None,
        active: Optional[bool] = None,
    ) -> Webhook:
        """
        Update a webhook.

        Args:
            id: Webhook ID
            name: New name
            url: New URL
            events: New events list
            headers: New headers
            filters: New filters
            active: Enable/disable webhook

        Returns:
            Updated webhook object

        Example:
            >>> webhook = client.webhooks.update(
            ...     "webhook_123",
            ...     active=False
            ... )
        """
        validate_id(id, "webhook")
        # Validate webhook URL if being updated
        if url:
            validate_webhook_url(url)
        data = WebhookUpdate(
            name=name,
            url=url,
            events=events,
            headers=headers,
            filters=filters,
            active=active,
        )
        response = self._client._request(
            "PATCH", f"/webhooks/{id}", json=data.model_dump(exclude_none=True)
        )
        return Webhook.model_validate(response)

    def delete(self, id: str) -> None:
        """
        Delete a webhook.

        Args:
            id: Webhook ID

        Example:
            >>> client.webhooks.delete("webhook_123")
        """
        validate_id(id, "webhook")
        self._client._request("DELETE", f"/webhooks/{id}")

    def test(self, id: str, event_type: Optional[WebhookEvent] = None) -> Dict[str, Any]:
        """
        Test a webhook by sending a test event.

        Args:
            id: Webhook ID
            event_type: Optional specific event type to test

        Returns:
            Test result

        Example:
            >>> result = client.webhooks.test("webhook_123")
        """
        validate_id(id, "webhook")
        params: Dict[str, Any] = {}
        if event_type:
            params["event_type"] = event_type.value

        response = self._client._request("POST", f"/webhooks/{id}/test", params=params)
        return dict(response)

    def get_deliveries(
        self, id: str, limit: int = 100, status: Optional[str] = None
    ) -> WebhookDeliveryList:
        """
        Get webhook delivery history.

        Args:
            id: Webhook ID
            limit: Maximum number of deliveries
            status: Filter by delivery status

        Returns:
            List of webhook deliveries

        Example:
            >>> deliveries = client.webhooks.get_deliveries("webhook_123", limit=50)
        """
        validate_id(id, "webhook")
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status

        response = self._client._request("GET", f"/webhooks/{id}/deliveries", params=params)
        return WebhookDeliveryList.model_validate(response)

    def retry_delivery(self, webhook_id: str, delivery_id: str) -> WebhookDelivery:
        """
        Retry a failed webhook delivery.

        Args:
            webhook_id: Webhook ID
            delivery_id: Delivery ID

        Returns:
            Updated delivery object

        Example:
            >>> delivery = client.webhooks.retry_delivery(
            ...     "webhook_123",
            ...     "delivery_456"
            ... )
        """
        validate_id(webhook_id, "webhook")
        validate_id(delivery_id, "delivery")
        response = self._client._request(
            "POST", f"/webhooks/{webhook_id}/deliveries/{delivery_id}/retry"
        )
        return WebhookDelivery.model_validate(response)

    def get_event_types(self) -> List[WebhookEventTypeInfo]:
        """
        Get available webhook event types.

        Returns:
            List of available event types

        Example:
            >>> event_types = client.webhooks.get_event_types()
            >>> for et in event_types:
            ...     print(f"{et.name}: {et.description}")
        """
        response = self._client._request("GET", "/webhooks/event-types")
        return [WebhookEventTypeInfo.model_validate(e) for e in response.get("event_types", [])]

    def get_stats(self) -> WebhookStats:
        """
        Get webhook statistics.

        Returns:
            Webhook statistics

        Example:
            >>> stats = client.webhooks.get_stats()
            >>> print(f"Total webhooks: {stats.total_webhooks}")
            >>> print(f"Delivery success rate: {stats.success_rate}%")
        """
        response = self._client._request("GET", "/webhooks/stats")
        return WebhookStats.model_validate(response)

    def get_events(self, limit: int = 100, offset: int = 0) -> WebhookDeliveryList:
        """
        Get webhook events.

        Args:
            limit: Maximum number of events
            offset: Offset for pagination

        Returns:
            List of webhook events

        Example:
            >>> events = client.webhooks.get_events(limit=50)
        """
        params = {"limit": limit, "offset": offset}
        response = self._client._request("GET", "/webhooks/events", params=params)
        return WebhookDeliveryList.model_validate(response)

    def bulk_create(self, webhooks: List[WebhookCreate]) -> Dict[str, Any]:
        """
        Create multiple webhooks in bulk.

        Args:
            webhooks: List of webhook creation requests

        Returns:
            Bulk operation result

        Example:
            >>> result = client.webhooks.bulk_create([
            ...     WebhookCreate(name="Hook1", url="https://example.com/1", events=[...]),
            ...     WebhookCreate(name="Hook2", url="https://example.com/2", events=[...])
            ... ])
        """
        # Validate all webhook URLs
        for webhook in webhooks:
            validate_webhook_url(webhook.url)
        data = {"webhooks": [w.model_dump(exclude_none=True) for w in webhooks]}
        response = self._client._request("POST", "/webhooks/bulk", json=data)
        return dict(response)

    def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple webhooks in bulk.

        Args:
            ids: List of webhook IDs to delete

        Returns:
            Bulk operation result

        Example:
            >>> result = client.webhooks.bulk_delete(["webhook_1", "webhook_2"])
        """
        for id in ids:
            validate_id(id, "webhook")
        data = {"ids": ids}
        response = self._client._request("DELETE", "/webhooks/bulk", json=data)
        return dict(response)


class AsyncWebhooksResource:
    """Async resource for managing webhooks."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async webhooks resource with client."""
        self._client = client

    async def create(
        self,
        name: str,
        url: str,
        events: List[WebhookEvent],
        space_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        filters: Optional[WebhookFilter] = None,
    ) -> Webhook:
        """Create a new webhook (async)."""
        # Validate webhook URL to prevent SSRF attacks
        validate_webhook_url(url)
        data = WebhookCreate(
            name=name,
            url=url,
            events=events,
            space_id=space_id,
            headers=headers,
            filters=filters,
        )
        response = await self._client._request(
            "POST", "/webhooks", json=data.model_dump(exclude_none=True)
        )
        return Webhook.model_validate(response)

    async def list(self) -> WebhookList:
        """List all webhooks (async)."""
        response = await self._client._request("GET", "/webhooks")
        return WebhookList.model_validate(response)

    async def get(self, id: str) -> Webhook:
        """Get a webhook by ID (async)."""
        validate_id(id, "webhook")
        response = await self._client._request("GET", f"/webhooks/{id}")
        return Webhook.model_validate(response)

    async def update(
        self,
        id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        headers: Optional[Dict[str, str]] = None,
        filters: Optional[WebhookFilter] = None,
        active: Optional[bool] = None,
    ) -> Webhook:
        """Update a webhook (async)."""
        validate_id(id, "webhook")
        # Validate webhook URL if being updated
        if url:
            validate_webhook_url(url)
        data = WebhookUpdate(
            name=name,
            url=url,
            events=events,
            headers=headers,
            filters=filters,
            active=active,
        )
        response = await self._client._request(
            "PATCH", f"/webhooks/{id}", json=data.model_dump(exclude_none=True)
        )
        return Webhook.model_validate(response)

    async def delete(self, id: str) -> None:
        """Delete a webhook (async)."""
        validate_id(id, "webhook")
        await self._client._request("DELETE", f"/webhooks/{id}")

    async def test(self, id: str, event_type: Optional[WebhookEvent] = None) -> Dict[str, Any]:
        """Test a webhook by sending a test event (async)."""
        validate_id(id, "webhook")
        params: Dict[str, Any] = {}
        if event_type:
            params["event_type"] = event_type.value

        response = await self._client._request("POST", f"/webhooks/{id}/test", params=params)
        return dict(response)

    async def get_deliveries(
        self, id: str, limit: int = 100, status: Optional[str] = None
    ) -> WebhookDeliveryList:
        """Get webhook delivery history (async)."""
        validate_id(id, "webhook")
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status

        response = await self._client._request("GET", f"/webhooks/{id}/deliveries", params=params)
        return WebhookDeliveryList.model_validate(response)

    async def retry_delivery(self, webhook_id: str, delivery_id: str) -> WebhookDelivery:
        """Retry a failed webhook delivery (async)."""
        validate_id(webhook_id, "webhook")
        validate_id(delivery_id, "delivery")
        response = await self._client._request(
            "POST", f"/webhooks/{webhook_id}/deliveries/{delivery_id}/retry"
        )
        return WebhookDelivery.model_validate(response)

    async def get_event_types(self) -> List[WebhookEventTypeInfo]:
        """Get available webhook event types (async)."""
        response = await self._client._request("GET", "/webhooks/event-types")
        return [WebhookEventTypeInfo.model_validate(e) for e in response.get("event_types", [])]

    async def get_stats(self) -> WebhookStats:
        """Get webhook statistics (async)."""
        response = await self._client._request("GET", "/webhooks/stats")
        return WebhookStats.model_validate(response)

    async def get_events(self, limit: int = 100, offset: int = 0) -> WebhookDeliveryList:
        """Get webhook events (async)."""
        params = {"limit": limit, "offset": offset}
        response = await self._client._request("GET", "/webhooks/events", params=params)
        return WebhookDeliveryList.model_validate(response)

    async def bulk_create(self, webhooks: List[WebhookCreate]) -> Dict[str, Any]:
        """Create multiple webhooks in bulk (async)."""
        for webhook in webhooks:
            validate_webhook_url(webhook.url)
        data = {"webhooks": [w.model_dump(exclude_none=True) for w in webhooks]}
        response = await self._client._request("POST", "/webhooks/bulk", json=data)
        return dict(response)

    async def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """Delete multiple webhooks in bulk (async)."""
        for id in ids:
            validate_id(id, "webhook")
        data = {"ids": ids}
        response = await self._client._request("DELETE", "/webhooks/bulk", json=data)
        return dict(response)
