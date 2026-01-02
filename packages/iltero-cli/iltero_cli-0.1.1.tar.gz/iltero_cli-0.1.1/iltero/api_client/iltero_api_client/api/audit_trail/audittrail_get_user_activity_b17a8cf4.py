import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.audit_category import AuditCategory
from ...types import UNSET, Response, Unset


def _get_kwargs(
    identifier: str,
    *,
    body: list[AuditCategory] | None,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

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
        "url": f"/v1/audit/logs/user/{identifier}",
        "params": params,
    }

    _kwargs["json"]: list[str] | None
    if isinstance(body, list):
        _kwargs["json"] = []
        for body_type_0_item_data in body:
            body_type_0_item = body_type_0_item_data.value
            _kwargs["json"].append(body_type_0_item)

    else:
        _kwargs["json"] = body

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
    identifier: str,
    *,
    client: AuthenticatedClient,
    body: list[AuditCategory] | None,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Get User Activity

     Get audit logs for specific user.

    Args:
        request: HTTP request
        identifier: User identifier (ID or email)
        categories: Optional category filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with user activity

    Raises:
        400: If validation fails

    Args:
        identifier (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (list[AuditCategory] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        identifier=identifier,
        body=body,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    identifier: str,
    *,
    client: AuthenticatedClient,
    body: list[AuditCategory] | None,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Get User Activity

     Get audit logs for specific user.

    Args:
        request: HTTP request
        identifier: User identifier (ID or email)
        categories: Optional category filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with user activity

    Raises:
        400: If validation fails

    Args:
        identifier (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (list[AuditCategory] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        identifier=identifier,
        client=client,
        body=body,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    identifier: str,
    *,
    client: AuthenticatedClient,
    body: list[AuditCategory] | None,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Get User Activity

     Get audit logs for specific user.

    Args:
        request: HTTP request
        identifier: User identifier (ID or email)
        categories: Optional category filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with user activity

    Raises:
        400: If validation fails

    Args:
        identifier (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (list[AuditCategory] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        identifier=identifier,
        body=body,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    identifier: str,
    *,
    client: AuthenticatedClient,
    body: list[AuditCategory] | None,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Get User Activity

     Get audit logs for specific user.

    Args:
        request: HTTP request
        identifier: User identifier (ID or email)
        categories: Optional category filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with user activity

    Raises:
        400: If validation fails

    Args:
        identifier (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.
        body (list[AuditCategory] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            identifier=identifier,
            client=client,
            body=body,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    ).parsed
