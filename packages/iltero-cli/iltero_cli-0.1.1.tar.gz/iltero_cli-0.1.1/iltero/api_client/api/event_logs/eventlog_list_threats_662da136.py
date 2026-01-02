from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.event_resolution import EventResolution
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: list[EventResolution] | None,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/event-logs/threats",
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
    *,
    client: AuthenticatedClient,
    body: list[EventResolution] | None,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[APIResponseModel]:
    """List Threats

     List security threats.

    Args:
        request: HTTP request
        resolution_statuses: Optional resolution status filter
        limit: Optional limit
        offset: Optional offset

    Returns:
        API response with threat events

    Raises:
        400: If validation fails

    Args:
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        body (list[EventResolution] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: list[EventResolution] | None,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> APIResponseModel | None:
    """List Threats

     List security threats.

    Args:
        request: HTTP request
        resolution_statuses: Optional resolution status filter
        limit: Optional limit
        offset: Optional offset

    Returns:
        API response with threat events

    Raises:
        400: If validation fails

    Args:
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        body (list[EventResolution] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        body=body,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: list[EventResolution] | None,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[APIResponseModel]:
    """List Threats

     List security threats.

    Args:
        request: HTTP request
        resolution_statuses: Optional resolution status filter
        limit: Optional limit
        offset: Optional offset

    Returns:
        API response with threat events

    Raises:
        400: If validation fails

    Args:
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        body (list[EventResolution] | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: list[EventResolution] | None,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> APIResponseModel | None:
    """List Threats

     List security threats.

    Args:
        request: HTTP request
        resolution_statuses: Optional resolution status filter
        limit: Optional limit
        offset: Optional offset

    Returns:
        API response with threat events

    Raises:
        400: If validation fails

    Args:
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        body (list[EventResolution] | None):

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
            limit=limit,
            offset=offset,
        )
    ).parsed
