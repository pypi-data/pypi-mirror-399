from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkspaceCreatedEvent(_message.Message):
    __slots__ = ("workspace_id", "name", "owner_id", "created_at", "workspace_data")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_DATA_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    name: str
    owner_id: str
    created_at: _timestamp_pb2.Timestamp
    workspace_data: _struct_pb2.Struct
    def __init__(self, workspace_id: _Optional[str] = ..., name: _Optional[str] = ..., owner_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., workspace_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class WorkspaceUpdatedEvent(_message.Message):
    __slots__ = ("workspace_id", "changed_fields", "previous_values", "updated_at")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_VALUES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    changed_fields: _struct_pb2.Struct
    previous_values: _struct_pb2.Struct
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, workspace_id: _Optional[str] = ..., changed_fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., previous_values: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WorkspaceMemberAddedEvent(_message.Message):
    __slots__ = ("workspace_id", "user_id", "role", "invited_by", "joined_at")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    INVITED_BY_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    user_id: str
    role: str
    invited_by: str
    joined_at: _timestamp_pb2.Timestamp
    def __init__(self, workspace_id: _Optional[str] = ..., user_id: _Optional[str] = ..., role: _Optional[str] = ..., invited_by: _Optional[str] = ..., joined_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WorkspaceMemberRemovedEvent(_message.Message):
    __slots__ = ("workspace_id", "user_id", "removed_by", "removed_at")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    REMOVED_BY_FIELD_NUMBER: _ClassVar[int]
    REMOVED_AT_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    user_id: str
    removed_by: str
    removed_at: _timestamp_pb2.Timestamp
    def __init__(self, workspace_id: _Optional[str] = ..., user_id: _Optional[str] = ..., removed_by: _Optional[str] = ..., removed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WorkspaceDeletedEvent(_message.Message):
    __slots__ = ("workspace_id", "deleted_by", "deleted_at", "soft_delete")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_BY_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    SOFT_DELETE_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    deleted_by: str
    deleted_at: _timestamp_pb2.Timestamp
    soft_delete: bool
    def __init__(self, workspace_id: _Optional[str] = ..., deleted_by: _Optional[str] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., soft_delete: bool = ...) -> None: ...
