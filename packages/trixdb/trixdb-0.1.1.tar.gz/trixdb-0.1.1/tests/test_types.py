"""Tests for Trix types."""

from datetime import datetime

from trix.types import (
    Memory,
    MemoryCreate,
    MemoryType,
    RelationshipType,
    SearchMode,
)


def test_memory_create_validation():
    """Test MemoryCreate validation."""
    memory = MemoryCreate(
        content="Test content",
        type=MemoryType.TEXT,
        tags=["test"],
    )
    assert memory.content == "Test content"
    assert memory.type == MemoryType.TEXT
    assert memory.tags == ["test"]


def test_memory_type_enum():
    """Test MemoryType enum values."""
    assert MemoryType.TEXT == "text"
    assert MemoryType.MARKDOWN == "markdown"
    assert MemoryType.URL == "url"
    assert MemoryType.AUDIO == "audio"


def test_relationship_type_enum():
    """Test RelationshipType enum values."""
    assert RelationshipType.RELATED_TO == "related_to"
    assert RelationshipType.SUPPORTS == "supports"
    assert RelationshipType.CONTRADICTS == "contradicts"


def test_search_mode_enum():
    """Test SearchMode enum values."""
    assert SearchMode.SEMANTIC == "semantic"
    assert SearchMode.KEYWORD == "keyword"
    assert SearchMode.HYBRID == "hybrid"


def test_memory_model_parsing():
    """Test Memory model parsing from dict."""
    data = {
        "id": "mem_123",
        "content": "Test content",
        "type": "text",
        "tags": ["test"],
        "metadata": {},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "access_count": 0,
    }
    memory = Memory.model_validate(data)
    assert memory.id == "mem_123"
    assert memory.content == "Test content"
    assert isinstance(memory.created_at, datetime)
