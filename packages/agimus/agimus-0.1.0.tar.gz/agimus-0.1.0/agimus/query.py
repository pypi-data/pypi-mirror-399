"""
Query Builder for fluent API queries.

Provides Django-style filtering with method chaining:
    client.objects("customer").filter(status="active", region__in=["US", "EU"]).all()
"""
from typing import Any, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AgimusClient


class QueryBuilder:
    """
    Fluent query builder for Object Store queries.

    Supports:
    - filter(): Add filter conditions
    - sort(): Set sort order
    - fields(): Select specific fields
    - expand(): Include related objects
    - limit(): Set page size
    - all(): Execute and return all results
    - first(): Execute and return first result
    - count(): Return count of matching objects
    - distinct(): Get distinct values for a field
    - aggregate(): Run aggregation queries
    - iter(): Iterate with auto-pagination
    - batch_get(): Get multiple objects by PKs
    - batch(): Execute batch operations
    - links(): Get related objects via link
    """

    def __init__(self, client: "AgimusClient", entity: str):
        """
        Initialize query builder.

        Args:
            client: AgimusClient instance
            entity: Entity API name (e.g., "customer")
        """
        self._client = client
        self._entity = entity
        self._filters: list[dict] = []
        self._sort: list[str] = []
        self._fields: Optional[list[str]] = None
        self._expand: list[str] = []
        self._page_size: int = 50

    def filter(self, **kwargs: Any) -> "QueryBuilder":
        """
        Add filter conditions.

        Supports Django-style lookups:
            filter(status="active")              # equals
            filter(status__ne="deleted")         # not equals
            filter(age__gt=18)                   # greater than
            filter(age__gte=18)                  # greater or equal
            filter(age__lt=65)                   # less than
            filter(age__lte=65)                  # less or equal
            filter(age__between=[18, 65])        # between (inclusive)
            filter(status__in=["a", "b"])        # in list
            filter(status__nin=["x"])            # not in list
            filter(name__like="John%")           # SQL LIKE
            filter(name__ilike="%john%")         # case-insensitive LIKE
            filter(name__starts_with="John")     # starts with
            filter(name__ends_with="son")        # ends with
            filter(deleted_at__is_null=True)     # is null
            filter(deleted_at__is_not_null=True) # is not null
            filter(tags__is_empty=True)          # is empty (null or [])
            filter(tags__is_not_empty=True)      # is not empty
            filter(tags__contains="vip")         # array contains value
            filter(tags__overlaps=["a", "b"])    # array overlaps with list

        Returns:
            self for chaining
        """
        for key, value in kwargs.items():
            filter_clause = self._parse_filter(key, value)
            self._filters.append(filter_clause)
        return self

    def _parse_filter(self, key: str, value: Any) -> dict:
        """Parse a filter key into field, operator, and value."""
        # Map of suffix -> operator (order matters - longer suffixes first)
        operators = [
            ("__is_not_empty", "is_not_empty"),
            ("__is_not_null", "is_not_null"),
            ("__starts_with", "starts_with"),
            ("__ends_with", "ends_with"),
            ("__is_empty", "is_empty"),
            ("__is_null", "is_null"),
            ("__overlaps", "overlaps"),
            ("__contains", "contains"),
            ("__between", "between"),
            ("__ilike", "ilike"),
            ("__like", "like"),
            ("__gte", "gte"),
            ("__lte", "lte"),
            ("__nin", "nin"),
            ("__gt", "gt"),
            ("__lt", "lt"),
            ("__ne", "ne"),
            ("__in", "in"),
        ]

        # Check for operator suffix
        for suffix, op in operators:
            if key.endswith(suffix):
                field = key[: -len(suffix)]
                return {"field": field, "op": op, "value": value}

        # Default to equals
        return {"field": key, "op": "eq", "value": value}

    def sort(self, *fields: str) -> "QueryBuilder":
        """
        Set sort order.

        Prefix with - for descending:
            sort("-createdAt", "name")  # createdAt DESC, name ASC

        Returns:
            self for chaining
        """
        self._sort = list(fields)
        return self

    def order_by(self, *fields: str) -> "QueryBuilder":
        """Alias for sort()."""
        return self.sort(*fields)

    def fields(self, *fields: str) -> "QueryBuilder":
        """
        Select specific fields to return.

        If not called, all accessible fields are returned.

        Returns:
            self for chaining
        """
        self._fields = list(fields)
        return self

    def select(self, *fields: str) -> "QueryBuilder":
        """Alias for fields()."""
        return self.fields(*fields)

    def expand(self, *links: str) -> "QueryBuilder":
        """
        Include related objects.

        Supports nested expansion:
            expand("orders", "orders.items")

        Returns:
            self for chaining
        """
        self._expand = list(links)
        return self

    def include(self, *links: str) -> "QueryBuilder":
        """Alias for expand()."""
        return self.expand(*links)

    def limit(self, size: int) -> "QueryBuilder":
        """
        Set page size (max 100).

        Returns:
            self for chaining
        """
        self._page_size = min(size, 100)
        return self

    def page_size(self, size: int) -> "QueryBuilder":
        """Alias for limit()."""
        return self.limit(size)

    def _build_filter(self) -> Optional[dict]:
        """Build filter dict from accumulated filters."""
        if not self._filters:
            return None
        if len(self._filters) == 1:
            return self._filters[0]
        return {"and": self._filters}

    def _build_request(self, cursor: Optional[str] = None) -> dict:
        """Build the query request body."""
        request: dict[str, Any] = {
            "pageSize": self._page_size,
        }

        filter_dict = self._build_filter()
        if filter_dict:
            request["filter"] = filter_dict

        if self._sort:
            request["sort"] = self._sort

        if self._fields:
            request["fields"] = self._fields

        if self._expand:
            request["expand"] = self._expand

        if cursor:
            request["cursor"] = cursor

        return request

    # =========================================================================
    # Read Operations
    # =========================================================================

    def all(self) -> list[dict]:
        """
        Execute query and return all results.

        Note: For large result sets, use iter() instead.

        Returns:
            List of objects
        """
        return list(self.iter())

    def first(self) -> Optional[dict]:
        """
        Execute query and return first result.

        Returns:
            First object or None if no results
        """
        original_limit = self._page_size
        self._page_size = 1

        request = self._build_request()
        response = self._client._query(self._entity, request)

        self._page_size = original_limit

        data = response.get("data", [])
        return data[0] if data else None

    def count(self) -> int:
        """
        Return count of matching objects.

        Returns:
            Number of matching objects
        """
        request: dict[str, Any] = {}
        filter_dict = self._build_filter()
        if filter_dict:
            request["filter"] = filter_dict

        return self._client._count(self._entity, request)

    def get(
        self,
        pk: str,
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict:
        """
        Get a single object by primary key.

        Args:
            pk: Primary key value
            fields: Optional list of fields to return (overrides builder fields)
            expand: Optional list of links to expand (overrides builder expand)

        Returns:
            Object data

        Raises:
            NotFoundError: If object not found
        """
        return self._client._get_object(
            self._entity,
            pk,
            fields=fields or self._fields,
            expand=expand or self._expand or None,
        )

    def batch_get(
        self,
        pks: list[str],
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict:
        """
        Get multiple objects by primary keys.

        Args:
            pks: List of primary key values (max 100)
            fields: Optional list of fields to return
            expand: Optional list of links to expand

        Returns:
            Dict with data (list of objects), found (count), requested (count)
        """
        return self._client._batch_get(
            self._entity,
            pks,
            fields=fields or self._fields,
            expand=expand or self._expand or None,
        )

    def distinct(self, field: str, limit: int = 1000) -> list[Any]:
        """
        Get distinct values for a field.

        Args:
            field: Field API name
            limit: Max values to return (default 1000)

        Returns:
            List of distinct values
        """
        return self._client._distinct(
            self._entity,
            field,
            filter=self._build_filter(),
            limit=limit,
        )

    def iter(self) -> Iterator[dict]:
        """
        Iterate through all results with auto-pagination.

        Yields objects one at a time, automatically fetching
        next pages as needed.

        Yields:
            Individual objects
        """
        cursor = None

        while True:
            request = self._build_request(cursor)
            response = self._client._query(self._entity, request)

            for obj in response.get("data", []):
                yield obj

            if not response.get("hasMore", False):
                break

            cursor = response.get("cursor")
            if not cursor:
                break

    def __iter__(self) -> Iterator[dict]:
        """Allow direct iteration: for obj in client.objects("customer").filter(...)"""
        return self.iter()

    # =========================================================================
    # Aggregation
    # =========================================================================

    def aggregate(
        self,
        metrics: list[dict],
        group_by: Optional[list[dict]] = None,
        having: Optional[dict] = None,
        sort: Optional[list[str]] = None,
        limit: int = 1000,
    ) -> dict:
        """
        Run an aggregation query.

        Args:
            metrics: List of metrics, each with:
                - op: Aggregation operator (count, count_distinct, sum, avg, min, max, first, last)
                - field: Field to aggregate (optional for count)
                - alias: Output name (optional)
            group_by: List of groupings, each with:
                - field: Field to group by
                - granularity: Time granularity for date fields (year, quarter, month, week, day, hour)
            having: Post-aggregation filter (same format as filter clause)
            sort: Sort fields (can reference metric aliases)
            limit: Max groups to return (default 1000, max 10000)

        Returns:
            Dict with data (list of aggregated rows), totalGroups

        Example:
            # Count customers by region
            result = client.objects("customer").aggregate(
                metrics=[{"op": "count", "alias": "total"}],
                group_by=[{"field": "region"}],
                sort=["-total"],
                limit=10
            )

            # Monthly revenue
            result = client.objects("order").filter(status="completed").aggregate(
                metrics=[
                    {"op": "sum", "field": "total", "alias": "revenue"},
                    {"op": "count", "alias": "orders"}
                ],
                group_by=[{"field": "createdAt", "granularity": "month"}],
                sort=["-revenue"]
            )
        """
        request: dict[str, Any] = {
            "metrics": metrics,
            "limit": min(limit, 10000),
        }

        filter_dict = self._build_filter()
        if filter_dict:
            request["filter"] = filter_dict

        if group_by:
            request["groupBy"] = group_by

        if having:
            request["having"] = having

        if sort:
            request["sort"] = sort

        return self._client._aggregate(self._entity, request)

    # =========================================================================
    # Link Traversal
    # =========================================================================

    def links(self, pk: str, link: str, page_size: int = 50, offset: int = 0) -> dict:
        """
        Get related objects via a link.

        Args:
            pk: Primary key of the source object
            link: Link API name
            page_size: Number of results per page (max 100)
            offset: Number of items to skip

        Returns:
            Dict with data (list of related objects), cursor, hasMore
        """
        return self._client._get_related(
            self._entity, pk, link, page_size=page_size, offset=offset
        )

    def count_links(self, pk: str, link: str) -> int:
        """
        Count related objects via a link.

        Args:
            pk: Primary key of the source object
            link: Link API name

        Returns:
            Number of related objects
        """
        return self._client._count_related(self._entity, pk, link)

    # =========================================================================
    # Write Operations
    # =========================================================================

    def create(self, data: dict) -> dict:
        """
        Create a new object.

        Args:
            data: Object data (must include primary key)

        Returns:
            Created object
        """
        return self._client._create(self._entity, data)

    def update(self, pk: str, data: dict) -> dict:
        """
        Update an object.

        Args:
            pk: Primary key
            data: Fields to update (partial update)

        Returns:
            Updated object
        """
        return self._client._update(self._entity, pk, data)

    def upsert(self, pk: str, data: dict) -> dict:
        """
        Create or update an object.

        If the object exists, it will be updated.
        If it doesn't exist, it will be created.

        Args:
            pk: Primary key
            data: Object data

        Returns:
            Created or updated object
        """
        return self._client._upsert(self._entity, pk, data)

    def delete(self, pk: str) -> bool:
        """
        Delete an object.

        Creates a tombstone - the object won't appear in queries
        but can be restored by removing the tombstone.

        Args:
            pk: Primary key

        Returns:
            True if deleted
        """
        return self._client._delete(self._entity, pk)

    def batch(self, operations: list[dict]) -> dict:
        """
        Execute batch operations.

        Args:
            operations: List of operations, each with:
                - op: "create", "update", or "delete"
                - pk: Primary key (required for update/delete)
                - data: Object data (required for create/update)

        Returns:
            Dict with results (list of BatchResultItem), succeeded (count), failed (count)

        Example:
            result = client.objects("customer").batch([
                {"op": "create", "data": {"id": "C1", "name": "Customer 1"}},
                {"op": "update", "pk": "C2", "data": {"status": "active"}},
                {"op": "delete", "pk": "C3"},
            ])
        """
        return self._client._batch(self._entity, operations)
