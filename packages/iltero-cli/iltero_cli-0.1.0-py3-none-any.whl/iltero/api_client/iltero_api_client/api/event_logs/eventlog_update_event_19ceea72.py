from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.event_log_update_schema import EventLogUpdateSchema
from ...types import Response


def _get_kwargs(
    event_id: str,
    *,
    body: EventLogUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/event-logs/{event_id}",
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

    if response.status_code == 404:
        response_404 = APIResponseModel.from_dict(response.json())

        return response_404

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
    event_id: str,
    *,
    client: AuthenticatedClient,
    body: EventLogUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Event

     Update an event log resolution status.

    Args:
        request: HTTP request
        event_id: Event ID
        data: Event log update data

    Returns:
        API response with updated event

    Raises:
        404: If event not found
        400: If validation fails

    Args:
        event_id (str):
        body (EventLogUpdateSchema): Schema for updating event logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str,
    *,
    client: AuthenticatedClient,
    body: EventLogUpdateSchema,
) -> APIResponseModel | None:
    """Update Event

     Update an event log resolution status.

    Args:
        request: HTTP request
        event_id: Event ID
        data: Event log update data

    Returns:
        API response with updated event

    Raises:
        404: If event not found
        400: If validation fails

    Args:
        event_id (str):
        body (EventLogUpdateSchema): Schema for updating event logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    event_id: str,
    *,
    client: AuthenticatedClient,
    body: EventLogUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Event

     Update an event log resolution status.

    Args:
        request: HTTP request
        event_id: Event ID
        data: Event log update data

    Returns:
        API response with updated event

    Raises:
        404: If event not found
        400: If validation fails

    Args:
        event_id (str):
        body (EventLogUpdateSchema): Schema for updating event logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str,
    *,
    client: AuthenticatedClient,
    body: EventLogUpdateSchema,
) -> APIResponseModel | None:
    """Update Event

     Update an event log resolution status.

    Args:
        request: HTTP request
        event_id: Event ID
        data: Event log update data

    Returns:
        API response with updated event

    Raises:
        404: If event not found
        400: If validation fails

    Args:
        event_id (str):
        body (EventLogUpdateSchema): Schema for updating event logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
            body=body,
        )
    ).parsed
