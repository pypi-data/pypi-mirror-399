from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    token_type: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_token_type: None | str | Unset
    if isinstance(token_type, Unset):
        json_token_type = UNSET
    else:
        json_token_type = token_type
    params["token_type"] = json_token_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/auth/tokens/",
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
    token_type: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List Tokens

     List user's tokens with optional type filtering.

    Args:
        request: HTTP request
        token_type: Optional token type filter

    Returns:
        API response with list of tokens

    Args:
        token_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        token_type=token_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    token_type: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List Tokens

     List user's tokens with optional type filtering.

    Args:
        request: HTTP request
        token_type: Optional token type filter

    Returns:
        API response with list of tokens

    Args:
        token_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        token_type=token_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    token_type: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List Tokens

     List user's tokens with optional type filtering.

    Args:
        request: HTTP request
        token_type: Optional token type filter

    Returns:
        API response with list of tokens

    Args:
        token_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        token_type=token_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    token_type: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List Tokens

     List user's tokens with optional type filtering.

    Args:
        request: HTTP request
        token_type: Optional token type filter

    Returns:
        API response with list of tokens

    Args:
        token_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            token_type=token_type,
        )
    ).parsed
