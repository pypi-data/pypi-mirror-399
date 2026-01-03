from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PermissionDeniedEvent(_message.Message):
    __slots__ = ("user_id", "resource_id", "resource_type", "required_permission", "occurred_at", "ip_address")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    resource_id: str
    resource_type: str
    required_permission: str
    occurred_at: _timestamp_pb2.Timestamp
    ip_address: str
    def __init__(self, user_id: _Optional[str] = ..., resource_id: _Optional[str] = ..., resource_type: _Optional[str] = ..., required_permission: _Optional[str] = ..., occurred_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ip_address: _Optional[str] = ...) -> None: ...

class DataAccessLoggedEvent(_message.Message):
    __slots__ = ("user_id", "resource_id", "resource_type", "access_type", "logged_at", "ip_address", "user_agent")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOGGED_AT_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    resource_id: str
    resource_type: str
    access_type: str
    logged_at: _timestamp_pb2.Timestamp
    ip_address: str
    user_agent: str
    def __init__(self, user_id: _Optional[str] = ..., resource_id: _Optional[str] = ..., resource_type: _Optional[str] = ..., access_type: _Optional[str] = ..., logged_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ...) -> None: ...

class AuditLogCreatedEvent(_message.Message):
    __slots__ = ("audit_log_id", "user_id", "action", "resource_type", "resource_id", "changes", "created_at")
    AUDIT_LOG_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    audit_log_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    changes: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, audit_log_id: _Optional[str] = ..., user_id: _Optional[str] = ..., action: _Optional[str] = ..., resource_type: _Optional[str] = ..., resource_id: _Optional[str] = ..., changes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
