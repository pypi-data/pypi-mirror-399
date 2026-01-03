"""Tests for Entities resource."""

import pytest
from unittest.mock import Mock, AsyncMock

from trix.resources.entities import EntitiesResource, AsyncEntitiesResource


class TestEntitiesResource:
    """Tests for EntitiesResource (sync)."""

    def test_create_entity(self):
        """Test creating an entity."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "ent_123",
            "name": "Albert Einstein",
            "type": "person",
            "aliases": ["Einstein", "A. Einstein"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = EntitiesResource(mock_client)
        result = resource.create(
            name="Albert Einstein",
            entity_type="person",
            aliases=["Einstein", "A. Einstein"],
        )

        mock_client._request.assert_called_once()
        assert result.id == "ent_123"
        assert result.name == "Albert Einstein"
        assert result.type == "person"

    def test_create_entity_with_properties(self):
        """Test creating an entity with custom properties."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "ent_124",
            "name": "Trix",
            "type": "product",
            "properties": {"language": "TypeScript", "open_source": True},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = EntitiesResource(mock_client)
        result = resource.create(
            name="Trix",
            entity_type="product",
            properties={"language": "TypeScript", "open_source": True},
        )

        mock_client._request.assert_called_once()
        assert result.properties["language"] == "TypeScript"

    def test_get_entity(self):
        """Test getting an entity by ID."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "ent_123",
            "name": "Einstein",
            "type": "person",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = EntitiesResource(mock_client)
        result = resource.get("ent_123")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("GET", "/entities/ent_123")
        assert result.id == "ent_123"

    def test_list_entities(self):
        """Test listing entities."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "ent_1",
                    "name": "Einstein",
                    "type": "person",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
            "total": 1,
            "limit": 10,
            "offset": 0,
        }

        resource = EntitiesResource(mock_client)
        result = resource.list()

        mock_client._request.assert_called_once()
        assert len(result.data) == 1

    def test_list_entities_by_type(self):
        """Test listing entities filtered by type."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [],
            "total": 0,
            "limit": 10,
            "offset": 0,
        }

        resource = EntitiesResource(mock_client)
        resource.list(entity_type="person")

        mock_client._request.assert_called_once()
        call_args = mock_client._request.call_args
        assert call_args[1]["params"]["type"] == "person"

    def test_update_entity(self):
        """Test updating an entity."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "id": "ent_123",
            "name": "Einstein",
            "type": "person",
            "description": "Theoretical physicist",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        resource = EntitiesResource(mock_client)
        result = resource.update("ent_123", description="Theoretical physicist")

        mock_client._request.assert_called_once()
        assert result.description == "Theoretical physicist"

    def test_delete_entity(self):
        """Test deleting an entity."""
        mock_client = Mock()
        mock_client._request.return_value = None

        resource = EntitiesResource(mock_client)
        resource.delete("ent_123")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("DELETE", "/entities/ent_123")

    def test_search_entities(self):
        """Test searching entities."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "ent_1",
                    "name": "Albert Einstein",
                    "type": "person",
                    "score": 0.98,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        }

        resource = EntitiesResource(mock_client)
        result = resource.search("Einstein")

        mock_client._request.assert_called_once()
        assert len(result.data) == 1

    def test_resolve_entity(self):
        """Test resolving text to an entity."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "text": "Einstein",
            "entity": {
                "id": "ent_123",
                "name": "Albert Einstein",
                "type": "person",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            "confidence": 0.95,
        }

        resource = EntitiesResource(mock_client)
        result = resource.resolve("Einstein")

        mock_client._request.assert_called_once()
        assert result.entity.id == "ent_123"
        assert result.confidence == 0.95

    def test_merge_entities(self):
        """Test merging two entities."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "merged_entity": {
                "id": "ent_1",
                "name": "Albert Einstein",
                "aliases": ["Einstein", "A. Einstein"],
                "type": "person",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            "deleted_id": "ent_2",
        }

        resource = EntitiesResource(mock_client)
        result = resource.merge("ent_1", "ent_2")

        mock_client._request.assert_called_once()
        assert result.deleted_id == "ent_2"

    def test_link_to_memory(self):
        """Test linking an entity to a memory."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "entity_id": "ent_123",
            "memory_id": "mem_456",
            "linked": True,
        }

        resource = EntitiesResource(mock_client)
        result = resource.link_to_memory("ent_123", "mem_456")

        mock_client._request.assert_called_once()
        assert result.linked is True

    def test_unlink_from_memory(self):
        """Test unlinking an entity from a memory."""
        mock_client = Mock()
        mock_client._request.return_value = None

        resource = EntitiesResource(mock_client)
        resource.unlink_from_memory("ent_123", "mem_456")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("DELETE", "/entities/ent_123/memories/mem_456")

    def test_bulk_create_entities(self):
        """Test creating multiple entities in bulk."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "success": 2,
            "failed": 0,
        }

        resource = EntitiesResource(mock_client)
        entities = [
            {"name": "Einstein", "type": "person"},
            {"name": "Berlin", "type": "location"},
        ]
        result = resource.bulk_create(entities)

        mock_client._request.assert_called_once()
        assert result["success"] == 2

    def test_bulk_create_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        mock_client = Mock()
        resource = EntitiesResource(mock_client)

        with pytest.raises(ValueError, match="array cannot be empty"):
            resource.bulk_create([])

    def test_extract_entities(self):
        """Test extracting entities from a memory."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "memory_id": "mem_123",
            "entities": [
                {"name": "Einstein", "type": "person", "confidence": 0.95},
                {"name": "Germany", "type": "location", "confidence": 0.88},
            ],
        }

        resource = EntitiesResource(mock_client)
        result = resource.extract("mem_123")

        mock_client._request.assert_called_once()
        assert len(result.entities) == 2

    def test_get_types(self):
        """Test getting all entity types."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "types": [
                {"name": "person", "count": 150},
                {"name": "location", "count": 75},
            ],
        }

        resource = EntitiesResource(mock_client)
        result = resource.get_types()

        call_args = mock_client._request.call_args
        assert call_args[0] == ("GET", "/entities/types")
        assert len(result.types) == 2

    def test_get_facts(self):
        """Test getting facts about an entity."""
        mock_client = Mock()
        mock_client._request.return_value = {
            "entity_id": "ent_123",
            "facts": [
                {
                    "id": "fact_1",
                    "subject": "ent_123",
                    "predicate": "born_in",
                    "object": "Germany",
                    "confidence": 0.95,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        }

        resource = EntitiesResource(mock_client)
        result = resource.get_facts("ent_123")

        call_args = mock_client._request.call_args
        assert call_args[0] == ("GET", "/entities/ent_123/facts")
        assert len(result.facts) == 1


class TestAsyncEntitiesResource:
    """Tests for AsyncEntitiesResource."""

    @pytest.mark.asyncio
    async def test_create_entity(self):
        """Test creating an entity asynchronously."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {
            "id": "ent_123",
            "name": "Einstein",
            "type": "person",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        resource = AsyncEntitiesResource(mock_client)
        result = await resource.create(name="Einstein", entity_type="person")

        mock_client._request.assert_called_once()
        assert result.id == "ent_123"

    @pytest.mark.asyncio
    async def test_search_entities(self):
        """Test searching entities asynchronously."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {
            "data": [
                {
                    "id": "ent_1",
                    "name": "Einstein",
                    "type": "person",
                    "score": 0.98,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        }

        resource = AsyncEntitiesResource(mock_client)
        result = await resource.search("Einstein")

        mock_client._request.assert_called_once()
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_resolve_entity(self):
        """Test resolving text to entity asynchronously."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {
            "text": "Einstein",
            "entity": {
                "id": "ent_123",
                "name": "Albert Einstein",
                "type": "person",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            "confidence": 0.95,
        }

        resource = AsyncEntitiesResource(mock_client)
        result = await resource.resolve("Einstein")

        mock_client._request.assert_called_once()
        assert result.entity.id == "ent_123"
