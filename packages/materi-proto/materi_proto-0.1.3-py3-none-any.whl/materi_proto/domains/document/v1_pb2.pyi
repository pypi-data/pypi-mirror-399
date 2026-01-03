from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DocumentCreatedEvent(_message.Message):
    __slots__ = ("document_id", "title", "workspace_id", "owner_id", "created_at", "document_data")
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    title: str
    workspace_id: str
    owner_id: str
    created_at: _timestamp_pb2.Timestamp
    document_data: _struct_pb2.Struct
    def __init__(self, document_id: _Optional[str] = ..., title: _Optional[str] = ..., workspace_id: _Optional[str] = ..., owner_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., document_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DocumentUpdatedEvent(_message.Message):
    __slots__ = ("document_id", "version", "updated_by", "changed_fields", "updated_at")
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    version: int
    updated_by: str
    changed_fields: _struct_pb2.Struct
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, document_id: _Optional[str] = ..., version: _Optional[int] = ..., updated_by: _Optional[str] = ..., changed_fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DocumentDeletedEvent(_message.Message):
    __slots__ = ("document_id", "deleted_by", "deleted_at", "soft_delete")
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_BY_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    SOFT_DELETE_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    deleted_by: str
    deleted_at: _timestamp_pb2.Timestamp
    soft_delete: bool
    def __init__(self, document_id: _Optional[str] = ..., deleted_by: _Optional[str] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., soft_delete: bool = ...) -> None: ...

class DocumentSharedEvent(_message.Message):
    __slots__ = ("document_id", "shared_by", "shared_with", "permission_level", "shared_at")
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SHARED_BY_FIELD_NUMBER: _ClassVar[int]
    SHARED_WITH_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SHARED_AT_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    shared_by: str
    shared_with: _containers.RepeatedScalarFieldContainer[str]
    permission_level: str
    shared_at: _timestamp_pb2.Timestamp
    def __init__(self, document_id: _Optional[str] = ..., shared_by: _Optional[str] = ..., shared_with: _Optional[_Iterable[str]] = ..., permission_level: _Optional[str] = ..., shared_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
