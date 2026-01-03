from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DomainEvent(_message.Message):
    __slots__ = ("event_id", "event_type", "aggregate_id", "aggregate_type", "version", "payload", "metadata", "occurred_at", "published_at", "source_service", "user_id", "correlation_id", "trace_id", "span_id", "parent_span_id", "hlc_timestamp", "hlc_counter")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATE_ID_FIELD_NUMBER: _ClassVar[int]
    AGGREGATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    HLC_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HLC_COUNTER_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    version: int
    payload: _struct_pb2.Struct
    metadata: _struct_pb2.Struct
    occurred_at: _timestamp_pb2.Timestamp
    published_at: _timestamp_pb2.Timestamp
    source_service: str
    user_id: str
    correlation_id: str
    trace_id: str
    span_id: str
    parent_span_id: str
    hlc_timestamp: int
    hlc_counter: int
    def __init__(self, event_id: _Optional[str] = ..., event_type: _Optional[str] = ..., aggregate_id: _Optional[str] = ..., aggregate_type: _Optional[str] = ..., version: _Optional[int] = ..., payload: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., occurred_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., published_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., source_service: _Optional[str] = ..., user_id: _Optional[str] = ..., correlation_id: _Optional[str] = ..., trace_id: _Optional[str] = ..., span_id: _Optional[str] = ..., parent_span_id: _Optional[str] = ..., hlc_timestamp: _Optional[int] = ..., hlc_counter: _Optional[int] = ...) -> None: ...

class EventAcknowledgment(_message.Message):
    __slots__ = ("event_id", "consumer_service", "success", "error_message", "processed_at")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_SERVICE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    consumer_service: str
    success: bool
    error_message: str
    processed_at: _timestamp_pb2.Timestamp
    def __init__(self, event_id: _Optional[str] = ..., consumer_service: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ..., processed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
