"""
Materi Proto - Python bindings for Materi Event Schema

This package provides Python types and utilities for working with
Materi's Protocol Buffer event definitions.

Example:
    >>> from materi_proto import UserCreatedEvent, DomainEvent, Status
    >>>
    >>> event = UserCreatedEvent(
    ...     user_id="user-123",
    ...     email="alice@example.com",
    ...     name="Alice",
    ... )

Domains:
    - envelope: Core event envelope (DomainEvent, EventAcknowledgment)
    - user: User lifecycle events
    - document: Document CRUD events
    - workspace: Workspace management events
    - collaboration: Real-time collaboration events
    - aria: AI/ML analysis events
    - notification: Email and notification events
    - audit: Security and audit events
"""

__version__ = "0.1.3"

# Envelope domain
from materi_proto.domains.envelope.v1_pb2 import (
    DomainEvent,
    EventAcknowledgment,
)

# User domain
from materi_proto.domains.user.v1_pb2 import (
    UserCreatedEvent,
    UserUpdatedEvent,
    UserDeletedEvent,
    UserLoginEvent,
    UserLogoutEvent,
    UserPasswordChangedEvent,
    UserMFAEnabledEvent,
    UserMFADisabledEvent,
    UserLoginFailedEvent,
    UserLockedEvent,
    UserUnlockedEvent,
)

# Document domain
from materi_proto.domains.document.v1_pb2 import (
    DocumentCreatedEvent,
    DocumentUpdatedEvent,
    DocumentDeletedEvent,
    DocumentSharedEvent,
)

# Workspace domain
from materi_proto.domains.workspace.v1_pb2 import (
    WorkspaceCreatedEvent,
    WorkspaceUpdatedEvent,
    WorkspaceMemberAddedEvent,
    WorkspaceMemberRemovedEvent,
    WorkspaceDeletedEvent,
)

# Collaboration domain
from materi_proto.domains.collaboration.v1_pb2 import (
    CollaborationSessionStartedEvent,
    CollaborationSessionEndedEvent,
    OperationAppliedEvent,
    PresenceUpdatedEvent,
    ConflictResolvedEvent,
)

# Aria domain
from materi_proto.domains.aria.v1_pb2 import (
    AriaAnalysisStartedEvent,
    AriaAnalysisCompleteEvent,
    AriaAnalysisFailedEvent,
    AriaSafetyGatePassedEvent,
    AriaSafetyGateBlockedEvent,
)

# Notification domain
from materi_proto.domains.notification.v1_pb2 import (
    EmailSentEvent,
    EmailDeliveryFailedEvent,
    NotificationPublishedEvent,
    NotificationReadEvent,
)

# Audit domain
from materi_proto.domains.audit.v1_pb2 import (
    PermissionDeniedEvent,
    DataAccessLoggedEvent,
    AuditLogCreatedEvent,
)

# Shared types
from materi_proto.shared.v1_pb2 import (
    Status,
    SourceService,
    PermissionLevel,
    OperationType,
    EventMetadata,
    AggregateMetadata,
    SchemaMetadata,
)

__all__ = [
    # Version
    "__version__",
    # Envelope
    "DomainEvent",
    "EventAcknowledgment",
    # User domain
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserDeletedEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    "UserPasswordChangedEvent",
    "UserMFAEnabledEvent",
    "UserMFADisabledEvent",
    "UserLoginFailedEvent",
    "UserLockedEvent",
    "UserUnlockedEvent",
    # Document domain
    "DocumentCreatedEvent",
    "DocumentUpdatedEvent",
    "DocumentDeletedEvent",
    "DocumentSharedEvent",
    # Workspace domain
    "WorkspaceCreatedEvent",
    "WorkspaceUpdatedEvent",
    "WorkspaceMemberAddedEvent",
    "WorkspaceMemberRemovedEvent",
    "WorkspaceDeletedEvent",
    # Collaboration domain
    "CollaborationSessionStartedEvent",
    "CollaborationSessionEndedEvent",
    "OperationAppliedEvent",
    "PresenceUpdatedEvent",
    "ConflictResolvedEvent",
    # Aria domain
    "AriaAnalysisStartedEvent",
    "AriaAnalysisCompleteEvent",
    "AriaAnalysisFailedEvent",
    "AriaSafetyGatePassedEvent",
    "AriaSafetyGateBlockedEvent",
    # Notification domain
    "EmailSentEvent",
    "EmailDeliveryFailedEvent",
    "NotificationPublishedEvent",
    "NotificationReadEvent",
    # Audit domain
    "PermissionDeniedEvent",
    "DataAccessLoggedEvent",
    "AuditLogCreatedEvent",
    # Shared types
    "Status",
    "SourceService",
    "PermissionLevel",
    "OperationType",
    "EventMetadata",
    "AggregateMetadata",
    "SchemaMetadata",
]
