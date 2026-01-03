from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AriaAnalysisStartedEvent(_message.Message):
    __slots__ = ("analysis_id", "document_id", "user_id", "analysis_type", "parameters", "started_at")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    document_id: str
    user_id: str
    analysis_type: str
    parameters: _struct_pb2.Struct
    started_at: _timestamp_pb2.Timestamp
    def __init__(self, analysis_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., analysis_type: _Optional[str] = ..., parameters: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AriaAnalysisCompleteEvent(_message.Message):
    __slots__ = ("analysis_id", "document_id", "user_id", "analysis_type", "results", "completed_at", "duration_ms")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    document_id: str
    user_id: str
    analysis_type: str
    results: _struct_pb2.Struct
    completed_at: _timestamp_pb2.Timestamp
    duration_ms: int
    def __init__(self, analysis_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., analysis_type: _Optional[str] = ..., results: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class AriaAnalysisFailedEvent(_message.Message):
    __slots__ = ("analysis_id", "document_id", "user_id", "analysis_type", "error_message", "failed_at")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FAILED_AT_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    document_id: str
    user_id: str
    analysis_type: str
    error_message: str
    failed_at: _timestamp_pb2.Timestamp
    def __init__(self, analysis_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., analysis_type: _Optional[str] = ..., error_message: _Optional[str] = ..., failed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AriaSafetyGatePassedEvent(_message.Message):
    __slots__ = ("analysis_id", "document_id", "user_id", "check_type", "passed_at")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHECK_TYPE_FIELD_NUMBER: _ClassVar[int]
    PASSED_AT_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    document_id: str
    user_id: str
    check_type: str
    passed_at: _timestamp_pb2.Timestamp
    def __init__(self, analysis_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., check_type: _Optional[str] = ..., passed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AriaSafetyGateBlockedEvent(_message.Message):
    __slots__ = ("analysis_id", "document_id", "user_id", "check_type", "reason", "flagged_items", "blocked_at")
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHECK_TYPE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    FLAGGED_ITEMS_FIELD_NUMBER: _ClassVar[int]
    BLOCKED_AT_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    document_id: str
    user_id: str
    check_type: str
    reason: str
    flagged_items: _containers.RepeatedScalarFieldContainer[str]
    blocked_at: _timestamp_pb2.Timestamp
    def __init__(self, analysis_id: _Optional[str] = ..., document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., check_type: _Optional[str] = ..., reason: _Optional[str] = ..., flagged_items: _Optional[_Iterable[str]] = ..., blocked_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
