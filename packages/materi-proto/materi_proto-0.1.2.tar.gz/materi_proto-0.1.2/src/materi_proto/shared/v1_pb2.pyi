from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    ACTIVE: _ClassVar[Status]
    INACTIVE: _ClassVar[Status]
    PENDING: _ClassVar[Status]
    ARCHIVED: _ClassVar[Status]
    DELETED: _ClassVar[Status]

class SourceService(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOURCE_SERVICE_UNSPECIFIED: _ClassVar[SourceService]
    SHIELD: _ClassVar[SourceService]
    API: _ClassVar[SourceService]
    RELAY: _ClassVar[SourceService]
    ARIA: _ClassVar[SourceService]
    FOLIO: _ClassVar[SourceService]
    PRINTERY: _ClassVar[SourceService]
    ARENA: _ClassVar[SourceService]

class PermissionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PERMISSION_LEVEL_UNSPECIFIED: _ClassVar[PermissionLevel]
    PERMISSION_LEVEL_NONE: _ClassVar[PermissionLevel]
    PERMISSION_LEVEL_READ: _ClassVar[PermissionLevel]
    PERMISSION_LEVEL_WRITE: _ClassVar[PermissionLevel]
    PERMISSION_LEVEL_ADMIN: _ClassVar[PermissionLevel]

class OperationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_TYPE_UNSPECIFIED: _ClassVar[OperationType]
    OPERATION_TYPE_INSERT: _ClassVar[OperationType]
    OPERATION_TYPE_DELETE: _ClassVar[OperationType]
    OPERATION_TYPE_RETAIN: _ClassVar[OperationType]
    OPERATION_TYPE_FORMAT: _ClassVar[OperationType]
STATUS_UNSPECIFIED: Status
ACTIVE: Status
INACTIVE: Status
PENDING: Status
ARCHIVED: Status
DELETED: Status
SOURCE_SERVICE_UNSPECIFIED: SourceService
SHIELD: SourceService
API: SourceService
RELAY: SourceService
ARIA: SourceService
FOLIO: SourceService
PRINTERY: SourceService
ARENA: SourceService
PERMISSION_LEVEL_UNSPECIFIED: PermissionLevel
PERMISSION_LEVEL_NONE: PermissionLevel
PERMISSION_LEVEL_READ: PermissionLevel
PERMISSION_LEVEL_WRITE: PermissionLevel
PERMISSION_LEVEL_ADMIN: PermissionLevel
OPERATION_TYPE_UNSPECIFIED: OperationType
OPERATION_TYPE_INSERT: OperationType
OPERATION_TYPE_DELETE: OperationType
OPERATION_TYPE_RETAIN: OperationType
OPERATION_TYPE_FORMAT: OperationType
EVENT_METADATA_FIELD_NUMBER: _ClassVar[int]
event_metadata: _descriptor.FieldDescriptor
AGGREGATE_METADATA_FIELD_NUMBER: _ClassVar[int]
aggregate_metadata: _descriptor.FieldDescriptor
SCHEMA_METADATA_FIELD_NUMBER: _ClassVar[int]
schema_metadata: _descriptor.FieldDescriptor

class EventMetadata(_message.Message):
    __slots__ = ("event_type", "aggregate_type", "stream_name", "consumers", "retention_days", "ordering", "deprecation_notes", "first_published", "frequency", "is_auditable", "is_replayable")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    RETENTION_DAYS_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    DEPRECATION_NOTES_FIELD_NUMBER: _ClassVar[int]
    FIRST_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    IS_AUDITABLE_FIELD_NUMBER: _ClassVar[int]
    IS_REPLAYABLE_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    aggregate_type: str
    stream_name: str
    consumers: _containers.RepeatedScalarFieldContainer[str]
    retention_days: int
    ordering: str
    deprecation_notes: _containers.RepeatedScalarFieldContainer[str]
    first_published: str
    frequency: str
    is_auditable: bool
    is_replayable: bool
    def __init__(self, event_type: _Optional[str] = ..., aggregate_type: _Optional[str] = ..., stream_name: _Optional[str] = ..., consumers: _Optional[_Iterable[str]] = ..., retention_days: _Optional[int] = ..., ordering: _Optional[str] = ..., deprecation_notes: _Optional[_Iterable[str]] = ..., first_published: _Optional[str] = ..., frequency: _Optional[str] = ..., is_auditable: bool = ..., is_replayable: bool = ...) -> None: ...

class AggregateMetadata(_message.Message):
    __slots__ = ("aggregate_type", "description", "event_types", "partition_key")
    AGGREGATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    PARTITION_KEY_FIELD_NUMBER: _ClassVar[int]
    aggregate_type: str
    description: str
    event_types: _containers.RepeatedScalarFieldContainer[str]
    partition_key: str
    def __init__(self, aggregate_type: _Optional[str] = ..., description: _Optional[str] = ..., event_types: _Optional[_Iterable[str]] = ..., partition_key: _Optional[str] = ...) -> None: ...

class SchemaMetadata(_message.Message):
    __slots__ = ("version", "updated_at", "total_event_types", "total_streams", "description", "maintainer_email", "documentation_url")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STREAMS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MAINTAINER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTATION_URL_FIELD_NUMBER: _ClassVar[int]
    version: str
    updated_at: str
    total_event_types: int
    total_streams: int
    description: str
    maintainer_email: str
    documentation_url: str
    def __init__(self, version: _Optional[str] = ..., updated_at: _Optional[str] = ..., total_event_types: _Optional[int] = ..., total_streams: _Optional[int] = ..., description: _Optional[str] = ..., maintainer_email: _Optional[str] = ..., documentation_url: _Optional[str] = ...) -> None: ...
