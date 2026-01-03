from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmailSentEvent(_message.Message):
    __slots__ = ("email_id", "recipient_email", "subject", "template", "template_vars", "sent_at")
    EMAIL_ID_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_VARS_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    email_id: str
    recipient_email: str
    subject: str
    template: str
    template_vars: _struct_pb2.Struct
    sent_at: _timestamp_pb2.Timestamp
    def __init__(self, email_id: _Optional[str] = ..., recipient_email: _Optional[str] = ..., subject: _Optional[str] = ..., template: _Optional[str] = ..., template_vars: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., sent_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EmailDeliveryFailedEvent(_message.Message):
    __slots__ = ("email_id", "recipient_email", "error_message", "retry_count", "failed_at")
    EMAIL_ID_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_AT_FIELD_NUMBER: _ClassVar[int]
    email_id: str
    recipient_email: str
    error_message: str
    retry_count: int
    failed_at: _timestamp_pb2.Timestamp
    def __init__(self, email_id: _Optional[str] = ..., recipient_email: _Optional[str] = ..., error_message: _Optional[str] = ..., retry_count: _Optional[int] = ..., failed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class NotificationPublishedEvent(_message.Message):
    __slots__ = ("notification_id", "user_id", "notification_type", "title", "message", "action_url", "published_at")
    NOTIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ACTION_URL_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_AT_FIELD_NUMBER: _ClassVar[int]
    notification_id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    action_url: str
    published_at: _timestamp_pb2.Timestamp
    def __init__(self, notification_id: _Optional[str] = ..., user_id: _Optional[str] = ..., notification_type: _Optional[str] = ..., title: _Optional[str] = ..., message: _Optional[str] = ..., action_url: _Optional[str] = ..., published_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class NotificationReadEvent(_message.Message):
    __slots__ = ("notification_id", "user_id", "read_at")
    NOTIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    notification_id: str
    user_id: str
    read_at: _timestamp_pb2.Timestamp
    def __init__(self, notification_id: _Optional[str] = ..., user_id: _Optional[str] = ..., read_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
