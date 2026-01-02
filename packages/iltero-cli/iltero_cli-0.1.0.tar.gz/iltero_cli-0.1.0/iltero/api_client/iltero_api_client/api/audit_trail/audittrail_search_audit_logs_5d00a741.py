import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.audit_status import AuditStatus
from ...models.audittrail_search_audit_logs_5d00a741_body_params import AudittrailSearchAuditLogs5D00A741BodyParams
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: AudittrailSearchAuditLogs5D00A741BodyParams,
    status: AuditStatus | None | Unset = UNSET,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, AuditStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_start_date: None | str | Unset
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    elif isinstance(start_date, datetime.datetime):
        json_start_date = start_date.isoformat()
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    json_end_date: None | str | Unset
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    elif isinstance(end_date, datetime.datetime):
        json_end_date = end_date.isoformat()
    else:
        json_end_date = end_date
    params["end_date"] = json_end_date

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/audit/logs",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> APIResponseModel | None:
    if response.status_code == 200:
        response_200 = APIResponseModel.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = APIResponseModel.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[APIResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: AudittrailSearchAuditLogs5D00A741BodyParams,
    status: AuditStatus | None | Unset = UNSET,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Search Audit Logs

     Search audit logs with filters.

    Args:
        request: HTTP request
        categories: Filter by audit categories
        event_types: Filter by event types
        resource_types: Filter by resource types
        user_identifiers: Filter by user IDs or emails
        status: Filter by status
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        limit: Maximum number of logs to return

    Returns:
        API response with matching logs

    Raises:
        400: If validation fails

    Args:
        status (AuditStatus | None | Unset):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (AudittrailSearchAuditLogs5D00A741BodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: AudittrailSearchAuditLogs5D00A741BodyParams,
    status: AuditStatus | None | Unset = UNSET,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Search Audit Logs

     Search audit logs with filters.

    Args:
        request: HTTP request
        categories: Filter by audit categories
        event_types: Filter by event types
        resource_types: Filter by resource types
        user_identifiers: Filter by user IDs or emails
        status: Filter by status
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        limit: Maximum number of logs to return

    Returns:
        API response with matching logs

    Raises:
        400: If validation fails

    Args:
        status (AuditStatus | None | Unset):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (AudittrailSearchAuditLogs5D00A741BodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        body=body,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: AudittrailSearchAuditLogs5D00A741BodyParams,
    status: AuditStatus | None | Unset = UNSET,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Search Audit Logs

     Search audit logs with filters.

    Args:
        request: HTTP request
        categories: Filter by audit categories
        event_types: Filter by event types
        resource_types: Filter by resource types
        user_identifiers: Filter by user IDs or emails
        status: Filter by status
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        limit: Maximum number of logs to return

    Returns:
        API response with matching logs

    Raises:
        400: If validation fails

    Args:
        status (AuditStatus | None | Unset):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (AudittrailSearchAuditLogs5D00A741BodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: AudittrailSearchAuditLogs5D00A741BodyParams,
    status: AuditStatus | None | Unset = UNSET,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Search Audit Logs

     Search audit logs with filters.

    Args:
        request: HTTP request
        categories: Filter by audit categories
        event_types: Filter by event types
        resource_types: Filter by resource types
        user_identifiers: Filter by user IDs or emails
        status: Filter by status
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        limit: Maximum number of logs to return

    Returns:
        API response with matching logs

    Raises:
        400: If validation fails

    Args:
        status (AuditStatus | None | Unset):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (AudittrailSearchAuditLogs5D00A741BodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    ).parsed
