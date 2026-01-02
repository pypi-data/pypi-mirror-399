from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response


def _get_kwargs(
    *,
    new_role: str,
    target_user_email: str,
    scope_type: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["new_role"] = new_role

    params["target_user_email"] = target_user_email

    params["scope_type"] = scope_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/orgs/memberships/change-role",
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
    new_role: str,
    target_user_email: str,
    scope_type: str,
) -> Response[APIResponseModel]:
    """Update Role

     Update a member's role in a org (Owners & Admins only).

    Args:
        request: HTTP request containing org model
        new_role: New role to assign
        target_user_email: Email of user to update
        scope_type: Type of scope (org, workspace, etc)

    Args:
        new_role (str):
        target_user_email (str):
        scope_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        new_role=new_role,
        target_user_email=target_user_email,
        scope_type=scope_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    new_role: str,
    target_user_email: str,
    scope_type: str,
) -> APIResponseModel | None:
    """Update Role

     Update a member's role in a org (Owners & Admins only).

    Args:
        request: HTTP request containing org model
        new_role: New role to assign
        target_user_email: Email of user to update
        scope_type: Type of scope (org, workspace, etc)

    Args:
        new_role (str):
        target_user_email (str):
        scope_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        new_role=new_role,
        target_user_email=target_user_email,
        scope_type=scope_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    new_role: str,
    target_user_email: str,
    scope_type: str,
) -> Response[APIResponseModel]:
    """Update Role

     Update a member's role in a org (Owners & Admins only).

    Args:
        request: HTTP request containing org model
        new_role: New role to assign
        target_user_email: Email of user to update
        scope_type: Type of scope (org, workspace, etc)

    Args:
        new_role (str):
        target_user_email (str):
        scope_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        new_role=new_role,
        target_user_email=target_user_email,
        scope_type=scope_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    new_role: str,
    target_user_email: str,
    scope_type: str,
) -> APIResponseModel | None:
    """Update Role

     Update a member's role in a org (Owners & Admins only).

    Args:
        request: HTTP request containing org model
        new_role: New role to assign
        target_user_email: Email of user to update
        scope_type: Type of scope (org, workspace, etc)

    Args:
        new_role (str):
        target_user_email (str):
        scope_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            new_role=new_role,
            target_user_email=target_user_email,
            scope_type=scope_type,
        )
    ).parsed
