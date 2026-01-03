from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GeneralSettings(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    COMPANY_NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PIN_CODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CIN_FIELD_NUMBER: _ClassVar[int]
    PAN_FIELD_NUMBER: _ClassVar[int]
    GSTIN_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHLESS_ACCESS_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_QUOTATION_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    EXPENSE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISABLE_VI_CREATION_WITH_BILL_DATE_AFTER_PO_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_MFA_FOR_RECORD_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    AUTO_REQ_VERIFY_ON_EXIT_RECORD_ENTRY_FIELD_NUMBER: _ClassVar[int]
    LICENSED_TO_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    company_name: str
    phone: str
    email: str
    address: str
    city: str
    state: str
    pin_code: str
    country: str
    cin: str
    pan: str
    gstin: str
    domain_name: str
    authless_access_domain: str
    purchase_order_sender_email: str
    sales_enquiry_sender_email: str
    sales_order_sender_email: str
    sales_invoice_sender_email: str
    sales_quotation_sender_email: str
    vendor_invoice_sender_email: str
    work_order_sender_email: str
    expense_sender_email: str
    disable_vi_creation_with_bill_date_after_po_approval: bool
    require_mfa_for_record_approval: bool
    auto_req_verify_on_exit_record_entry: bool
    licensed_to: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., company_name: _Optional[str] = ..., phone: _Optional[str] = ..., email: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pin_code: _Optional[str] = ..., country: _Optional[str] = ..., cin: _Optional[str] = ..., pan: _Optional[str] = ..., gstin: _Optional[str] = ..., domain_name: _Optional[str] = ..., authless_access_domain: _Optional[str] = ..., purchase_order_sender_email: _Optional[str] = ..., sales_enquiry_sender_email: _Optional[str] = ..., sales_order_sender_email: _Optional[str] = ..., sales_invoice_sender_email: _Optional[str] = ..., sales_quotation_sender_email: _Optional[str] = ..., vendor_invoice_sender_email: _Optional[str] = ..., work_order_sender_email: _Optional[str] = ..., expense_sender_email: _Optional[str] = ..., disable_vi_creation_with_bill_date_after_po_approval: _Optional[bool] = ..., require_mfa_for_record_approval: _Optional[bool] = ..., auto_req_verify_on_exit_record_entry: _Optional[bool] = ..., licensed_to: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class GeneralSettingsServiceCreateRequest(_message.Message):
    __slots__ = ()
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    COMPANY_NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PIN_CODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CIN_FIELD_NUMBER: _ClassVar[int]
    PAN_FIELD_NUMBER: _ClassVar[int]
    GSTIN_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHLESS_ACCESS_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    SALES_QUOTATION_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    EXPENSE_SENDER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISABLE_VI_CREATION_WITH_BILL_DATE_AFTER_PO_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_MFA_FOR_RECORD_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    AUTO_REQ_VERIFY_ON_EXIT_RECORD_ENTRY_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    company_name: str
    phone: str
    email: str
    address: str
    city: str
    state: str
    pin_code: str
    country: str
    cin: str
    pan: str
    gstin: str
    domain_name: str
    authless_access_domain: str
    purchase_order_sender_email: str
    sales_enquiry_sender_email: str
    sales_order_sender_email: str
    sales_invoice_sender_email: str
    sales_quotation_sender_email: str
    vendor_invoice_sender_email: str
    work_order_sender_email: str
    expense_sender_email: str
    disable_vi_creation_with_bill_date_after_po_approval: bool
    require_mfa_for_record_approval: bool
    auto_req_verify_on_exit_record_entry: bool
    logo: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., company_name: _Optional[str] = ..., phone: _Optional[str] = ..., email: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pin_code: _Optional[str] = ..., country: _Optional[str] = ..., cin: _Optional[str] = ..., pan: _Optional[str] = ..., gstin: _Optional[str] = ..., domain_name: _Optional[str] = ..., authless_access_domain: _Optional[str] = ..., purchase_order_sender_email: _Optional[str] = ..., sales_enquiry_sender_email: _Optional[str] = ..., sales_order_sender_email: _Optional[str] = ..., sales_invoice_sender_email: _Optional[str] = ..., sales_quotation_sender_email: _Optional[str] = ..., vendor_invoice_sender_email: _Optional[str] = ..., work_order_sender_email: _Optional[str] = ..., expense_sender_email: _Optional[str] = ..., disable_vi_creation_with_bill_date_after_po_approval: _Optional[bool] = ..., require_mfa_for_record_approval: _Optional[bool] = ..., auto_req_verify_on_exit_record_entry: _Optional[bool] = ..., logo: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...
