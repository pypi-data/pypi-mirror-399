"""Test that all proto imports work correctly."""

import pytest


def test_version_available():
    """Test that version is accessible."""
    from materi_proto import __version__
    assert __version__ == "0.1.0"


def test_envelope_imports():
    """Test envelope domain imports."""
    from materi_proto import DomainEvent, EventAcknowledgment
    assert DomainEvent is not None
    assert EventAcknowledgment is not None


def test_user_imports():
    """Test user domain imports."""
    from materi_proto import (
        UserCreatedEvent,
        UserUpdatedEvent,
        UserDeletedEvent,
        UserLoginEvent,
    )
    assert UserCreatedEvent is not None
    assert UserUpdatedEvent is not None
    assert UserDeletedEvent is not None
    assert UserLoginEvent is not None


def test_shared_imports():
    """Test shared type imports."""
    from materi_proto import Status, SourceService, PermissionLevel
    assert Status is not None
    assert SourceService is not None
    assert PermissionLevel is not None


def test_create_user_event():
    """Test creating a user event."""
    from materi_proto import UserCreatedEvent

    event = UserCreatedEvent(
        user_id="user-123",
        email="test@example.com",
        name="Test User",
    )
    assert event.user_id == "user-123"
    assert event.email == "test@example.com"
    assert event.name == "Test User"


def test_serialize_deserialize():
    """Test serializing and deserializing a message."""
    from materi_proto import UserCreatedEvent

    original = UserCreatedEvent(
        user_id="user-456",
        email="alice@example.com",
        name="Alice",
    )

    # Serialize to bytes
    data = original.SerializeToString()
    assert isinstance(data, bytes)
    assert len(data) > 0

    # Deserialize from bytes
    parsed = UserCreatedEvent()
    parsed.ParseFromString(data)

    assert parsed.user_id == "user-456"
    assert parsed.email == "alice@example.com"
    assert parsed.name == "Alice"
