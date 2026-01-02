from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.installation_token_request_schema import InstallationTokenRequestSchema
from ...types import Response


def _get_kwargs(
    *,
    body: InstallationTokenRequestSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/stacks/gh/installation-token",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: InstallationTokenRequestSchema,
) -> Response[APIResponseModel]:
    """Get GitHub installation token


            Generates a GitHub App installation token for private repository access.

            This endpoint is called by GitHub Actions workflows to fetch tokens
            for accessing private deployment units. Tokens are short-lived (60 minutes).


    Args:
        body (InstallationTokenRequestSchema): Schema for GitHub App installation token request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: InstallationTokenRequestSchema,
) -> APIResponseModel | None:
    """Get GitHub installation token


            Generates a GitHub App installation token for private repository access.

            This endpoint is called by GitHub Actions workflows to fetch tokens
            for accessing private deployment units. Tokens are short-lived (60 minutes).


    Args:
        body (InstallationTokenRequestSchema): Schema for GitHub App installation token request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: InstallationTokenRequestSchema,
) -> Response[APIResponseModel]:
    """Get GitHub installation token


            Generates a GitHub App installation token for private repository access.

            This endpoint is called by GitHub Actions workflows to fetch tokens
            for accessing private deployment units. Tokens are short-lived (60 minutes).


    Args:
        body (InstallationTokenRequestSchema): Schema for GitHub App installation token request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: InstallationTokenRequestSchema,
) -> APIResponseModel | None:
    """Get GitHub installation token


            Generates a GitHub App installation token for private repository access.

            This endpoint is called by GitHub Actions workflows to fetch tokens
            for accessing private deployment units. Tokens are short-lived (60 minutes).


    Args:
        body (InstallationTokenRequestSchema): Schema for GitHub App installation token request.

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
        )
    ).parsed
