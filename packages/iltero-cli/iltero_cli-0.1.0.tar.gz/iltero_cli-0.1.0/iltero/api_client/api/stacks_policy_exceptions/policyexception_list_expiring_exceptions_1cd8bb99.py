from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    days: int | Unset = 7,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["days"] = days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/stacks/policy-exceptions/expiring-soon",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> APIResponseModel | None:
    if response.status_code == 200:
        response_200 = APIResponseModel.from_dict(response.json())

        return response_200

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
    days: int | Unset = 7,
) -> Response[APIResponseModel]:
    """List Expiring Exceptions

     List policy exceptions expiring within specified days.

    Useful for proactive renewal or migration planning before
    exceptions expire and baseline policies are enforced.

    Args:
        days (int | Unset):  Default: 7.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        days=days,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    days: int | Unset = 7,
) -> APIResponseModel | None:
    """List Expiring Exceptions

     List policy exceptions expiring within specified days.

    Useful for proactive renewal or migration planning before
    exceptions expire and baseline policies are enforced.

    Args:
        days (int | Unset):  Default: 7.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        days=days,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    days: int | Unset = 7,
) -> Response[APIResponseModel]:
    """List Expiring Exceptions

     List policy exceptions expiring within specified days.

    Useful for proactive renewal or migration planning before
    exceptions expire and baseline policies are enforced.

    Args:
        days (int | Unset):  Default: 7.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        days=days,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    days: int | Unset = 7,
) -> APIResponseModel | None:
    """List Expiring Exceptions

     List policy exceptions expiring within specified days.

    Useful for proactive renewal or migration planning before
    exceptions expire and baseline policies are enforced.

    Args:
        days (int | Unset):  Default: 7.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            days=days,
        )
    ).parsed
