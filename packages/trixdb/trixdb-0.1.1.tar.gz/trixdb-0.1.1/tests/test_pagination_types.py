"""TDD tests for pagination types."""

from trix.types import (
    BulkResult,
    Pagination,
    PaginatedResponse,
)


class TestPagination:
    """Tests for Pagination model."""

    def test_creates_with_required_fields(self):
        """Test Pagination with all required fields."""
        pagination = Pagination(
            total=100,
            page=1,
            limit=10,
            has_more=True,
        )
        assert pagination.total == 100
        assert pagination.page == 1
        assert pagination.limit == 10
        assert pagination.has_more is True

    def test_creates_with_cursor_based_pagination(self):
        """Test Pagination supports cursor-based pagination."""
        pagination = Pagination(
            total=100,
            page=1,
            limit=10,
            has_more=True,
            cursor="abc123",
        )
        assert pagination.cursor == "abc123"

    def test_cursor_is_optional(self):
        """Test cursor field is optional and defaults to None."""
        pagination = Pagination(
            total=50,
            page=1,
            limit=25,
            has_more=True,
        )
        assert pagination.cursor is None


class TestPaginatedResponse:
    """Tests for PaginatedResponse model."""

    def test_creates_with_data_and_pagination(self):
        """Test PaginatedResponse with data and pagination."""
        pagination = Pagination(
            total=2,
            page=1,
            limit=10,
            has_more=False,
        )
        response = PaginatedResponse(
            data=["item1", "item2"],
            pagination=pagination,
        )
        assert response.data == ["item1", "item2"]
        assert response.pagination.total == 2

    def test_creates_with_empty_data(self):
        """Test PaginatedResponse with empty data list."""
        pagination = Pagination(
            total=0,
            page=1,
            limit=10,
            has_more=False,
        )
        response = PaginatedResponse(
            data=[],
            pagination=pagination,
        )
        assert response.data == []
        assert response.pagination.total == 0


class TestBulkResult:
    """Tests for BulkResult model."""

    def test_creates_with_success_count(self):
        """Test BulkResult with success count."""
        result = BulkResult(success=10, failed=0)
        assert result.success == 10
        assert result.failed == 0
        assert result.errors == []

    def test_creates_with_failures_and_errors(self):
        """Test BulkResult with failures and error details."""
        errors = [
            {"index": 0, "error": "Invalid content"},
            {"index": 2, "error": "Duplicate ID"},
        ]
        result = BulkResult(success=8, failed=2, errors=errors)
        assert result.success == 8
        assert result.failed == 2
        assert len(result.errors) == 2
        assert result.errors[0]["error"] == "Invalid content"

    def test_errors_defaults_to_empty_list(self):
        """Test errors field defaults to empty list."""
        result = BulkResult(success=5, failed=0)
        assert result.errors == []

    def test_total_property(self):
        """Test total property returns sum of success and failed."""
        result = BulkResult(success=7, failed=3)
        assert result.total == 10

    def test_success_rate_property(self):
        """Test success_rate property calculates correctly."""
        result = BulkResult(success=8, failed=2)
        assert result.success_rate == 0.8

    def test_success_rate_handles_zero_total(self):
        """Test success_rate handles zero total gracefully."""
        result = BulkResult(success=0, failed=0)
        assert result.success_rate == 0.0
