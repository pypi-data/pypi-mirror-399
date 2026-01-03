"""
Agimus Client - Main entry point for the SDK.
"""
from typing import Any, Optional

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    AccessDeniedError,
    RateLimitError,
    ServerError,
)
from .query import QueryBuilder


# Default API base URL (can be overridden)
DEFAULT_BASE_URL = "https://api.agimus.ai"
DEFAULT_TIMEOUT = 30.0


class AgimusClient:
    """
    Agimus Platform SDK Client.

    Usage:
        client = AgimusClient(api_key="agm_...")

        # Query objects
        customers = client.objects("customer").filter(status="active").all()

        # Get single object
        customer = client.objects("customer").get("C123")

        # CRUD operations
        client.objects("customer").create({"id": "C1", "name": "Acme"})
        client.objects("customer").update("C1", {"status": "premium"})
        client.objects("customer").delete("C1")
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Agimus client.

        Args:
            api_key: API key (starts with "agm_")
            base_url: Override API base URL (default: https://api.agimus.ai)
            timeout: Request timeout in seconds (default: 30)

        Raises:
            ValueError: If api_key is missing or invalid format
        """
        if not api_key:
            raise ValueError("api_key is required")

        if not api_key.startswith("agm_"):
            raise ValueError("Invalid API key format. Keys should start with 'agm_'")

        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout

        # Create HTTP client with default headers
        self._http = httpx.Client(
            base_url=f"{self._base_url}/api/v1/objects",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self) -> "AgimusClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # =========================================================================
    # Public API - Query Builder
    # =========================================================================

    def objects(self, entity: str) -> QueryBuilder:
        """
        Start a query on an entity.

        Args:
            entity: Entity API name (e.g., "customer", "order")

        Returns:
            QueryBuilder for fluent query construction
        """
        return QueryBuilder(self, entity)

    # =========================================================================
    # Public API - Utility
    # =========================================================================

    def health(self) -> dict:
        """
        Check API health.

        Returns:
            Health status with version info
        """
        return self._request("GET", "/health")

    def me(self) -> dict:
        """
        Get info about the authenticated service user.

        Returns:
            Service user info (tenantId, tenantName, userId, isServiceUser,
            groupCount, rateLimitPerMinute, requestId)
        """
        return self._request("GET", "/me")

    # =========================================================================
    # Public API - Schema
    # =========================================================================

    def list_entities(self) -> list[dict]:
        """
        List all accessible entities.

        Returns:
            List of entity summaries with apiName, displayName, pluralName,
            description, icon, iconColor
        """
        response = self._request("GET", "/schema/entities")
        return response.get("entities", [])

    def get_entity_schema(self, entity: str) -> dict:
        """
        Get full schema for an entity.

        Args:
            entity: Entity API name

        Returns:
            Entity schema with apiName, entityId, displayName, pluralName,
            description, primaryKey, properties, links
        """
        return self._request("GET", f"/schema/entities/{entity}")

    def get_properties(self, entity: str) -> list[dict]:
        """
        Get properties for an entity.

        Args:
            entity: Entity API name

        Returns:
            List of property schemas
        """
        response = self._request("GET", f"/schema/entities/{entity}/properties")
        return response.get("properties", [])

    def get_property(self, entity: str, property_name: str) -> dict:
        """
        Get details for a specific property.

        Args:
            entity: Entity API name
            property_name: Property API name

        Returns:
            Property schema with apiName, propertyId, displayName, description,
            baseType, isArray, nullable, isPrimaryKey, isEditable
        """
        response = self._request("GET", f"/schema/entities/{entity}/properties/{property_name}")
        return response.get("property", {})

    def get_primary_key(self, entity: str) -> dict:
        """
        Get primary key property for an entity.

        Args:
            entity: Entity API name

        Returns:
            Primary key property schema
        """
        response = self._request("GET", f"/schema/entities/{entity}/primary-key")
        return response.get("primaryKey", {})

    def get_links(self, entity: str) -> list[dict]:
        """
        Get links for an entity.

        Args:
            entity: Entity API name

        Returns:
            List of link schemas with apiName, displayName, targetEntity,
            cardinality, direction
        """
        response = self._request("GET", f"/schema/entities/{entity}/links")
        return response.get("links", [])

    # =========================================================================
    # Internal Methods (called by QueryBuilder)
    # =========================================================================

    def _query(self, entity: str, request: dict) -> dict:
        """Execute a query request."""
        return self._request("POST", f"/{entity}/query", json=request)

    def _get_object(
        self,
        entity: str,
        pk: str,
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict:
        """Get single object by PK."""
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)

        response = self._request("GET", f"/{entity}/{pk}", params=params or None)
        return response.get("data", {})

    def _batch_get(
        self,
        entity: str,
        pks: list[str],
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict:
        """Get multiple objects by PKs."""
        request: dict[str, Any] = {"pks": pks}
        if fields:
            request["fields"] = fields
        if expand:
            request["expand"] = expand
        return self._request("POST", f"/{entity}/batch-get", json=request)

    def _count(self, entity: str, request: dict) -> int:
        """Get count of matching objects."""
        response = self._request("POST", f"/{entity}/count", json=request)
        return response.get("count", 0)

    def _distinct(
        self,
        entity: str,
        field: str,
        filter: Optional[dict] = None,
        limit: int = 1000,
    ) -> list[Any]:
        """Get distinct values for a field."""
        request: dict[str, Any] = {"field": field, "limit": limit}
        if filter:
            request["filter"] = filter
        response = self._request("POST", f"/{entity}/distinct", json=request)
        return response.get("values", [])

    def _aggregate(self, entity: str, request: dict) -> dict:
        """Run aggregation query."""
        return self._request("POST", f"/{entity}/aggregate", json=request)

    def _get_related(
        self,
        entity: str,
        pk: str,
        link: str,
        page_size: int = 50,
        offset: int = 0,
    ) -> dict:
        """Get related objects via link."""
        params = {"pageSize": page_size, "offset": offset}
        return self._request("GET", f"/{entity}/{pk}/links/{link}", params=params)

    def _count_related(self, entity: str, pk: str, link: str) -> int:
        """Count related objects via link."""
        response = self._request("GET", f"/{entity}/{pk}/links/{link}/count")
        return response.get("count", 0)

    def _create(self, entity: str, data: dict) -> dict:
        """Create an object."""
        response = self._request("POST", f"/{entity}", json=data)
        return response.get("data", {})

    def _update(self, entity: str, pk: str, data: dict) -> dict:
        """Update an object."""
        response = self._request("PATCH", f"/{entity}/{pk}", json=data)
        return response.get("data", {})

    def _upsert(self, entity: str, pk: str, data: dict) -> dict:
        """Upsert an object."""
        response = self._request("PUT", f"/{entity}/{pk}", json=data)
        return response.get("data", {})

    def _delete(self, entity: str, pk: str) -> bool:
        """Delete an object."""
        response = self._request("DELETE", f"/{entity}/{pk}")
        return response.get("deleted", False)

    def _batch(self, entity: str, operations: list[dict]) -> dict:
        """Execute batch operations."""
        return self._request("POST", f"/{entity}/batch", json={"operations": operations})

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method
            path: URL path (relative to base)
            params: Query parameters
            json: JSON body

        Returns:
            Response JSON

        Raises:
            APIError: On API error responses
        """
        try:
            response = self._http.request(
                method=method,
                url=path,
                params=params,
                json=json,
            )
        except httpx.TimeoutException:
            raise ServerError("Request timed out", status_code=504)
        except httpx.ConnectError:
            raise ServerError("Failed to connect to API", status_code=503)

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response

        Returns:
            Response JSON data

        Raises:
            Various exceptions based on status code
        """
        # Success
        if response.status_code < 400:
            if response.status_code == 204:
                return {}
            return response.json()

        # Parse error response
        try:
            error_data = response.json()
            # Handle FastAPI's HTTPException format: {"detail": {"error": {...}}}
            # And direct format: {"error": {...}}
            if "detail" in error_data:
                error = error_data["detail"].get("error", error_data["detail"])
            else:
                error = error_data.get("error", error_data)

            code = error.get("code", "UNKNOWN_ERROR") if isinstance(error, dict) else "UNKNOWN_ERROR"
            message = error.get("message", "An error occurred") if isinstance(error, dict) else str(error)
            request_id = error.get("requestId") if isinstance(error, dict) else None
            field = error.get("field") if isinstance(error, dict) else None
        except Exception:
            code = "UNKNOWN_ERROR"
            message = response.text or "An error occurred"
            request_id = None
            field = None

        status = response.status_code

        # Map to specific exception types
        if status == 401:
            raise AuthenticationError(message)

        if status == 403:
            raise AccessDeniedError(message)

        if status == 404:
            raise NotFoundError(entity=code, pk=None)

        if status == 409:
            raise ValidationError(message, field=field, details={"code": code})

        if status == 422 or status == 400:
            raise ValidationError(message, field=field, details={"code": code})

        if status == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)

        if status >= 500:
            raise ServerError(message, status_code=status)

        # Generic API error
        raise APIError(
            code=code,
            message=message,
            status_code=status,
            request_id=request_id,
            field=field,
        )
