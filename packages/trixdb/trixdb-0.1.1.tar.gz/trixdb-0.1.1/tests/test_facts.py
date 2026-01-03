"""Tests for Facts resource."""

import pytest
from unittest.mock import Mock, AsyncMock

from trix.resources.facts import FactsResource, AsyncFactsResource


class TestFactsResource:
    """Tests for FactsResource (sync)."""

    def test_create_fact(self):
        """Test creating a fact with subject-predicate-object."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "fact_123",
            "subject": "Albert Einstein",
            "predicate": "was_born_in",
            "object": "Ulm, Germany",
            "confidence": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = FactsResource(mock_client)
        result = resource.create(
            subject="Albert Einstein",
            predicate="was_born_in",
            obj="Ulm, Germany",
            confidence=0.95,
        )

        mock_client._request.assert_called_once()
        assert result.id == "fact_123"
        assert result.subject == "Albert Einstein"
        assert result.predicate == "was_born_in"
        assert result.object == "Ulm, Germany"

    def test_get_fact(self):
        """Test getting a fact by ID."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "fact_123",
            "subject": "Einstein",
            "predicate": "discovered",
            "object": "Relativity",
            "confidence": 1.0,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = FactsResource(mock_client)
        result = resource.get("fact_123")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("GET", "/facts/fact_123")
        assert result.id == "fact_123"

    def test_list_facts(self):
        """Test listing facts."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "fact_1",
                    "subject": "A",
                    "predicate": "is",
                    "object": "B",
                    "confidence": 1.0,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
            "total": 1,
            "limit": 10,
            "offset": 0,
        }

        resource = FactsResource(mock_client)
        result = resource.list()

        mock_client._request.assert_called_once()
        assert len(result.data) == 1

    def test_list_facts_with_filters(self):
        """Test listing facts with filters."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [],
            "total": 0,
            "limit": 10,
            "offset": 0,
        }

        resource = FactsResource(mock_client)
        resource.list(subject="Einstein", min_confidence=0.9)

        mock_client._request.assert_called_once()
        call_args = mock_client._request.call_args
        assert call_args[1]["params"]["subject"] == "Einstein"
        assert call_args[1]["params"]["minConfidence"] == 0.9

    def test_update_fact(self):
        """Test updating a fact."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "fact_123",
            "subject": "Einstein",
            "predicate": "discovered",
            "object": "General Relativity",
            "confidence": 1.0,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        resource = FactsResource(mock_client)
        result = resource.update("fact_123", obj="General Relativity")

        mock_client._request.assert_called_once()
        assert result.object == "General Relativity"

    def test_delete_fact(self):
        """Test deleting a fact."""
        mock_client = Mock()
        mock_client._request.return_value = None

        resource = FactsResource(mock_client)
        resource.delete("fact_123")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("DELETE", "/facts/fact_123")

    def test_query_facts(self):
        """Test querying facts with natural language."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "fact_1",
                    "subject": "Einstein",
                    "predicate": "born_in",
                    "object": "Germany",
                    "confidence": 0.95,
                    "score": 0.98,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        }

        resource = FactsResource(mock_client)
        result = resource.query("Where was Einstein born?")

        mock_client._request.assert_called_once()
        assert len(result.data) == 1

    def test_bulk_create_facts(self):
        """Test creating multiple facts in bulk."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "success": 2,
            "failed": 0,
        }

        resource = FactsResource(mock_client)
        facts = [
            {"subject": "A", "predicate": "is", "object": "B", "confidence": 1.0},
            {"subject": "C", "predicate": "has", "object": "D", "confidence": 0.9},
        ]
        result = resource.bulk_create(facts)

        mock_client._request.assert_called_once()
        assert result["success"] == 2

    def test_bulk_create_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        mock_client = Mock()
        resource = FactsResource(mock_client)

        with pytest.raises(ValueError, match="array cannot be empty"):
            resource.bulk_create([])

    def test_extract_facts(self):
        """Test extracting facts from a memory."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "memory_id": "mem_123",
            "facts": [
                {
                    "subject": "Einstein",
                    "predicate": "developed",
                    "object": "Relativity",
                    "confidence": 0.92,
                },
            ],
        }

        resource = FactsResource(mock_client)
        result = resource.extract("mem_123")

        mock_client._request.assert_called_once()
        assert len(result.facts) == 1

    def test_verify_fact(self):
        """Test verifying a fact."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "fact_id": "fact_123",
            "verified": True,
            "confidence": 0.95,
            "supporting_memories": ["mem_1", "mem_2"],
        }

        resource = FactsResource(mock_client)
        result = resource.verify("fact_123")

        mock_client._request.assert_called_once()
        assert result.verified is True
        assert len(result.supporting_memories) == 2


class TestAsyncFactsResource:
    """Tests for AsyncFactsResource."""

    @pytest.mark.asyncio
    async def test_create_fact(self):
        """Test creating a fact asynchronously."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {
            "id": "fact_123",
            "subject": "Einstein",
            "predicate": "was_born_in",
            "object": "Germany",
            "confidence": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = AsyncFactsResource(mock_client)
        result = await resource.create(
            subject="Einstein",
            predicate="was_born_in",
            obj="Germany",
            confidence=0.95,
        )

        mock_client._request.assert_called_once()
        assert result.id == "fact_123"

    @pytest.mark.asyncio
    async def test_query_facts(self):
        """Test querying facts asynchronously."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "fact_1",
                    "subject": "Einstein",
                    "predicate": "born_in",
                    "object": "Germany",
                    "confidence": 0.95,
                    "score": 0.98,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        }

        resource = AsyncFactsResource(mock_client)
        result = await resource.query("Where was Einstein born?")

        mock_client._request.assert_called_once()
        assert len(result.data) == 1
