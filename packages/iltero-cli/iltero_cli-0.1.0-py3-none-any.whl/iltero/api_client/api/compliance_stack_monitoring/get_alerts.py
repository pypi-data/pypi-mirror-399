from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    stack_id: str,
    *,
    status: None | str | Unset = "ACTIVE",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/compliance/stacks/{stack_id}/alerts",
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
    stack_id: str,
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "ACTIVE",
) -> Response[APIResponseModel]:
    """Get compliance alerts

     Retrieves active compliance alerts for a stack.

    Args:
        stack_id (str):
        status (None | str | Unset):  Default: 'ACTIVE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "ACTIVE",
) -> APIResponseModel | None:
    """Get compliance alerts

     Retrieves active compliance alerts for a stack.

    Args:
        stack_id (str):
        status (None | str | Unset):  Default: 'ACTIVE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        status=status,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "ACTIVE",
) -> Response[APIResponseModel]:
    """Get compliance alerts

     Retrieves active compliance alerts for a stack.

    Args:
        stack_id (str):
        status (None | str | Unset):  Default: 'ACTIVE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    status: None | str | Unset = "ACTIVE",
) -> APIResponseModel | None:
    """Get compliance alerts

     Retrieves active compliance alerts for a stack.

    Args:
        stack_id (str):
        status (None | str | Unset):  Default: 'ACTIVE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            client=client,
            status=status,
        )
    ).parsed
