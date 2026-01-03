from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CollaborationSessionStartedEvent(_message.Message):
    __slots__ = ("session_id", "document_id", "user_id", "connection_id", "started_at")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    document_id: str
    user_id: str
    connection_id: str
    started_at: _timestamp_pb2.Timestamp
    def __init__(self, session_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., connection_id: _Optional[str] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CollaborationSessionEndedEvent(_message.Message):
    __slots__ = ("session_id", "user_id", "ended_at", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_id: str
    ended_at: _timestamp_pb2.Timestamp
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., user_id: _Optional[str] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class OperationAppliedEvent(_message.Message):
    __slots__ = ("operation_id", "document_id", "user_id", "operation_type", "operation_data", "applied_at")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DATA_FIELD_NUMBER: _ClassVar[int]
    APPLIED_AT_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    document_id: str
    user_id: str
    operation_type: str
    operation_data: _struct_pb2.Struct
    applied_at: _timestamp_pb2.Timestamp
    def __init__(self, operation_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., operation_type: _Optional[str] = ..., operation_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., applied_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PresenceUpdatedEvent(_message.Message):
    __slots__ = ("user_id", "document_id", "presence_data", "updated_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_DATA_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    document_id: str
    presence_data: _struct_pb2.Struct
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., document_id: _Optional[str] = ..., presence_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ConflictResolvedEvent(_message.Message):
    __slots__ = ("conflict_id", "document_id", "user_id", "resolution_strategy", "resolved_data", "resolved_at")
    CONFLICT_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_DATA_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_AT_FIELD_NUMBER: _ClassVar[int]
    conflict_id: str
    document_id: str
    user_id: str
    resolution_strategy: str
    resolved_data: _struct_pb2.Struct
    resolved_at: _timestamp_pb2.Timestamp
    def __init__(self, conflict_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., resolution_strategy: _Optional[str] = ..., resolved_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., resolved_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
