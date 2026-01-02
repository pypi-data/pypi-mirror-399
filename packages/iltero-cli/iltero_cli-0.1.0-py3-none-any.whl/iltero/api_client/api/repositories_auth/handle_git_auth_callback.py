from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    code: None | str | Unset = UNSET,
    state: None | str | Unset = UNSET,
    installation_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_code: None | str | Unset
    if isinstance(code, Unset):
        json_code = UNSET
    else:
        json_code = code
    params["code"] = json_code

    json_state: None | str | Unset
    if isinstance(state, Unset):
        json_state = UNSET
    else:
        json_state = state
    params["state"] = json_state

    json_installation_id: int | None | Unset
    if isinstance(installation_id, Unset):
        json_installation_id = UNSET
    else:
        json_installation_id = installation_id
    params["installation_id"] = json_installation_id

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/git/auth/gh/callback",
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
    client: AuthenticatedClient | Client,
    code: None | str | Unset = UNSET,
    state: None | str | Unset = UNSET,
    installation_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Handle Git provider OAuth callback


            Handles Git provider OAuth2 or App installation callback.

            Supports GitHub, GitLab, and Bitbucket with both OAuth2 and App flows.
            Returns authentication credentials for repository access.


    Args:
        code (None | str | Unset):
        state (None | str | Unset):
        installation_id (int | None | Unset):
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
        installation_id=installation_id,
        provider=provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    code: None | str | Unset = UNSET,
    state: None | str | Unset = UNSET,
    installation_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Handle Git provider OAuth callback


            Handles Git provider OAuth2 or App installation callback.

            Supports GitHub, GitLab, and Bitbucket with both OAuth2 and App flows.
            Returns authentication credentials for repository access.


    Args:
        code (None | str | Unset):
        state (None | str | Unset):
        installation_id (int | None | Unset):
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        code=code,
        state=state,
        installation_id=installation_id,
        provider=provider,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: None | str | Unset = UNSET,
    state: None | str | Unset = UNSET,
    installation_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Handle Git provider OAuth callback


            Handles Git provider OAuth2 or App installation callback.

            Supports GitHub, GitLab, and Bitbucket with both OAuth2 and App flows.
            Returns authentication credentials for repository access.


    Args:
        code (None | str | Unset):
        state (None | str | Unset):
        installation_id (int | None | Unset):
        provider (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
        installation_id=installation_id,
        provider=provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    code: None | str | Unset = UNSET,
    state: None | str | Unset = UNSET,
    installation_id: int | None | Unset = UNSET,
    provider: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Handle Git provider OAuth callback


            Handles Git provider OAuth2 or App installation callback.

            Supports GitHub, GitLab, and Bitbucket with both OAuth2 and App flows.
            Returns authentication credentials for repository access.


    Args:
        code (None | str | Unset):
        state (None | str | Unset):
        installation_id (int | None | Unset):
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
            code=code,
            state=state,
            installation_id=installation_id,
            provider=provider,
        )
    ).parsed
