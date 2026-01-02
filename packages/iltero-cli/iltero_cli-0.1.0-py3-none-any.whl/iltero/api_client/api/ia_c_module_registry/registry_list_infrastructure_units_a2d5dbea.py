from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    capabilities: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    unit_type: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_capabilities: None | str | Unset
    if isinstance(capabilities, Unset):
        json_capabilities = UNSET
    else:
        json_capabilities = capabilities
    params["capabilities"] = json_capabilities

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    json_unit_type: None | str | Unset
    if isinstance(unit_type, Unset):
        json_unit_type = UNSET
    else:
        json_unit_type = unit_type
    params["unit_type"] = json_unit_type

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/registry/infrastructure-units",
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
    capabilities: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    unit_type: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
) -> Response[APIResponseModel]:
    """List Infrastructure Units

     List infrastructure unit modules with filtering.

    Args:
        capabilities (None | str | Unset):
        provider (None | str | Unset):
        unit_type (None | str | Unset):
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        capabilities=capabilities,
        provider=provider,
        unit_type=unit_type,
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
    capabilities: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    unit_type: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
) -> APIResponseModel | None:
    """List Infrastructure Units

     List infrastructure unit modules with filtering.

    Args:
        capabilities (None | str | Unset):
        provider (None | str | Unset):
        unit_type (None | str | Unset):
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        capabilities=capabilities,
        provider=provider,
        unit_type=unit_type,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    capabilities: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    unit_type: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
) -> Response[APIResponseModel]:
    """List Infrastructure Units

     List infrastructure unit modules with filtering.

    Args:
        capabilities (None | str | Unset):
        provider (None | str | Unset):
        unit_type (None | str | Unset):
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        capabilities=capabilities,
        provider=provider,
        unit_type=unit_type,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    capabilities: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    unit_type: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
) -> APIResponseModel | None:
    """List Infrastructure Units

     List infrastructure unit modules with filtering.

    Args:
        capabilities (None | str | Unset):
        provider (None | str | Unset):
        unit_type (None | str | Unset):
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            capabilities=capabilities,
            provider=provider,
            unit_type=unit_type,
            limit=limit,
            offset=offset,
        )
    ).parsed
