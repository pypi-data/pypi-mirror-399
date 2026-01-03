from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TRANSACTIONAL_EMAIL_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSACTIONAL_EMAIL_SORT_KEY_ID_UNSPECIFIED: _ClassVar[TRANSACTIONAL_EMAIL_SORT_KEY]
    TRANSACTIONAL_EMAIL_SORT_KEY_CREATED_AT: _ClassVar[TRANSACTIONAL_EMAIL_SORT_KEY]
    TRANSACTIONAL_EMAIL_SORT_KEY_MODIFIED_AT: _ClassVar[TRANSACTIONAL_EMAIL_SORT_KEY]
TRANSACTIONAL_EMAIL_SORT_KEY_ID_UNSPECIFIED: TRANSACTIONAL_EMAIL_SORT_KEY
TRANSACTIONAL_EMAIL_SORT_KEY_CREATED_AT: TRANSACTIONAL_EMAIL_SORT_KEY
TRANSACTIONAL_EMAIL_SORT_KEY_MODIFIED_AT: TRANSACTIONAL_EMAIL_SORT_KEY

class TransactionalEmailsServiceCreateRequest(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REPLY_TO_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    sender_name: str
    title: str
    reply_to: str
    subject: str
    content: str
    recipients: _containers.RepeatedCompositeFieldContainer[TransactionalEmailsServiceAddRecipientRequest]
    attachments: _containers.RepeatedCompositeFieldContainer[TransactionalEmailsServiceAddAttachmentRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., sender_name: _Optional[str] = ..., title: _Optional[str] = ..., reply_to: _Optional[str] = ..., subject: _Optional[str] = ..., content: _Optional[str] = ..., recipients: _Optional[_Iterable[_Union[TransactionalEmailsServiceAddRecipientRequest, _Mapping]]] = ..., attachments: _Optional[_Iterable[_Union[TransactionalEmailsServiceAddAttachmentRequest, _Mapping]]] = ...) -> None: ...

class TransactionalEmail(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REPLY_TO_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TRACKING_URL_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    sender_name: str
    title: str
    reply_to: str
    subject: str
    content: str
    tracking_url: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., sender_name: _Optional[str] = ..., title: _Optional[str] = ..., reply_to: _Optional[str] = ..., subject: _Optional[str] = ..., content: _Optional[str] = ..., tracking_url: _Optional[str] = ...) -> None: ...

class TransactionalEmailsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[TransactionalEmail]
    def __init__(self, list: _Optional[_Iterable[_Union[TransactionalEmail, _Mapping]]] = ...) -> None: ...

class TransactionalEmailPaginationResp(_message.Message):
    __slots__ = ()
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[TransactionalEmail]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[TransactionalEmail, _Mapping]]] = ...) -> None: ...

class TransactionalEmailsServicePaginationReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: TRANSACTIONAL_EMAIL_SORT_KEY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TRANSACTIONAL_EMAIL_SORT_KEY, str]] = ...) -> None: ...

class TransactionalEmailsServiceFilterReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REPLY_TO_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_EMAIL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: TRANSACTIONAL_EMAIL_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    sender_name: str
    title: str
    reply_to: str
    subject: str
    recipient_email_address: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TRANSACTIONAL_EMAIL_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., sender_name: _Optional[str] = ..., title: _Optional[str] = ..., reply_to: _Optional[str] = ..., subject: _Optional[str] = ..., recipient_email_address: _Optional[str] = ...) -> None: ...

class TransactionalEmailsServiceCountReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REPLY_TO_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_EMAIL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    sender_name: str
    title: str
    reply_to: str
    subject: str
    recipient_email_address: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., sender_name: _Optional[str] = ..., title: _Optional[str] = ..., reply_to: _Optional[str] = ..., subject: _Optional[str] = ..., recipient_email_address: _Optional[str] = ...) -> None: ...

class TransactionalEmailsServiceSearchAllReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: TRANSACTIONAL_EMAIL_SORT_KEY
    entity_uuid: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TRANSACTIONAL_EMAIL_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class TransactionalEmailsServiceAddRecipientRequest(_message.Message):
    __slots__ = ()
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class TransactionalEmailRecipient(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONAL_EMAIL_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    transactional_email_id: int
    address: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., transactional_email_id: _Optional[int] = ..., address: _Optional[str] = ...) -> None: ...

class TransactionalEmailRecipientsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[TransactionalEmailRecipient]
    def __init__(self, list: _Optional[_Iterable[_Union[TransactionalEmailRecipient, _Mapping]]] = ...) -> None: ...

class TransactionalEmailsServiceAddAttachmentRequest(_message.Message):
    __slots__ = ()
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    content: bytes
    def __init__(self, name: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class TransactionalEmailAttachment(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONAL_EMAIL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    transactional_email_id: int
    name: str
    content: bytes
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., transactional_email_id: _Optional[int] = ..., name: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class TransactionalEmailAttachmentsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[TransactionalEmailAttachment]
    def __init__(self, list: _Optional[_Iterable[_Union[TransactionalEmailAttachment, _Mapping]]] = ...) -> None: ...
