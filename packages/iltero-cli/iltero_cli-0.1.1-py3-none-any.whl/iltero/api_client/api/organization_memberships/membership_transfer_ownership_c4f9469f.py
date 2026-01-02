from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response


def _get_kwargs(
    *,
    new_owner_email: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["new_owner_email"] = new_owner_email

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/orgs/memberships/transfer-ownership",
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
    new_owner_email: str,
) -> Response[APIResponseModel]:
    """Transfer Ownership

     Transfer ownership of a org to a new owner.

    Args:
        request: HTTP request containing org model
        new_owner_email: Email of the new owner

    Args:
        new_owner_email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        new_owner_email=new_owner_email,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    new_owner_email: str,
) -> APIResponseModel | None:
    """Transfer Ownership

     Transfer ownership of a org to a new owner.

    Args:
        request: HTTP request containing org model
        new_owner_email: Email of the new owner

    Args:
        new_owner_email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        new_owner_email=new_owner_email,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    new_owner_email: str,
) -> Response[APIResponseModel]:
    """Transfer Ownership

     Transfer ownership of a org to a new owner.

    Args:
        request: HTTP request containing org model
        new_owner_email: Email of the new owner

    Args:
        new_owner_email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        new_owner_email=new_owner_email,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    new_owner_email: str,
) -> APIResponseModel | None:
    """Transfer Ownership

     Transfer ownership of a org to a new owner.

    Args:
        request: HTTP request containing org model
        new_owner_email: Email of the new owner

    Args:
        new_owner_email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            new_owner_email=new_owner_email,
        )
    ).parsed
