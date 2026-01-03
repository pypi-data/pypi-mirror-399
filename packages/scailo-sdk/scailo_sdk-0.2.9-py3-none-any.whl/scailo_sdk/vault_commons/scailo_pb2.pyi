from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VAULT_REF_FOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_REF_FOR_ANY_UNSPECIFIED: _ClassVar[VAULT_REF_FOR]
    VAULT_REF_FOR_FILE: _ClassVar[VAULT_REF_FOR]
    VAULT_REF_FOR_FOLDER: _ClassVar[VAULT_REF_FOR]

class VAULT_PERMISSION_CODE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_PERMISSION_CODE_UNSPECIFIED: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_VIEW: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_META: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_DOWNLOAD: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_ADD: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_DELETE: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_EXECUTE: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_ALL: _ClassVar[VAULT_PERMISSION_CODE]

class ENCLAVE_DOMAIN_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENCLAVE_DOMAIN_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ENCLAVE_DOMAIN_SORT_KEY]
    ENCLAVE_DOMAIN_SORT_KEY_CREATED_AT: _ClassVar[ENCLAVE_DOMAIN_SORT_KEY]
    ENCLAVE_DOMAIN_SORT_KEY_DOMAIN: _ClassVar[ENCLAVE_DOMAIN_SORT_KEY]

class VAULT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_CREATED_AT: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_MODIFIED_AT: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_NAME: _ClassVar[VAULT_SORT_KEY]

class VAULT_ACCESS_LOG_OPERATION(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_ACCESS_LOG_OPERATION_ANY_UNSPECIFIED: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_CREATE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_MOVE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_RENAME: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_DELETE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_DOWNLOAD: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_UPLOAD: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_UNZIP: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_PERSISTENT: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_PERMISSIONS: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_EXECUTE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
VAULT_REF_FOR_ANY_UNSPECIFIED: VAULT_REF_FOR
VAULT_REF_FOR_FILE: VAULT_REF_FOR
VAULT_REF_FOR_FOLDER: VAULT_REF_FOR
VAULT_PERMISSION_CODE_UNSPECIFIED: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_VIEW: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_META: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_DOWNLOAD: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_ADD: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_DELETE: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_EXECUTE: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_ALL: VAULT_PERMISSION_CODE
ENCLAVE_DOMAIN_SORT_KEY_ID_UNSPECIFIED: ENCLAVE_DOMAIN_SORT_KEY
ENCLAVE_DOMAIN_SORT_KEY_CREATED_AT: ENCLAVE_DOMAIN_SORT_KEY
ENCLAVE_DOMAIN_SORT_KEY_DOMAIN: ENCLAVE_DOMAIN_SORT_KEY
VAULT_SORT_KEY_ID_UNSPECIFIED: VAULT_SORT_KEY
VAULT_SORT_KEY_CREATED_AT: VAULT_SORT_KEY
VAULT_SORT_KEY_MODIFIED_AT: VAULT_SORT_KEY
VAULT_SORT_KEY_NAME: VAULT_SORT_KEY
VAULT_ACCESS_LOG_OPERATION_ANY_UNSPECIFIED: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_CREATE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_MOVE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_RENAME: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_DELETE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_DOWNLOAD: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_UPLOAD: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_UNZIP: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_PERSISTENT: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_PERMISSIONS: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_EXECUTE: VAULT_ACCESS_LOG_OPERATION

class VaultPermission(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    ref_for: VAULT_REF_FOR
    ref_id: int
    role_id: int
    permission_code: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., role_id: _Optional[int] = ..., permission_code: _Optional[int] = ...) -> None: ...

class VaultPermissionAddRequest(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    ref_uuid: str
    role_id: int
    permission_code: int
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., ref_uuid: _Optional[str] = ..., role_id: _Optional[int] = ..., permission_code: _Optional[int] = ...) -> None: ...

class VaultPermissionModifyRequest(_message.Message):
    __slots__ = ()
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_comment: str
    permission_code: int
    def __init__(self, uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., permission_code: _Optional[int] = ...) -> None: ...

class GixResources(_message.Message):
    __slots__ = ()
    HTML_ENTRY_FIELD_NUMBER: _ClassVar[int]
    LOGOS_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_APIS_FIELD_NUMBER: _ClassVar[int]
    html_entry: str
    logos: _containers.RepeatedScalarFieldContainer[str]
    external_apis: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, html_entry: _Optional[str] = ..., logos: _Optional[_Iterable[str]] = ..., external_apis: _Optional[_Iterable[str]] = ...) -> None: ...

class GiXManifest(_message.Message):
    __slots__ = ()
    MANIFEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_UNIQUE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    MIN_GENESIS_VERSION_FIELD_NUMBER: _ClassVar[int]
    MAX_GENESIS_VERSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    manifest_version: str
    app_version: str
    app_name: str
    app_unique_identifier: str
    min_genesis_version: str
    max_genesis_version: str
    resources: GixResources
    def __init__(self, manifest_version: _Optional[str] = ..., app_version: _Optional[str] = ..., app_name: _Optional[str] = ..., app_unique_identifier: _Optional[str] = ..., min_genesis_version: _Optional[str] = ..., max_genesis_version: _Optional[str] = ..., resources: _Optional[_Union[GixResources, _Mapping]] = ...) -> None: ...

class GiXAppRun(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    APP_UNIQUE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    EXTRACTED_PATH_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    MANIFEST_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_file_id: int
    vault_file_version_id: int
    app_unique_identifier: str
    extracted_path: str
    ip_addr: str
    manifest: GiXManifest
    run_by: str
    app_version: str
    app_name: str
    app_endpoint: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_file_id: _Optional[int] = ..., vault_file_version_id: _Optional[int] = ..., app_unique_identifier: _Optional[str] = ..., extracted_path: _Optional[str] = ..., ip_addr: _Optional[str] = ..., manifest: _Optional[_Union[GiXManifest, _Mapping]] = ..., run_by: _Optional[str] = ..., app_version: _Optional[str] = ..., app_name: _Optional[str] = ..., app_endpoint: _Optional[str] = ...) -> None: ...

class GiXAppRunsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GiXAppRun]
    def __init__(self, list: _Optional[_Iterable[_Union[GiXAppRun, _Mapping]]] = ...) -> None: ...

class GiXAppRunCountReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    run_by: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., run_by: _Optional[str] = ...) -> None: ...

class GiXAppRunFilterReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    run_by: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., run_by: _Optional[str] = ...) -> None: ...

class EnclaveResources(_message.Message):
    __slots__ = ()
    LOGOS_FIELD_NUMBER: _ClassVar[int]
    FOLDERS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    logos: _containers.RepeatedScalarFieldContainer[str]
    folders: _containers.RepeatedScalarFieldContainer[str]
    files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, logos: _Optional[_Iterable[str]] = ..., folders: _Optional[_Iterable[str]] = ..., files: _Optional[_Iterable[str]] = ...) -> None: ...

class EnclaveManifest(_message.Message):
    __slots__ = ()
    MANIFEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    ENCLAVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    ENCLAVE_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_UNIQUE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    START_EXEC_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    manifest_version: str
    enclave_type: str
    app_version: str
    app_name: str
    enclave_name: str
    app_unique_identifier: str
    start_exec: str
    resources: EnclaveResources
    def __init__(self, manifest_version: _Optional[str] = ..., enclave_type: _Optional[str] = ..., app_version: _Optional[str] = ..., app_name: _Optional[str] = ..., enclave_name: _Optional[str] = ..., app_unique_identifier: _Optional[str] = ..., start_exec: _Optional[str] = ..., resources: _Optional[_Union[EnclaveResources, _Mapping]] = ...) -> None: ...

class EnclaveIngress(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    ENCLAVE_NAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    RUNNER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    APP_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    token: str
    expires_at: int
    vault_file_id: int
    vault_file_version_id: int
    enclave_name: str
    ip_addr: str
    runner_user_id: int
    runner_role_id: int
    app_endpoint: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., token: _Optional[str] = ..., expires_at: _Optional[int] = ..., vault_file_id: _Optional[int] = ..., vault_file_version_id: _Optional[int] = ..., enclave_name: _Optional[str] = ..., ip_addr: _Optional[str] = ..., runner_user_id: _Optional[int] = ..., runner_role_id: _Optional[int] = ..., app_endpoint: _Optional[str] = ...) -> None: ...

class EnclaveIngressesList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EnclaveIngress]
    def __init__(self, list: _Optional[_Iterable[_Union[EnclaveIngress, _Mapping]]] = ...) -> None: ...

class EnclaveIngressCountReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    runner_user_id: int
    runner_role_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., runner_user_id: _Optional[int] = ..., runner_role_id: _Optional[int] = ...) -> None: ...

class EnclaveIngressFilterReq(_message.Message):
    __slots__ = ()
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    runner_user_id: int
    runner_role_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., runner_user_id: _Optional[int] = ..., runner_role_id: _Optional[int] = ...) -> None: ...

class VerifyEnclaveIngressRequest(_message.Message):
    __slots__ = ()
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class VerifyEnclaveIngressResponse(_message.Message):
    __slots__ = ()
    ENCLAVE_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    ROLE_UUID_FIELD_NUMBER: _ClassVar[int]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    enclave_name: str
    user_uuid: str
    role_uuid: str
    auth_token: str
    expires_at: int
    def __init__(self, enclave_name: _Optional[str] = ..., user_uuid: _Optional[str] = ..., role_uuid: _Optional[str] = ..., auth_token: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

class EnclaveEnvironmentVariableAddRequest(_message.Message):
    __slots__ = ()
    FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_SECRET_FIELD_NUMBER: _ClassVar[int]
    file_uuid: str
    name: str
    value: str
    is_secret: bool
    def __init__(self, file_uuid: _Optional[str] = ..., name: _Optional[str] = ..., value: _Optional[str] = ..., is_secret: _Optional[bool] = ...) -> None: ...

class EnclaveEnvironmentVariableUpdateRequest(_message.Message):
    __slots__ = ()
    UUID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    value: str
    def __init__(self, uuid: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class EnclaveEnvironmentVariable(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_SECRET_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_file_id: int
    name: str
    value: str
    is_secret: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_file_id: _Optional[int] = ..., name: _Optional[str] = ..., value: _Optional[str] = ..., is_secret: _Optional[bool] = ...) -> None: ...

class EnclaveEnvironmentVariablesList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EnclaveEnvironmentVariable]
    def __init__(self, list: _Optional[_Iterable[_Union[EnclaveEnvironmentVariable, _Mapping]]] = ...) -> None: ...

class EnclaveDomainAddRequest(_message.Message):
    __slots__ = ()
    FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    file_uuid: str
    domain: str
    def __init__(self, file_uuid: _Optional[str] = ..., domain: _Optional[str] = ...) -> None: ...

class EnclaveDomain(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ADDR_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_file_id: int
    domain: str
    service_addr: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_file_id: _Optional[int] = ..., domain: _Optional[str] = ..., service_addr: _Optional[str] = ...) -> None: ...

class EnclaveDomainsFilterReq(_message.Message):
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
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ADDR_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ENCLAVE_DOMAIN_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    domain: str
    service_addr: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ENCLAVE_DOMAIN_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., domain: _Optional[str] = ..., service_addr: _Optional[str] = ...) -> None: ...

class EnclaveDomainsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EnclaveDomain]
    def __init__(self, list: _Optional[_Iterable[_Union[EnclaveDomain, _Mapping]]] = ...) -> None: ...

class EnclaveDomainSuffixResp(_message.Message):
    __slots__ = ()
    SUFFIX_FIELD_NUMBER: _ClassVar[int]
    RELAY_FIELD_NUMBER: _ClassVar[int]
    suffix: str
    relay: str
    def __init__(self, suffix: _Optional[str] = ..., relay: _Optional[str] = ...) -> None: ...

class VaultSearchReq(_message.Message):
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
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VAULT_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    ref_for: VAULT_REF_FOR
    folder_uuid: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VAULT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., folder_uuid: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class VaultSearchResponse(_message.Message):
    __slots__ = ()
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: VAULT_REF_FOR
    element_id: int
    element_uuid: str
    path: str
    parent_folder_uuid: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[VAULT_REF_FOR, str]] = ..., element_id: _Optional[int] = ..., element_uuid: _Optional[str] = ..., path: _Optional[str] = ..., parent_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultSearchResponsesList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultSearchResponse]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultSearchResponse, _Mapping]]] = ...) -> None: ...

class VaultDuplicateCheckReq(_message.Message):
    __slots__ = ()
    NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    name: str
    folder_uuid: str
    def __init__(self, name: _Optional[str] = ..., folder_uuid: _Optional[str] = ...) -> None: ...

class VaultAccessLog(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    ref_for: VAULT_REF_FOR
    ref_id: int
    username: str
    ip_addr: str
    operation: VAULT_ACCESS_LOG_OPERATION
    comment: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., username: _Optional[str] = ..., ip_addr: _Optional[str] = ..., operation: _Optional[_Union[VAULT_ACCESS_LOG_OPERATION, str]] = ..., comment: _Optional[str] = ...) -> None: ...

class VaultAccessLogCreateRequest(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    ref_for: VAULT_REF_FOR
    ref_id: int
    username: str
    ip_addr: str
    operation: VAULT_ACCESS_LOG_OPERATION
    comment: str
    def __init__(self, entity_uuid: _Optional[str] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., username: _Optional[str] = ..., ip_addr: _Optional[str] = ..., operation: _Optional[_Union[VAULT_ACCESS_LOG_OPERATION, str]] = ..., comment: _Optional[str] = ...) -> None: ...

class VaultAccessLogsList(_message.Message):
    __slots__ = ()
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultAccessLog]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultAccessLog, _Mapping]]] = ...) -> None: ...
