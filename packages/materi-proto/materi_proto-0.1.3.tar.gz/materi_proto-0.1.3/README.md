# @materi/proto (Python)

Python bindings for Materi Event Schema - Protocol Buffer event definitions.

## Installation

```bash
pip install materi-proto
```

## Usage

```python
from materi_proto import (
    DomainEvent,
    UserCreatedEvent,
    DocumentCreatedEvent,
    Status,
    SourceService,
)

# Create a user event
user_event = UserCreatedEvent(
    user_id="user-123",
    email="alice@example.com",
    name="Alice",
)

# Wrap in domain envelope
envelope = DomainEvent(
    event_id="evt-456",
    event_type="user.created",
    aggregate_id="user-123",
    aggregate_type="user",
    version=1,
)

# Serialize to bytes
data = envelope.SerializeToString()

# Parse from bytes
parsed = DomainEvent()
parsed.ParseFromString(data)
```

## Direct Domain Access

For more granular imports:

```python
from materi_proto.domains import user_pb2, document_pb2
from materi_proto.shared import shared_pb2

event = user_pb2.UserCreatedEvent(user_id="user-123")
status = shared_pb2.Status.STATUS_ACTIVE
```

## Available Domains

| Domain | Module | Events |
|--------|--------|--------|
| Envelope | `envelope_pb2` | DomainEvent, EventAcknowledgment |
| User | `user_pb2` | UserCreated, UserUpdated, UserDeleted, UserLogin, etc. |
| Document | `document_pb2` | DocumentCreated, DocumentUpdated, DocumentDeleted, DocumentShared |
| Workspace | `workspace_pb2` | WorkspaceCreated, WorkspaceMemberAdded, etc. |
| Collaboration | `collaboration_pb2` | SessionStarted, OperationApplied, PresenceUpdated, etc. |
| Aria | `aria_pb2` | AnalysisStarted, AnalysisComplete, SafetyGatePassed, etc. |
| Notification | `notification_pb2` | EmailSent, NotificationPublished, etc. |
| Audit | `audit_pb2` | PermissionDenied, DataAccessLogged, AuditLogCreated |

## Shared Types

```python
from materi_proto import Status, SourceService, PermissionLevel, OperationType

# Enums
Status.STATUS_ACTIVE
Status.STATUS_INACTIVE
Status.STATUS_DELETED

SourceService.SOURCE_SERVICE_API
SourceService.SOURCE_SERVICE_RELAY
SourceService.SOURCE_SERVICE_SHIELD

PermissionLevel.PERMISSION_LEVEL_OWNER
PermissionLevel.PERMISSION_LEVEL_EDITOR
PermissionLevel.PERMISSION_LEVEL_VIEWER

OperationType.OPERATION_TYPE_INSERT
OperationType.OPERATION_TYPE_DELETE
OperationType.OPERATION_TYPE_RETAIN
```

## Type Hints

This package includes `py.typed` marker and `.pyi` stub files for full type checking support:

```python
from materi_proto import UserCreatedEvent

def process_user(event: UserCreatedEvent) -> str:
    return event.user_id  # Type-safe access
```

## Development

### Regenerate from Proto

```bash
cd ../.msx
make compile-py
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest
```

### Type Checking

```bash
mypy src/materi_proto
```

## License

MIT
