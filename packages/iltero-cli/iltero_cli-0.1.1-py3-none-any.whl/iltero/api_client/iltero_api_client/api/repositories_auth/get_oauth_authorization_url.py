from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    provider: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/git/auth/oauth/url",
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
    provider: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Get OAuth authorization URL


            Generates OAuth authorization URL for Git provider authentication.

            Returns the URL where users should be redirected to begin the OAuth flow.
            Provider can be specified or auto-detected from X-Git-Provider header.


    Args:
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    provider: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Get OAuth authorization URL


            Generates OAuth authorization URL for Git provider authentication.

            Returns the URL where users should be redirected to begin the OAuth flow.
            Provider can be specified or auto-detected from X-Git-Provider header.


    Args:
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        provider=provider,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    provider: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Get OAuth authorization URL


            Generates OAuth authorization URL for Git provider authentication.

            Returns the URL where users should be redirected to begin the OAuth flow.
            Provider can be specified or auto-detected from X-Git-Provider header.


    Args:
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    provider: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Get OAuth authorization URL


            Generates OAuth authorization URL for Git provider authentication.

            Returns the URL where users should be redirected to begin the OAuth flow.
            Provider can be specified or auto-detected from X-Git-Provider header.


    Args:
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            provider=provider,
        )
    ).parsed
