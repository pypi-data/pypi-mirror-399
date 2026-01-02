from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response


def _get_kwargs(
    role_id: str,
    *,
    scope_type: str,
    scope_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["scope_type"] = scope_type

    params["scope_id"] = scope_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/rbac/roles/{role_id}",
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
    role_id: str,
    *,
    client: AuthenticatedClient,
    scope_type: str,
    scope_id: str,
) -> Response[APIResponseModel]:
    """Get Role

     Get role endpoint.

    Args:
        request: HTTP request
        role_id: Role ID
        scope_type: Type of scope
        scope_id: Scope ID

    Returns:
        API response with role details

    Args:
        role_id (str):
        scope_type (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        role_id=role_id,
        scope_type=scope_type,
        scope_id=scope_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    role_id: str,
    *,
    client: AuthenticatedClient,
    scope_type: str,
    scope_id: str,
) -> APIResponseModel | None:
    """Get Role

     Get role endpoint.

    Args:
        request: HTTP request
        role_id: Role ID
        scope_type: Type of scope
        scope_id: Scope ID

    Returns:
        API response with role details

    Args:
        role_id (str):
        scope_type (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        role_id=role_id,
        client=client,
        scope_type=scope_type,
        scope_id=scope_id,
    ).parsed


async def asyncio_detailed(
    role_id: str,
    *,
    client: AuthenticatedClient,
    scope_type: str,
    scope_id: str,
) -> Response[APIResponseModel]:
    """Get Role

     Get role endpoint.

    Args:
        request: HTTP request
        role_id: Role ID
        scope_type: Type of scope
        scope_id: Scope ID

    Returns:
        API response with role details

    Args:
        role_id (str):
        scope_type (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        role_id=role_id,
        scope_type=scope_type,
        scope_id=scope_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    role_id: str,
    *,
    client: AuthenticatedClient,
    scope_type: str,
    scope_id: str,
) -> APIResponseModel | None:
    """Get Role

     Get role endpoint.

    Args:
        request: HTTP request
        role_id: Role ID
        scope_type: Type of scope
        scope_id: Scope ID

    Returns:
        API response with role details

    Args:
        role_id (str):
        scope_type (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            role_id=role_id,
            client=client,
            scope_type=scope_type,
            scope_id=scope_id,
        )
    ).parsed
