# Generated Connect client code

from __future__ import annotations
from collections.abc import AsyncIterator
from collections.abc import Iterator
from collections.abc import Iterable
import aiohttp
import urllib3
import typing
import sys

from connectrpc.client_async import AsyncConnectClient
from connectrpc.client_sync import ConnectClient
from connectrpc.client_protocol import ConnectProtocol
from connectrpc.client_connect import ConnectProtocolError
from connectrpc.headers import HeaderInput
from connectrpc.server import ClientRequest
from connectrpc.server import ClientStream
from connectrpc.server import ServerResponse
from connectrpc.server import ServerStream
from connectrpc.server_sync import ConnectWSGI
from connectrpc.streams import StreamInput
from connectrpc.streams import AsyncStreamOutput
from connectrpc.streams import StreamOutput
from connectrpc.unary import UnaryOutput
from connectrpc.unary import ClientStreamingOutput

if typing.TYPE_CHECKING:
    # wsgiref.types was added in Python 3.11.
    if sys.version_info >= (3, 11):
        from wsgiref.types import WSGIApplication
    else:
        from _typeshed.wsgi import WSGIApplication

from scailo_sdk import base, transactional_emails

class TransactionalEmailsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Create"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)


    def create(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewByID"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = self.call_view_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_recipients(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailRecipientsList]:
        """Low-level method to call ViewRecipients, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewRecipients"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailRecipientsList,extra_headers, timeout_seconds)


    def view_recipients(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailRecipientsList:
        response = self.call_view_recipients(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_attachments(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList]:
        """Low-level method to call ViewAttachments, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewAttachments"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList,extra_headers, timeout_seconds)


    def view_attachments(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList:
        response = self.call_view_attachments(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/SearchAll"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Filter"
        return self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)


    def filter(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_as_csv(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncTransactionalEmailsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Create"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)

    async def create(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = await self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewByID"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = await self.call_view_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmail]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmail,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmail:
        response = await self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = await self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_recipients(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailRecipientsList]:
        """Low-level method to call ViewRecipients, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewRecipients"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailRecipientsList,extra_headers, timeout_seconds)

    async def view_recipients(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailRecipientsList:
        response = await self.call_view_recipients(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_attachments(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList]:
        """Low-level method to call ViewAttachments, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/ViewAttachments"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList,extra_headers, timeout_seconds)

    async def view_attachments(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList:
        response = await self.call_view_attachments(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/SearchAll"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Filter"
        return await self._connect_client.call_unary(url, req, transactional_emails.scailo_pb2.TransactionalEmailsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> transactional_emails.scailo_pb2.TransactionalEmailsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_as_csv(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.TransactionalEmailsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class TransactionalEmailsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmail]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmail]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmail]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        ...
    def view_recipients(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmailRecipientsList]:
        ...
    def view_attachments(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmailAttachmentsList]:
        ...
    def search_all(self, req: ClientRequest[transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        ...
    def filter(self, req: ClientRequest[transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq]) -> ServerResponse[transactional_emails.scailo_pb2.TransactionalEmailsList]:
        ...
    def count(self, req: ClientRequest[transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

TRANSACTIONAL_EMAILS_SERVICE_PATH_PREFIX = "/Scailo.TransactionalEmailsService"

def wsgi_transactional_emails_service(implementation: TransactionalEmailsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/Create", implementation.create, transactional_emails.scailo_pb2.TransactionalEmailsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/ViewRecipients", implementation.view_recipients, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/ViewAttachments", implementation.view_attachments, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/SearchAll", implementation.search_all, transactional_emails.scailo_pb2.TransactionalEmailsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/Filter", implementation.filter, transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/Count", implementation.count, transactional_emails.scailo_pb2.TransactionalEmailsServiceCountReq)
    app.register_unary_rpc("/Scailo.TransactionalEmailsService/DownloadAsCSV", implementation.download_as_csv, transactional_emails.scailo_pb2.TransactionalEmailsServiceFilterReq)
    return app
