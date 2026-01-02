from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.registry_health_check_9_af_794_ca_response import RegistryHealthCheck9Af794CaResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/registry/health",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RegistryHealthCheck9Af794CaResponse | None:
    if response.status_code == 200:
        response_200 = RegistryHealthCheck9Af794CaResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RegistryHealthCheck9Af794CaResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[RegistryHealthCheck9Af794CaResponse]:
    """Health Check

     Health check endpoint for the registry.

    Returns:
        JSON response indicating registry health status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegistryHealthCheck9Af794CaResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> RegistryHealthCheck9Af794CaResponse | None:
    """Health Check

     Health check endpoint for the registry.

    Returns:
        JSON response indicating registry health status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegistryHealthCheck9Af794CaResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[RegistryHealthCheck9Af794CaResponse]:
    """Health Check

     Health check endpoint for the registry.

    Returns:
        JSON response indicating registry health status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegistryHealthCheck9Af794CaResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> RegistryHealthCheck9Af794CaResponse | None:
    """Health Check

     Health check endpoint for the registry.

    Returns:
        JSON response indicating registry health status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegistryHealthCheck9Af794CaResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
