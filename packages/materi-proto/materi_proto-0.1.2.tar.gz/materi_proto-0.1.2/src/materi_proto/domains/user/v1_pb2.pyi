from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from materi_proto.shared import v1_pb2 as _v1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserCreatedEvent(_message.Message):
    __slots__ = ("user_id", "email", "name", "created_at", "user_data")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    USER_DATA_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    user_data: _struct_pb2.Struct
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., user_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UserUpdatedEvent(_message.Message):
    __slots__ = ("user_id", "changed_fields", "previous_values", "updated_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_VALUES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    changed_fields: _struct_pb2.Struct
    previous_values: _struct_pb2.Struct
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., changed_fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., previous_values: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserDeletedEvent(_message.Message):
    __slots__ = ("user_id", "email", "deleted_at", "soft_delete")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    SOFT_DELETE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    deleted_at: _timestamp_pb2.Timestamp
    soft_delete: bool
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., soft_delete: bool = ...) -> None: ...

class UserLoginEvent(_message.Message):
    __slots__ = ("user_id", "session_id", "ip_address", "user_agent", "login_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    LOGIN_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    login_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., session_id: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ..., login_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserLogoutEvent(_message.Message):
    __slots__ = ("user_id", "session_id", "logout_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    LOGOUT_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    session_id: str
    logout_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., session_id: _Optional[str] = ..., logout_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserPasswordChangedEvent(_message.Message):
    __slots__ = ("user_id", "changed_at", "by_user", "changed_by")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_AT_FIELD_NUMBER: _ClassVar[int]
    BY_USER_FIELD_NUMBER: _ClassVar[int]
    CHANGED_BY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    changed_at: _timestamp_pb2.Timestamp
    by_user: bool
    changed_by: str
    def __init__(self, user_id: _Optional[str] = ..., changed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., by_user: bool = ..., changed_by: _Optional[str] = ...) -> None: ...

class UserMFAEnabledEvent(_message.Message):
    __slots__ = ("user_id", "mfa_method", "enabled_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MFA_METHOD_FIELD_NUMBER: _ClassVar[int]
    ENABLED_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    mfa_method: str
    enabled_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., mfa_method: _Optional[str] = ..., enabled_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserMFADisabledEvent(_message.Message):
    __slots__ = ("user_id", "mfa_method", "disabled_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MFA_METHOD_FIELD_NUMBER: _ClassVar[int]
    DISABLED_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    mfa_method: str
    disabled_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., mfa_method: _Optional[str] = ..., disabled_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserLoginFailedEvent(_message.Message):
    __slots__ = ("email", "ip_address", "user_agent", "reason", "attempted_at", "user_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTED_AT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    ip_address: str
    user_agent: str
    reason: str
    attempted_at: _timestamp_pb2.Timestamp
    user_id: str
    def __init__(self, email: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ..., reason: _Optional[str] = ..., attempted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., user_id: _Optional[str] = ...) -> None: ...

class UserLockedEvent(_message.Message):
    __slots__ = ("user_id", "reason", "locked_at", "auto_unlock")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LOCKED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTO_UNLOCK_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    reason: str
    locked_at: _timestamp_pb2.Timestamp
    auto_unlock: bool
    def __init__(self, user_id: _Optional[str] = ..., reason: _Optional[str] = ..., locked_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., auto_unlock: bool = ...) -> None: ...

class UserUnlockedEvent(_message.Message):
    __slots__ = ("user_id", "unlocked_by", "unlocked_at")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UNLOCKED_BY_FIELD_NUMBER: _ClassVar[int]
    UNLOCKED_AT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    unlocked_by: str
    unlocked_at: _timestamp_pb2.Timestamp
    def __init__(self, user_id: _Optional[str] = ..., unlocked_by: _Optional[str] = ..., unlocked_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
